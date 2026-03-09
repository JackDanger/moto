"""CostExplorerBackend class with methods for supported APIs."""

from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_without_milliseconds
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import PARTITION_NAMES, get_partition

from .exceptions import CostCategoryNotFound, ResourceNotFoundException


def first_day() -> str:
    as_date = (
        datetime.today()
        .replace(day=1)
        .replace(hour=0)
        .replace(minute=0)
        .replace(second=0)
    )
    return iso_8601_datetime_without_milliseconds(as_date)


class CostCategoryDefinition(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        effective_start: Optional[str],
        rule_version: str,
        rules: list[dict[str, Any]],
        default_value: str,
        split_charge_rules: list[dict[str, Any]],
    ):
        self.name = name
        self.rule_version = rule_version
        self.rules = rules
        self.default_value = default_value
        self.split_charge_rules = split_charge_rules
        self.arn = f"arn:{get_partition(region_name)}:ce::{account_id}:costcategory/{str(mock_random.uuid4())}"
        self.effective_start: str = effective_start or first_day()

    def update(
        self,
        rule_version: str,
        effective_start: Optional[str],
        rules: list[dict[str, Any]],
        default_value: str,
        split_charge_rules: list[dict[str, Any]],
    ) -> None:
        self.rule_version = rule_version
        self.rules = rules
        self.default_value = default_value
        self.split_charge_rules = split_charge_rules
        self.effective_start = effective_start or first_day()

    def to_json(self) -> dict[str, Any]:
        return {
            "CostCategoryArn": self.arn,
            "Name": self.name,
            "EffectiveStart": self.effective_start,
            "RuleVersion": self.rule_version,
            "Rules": self.rules,
            "DefaultValue": self.default_value,
            "SplitChargeRules": self.split_charge_rules,
        }


class AnomalyMonitor(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        monitor_name: str,
        monitor_type: str,
        monitor_dimension: Optional[str] = None,
        monitor_specification: Optional[dict[str, Any]] = None,
    ):
        self.monitor_arn = f"arn:{get_partition(region_name)}:ce::{account_id}:anomalymonitor/{str(mock_random.uuid4())}"
        self.monitor_name = monitor_name
        self.monitor_type = monitor_type
        self.monitor_dimension = monitor_dimension
        self.monitor_specification = monitor_specification
        self.creation_date = iso_8601_datetime_without_milliseconds(datetime.now())
        self.last_updated_date = self.creation_date
        self.last_evaluated_date = ""
        self.dimensional_value_count = 0

    def update(self, monitor_name: Optional[str]) -> None:
        if monitor_name:
            self.monitor_name = monitor_name
        self.last_updated_date = iso_8601_datetime_without_milliseconds(datetime.now())

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "MonitorArn": self.monitor_arn,
            "MonitorName": self.monitor_name,
            "MonitorType": self.monitor_type,
            "CreationDate": self.creation_date,
            "LastUpdatedDate": self.last_updated_date,
            "LastEvaluatedDate": self.last_evaluated_date,
            "DimensionalValueCount": self.dimensional_value_count,
        }
        if self.monitor_dimension:
            result["MonitorDimension"] = self.monitor_dimension
        if self.monitor_specification:
            result["MonitorSpecification"] = self.monitor_specification
        return result


class AnomalySubscription(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        subscription_name: str,
        monitor_arn_list: list[str],
        subscribers: list[dict[str, str]],
        frequency: str,
        threshold: Optional[float] = None,
        threshold_expression: Optional[dict[str, Any]] = None,
    ):
        self.subscription_arn = f"arn:{get_partition(region_name)}:ce::{account_id}:anomalysubscription/{str(mock_random.uuid4())}"
        self.subscription_name = subscription_name
        self.monitor_arn_list = monitor_arn_list
        self.subscribers = subscribers
        self.frequency = frequency
        self.threshold = threshold or 0.0
        self.threshold_expression = threshold_expression
        self.account_id = account_id

    def update(
        self,
        subscription_name: Optional[str] = None,
        threshold: Optional[float] = None,
        frequency: Optional[str] = None,
        monitor_arn_list: Optional[list[str]] = None,
        subscribers: Optional[list[dict[str, str]]] = None,
        threshold_expression: Optional[dict[str, Any]] = None,
    ) -> None:
        if subscription_name is not None:
            self.subscription_name = subscription_name
        if threshold is not None:
            self.threshold = threshold
        if frequency is not None:
            self.frequency = frequency
        if monitor_arn_list is not None:
            self.monitor_arn_list = monitor_arn_list
        if subscribers is not None:
            self.subscribers = subscribers
        if threshold_expression is not None:
            self.threshold_expression = threshold_expression

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "SubscriptionArn": self.subscription_arn,
            "SubscriptionName": self.subscription_name,
            "MonitorArnList": self.monitor_arn_list,
            "Subscribers": self.subscribers,
            "Frequency": self.frequency,
            "Threshold": self.threshold,
            "AccountId": self.account_id,
        }
        if self.threshold_expression:
            result["ThresholdExpression"] = self.threshold_expression
        return result


class CostAllocationTag(BaseModel):
    def __init__(self, tag_key: str, tag_type: str, status: str):
        self.tag_key = tag_key
        self.type = tag_type
        self.status = status
        self.last_updated_date: Optional[str] = None
        self.last_used_date: Optional[str] = None

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "TagKey": self.tag_key,
            "Type": self.type,
            "Status": self.status,
        }
        if self.last_updated_date:
            result["LastUpdatedDate"] = self.last_updated_date
        if self.last_used_date:
            result["LastUsedDate"] = self.last_used_date
        return result


class CostExplorerBackend(BaseBackend):
    """Implementation of CostExplorer APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.cost_categories: dict[str, CostCategoryDefinition] = {}
        self.cost_usage_results_queue: list[dict[str, Any]] = []
        self.cost_usage_results: dict[str, dict[str, Any]] = {}
        self.tagger = TaggingService()
        self.anomaly_monitors: dict[str, AnomalyMonitor] = {}
        self.anomaly_subscriptions: dict[str, AnomalySubscription] = {}
        self.cost_allocation_tags: dict[str, CostAllocationTag] = {}

    def create_cost_category_definition(
        self,
        name: str,
        effective_start: Optional[str],
        rule_version: str,
        rules: list[dict[str, Any]],
        default_value: str,
        split_charge_rules: list[dict[str, Any]],
        tags: list[dict[str, str]],
    ) -> tuple[str, str]:
        """
        The EffectiveOn and ResourceTags-parameters are not yet implemented
        """
        ccd = CostCategoryDefinition(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            effective_start=effective_start,
            rule_version=rule_version,
            rules=rules,
            default_value=default_value,
            split_charge_rules=split_charge_rules,
        )
        self.cost_categories[ccd.arn] = ccd
        self.tag_resource(ccd.arn, tags)
        return ccd.arn, ccd.effective_start

    def describe_cost_category_definition(
        self, cost_category_arn: str
    ) -> CostCategoryDefinition:
        """
        The EffectiveOn-parameter is not yet implemented
        """
        if cost_category_arn not in self.cost_categories:
            ccd_id = cost_category_arn.split("/")[-1]
            raise CostCategoryNotFound(ccd_id)
        return self.cost_categories[cost_category_arn]

    def delete_cost_category_definition(
        self, cost_category_arn: str
    ) -> tuple[str, str]:
        """
        The EffectiveOn-parameter is not yet implemented
        """
        self.cost_categories.pop(cost_category_arn, None)
        return cost_category_arn, ""

    def update_cost_category_definition(
        self,
        cost_category_arn: str,
        effective_start: Optional[str],
        rule_version: str,
        rules: list[dict[str, Any]],
        default_value: str,
        split_charge_rules: list[dict[str, Any]],
    ) -> tuple[str, str]:
        """
        The EffectiveOn-parameter is not yet implemented
        """
        cost_category = self.describe_cost_category_definition(cost_category_arn)
        cost_category.update(
            rule_version=rule_version,
            rules=rules,
            default_value=default_value,
            split_charge_rules=split_charge_rules,
            effective_start=effective_start,
        )

        return cost_category_arn, cost_category.effective_start

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        return self.tagger.list_tags_for_resource(arn=resource_arn)["Tags"]

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def get_cost_and_usage(self, body: str) -> dict[str, Any]:
        """
        There is no validation yet on any of the input parameters.

        Cost or usage is not tracked by Moto, so this call will return nothing by default.

        You can use a dedicated API to override this, by configuring a queue of expected results.

        A request to `get_cost_and_usage` will take the first result from that queue, and assign it to the provided parameters. Subsequent requests using the same parameters will return the same result. Other requests using different parameters will take the next result from the queue, or return an empty result if the queue is empty.

        Configure this queue by making an HTTP request to `/moto-api/static/ce/cost-and-usage-results`. An example invocation looks like this:

        .. sourcecode:: python

            result = {
                "results": [
                    {
                        "ResultsByTime": [
                            {
                                "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-02"},
                                "Total": {
                                    "BlendedCost": {"Amount": "0.0101516483", "Unit": "USD"}
                                },
                                "Groups": [],
                                "Estimated": False
                            }
                        ],
                        "DimensionValueAttributes": [{"Value": "v", "Attributes": {"a": "b"}}]
                    },
                    {
                        ...
                    },
                ]
            }
            resp = requests.post(
                "http://motoapi.amazonaws.com/moto-api/static/ce/cost-and-usage-results",
                json=expected_results,
            )
            assert resp.status_code == 201

            ce = boto3.client("ce", region_name="us-east-1")
            resp = ce.get_cost_and_usage(...)
        """
        default_result: dict[str, Any] = {
            "ResultsByTime": [],
            "DimensionValueAttributes": [],
        }
        if body not in self.cost_usage_results and self.cost_usage_results_queue:
            self.cost_usage_results[body] = self.cost_usage_results_queue.pop(0)
        return self.cost_usage_results.get(body, default_result)

    # --- Anomaly Monitor operations ---

    def create_anomaly_monitor(
        self,
        monitor: dict[str, Any],
        tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        am = AnomalyMonitor(
            account_id=self.account_id,
            region_name=self.region_name,
            monitor_name=monitor["MonitorName"],
            monitor_type=monitor["MonitorType"],
            monitor_dimension=monitor.get("MonitorDimension"),
            monitor_specification=monitor.get("MonitorSpecification"),
        )
        self.anomaly_monitors[am.monitor_arn] = am
        if tags:
            self.tag_resource(am.monitor_arn, tags)
        return am.monitor_arn

    def get_anomaly_monitors(
        self,
        monitor_arn_list: Optional[list[str]] = None,
        next_page_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        if monitor_arn_list:
            monitors = []
            for arn in monitor_arn_list:
                if arn not in self.anomaly_monitors:
                    raise ResourceNotFoundException(f"Monitor {arn} is not found")
                monitors.append(self.anomaly_monitors[arn])
        else:
            monitors = list(self.anomaly_monitors.values())
        result = [m.to_json() for m in monitors]
        return result, None

    def update_anomaly_monitor(
        self,
        monitor_arn: str,
        monitor_name: Optional[str] = None,
    ) -> str:
        if monitor_arn not in self.anomaly_monitors:
            raise ResourceNotFoundException(f"Monitor {monitor_arn} is not found")
        monitor = self.anomaly_monitors[monitor_arn]
        monitor.update(monitor_name=monitor_name)
        return monitor_arn

    def delete_anomaly_monitor(self, monitor_arn: str) -> None:
        if monitor_arn not in self.anomaly_monitors:
            raise ResourceNotFoundException(f"Monitor {monitor_arn} is not found")
        self.anomaly_monitors.pop(monitor_arn)

    # --- Anomaly Subscription operations ---

    def create_anomaly_subscription(
        self,
        subscription: dict[str, Any],
        tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        asub = AnomalySubscription(
            account_id=self.account_id,
            region_name=self.region_name,
            subscription_name=subscription["SubscriptionName"],
            monitor_arn_list=subscription.get("MonitorArnList", []),
            subscribers=subscription.get("Subscribers", []),
            frequency=subscription["Frequency"],
            threshold=subscription.get("Threshold"),
            threshold_expression=subscription.get("ThresholdExpression"),
        )
        self.anomaly_subscriptions[asub.subscription_arn] = asub
        if tags:
            self.tag_resource(asub.subscription_arn, tags)
        return asub.subscription_arn

    def get_anomaly_subscriptions(
        self,
        subscription_arn_list: Optional[list[str]] = None,
        monitor_arn: Optional[str] = None,
        next_page_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        if subscription_arn_list:
            subs = []
            for arn in subscription_arn_list:
                if arn not in self.anomaly_subscriptions:
                    raise ResourceNotFoundException(
                        f"Subscription {arn} is not found"
                    )
                subs.append(self.anomaly_subscriptions[arn])
        else:
            subs = list(self.anomaly_subscriptions.values())
        if monitor_arn:
            subs = [s for s in subs if monitor_arn in s.monitor_arn_list]
        result = [s.to_json() for s in subs]
        return result, None

    def update_anomaly_subscription(
        self,
        subscription_arn: str,
        threshold: Optional[float] = None,
        frequency: Optional[str] = None,
        monitor_arn_list: Optional[list[str]] = None,
        subscribers: Optional[list[dict[str, str]]] = None,
        subscription_name: Optional[str] = None,
        threshold_expression: Optional[dict[str, Any]] = None,
    ) -> str:
        if subscription_arn not in self.anomaly_subscriptions:
            raise ResourceNotFoundException(
                f"Subscription {subscription_arn} is not found"
            )
        sub = self.anomaly_subscriptions[subscription_arn]
        sub.update(
            subscription_name=subscription_name,
            threshold=threshold,
            frequency=frequency,
            monitor_arn_list=monitor_arn_list,
            subscribers=subscribers,
            threshold_expression=threshold_expression,
        )
        return subscription_arn

    def delete_anomaly_subscription(self, subscription_arn: str) -> None:
        if subscription_arn not in self.anomaly_subscriptions:
            raise ResourceNotFoundException(
                f"Subscription {subscription_arn} is not found"
            )
        self.anomaly_subscriptions.pop(subscription_arn)

    # --- Anomaly retrieval ---

    def get_anomalies(
        self,
        monitor_arn: Optional[str] = None,
        date_interval: Optional[dict[str, str]] = None,
        feedback: Optional[str] = None,
        total_impact: Optional[dict[str, Any]] = None,
        next_page_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        # No real anomaly detection — return empty list
        return [], None

    def provide_anomaly_feedback(
        self, anomaly_id: str, feedback: str
    ) -> str:
        return anomaly_id

    # --- Cost query operations (return empty/stub data) ---

    def get_cost_and_usage_with_resources(self, body: str) -> dict[str, Any]:
        return {"ResultsByTime": [], "DimensionValueAttributes": []}

    def get_cost_categories(self, body: str) -> dict[str, Any]:
        names = [cc.name for cc in self.cost_categories.values()]
        return {
            "CostCategoryNames": names,
            "CostCategoryValues": [],
            "ReturnSize": len(names),
            "TotalSize": len(names),
        }

    def get_cost_forecast(self, body: str) -> dict[str, Any]:
        return {
            "Total": {"Amount": "0", "Unit": "USD"},
            "ForecastResultsByTime": [],
        }

    def get_dimension_values(self, body: str) -> dict[str, Any]:
        return {
            "DimensionValues": [],
            "ReturnSize": 0,
            "TotalSize": 0,
        }

    def get_reservation_coverage(self, body: str) -> dict[str, Any]:
        return {"CoveragesByTime": [], "Total": {}}

    def get_reservation_purchase_recommendation(
        self, body: str
    ) -> dict[str, Any]:
        return {"Recommendations": []}

    def get_reservation_utilization(self, body: str) -> dict[str, Any]:
        return {"UtilizationsByTime": [], "Total": {}}

    def get_rightsizing_recommendation(self, body: str) -> dict[str, Any]:
        return {"RightsizingRecommendations": []}

    def get_savings_plan_purchase_recommendation_details(
        self, body: str
    ) -> dict[str, Any]:
        return {}

    def get_savings_plans_coverage(self, body: str) -> dict[str, Any]:
        return {"SavingsPlansCoverages": []}

    def get_savings_plans_purchase_recommendation(
        self, body: str
    ) -> dict[str, Any]:
        return {}

    def get_savings_plans_utilization(self, body: str) -> dict[str, Any]:
        return {"Total": {}}

    def get_savings_plans_utilization_details(
        self, body: str
    ) -> dict[str, Any]:
        return {"SavingsPlansUtilizationDetails": []}

    def get_tags(self, body: str) -> dict[str, Any]:
        return {"Tags": [], "ReturnSize": 0, "TotalSize": 0}

    def get_usage_forecast(self, body: str) -> dict[str, Any]:
        return {
            "Total": {"Amount": "0", "Unit": "USD"},
            "ForecastResultsByTime": [],
        }

    def get_approximate_usage_records(self, body: str) -> dict[str, Any]:
        return {"Services": {}, "TotalRecords": 0, "LookbackPeriod": {}}

    def get_commitment_purchase_analysis(
        self, body: str
    ) -> dict[str, Any]:
        return {}

    def get_cost_and_usage_comparisons(
        self, body: str
    ) -> dict[str, Any]:
        return {"CostAndUsageComparisons": []}

    def get_cost_comparison_drivers(self, body: str) -> dict[str, Any]:
        return {"CostComparisonDrivers": []}

    # --- List operations ---

    def list_cost_category_definitions(
        self,
        effective_on: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        refs = []
        for cc in self.cost_categories.values():
            refs.append(
                {
                    "CostCategoryArn": cc.arn,
                    "Name": cc.name,
                    "EffectiveStart": cc.effective_start,
                    "NumberOfRules": len(cc.rules) if cc.rules else 0,
                }
            )
        return refs, None

    def list_commitment_purchase_analyses(
        self,
        analysis_status: Optional[str] = None,
        next_page_token: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        return [], None

    def list_cost_allocation_tag_backfill_history(
        self,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        return [], None

    def list_cost_allocation_tags(
        self,
        status: Optional[str] = None,
        tag_keys: Optional[list[str]] = None,
        tag_type: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        tags = list(self.cost_allocation_tags.values())
        if status:
            tags = [t for t in tags if t.status == status]
        if tag_keys:
            tags = [t for t in tags if t.tag_key in tag_keys]
        if tag_type:
            tags = [t for t in tags if t.type == tag_type]
        return [t.to_json() for t in tags], None

    def list_cost_category_resource_associations(
        self,
        cost_category_arn: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        return [], None

    def list_savings_plans_purchase_recommendation_generation(
        self,
        generation_status: Optional[str] = None,
        recommendation_ids: Optional[list[str]] = None,
        page_size: Optional[int] = None,
        next_page_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        return [], None

    # --- Start/async operations ---

    def start_commitment_purchase_analysis(
        self,
        commitment_purchase_analysis_configuration: dict[str, Any],
    ) -> tuple[str, str, str]:
        analysis_id = str(mock_random.uuid4())
        now = iso_8601_datetime_without_milliseconds(datetime.now())
        return analysis_id, now, now

    def start_cost_allocation_tag_backfill(
        self,
        backfill_from: str,
    ) -> dict[str, Any]:
        now = iso_8601_datetime_without_milliseconds(datetime.now())
        return {
            "BackfillFrom": backfill_from,
            "RequestedAt": now,
            "CompletedAt": "",
            "BackfillStatus": "SUCCEEDED",
            "LastUpdatedAt": now,
        }

    def start_savings_plans_purchase_recommendation_generation(
        self,
    ) -> tuple[str, str, str]:
        rec_id = str(mock_random.uuid4())
        now = iso_8601_datetime_without_milliseconds(datetime.now())
        return rec_id, now, now

    # --- Cost allocation tag management ---

    def update_cost_allocation_tags_status(
        self,
        cost_allocation_tags_status: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []
        for tag_entry in cost_allocation_tags_status:
            tag_key = tag_entry["TagKey"]
            status = tag_entry["Status"]
            if tag_key in self.cost_allocation_tags:
                self.cost_allocation_tags[tag_key].status = status
            else:
                cat = CostAllocationTag(
                    tag_key=tag_key, tag_type="UserDefined", status=status
                )
                cat.last_updated_date = iso_8601_datetime_without_milliseconds(
                    datetime.now()
                )
                self.cost_allocation_tags[tag_key] = cat
        return errors


ce_backends = BackendDict(
    CostExplorerBackend,
    "ce",
    use_boto3_regions=False,
    additional_regions=PARTITION_NAMES,
)
