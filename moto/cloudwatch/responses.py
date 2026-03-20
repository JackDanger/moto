import json
from collections.abc import Iterable

from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .exceptions import (
    DashboardInvalidInputError,
    InvalidParameterCombination,
    InvalidParameterValue,
    ResourceNotFound,
    ValidationError,
)
from .models import (
    Alarm,
    CloudWatchBackend,
    Dimension,
    Metric,
    MetricDataQuery,
    MetricStat,
    cloudwatch_backends,
)


class CloudWatchResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="cloudwatch")
        self.automated_parameter_parsing = True

    @property
    def cloudwatch_backend(self) -> CloudWatchBackend:
        return cloudwatch_backends[self.current_account][self.region]

    def put_metric_alarm(self) -> ActionResult:
        name = self._get_param("AlarmName")
        namespace = self._get_param("Namespace")
        metric_name = self._get_param("MetricName")
        metrics = self._get_param("Metrics", [])
        metric_data_queries = None
        if metrics:
            metric_data_queries = []
            for metric in metrics:
                metric_dimensions = []
                dims = (
                    metric.get("MetricStat", {}).get("Metric", {}).get("Dimensions", [])
                )
                for dim in dims:
                    metric_dimensions.append(
                        Dimension(name=dim.get("Name"), value=dim.get("Value"))
                    )
                metric_stat = None
                stat_metric_name = (
                    metric.get("MetricStat", {}).get("Metric", {}).get("MetricName")
                )
                if stat_metric_name:
                    stat_details = metric.get("MetricStat", {})
                    stat_metric_ns = stat_details.get("Metric", {}).get("Namespace")
                    metric_stat = MetricStat(
                        metric=Metric(
                            metric_name=stat_metric_name,
                            namespace=stat_metric_ns,
                            dimensions=metric_dimensions,
                        ),
                        period=stat_details.get("Period"),
                        stat=stat_details.get("Stat"),
                        unit=stat_details.get("Unit"),
                    )
                metric_data_queries.append(
                    MetricDataQuery(
                        query_id=metric.get("Id"),
                        label=metric.get("Label"),
                        period=metric.get("Period"),
                        return_data=metric.get("ReturnData"),
                        expression=metric.get("Expression"),
                        metric_stat=metric_stat,
                    )
                )

        comparison_operator = self._get_param("ComparisonOperator")
        evaluation_periods = self._get_param("EvaluationPeriods")
        datapoints_to_alarm = self._get_param("DatapointsToAlarm")
        period = self._get_param("Period")
        threshold = self._get_param("Threshold")
        statistic = self._get_param("Statistic")
        extended_statistic = self._get_param("ExtendedStatistic")
        description = self._get_param("AlarmDescription")
        dimensions = self._get_param("Dimensions", [])
        alarm_actions = self._get_param("AlarmActions", [])
        ok_actions = self._get_param("OKActions", [])
        actions_enabled = self._get_bool_param("ActionsEnabled")
        insufficient_data_actions = self._get_param("InsufficientDataActions", [])
        unit = self._get_param("Unit")
        treat_missing_data = self._get_param("TreatMissingData")
        evaluate_low_sample_count_percentile = self._get_param(
            "EvaluateLowSampleCountPercentile"
        )
        threshold_metric_id = self._get_param("ThresholdMetricId")
        # fetch AlarmRule to re-use this method for composite alarms as well
        rule = self._get_param("AlarmRule")
        tags = self._get_param("Tags", [])
        self.cloudwatch_backend.put_metric_alarm(
            name=name,
            namespace=namespace,
            metric_name=metric_name,
            metric_data_queries=metric_data_queries,
            comparison_operator=comparison_operator,
            evaluation_periods=evaluation_periods,
            datapoints_to_alarm=datapoints_to_alarm,
            period=period,
            threshold=threshold,
            statistic=statistic,
            extended_statistic=extended_statistic,
            description=description,
            dimensions=dimensions,
            alarm_actions=alarm_actions,
            ok_actions=ok_actions,
            insufficient_data_actions=insufficient_data_actions,
            unit=unit,
            actions_enabled=actions_enabled,
            treat_missing_data=treat_missing_data,
            evaluate_low_sample_count_percentile=evaluate_low_sample_count_percentile,
            threshold_metric_id=threshold_metric_id,
            rule=rule,
            tags=tags,
        )
        return EmptyResult()

    def describe_alarms(self) -> ActionResult:
        action_prefix = self._get_param("ActionPrefix")
        alarm_name_prefix = self._get_param("AlarmNamePrefix")
        alarm_names = self._get_param("AlarmNames", [])
        state_value = self._get_param("StateValue")

        if action_prefix:
            alarms = self.cloudwatch_backend.get_alarms_by_action_prefix(action_prefix)
        elif alarm_name_prefix:
            alarms = self.cloudwatch_backend.get_alarms_by_alarm_name_prefix(
                alarm_name_prefix
            )
        elif alarm_names:
            alarms = self.cloudwatch_backend.get_alarms_by_alarm_names(alarm_names)
        elif state_value:
            alarms = self.cloudwatch_backend.get_alarms_by_state_value(state_value)
        else:
            alarms = self.cloudwatch_backend.describe_alarms()

        metric_alarms = [a for a in alarms if a.rule is None]
        composite_alarms = [a for a in alarms if a.rule is not None]

        result = {"MetricAlarms": metric_alarms, "CompositeAlarms": composite_alarms}
        return ActionResult(result)

    def delete_alarms(self) -> ActionResult:
        alarm_names = self._get_param("AlarmNames", [])
        self.cloudwatch_backend.delete_alarms(alarm_names)
        return EmptyResult()

    def put_metric_data(self) -> ActionResult:
        namespace = self._get_param("Namespace")
        metric_data = self._get_param("MetricData", [])
        self.cloudwatch_backend.put_metric_data(namespace, metric_data)
        return EmptyResult()

    def get_metric_data(self) -> ActionResult:
        params = self._get_params()
        start = params["StartTime"]
        end = params["EndTime"]
        scan_by = params.get("ScanBy") or "TimestampDescending"

        queries = params.get("MetricDataQueries", [])
        for query in queries:
            if "MetricStat" not in query and "Expression" not in query:
                # AWS also returns the empty line
                raise ValidationError(
                    "The parameter MetricDataQueries.member.1.MetricStat is required.\n"
                )
        results = self.cloudwatch_backend.get_metric_data(
            start_time=start, end_time=end, queries=queries, scan_by=scan_by
        )

        result = {"MetricDataResults": results}
        return ActionResult(result)

    def get_metric_statistics(self) -> ActionResult:
        namespace = self._get_param("Namespace")
        metric_name = self._get_param("MetricName")
        start_time = self._get_param("StartTime")
        end_time = self._get_param("EndTime")
        period = self._get_int_param("Period")
        statistics = self._get_param("Statistics", [])
        dimensions = self._get_param("Dimensions", [])

        # Unsupported Parameters (To Be Implemented)
        unit = self._get_param("Unit")
        extended_statistics = self._get_param("ExtendedStatistics")

        if not statistics and not extended_statistics:
            raise InvalidParameterCombination(
                "Must specify either Statistics or ExtendedStatistics"
            )

        datapoints = self.cloudwatch_backend.get_metric_statistics(
            namespace,
            metric_name,
            start_time,
            end_time,
            period,
            statistics,
            unit=unit,
            dimensions=dimensions,
        )
        result = {"Label": metric_name, "Datapoints": datapoints}
        return ActionResult(result)

    def list_metrics(self) -> ActionResult:
        namespace = self._get_param("Namespace")
        metric_name = self._get_param("MetricName")
        dimensions = self._get_params().get("Dimensions", [])
        next_token = self._get_param("NextToken")
        next_token, metrics = self.cloudwatch_backend.list_metrics(
            next_token, namespace, metric_name, dimensions
        )
        result = {"Metrics": metrics, "NextToken": next_token}
        return ActionResult(result)

    def delete_dashboards(self) -> ActionResult:
        dashboards = self._get_param("DashboardNames", [])
        if not dashboards:
            raise InvalidParameterValue("Need at least 1 dashboard")

        error = self.cloudwatch_backend.delete_dashboards(dashboards)
        if error is not None:
            raise ResourceNotFound(error)

        return EmptyResult()

    @staticmethod
    def filter_alarms(
        alarms: Iterable[Alarm], metric_name: str, namespace: str
    ) -> list[Alarm]:
        metric_filtered_alarms = []

        for alarm in alarms:
            if alarm.metric_name == metric_name and alarm.namespace == namespace:
                metric_filtered_alarms.append(alarm)
        return metric_filtered_alarms

    def describe_alarms_for_metric(self) -> ActionResult:
        alarms = self.cloudwatch_backend.describe_alarms()
        namespace = self._get_param("Namespace")
        metric_name = self._get_param("MetricName")
        filtered_alarms = self.filter_alarms(alarms, metric_name, namespace)
        result = {"MetricAlarms": filtered_alarms}
        return ActionResult(result)

    def disable_alarm_actions(self) -> ActionResult:
        alarm_names = self._get_param("AlarmNames", [])
        self.cloudwatch_backend.disable_alarm_actions(alarm_names)
        return EmptyResult()

    def enable_alarm_actions(self) -> ActionResult:
        alarm_names = self._get_param("AlarmNames", [])
        self.cloudwatch_backend.enable_alarm_actions(alarm_names)
        return EmptyResult()

    def get_dashboard(self) -> ActionResult:
        dashboard_name = self._get_param("DashboardName")
        dashboard = self.cloudwatch_backend.get_dashboard(dashboard_name)
        if dashboard is None:
            raise ResourceNotFound("Dashboard does not exist")
        return ActionResult(dashboard)

    def list_dashboards(self) -> ActionResult:
        prefix = self._get_param("DashboardNamePrefix", "")
        dashboards = self.cloudwatch_backend.list_dashboards(prefix)
        result = {"DashboardEntries": dashboards}
        return ActionResult(result)

    def put_dashboard(self) -> ActionResult:
        name = self._get_param("DashboardName")
        body = self._get_param("DashboardBody")
        try:
            json.loads(body)
        except ValueError:
            raise DashboardInvalidInputError("Body is invalid JSON")
        self.cloudwatch_backend.put_dashboard(name, body)
        result = {"DashboardValidationMessages": []}  # type: ignore[var-annotated]
        return ActionResult(result)

    def set_alarm_state(self) -> ActionResult:
        alarm_name = self._get_param("AlarmName")
        reason = self._get_param("StateReason")
        reason_data = self._get_param("StateReasonData")
        state_value = self._get_param("StateValue")
        self.cloudwatch_backend.set_alarm_state(
            alarm_name, reason, reason_data, state_value
        )
        return EmptyResult()

    def list_tags_for_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceARN")
        tags = self.cloudwatch_backend.list_tags_for_resource(resource_arn)
        result = {"Tags": [{"Key": k, "Value": v} for k, v in tags.items()]}
        return ActionResult(result)

    def tag_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceARN")
        tags = self._get_param("Tags", [])
        self.cloudwatch_backend.tag_resource(resource_arn, tags)
        return EmptyResult()

    def untag_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceARN")
        tag_keys = self._get_param("TagKeys", [])
        self.cloudwatch_backend.untag_resource(resource_arn, tag_keys)
        return EmptyResult()

    def put_insight_rule(self) -> ActionResult:
        name = self._get_param("RuleName")
        state = self._get_param("RuleState")
        definition = self._get_param("RuleDefinition")
        tags = self._get_param("Tags", [])
        self.cloudwatch_backend.put_insight_rule(
            name=name,
            state=state,
            definition=definition,
            tags=tags,
        )
        return EmptyResult()

    def describe_insight_rules(self) -> ActionResult:
        rules = self.cloudwatch_backend.describe_insight_rules()
        result = {"InsightRules": rules}
        return ActionResult(result)

    def delete_insight_rules(self) -> ActionResult:
        names = self._get_param("RuleNames", [])
        failures = self.cloudwatch_backend.delete_insight_rules(rule_names=names)
        result = {"Failures": failures}
        return ActionResult(result)

    def disable_insight_rules(self) -> ActionResult:
        names = self._get_param("RuleNames", [])
        failures = self.cloudwatch_backend.disable_insight_rules(rule_names=names)
        result = {"Failures": failures}
        return ActionResult(result)

    def enable_insight_rules(self) -> ActionResult:
        names = self._get_param("RuleNames", [])
        failures = self.cloudwatch_backend.enable_insight_rules(rule_names=names)
        result = {"Failures": failures}
        return ActionResult(result)

    def put_anomaly_detector(self) -> ActionResult:
        namespace = self._get_param("Namespace")
        metric_name = self._get_param("MetricName")
        dimensions = self._get_param("Dimensions", [])
        stat = self._get_param("Stat")
        configuration = self._get_param("Configuration")
        metric_math_anomaly_detector = self._get_param("MetricMathAnomalyDetector")
        single_metric_anomaly_detector = self._get_param("SingleMetricAnomalyDetector")
        self.cloudwatch_backend.put_anomaly_detector(
            namespace=namespace,
            metric_name=metric_name,
            dimensions=dimensions,
            stat=stat,
            configuration=configuration,
            metric_math_anomaly_detector=metric_math_anomaly_detector,
            single_metric_anomaly_detector=single_metric_anomaly_detector,
        )
        return EmptyResult()

    def describe_anomaly_detectors(self) -> ActionResult:
        namespace = self._get_param("Namespace")
        metric_name = self._get_param("MetricName")
        detectors = self.cloudwatch_backend.describe_anomaly_detectors(
            namespace=namespace,
            metric_name=metric_name,
        )
        result = {"AnomalyDetectors": detectors}
        return ActionResult(result)

    def delete_anomaly_detector(self) -> ActionResult:
        namespace = self._get_param("Namespace")
        metric_name = self._get_param("MetricName")
        stat = self._get_param("Stat")
        single_metric_anomaly_detector = self._get_param("SingleMetricAnomalyDetector")
        self.cloudwatch_backend.delete_anomaly_detector(
            namespace=namespace,
            metric_name=metric_name,
            stat=stat,
            single_metric_anomaly_detector=single_metric_anomaly_detector,
        )
        return EmptyResult()

    def put_metric_stream(self) -> ActionResult:
        name = self._get_param("Name")
        firehose_arn = self._get_param("FirehoseArn")
        role_arn = self._get_param("RoleArn")
        output_format = self._get_param("OutputFormat")
        include_filters = self._get_param("IncludeFilters", [])
        exclude_filters = self._get_param("ExcludeFilters", [])
        statistics_configurations = self._get_param("StatisticsConfigurations", [])
        include_linked = self._get_param("IncludeLinkedAccountsMetrics", False)
        tags = self._get_param("Tags", [])
        stream = self.cloudwatch_backend.put_metric_stream(
            name=name,
            firehose_arn=firehose_arn,
            role_arn=role_arn,
            output_format=output_format,
            include_filters=include_filters,
            exclude_filters=exclude_filters,
            statistics_configurations=statistics_configurations,
            include_linked_accounts_metrics=include_linked,
            tags=tags,
        )
        result = {"Arn": stream.arn}
        return ActionResult(result)

    def get_metric_stream(self) -> ActionResult:
        name = self._get_param("Name")
        stream = self.cloudwatch_backend.get_metric_stream(name)
        result = {
            "Arn": stream.arn,
            "Name": stream.name,
            "FirehoseArn": stream.firehose_arn,
            "RoleArn": stream.role_arn,
            "OutputFormat": stream.output_format,
            "IncludeFilters": stream.include_filters,
            "ExcludeFilters": stream.exclude_filters,
            "StatisticsConfigurations": stream.statistics_configurations,
            "State": stream.state,
            "CreationDate": stream.creation_date,
            "LastUpdateDate": stream.last_update_date,
            "IncludeLinkedAccountsMetrics": stream.include_linked_accounts_metrics,
        }
        return ActionResult(result)

    def delete_metric_stream(self) -> ActionResult:
        name = self._get_param("Name")
        self.cloudwatch_backend.delete_metric_stream(name)
        return EmptyResult()

    def start_metric_streams(self) -> ActionResult:
        names = self._get_param("Names", [])
        self.cloudwatch_backend.start_metric_streams(names)
        return EmptyResult()

    def stop_metric_streams(self) -> ActionResult:
        names = self._get_param("Names", [])
        self.cloudwatch_backend.stop_metric_streams(names)
        return EmptyResult()

    def list_metric_streams(self) -> ActionResult:
        streams = self.cloudwatch_backend.list_metric_streams()
        entries = []
        for s in streams:
            entries.append(
                {
                    "Arn": s.arn,
                    "Name": s.name,
                    "FirehoseArn": s.firehose_arn,
                    "State": s.state,
                    "OutputFormat": s.output_format,
                    "CreationDate": s.creation_date,
                    "LastUpdateDate": s.last_update_date,
                }
            )
        result = {"Entries": entries}
        return ActionResult(result)

    def list_managed_insight_rules(self) -> ActionResult:
        resource_arn = self._get_param("ResourceARN")
        rules = self.cloudwatch_backend.list_managed_insight_rules(
            resource_arn=resource_arn,
        )
        result = {"ManagedRules": rules}
        return ActionResult(result)

    def put_managed_insight_rules(self) -> ActionResult:
        managed_rules = self._get_param("ManagedRules", [])
        failures = self.cloudwatch_backend.put_managed_insight_rules(
            managed_rules=managed_rules,
        )
        result = {"Failures": failures}
        return ActionResult(result)

    def get_insight_rule_report(self) -> ActionResult:
        rule_name = self._get_param("RuleName")
        start_time = self._get_param("StartTime")
        end_time = self._get_param("EndTime")
        period = self._get_int_param("Period")
        max_contributor_count = self._get_param("MaxContributorCount")
        metrics = self._get_param("Metrics", [])
        order_by = self._get_param("OrderBy")
        report = self.cloudwatch_backend.get_insight_rule_report(
            rule_name=rule_name,
            start_time=start_time,
            end_time=end_time,
            period=period,
            max_contributor_count=max_contributor_count,
            metrics=metrics,
            order_by=order_by,
        )
        return ActionResult(report)

    def get_metric_widget_image(self) -> ActionResult:
        metric_widget = self._get_param("MetricWidget")
        output_format = self._get_param("OutputFormat", "png")
        image_data = self.cloudwatch_backend.get_metric_widget_image(
            metric_widget=metric_widget,
            output_format=output_format,
        )
        import base64

        result = {"MetricWidgetImage": base64.b64encode(image_data).decode("utf-8")}
        return ActionResult(result)

    def list_alarm_mute_rules(self) -> ActionResult:
        alarm_name = self._get_param("AlarmName")
        mute_rules = self.cloudwatch_backend.list_alarm_mute_rules(
            alarm_name=alarm_name,
        )
        result = {"MuteRules": mute_rules}
        return ActionResult(result)

    def describe_alarm_contributors(self) -> ActionResult:
        alarm_name = self._get_param("AlarmName")
        report = self.cloudwatch_backend.describe_alarm_contributors(
            alarm_name=alarm_name,
        )
        return ActionResult(report)

    def put_alarm_mute_rule(self) -> ActionResult:
        rule_name = self._get_param("RuleName")
        alarm_name = self._get_param("AlarmName")
        result = {
            "RuleName": rule_name,
            "AlarmName": alarm_name,
        }
        return ActionResult(result)

    def delete_alarm_mute_rule(self) -> EmptyResult:
        return EmptyResult()
