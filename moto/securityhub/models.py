"""SecurityHubBackend class with methods for supported APIs."""

import datetime
import uuid
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.exceptions import RESTError
from moto.core.utils import iso_8601_datetime_with_milliseconds
from moto.organizations.exceptions import AWSOrganizationsNotInUseException
from moto.organizations.models import organizations_backends
from moto.securityhub.exceptions import InvalidInputException
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService


def _utc_now() -> str:
    return iso_8601_datetime_with_milliseconds(
        datetime.datetime.now(datetime.timezone.utc)
    )


class Finding(BaseModel):
    def __init__(self, finding_id: str, finding_data: dict[str, Any]):
        self.id = finding_id
        self.data = finding_data

    def as_dict(self) -> dict[str, Any]:
        return self.data


class ActionTarget(BaseModel):
    def __init__(self, arn: str, name: str, description: str):
        self.arn = arn
        self.name = name
        self.description = description

    def as_dict(self) -> dict[str, Any]:
        return {
            "ActionTargetArn": self.arn,
            "Name": self.name,
            "Description": self.description,
        }


class Insight(BaseModel):
    def __init__(
        self,
        arn: str,
        name: str,
        filters: dict[str, Any],
        group_by_attribute: str,
    ):
        self.arn = arn
        self.name = name
        self.filters = filters
        self.group_by_attribute = group_by_attribute

    def as_dict(self) -> dict[str, Any]:
        return {
            "InsightArn": self.arn,
            "Name": self.name,
            "Filters": self.filters,
            "GroupByAttribute": self.group_by_attribute,
        }


class StandardsSubscription(BaseModel):
    def __init__(
        self,
        standards_arn: str,
        standards_input: Optional[dict[str, str]],
        region: str,
        account_id: str,
    ):
        self.standards_arn = standards_arn
        self.standards_input = standards_input or {}
        self.standards_subscription_arn = (
            f"arn:aws:securityhub:{region}:{account_id}:"
            f"subscription/{standards_arn.split('/')[-1]}"
        )
        self.standards_status = "READY"

    def as_dict(self) -> dict[str, Any]:
        return {
            "StandardsArn": self.standards_arn,
            "StandardsSubscriptionArn": self.standards_subscription_arn,
            "StandardsInput": self.standards_input,
            "StandardsStatus": self.standards_status,
        }


class StandardsControl(BaseModel):
    def __init__(
        self,
        control_id: str,
        standards_control_arn: str,
        title: str,
        description: str,
    ):
        self.control_id = control_id
        self.standards_control_arn = standards_control_arn
        self.control_status = "ENABLED"
        self.disabled_reason = ""
        self.title = title
        self.description = description
        self.severity_rating = "MEDIUM"
        self.related_requirements: list[str] = []
        self.remediation_url = ""

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "StandardsControlArn": self.standards_control_arn,
            "ControlStatus": self.control_status,
            "ControlId": self.control_id,
            "Title": self.title,
            "Description": self.description,
            "SeverityRating": self.severity_rating,
            "RelatedRequirements": self.related_requirements,
            "RemediationUrl": self.remediation_url,
        }
        if self.disabled_reason:
            result["DisabledReason"] = self.disabled_reason
        return result


class AutomationRule(BaseModel):
    def __init__(
        self,
        arn: str,
        rule_name: str,
        rule_order: int,
        rule_status: str,
        description: str,
        is_terminal: bool,
        criteria: dict[str, Any],
        actions: list[dict[str, Any]],
        created_at: str,
    ):
        self.arn = arn
        self.rule_name = rule_name
        self.rule_order = rule_order
        self.rule_status = rule_status
        self.description = description
        self.is_terminal = is_terminal
        self.criteria = criteria
        self.actions = actions
        self.created_at = created_at
        self.updated_at = created_at

    def as_dict(self) -> dict[str, Any]:
        return {
            "RuleArn": self.arn,
            "RuleName": self.rule_name,
            "RuleOrder": self.rule_order,
            "RuleStatus": self.rule_status,
            "Description": self.description,
            "IsTerminal": self.is_terminal,
            "Criteria": self.criteria,
            "Actions": self.actions,
            "CreatedAt": self.created_at,
            "UpdatedAt": self.updated_at,
        }

    def as_metadata(self) -> dict[str, Any]:
        return {
            "RuleArn": self.arn,
            "RuleName": self.rule_name,
            "RuleOrder": self.rule_order,
            "RuleStatus": self.rule_status,
            "Description": self.description,
            "IsTerminal": self.is_terminal,
            "CreatedAt": self.created_at,
            "UpdatedAt": self.updated_at,
        }


class FindingAggregator(BaseModel):
    def __init__(
        self,
        arn: str,
        region: str,
        region_linking_mode: str,
        regions: Optional[list[str]],
    ):
        self.arn = arn
        self.finding_aggregation_region = region
        self.region_linking_mode = region_linking_mode
        self.regions = regions or []

    def as_dict(self) -> dict[str, Any]:
        return {
            "FindingAggregatorArn": self.arn,
            "FindingAggregationRegion": self.finding_aggregation_region,
            "RegionLinkingMode": self.region_linking_mode,
            "Regions": self.regions,
        }


class ConfigurationPolicy(BaseModel):
    def __init__(
        self,
        policy_id: str,
        arn: str,
        name: str,
        description: str,
        configuration_policy: dict[str, Any],
        created_at: str,
    ):
        self.id = policy_id
        self.arn = arn
        self.name = name
        self.description = description
        self.configuration_policy = configuration_policy
        self.created_at = created_at
        self.updated_at = created_at

    def as_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
            "ConfigurationPolicy": self.configuration_policy,
            "CreatedAt": self.created_at,
            "UpdatedAt": self.updated_at,
        }

    def as_summary(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
            "UpdatedAt": self.updated_at,
            "ServiceEnabled": self.configuration_policy.get(
                "SecurityHub", {}
            ).get("ServiceEnabled", False),
        }


class ConfigurationPolicyAssociation(BaseModel):
    def __init__(
        self,
        configuration_policy_id: str,
        target_id: str,
        target_type: str,
        association_type: str,
    ):
        self.configuration_policy_id = configuration_policy_id
        self.target_id = target_id
        self.target_type = target_type
        self.association_type = association_type
        self.association_status = "SUCCESS"
        self.association_status_message = ""
        self.updated_at = _utc_now()

    def as_dict(self) -> dict[str, Any]:
        return {
            "ConfigurationPolicyId": self.configuration_policy_id,
            "TargetId": self.target_id,
            "TargetType": self.target_type,
            "AssociationType": self.association_type,
            "UpdatedAt": self.updated_at,
            "AssociationStatus": self.association_status,
            "AssociationStatusMessage": self.association_status_message,
        }


class SecurityControl(BaseModel):
    def __init__(self, security_control_id: str, parameters: dict[str, Any]):
        self.security_control_id = security_control_id
        self.parameters = parameters
        self.last_update_reason = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "SecurityControlId": self.security_control_id,
            "SecurityControlArn": "",
            "Title": self.security_control_id,
            "Description": f"Control {self.security_control_id}",
            "RemediationUrl": "",
            "SeverityRating": "MEDIUM",
            "SecurityControlStatus": "ENABLED",
            "Parameters": self.parameters,
            "LastUpdateReason": self.last_update_reason,
        }


class Product(BaseModel):
    """Represents an AWS or third-party product integration."""

    def __init__(self, product_arn: str, product_name: str, company_name: str):
        self.product_arn = product_arn
        self.product_name = product_name
        self.company_name = company_name

    def as_dict(self) -> dict[str, Any]:
        return {
            "ProductArn": self.product_arn,
            "ProductName": self.product_name,
            "CompanyName": self.company_name,
            "Description": f"{self.product_name} integration",
            "Categories": ["Software and Configuration Checks"],
            "IntegrationTypes": ["SEND_FINDINGS_TO_SECURITY_HUB"],
            "MarketplaceUrl": "",
            "ActivationUrl": "",
            "ProductSubscriptionResourcePolicy": "",
        }


class AutomationRuleV2(BaseModel):
    def __init__(
        self,
        rule_id: str,
        arn: str,
        rule_name: str,
        rule_order: int,
        rule_status: str,
        description: str,
        criteria: dict[str, Any],
        actions: list[dict[str, Any]],
        created_at: str,
    ):
        self.rule_id = rule_id
        self.arn = arn
        self.rule_name = rule_name
        self.rule_order = rule_order
        self.rule_status = rule_status
        self.description = description
        self.criteria = criteria
        self.actions = actions
        self.created_at = created_at
        self.updated_at = created_at

    def as_dict(self) -> dict[str, Any]:
        return {
            "RuleArn": self.arn,
            "RuleId": self.rule_id,
            "RuleOrder": self.rule_order,
            "RuleName": self.rule_name,
            "RuleStatus": self.rule_status,
            "Description": self.description,
            "Criteria": self.criteria,
            "Actions": self.actions,
            "CreatedAt": self.created_at,
            "UpdatedAt": self.updated_at,
        }

    def as_summary(self) -> dict[str, Any]:
        return {
            "RuleArn": self.arn,
            "RuleId": self.rule_id,
            "RuleName": self.rule_name,
            "RuleStatus": self.rule_status,
            "RuleOrder": self.rule_order,
            "Description": self.description,
            "CreatedAt": self.created_at,
            "UpdatedAt": self.updated_at,
        }


class AggregatorV2(BaseModel):
    def __init__(
        self,
        arn: str,
        aggregation_region: str,
        region_linking_mode: str,
        linked_regions: Optional[list[str]],
    ):
        self.arn = arn
        self.aggregation_region = aggregation_region
        self.region_linking_mode = region_linking_mode
        self.linked_regions = linked_regions or []

    def as_dict(self) -> dict[str, Any]:
        return {
            "AggregatorV2Arn": self.arn,
            "AggregationRegion": self.aggregation_region,
            "RegionLinkingMode": self.region_linking_mode,
            "LinkedRegions": self.linked_regions,
        }


class ConnectorV2(BaseModel):
    def __init__(
        self,
        connector_id: str,
        arn: str,
        name: str,
        description: str,
        provider: dict[str, Any],
        kms_key_arn: str,
        created_at: str,
    ):
        self.connector_id = connector_id
        self.arn = arn
        self.name = name
        self.description = description
        self.provider = provider
        self.kms_key_arn = kms_key_arn
        self.created_at = created_at
        self.last_updated_at = created_at
        self.status = "CONNECTED"
        self.health: dict[str, Any] = {
            "ConnectorStatus": "CONNECTED",
            "Message": "",
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "ConnectorArn": self.arn,
            "ConnectorId": self.connector_id,
            "Name": self.name,
            "Description": self.description,
            "KmsKeyArn": self.kms_key_arn,
            "CreatedAt": self.created_at,
            "LastUpdatedAt": self.last_updated_at,
            "Health": self.health,
            "ProviderDetail": self.provider,
        }

    def as_summary(self) -> dict[str, Any]:
        return {
            "ConnectorArn": self.arn,
            "ConnectorId": self.connector_id,
            "Name": self.name,
            "Description": self.description,
            "ConnectorStatus": self.status,
            "CreatedAt": self.created_at,
        }


# Built-in AWS standards
_BUILTIN_STANDARDS = [
    {
        "StandardsArn": "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0",
        "Name": "CIS AWS Foundations Benchmark v1.2.0",
        "Description": "The Center for Internet Security (CIS) AWS Foundations Benchmark v1.2.0",
        "EnabledByDefault": True,
    },
    {
        "StandardsArn": "arn:aws:securityhub::{region}::standards/aws-foundational-security-best-practices/v/1.0.0",
        "Name": "AWS Foundational Security Best Practices v1.0.0",
        "Description": "AWS Foundational Security Best Practices",
        "EnabledByDefault": True,
    },
    {
        "StandardsArn": "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.4.0",
        "Name": "CIS AWS Foundations Benchmark v1.4.0",
        "Description": "The Center for Internet Security (CIS) AWS Foundations Benchmark v1.4.0",
        "EnabledByDefault": False,
    },
    {
        "StandardsArn": "arn:aws:securityhub:::standards/pci-dss/v/3.2.1",
        "Name": "PCI DSS v3.2.1",
        "Description": "Payment Card Industry Data Security Standard (PCI DSS) v3.2.1",
        "EnabledByDefault": False,
    },
]

# Built-in products
_BUILTIN_PRODUCTS = [
    ("arn:aws:securityhub:{region}::product/aws/guardduty", "GuardDuty", "Amazon"),
    ("arn:aws:securityhub:{region}::product/aws/inspector", "Inspector", "Amazon"),
    ("arn:aws:securityhub:{region}::product/aws/macie", "Macie", "Amazon"),
    ("arn:aws:securityhub:{region}::product/aws/config", "Config", "Amazon"),
    ("arn:aws:securityhub:{region}::product/aws/firewall-manager", "Firewall Manager", "Amazon"),
    ("arn:aws:securityhub:{region}::product/aws/access-analyzer", "IAM Access Analyzer", "Amazon"),
    (
        "arn:aws:securityhub:{region}::product/aws/systems-manager-patch-manager",
        "Systems Manager Patch Manager",
        "Amazon",
    ),
]


class SecurityHubBackend(BaseBackend):
    """Implementation of SecurityHub APIs."""

    PAGINATION_MODEL = {
        "get_findings": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "Id",
            "fail_on_invalid_token": True,
        },
        "list_members": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 50,
            "unique_attribute": "AccountId",
            "fail_on_invalid_token": False,
        },
    }

    _org_configs: dict[str, dict[str, Any]] = {}

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.findings: list[Finding] = []
        self.region_name = region_name
        self.org_backend = organizations_backends[self.account_id]["aws"]
        self.enabled_at: Optional[str] = None
        self.enabled = False
        self.auto_enable_controls = True
        self.control_finding_generator = "SECURITY_CONTROL"
        self.members: dict[str, dict[str, str]] = {}
        self.tags: dict[str, str] = {}
        self.action_targets: dict[str, ActionTarget] = {}
        self.insights: dict[str, Insight] = {}
        self.standards_subscriptions: dict[str, StandardsSubscription] = {}
        self.standards_controls: dict[str, StandardsControl] = {}
        self.automation_rules: dict[str, AutomationRule] = {}
        self.finding_aggregators: dict[str, FindingAggregator] = {}
        self.configuration_policies: dict[str, ConfigurationPolicy] = {}
        self.configuration_policy_associations: dict[
            str, ConfigurationPolicyAssociation
        ] = {}
        self.security_controls: dict[str, SecurityControl] = {}
        self.product_subscriptions: dict[str, str] = {}
        self.invitations: list[dict[str, Any]] = []
        self.automation_rules_v2: dict[str, AutomationRuleV2] = {}
        self.aggregators_v2: dict[str, AggregatorV2] = {}
        self.connectors_v2: dict[str, ConnectorV2] = {}
        self.hub_v2_arn: Optional[str] = None
        self.hub_v2_subscribed_at: Optional[str] = None
        self.tagger = TaggingService()

    def _get_org_config(self) -> dict[str, Any]:
        """Get organization config for the current account."""
        try:
            org = self.org_backend.describe_organization()
            org_id = org["Organization"]["Id"]
        except RESTError:
            raise AWSOrganizationsNotInUseException()

        if org_id not in SecurityHubBackend._org_configs:
            SecurityHubBackend._org_configs[org_id] = {
                "admin_account_id": None,
                "auto_enable": False,
                "auto_enable_standards": "DEFAULT",
                "configuration": {
                    "ConfigurationType": "LOCAL",
                    "Status": "ENABLED",
                    "StatusMessage": "",
                },
            }
        return SecurityHubBackend._org_configs[org_id]

    def _hub_arn(self) -> str:
        return f"arn:aws:securityhub:{self.region_name}:{self.account_id}:hub/default"

    def enable_security_hub(
        self,
        enable_default_standards: bool = True,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        if self.enabled:
            return {}

        self.enabled = True
        self.enabled_at = _utc_now()
        self.tags = tags or {}

        if tags:
            self.tagger.tag_resource(self._hub_arn(), [
                {"Key": k, "Value": v} for k, v in tags.items()
            ])

        if enable_default_standards:
            pass

        return {}

    def disable_security_hub(self) -> dict[str, Any]:
        if not self.enabled:
            raise RESTError(
                "InvalidAccessException",
                "Account is not subscribed to AWS Security Hub",
            )

        self.enabled = False
        self.enabled_at = None
        self.findings = []

        return {}

    def describe_hub(self, hub_arn: Optional[str] = None) -> dict[str, Any]:
        if not self.enabled:
            raise RESTError(
                "InvalidAccessException",
                "Account is not subscribed to AWS Security Hub",
            )

        expected_arn = self._hub_arn()
        if hub_arn and hub_arn != expected_arn:
            raise RESTError(
                "ResourceNotFoundException",
                f"The request was rejected because no hub was found with ARN {hub_arn}.",
            )

        return {
            "HubArn": expected_arn,
            "SubscribedAt": self.enabled_at,
            "AutoEnableControls": self.auto_enable_controls,
            "ControlFindingGenerator": self.control_finding_generator,
            "Tags": self.tags or {},
        }

    def update_security_hub_configuration(
        self,
        auto_enable_controls: Optional[bool] = None,
        control_finding_generator: Optional[str] = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            raise RESTError(
                "InvalidAccessException",
                "Account is not subscribed to AWS Security Hub",
            )
        if auto_enable_controls is not None:
            self.auto_enable_controls = auto_enable_controls
        if control_finding_generator is not None:
            self.control_finding_generator = control_finding_generator
        return {}

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_findings(
        self,
        filters: Optional[dict[str, Any]] = None,
        sort_criteria: Optional[list[dict[str, str]]] = None,
        max_results: Optional[int] = None,
    ) -> list[dict[str, str]]:
        """
        Filters and SortCriteria is not yet implemented
        """
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1 or max_results > 100:
                    raise InvalidInputException(
                        op="GetFindings",
                        msg="MaxResults must be a number between 1 and 100",
                    )
            except ValueError:
                raise InvalidInputException(
                    op="GetFindings", msg="MaxResults must be a number greater than 0"
                )

        return [f.as_dict() for f in self.findings]

    def batch_import_findings(
        self, findings: list[dict[str, Any]]
    ) -> tuple[int, int, list[dict[str, Any]]]:
        failed_count = 0
        success_count = 0
        failed_findings = []

        for finding_data in findings:
            try:
                if (
                    not isinstance(finding_data["Resources"], list)
                    or len(finding_data["Resources"]) == 0
                ):
                    raise InvalidInputException(
                        op="BatchImportFindings",
                        msg="Finding must contain at least one resource in the Resources array",
                    )

                finding_id = finding_data["Id"]

                existing_finding = next(
                    (f for f in self.findings if f.id == finding_id), None
                )

                if existing_finding:
                    existing_finding.data.update(finding_data)
                else:
                    new_finding = Finding(finding_id, finding_data)
                    self.findings.append(new_finding)

                success_count += 1

            except Exception as e:
                failed_count += 1
                failed_findings.append(
                    {
                        "Id": finding_data.get("Id", ""),
                        "ErrorCode": "InvalidInput",
                        "ErrorMessage": str(e),
                    }
                )

        return failed_count, success_count, failed_findings

    def batch_update_findings(
        self,
        finding_identifiers: list[dict[str, str]],
        note: Optional[dict[str, str]] = None,
        severity: Optional[dict[str, Any]] = None,
        verification_state: Optional[str] = None,
        confidence: Optional[int] = None,
        criticality: Optional[int] = None,
        types: Optional[list[str]] = None,
        user_defined_fields: Optional[dict[str, str]] = None,
        workflow: Optional[dict[str, str]] = None,
        related_findings: Optional[list[dict[str, str]]] = None,
    ) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
        processed = []
        unprocessed = []

        for identifier in finding_identifiers:
            finding_id = identifier.get("Id", "")
            product_arn = identifier.get("ProductArn", "")
            existing = next((f for f in self.findings if f.id == finding_id), None)
            if not existing:
                unprocessed.append({
                    "FindingIdentifier": identifier,
                    "ErrorCode": "FindingNotFound",
                    "ErrorMessage": f"Finding with Id {finding_id} not found",
                })
                continue

            if note:
                existing.data["Note"] = note
            if severity:
                existing.data.setdefault("Severity", {}).update(severity)
            if verification_state:
                existing.data["VerificationState"] = verification_state
            if confidence is not None:
                existing.data["Confidence"] = confidence
            if criticality is not None:
                existing.data["Criticality"] = criticality
            if types:
                existing.data["Types"] = types
            if user_defined_fields:
                existing.data.setdefault("UserDefinedFields", {}).update(
                    user_defined_fields
                )
            if workflow:
                existing.data.setdefault("Workflow", {}).update(workflow)
            if related_findings:
                existing.data["RelatedFindings"] = related_findings

            existing.data["UpdatedAt"] = _utc_now()
            processed.append({"Id": finding_id, "ProductArn": product_arn})

        return processed, unprocessed

    def update_findings(
        self,
        filters: Optional[dict[str, Any]] = None,
        note: Optional[dict[str, str]] = None,
        record_state: Optional[str] = None,
    ) -> dict[str, Any]:
        # Simple implementation: update all findings (filters not fully implemented)
        for finding in self.findings:
            if note:
                finding.data["Note"] = note
            if record_state:
                finding.data["RecordState"] = record_state
            finding.data["UpdatedAt"] = _utc_now()
        return {}

    def get_finding_history(
        self,
        finding_identifier: dict[str, str],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        # Return empty history - tracking full history is not implemented
        return {"Records": [], "NextToken": None}

    # --- Action Targets ---

    def create_action_target(
        self, name: str, description: str, target_id: str
    ) -> str:
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"action/custom/{target_id}"
        )
        if arn in self.action_targets:
            raise RESTError(
                "ResourceConflictException",
                f"The action target {arn} already exists.",
            )
        self.action_targets[arn] = ActionTarget(arn, name, description)
        return arn

    def describe_action_targets(
        self,
        action_target_arns: Optional[list[str]] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        targets = list(self.action_targets.values())
        if action_target_arns:
            targets = [t for t in targets if t.arn in action_target_arns]
            for arn in action_target_arns:
                if arn not in self.action_targets:
                    raise RESTError(
                        "ResourceNotFoundException",
                        f"The action target {arn} was not found.",
                    )
        return [t.as_dict() for t in targets], None

    def update_action_target(
        self,
        action_target_arn: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        if action_target_arn not in self.action_targets:
            raise RESTError(
                "ResourceNotFoundException",
                f"The action target {action_target_arn} was not found.",
            )
        target = self.action_targets[action_target_arn]
        if name is not None:
            target.name = name
        if description is not None:
            target.description = description
        return {}

    def delete_action_target(self, action_target_arn: str) -> str:
        if action_target_arn not in self.action_targets:
            raise RESTError(
                "ResourceNotFoundException",
                f"The action target {action_target_arn} was not found.",
            )
        del self.action_targets[action_target_arn]
        return action_target_arn

    # --- Insights ---

    def create_insight(
        self,
        name: str,
        filters: dict[str, Any],
        group_by_attribute: str,
    ) -> str:
        insight_id = str(uuid.uuid4())
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"insight/{insight_id}"
        )
        self.insights[arn] = Insight(arn, name, filters, group_by_attribute)
        return arn

    def get_insights(
        self,
        insight_arns: Optional[list[str]] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        if insight_arns:
            results = []
            for arn in insight_arns:
                if arn not in self.insights:
                    raise RESTError(
                        "ResourceNotFoundException",
                        f"The insight {arn} was not found.",
                    )
                results.append(self.insights[arn].as_dict())
            return results, None
        return [i.as_dict() for i in self.insights.values()], None

    def get_insight_results(self, insight_arn: str) -> dict[str, Any]:
        if insight_arn not in self.insights:
            raise RESTError(
                "ResourceNotFoundException",
                f"The insight {insight_arn} was not found.",
            )
        insight = self.insights[insight_arn]
        return {
            "InsightArn": insight_arn,
            "GroupByAttribute": insight.group_by_attribute,
            "ResultValues": [],
        }

    def update_insight(
        self,
        insight_arn: str,
        name: Optional[str] = None,
        filters: Optional[dict[str, Any]] = None,
        group_by_attribute: Optional[str] = None,
    ) -> dict[str, Any]:
        if insight_arn not in self.insights:
            raise RESTError(
                "ResourceNotFoundException",
                f"The insight {insight_arn} was not found.",
            )
        insight = self.insights[insight_arn]
        if name is not None:
            insight.name = name
        if filters is not None:
            insight.filters = filters
        if group_by_attribute is not None:
            insight.group_by_attribute = group_by_attribute
        return {}

    def delete_insight(self, insight_arn: str) -> str:
        if insight_arn not in self.insights:
            raise RESTError(
                "ResourceNotFoundException",
                f"The insight {insight_arn} was not found.",
            )
        del self.insights[insight_arn]
        return insight_arn

    # --- Standards ---

    def batch_enable_standards(
        self,
        standards_subscription_requests: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        results = []
        for req in standards_subscription_requests:
            standards_arn = req.get("StandardsArn", "")
            standards_input = req.get("StandardsInput", {})
            sub = StandardsSubscription(
                standards_arn, standards_input, self.region_name, self.account_id
            )
            self.standards_subscriptions[sub.standards_subscription_arn] = sub
            results.append(sub.as_dict())
        return results

    def batch_disable_standards(
        self,
        standards_subscription_arns: list[str],
    ) -> list[dict[str, Any]]:
        results = []
        for arn in standards_subscription_arns:
            if arn in self.standards_subscriptions:
                sub = self.standards_subscriptions.pop(arn)
                sub.standards_status = "INCOMPLETE"
                results.append(sub.as_dict())
            else:
                raise RESTError(
                    "ResourceNotFoundException",
                    f"The standards subscription {arn} was not found.",
                )
        return results

    def get_enabled_standards(
        self,
        standards_subscription_arns: Optional[list[str]] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        if standards_subscription_arns:
            results = []
            for arn in standards_subscription_arns:
                if arn in self.standards_subscriptions:
                    results.append(self.standards_subscriptions[arn].as_dict())
            return results, None
        return [s.as_dict() for s in self.standards_subscriptions.values()], None

    def describe_standards(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        standards = []
        for s in _BUILTIN_STANDARDS:
            standard = dict(s)
            standard["StandardsArn"] = standard["StandardsArn"].replace(
                "{region}", self.region_name
            )
            standards.append(standard)
        return standards, None

    def describe_standards_controls(
        self,
        standards_subscription_arn: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        if standards_subscription_arn not in self.standards_subscriptions:
            raise RESTError(
                "ResourceNotFoundException",
                f"The standards subscription {standards_subscription_arn} was not found.",
            )
        controls = [
            c.as_dict()
            for c in self.standards_controls.values()
            if c.standards_control_arn.startswith(standards_subscription_arn)
        ]
        return controls, None

    def update_standards_control(
        self,
        standards_control_arn: str,
        control_status: Optional[str] = None,
        disabled_reason: Optional[str] = None,
    ) -> dict[str, Any]:
        if standards_control_arn not in self.standards_controls:
            # Auto-create the control if it doesn't exist
            control_id = standards_control_arn.split("/")[-1]
            self.standards_controls[standards_control_arn] = StandardsControl(
                control_id=control_id,
                standards_control_arn=standards_control_arn,
                title=control_id,
                description=f"Control {control_id}",
            )
        control = self.standards_controls[standards_control_arn]
        if control_status is not None:
            control.control_status = control_status
        if disabled_reason is not None:
            control.disabled_reason = disabled_reason
        return {}

    def batch_get_standards_control_associations(
        self,
        standards_control_association_ids: list[dict[str, str]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        details = []
        unprocessed = []
        for assoc_id in standards_control_association_ids:
            security_control_id = assoc_id.get("SecurityControlId", "")
            standards_arn = assoc_id.get("StandardsArn", "")
            details.append({
                "StandardsArn": standards_arn,
                "SecurityControlId": security_control_id,
                "SecurityControlArn": (
                    f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
                    f"security-control/{security_control_id}"
                ),
                "AssociationStatus": "ENABLED",
                "RelatedRequirements": [],
                "UpdatedAt": _utc_now(),
                "UpdatedReason": "",
                "StandardsControlTitle": security_control_id,
                "StandardsControlDescription": f"Control {security_control_id}",
            })
        return details, unprocessed

    def batch_update_standards_control_associations(
        self,
        standards_control_association_updates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        unprocessed = []
        for update in standards_control_association_updates:
            security_control_id = update.get("SecurityControlId", "")
            standards_arn = update.get("StandardsArn", "")
            association_status = update.get("AssociationStatus", "ENABLED")
            # Store as a standards control
            key = f"{standards_arn}/{security_control_id}"
            if key not in self.standards_controls:
                self.standards_controls[key] = StandardsControl(
                    control_id=security_control_id,
                    standards_control_arn=key,
                    title=security_control_id,
                    description=f"Control {security_control_id}",
                )
            self.standards_controls[key].control_status = association_status
        return unprocessed

    def list_standards_control_associations(
        self,
        security_control_id: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        results = []
        for sub in self.standards_subscriptions.values():
            results.append({
                "StandardsArn": sub.standards_arn,
                "SecurityControlId": security_control_id,
                "SecurityControlArn": (
                    f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
                    f"security-control/{security_control_id}"
                ),
                "AssociationStatus": "ENABLED",
                "RelatedRequirements": [],
                "UpdatedAt": _utc_now(),
                "UpdatedReason": "",
                "StandardsControlTitle": security_control_id,
                "StandardsControlDescription": f"Control {security_control_id}",
            })
        return results, None

    # --- Automation Rules ---

    def create_automation_rule(
        self,
        rule_name: str,
        rule_order: int,
        rule_status: str,
        description: str,
        is_terminal: bool,
        criteria: dict[str, Any],
        actions: list[dict[str, Any]],
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        rule_id = str(uuid.uuid4())
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"automation-rule/{rule_id}"
        )
        now = _utc_now()
        rule = AutomationRule(
            arn=arn,
            rule_name=rule_name,
            rule_order=rule_order,
            rule_status=rule_status or "ENABLED",
            description=description or "",
            is_terminal=is_terminal if is_terminal is not None else False,
            criteria=criteria or {},
            actions=actions or [],
            created_at=now,
        )
        self.automation_rules[arn] = rule
        if tags:
            self.tagger.tag_resource(arn, [
                {"Key": k, "Value": v} for k, v in tags.items()
            ])
        return arn

    def batch_get_automation_rules(
        self,
        automation_rules_arns: list[str],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        rules = []
        unprocessed = []
        for arn in automation_rules_arns:
            if arn in self.automation_rules:
                rules.append(self.automation_rules[arn].as_dict())
            else:
                unprocessed.append({
                    "RuleArn": arn,
                    "ErrorCode": 404,
                    "ErrorMessage": f"Rule {arn} not found",
                })
        return rules, unprocessed

    def batch_update_automation_rules(
        self,
        update_items: list[dict[str, Any]],
    ) -> tuple[list[str], list[dict[str, Any]]]:
        processed = []
        unprocessed = []
        for item in update_items:
            arn = item.get("RuleArn", "")
            if arn not in self.automation_rules:
                unprocessed.append({
                    "RuleArn": arn,
                    "ErrorCode": 404,
                    "ErrorMessage": f"Rule {arn} not found",
                })
                continue
            rule = self.automation_rules[arn]
            if "RuleStatus" in item:
                rule.rule_status = item["RuleStatus"]
            if "RuleOrder" in item:
                rule.rule_order = item["RuleOrder"]
            if "Description" in item:
                rule.description = item["Description"]
            if "RuleName" in item:
                rule.rule_name = item["RuleName"]
            if "IsTerminal" in item:
                rule.is_terminal = item["IsTerminal"]
            if "Criteria" in item:
                rule.criteria = item["Criteria"]
            if "Actions" in item:
                rule.actions = item["Actions"]
            rule.updated_at = _utc_now()
            processed.append(arn)
        return processed, unprocessed

    def batch_delete_automation_rules(
        self,
        automation_rules_arns: list[str],
    ) -> tuple[list[str], list[dict[str, Any]]]:
        processed = []
        unprocessed = []
        for arn in automation_rules_arns:
            if arn in self.automation_rules:
                del self.automation_rules[arn]
                processed.append(arn)
            else:
                unprocessed.append({
                    "RuleArn": arn,
                    "ErrorCode": 404,
                    "ErrorMessage": f"Rule {arn} not found",
                })
        return processed, unprocessed

    def list_automation_rules(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        rules = [r.as_metadata() for r in self.automation_rules.values()]
        return rules, None

    # --- Finding Aggregator ---

    def create_finding_aggregator(
        self,
        region_linking_mode: str,
        regions: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        agg_id = str(uuid.uuid4())
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"finding-aggregator/{agg_id}"
        )
        agg = FindingAggregator(arn, self.region_name, region_linking_mode, regions)
        self.finding_aggregators[arn] = agg
        return agg.as_dict()

    def get_finding_aggregator(self, finding_aggregator_arn: str) -> dict[str, Any]:
        if finding_aggregator_arn not in self.finding_aggregators:
            raise RESTError(
                "ResourceNotFoundException",
                f"Finding aggregator {finding_aggregator_arn} not found.",
            )
        return self.finding_aggregators[finding_aggregator_arn].as_dict()

    def update_finding_aggregator(
        self,
        finding_aggregator_arn: str,
        region_linking_mode: str,
        regions: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        if finding_aggregator_arn not in self.finding_aggregators:
            raise RESTError(
                "ResourceNotFoundException",
                f"Finding aggregator {finding_aggregator_arn} not found.",
            )
        agg = self.finding_aggregators[finding_aggregator_arn]
        agg.region_linking_mode = region_linking_mode
        if regions is not None:
            agg.regions = regions
        return agg.as_dict()

    def delete_finding_aggregator(self, finding_aggregator_arn: str) -> dict[str, Any]:
        if finding_aggregator_arn not in self.finding_aggregators:
            raise RESTError(
                "ResourceNotFoundException",
                f"Finding aggregator {finding_aggregator_arn} not found.",
            )
        del self.finding_aggregators[finding_aggregator_arn]
        return {}

    def list_finding_aggregators(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        aggs = [
            {"FindingAggregatorArn": a.arn, "FindingAggregationRegion": a.finding_aggregation_region}
            for a in self.finding_aggregators.values()
        ]
        return aggs, None

    # --- Configuration Policies ---

    def create_configuration_policy(
        self,
        name: str,
        description: str,
        configuration_policy: dict[str, Any],
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        policy_id = str(uuid.uuid4())
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"configuration-policy/{policy_id}"
        )
        now = _utc_now()
        policy = ConfigurationPolicy(
            policy_id, arn, name, description or "", configuration_policy or {}, now
        )
        self.configuration_policies[policy_id] = policy
        if tags:
            self.tagger.tag_resource(arn, [
                {"Key": k, "Value": v} for k, v in tags.items()
            ])
        return policy.as_dict()

    def get_configuration_policy(self, identifier: str) -> dict[str, Any]:
        policy = self._find_configuration_policy(identifier)
        if not policy:
            raise RESTError(
                "ResourceNotFoundException",
                f"Configuration policy {identifier} not found.",
            )
        return policy.as_dict()

    def update_configuration_policy(
        self,
        identifier: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_reason: Optional[str] = None,
        configuration_policy: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        policy = self._find_configuration_policy(identifier)
        if not policy:
            raise RESTError(
                "ResourceNotFoundException",
                f"Configuration policy {identifier} not found.",
            )
        if name is not None:
            policy.name = name
        if description is not None:
            policy.description = description
        if configuration_policy is not None:
            policy.configuration_policy = configuration_policy
        policy.updated_at = _utc_now()
        return policy.as_dict()

    def delete_configuration_policy(self, identifier: str) -> dict[str, Any]:
        policy = self._find_configuration_policy(identifier)
        if not policy:
            raise RESTError(
                "ResourceNotFoundException",
                f"Configuration policy {identifier} not found.",
            )
        del self.configuration_policies[policy.id]
        return {}

    def list_configuration_policies(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        summaries = [p.as_summary() for p in self.configuration_policies.values()]
        return summaries, None

    def _find_configuration_policy(
        self, identifier: str
    ) -> Optional[ConfigurationPolicy]:
        if identifier in self.configuration_policies:
            return self.configuration_policies[identifier]
        for policy in self.configuration_policies.values():
            if policy.arn == identifier:
                return policy
        return None

    # --- Configuration Policy Associations ---

    def start_configuration_policy_association(
        self,
        configuration_policy_identifier: str,
        target: dict[str, Any],
    ) -> dict[str, Any]:
        target_id = (
            target.get("AccountId")
            or target.get("OrganizationalUnitId")
            or target.get("RootId", "")
        )
        target_type = "ACCOUNT"
        if target.get("OrganizationalUnitId"):
            target_type = "ORGANIZATIONAL_UNIT"
        elif target.get("RootId"):
            target_type = "ROOT"

        assoc = ConfigurationPolicyAssociation(
            configuration_policy_id=configuration_policy_identifier,
            target_id=target_id,
            target_type=target_type,
            association_type="APPLIED",
        )
        self.configuration_policy_associations[target_id] = assoc
        return assoc.as_dict()

    def start_configuration_policy_disassociation(
        self,
        configuration_policy_identifier: str,
        target: dict[str, Any],
    ) -> dict[str, Any]:
        target_id = (
            target.get("AccountId")
            or target.get("OrganizationalUnitId")
            or target.get("RootId", "")
        )
        if target_id in self.configuration_policy_associations:
            del self.configuration_policy_associations[target_id]
        return {}

    def get_configuration_policy_association(
        self, target: dict[str, Any]
    ) -> dict[str, Any]:
        target_id = (
            target.get("AccountId")
            or target.get("OrganizationalUnitId")
            or target.get("RootId", "")
        )
        if target_id not in self.configuration_policy_associations:
            raise RESTError(
                "ResourceNotFoundException",
                f"No configuration policy association found for target {target_id}.",
            )
        return self.configuration_policy_associations[target_id].as_dict()

    def batch_get_configuration_policy_associations(
        self,
        configuration_policy_association_identifiers: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        results = []
        unprocessed = []
        for identifier in configuration_policy_association_identifiers:
            target_id = identifier.get("Target", {}).get(
                "AccountId",
                identifier.get("Target", {}).get(
                    "OrganizationalUnitId",
                    identifier.get("Target", {}).get("RootId", ""),
                ),
            )
            if target_id in self.configuration_policy_associations:
                results.append(
                    self.configuration_policy_associations[target_id].as_dict()
                )
            else:
                unprocessed.append({
                    "ConfigurationPolicyAssociationIdentifiers": identifier,
                    "ErrorCode": "404",
                    "ErrorReason": "Not found",
                })
        return results, unprocessed

    def list_configuration_policy_associations(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        filters: Optional[dict[str, Any]] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        results = [a.as_dict() for a in self.configuration_policy_associations.values()]
        return results, None

    # --- Security Controls ---

    def batch_get_security_controls(
        self,
        security_control_ids: list[str],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        controls = []
        unprocessed = []
        for control_id in security_control_ids:
            if control_id in self.security_controls:
                controls.append(self.security_controls[control_id].as_dict())
            else:
                # Return a default control
                controls.append({
                    "SecurityControlId": control_id,
                    "SecurityControlArn": (
                        f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
                        f"security-control/{control_id}"
                    ),
                    "Title": control_id,
                    "Description": f"Control {control_id}",
                    "RemediationUrl": "",
                    "SeverityRating": "MEDIUM",
                    "SecurityControlStatus": "ENABLED",
                    "Parameters": {},
                    "LastUpdateReason": "",
                })
        return controls, unprocessed

    def update_security_control(
        self,
        security_control_id: str,
        parameters: dict[str, Any],
        last_update_reason: Optional[str] = None,
    ) -> dict[str, Any]:
        if security_control_id not in self.security_controls:
            self.security_controls[security_control_id] = SecurityControl(
                security_control_id, {}
            )
        control = self.security_controls[security_control_id]
        control.parameters = parameters
        if last_update_reason:
            control.last_update_reason = last_update_reason
        return {}

    def get_security_control_definition(
        self, security_control_id: str
    ) -> dict[str, Any]:
        return {
            "SecurityControlDefinition": {
                "SecurityControlId": security_control_id,
                "Title": security_control_id,
                "Description": f"Control {security_control_id}",
                "RemediationUrl": "",
                "SeverityRating": "MEDIUM",
                "CurrentRegionAvailability": "AVAILABLE",
                "CustomizableProperties": ["Parameters"],
                "ParameterDefinitions": {},
            }
        }

    def list_security_control_definitions(
        self,
        standards_arn: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        # Return empty list - no built-in control definitions
        return [], None

    # --- Products ---

    def describe_products(
        self,
        product_arn: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        products = []
        for arn_template, name, company in _BUILTIN_PRODUCTS:
            arn = arn_template.replace("{region}", self.region_name)
            if product_arn and arn != product_arn:
                continue
            products.append(
                Product(arn, name, company).as_dict()
            )
        return products, None

    def enable_import_findings_for_product(
        self, product_arn: str
    ) -> str:
        sub_arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"product-subscription/{product_arn.split('::product/')[-1]}"
        )
        if product_arn in self.product_subscriptions:
            raise RESTError(
                "ResourceConflictException",
                f"The product subscription for {product_arn} already exists.",
            )
        self.product_subscriptions[product_arn] = sub_arn
        return sub_arn

    def disable_import_findings_for_product(
        self, product_subscription_arn: str
    ) -> dict[str, Any]:
        for product_arn, sub_arn in list(self.product_subscriptions.items()):
            if sub_arn == product_subscription_arn:
                del self.product_subscriptions[product_arn]
                return {}
        raise RESTError(
            "ResourceNotFoundException",
            f"The product subscription {product_subscription_arn} was not found.",
        )

    def list_enabled_products_for_import(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[str], Optional[str]]:
        return list(self.product_subscriptions.values()), None

    # --- Members (additional operations) ---

    def delete_members(
        self, account_ids: list[str]
    ) -> list[dict[str, str]]:
        unprocessed = []
        for account_id in account_ids:
            if account_id in self.members:
                del self.members[account_id]
            else:
                unprocessed.append({
                    "AccountId": account_id,
                    "ProcessingResult": f"Account {account_id} is not a member",
                })
        return unprocessed

    def disassociate_members(self, account_ids: list[str]) -> dict[str, Any]:
        for account_id in account_ids:
            if account_id in self.members:
                self.members[account_id]["MemberStatus"] = "DISASSOCIATED"
        return {}

    def invite_members(
        self, account_ids: list[str]
    ) -> list[dict[str, str]]:
        unprocessed = []
        for account_id in account_ids:
            if account_id in self.members:
                self.members[account_id]["MemberStatus"] = "INVITED"
            else:
                unprocessed.append({
                    "AccountId": account_id,
                    "ProcessingResult": f"Account {account_id} is not a member",
                })
        return unprocessed

    # --- Invitations ---

    def accept_administrator_invitation(
        self, administrator_id: str, invitation_id: str
    ) -> dict[str, Any]:
        return {}

    def accept_invitation(
        self, master_id: str, invitation_id: str
    ) -> dict[str, Any]:
        return {}

    def decline_invitations(
        self, account_ids: list[str]
    ) -> list[dict[str, str]]:
        return []

    def delete_invitations(
        self, account_ids: list[str]
    ) -> list[dict[str, str]]:
        return []

    def list_invitations(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        return self.invitations, None

    def get_invitations_count(self) -> int:
        return len(self.invitations)

    def disassociate_from_administrator_account(self) -> dict[str, Any]:
        return {}

    def disassociate_from_master_account(self) -> dict[str, Any]:
        return {}

    # --- Organization Admin ---

    def enable_organization_admin_account(self, admin_account_id: str) -> None:
        try:
            org = self.org_backend.describe_organization()
            org_id = org["Organization"]["Id"]
        except RESTError:
            raise AWSOrganizationsNotInUseException()

        if self.account_id != org["Organization"]["MasterAccountId"]:
            raise RESTError(
                "AccessDeniedException",
                "The request was rejected because you don't have sufficient permissions "
                "to perform this operation. The security token included in the request "
                "is for an account that isn't authorized to perform this operation.",
            )

        try:
            self.org_backend.get_account_by_id(admin_account_id)
        except RESTError:
            raise RESTError(
                "InvalidInputException",
                f"The request was rejected because the account {admin_account_id} is not "
                f"a member of organization {org_id}.",
            )

        org_config = self._get_org_config()
        org_config["admin_account_id"] = admin_account_id

    def disable_organization_admin_account(
        self, admin_account_id: str
    ) -> dict[str, Any]:
        try:
            self.org_backend.describe_organization()
        except RESTError:
            raise AWSOrganizationsNotInUseException()

        org_config = self._get_org_config()
        if org_config["admin_account_id"] == admin_account_id:
            org_config["admin_account_id"] = None
        return {}

    def list_organization_admin_accounts(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        try:
            org_config = self._get_org_config()
        except Exception:
            return [], None
        admin_id = org_config.get("admin_account_id")
        if admin_id:
            return [{"AccountId": admin_id, "Status": "ENABLED"}], None
        return [], None

    def update_organization_configuration(
        self,
        auto_enable: bool,
        auto_enable_standards: Optional[str] = None,
        organization_configuration: Optional[dict[str, Any]] = None,
    ) -> None:
        try:
            self.org_backend.describe_organization()
        except RESTError:
            raise RESTError(
                "ResourceNotFoundException",
                "The request was rejected because AWS Organizations is not in use or not "
                "configured for this account.",
            )

        org_config = self._get_org_config()
        if not org_config["admin_account_id"]:
            raise RESTError(
                "ResourceNotFoundException",
                "The request was rejected because no administrator account has been designated.",
            )

        if self.account_id != org_config["admin_account_id"]:
            raise RESTError(
                "AccessDeniedException",
                "The request was rejected because you don't have permission to perform "
                "this action. Only the designated administrator account can update the "
                "organization configuration.",
            )

        if organization_configuration:
            config_type = organization_configuration.get("ConfigurationType")
            if config_type not in ["CENTRAL", "LOCAL"]:
                raise RESTError(
                    "InvalidInputException",
                    "The request was rejected because the ConfigurationType value must be "
                    "either CENTRAL or LOCAL.",
                )

            status = organization_configuration.get("Status")
            if status not in ["PENDING", "ENABLED", "FAILED"]:
                raise RESTError(
                    "InvalidInputException",
                    "The request was rejected because the Status value must be one of "
                    "PENDING, ENABLED, or FAILED.",
                )

            if config_type == "CENTRAL":
                if auto_enable:
                    raise RESTError(
                        "ValidationException",
                        "The request was rejected because AutoEnable must be false when "
                        "ConfigurationType is CENTRAL.",
                    )
                if auto_enable_standards != "NONE":
                    raise RESTError(
                        "ValidationException",
                        "The request was rejected because AutoEnableStandards must be NONE "
                        "when ConfigurationType is CENTRAL.",
                    )

            org_config["configuration"] = organization_configuration

        org_config["auto_enable"] = auto_enable

        if auto_enable_standards is not None:
            if auto_enable_standards not in ["NONE", "DEFAULT"]:
                raise RESTError(
                    "InvalidInputException",
                    "The request was rejected because AutoEnableStandards must be either "
                    "NONE or DEFAULT.",
                )
            org_config["auto_enable_standards"] = auto_enable_standards

    def get_administrator_account(self) -> dict[str, Any]:
        try:
            org = self.org_backend.describe_organization()
            management_account_id = org["Organization"]["MasterAccountId"]
        except RESTError:
            return {}

        org_config = self._get_org_config()
        admin_account_id = org_config["admin_account_id"]

        if not admin_account_id:
            return {}

        if (
            self.account_id == management_account_id
            or self.account_id == admin_account_id
        ):
            return {}

        return {
            "Administrator": {
                "AccountId": admin_account_id,
                "MemberStatus": "ENABLED",
                "InvitationId": f"invitation-{admin_account_id}",
                "InvitedAt": datetime.datetime.now().isoformat(),
            }
        }

    def describe_organization_configuration(self) -> dict[str, Any]:
        try:
            self.org_backend.describe_organization()
        except RESTError:
            raise RESTError(
                "AccessDeniedException",
                "You do not have sufficient access to perform this action.",
            )

        org_config = self._get_org_config()
        if not org_config["admin_account_id"]:
            raise RESTError(
                "AccessDeniedException",
                "You do not have sufficient access to perform this action.",
            )

        if self.account_id != org_config["admin_account_id"]:
            raise RESTError(
                "AccessDeniedException",
                "You do not have sufficient access to perform this action.",
            )

        return {
            "AutoEnable": org_config["auto_enable"],
            "MemberAccountLimitReached": False,
            "AutoEnableStandards": org_config["auto_enable_standards"],
            "OrganizationConfiguration": org_config["configuration"],
        }

    def create_members(
        self, account_details: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        unprocessed_accounts: list[dict[str, str]] = []

        if not account_details:
            return unprocessed_accounts

        for account in account_details:
            account_id = account.get("AccountId")
            email = account.get("Email", "")

            if not account_id:
                unprocessed_accounts.append(
                    {
                        "AccountId": account_id or "",
                        "ProcessingResult": "Invalid input: AccountId is required",
                    }
                )
                continue

            if account_id in self.members:
                unprocessed_accounts.append(
                    {
                        "AccountId": account_id,
                        "ProcessingResult": f"Account {account_id} is already a member",
                    }
                )
                continue

            self.members[account_id] = {
                "AccountId": account_id,
                "Email": email,
                "MemberStatus": "ENABLED",
                "InvitedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "UpdatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

        return unprocessed_accounts

    def get_members(
        self, account_ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        members = []
        unprocessed_accounts = []

        try:
            org_config = self._get_org_config()
            admin_account_id = org_config.get("admin_account_id")
        except Exception:
            admin_account_id = None

        for account_id in account_ids:
            if account_id in self.members:
                member_data = self.members[account_id].copy()
                if admin_account_id:
                    member_data["AdministratorId"] = admin_account_id
                    member_data["MasterId"] = admin_account_id
                members.append(member_data)
            else:
                unprocessed_accounts.append(
                    {
                        "AccountId": account_id,
                        "ProcessingResult": f"Account {account_id} is not a member",
                    }
                )

        return members, unprocessed_accounts

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_members(
        self, only_associated: Optional[bool] = None
    ) -> list[dict[str, str]]:
        if only_associated is None:
            only_associated = True

        try:
            org_config = self._get_org_config()
            admin_account_id = org_config.get("admin_account_id")
        except Exception:
            admin_account_id = None

        members = []
        for member_data in self.members.values():
            if only_associated and member_data.get("MemberStatus") != "ENABLED":
                continue

            member = member_data.copy()
            if admin_account_id:
                member["AdministratorId"] = admin_account_id
                member["MasterId"] = admin_account_id
            members.append(member)

        return members

    def get_master_account(self) -> dict[str, Any]:
        admin_result = self.get_administrator_account()

        if not admin_result or "Administrator" not in admin_result:
            return {}

        return {"Master": admin_result["Administrator"]}

    # --- Tags ---

    def tag_resource(
        self, resource_arn: str, tags: dict[str, str]
    ) -> dict[str, Any]:
        self.tagger.tag_resource(
            resource_arn,
            [{"Key": k, "Value": v} for k, v in tags.items()],
        )
        return {}

    def untag_resource(
        self, resource_arn: str, tag_keys: list[str]
    ) -> dict[str, Any]:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)
        return {}

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        tag_list = self.tagger.list_tags_for_resource(resource_arn).get("Tags", [])
        return {t["Key"]: t["Value"] for t in tag_list}

    # --- V2 APIs ---

    def batch_update_findings_v2(
        self,
        metadata_uids: Optional[list[str]] = None,
        finding_identifiers: Optional[list[dict[str, str]]] = None,
        comment: Optional[str] = None,
        severity_id: Optional[int] = None,
        status_id: Optional[int] = None,
    ) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
        processed = []
        unprocessed = []
        identifiers = finding_identifiers or []
        if metadata_uids:
            identifiers.extend(
                [{"Id": uid, "ProductArn": ""} for uid in metadata_uids]
            )
        for identifier in identifiers:
            finding_id = identifier.get("Id", "")
            existing = next((f for f in self.findings if f.id == finding_id), None)
            if not existing:
                unprocessed.append({
                    "FindingIdentifier": identifier,
                    "ErrorCode": "FindingNotFound",
                    "ErrorMessage": f"Finding {finding_id} not found",
                })
                continue
            if comment:
                existing.data.setdefault("Note", {})["Text"] = comment
            if severity_id is not None:
                existing.data["SeverityId"] = severity_id
            if status_id is not None:
                existing.data["StatusId"] = status_id
            existing.data["UpdatedAt"] = _utc_now()
            processed.append({"Id": finding_id, "ProductArn": identifier.get("ProductArn", "")})
        return processed, unprocessed

    def get_findings_v2(
        self,
        filters: Optional[dict[str, Any]] = None,
        sort_criteria: Optional[list[dict[str, str]]] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        return [f.as_dict() for f in self.findings], None

    def get_finding_statistics_v2(
        self,
        group_by_rules: Optional[list[dict[str, Any]]] = None,
        sort_order: Optional[str] = None,
        max_statistic_results: Optional[int] = None,
    ) -> dict[str, Any]:
        return {"GroupByResults": []}

    def get_findings_trends_v2(
        self,
        filters: Optional[dict[str, Any]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        return {"Granularity": "DAILY", "TrendsMetrics": [], "NextToken": None}

    def get_resources_v2(
        self,
        filters: Optional[dict[str, Any]] = None,
        sort_criteria: Optional[list[dict[str, str]]] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        return [], None

    def get_resources_statistics_v2(
        self,
        group_by_rules: Optional[list[dict[str, Any]]] = None,
        sort_order: Optional[str] = None,
        max_statistic_results: Optional[int] = None,
    ) -> dict[str, Any]:
        return {"GroupByResults": []}

    def get_resources_trends_v2(
        self,
        filters: Optional[dict[str, Any]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        return {"Granularity": "DAILY", "TrendsMetrics": [], "NextToken": None}

    def describe_products_v2(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        products = []
        for arn_template, name, company in _BUILTIN_PRODUCTS:
            arn = arn_template.replace("{region}", self.region_name)
            products.append({
                "ProductArn": arn,
                "ProductName": name,
                "CompanyName": company,
            })
        return products, None

    def enable_security_hub_v2(
        self, tags: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        self.hub_v2_arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:hubv2/default"
        )
        self.hub_v2_subscribed_at = _utc_now()
        if tags:
            self.tagger.tag_resource(self.hub_v2_arn, [
                {"Key": k, "Value": v} for k, v in tags.items()
            ])
        return {"HubV2Arn": self.hub_v2_arn}

    def disable_security_hub_v2(self) -> dict[str, Any]:
        self.hub_v2_arn = None
        self.hub_v2_subscribed_at = None
        return {}

    def describe_security_hub_v2(self) -> dict[str, Any]:
        if not self.hub_v2_arn:
            raise RESTError(
                "InvalidAccessException",
                "Account is not subscribed to AWS Security Hub V2",
            )
        return {
            "HubV2Arn": self.hub_v2_arn,
            "SubscribedAt": self.hub_v2_subscribed_at,
        }

    # --- Automation Rules V2 ---

    def create_automation_rule_v2(
        self,
        rule_name: str,
        rule_status: str,
        description: str,
        rule_order: int,
        criteria: dict[str, Any],
        actions: list[dict[str, Any]],
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        rule_id = str(uuid.uuid4())
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"automation-rule-v2/{rule_id}"
        )
        now = _utc_now()
        rule = AutomationRuleV2(
            rule_id=rule_id,
            arn=arn,
            rule_name=rule_name,
            rule_order=rule_order,
            rule_status=rule_status or "ENABLED",
            description=description or "",
            criteria=criteria or {},
            actions=actions or [],
            created_at=now,
        )
        self.automation_rules_v2[rule_id] = rule
        if tags:
            self.tagger.tag_resource(arn, [
                {"Key": k, "Value": v} for k, v in tags.items()
            ])
        return {"RuleArn": arn, "RuleId": rule_id}

    def get_automation_rule_v2(self, identifier: str) -> dict[str, Any]:
        rule = self._find_automation_rule_v2(identifier)
        if not rule:
            raise RESTError(
                "ResourceNotFoundException",
                f"Automation rule {identifier} not found.",
            )
        return rule.as_dict()

    def update_automation_rule_v2(
        self,
        identifier: str,
        rule_status: Optional[str] = None,
        rule_order: Optional[int] = None,
        description: Optional[str] = None,
        rule_name: Optional[str] = None,
        criteria: Optional[dict[str, Any]] = None,
        actions: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        rule = self._find_automation_rule_v2(identifier)
        if not rule:
            raise RESTError(
                "ResourceNotFoundException",
                f"Automation rule {identifier} not found.",
            )
        if rule_status is not None:
            rule.rule_status = rule_status
        if rule_order is not None:
            rule.rule_order = rule_order
        if description is not None:
            rule.description = description
        if rule_name is not None:
            rule.rule_name = rule_name
        if criteria is not None:
            rule.criteria = criteria
        if actions is not None:
            rule.actions = actions
        rule.updated_at = _utc_now()
        return {}

    def delete_automation_rule_v2(self, identifier: str) -> dict[str, Any]:
        rule = self._find_automation_rule_v2(identifier)
        if not rule:
            raise RESTError(
                "ResourceNotFoundException",
                f"Automation rule {identifier} not found.",
            )
        del self.automation_rules_v2[rule.rule_id]
        return {}

    def list_automation_rules_v2(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        rules = [r.as_summary() for r in self.automation_rules_v2.values()]
        return rules, None

    def _find_automation_rule_v2(
        self, identifier: str
    ) -> Optional[AutomationRuleV2]:
        if identifier in self.automation_rules_v2:
            return self.automation_rules_v2[identifier]
        for rule in self.automation_rules_v2.values():
            if rule.arn == identifier:
                return rule
        return None

    # --- Aggregator V2 ---

    def create_aggregator_v2(
        self,
        region_linking_mode: str,
        linked_regions: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        agg_id = str(uuid.uuid4())
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"aggregator-v2/{agg_id}"
        )
        agg = AggregatorV2(arn, self.region_name, region_linking_mode, linked_regions)
        self.aggregators_v2[arn] = agg
        if tags:
            self.tagger.tag_resource(arn, [
                {"Key": k, "Value": v} for k, v in tags.items()
            ])
        return agg.as_dict()

    def get_aggregator_v2(self, aggregator_v2_arn: str) -> dict[str, Any]:
        if aggregator_v2_arn not in self.aggregators_v2:
            raise RESTError(
                "ResourceNotFoundException",
                f"Aggregator {aggregator_v2_arn} not found.",
            )
        return self.aggregators_v2[aggregator_v2_arn].as_dict()

    def update_aggregator_v2(
        self,
        aggregator_v2_arn: str,
        region_linking_mode: Optional[str] = None,
        linked_regions: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        if aggregator_v2_arn not in self.aggregators_v2:
            raise RESTError(
                "ResourceNotFoundException",
                f"Aggregator {aggregator_v2_arn} not found.",
            )
        agg = self.aggregators_v2[aggregator_v2_arn]
        if region_linking_mode is not None:
            agg.region_linking_mode = region_linking_mode
        if linked_regions is not None:
            agg.linked_regions = linked_regions
        return agg.as_dict()

    def delete_aggregator_v2(self, aggregator_v2_arn: str) -> dict[str, Any]:
        if aggregator_v2_arn not in self.aggregators_v2:
            raise RESTError(
                "ResourceNotFoundException",
                f"Aggregator {aggregator_v2_arn} not found.",
            )
        del self.aggregators_v2[aggregator_v2_arn]
        return {}

    def list_aggregators_v2(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        aggs = [a.as_dict() for a in self.aggregators_v2.values()]
        return aggs, None

    # --- Connector V2 ---

    def create_connector_v2(
        self,
        name: str,
        description: str,
        provider: dict[str, Any],
        kms_key_arn: str,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        connector_id = str(uuid.uuid4())
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"connector-v2/{connector_id}"
        )
        now = _utc_now()
        connector = ConnectorV2(
            connector_id=connector_id,
            arn=arn,
            name=name,
            description=description or "",
            provider=provider or {},
            kms_key_arn=kms_key_arn or "",
            created_at=now,
        )
        self.connectors_v2[connector_id] = connector
        if tags:
            self.tagger.tag_resource(arn, [
                {"Key": k, "Value": v} for k, v in tags.items()
            ])
        return {
            "ConnectorArn": arn,
            "ConnectorId": connector_id,
            "AuthUrl": "",
            "ConnectorStatus": "CONNECTED",
        }

    def get_connector_v2(self, connector_id: str) -> dict[str, Any]:
        connector = self._find_connector_v2(connector_id)
        if not connector:
            raise RESTError(
                "ResourceNotFoundException",
                f"Connector {connector_id} not found.",
            )
        return connector.as_dict()

    def update_connector_v2(
        self,
        connector_id: str,
        description: Optional[str] = None,
        provider: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        connector = self._find_connector_v2(connector_id)
        if not connector:
            raise RESTError(
                "ResourceNotFoundException",
                f"Connector {connector_id} not found.",
            )
        if description is not None:
            connector.description = description
        if provider is not None:
            connector.provider = provider
        connector.last_updated_at = _utc_now()
        return {}

    def delete_connector_v2(self, connector_id: str) -> dict[str, Any]:
        connector = self._find_connector_v2(connector_id)
        if not connector:
            raise RESTError(
                "ResourceNotFoundException",
                f"Connector {connector_id} not found.",
            )
        del self.connectors_v2[connector.connector_id]
        return {}

    def list_connectors_v2(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        provider_name: Optional[str] = None,
        connector_status: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        connectors = list(self.connectors_v2.values())
        if provider_name:
            connectors = [
                c for c in connectors
                if c.provider.get("ProviderName") == provider_name
            ]
        if connector_status:
            connectors = [c for c in connectors if c.status == connector_status]
        return [c.as_summary() for c in connectors], None

    def register_connector_v2(
        self, auth_code: str, auth_state: str
    ) -> dict[str, Any]:
        # Find a connector that might match — simplified stub
        connector_id = str(uuid.uuid4())
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}:"
            f"connector-v2/{connector_id}"
        )
        return {"ConnectorArn": arn, "ConnectorId": connector_id}

    def _find_connector_v2(self, connector_id: str) -> Optional[ConnectorV2]:
        if connector_id in self.connectors_v2:
            return self.connectors_v2[connector_id]
        for c in self.connectors_v2.values():
            if c.arn == connector_id:
                return c
        return None

    # --- Tickets V2 ---

    def create_ticket_v2(
        self,
        connector_id: str,
        finding_metadata_uid: str,
        mode: Optional[str] = None,
    ) -> dict[str, Any]:
        ticket_id = str(uuid.uuid4())
        return {
            "TicketId": ticket_id,
            "TicketSrcUrl": f"https://ticket.example.com/{ticket_id}",
        }


securityhub_backends = BackendDict(SecurityHubBackend, "securityhub")
