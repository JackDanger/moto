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

    def enable_security_hub(self) -> str:
        params = json.loads(self.body) if self.body else {}
        enable_default_standards = params.get("EnableDefaultStandards", True)
        tags = params.get("Tags", {})
        self.securityhub_backend.enable_security_hub(
            enable_default_standards=enable_default_standards, tags=tags,
        )
        return json.dumps({})

    def disable_security_hub(self) -> str:
        self.securityhub_backend.disable_security_hub()
        return json.dumps({})

    def describe_hub(self) -> str:
        params = json.loads(self.body) if self.body else {}
        hub_arn = params.get("HubArn")
        hub_info = self.securityhub_backend.describe_hub(hub_arn=hub_arn)
        return json.dumps(hub_info)

    def get_findings(self) -> str:
        filters = self._get_param("Filters")
        sort_criteria = self._get_param("SortCriteria")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        findings, next_token = self.securityhub_backend.get_findings(
            filters=filters, sort_criteria=sort_criteria,
            max_results=max_results, next_token=next_token,
        )
        response = {"Findings": findings, "NextToken": next_token}
        return json.dumps(response)

    def batch_import_findings(self) -> str:
        raw_body = self.body
        if isinstance(raw_body, bytes):
            raw_body = raw_body.decode("utf-8")
        body = json.loads(raw_body)
        findings = body.get("Findings", [])
        failed_count, success_count, failed_findings = (
            self.securityhub_backend.batch_import_findings(findings=findings)
        )
        return json.dumps({
            "FailedCount": failed_count,
            "FailedFindings": [
                {
                    "ErrorCode": finding.get("ErrorCode"),
                    "ErrorMessage": finding.get("ErrorMessage"),
                    "Id": finding.get("Id"),
                }
                for finding in failed_findings
            ],
            "SuccessCount": success_count,
        })

    def batch_update_findings(self) -> str:
        raw_body = self.body
        if isinstance(raw_body, bytes):
            raw_body = raw_body.decode("utf-8")
        body = json.loads(raw_body)
        finding_identifiers = body.get("FindingIdentifiers", [])
        processed, unprocessed = self.securityhub_backend.batch_update_findings(
            finding_identifiers=finding_identifiers,
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

    def enable_import_findings_for_product(self) -> str:
        params = json.loads(self.body) if self.body else {}
        product_arn = params.get("ProductArn", "")
        subscription_arn = self.securityhub_backend.enable_import_findings_for_product(product_arn)
        return json.dumps({"ProductSubscriptionArn": subscription_arn})

    def disable_import_findings_for_product(self) -> str:
        path = unquote(self.path)
        idx = path.find("/productSubscriptions/")
        product_subscription_arn = path[idx + len("/productSubscriptions/"):] if idx >= 0 else ""
        self.securityhub_backend.disable_import_findings_for_product(product_subscription_arn)
        return json.dumps({})

    def list_enabled_products_for_import(self) -> str:
        product_subscriptions = self.securityhub_backend.list_enabled_products_for_import()
        return json.dumps({"ProductSubscriptions": product_subscriptions})

    def create_action_target(self) -> str:
        params = json.loads(self.body) if self.body else {}
        name = params.get("Name", "")
        description = params.get("Description", "")
        action_target_id = params.get("Id", "")
        arn = self.securityhub_backend.create_action_target(
            name=name, description=description, action_target_id=action_target_id,
        )
        return json.dumps({"ActionTargetArn": arn})

    def describe_action_targets(self) -> str:
        params = json.loads(self.body) if self.body else {}
        action_target_arns = params.get("ActionTargetArns")
        action_targets = self.securityhub_backend.describe_action_targets(
            action_target_arns=action_target_arns,
        )
        return json.dumps({"ActionTargets": action_targets})

    def update_action_target(self) -> str:
        path = unquote(self.path)
        idx = path.find("/actionTargets/")
        action_target_arn = path[idx + len("/actionTargets/"):] if idx >= 0 else ""
        params = json.loads(self.body) if self.body else {}
        name = params.get("Name")
        description = params.get("Description")
        self.securityhub_backend.update_action_target(
            action_target_arn=action_target_arn, name=name, description=description,
        )
        return json.dumps({})

    def delete_action_target(self) -> str:
        path = unquote(self.path)
        idx = path.find("/actionTargets/")
        action_target_arn = path[idx + len("/actionTargets/"):] if idx >= 0 else ""
        arn = self.securityhub_backend.delete_action_target(action_target_arn)
        return json.dumps({"ActionTargetArn": arn})

    def tag_resource(self) -> str:
        resource_arn = self._get_resource_arn_from_path()
        params = json.loads(self.body) if self.body else {}
        tags = params.get("Tags", {})
        self.securityhub_backend.tag_resource(resource_arn, tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = self._get_resource_arn_from_path()
        tag_keys = self.querystring.get("tagKeys", [])
        self.securityhub_backend.untag_resource(resource_arn, tag_keys)
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_resource_arn_from_path()
        tags = self.securityhub_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"Tags": tags})

    def _get_resource_arn_from_path(self) -> str:
        path = unquote(self.path)
        idx = path.find("/tags/")
        if idx >= 0:
            return path[idx + 6:]
        return ""

    def enable_organization_admin_account(self) -> str:
        params = json.loads(self.body)
        admin_account_id = params.get("AdminAccountId")
        self.securityhub_backend.enable_organization_admin_account(
            admin_account_id=admin_account_id,
        )
        return json.dumps({})

    def update_organization_configuration(self) -> str:
        params = json.loads(self.body)
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

    def create_members(self) -> str:
        params = json.loads(self.body) if self.body else {}
        account_details = params.get("AccountDetails", [])
        unprocessed_accounts = self.securityhub_backend.create_members(
            account_details=account_details,
        )
        return json.dumps({"UnprocessedAccounts": unprocessed_accounts})

    def get_members(self) -> str:
        params = json.loads(self.body) if self.body else {}
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

    def get_master_account(self) -> str:
        master = self.securityhub_backend.get_master_account()
        return json.dumps(master)
