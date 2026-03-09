"""SecurityHubBackend class with methods for supported APIs."""

import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.exceptions import RESTError
from moto.moto_api._internal import mock_random
from moto.organizations.exceptions import AWSOrganizationsNotInUseException
from moto.organizations.models import organizations_backends
from moto.securityhub.exceptions import (
    InvalidAccessException,
    InvalidInputException,
    ResourceNotFoundException,
)
from moto.utilities.paginator import paginate


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

    def to_dict(self) -> dict[str, Any]:
        return {
            "ActionTargetArn": self.arn,
            "Name": self.name,
            "Description": self.description,
        }


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
        self.members: dict[str, dict[str, str]] = {}
        self.tags: dict[str, str] = {}
        self.action_targets: dict[str, ActionTarget] = {}
        self.enabled_products: dict[str, str] = {}

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
        self.enabled_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.tags = tags or {}
        return {}

    def disable_security_hub(self) -> dict[str, Any]:
        if not self.enabled:
            raise InvalidAccessException("Account is not subscribed to AWS Security Hub")
        self.enabled = False
        self.enabled_at = None
        self.findings = []
        return {}

    def describe_hub(self, hub_arn: Optional[str] = None) -> dict[str, Any]:
        if not self.enabled:
            raise InvalidAccessException("Account is not subscribed to AWS Security Hub")
        expected_arn = self._hub_arn()
        if hub_arn and hub_arn != expected_arn:
            raise ResourceNotFoundException(
                f"The request was rejected because no hub was found with ARN {hub_arn}."
            )
        return {
            "HubArn": expected_arn,
            "SubscribedAt": self.enabled_at,
            "AutoEnableControls": True,
            "ControlFindingGenerator": "SECURITY_CONTROL",
            "Tags": self.tags or {},
        }

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_findings(
        self,
        filters: Optional[dict[str, Any]] = None,
        sort_criteria: Optional[list[dict[str, str]]] = None,
        max_results: Optional[int] = None,
    ) -> list[dict[str, str]]:
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
        failed_findings: list[dict[str, Any]] = []
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
                failed_findings.append({
                    "Id": finding_data.get("Id", ""),
                    "ErrorCode": "InvalidInput",
                    "ErrorMessage": str(e),
                })
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
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        processed_findings: list[dict[str, str]] = []
        unprocessed_findings: list[dict[str, str]] = []
        for identifier in finding_identifiers:
            finding_id = identifier.get("Id", "")
            product_arn = identifier.get("ProductArn", "")
            existing = next((f for f in self.findings if f.id == finding_id), None)
            if existing is None:
                unprocessed_findings.append({
                    "FindingIdentifier": identifier,
                    "ErrorCode": "FindingNotFound",
                    "ErrorMessage": f"Finding with Id {finding_id} not found",
                })
                continue
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            if note is not None:
                existing.data["Note"] = {
                    "Text": note.get("Text", ""),
                    "UpdatedBy": note.get("UpdatedBy", ""),
                    "UpdatedAt": now,
                }
            if severity is not None:
                if "Severity" not in existing.data:
                    existing.data["Severity"] = {}
                existing.data["Severity"].update(severity)
            if verification_state is not None:
                existing.data["VerificationState"] = verification_state
            if confidence is not None:
                existing.data["Confidence"] = confidence
            if criticality is not None:
                existing.data["Criticality"] = criticality
            if types is not None:
                existing.data["Types"] = types
            if user_defined_fields is not None:
                existing.data["UserDefinedFields"] = user_defined_fields
            if workflow is not None:
                if "Workflow" not in existing.data:
                    existing.data["Workflow"] = {}
                existing.data["Workflow"].update(workflow)
            if related_findings is not None:
                existing.data["RelatedFindings"] = related_findings
            existing.data["UpdatedAt"] = now
            processed_findings.append({"Id": finding_id, "ProductArn": product_arn})
        return processed_findings, unprocessed_findings

    def enable_import_findings_for_product(self, product_arn: str) -> str:
        for sub_arn, prod_arn in self.enabled_products.items():
            if prod_arn == product_arn:
                raise RESTError("ResourceConflictException", f"Product already enabled: {product_arn}")
        subscription_arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}"
            f":product-subscription/{mock_random.get_random_hex(length=32)}"
        )
        self.enabled_products[subscription_arn] = product_arn
        return subscription_arn

    def disable_import_findings_for_product(self, product_subscription_arn: str) -> None:
        if product_subscription_arn not in self.enabled_products:
            raise ResourceNotFoundException(f"Subscription not found: {product_subscription_arn}")
        del self.enabled_products[product_subscription_arn]

    def list_enabled_products_for_import(self) -> list[str]:
        return list(self.enabled_products.keys())

    def create_action_target(self, name: str, description: str, action_target_id: str) -> str:
        arn = (
            f"arn:aws:securityhub:{self.region_name}:{self.account_id}"
            f":action/custom/{action_target_id}"
        )
        if arn in self.action_targets:
            raise RESTError("ResourceConflictException", f"ActionTarget already exists for {arn}")
        action_target = ActionTarget(arn=arn, name=name, description=description)
        self.action_targets[arn] = action_target
        return arn

    def describe_action_targets(
        self, action_target_arns: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        if not action_target_arns:
            return [at.to_dict() for at in self.action_targets.values()]
        results = []
        for arn in action_target_arns:
            if arn not in self.action_targets:
                raise ResourceNotFoundException(f"ActionTarget not found: {arn}")
            results.append(self.action_targets[arn].to_dict())
        return results

    def update_action_target(
        self, action_target_arn: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> None:
        if action_target_arn not in self.action_targets:
            raise ResourceNotFoundException(f"ActionTarget not found: {action_target_arn}")
        at = self.action_targets[action_target_arn]
        if name is not None:
            at.name = name
        if description is not None:
            at.description = description

    def delete_action_target(self, action_target_arn: str) -> str:
        if action_target_arn not in self.action_targets:
            raise ResourceNotFoundException(f"ActionTarget not found: {action_target_arn}")
        del self.action_targets[action_target_arn]
        return action_target_arn

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self._validate_resource_arn(resource_arn)
        if resource_arn == self._hub_arn():
            self.tags.update(tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self._validate_resource_arn(resource_arn)
        if resource_arn == self._hub_arn():
            for key in tag_keys:
                self.tags.pop(key, None)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        self._validate_resource_arn(resource_arn)
        if resource_arn == self._hub_arn():
            return dict(self.tags)
        return {}

    def _validate_resource_arn(self, resource_arn: str) -> None:
        if resource_arn == self._hub_arn():
            if not self.enabled:
                raise ResourceNotFoundException(f"Hub not found: {resource_arn}")
            return
        if resource_arn in self.action_targets:
            return
        if resource_arn in self.enabled_products:
            return
        raise ResourceNotFoundException(f"Resource not found: {resource_arn}")

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
        if self.account_id == management_account_id or self.account_id == admin_account_id:
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

    def create_members(self, account_details: list[dict[str, str]]) -> list[dict[str, str]]:
        unprocessed_accounts: list[dict[str, str]] = []
        if not account_details:
            return unprocessed_accounts
        for account in account_details:
            account_id = account.get("AccountId")
            email = account.get("Email", "")
            if not account_id:
                unprocessed_accounts.append({
                    "AccountId": account_id or "",
                    "ProcessingResult": "Invalid input: AccountId is required",
                })
                continue
            if account_id in self.members:
                unprocessed_accounts.append({
                    "AccountId": account_id,
                    "ProcessingResult": f"Account {account_id} is already a member",
                })
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
                unprocessed_accounts.append({
                    "AccountId": account_id,
                    "ProcessingResult": f"Account {account_id} is not a member",
                })
        return members, unprocessed_accounts

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_members(self, only_associated: Optional[bool] = None) -> list[dict[str, str]]:
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


securityhub_backends = BackendDict(SecurityHubBackend, "securityhub")
