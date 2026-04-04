"""ServiceCatalogBackend class with methods for supported APIs."""

import uuid
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    DuplicateResourceException,
    InvalidParametersException,
    ResourceInUseException,
    ResourceNotFoundException,
)

PAGINATION_MODEL = {
    "list_portfolio_access": {
        "input_token": "page_token",
        "limit_key": "page_size",
        "limit_default": 20,
        "unique_attribute": "account_id",
    }
}


class Portfolio(BaseModel):
    """Portfolio resource."""

    def __init__(
        self,
        portfolio_id: str,
        display_name: str,
        description: str,
        provider_name: str,
        tags: list[dict[str, str]],
        region_name: str,
        account_id: str,
        backend: "ServiceCatalogBackend",
    ) -> None:
        self.id = portfolio_id
        self.display_name = display_name
        self.description = description
        self.provider_name = provider_name
        self.created_time = utcnow()
        self.tags = tags
        self.region_name = region_name
        self.account_id = account_id
        self.backend = backend
        if tags:
            self.backend._tag_resource(self.arn, tags)

    @property
    def arn(self) -> str:
        return (
            f"arn:{get_partition(self.region_name)}:catalog:"
            f"{self.region_name}:{self.account_id}:portfolio/{self.id}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "ARN": self.arn,
            "DisplayName": self.display_name,
            "Description": self.description,
            "CreatedTime": self.created_time,
            "ProviderName": self.provider_name,
        }


class Product(BaseModel):
    """Service Catalog Product resource."""

    def __init__(
        self,
        name: str,
        owner: str,
        description: Optional[str],
        distributor: Optional[str],
        support_description: Optional[str],
        support_email: Optional[str],
        support_url: Optional[str],
        product_type: str,
        tags: Optional[list[dict[str, str]]],
        provisioning_artifact_parameters: Optional[dict[str, Any]],
        source_connection: Optional[dict[str, Any]],
        accept_language: Optional[str],
        region_name: str,
        account_id: str,
        backend: "ServiceCatalogBackend",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.owner = owner
        self.description = description
        self.distributor = distributor
        self.support_description = support_description
        self.support_email = support_email
        self.support_url = support_url
        self.product_type = product_type
        self.tags = tags or []
        self.provisioning_artifact_parameters = provisioning_artifact_parameters or {}
        self.source_connection = source_connection or {}
        self.accept_language = accept_language
        self.created_time = utcnow()
        self.region_name = region_name
        self.account_id = account_id
        self.backend = backend
        self.status = "AVAILABLE"
        if tags:
            self.backend._tag_resource(self.arn, tags)

    @property
    def arn(self) -> str:
        return (
            f"arn:{get_partition(self.region_name)}:catalog:"
            f"{self.region_name}:{self.account_id}:product/{self.id}"
        )

    def to_dict(self) -> dict[str, Any]:
        product_view_summary = {
            "Id": self.id,
            "ProductId": self.id,
            "Name": self.name,
            "Owner": self.owner,
            "Type": self.product_type,
            "Distributor": self.distributor,
            "HasDefaultPath": False,
            "ShortDescription": self.description,
            "SupportDescription": self.support_description,
            "SupportEmail": self.support_email,
            "SupportUrl": self.support_url,
        }
        return product_view_summary

    def to_product_view_detail(self) -> dict[str, Any]:
        return {
            "ProductViewSummary": self.to_dict(),
            "Status": self.status,
            "ProductARN": self.arn,
            "CreatedTime": self.created_time,
            "SourceConnection": self.source_connection,
        }


class ProvisioningArtifact(BaseModel):
    """Provisioning artifact (version) of a product."""

    def __init__(
        self,
        product_id: str,
        name: Optional[str],
        description: Optional[str],
        artifact_type: Optional[str],
        info: Optional[dict[str, Any]],
        disable_template_validation: bool,
        region_name: str,
        account_id: str,
    ) -> None:
        self.id = f"pa-{uuid.uuid4().hex[:12]}"
        self.product_id = product_id
        self.name = name or self.id
        self.description = description or ""
        self.type = artifact_type or "CLOUD_FORMATION_TEMPLATE"
        self.info = info or {}
        self.disable_template_validation = disable_template_validation
        self.created_time = utcnow()
        self.active = True
        self.guidance = "DEFAULT"
        self.region_name = region_name
        self.account_id = account_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
            "Type": self.type,
            "CreatedTime": self.created_time,
            "Active": self.active,
            "Guidance": self.guidance,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        d = self.to_dict()
        return d

    def to_parameter_dict(self) -> dict[str, Any]:
        return {
            "ParameterKey": "",
            "DefaultValue": "",
            "ParameterType": "String",
            "IsNoEcho": False,
            "Description": "",
            "ParameterConstraints": {"AllowedValues": []},
        }


class Constraint(BaseModel):
    """Constraint on a product within a portfolio."""

    def __init__(
        self,
        portfolio_id: str,
        product_id: str,
        parameters: str,
        constraint_type: str,
        description: Optional[str],
        region_name: str,
        account_id: str,
    ) -> None:
        self.id = f"cons-{uuid.uuid4().hex[:12]}"
        self.portfolio_id = portfolio_id
        self.product_id = product_id
        self.parameters = parameters
        self.type = constraint_type
        self.description = description or ""
        self.created_time = utcnow()
        self.owner = account_id
        self.region_name = region_name
        self.account_id = account_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "ConstraintId": self.id,
            "Type": self.type,
            "Description": self.description,
            "Owner": self.owner,
            "ProductId": self.product_id,
            "PortfolioId": self.portfolio_id,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        return {
            "ConstraintId": self.id,
            "Type": self.type,
            "Description": self.description,
            "Owner": self.owner,
        }


class ServiceAction(BaseModel):
    """Service action (SSM Automation document)."""

    def __init__(
        self,
        name: str,
        definition_type: str,
        definition: dict[str, str],
        description: Optional[str],
        accept_language: Optional[str],
        region_name: str,
        account_id: str,
    ) -> None:
        self.id = f"act-{uuid.uuid4().hex[:12]}"
        self.name = name
        self.definition_type = definition_type
        self.definition = definition
        self.description = description or ""
        self.accept_language = accept_language
        self.created_time = utcnow()
        self.region_name = region_name
        self.account_id = account_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
            "DefinitionType": self.definition_type,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        d = self.to_dict()
        d["Definition"] = self.definition
        return d


class TagOption(BaseModel):
    """Tag option resource."""

    def __init__(
        self,
        key: str,
        value: str,
        region_name: str,
        account_id: str,
    ) -> None:
        self.id = f"tag-{uuid.uuid4().hex[:12]}"
        self.key = key
        self.value = value
        self.active = True
        self.owner = account_id
        self.region_name = region_name
        self.account_id = account_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "Key": self.key,
            "Value": self.value,
            "Active": self.active,
            "Owner": self.owner,
        }


class ProvisionedProduct(BaseModel):
    """Provisioned product instance."""

    def __init__(
        self,
        name: str,
        product_id: str,
        provisioning_artifact_id: str,
        path_id: Optional[str],
        provisioning_parameters: Optional[list[dict[str, str]]],
        provisioning_preferences: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
        notification_arns: Optional[list[str]],
        region_name: str,
        account_id: str,
    ) -> None:
        self.id = f"pp-{uuid.uuid4().hex[:12]}"
        self.name = name
        self.product_id = product_id
        self.provisioning_artifact_id = provisioning_artifact_id
        self.path_id = path_id or ""
        self.provisioning_parameters = provisioning_parameters or []
        self.provisioning_preferences = provisioning_preferences or {}
        self.tags = tags or []
        self.notification_arns = notification_arns or []
        self.status = "AVAILABLE"
        self.status_message = ""
        self.created_time = utcnow()
        self.last_record_id = f"rec-{uuid.uuid4().hex[:12]}"
        self.last_provisioning_record_id = self.last_record_id
        self.last_successful_provisioning_record_id = self.last_record_id
        self.product_name = ""
        self.provisioning_artifact_name = ""
        self.user_arn = f"arn:aws:iam::{account_id}:root"
        self.type = "CFN_STACK"
        self.region_name = region_name
        self.account_id = account_id
        self.outputs: list[dict[str, str]] = []
        self.idempotency_token: Optional[str] = None

    @property
    def arn(self) -> str:
        return (
            f"arn:{get_partition(self.region_name)}:servicecatalog:"
            f"{self.region_name}:{self.account_id}:stack/{self.name}/{self.id}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Arn": self.arn,
            "Type": self.type,
            "Id": self.id,
            "Status": self.status,
            "StatusMessage": self.status_message,
            "CreatedTime": self.created_time,
            "IdempotencyToken": self.idempotency_token or "",
            "LastRecordId": self.last_record_id,
            "LastProvisioningRecordId": self.last_provisioning_record_id,
            "LastSuccessfulProvisioningRecordId": self.last_successful_provisioning_record_id,
            "ProductId": self.product_id,
            "ProvisioningArtifactId": self.provisioning_artifact_id,
            "UserArn": self.user_arn,
            "UserArnSession": self.user_arn,
        }

    def to_record_detail(self) -> dict[str, Any]:
        return {
            "RecordId": self.last_record_id,
            "ProvisionedProductName": self.name,
            "Status": "SUCCEEDED",
            "CreatedTime": self.created_time,
            "UpdatedTime": self.created_time,
            "ProvisionedProductType": self.type,
            "RecordType": "PROVISION_PRODUCT",
            "ProvisionedProductId": self.id,
            "ProductId": self.product_id,
            "ProvisioningArtifactId": self.provisioning_artifact_id,
            "PathId": self.path_id,
            "RecordErrors": [],
            "RecordTags": [],
        }


class ProvisionedProductPlan(BaseModel):
    """Plan for provisioning a product."""

    def __init__(
        self,
        plan_name: str,
        plan_type: str,
        product_id: str,
        provisioned_product_name: str,
        provisioning_artifact_id: str,
        path_id: Optional[str],
        provisioning_parameters: Optional[list[dict[str, str]]],
        tags: Optional[list[dict[str, str]]],
        notification_arns: Optional[list[str]],
        region_name: str,
        account_id: str,
    ) -> None:
        self.plan_id = f"plan-{uuid.uuid4().hex[:12]}"
        self.plan_name = plan_name
        self.plan_type = plan_type
        self.product_id = product_id
        self.provisioned_product_name = provisioned_product_name
        self.provisioning_artifact_id = provisioning_artifact_id
        self.path_id = path_id or ""
        self.provisioning_parameters = provisioning_parameters or []
        self.tags = tags or []
        self.notification_arns = notification_arns or []
        self.status = "CREATE_SUCCESS"
        self.status_message = ""
        self.created_time = utcnow()
        self.updated_time = self.created_time
        self.provision_product_id = f"pp-{uuid.uuid4().hex[:12]}"
        self.region_name = region_name
        self.account_id = account_id

    def to_summary(self) -> dict[str, Any]:
        return {
            "PlanName": self.plan_name,
            "PlanId": self.plan_id,
            "ProvisionProductId": self.provision_product_id,
            "ProvisionProductName": self.provisioned_product_name,
            "PlanType": self.plan_type,
            "ProvisioningArtifactId": self.provisioning_artifact_id,
        }

    def to_detail(self) -> dict[str, Any]:
        return {
            "PlanName": self.plan_name,
            "PlanId": self.plan_id,
            "ProvisionProductId": self.provision_product_id,
            "ProvisionProductName": self.provisioned_product_name,
            "PlanType": self.plan_type,
            "ProvisioningArtifactId": self.provisioning_artifact_id,
            "Status": self.status,
            "StatusMessage": self.status_message,
            "CreatedTime": self.created_time,
            "UpdatedTime": self.updated_time,
            "PathId": self.path_id,
            "ProductId": self.product_id,
            "NotificationArns": self.notification_arns,
            "Tags": self.tags,
            "ResourceChanges": [],
        }


class Record(BaseModel):
    """Record of a Service Catalog operation."""

    def __init__(
        self,
        provisioned_product_id: str,
        provisioned_product_name: str,
        product_id: str,
        provisioning_artifact_id: str,
        path_id: str,
        record_type: str,
        region_name: str,
        account_id: str,
    ) -> None:
        self.record_id = f"rec-{uuid.uuid4().hex[:12]}"
        self.provisioned_product_id = provisioned_product_id
        self.provisioned_product_name = provisioned_product_name
        self.product_id = product_id
        self.provisioning_artifact_id = provisioning_artifact_id
        self.path_id = path_id
        self.record_type = record_type
        self.status = "SUCCEEDED"
        self.created_time = utcnow()
        self.updated_time = self.created_time
        self.provisioned_product_type = "CFN_STACK"
        self.record_errors: list[dict[str, str]] = []
        self.record_tags: list[dict[str, str]] = []
        self.record_outputs: list[dict[str, str]] = []
        self.region_name = region_name
        self.account_id = account_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "RecordId": self.record_id,
            "ProvisionedProductName": self.provisioned_product_name,
            "Status": self.status,
            "CreatedTime": self.created_time,
            "UpdatedTime": self.updated_time,
            "ProvisionedProductType": self.provisioned_product_type,
            "RecordType": self.record_type,
            "ProvisionedProductId": self.provisioned_product_id,
            "ProductId": self.product_id,
            "ProvisioningArtifactId": self.provisioning_artifact_id,
            "PathId": self.path_id,
            "RecordErrors": self.record_errors,
            "RecordTags": self.record_tags,
        }


class ServiceCatalogBackend(BaseBackend):
    """Implementation of ServiceCatalog APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.portfolio_access: dict[str, list[str]] = {}
        self.portfolios: dict[str, Portfolio] = {}
        self.idempotency_tokens: dict[str, str] = {}
        self.portfolio_share_tokens: dict[str, list[str]] = {}
        self.products: dict[str, Product] = {}
        self.tagger = TaggingService()
        # New stores
        self.provisioning_artifacts: dict[str, ProvisioningArtifact] = {}
        self.constraints: dict[str, Constraint] = {}
        self.service_actions: dict[str, ServiceAction] = {}
        self.tag_options: dict[str, TagOption] = {}
        self.provisioned_products: dict[str, ProvisionedProduct] = {}
        self.provisioned_product_plans: dict[str, ProvisionedProductPlan] = {}
        self.records: dict[str, Record] = {}
        # Associations
        self.product_portfolio_associations: list[tuple[str, str]] = []
        self.principal_portfolio_associations: list[
            tuple[str, str, str]
        ] = []  # (principal_arn, portfolio_id, principal_type)
        self.tag_option_resource_associations: list[
            tuple[str, str]
        ] = []  # (tag_option_id, resource_id)
        self.budget_resource_associations: list[
            tuple[str, str]
        ] = []  # (budget_name, resource_id)
        self.service_action_artifact_associations: list[
            tuple[str, str, str]
        ] = []  # (service_action_id, product_id, provisioning_artifact_id)
        self.accepted_portfolio_shares: list[str] = []
        self.copy_product_operations: dict[str, dict[str, Any]] = {}
        self.aws_organizations_access_enabled = False

    # ---- Tagging helpers ----

    def _tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(resource_arn, tags)

    def _list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        if self.tagger.has_tags(resource_arn):
            return self.tagger.list_tags_for_resource(resource_arn)["Tags"]
        return []

    # ---- Portfolio operations ----

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_portfolio_access(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        organization_parent_id: Optional[str],
        page_token: Optional[str],
        page_size: Optional[int] = None,
    ) -> list[dict[str, str]]:
        account_ids = self.portfolio_access.get(portfolio_id, [])
        return [{"account_id": account_id} for account_id in account_ids]

    def delete_portfolio(self, accept_language: Optional[str], portfolio_id: str) -> None:
        if portfolio_id not in self.portfolios:
            raise ResourceNotFoundException(f"Portfolio {portfolio_id} not found.")
        if portfolio_id in self.portfolio_access:
            del self.portfolio_access[portfolio_id]
        del self.portfolios[portfolio_id]

    def delete_portfolio_share(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        account_id: Optional[str],
        organization_node: Optional[dict[str, str]],
    ) -> Optional[str]:
        if (
            portfolio_id in self.portfolio_access
            and account_id
            and account_id in self.portfolio_access[portfolio_id]
        ):
            self.portfolio_access[portfolio_id].remove(account_id)

        portfolio_share_token = None
        if organization_node:
            org_type = organization_node.get("Type", "")
            org_value = organization_node.get("Value", "")
            portfolio_share_token = f"share-{portfolio_id}-{org_type}-{org_value}"
            if portfolio_id in self.portfolio_share_tokens:
                tokens_to_remove = [
                    t
                    for t in self.portfolio_share_tokens[portfolio_id]
                    if org_type in t and org_value in t
                ]
                for token in tokens_to_remove:
                    self.portfolio_share_tokens[portfolio_id].remove(token)

        return portfolio_share_token

    def create_portfolio(
        self,
        accept_language: Optional[str],
        display_name: str,
        description: Optional[str],
        provider_name: str,
        tags: Optional[list[dict[str, str]]],
        idempotency_token: Optional[str],
    ) -> tuple[dict[str, str], list[dict[str, str]]]:
        if idempotency_token and idempotency_token in self.idempotency_tokens:
            portfolio_id = self.idempotency_tokens[idempotency_token]
            portfolio = self.portfolios[portfolio_id]
            return portfolio.to_dict(), portfolio.tags

        portfolio_id = str(uuid.uuid4())
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            display_name=display_name,
            description=description or "",
            provider_name=provider_name,
            tags=tags or [],
            region_name=self.region_name,
            account_id=self.account_id,
            backend=self,
        )
        self.portfolios[portfolio_id] = portfolio
        if idempotency_token:
            self.idempotency_tokens[idempotency_token] = portfolio_id
        self.portfolio_access[portfolio_id] = []
        return portfolio.to_dict(), portfolio.tags

    def create_portfolio_share(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        account_id: Optional[str],
        organization_node: Optional[dict[str, str]],
        share_tag_options: bool,
        share_principals: bool,
    ) -> Optional[str]:
        if portfolio_id not in self.portfolios:
            return None

        if account_id:
            if portfolio_id not in self.portfolio_access:
                self.portfolio_access[portfolio_id] = []
            if account_id not in self.portfolio_access[portfolio_id]:
                self.portfolio_access[portfolio_id].append(account_id)
            return None

        portfolio_share_token = None
        if organization_node:
            org_type = organization_node.get("Type", "")
            org_value = organization_node.get("Value", "")
            portfolio_share_token = f"share-{portfolio_id}-{org_type}-{org_value}"
            if share_tag_options:
                portfolio_share_token += "-tags"
            if share_principals:
                portfolio_share_token += "-principals"
            if portfolio_id not in self.portfolio_share_tokens:
                self.portfolio_share_tokens[portfolio_id] = []
            if portfolio_share_token not in self.portfolio_share_tokens[portfolio_id]:
                self.portfolio_share_tokens[portfolio_id].append(portfolio_share_token)

        return portfolio_share_token

    def list_portfolios(
        self,
        accept_language: Optional[str] = None,
        page_token: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> tuple[list[dict[str, str]], Optional[str]]:
        portfolio_details = [p.to_dict() for p in self.portfolios.values()]
        return portfolio_details, None

    def describe_portfolio_shares(
        self,
        portfolio_id: str,
        share_type: str,
        page_token: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> tuple[Optional[str], list[dict[str, Any]]]:
        portfolio_share_details: list[dict[str, Any]] = []
        if portfolio_id not in self.portfolios:
            return None, []

        if share_type == "ACCOUNT":
            account_ids = self.portfolio_access.get(portfolio_id, [])
            for aid in account_ids:
                portfolio_share_details.append(
                    {
                        "PrincipalId": aid,
                        "Type": "ACCOUNT",
                        "Accepted": True,
                        "ShareTagOptions": False,
                        "SharePrincipals": False,
                    }
                )
        elif share_type == "ORGANIZATION":
            tokens = self.portfolio_share_tokens.get(portfolio_id, [])
            for token in tokens:
                if "ORGANIZATION" in token and "-o-" in token:
                    org_id_start = token.find("-ORGANIZATION-") + len("-ORGANIZATION-")
                    if "-tags" in token:
                        org_id_end = token.find("-tags", org_id_start)
                    elif "-principals" in token:
                        org_id_end = token.find("-principals", org_id_start)
                    else:
                        org_id_end = len(token)
                    org_id = token[org_id_start:org_id_end]
                    portfolio_share_details.append(
                        {
                            "PrincipalId": org_id,
                            "Type": "ORGANIZATION",
                            "Accepted": True,
                            "ShareTagOptions": "tags" in token,
                            "SharePrincipals": "principals" in token,
                        }
                    )

        return None, portfolio_share_details

    def describe_portfolio(
        self, accept_language: Optional[str], portfolio_id: str
    ) -> tuple[
        dict[str, Any], list[dict[str, str]], list[dict[str, Any]], list[dict[str, str]]
    ]:
        if portfolio_id not in self.portfolios:
            raise ResourceNotFoundException(
                f"Portfolio {portfolio_id} not found."
            )
        portfolio = self.portfolios[portfolio_id]
        portfolio_detail = portfolio.to_dict()
        tags = portfolio.tags
        tag_options: list[dict[str, Any]] = [
            self.tag_options[assoc[0]].to_dict()
            for assoc in self.tag_option_resource_associations
            if assoc[1] == portfolio_id and assoc[0] in self.tag_options
        ]
        budgets: list[dict[str, Any]] = [
            {"BudgetName": assoc[0]}
            for assoc in self.budget_resource_associations
            if assoc[1] == portfolio_id
        ]
        return portfolio_detail, tags, tag_options, budgets

    def update_portfolio(
        self,
        portfolio_id: str,
        display_name: Optional[str],
        description: Optional[str],
        provider_name: Optional[str],
        add_tags: Optional[list[dict[str, str]]],
        remove_tags: Optional[list[str]],
        accept_language: Optional[str],
    ) -> tuple[dict[str, Any], list[dict[str, str]]]:
        if portfolio_id not in self.portfolios:
            raise ResourceNotFoundException(
                f"Portfolio {portfolio_id} not found."
            )
        portfolio = self.portfolios[portfolio_id]
        if display_name is not None:
            portfolio.display_name = display_name
        if description is not None:
            portfolio.description = description
        if provider_name is not None:
            portfolio.provider_name = provider_name
        if add_tags:
            existing_keys = {t["Key"] for t in portfolio.tags}
            for tag in add_tags:
                if tag["Key"] in existing_keys:
                    portfolio.tags = [
                        t if t["Key"] != tag["Key"] else tag for t in portfolio.tags
                    ]
                else:
                    portfolio.tags.append(tag)
            self._tag_resource(portfolio.arn, add_tags)
        if remove_tags:
            portfolio.tags = [t for t in portfolio.tags if t["Key"] not in remove_tags]
        return portfolio.to_dict(), portfolio.tags

    def update_portfolio_share(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        account_id: Optional[str],
        organization_node: Optional[dict[str, str]],
        share_tag_options: Optional[bool],
        share_principals: Optional[bool],
    ) -> tuple[Optional[str], str]:
        if portfolio_id not in self.portfolios:
            raise ResourceNotFoundException(
                f"Portfolio {portfolio_id} not found."
            )
        status = "COMPLETED"
        portfolio_share_token = None
        if organization_node:
            portfolio_share_token = f"share-{portfolio_id}-update-{uuid.uuid4().hex[:8]}"
        return portfolio_share_token, status

    def describe_portfolio_share_status(
        self,
        portfolio_share_token: str,
    ) -> dict[str, Any]:
        return {
            "PortfolioShareToken": portfolio_share_token,
            "PortfolioId": "",
            "OrganizationNodeValue": "",
            "Status": "COMPLETED",
            "ShareDetails": {"ShareErrors": [], "SuccessfulShares": []},
        }

    def accept_portfolio_share(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        portfolio_share_type: Optional[str],
    ) -> None:
        if portfolio_id not in self.portfolios:
            raise ResourceNotFoundException(
                f"Portfolio {portfolio_id} not found."
            )
        if portfolio_id not in self.accepted_portfolio_shares:
            self.accepted_portfolio_shares.append(portfolio_id)

    def reject_portfolio_share(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        portfolio_share_type: Optional[str],
    ) -> None:
        if portfolio_id in self.accepted_portfolio_shares:
            self.accepted_portfolio_shares.remove(portfolio_id)

    def list_accepted_portfolio_shares(
        self,
        accept_language: Optional[str],
        page_token: Optional[str],
        page_size: Optional[int],
        portfolio_share_type: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        details = []
        for pid in self.accepted_portfolio_shares:
            if pid in self.portfolios:
                details.append(self.portfolios[pid].to_dict())
        return details, None

    def list_portfolios_for_product(
        self,
        accept_language: Optional[str],
        product_id: str,
        page_token: Optional[str],
        page_size: Optional[int],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        portfolio_ids = [
            assoc[1]
            for assoc in self.product_portfolio_associations
            if assoc[0] == product_id
        ]
        details = [
            self.portfolios[pid].to_dict()
            for pid in portfolio_ids
            if pid in self.portfolios
        ]
        return details, None

    def list_organization_portfolio_access(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        organization_node_type: str,
        page_token: Optional[str],
        page_size: Optional[int],
    ) -> tuple[list[str], Optional[str]]:
        org_nodes: list[str] = []
        tokens = self.portfolio_share_tokens.get(portfolio_id, [])
        for token in tokens:
            if organization_node_type in token:
                parts = token.split("-")
                for part in parts:
                    if part.startswith("o-") or part.startswith("ou-") or part.startswith("r-"):
                        org_nodes.append(part)
        return org_nodes, None

    # ---- Product operations ----

    def create_product(
        self,
        name: str,
        owner: str,
        description: Optional[str],
        distributor: Optional[str],
        support_description: Optional[str],
        support_email: Optional[str],
        support_url: Optional[str],
        product_type: str,
        tags: list[dict[str, str]],
        provisioning_artifact_parameters: Optional[dict[str, Any]],
        idempotency_token: Optional[str] = None,
        source_connection: Optional[dict[str, Any]] = None,
        accept_language: Optional[str] = None,
    ) -> Product:
        token = idempotency_token or str(uuid.uuid4())
        existing_id = self.idempotency_tokens.get(token)
        if existing_id and existing_id in self.products:
            return self.products[existing_id]

        product = Product(
            name=name,
            owner=owner,
            description=description,
            distributor=distributor,
            support_description=support_description,
            support_email=support_email,
            support_url=support_url,
            product_type=product_type,
            tags=tags,
            provisioning_artifact_parameters=provisioning_artifact_parameters,
            source_connection=source_connection,
            accept_language=accept_language,
            region_name=self.region_name,
            account_id=self.account_id,
            backend=self,
        )
        self.products[product.id] = product
        self.idempotency_tokens[token] = product.id

        # Create initial provisioning artifact if parameters provided
        if provisioning_artifact_parameters:
            pa = ProvisioningArtifact(
                product_id=product.id,
                name=provisioning_artifact_parameters.get("Name"),
                description=provisioning_artifact_parameters.get("Description"),
                artifact_type=provisioning_artifact_parameters.get("Type"),
                info=provisioning_artifact_parameters.get("Info"),
                disable_template_validation=provisioning_artifact_parameters.get(
                    "DisableTemplateValidation", False
                ),
                region_name=self.region_name,
                account_id=self.account_id,
            )
            self.provisioning_artifacts[pa.id] = pa

        return product

    def describe_product(
        self, accept_language: Optional[str], product_id: str, name: str
    ) -> Product:
        if not product_id and not name:
            raise InvalidParametersException("Either Id or Name must be specified.")
        if product_id:
            product = self.products.get(product_id)
            if not product:
                raise ResourceNotFoundException(
                    f"Product with Id '{product_id}' not found."
                )
        else:
            product = self.lookup_by_name(name)
            if not product:
                raise ResourceNotFoundException(
                    f"Product with Name '{name}' not found."
                )
        return product

    def describe_product_as_admin(
        self,
        accept_language: Optional[str],
        product_id: Optional[str],
        name: Optional[str],
        source_portfolio_id: Optional[str],
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        if not product_id and not name:
            raise InvalidParametersException("Either Id or Name must be specified.")
        if product_id:
            product = self.products.get(product_id)
            if not product:
                raise ResourceNotFoundException(
                    f"Product with Id '{product_id}' not found."
                )
        else:
            product = self.lookup_by_name(name or "")
            if not product:
                raise ResourceNotFoundException(
                    f"Product with Name '{name}' not found."
                )

        pv_detail = product.to_product_view_detail()
        artifacts = self._list_provisioning_artifacts_for_product(product.id)
        tags = product.tags
        budgets = [
            {"BudgetName": assoc[0]}
            for assoc in self.budget_resource_associations
            if assoc[1] == product.id
        ]
        return pv_detail, artifacts, tags, budgets

    def describe_product_view(
        self,
        accept_language: Optional[str],
        product_view_id: str,
    ) -> dict[str, Any]:
        # product_view_id is the same as product id in our impl
        product = self.products.get(product_view_id)
        if not product:
            raise ResourceNotFoundException(
                f"Product with Id '{product_view_id}' not found."
            )
        return product.to_product_view_detail()

    def lookup_by_name(self, name: str) -> Optional[Product]:
        for product in self.products.values():
            if name == product.name:
                return product
        return None

    def delete_product(self, accept_language: Optional[str], product_id: str) -> None:
        # Check if product is associated with any portfolio
        for assoc in self.product_portfolio_associations:
            if assoc[0] == product_id:
                raise ResourceInUseException(
                    f"Product {product_id} is associated with portfolio {assoc[1]}."
                )
        if product_id in self.products:
            del self.products[product_id]

    def update_product(
        self,
        product_id: str,
        accept_language: Optional[str],
        name: Optional[str],
        owner: Optional[str],
        description: Optional[str],
        distributor: Optional[str],
        support_description: Optional[str],
        support_email: Optional[str],
        support_url: Optional[str],
        add_tags: Optional[list[dict[str, str]]],
        remove_tags: Optional[list[str]],
        source_connection: Optional[dict[str, Any]],
    ) -> Product:
        if product_id not in self.products:
            raise ResourceNotFoundException(
                f"Product {product_id} not found."
            )
        product = self.products[product_id]
        if name is not None:
            product.name = name
        if owner is not None:
            product.owner = owner
        if description is not None:
            product.description = description
        if distributor is not None:
            product.distributor = distributor
        if support_description is not None:
            product.support_description = support_description
        if support_email is not None:
            product.support_email = support_email
        if support_url is not None:
            product.support_url = support_url
        if source_connection is not None:
            product.source_connection = source_connection
        if add_tags:
            existing_keys = {t["Key"] for t in product.tags}
            for tag in add_tags:
                if tag["Key"] in existing_keys:
                    product.tags = [
                        t if t["Key"] != tag["Key"] else tag for t in product.tags
                    ]
                else:
                    product.tags.append(tag)
            self._tag_resource(product.arn, add_tags)
        if remove_tags:
            product.tags = [t for t in product.tags if t["Key"] not in remove_tags]
        return product

    def copy_product(
        self,
        accept_language: Optional[str],
        source_product_arn: str,
        target_product_id: Optional[str],
        target_product_name: Optional[str],
        source_provisioning_artifact_identifiers: Optional[list[dict[str, str]]],
        copy_options: Optional[list[str]],
        idempotency_token: Optional[str],
    ) -> str:
        copy_token = f"cpt-{uuid.uuid4().hex[:12]}"
        self.copy_product_operations[copy_token] = {
            "SourceProductArn": source_product_arn,
            "TargetProductId": target_product_id,
            "TargetProductName": target_product_name,
            "CopyProductStatus": "SUCCEEDED",
        }
        return copy_token

    def describe_copy_product_status(
        self,
        accept_language: Optional[str],
        copy_product_token: str,
    ) -> dict[str, Any]:
        op = self.copy_product_operations.get(copy_product_token, {})
        return {
            "CopyProductStatus": op.get("CopyProductStatus", "FAILED"),
            "TargetProductId": op.get("TargetProductId", ""),
        }

    def search_products(
        self,
        accept_language: Optional[str],
        filters: Optional[dict[str, list[str]]],
        page_size: Optional[int],
        sort_by: Optional[str],
        sort_order: Optional[str],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Optional[str]]:
        product_view_summaries = []
        product_view_aggregations: list[dict[str, Any]] = []
        for product in self.products.values():
            if filters:
                match = True
                for filter_key, filter_values in filters.items():
                    if filter_key == "FullTextSearch":
                        text_match = False
                        for val in filter_values:
                            val_lower = val.lower()
                            if (
                                val_lower in (product.name or "").lower()
                                or val_lower in (product.description or "").lower()
                                or val_lower in (product.owner or "").lower()
                            ):
                                text_match = True
                                break
                        if not text_match:
                            match = False
                    elif filter_key == "Owner" and product.owner not in filter_values:
                        match = False
                    elif filter_key == "ProductType" and product.product_type not in filter_values:
                        match = False
                if not match:
                    continue
            product_view_summaries.append(product.to_dict())
        return product_view_summaries, product_view_aggregations, None

    def search_products_as_admin(
        self,
        accept_language: Optional[str],
        portfolio_id: Optional[str],
        filters: Optional[dict[str, list[str]]],
        sort_by: Optional[str],
        sort_order: Optional[str],
        page_token: Optional[str],
        page_size: Optional[int],
        product_source: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        product_view_details = []
        if portfolio_id:
            product_ids = [
                assoc[0]
                for assoc in self.product_portfolio_associations
                if assoc[1] == portfolio_id
            ]
        else:
            product_ids = list(self.products.keys())

        for pid in product_ids:
            product = self.products.get(pid)
            if not product:
                continue
            if filters:
                match = True
                for filter_key, filter_values in filters.items():
                    if filter_key == "FullTextSearch":
                        text_match = any(
                            v.lower() in (product.name or "").lower()
                            or v.lower() in (product.description or "").lower()
                            for v in filter_values
                        )
                        if not text_match:
                            match = False
                    elif filter_key == "Owner" and product.owner not in filter_values:
                        match = False
                    elif filter_key == "ProductType" and product.product_type not in filter_values:
                        match = False
                if not match:
                    continue
            product_view_details.append(product.to_product_view_detail())
        return product_view_details, None

    # ---- Association operations ----

    def associate_product_with_portfolio(
        self,
        accept_language: Optional[str],
        product_id: str,
        portfolio_id: str,
        source_portfolio_id: Optional[str],
    ) -> None:
        if product_id not in self.products:
            raise ResourceNotFoundException(f"Product {product_id} not found.")
        if portfolio_id not in self.portfolios:
            raise ResourceNotFoundException(f"Portfolio {portfolio_id} not found.")
        assoc = (product_id, portfolio_id)
        if assoc not in self.product_portfolio_associations:
            self.product_portfolio_associations.append(assoc)

    def disassociate_product_from_portfolio(
        self,
        accept_language: Optional[str],
        product_id: str,
        portfolio_id: str,
    ) -> None:
        assoc = (product_id, portfolio_id)
        if assoc in self.product_portfolio_associations:
            self.product_portfolio_associations.remove(assoc)
        else:
            raise ResourceNotFoundException(
                f"Association between Product {product_id} and "
                f"Portfolio {portfolio_id} not found."
            )

    def associate_principal_with_portfolio(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        principal_arn: str,
        principal_type: str,
    ) -> None:
        if portfolio_id not in self.portfolios:
            raise ResourceNotFoundException(f"Portfolio {portfolio_id} not found.")
        assoc = (principal_arn, portfolio_id, principal_type)
        if assoc not in self.principal_portfolio_associations:
            self.principal_portfolio_associations.append(assoc)

    def disassociate_principal_from_portfolio(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        principal_arn: str,
        principal_type: Optional[str],
    ) -> None:
        to_remove = [
            a
            for a in self.principal_portfolio_associations
            if a[0] == principal_arn and a[1] == portfolio_id
        ]
        if not to_remove:
            raise ResourceNotFoundException(
                f"Principal {principal_arn} not associated with Portfolio {portfolio_id}."
            )
        for a in to_remove:
            self.principal_portfolio_associations.remove(a)

    def list_principals_for_portfolio(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, str]], Optional[str]]:
        principals = [
            {"PrincipalARN": a[0], "PrincipalType": a[2]}
            for a in self.principal_portfolio_associations
            if a[1] == portfolio_id
        ]
        return principals, None

    def associate_budget_with_resource(
        self,
        budget_name: str,
        resource_id: str,
    ) -> None:
        assoc = (budget_name, resource_id)
        if assoc not in self.budget_resource_associations:
            self.budget_resource_associations.append(assoc)

    def disassociate_budget_from_resource(
        self,
        budget_name: str,
        resource_id: str,
    ) -> None:
        assoc = (budget_name, resource_id)
        if assoc in self.budget_resource_associations:
            self.budget_resource_associations.remove(assoc)

    def list_budgets_for_resource(
        self,
        accept_language: Optional[str],
        resource_id: str,
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, str]], Optional[str]]:
        budgets = [
            {"BudgetName": assoc[0]}
            for assoc in self.budget_resource_associations
            if assoc[1] == resource_id
        ]
        return budgets, None

    # ---- Provisioning Artifact operations ----

    def _list_provisioning_artifacts_for_product(
        self, product_id: str
    ) -> list[dict[str, Any]]:
        return [
            pa.to_dict()
            for pa in self.provisioning_artifacts.values()
            if pa.product_id == product_id
        ]

    def create_provisioning_artifact(
        self,
        accept_language: Optional[str],
        product_id: str,
        parameters: dict[str, Any],
        idempotency_token: Optional[str],
    ) -> tuple[dict[str, Any], dict[str, str], str]:
        if product_id not in self.products:
            raise ResourceNotFoundException(f"Product {product_id} not found.")
        pa = ProvisioningArtifact(
            product_id=product_id,
            name=parameters.get("Name"),
            description=parameters.get("Description"),
            artifact_type=parameters.get("Type"),
            info=parameters.get("Info"),
            disable_template_validation=parameters.get(
                "DisableTemplateValidation", False
            ),
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.provisioning_artifacts[pa.id] = pa
        info = pa.info or {}
        return pa.to_dict(), info, "AVAILABLE"

    def describe_provisioning_artifact(
        self,
        accept_language: Optional[str],
        provisioning_artifact_id: Optional[str],
        product_id: Optional[str],
        provisioning_artifact_name: Optional[str],
        product_name: Optional[str],
        verbose: Optional[bool],
    ) -> tuple[dict[str, Any], dict[str, str], str]:
        pa = None
        if provisioning_artifact_id:
            pa = self.provisioning_artifacts.get(provisioning_artifact_id)
        elif provisioning_artifact_name and product_id:
            for artifact in self.provisioning_artifacts.values():
                if (
                    artifact.name == provisioning_artifact_name
                    and artifact.product_id == product_id
                ):
                    pa = artifact
                    break
        if not pa:
            raise ResourceNotFoundException("ProvisioningArtifact not found.")
        return pa.to_dict(), pa.info, "AVAILABLE"

    def update_provisioning_artifact(
        self,
        accept_language: Optional[str],
        product_id: str,
        provisioning_artifact_id: str,
        name: Optional[str],
        description: Optional[str],
        active: Optional[bool],
        guidance: Optional[str],
    ) -> tuple[dict[str, Any], dict[str, str], str]:
        pa = self.provisioning_artifacts.get(provisioning_artifact_id)
        if not pa:
            raise ResourceNotFoundException("ProvisioningArtifact not found.")
        if name is not None:
            pa.name = name
        if description is not None:
            pa.description = description
        if active is not None:
            pa.active = active
        if guidance is not None:
            pa.guidance = guidance
        return pa.to_dict(), pa.info, "AVAILABLE"

    def delete_provisioning_artifact(
        self,
        accept_language: Optional[str],
        product_id: str,
        provisioning_artifact_id: str,
    ) -> None:
        if provisioning_artifact_id in self.provisioning_artifacts:
            del self.provisioning_artifacts[provisioning_artifact_id]
        else:
            raise ResourceNotFoundException("ProvisioningArtifact not found.")

    def list_provisioning_artifacts(
        self,
        accept_language: Optional[str],
        product_id: str,
    ) -> list[dict[str, Any]]:
        return self._list_provisioning_artifacts_for_product(product_id)

    def describe_provisioning_parameters(
        self,
        accept_language: Optional[str],
        product_id: Optional[str],
        product_name: Optional[str],
        provisioning_artifact_id: Optional[str],
        provisioning_artifact_name: Optional[str],
        path_id: Optional[str],
        path_name: Optional[str],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
        provisioning_artifact_parameters: list[dict[str, Any]] = []
        constraint_summaries: list[dict[str, Any]] = []
        usage_instructions: list[dict[str, Any]] = []
        tag_options: list[str] = []
        return (
            provisioning_artifact_parameters,
            constraint_summaries,
            usage_instructions,
            tag_options,
        )

    def list_provisioning_artifacts_for_service_action(
        self,
        service_action_id: str,
        page_size: Optional[int],
        page_token: Optional[str],
        accept_language: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        results = []
        for assoc in self.service_action_artifact_associations:
            if assoc[0] == service_action_id:
                pa = self.provisioning_artifacts.get(assoc[2])
                if pa:
                    results.append(
                        {
                            "ProductId": assoc[1],
                            "ProvisioningArtifactId": assoc[2],
                            "ProvisioningArtifactDetail": pa.to_dict(),
                        }
                    )
        return results, None

    # ---- Constraint operations ----

    def create_constraint(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        product_id: str,
        parameters: str,
        constraint_type: str,
        description: Optional[str],
        idempotency_token: Optional[str],
    ) -> tuple[dict[str, Any], str, str]:
        if portfolio_id not in self.portfolios:
            raise ResourceNotFoundException(f"Portfolio {portfolio_id} not found.")
        if product_id not in self.products:
            raise ResourceNotFoundException(f"Product {product_id} not found.")
        constraint = Constraint(
            portfolio_id=portfolio_id,
            product_id=product_id,
            parameters=parameters,
            constraint_type=constraint_type,
            description=description,
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.constraints[constraint.id] = constraint
        return constraint.to_detail_dict(), parameters, "AVAILABLE"

    def describe_constraint(
        self,
        accept_language: Optional[str],
        constraint_id: str,
    ) -> tuple[dict[str, Any], str, str]:
        constraint = self.constraints.get(constraint_id)
        if not constraint:
            raise ResourceNotFoundException(
                f"Constraint {constraint_id} not found."
            )
        return constraint.to_detail_dict(), constraint.parameters, "AVAILABLE"

    def update_constraint(
        self,
        accept_language: Optional[str],
        constraint_id: str,
        description: Optional[str],
        parameters: Optional[str],
    ) -> tuple[dict[str, Any], str, str]:
        constraint = self.constraints.get(constraint_id)
        if not constraint:
            raise ResourceNotFoundException(
                f"Constraint {constraint_id} not found."
            )
        if description is not None:
            constraint.description = description
        if parameters is not None:
            constraint.parameters = parameters
        return constraint.to_detail_dict(), constraint.parameters, "AVAILABLE"

    def delete_constraint(
        self,
        accept_language: Optional[str],
        constraint_id: str,
    ) -> None:
        if constraint_id not in self.constraints:
            raise ResourceNotFoundException(
                f"Constraint {constraint_id} not found."
            )
        del self.constraints[constraint_id]

    def list_constraints_for_portfolio(
        self,
        accept_language: Optional[str],
        portfolio_id: str,
        product_id: Optional[str],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        details = []
        for constraint in self.constraints.values():
            if constraint.portfolio_id == portfolio_id:
                if product_id and constraint.product_id != product_id:
                    continue
                details.append(constraint.to_dict())
        return details, None

    # ---- Service Action operations ----

    def create_service_action(
        self,
        name: str,
        definition_type: str,
        definition: dict[str, str],
        description: Optional[str],
        accept_language: Optional[str],
        idempotency_token: Optional[str],
    ) -> dict[str, Any]:
        action = ServiceAction(
            name=name,
            definition_type=definition_type,
            definition=definition,
            description=description,
            accept_language=accept_language,
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.service_actions[action.id] = action
        return action.to_detail_dict()

    def describe_service_action(
        self,
        service_action_id: str,
        accept_language: Optional[str],
    ) -> dict[str, Any]:
        action = self.service_actions.get(service_action_id)
        if not action:
            raise ResourceNotFoundException(
                f"ServiceAction {service_action_id} not found."
            )
        return action.to_detail_dict()

    def describe_service_action_execution_parameters(
        self,
        provisioned_product_id: str,
        service_action_id: str,
        accept_language: Optional[str],
    ) -> list[dict[str, Any]]:
        return []

    def update_service_action(
        self,
        service_action_id: str,
        name: Optional[str],
        definition: Optional[dict[str, str]],
        description: Optional[str],
        accept_language: Optional[str],
    ) -> dict[str, Any]:
        action = self.service_actions.get(service_action_id)
        if not action:
            raise ResourceNotFoundException(
                f"ServiceAction {service_action_id} not found."
            )
        if name is not None:
            action.name = name
        if definition is not None:
            action.definition = definition
        if description is not None:
            action.description = description
        return action.to_detail_dict()

    def delete_service_action(
        self,
        service_action_id: str,
        accept_language: Optional[str],
    ) -> None:
        if service_action_id not in self.service_actions:
            raise ResourceNotFoundException(
                f"ServiceAction {service_action_id} not found."
            )
        # Remove associations
        self.service_action_artifact_associations = [
            a
            for a in self.service_action_artifact_associations
            if a[0] != service_action_id
        ]
        del self.service_actions[service_action_id]

    def list_service_actions(
        self,
        accept_language: Optional[str],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        details = [a.to_dict() for a in self.service_actions.values()]
        return details, None

    def list_service_actions_for_provisioning_artifact(
        self,
        product_id: str,
        provisioning_artifact_id: str,
        page_size: Optional[int],
        page_token: Optional[str],
        accept_language: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        action_ids = [
            a[0]
            for a in self.service_action_artifact_associations
            if a[1] == product_id and a[2] == provisioning_artifact_id
        ]
        details = [
            self.service_actions[aid].to_dict()
            for aid in action_ids
            if aid in self.service_actions
        ]
        return details, None

    def associate_service_action_with_provisioning_artifact(
        self,
        product_id: str,
        provisioning_artifact_id: str,
        service_action_id: str,
        accept_language: Optional[str],
    ) -> None:
        if service_action_id not in self.service_actions:
            raise ResourceNotFoundException(
                f"ServiceAction {service_action_id} not found."
            )
        assoc = (service_action_id, product_id, provisioning_artifact_id)
        if assoc not in self.service_action_artifact_associations:
            self.service_action_artifact_associations.append(assoc)

    def disassociate_service_action_from_provisioning_artifact(
        self,
        product_id: str,
        provisioning_artifact_id: str,
        service_action_id: str,
        accept_language: Optional[str],
    ) -> None:
        assoc = (service_action_id, product_id, provisioning_artifact_id)
        if assoc in self.service_action_artifact_associations:
            self.service_action_artifact_associations.remove(assoc)

    def batch_associate_service_action_with_provisioning_artifact(
        self,
        service_action_associations: list[dict[str, str]],
        accept_language: Optional[str],
    ) -> list[dict[str, Any]]:
        failed: list[dict[str, Any]] = []
        for entry in service_action_associations:
            try:
                self.associate_service_action_with_provisioning_artifact(
                    product_id=entry["ProductId"],
                    provisioning_artifact_id=entry["ProvisioningArtifactId"],
                    service_action_id=entry["ServiceActionId"],
                    accept_language=accept_language,
                )
            except ResourceNotFoundException as e:
                failed.append(
                    {
                        "ServiceActionId": entry["ServiceActionId"],
                        "ProductId": entry["ProductId"],
                        "ProvisioningArtifactId": entry["ProvisioningArtifactId"],
                        "ErrorCode": "RESOURCE_NOT_FOUND",
                        "ErrorMessage": str(e),
                    }
                )
        return failed

    def batch_disassociate_service_action_from_provisioning_artifact(
        self,
        service_action_associations: list[dict[str, str]],
        accept_language: Optional[str],
    ) -> list[dict[str, Any]]:
        failed: list[dict[str, Any]] = []
        for entry in service_action_associations:
            self.disassociate_service_action_from_provisioning_artifact(
                product_id=entry["ProductId"],
                provisioning_artifact_id=entry["ProvisioningArtifactId"],
                service_action_id=entry["ServiceActionId"],
                accept_language=accept_language,
            )
        return failed

    # ---- TagOption operations ----

    def create_tag_option(
        self,
        key: str,
        value: str,
    ) -> dict[str, Any]:
        # Check for duplicate
        for to in self.tag_options.values():
            if to.key == key and to.value == value:
                raise DuplicateResourceException(
                    f"TagOption with Key '{key}' and Value '{value}' already exists."
                )
        tag_option = TagOption(
            key=key,
            value=value,
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.tag_options[tag_option.id] = tag_option
        return tag_option.to_dict()

    def describe_tag_option(
        self,
        tag_option_id: str,
    ) -> dict[str, Any]:
        tag_option = self.tag_options.get(tag_option_id)
        if not tag_option:
            raise ResourceNotFoundException(
                f"TagOption {tag_option_id} not found."
            )
        return tag_option.to_dict()

    def update_tag_option(
        self,
        tag_option_id: str,
        value: Optional[str],
        active: Optional[bool],
    ) -> dict[str, Any]:
        tag_option = self.tag_options.get(tag_option_id)
        if not tag_option:
            raise ResourceNotFoundException(
                f"TagOption {tag_option_id} not found."
            )
        if value is not None:
            tag_option.value = value
        if active is not None:
            tag_option.active = active
        return tag_option.to_dict()

    def delete_tag_option(
        self,
        tag_option_id: str,
    ) -> None:
        if tag_option_id not in self.tag_options:
            raise ResourceNotFoundException(
                f"TagOption {tag_option_id} not found."
            )
        # Remove associations
        self.tag_option_resource_associations = [
            a
            for a in self.tag_option_resource_associations
            if a[0] != tag_option_id
        ]
        del self.tag_options[tag_option_id]

    def list_tag_options(
        self,
        filters: Optional[dict[str, Any]],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        tag_options = list(self.tag_options.values())
        if filters:
            key_filter = filters.get("Key")
            value_filter = filters.get("Value")
            active_filter = filters.get("Active")
            if key_filter:
                tag_options = [t for t in tag_options if t.key == key_filter]
            if value_filter:
                tag_options = [t for t in tag_options if t.value == value_filter]
            if active_filter is not None:
                tag_options = [t for t in tag_options if t.active == active_filter]
        return [t.to_dict() for t in tag_options], None

    def associate_tag_option_with_resource(
        self,
        resource_id: str,
        tag_option_id: str,
    ) -> None:
        if tag_option_id not in self.tag_options:
            raise ResourceNotFoundException(
                f"TagOption {tag_option_id} not found."
            )
        assoc = (tag_option_id, resource_id)
        if assoc not in self.tag_option_resource_associations:
            self.tag_option_resource_associations.append(assoc)

    def disassociate_tag_option_from_resource(
        self,
        resource_id: str,
        tag_option_id: str,
    ) -> None:
        assoc = (tag_option_id, resource_id)
        if assoc in self.tag_option_resource_associations:
            self.tag_option_resource_associations.remove(assoc)

    def list_resources_for_tag_option(
        self,
        tag_option_id: str,
        resource_type: Optional[str],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        resource_ids = [
            a[1]
            for a in self.tag_option_resource_associations
            if a[0] == tag_option_id
        ]
        resource_details = []
        for rid in resource_ids:
            if rid in self.portfolios:
                if resource_type and resource_type != "Portfolio":
                    continue
                resource_details.append(
                    {
                        "Id": rid,
                        "ARN": self.portfolios[rid].arn,
                        "Name": self.portfolios[rid].display_name,
                        "Description": self.portfolios[rid].description,
                        "CreatedTime": self.portfolios[rid].created_time,
                    }
                )
            elif rid in self.products:
                if resource_type and resource_type != "Product":
                    continue
                resource_details.append(
                    {
                        "Id": rid,
                        "ARN": self.products[rid].arn,
                        "Name": self.products[rid].name,
                        "Description": self.products[rid].description,
                        "CreatedTime": self.products[rid].created_time,
                    }
                )
        return resource_details, None

    # ---- Provisioned Product operations ----

    def provision_product(
        self,
        accept_language: Optional[str],
        product_id: Optional[str],
        product_name: Optional[str],
        provisioning_artifact_id: Optional[str],
        provisioning_artifact_name: Optional[str],
        path_id: Optional[str],
        path_name: Optional[str],
        provisioned_product_name: str,
        provisioning_parameters: Optional[list[dict[str, str]]],
        provisioning_preferences: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
        notification_arns: Optional[list[str]],
        provision_token: Optional[str],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        resolved_product_id = product_id or ""
        if not resolved_product_id and product_name:
            product = self.lookup_by_name(product_name)
            if product:
                resolved_product_id = product.id
        resolved_artifact_id = provisioning_artifact_id or ""

        pp = ProvisionedProduct(
            name=provisioned_product_name,
            product_id=resolved_product_id,
            provisioning_artifact_id=resolved_artifact_id,
            path_id=path_id,
            provisioning_parameters=provisioning_parameters,
            provisioning_preferences=provisioning_preferences,
            tags=tags,
            notification_arns=notification_arns,
            region_name=self.region_name,
            account_id=self.account_id,
        )
        pp.idempotency_token = provision_token
        self.provisioned_products[pp.id] = pp

        record = Record(
            provisioned_product_id=pp.id,
            provisioned_product_name=pp.name,
            product_id=resolved_product_id,
            provisioning_artifact_id=resolved_artifact_id,
            path_id=path_id or "",
            record_type="PROVISION_PRODUCT",
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.records[record.record_id] = record
        pp.last_record_id = record.record_id

        return pp.to_dict(), record.to_dict()

    def describe_provisioned_product(
        self,
        accept_language: Optional[str],
        provisioned_product_id: Optional[str],
        name: Optional[str],
    ) -> dict[str, Any]:
        pp = None
        if provisioned_product_id:
            pp = self.provisioned_products.get(provisioned_product_id)
        elif name:
            for p in self.provisioned_products.values():
                if p.name == name:
                    pp = p
                    break
        if not pp:
            raise ResourceNotFoundException("ProvisionedProduct not found.")
        return pp.to_dict()

    def update_provisioned_product(
        self,
        accept_language: Optional[str],
        provisioned_product_name: Optional[str],
        provisioned_product_id: Optional[str],
        product_id: Optional[str],
        product_name: Optional[str],
        provisioning_artifact_id: Optional[str],
        provisioning_artifact_name: Optional[str],
        path_id: Optional[str],
        path_name: Optional[str],
        provisioning_parameters: Optional[list[dict[str, str]]],
        provisioning_preferences: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
        update_token: Optional[str],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        pp = None
        if provisioned_product_id:
            pp = self.provisioned_products.get(provisioned_product_id)
        elif provisioned_product_name:
            for p in self.provisioned_products.values():
                if p.name == provisioned_product_name:
                    pp = p
                    break
        if not pp:
            raise ResourceNotFoundException("ProvisionedProduct not found.")

        if product_id:
            pp.product_id = product_id
        if provisioning_artifact_id:
            pp.provisioning_artifact_id = provisioning_artifact_id
        if path_id:
            pp.path_id = path_id
        if provisioning_parameters:
            pp.provisioning_parameters = provisioning_parameters
        if tags:
            pp.tags = tags

        record = Record(
            provisioned_product_id=pp.id,
            provisioned_product_name=pp.name,
            product_id=pp.product_id,
            provisioning_artifact_id=pp.provisioning_artifact_id,
            path_id=pp.path_id,
            record_type="UPDATE_PROVISIONED_PRODUCT",
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.records[record.record_id] = record
        pp.last_record_id = record.record_id

        return pp.to_dict(), record.to_dict()

    def update_provisioned_product_properties(
        self,
        accept_language: Optional[str],
        provisioned_product_id: str,
        provisioned_product_properties: dict[str, str],
        idempotency_token: Optional[str],
    ) -> tuple[str, str, dict[str, str]]:
        pp = self.provisioned_products.get(provisioned_product_id)
        if not pp:
            raise ResourceNotFoundException("ProvisionedProduct not found.")
        return pp.id, pp.status, provisioned_product_properties

    def terminate_provisioned_product(
        self,
        provisioned_product_name: Optional[str],
        provisioned_product_id: Optional[str],
        terminate_token: Optional[str],
        ignore_errors: Optional[bool],
        accept_language: Optional[str],
        retain_physical_resources: Optional[bool],
    ) -> dict[str, Any]:
        pp = None
        if provisioned_product_id:
            pp = self.provisioned_products.get(provisioned_product_id)
        elif provisioned_product_name:
            for p in self.provisioned_products.values():
                if p.name == provisioned_product_name:
                    pp = p
                    break
        if not pp:
            raise ResourceNotFoundException("ProvisionedProduct not found.")

        record = Record(
            provisioned_product_id=pp.id,
            provisioned_product_name=pp.name,
            product_id=pp.product_id,
            provisioning_artifact_id=pp.provisioning_artifact_id,
            path_id=pp.path_id,
            record_type="TERMINATE_PROVISIONED_PRODUCT",
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.records[record.record_id] = record
        del self.provisioned_products[pp.id]
        return record.to_dict()

    def scan_provisioned_products(
        self,
        accept_language: Optional[str],
        access_level_filter: Optional[dict[str, str]],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        details = [pp.to_dict() for pp in self.provisioned_products.values()]
        return details, None

    def search_provisioned_products(
        self,
        accept_language: Optional[str],
        access_level_filter: Optional[dict[str, str]],
        filters: Optional[dict[str, list[str]]],
        sort_by: Optional[str],
        sort_order: Optional[str],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], int, Optional[str]]:
        results = []
        for pp in self.provisioned_products.values():
            if filters:
                match = True
                for fk, fv in filters.items():
                    if fk == "SearchQuery":
                        text_match = any(
                            v.lower() in pp.name.lower() for v in fv
                        )
                        if not text_match:
                            match = False
                if not match:
                    continue
            results.append(pp.to_dict())
        return results, len(results), None

    def get_provisioned_product_outputs(
        self,
        accept_language: Optional[str],
        provisioned_product_id: Optional[str],
        provisioned_product_name: Optional[str],
        output_keys: Optional[list[str]],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, str]], Optional[str]]:
        pp = None
        if provisioned_product_id:
            pp = self.provisioned_products.get(provisioned_product_id)
        elif provisioned_product_name:
            for p in self.provisioned_products.values():
                if p.name == provisioned_product_name:
                    pp = p
                    break
        if not pp:
            raise ResourceNotFoundException("ProvisionedProduct not found.")
        outputs = pp.outputs
        if output_keys:
            outputs = [o for o in outputs if o.get("OutputKey") in output_keys]
        return outputs, None

    def import_as_provisioned_product(
        self,
        accept_language: Optional[str],
        product_id: str,
        provisioning_artifact_id: str,
        provisioned_product_name: str,
        physical_id: str,
        idempotency_token: Optional[str],
    ) -> dict[str, Any]:
        pp = ProvisionedProduct(
            name=provisioned_product_name,
            product_id=product_id,
            provisioning_artifact_id=provisioning_artifact_id,
            path_id=None,
            provisioning_parameters=None,
            provisioning_preferences=None,
            tags=None,
            notification_arns=None,
            region_name=self.region_name,
            account_id=self.account_id,
        )
        pp.idempotency_token = idempotency_token
        self.provisioned_products[pp.id] = pp

        record = Record(
            provisioned_product_id=pp.id,
            provisioned_product_name=pp.name,
            product_id=product_id,
            provisioning_artifact_id=provisioning_artifact_id,
            path_id="",
            record_type="IMPORT_PROVISIONED_PRODUCT",
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.records[record.record_id] = record
        return record.to_dict()

    def execute_provisioned_product_service_action(
        self,
        provisioned_product_id: str,
        service_action_id: str,
        execute_token: Optional[str],
        accept_language: Optional[str],
        parameters: Optional[dict[str, list[str]]],
    ) -> dict[str, Any]:
        pp = self.provisioned_products.get(provisioned_product_id)
        if not pp:
            raise ResourceNotFoundException("ProvisionedProduct not found.")
        if service_action_id not in self.service_actions:
            raise ResourceNotFoundException(
                f"ServiceAction {service_action_id} not found."
            )
        record = Record(
            provisioned_product_id=pp.id,
            provisioned_product_name=pp.name,
            product_id=pp.product_id,
            provisioning_artifact_id=pp.provisioning_artifact_id,
            path_id=pp.path_id,
            record_type="EXECUTE_PROVISIONED_PRODUCT_SERVICE_ACTION",
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.records[record.record_id] = record
        return record.to_dict()

    # ---- ProvisionedProductPlan operations ----

    def create_provisioned_product_plan(
        self,
        accept_language: Optional[str],
        plan_name: str,
        plan_type: str,
        notification_arns: Optional[list[str]],
        path_id: Optional[str],
        product_id: str,
        provisioned_product_name: str,
        provisioning_artifact_id: str,
        provisioning_parameters: Optional[list[dict[str, str]]],
        idempotency_token: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> tuple[str, str, str, str]:
        plan = ProvisionedProductPlan(
            plan_name=plan_name,
            plan_type=plan_type,
            product_id=product_id,
            provisioned_product_name=provisioned_product_name,
            provisioning_artifact_id=provisioning_artifact_id,
            path_id=path_id,
            provisioning_parameters=provisioning_parameters,
            tags=tags,
            notification_arns=notification_arns,
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.provisioned_product_plans[plan.plan_id] = plan
        return plan.plan_id, plan.plan_name, plan.provision_product_id, plan.provisioning_artifact_id

    def describe_provisioned_product_plan(
        self,
        accept_language: Optional[str],
        plan_id: str,
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[dict[str, Any], Optional[str], list[dict[str, Any]]]:
        plan = self.provisioned_product_plans.get(plan_id)
        if not plan:
            raise ResourceNotFoundException(f"Plan {plan_id} not found.")
        return plan.to_detail(), None, []

    def delete_provisioned_product_plan(
        self,
        accept_language: Optional[str],
        plan_id: str,
        ignore_errors: Optional[bool],
    ) -> None:
        if plan_id not in self.provisioned_product_plans:
            raise ResourceNotFoundException(f"Plan {plan_id} not found.")
        del self.provisioned_product_plans[plan_id]

    def execute_provisioned_product_plan(
        self,
        accept_language: Optional[str],
        plan_id: str,
        idempotency_token: Optional[str],
    ) -> dict[str, Any]:
        plan = self.provisioned_product_plans.get(plan_id)
        if not plan:
            raise ResourceNotFoundException(f"Plan {plan_id} not found.")
        record = Record(
            provisioned_product_id=plan.provision_product_id,
            provisioned_product_name=plan.provisioned_product_name,
            product_id=plan.product_id,
            provisioning_artifact_id=plan.provisioning_artifact_id,
            path_id=plan.path_id,
            record_type="PROVISION_PRODUCT",
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.records[record.record_id] = record
        return record.to_dict()

    def list_provisioned_product_plans(
        self,
        accept_language: Optional[str],
        provision_product_id: Optional[str],
        page_size: Optional[int],
        page_token: Optional[str],
        access_level_filter: Optional[dict[str, str]],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        summaries = []
        for plan in self.provisioned_product_plans.values():
            if provision_product_id and plan.provision_product_id != provision_product_id:
                continue
            summaries.append(plan.to_summary())
        return summaries, None

    # ---- Record operations ----

    def describe_record(
        self,
        accept_language: Optional[str],
        record_id: str,
        page_token: Optional[str],
        page_size: Optional[int],
    ) -> tuple[dict[str, Any], Optional[str], list[dict[str, str]]]:
        record = self.records.get(record_id)
        if not record:
            raise ResourceNotFoundException(f"Record {record_id} not found.")
        return record.to_dict(), None, record.record_outputs

    def list_record_history(
        self,
        accept_language: Optional[str],
        access_level_filter: Optional[dict[str, str]],
        search_filter: Optional[dict[str, str]],
        sort_by: Optional[str],
        sort_order: Optional[str],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        details = [r.to_dict() for r in self.records.values()]
        return details, None

    # ---- Launch Path operations ----

    def list_launch_paths(
        self,
        accept_language: Optional[str],
        product_id: str,
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        launch_path_summaries: list[dict[str, Any]] = []
        portfolio_ids = [
            a[1]
            for a in self.product_portfolio_associations
            if a[0] == product_id
        ]
        for pid in portfolio_ids:
            if pid in self.portfolios:
                portfolio = self.portfolios[pid]
                launch_path_summaries.append(
                    {
                        "Id": f"lp-{pid}",
                        "ConstraintSummaries": [],
                        "Tags": [],
                        "Name": portfolio.display_name,
                    }
                )
        return launch_path_summaries, None

    # ---- Stack instances ----

    def list_stack_instances_for_provisioned_product(
        self,
        accept_language: Optional[str],
        provisioned_product_id: str,
        page_token: Optional[str],
        page_size: Optional[int],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        return [], None

    # ---- AWS Organizations Access ----

    def enable_aws_organizations_access(self) -> None:
        self.aws_organizations_access_enabled = True

    def disable_aws_organizations_access(self) -> None:
        self.aws_organizations_access_enabled = False

    def get_aws_organizations_access_status(self) -> str:
        return "ENABLED" if self.aws_organizations_access_enabled else "DISABLED"

    # ---- Notify engine workflow results ----

    def notify_provision_product_engine_workflow_result(
        self,
        workflow_token: str,
        record_id: str,
        status: str,
        failure_reason: Optional[str],
        resource_identifier: Optional[dict[str, str]],
        outputs: Optional[list[dict[str, str]]],
        idempotency_token: Optional[str],
    ) -> None:
        record = self.records.get(record_id)
        if record:
            record.status = status
            record.updated_time = utcnow()
            if outputs:
                record.record_outputs = outputs
            if failure_reason:
                record.record_errors = [{"Code": "FAILED", "Description": failure_reason}]

    def notify_terminate_provisioned_product_engine_workflow_result(
        self,
        workflow_token: str,
        record_id: str,
        status: str,
        failure_reason: Optional[str],
        idempotency_token: Optional[str],
    ) -> None:
        record = self.records.get(record_id)
        if record:
            record.status = status
            record.updated_time = utcnow()
            if failure_reason:
                record.record_errors = [{"Code": "FAILED", "Description": failure_reason}]

    def notify_update_provisioned_product_engine_workflow_result(
        self,
        workflow_token: str,
        record_id: str,
        status: str,
        failure_reason: Optional[str],
        outputs: Optional[list[dict[str, str]]],
        idempotency_token: Optional[str],
    ) -> None:
        record = self.records.get(record_id)
        if record:
            record.status = status
            record.updated_time = utcnow()
            if outputs:
                record.record_outputs = outputs
            if failure_reason:
                record.record_errors = [{"Code": "FAILED", "Description": failure_reason}]


servicecatalog_backends = BackendDict(ServiceCatalogBackend, "servicecatalog")
