"""Handles incoming securityhub requests, invokes methods, returns responses."""

import json
from typing import Any
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import SecurityHubBackend, securityhub_backends


class SecurityHubResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="securityhub")

    @property
    def securityhub_backend(self) -> SecurityHubBackend:
        return securityhub_backends[self.current_account][self.region]

    def _parse_body(self) -> dict[str, Any]:
        if self.body:
            raw = self.body
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            return json.loads(raw)
        return {}

    # --- Hub ---

    def enable_security_hub(self) -> str:
        params = self._parse_body()
        enable_default_standards = params.get("EnableDefaultStandards", True)
        tags = params.get("Tags", {})
        self.securityhub_backend.enable_security_hub(
            enable_default_standards=enable_default_standards,
            tags=tags,
        )
        return json.dumps({})

    def disable_security_hub(self) -> str:
        self.securityhub_backend.disable_security_hub()
        return json.dumps({})

    def describe_hub(self) -> str:
        params = self._parse_body()
        hub_arn = params.get("HubArn") or self._get_param("HubArn")
        hub_info = self.securityhub_backend.describe_hub(hub_arn=hub_arn)
        return json.dumps(hub_info)

    def update_security_hub_configuration(self) -> str:
        params = self._parse_body()
        auto_enable_controls = params.get("AutoEnableControls")
        control_finding_generator = params.get("ControlFindingGenerator")
        self.securityhub_backend.update_security_hub_configuration(
            auto_enable_controls=auto_enable_controls,
            control_finding_generator=control_finding_generator,
        )
        return json.dumps({})

    # --- Findings ---

    def get_findings(self) -> str:
        filters = self._get_param("Filters")
        sort_criteria = self._get_param("SortCriteria")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")

        findings, next_token = self.securityhub_backend.get_findings(
            filters=filters,
            sort_criteria=sort_criteria,
            max_results=max_results,
            next_token=next_token,
        )

        response = {"Findings": findings, "NextToken": next_token}
        return json.dumps(response)

    def batch_import_findings(self) -> str:
        body = self._parse_body()
        findings = body.get("Findings", [])
        failed_count, success_count, failed_findings = (
            self.securityhub_backend.batch_import_findings(findings=findings)
        )
        return json.dumps({
            "FailedCount": failed_count,
            "FailedFindings": [
                {
                    "ErrorCode": f.get("ErrorCode"),
                    "ErrorMessage": f.get("ErrorMessage"),
                    "Id": f.get("Id"),
                }
                for f in failed_findings
            ],
            "SuccessCount": success_count,
        })

    def batch_update_findings(self) -> str:
        body = self._parse_body()
        processed, unprocessed = self.securityhub_backend.batch_update_findings(
            finding_identifiers=body.get("FindingIdentifiers", []),
            note=body.get("Note"),
            severity=body.get("Severity"),
            verification_state=body.get("VerificationState"),
            confidence=body.get("Confidence"),
            criticality=body.get("Criticality"),
            types=body.get("Types"),
            user_defined_fields=body.get("UserDefinedFields"),
            workflow=body.get("Workflow"),
            related_findings=body.get("RelatedFindings"),
        )
        return json.dumps({
            "ProcessedFindings": processed,
            "UnprocessedFindings": unprocessed,
        })

    def update_findings(self) -> str:
        body = self._parse_body()
        self.securityhub_backend.update_findings(
            filters=body.get("Filters"),
            note=body.get("Note"),
            record_state=body.get("RecordState"),
        )
        return json.dumps({})

    def get_finding_history(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.get_finding_history(
            finding_identifier=body.get("FindingIdentifier", {}),
            start_time=body.get("StartTime"),
            end_time=body.get("EndTime"),
            max_results=body.get("MaxResults"),
            next_token=body.get("NextToken"),
        )
        return json.dumps(result)

    # --- Action Targets ---

    def create_action_target(self) -> str:
        body = self._parse_body()
        arn = self.securityhub_backend.create_action_target(
            name=body.get("Name", ""),
            description=body.get("Description", ""),
            target_id=body.get("Id", ""),
        )
        return json.dumps({"ActionTargetArn": arn})

    def describe_action_targets(self) -> str:
        body = self._parse_body()
        targets, next_token = self.securityhub_backend.describe_action_targets(
            action_target_arns=body.get("ActionTargetArns"),
            max_results=body.get("MaxResults"),
            next_token=body.get("NextToken"),
        )
        response: dict[str, Any] = {"ActionTargets": targets}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def update_action_target(self) -> str:
        body = self._parse_body()
        action_target_arn = unquote(self._get_param("ActionTargetArn") or "")
        # The ARN comes from the URL path
        if not action_target_arn:
            action_target_arn = self._extract_arn_from_path("actionTargets")
        self.securityhub_backend.update_action_target(
            action_target_arn=action_target_arn,
            name=body.get("Name"),
            description=body.get("Description"),
        )
        return json.dumps({})

    def delete_action_target(self) -> str:
        action_target_arn = self._extract_arn_from_path("actionTargets")
        arn = self.securityhub_backend.delete_action_target(action_target_arn)
        return json.dumps({"ActionTargetArn": arn})

    # --- Insights ---

    def create_insight(self) -> str:
        body = self._parse_body()
        arn = self.securityhub_backend.create_insight(
            name=body.get("Name", ""),
            filters=body.get("Filters", {}),
            group_by_attribute=body.get("GroupByAttribute", ""),
        )
        return json.dumps({"InsightArn": arn})

    def get_insights(self) -> str:
        body = self._parse_body()
        insights, next_token = self.securityhub_backend.get_insights(
            insight_arns=body.get("InsightArns"),
            max_results=body.get("MaxResults"),
            next_token=body.get("NextToken"),
        )
        response: dict[str, Any] = {"Insights": insights}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def get_insight_results(self) -> str:
        insight_arn = self._extract_arn_from_path("insights/results")
        results = self.securityhub_backend.get_insight_results(insight_arn)
        return json.dumps({"InsightResults": results})

    def update_insight(self) -> str:
        body = self._parse_body()
        insight_arn = self._extract_arn_from_path("insights")
        self.securityhub_backend.update_insight(
            insight_arn=insight_arn,
            name=body.get("Name"),
            filters=body.get("Filters"),
            group_by_attribute=body.get("GroupByAttribute"),
        )
        return json.dumps({})

    def delete_insight(self) -> str:
        insight_arn = self._extract_arn_from_path("insights")
        arn = self.securityhub_backend.delete_insight(insight_arn)
        return json.dumps({"InsightArn": arn})

    # --- Standards ---

    def batch_enable_standards(self) -> str:
        body = self._parse_body()
        subscriptions = self.securityhub_backend.batch_enable_standards(
            standards_subscription_requests=body.get(
                "StandardsSubscriptionRequests", []
            ),
        )
        return json.dumps({"StandardsSubscriptions": subscriptions})

    def batch_disable_standards(self) -> str:
        body = self._parse_body()
        subscriptions = self.securityhub_backend.batch_disable_standards(
            standards_subscription_arns=body.get("StandardsSubscriptionArns", []),
        )
        return json.dumps({"StandardsSubscriptions": subscriptions})

    def get_enabled_standards(self) -> str:
        body = self._parse_body()
        subscriptions, next_token = self.securityhub_backend.get_enabled_standards(
            standards_subscription_arns=body.get("StandardsSubscriptionArns"),
            max_results=body.get("MaxResults"),
            next_token=body.get("NextToken"),
        )
        response: dict[str, Any] = {"StandardsSubscriptions": subscriptions}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def describe_standards(self) -> str:
        standards, next_token = self.securityhub_backend.describe_standards(
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"Standards": standards}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def describe_standards_controls(self) -> str:
        standards_subscription_arn = self._extract_arn_from_path("standards/controls")
        controls, next_token = self.securityhub_backend.describe_standards_controls(
            standards_subscription_arn=standards_subscription_arn,
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"Controls": controls}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def update_standards_control(self) -> str:
        body = self._parse_body()
        standards_control_arn = self._extract_arn_from_path("standards/control")
        self.securityhub_backend.update_standards_control(
            standards_control_arn=standards_control_arn,
            control_status=body.get("ControlStatus"),
            disabled_reason=body.get("DisabledReason"),
        )
        return json.dumps({})

    def batch_get_standards_control_associations(self) -> str:
        body = self._parse_body()
        details, unprocessed = (
            self.securityhub_backend.batch_get_standards_control_associations(
                standards_control_association_ids=body.get(
                    "StandardsControlAssociationIds", []
                ),
            )
        )
        return json.dumps({
            "StandardsControlAssociationDetails": details,
            "UnprocessedAssociations": unprocessed,
        })

    def batch_update_standards_control_associations(self) -> str:
        body = self._parse_body()
        unprocessed = (
            self.securityhub_backend.batch_update_standards_control_associations(
                standards_control_association_updates=body.get(
                    "StandardsControlAssociationUpdates", []
                ),
            )
        )
        return json.dumps({"UnprocessedAssociationUpdates": unprocessed})

    def list_standards_control_associations(self) -> str:
        security_control_id = self._get_param("SecurityControlId") or ""
        assocs, next_token = (
            self.securityhub_backend.list_standards_control_associations(
                security_control_id=security_control_id,
                max_results=self._get_param("MaxResults"),
                next_token=self._get_param("NextToken"),
            )
        )
        response: dict[str, Any] = {
            "StandardsControlAssociationSummaries": assocs,
        }
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Automation Rules ---

    def create_automation_rule(self) -> str:
        body = self._parse_body()
        arn = self.securityhub_backend.create_automation_rule(
            rule_name=body.get("RuleName", ""),
            rule_order=body.get("RuleOrder", 1),
            rule_status=body.get("RuleStatus", "ENABLED"),
            description=body.get("Description", ""),
            is_terminal=body.get("IsTerminal", False),
            criteria=body.get("Criteria", {}),
            actions=body.get("Actions", []),
            tags=body.get("Tags"),
        )
        return json.dumps({"RuleArn": arn})

    def batch_get_automation_rules(self) -> str:
        body = self._parse_body()
        rules, unprocessed = self.securityhub_backend.batch_get_automation_rules(
            automation_rules_arns=body.get("AutomationRulesArns", []),
        )
        return json.dumps({
            "Rules": rules,
            "UnprocessedAutomationRules": unprocessed,
        })

    def batch_update_automation_rules(self) -> str:
        body = self._parse_body()
        processed, unprocessed = (
            self.securityhub_backend.batch_update_automation_rules(
                update_items=body.get("UpdateAutomationRulesRequestItems", []),
            )
        )
        return json.dumps({
            "ProcessedAutomationRules": processed,
            "UnprocessedAutomationRules": unprocessed,
        })

    def batch_delete_automation_rules(self) -> str:
        body = self._parse_body()
        processed, unprocessed = (
            self.securityhub_backend.batch_delete_automation_rules(
                automation_rules_arns=body.get("AutomationRulesArns", []),
            )
        )
        return json.dumps({
            "ProcessedAutomationRules": processed,
            "UnprocessedAutomationRules": unprocessed,
        })

    def list_automation_rules(self) -> str:
        rules, next_token = self.securityhub_backend.list_automation_rules(
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"AutomationRulesMetadata": rules}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Finding Aggregator ---

    def create_finding_aggregator(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.create_finding_aggregator(
            region_linking_mode=body.get("RegionLinkingMode", ""),
            regions=body.get("Regions"),
        )
        return json.dumps(result)

    def get_finding_aggregator(self) -> str:
        arn = self._extract_arn_from_path("findingAggregator/get")
        result = self.securityhub_backend.get_finding_aggregator(arn)
        return json.dumps(result)

    def update_finding_aggregator(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.update_finding_aggregator(
            finding_aggregator_arn=body.get("FindingAggregatorArn", ""),
            region_linking_mode=body.get("RegionLinkingMode", ""),
            regions=body.get("Regions"),
        )
        return json.dumps(result)

    def delete_finding_aggregator(self) -> str:
        arn = self._extract_arn_from_path("findingAggregator/delete")
        self.securityhub_backend.delete_finding_aggregator(arn)
        return json.dumps({})

    def list_finding_aggregators(self) -> str:
        aggs, next_token = self.securityhub_backend.list_finding_aggregators(
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"FindingAggregators": aggs}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Configuration Policies ---

    def create_configuration_policy(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.create_configuration_policy(
            name=body.get("Name", ""),
            description=body.get("Description", ""),
            configuration_policy=body.get("ConfigurationPolicy", {}),
            tags=body.get("Tags"),
        )
        return json.dumps(result)

    def get_configuration_policy(self) -> str:
        identifier = self._extract_path_param("configurationPolicy/get")
        result = self.securityhub_backend.get_configuration_policy(identifier)
        return json.dumps(result)

    def update_configuration_policy(self) -> str:
        body = self._parse_body()
        identifier = self._extract_path_param("configurationPolicy")
        result = self.securityhub_backend.update_configuration_policy(
            identifier=identifier,
            name=body.get("Name"),
            description=body.get("Description"),
            updated_reason=body.get("UpdatedReason"),
            configuration_policy=body.get("ConfigurationPolicy"),
        )
        return json.dumps(result)

    def delete_configuration_policy(self) -> str:
        identifier = self._extract_path_param("configurationPolicy")
        self.securityhub_backend.delete_configuration_policy(identifier)
        return json.dumps({})

    def list_configuration_policies(self) -> str:
        summaries, next_token = (
            self.securityhub_backend.list_configuration_policies(
                max_results=self._get_param("MaxResults"),
                next_token=self._get_param("NextToken"),
            )
        )
        response: dict[str, Any] = {"ConfigurationPolicySummaries": summaries}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Configuration Policy Associations ---

    def start_configuration_policy_association(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.start_configuration_policy_association(
            configuration_policy_identifier=body.get(
                "ConfigurationPolicyIdentifier", ""
            ),
            target=body.get("Target", {}),
        )
        return json.dumps(result)

    def start_configuration_policy_disassociation(self) -> str:
        body = self._parse_body()
        self.securityhub_backend.start_configuration_policy_disassociation(
            configuration_policy_identifier=body.get(
                "ConfigurationPolicyIdentifier", ""
            ),
            target=body.get("Target", {}),
        )
        return json.dumps({})

    def get_configuration_policy_association(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.get_configuration_policy_association(
            target=body.get("Target", {}),
        )
        return json.dumps(result)

    def batch_get_configuration_policy_associations(self) -> str:
        body = self._parse_body()
        results, unprocessed = (
            self.securityhub_backend.batch_get_configuration_policy_associations(
                configuration_policy_association_identifiers=body.get(
                    "ConfigurationPolicyAssociationIdentifiers", []
                ),
            )
        )
        return json.dumps({
            "ConfigurationPolicyAssociations": results,
            "UnprocessedConfigurationPolicyAssociations": unprocessed,
        })

    def list_configuration_policy_associations(self) -> str:
        body = self._parse_body()
        results, next_token = (
            self.securityhub_backend.list_configuration_policy_associations(
                max_results=body.get("MaxResults"),
                next_token=body.get("NextToken"),
                filters=body.get("Filters"),
            )
        )
        response: dict[str, Any] = {
            "ConfigurationPolicyAssociationSummaries": results,
        }
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Security Controls ---

    def batch_get_security_controls(self) -> str:
        body = self._parse_body()
        controls, unprocessed = self.securityhub_backend.batch_get_security_controls(
            security_control_ids=body.get("SecurityControlIds", []),
        )
        return json.dumps({
            "SecurityControls": controls,
            "UnprocessedIds": unprocessed,
        })

    def update_security_control(self) -> str:
        body = self._parse_body()
        self.securityhub_backend.update_security_control(
            security_control_id=body.get("SecurityControlId", ""),
            parameters=body.get("Parameters", {}),
            last_update_reason=body.get("LastUpdateReason"),
        )
        return json.dumps({})

    def get_security_control_definition(self) -> str:
        security_control_id = self._get_param("SecurityControlId") or ""
        result = self.securityhub_backend.get_security_control_definition(
            security_control_id
        )
        return json.dumps(result)

    def list_security_control_definitions(self) -> str:
        defs, next_token = (
            self.securityhub_backend.list_security_control_definitions(
                standards_arn=self._get_param("StandardsArn"),
                max_results=self._get_param("MaxResults"),
                next_token=self._get_param("NextToken"),
            )
        )
        response: dict[str, Any] = {"SecurityControlDefinitions": defs}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Products ---

    def describe_products(self) -> str:
        products, next_token = self.securityhub_backend.describe_products(
            product_arn=self._get_param("ProductArn"),
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"Products": products}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def enable_import_findings_for_product(self) -> str:
        body = self._parse_body()
        sub_arn = self.securityhub_backend.enable_import_findings_for_product(
            product_arn=body.get("ProductArn", ""),
        )
        return json.dumps({"ProductSubscriptionArn": sub_arn})

    def disable_import_findings_for_product(self) -> str:
        sub_arn = self._extract_arn_from_path("productSubscriptions")
        self.securityhub_backend.disable_import_findings_for_product(sub_arn)
        return json.dumps({})

    def list_enabled_products_for_import(self) -> str:
        subs, next_token = (
            self.securityhub_backend.list_enabled_products_for_import(
                max_results=self._get_param("MaxResults"),
                next_token=self._get_param("NextToken"),
            )
        )
        response: dict[str, Any] = {"ProductSubscriptions": subs}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Members ---

    def create_members(self) -> str:
        params = self._parse_body()
        account_details = params.get("AccountDetails", [])
        unprocessed_accounts = self.securityhub_backend.create_members(
            account_details=account_details,
        )
        return json.dumps({"UnprocessedAccounts": unprocessed_accounts})

    def get_members(self) -> str:
        params = self._parse_body()
        account_ids = params.get("AccountIds", [])
        members, unprocessed_accounts = self.securityhub_backend.get_members(
            account_ids=account_ids,
        )
        return json.dumps(
            {"Members": members, "UnprocessedAccounts": unprocessed_accounts}
        )

    def list_members(self) -> str:
        only_associated = self._get_param("OnlyAssociated")
        max_results = self._get_param("MaxResults")
        if max_results is not None:
            max_results = int(max_results)
        next_token = self._get_param("NextToken")

        members, next_token = self.securityhub_backend.list_members(
            only_associated=only_associated,
            max_results=max_results,
            next_token=next_token,
        )
        response: dict[str, Any] = {"Members": members}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def delete_members(self) -> str:
        body = self._parse_body()
        unprocessed = self.securityhub_backend.delete_members(
            account_ids=body.get("AccountIds", []),
        )
        return json.dumps({"UnprocessedAccounts": unprocessed})

    def disassociate_members(self) -> str:
        body = self._parse_body()
        self.securityhub_backend.disassociate_members(
            account_ids=body.get("AccountIds", []),
        )
        return json.dumps({})

    def invite_members(self) -> str:
        body = self._parse_body()
        unprocessed = self.securityhub_backend.invite_members(
            account_ids=body.get("AccountIds", []),
        )
        return json.dumps({"UnprocessedAccounts": unprocessed})

    # --- Invitations ---

    def accept_administrator_invitation(self) -> str:
        body = self._parse_body()
        self.securityhub_backend.accept_administrator_invitation(
            administrator_id=body.get("AdministratorId", ""),
            invitation_id=body.get("InvitationId", ""),
        )
        return json.dumps({})

    def accept_invitation(self) -> str:
        body = self._parse_body()
        self.securityhub_backend.accept_invitation(
            master_id=body.get("MasterId", ""),
            invitation_id=body.get("InvitationId", ""),
        )
        return json.dumps({})

    def decline_invitations(self) -> str:
        body = self._parse_body()
        unprocessed = self.securityhub_backend.decline_invitations(
            account_ids=body.get("AccountIds", []),
        )
        return json.dumps({"UnprocessedAccounts": unprocessed})

    def delete_invitations(self) -> str:
        body = self._parse_body()
        unprocessed = self.securityhub_backend.delete_invitations(
            account_ids=body.get("AccountIds", []),
        )
        return json.dumps({"UnprocessedAccounts": unprocessed})

    def list_invitations(self) -> str:
        invitations, next_token = self.securityhub_backend.list_invitations(
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"Invitations": invitations}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def get_invitations_count(self) -> str:
        count = self.securityhub_backend.get_invitations_count()
        return json.dumps({"InvitationsCount": count})

    def disassociate_from_administrator_account(self) -> str:
        self.securityhub_backend.disassociate_from_administrator_account()
        return json.dumps({})

    def disassociate_from_master_account(self) -> str:
        self.securityhub_backend.disassociate_from_master_account()
        return json.dumps({})

    # --- Organization Admin ---

    def enable_organization_admin_account(self) -> str:
        params = self._parse_body()
        admin_account_id = params.get("AdminAccountId")
        self.securityhub_backend.enable_organization_admin_account(
            admin_account_id=admin_account_id,
        )
        return json.dumps({})

    def disable_organization_admin_account(self) -> str:
        body = self._parse_body()
        self.securityhub_backend.disable_organization_admin_account(
            admin_account_id=body.get("AdminAccountId", ""),
        )
        return json.dumps({})

    def list_organization_admin_accounts(self) -> str:
        accounts, next_token = (
            self.securityhub_backend.list_organization_admin_accounts(
                max_results=self._get_param("MaxResults"),
                next_token=self._get_param("NextToken"),
            )
        )
        response: dict[str, Any] = {"AdminAccounts": accounts}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def update_organization_configuration(self) -> str:
        params = self._parse_body()
        auto_enable = params.get("AutoEnable")
        auto_enable_standards = params.get("AutoEnableStandards")
        organization_configuration = params.get("OrganizationConfiguration")
        self.securityhub_backend.update_organization_configuration(
            auto_enable=auto_enable,
            auto_enable_standards=auto_enable_standards,
            organization_configuration=organization_configuration,
        )
        return json.dumps({})

    def get_administrator_account(self) -> str:
        administrator = self.securityhub_backend.get_administrator_account()
        return json.dumps(administrator)

    def describe_organization_configuration(self) -> str:
        response = self.securityhub_backend.describe_organization_configuration()
        return json.dumps(dict(response))

    def get_master_account(self) -> str:
        master = self.securityhub_backend.get_master_account()
        return json.dumps(master)

    # --- Tags ---

    def tag_resource(self) -> str:
        body = self._parse_body()
        resource_arn = self._extract_arn_from_path("tags")
        self.securityhub_backend.tag_resource(
            resource_arn=resource_arn,
            tags=body.get("Tags", {}),
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = self._extract_arn_from_path("tags")
        tag_keys = self.querystring.get("tagKeys", [])
        if isinstance(tag_keys, str):
            tag_keys = [tag_keys]
        self.securityhub_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = self._extract_arn_from_path("tags")
        tags = self.securityhub_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"Tags": tags})

    # --- V2 APIs ---

    def batch_update_findings_v2(self) -> str:
        body = self._parse_body()
        processed, unprocessed = self.securityhub_backend.batch_update_findings_v2(
            metadata_uids=body.get("MetadataUids"),
            finding_identifiers=body.get("FindingIdentifiers"),
            comment=body.get("Comment"),
            severity_id=body.get("SeverityId"),
            status_id=body.get("StatusId"),
        )
        return json.dumps({
            "ProcessedFindings": processed,
            "UnprocessedFindings": unprocessed,
        })

    def get_findings_v2(self) -> str:
        body = self._parse_body()
        findings, next_token = self.securityhub_backend.get_findings_v2(
            filters=body.get("Filters"),
            sort_criteria=body.get("SortCriteria"),
            max_results=body.get("MaxResults"),
            next_token=body.get("NextToken"),
        )
        response: dict[str, Any] = {"Findings": findings}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def get_finding_statistics_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.get_finding_statistics_v2(
            group_by_rules=body.get("GroupByRules"),
            sort_order=body.get("SortOrder"),
            max_statistic_results=body.get("MaxStatisticResults"),
        )
        return json.dumps(result)

    def get_findings_trends_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.get_findings_trends_v2(
            filters=body.get("Filters"),
            start_time=body.get("StartTime"),
            end_time=body.get("EndTime"),
            max_results=body.get("MaxResults"),
            next_token=body.get("NextToken"),
        )
        return json.dumps(result)

    def get_resources_v2(self) -> str:
        body = self._parse_body()
        resources, next_token = self.securityhub_backend.get_resources_v2(
            filters=body.get("Filters"),
            sort_criteria=body.get("SortCriteria"),
            max_results=body.get("MaxResults"),
            next_token=body.get("NextToken"),
        )
        response: dict[str, Any] = {"Resources": resources}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def get_resources_statistics_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.get_resources_statistics_v2(
            group_by_rules=body.get("GroupByRules"),
            sort_order=body.get("SortOrder"),
            max_statistic_results=body.get("MaxStatisticResults"),
        )
        return json.dumps(result)

    def get_resources_trends_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.get_resources_trends_v2(
            filters=body.get("Filters"),
            start_time=body.get("StartTime"),
            end_time=body.get("EndTime"),
            max_results=body.get("MaxResults"),
            next_token=body.get("NextToken"),
        )
        return json.dumps(result)

    def describe_products_v2(self) -> str:
        products, next_token = self.securityhub_backend.describe_products_v2(
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"ProductsV2": products}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def enable_security_hub_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.enable_security_hub_v2(
            tags=body.get("Tags"),
        )
        return json.dumps(result)

    def disable_security_hub_v2(self) -> str:
        self.securityhub_backend.disable_security_hub_v2()
        return json.dumps({})

    def describe_security_hub_v2(self) -> str:
        result = self.securityhub_backend.describe_security_hub_v2()
        return json.dumps(result)

    # --- Automation Rules V2 ---

    def create_automation_rule_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.create_automation_rule_v2(
            rule_name=body.get("RuleName", ""),
            rule_status=body.get("RuleStatus", "ENABLED"),
            description=body.get("Description", ""),
            rule_order=body.get("RuleOrder", 1),
            criteria=body.get("Criteria", {}),
            actions=body.get("Actions", []),
            tags=body.get("Tags"),
        )
        return json.dumps(result)

    def get_automation_rule_v2(self) -> str:
        identifier = self._extract_path_param("automationrulesv2")
        result = self.securityhub_backend.get_automation_rule_v2(identifier)
        return json.dumps(result)

    def update_automation_rule_v2(self) -> str:
        body = self._parse_body()
        identifier = self._extract_path_param("automationrulesv2")
        self.securityhub_backend.update_automation_rule_v2(
            identifier=identifier,
            rule_status=body.get("RuleStatus"),
            rule_order=body.get("RuleOrder"),
            description=body.get("Description"),
            rule_name=body.get("RuleName"),
            criteria=body.get("Criteria"),
            actions=body.get("Actions"),
        )
        return json.dumps({})

    def delete_automation_rule_v2(self) -> str:
        identifier = self._extract_path_param("automationrulesv2")
        self.securityhub_backend.delete_automation_rule_v2(identifier)
        return json.dumps({})

    def list_automation_rules_v2(self) -> str:
        rules, next_token = self.securityhub_backend.list_automation_rules_v2(
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"Rules": rules}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Aggregator V2 ---

    def create_aggregator_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.create_aggregator_v2(
            region_linking_mode=body.get("RegionLinkingMode", ""),
            linked_regions=body.get("LinkedRegions"),
            tags=body.get("Tags"),
        )
        return json.dumps(result)

    def get_aggregator_v2(self) -> str:
        arn = self._extract_arn_from_path("aggregatorv2/get")
        result = self.securityhub_backend.get_aggregator_v2(arn)
        return json.dumps(result)

    def update_aggregator_v2(self) -> str:
        body = self._parse_body()
        arn = self._extract_arn_from_path("aggregatorv2/update")
        result = self.securityhub_backend.update_aggregator_v2(
            aggregator_v2_arn=arn,
            region_linking_mode=body.get("RegionLinkingMode"),
            linked_regions=body.get("LinkedRegions"),
        )
        return json.dumps(result)

    def delete_aggregator_v2(self) -> str:
        arn = self._extract_arn_from_path("aggregatorv2/delete")
        self.securityhub_backend.delete_aggregator_v2(arn)
        return json.dumps({})

    def list_aggregators_v2(self) -> str:
        aggs, next_token = self.securityhub_backend.list_aggregators_v2(
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        response: dict[str, Any] = {"AggregatorsV2": aggs}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    # --- Connector V2 ---

    def create_connector_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.create_connector_v2(
            name=body.get("Name", ""),
            description=body.get("Description", ""),
            provider=body.get("Provider", {}),
            kms_key_arn=body.get("KmsKeyArn", ""),
            tags=body.get("Tags"),
        )
        return json.dumps(result)

    def get_connector_v2(self) -> str:
        connector_id = self._extract_path_param("connectorsv2")
        result = self.securityhub_backend.get_connector_v2(connector_id)
        return json.dumps(result)

    def update_connector_v2(self) -> str:
        body = self._parse_body()
        connector_id = self._extract_path_param("connectorsv2")
        self.securityhub_backend.update_connector_v2(
            connector_id=connector_id,
            description=body.get("Description"),
            provider=body.get("Provider"),
        )
        return json.dumps({})

    def delete_connector_v2(self) -> str:
        connector_id = self._extract_path_param("connectorsv2")
        self.securityhub_backend.delete_connector_v2(connector_id)
        return json.dumps({})

    def list_connectors_v2(self) -> str:
        connectors, next_token = self.securityhub_backend.list_connectors_v2(
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
            provider_name=self._get_param("ProviderName"),
            connector_status=self._get_param("ConnectorStatus"),
        )
        response: dict[str, Any] = {"Connectors": connectors}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def register_connector_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.register_connector_v2(
            auth_code=body.get("AuthCode", ""),
            auth_state=body.get("AuthState", ""),
        )
        return json.dumps(result)

    # --- Tickets V2 ---

    def create_ticket_v2(self) -> str:
        body = self._parse_body()
        result = self.securityhub_backend.create_ticket_v2(
            connector_id=body.get("ConnectorId", ""),
            finding_metadata_uid=body.get("FindingMetadataUid", ""),
            mode=body.get("Mode"),
        )
        return json.dumps(result)

    # --- Helpers ---

    def _extract_arn_from_path(self, prefix: str) -> str:
        """Extract an ARN-like value from the URL path after a given prefix.

        For REST-JSON SecurityHub, the path looks like:
        /actionTargets/arn:aws:securityhub:...
        /insights/arn:aws:securityhub:...
        """
        path = unquote(self.path)
        idx = path.find(f"/{prefix}/")
        if idx >= 0:
            return path[idx + len(prefix) + 2 :]
        return ""

    def _extract_path_param(self, prefix: str) -> str:
        """Extract a single path parameter after a prefix.

        E.g., /configurationPolicy/get/{Identifier} -> Identifier
              /automationrulesv2/{Identifier} -> Identifier
        """
        path = unquote(self.path)
        idx = path.find(f"/{prefix}/")
        if idx >= 0:
            return path[idx + len(prefix) + 2 :]
        return ""
