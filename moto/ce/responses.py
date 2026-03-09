"""Handles incoming ce requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import CostExplorerBackend, ce_backends


class CostExplorerResponse(BaseResponse):
    """Handler for CostExplorer requests and responses."""

    @property
    def ce_backend(self) -> CostExplorerBackend:
        """Return backend instance specific for this region."""
        return ce_backends[self.current_account][self.partition]

    def create_cost_category_definition(self) -> str:
        params = json.loads(self.body)
        name = params.get("Name")
        rule_version = params.get("RuleVersion")
        rules = params.get("Rules")
        default_value = params.get("DefaultValue")
        split_charge_rules = params.get("SplitChargeRules")
        effective_start = params.get("EffectiveStart")
        tags = params.get("ResourceTags")
        (
            cost_category_arn,
            effective_start,
        ) = self.ce_backend.create_cost_category_definition(
            name=name,
            effective_start=effective_start,
            rule_version=rule_version,
            rules=rules,
            default_value=default_value,
            split_charge_rules=split_charge_rules,
            tags=tags,
        )
        return json.dumps(
            {"CostCategoryArn": cost_category_arn, "EffectiveStart": effective_start}
        )

    def describe_cost_category_definition(self) -> str:
        params = json.loads(self.body)
        cost_category_arn = params.get("CostCategoryArn")
        cost_category = self.ce_backend.describe_cost_category_definition(
            cost_category_arn=cost_category_arn
        )
        return json.dumps({"CostCategory": cost_category.to_json()})

    def delete_cost_category_definition(self) -> str:
        params = json.loads(self.body)
        cost_category_arn = params.get("CostCategoryArn")
        (
            cost_category_arn,
            effective_end,
        ) = self.ce_backend.delete_cost_category_definition(
            cost_category_arn=cost_category_arn,
        )
        return json.dumps(
            {"CostCategoryArn": cost_category_arn, "EffectiveEnd": effective_end}
        )

    def update_cost_category_definition(self) -> str:
        params = json.loads(self.body)
        cost_category_arn = params.get("CostCategoryArn")
        effective_start = params.get("EffectiveStart")
        rule_version = params.get("RuleVersion")
        rules = params.get("Rules")
        default_value = params.get("DefaultValue")
        split_charge_rules = params.get("SplitChargeRules")
        (
            cost_category_arn,
            effective_start,
        ) = self.ce_backend.update_cost_category_definition(
            cost_category_arn=cost_category_arn,
            effective_start=effective_start,
            rule_version=rule_version,
            rules=rules,
            default_value=default_value,
            split_charge_rules=split_charge_rules,
        )
        return json.dumps(
            {"CostCategoryArn": cost_category_arn, "EffectiveStart": effective_start}
        )

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        tags = self.ce_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"ResourceTags": tags})

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        tags = params.get("ResourceTags")
        self.ce_backend.tag_resource(resource_arn, tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        tag_names = params.get("ResourceTagKeys")
        self.ce_backend.untag_resource(resource_arn, tag_names)
        return json.dumps({})

    def get_cost_and_usage(self) -> str:
        resp = self.ce_backend.get_cost_and_usage(self.body)
        return json.dumps(resp)

    # --- Anomaly Monitor operations ---

    def create_anomaly_monitor(self) -> str:
        params = json.loads(self.body)
        monitor = params.get("AnomalyMonitor")
        tags = params.get("ResourceTags")
        monitor_arn = self.ce_backend.create_anomaly_monitor(
            monitor=monitor, tags=tags
        )
        return json.dumps({"MonitorArn": monitor_arn})

    def get_anomaly_monitors(self) -> str:
        params = json.loads(self.body)
        monitors, next_token = self.ce_backend.get_anomaly_monitors(
            monitor_arn_list=params.get("MonitorArnList"),
            next_page_token=params.get("NextPageToken"),
            max_results=params.get("MaxResults"),
        )
        result: dict = {"AnomalyMonitors": monitors}
        if next_token:
            result["NextPageToken"] = next_token
        return json.dumps(result)

    def update_anomaly_monitor(self) -> str:
        params = json.loads(self.body)
        monitor_arn = self.ce_backend.update_anomaly_monitor(
            monitor_arn=params["MonitorArn"],
            monitor_name=params.get("MonitorName"),
        )
        return json.dumps({"MonitorArn": monitor_arn})

    def delete_anomaly_monitor(self) -> str:
        params = json.loads(self.body)
        self.ce_backend.delete_anomaly_monitor(params["MonitorArn"])
        return json.dumps({})

    # --- Anomaly Subscription operations ---

    def create_anomaly_subscription(self) -> str:
        params = json.loads(self.body)
        subscription = params.get("AnomalySubscription")
        tags = params.get("ResourceTags")
        subscription_arn = self.ce_backend.create_anomaly_subscription(
            subscription=subscription, tags=tags
        )
        return json.dumps({"SubscriptionArn": subscription_arn})

    def get_anomaly_subscriptions(self) -> str:
        params = json.loads(self.body)
        subs, next_token = self.ce_backend.get_anomaly_subscriptions(
            subscription_arn_list=params.get("SubscriptionArnList"),
            monitor_arn=params.get("MonitorArn"),
            next_page_token=params.get("NextPageToken"),
            max_results=params.get("MaxResults"),
        )
        result: dict = {"AnomalySubscriptions": subs}
        if next_token:
            result["NextPageToken"] = next_token
        return json.dumps(result)

    def update_anomaly_subscription(self) -> str:
        params = json.loads(self.body)
        subscription_arn = self.ce_backend.update_anomaly_subscription(
            subscription_arn=params["SubscriptionArn"],
            threshold=params.get("Threshold"),
            frequency=params.get("Frequency"),
            monitor_arn_list=params.get("MonitorArnList"),
            subscribers=params.get("Subscribers"),
            subscription_name=params.get("SubscriptionName"),
            threshold_expression=params.get("ThresholdExpression"),
        )
        return json.dumps({"SubscriptionArn": subscription_arn})

    def delete_anomaly_subscription(self) -> str:
        params = json.loads(self.body)
        self.ce_backend.delete_anomaly_subscription(params["SubscriptionArn"])
        return json.dumps({})

    # --- Anomaly retrieval ---

    def get_anomalies(self) -> str:
        params = json.loads(self.body)
        anomalies, next_token = self.ce_backend.get_anomalies(
            monitor_arn=params.get("MonitorArn"),
            date_interval=params.get("DateInterval"),
            feedback=params.get("Feedback"),
            total_impact=params.get("TotalImpact"),
            next_page_token=params.get("NextPageToken"),
            max_results=params.get("MaxResults"),
        )
        result: dict = {"Anomalies": anomalies}
        if next_token:
            result["NextPageToken"] = next_token
        return json.dumps(result)

    def provide_anomaly_feedback(self) -> str:
        params = json.loads(self.body)
        anomaly_id = self.ce_backend.provide_anomaly_feedback(
            anomaly_id=params["AnomalyId"],
            feedback=params["Feedback"],
        )
        return json.dumps({"AnomalyId": anomaly_id})

    # --- Cost query operations ---

    def get_cost_and_usage_with_resources(self) -> str:
        resp = self.ce_backend.get_cost_and_usage_with_resources(self.body)
        return json.dumps(resp)

    def get_cost_categories(self) -> str:
        resp = self.ce_backend.get_cost_categories(self.body)
        return json.dumps(resp)

    def get_cost_forecast(self) -> str:
        resp = self.ce_backend.get_cost_forecast(self.body)
        return json.dumps(resp)

    def get_dimension_values(self) -> str:
        resp = self.ce_backend.get_dimension_values(self.body)
        return json.dumps(resp)

    def get_reservation_coverage(self) -> str:
        resp = self.ce_backend.get_reservation_coverage(self.body)
        return json.dumps(resp)

    def get_reservation_purchase_recommendation(self) -> str:
        resp = self.ce_backend.get_reservation_purchase_recommendation(self.body)
        return json.dumps(resp)

    def get_reservation_utilization(self) -> str:
        resp = self.ce_backend.get_reservation_utilization(self.body)
        return json.dumps(resp)

    def get_rightsizing_recommendation(self) -> str:
        resp = self.ce_backend.get_rightsizing_recommendation(self.body)
        return json.dumps(resp)

    def get_savings_plan_purchase_recommendation_details(self) -> str:
        resp = self.ce_backend.get_savings_plan_purchase_recommendation_details(
            self.body
        )
        return json.dumps(resp)

    def get_savings_plans_coverage(self) -> str:
        resp = self.ce_backend.get_savings_plans_coverage(self.body)
        return json.dumps(resp)

    def get_savings_plans_purchase_recommendation(self) -> str:
        resp = self.ce_backend.get_savings_plans_purchase_recommendation(self.body)
        return json.dumps(resp)

    def get_savings_plans_utilization(self) -> str:
        resp = self.ce_backend.get_savings_plans_utilization(self.body)
        return json.dumps(resp)

    def get_savings_plans_utilization_details(self) -> str:
        resp = self.ce_backend.get_savings_plans_utilization_details(self.body)
        return json.dumps(resp)

    def get_tags(self) -> str:
        resp = self.ce_backend.get_tags(self.body)
        return json.dumps(resp)

    def get_usage_forecast(self) -> str:
        resp = self.ce_backend.get_usage_forecast(self.body)
        return json.dumps(resp)

    def get_approximate_usage_records(self) -> str:
        resp = self.ce_backend.get_approximate_usage_records(self.body)
        return json.dumps(resp)

    def get_commitment_purchase_analysis(self) -> str:
        resp = self.ce_backend.get_commitment_purchase_analysis(self.body)
        return json.dumps(resp)

    def get_cost_and_usage_comparisons(self) -> str:
        resp = self.ce_backend.get_cost_and_usage_comparisons(self.body)
        return json.dumps(resp)

    def get_cost_comparison_drivers(self) -> str:
        resp = self.ce_backend.get_cost_comparison_drivers(self.body)
        return json.dumps(resp)

    # --- List operations ---

    def list_cost_category_definitions(self) -> str:
        params = json.loads(self.body)
        refs, next_token = self.ce_backend.list_cost_category_definitions(
            effective_on=params.get("EffectiveOn"),
            next_token=params.get("NextToken"),
            max_results=params.get("MaxResults"),
        )
        result: dict = {"CostCategoryReferences": refs}
        if next_token:
            result["NextToken"] = next_token
        return json.dumps(result)

    def list_commitment_purchase_analyses(self) -> str:
        params = json.loads(self.body)
        analyses, next_token = self.ce_backend.list_commitment_purchase_analyses(
            analysis_status=params.get("AnalysisStatus"),
            next_page_token=params.get("NextPageToken"),
            page_size=params.get("PageSize"),
        )
        result: dict = {"AnalysisSummaryList": analyses}
        if next_token:
            result["NextPageToken"] = next_token
        return json.dumps(result)

    def list_cost_allocation_tag_backfill_history(self) -> str:
        params = json.loads(self.body)
        history, next_token = self.ce_backend.list_cost_allocation_tag_backfill_history(
            next_token=params.get("NextToken"),
            max_results=params.get("MaxResults"),
        )
        result: dict = {"BackfillRequests": history}
        if next_token:
            result["NextToken"] = next_token
        return json.dumps(result)

    def list_cost_allocation_tags(self) -> str:
        params = json.loads(self.body)
        tags, next_token = self.ce_backend.list_cost_allocation_tags(
            status=params.get("Status"),
            tag_keys=params.get("TagKeys"),
            tag_type=params.get("Type"),
            next_token=params.get("NextToken"),
            max_results=params.get("MaxResults"),
        )
        result: dict = {"CostAllocationTags": tags}
        if next_token:
            result["NextToken"] = next_token
        return json.dumps(result)

    def list_cost_category_resource_associations(self) -> str:
        params = json.loads(self.body)
        assocs, next_token = (
            self.ce_backend.list_cost_category_resource_associations(
                cost_category_arn=params.get("CostCategoryArn"),
                next_token=params.get("NextToken"),
                max_results=params.get("MaxResults"),
            )
        )
        result: dict = {"CostCategoryResourceAssociations": assocs}
        if next_token:
            result["NextToken"] = next_token
        return json.dumps(result)

    def list_savings_plans_purchase_recommendation_generation(self) -> str:
        params = json.loads(self.body)
        gens, next_token = (
            self.ce_backend.list_savings_plans_purchase_recommendation_generation(
                generation_status=params.get("GenerationStatus"),
                recommendation_ids=params.get("RecommendationIds"),
                page_size=params.get("PageSize"),
                next_page_token=params.get("NextPageToken"),
            )
        )
        result: dict = {"GenerationSummaryList": gens}
        if next_token:
            result["NextPageToken"] = next_token
        return json.dumps(result)

    # --- Start/async operations ---

    def start_commitment_purchase_analysis(self) -> str:
        params = json.loads(self.body)
        analysis_id, started, estimated = (
            self.ce_backend.start_commitment_purchase_analysis(
                commitment_purchase_analysis_configuration=params.get(
                    "CommitmentPurchaseAnalysisConfiguration"
                ),
            )
        )
        return json.dumps(
            {
                "AnalysisId": analysis_id,
                "AnalysisStartedTime": started,
                "EstimatedCompletionTime": estimated,
            }
        )

    def start_cost_allocation_tag_backfill(self) -> str:
        params = json.loads(self.body)
        backfill_request = self.ce_backend.start_cost_allocation_tag_backfill(
            backfill_from=params["BackfillFrom"],
        )
        return json.dumps({"BackfillRequest": backfill_request})

    def start_savings_plans_purchase_recommendation_generation(self) -> str:
        rec_id, started, estimated = (
            self.ce_backend.start_savings_plans_purchase_recommendation_generation()
        )
        return json.dumps(
            {
                "RecommendationId": rec_id,
                "GenerationStartedTime": started,
                "EstimatedCompletionTime": estimated,
            }
        )

    # --- Cost allocation tag management ---

    def update_cost_allocation_tags_status(self) -> str:
        params = json.loads(self.body)
        errors = self.ce_backend.update_cost_allocation_tags_status(
            cost_allocation_tags_status=params["CostAllocationTagsStatus"],
        )
        return json.dumps({"Errors": errors})
