"""Handles incoming servicecatalog requests, invokes methods, returns responses."""

import json

from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .models import ServiceCatalogBackend, servicecatalog_backends


class ServiceCatalogResponse(BaseResponse):
    """Handler for ServiceCatalog requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="servicecatalog")

    @property
    def servicecatalog_backend(self) -> ServiceCatalogBackend:
        return servicecatalog_backends[self.current_account][self.region]

    # ---- Portfolio operations ----

    def list_portfolio_access(self) -> ActionResult:
        params = json.loads(self.body)
        account_id_objects, next_page_token = (
            self.servicecatalog_backend.list_portfolio_access(
                accept_language=params.get("AcceptLanguage"),
                portfolio_id=params.get("PortfolioId"),
                organization_parent_id=params.get("OrganizationParentId"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
            )
        )
        account_ids = [obj["account_id"] for obj in account_id_objects]
        return ActionResult(
            {"AccountIds": account_ids, "NextPageToken": next_page_token}
        )

    def delete_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.delete_portfolio(
            accept_language=params.get("AcceptLanguage"),
            portfolio_id=params.get("Id"),
        )
        return EmptyResult()

    def delete_portfolio_share(self) -> ActionResult:
        params = json.loads(self.body)
        portfolio_share_token = self.servicecatalog_backend.delete_portfolio_share(
            accept_language=params.get("AcceptLanguage"),
            portfolio_id=params.get("PortfolioId"),
            account_id=params.get("AccountId"),
            organization_node=params.get("OrganizationNode"),
        )
        response = {}
        if portfolio_share_token:
            response["PortfolioShareToken"] = portfolio_share_token
        return ActionResult(response)

    def create_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        portfolio_detail, tags = self.servicecatalog_backend.create_portfolio(
            accept_language=params.get("AcceptLanguage"),
            display_name=params.get("DisplayName"),
            description=params.get("Description"),
            provider_name=params.get("ProviderName"),
            tags=params.get("Tags"),
            idempotency_token=params.get("IdempotencyToken"),
        )
        return ActionResult({"PortfolioDetail": portfolio_detail, "Tags": tags})

    def create_portfolio_share(self) -> ActionResult:
        params = json.loads(self.body)
        portfolio_share_token = self.servicecatalog_backend.create_portfolio_share(
            accept_language=params.get("AcceptLanguage"),
            portfolio_id=params.get("PortfolioId"),
            account_id=params.get("AccountId"),
            organization_node=params.get("OrganizationNode"),
            share_tag_options=params.get("ShareTagOptions", False),
            share_principals=params.get("SharePrincipals", False),
        )
        response = {}
        if portfolio_share_token:
            response["PortfolioShareToken"] = portfolio_share_token
        return ActionResult(response)

    def list_portfolios(self) -> ActionResult:
        params = self._get_params()
        portfolio_details, next_page_token = (
            self.servicecatalog_backend.list_portfolios(
                accept_language=params.get("AcceptLanguage"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
            )
        )
        return ActionResult(
            {"PortfolioDetails": portfolio_details, "NextPageToken": next_page_token}
        )

    def describe_portfolio_shares(self) -> ActionResult:
        params = json.loads(self.body)
        next_page_token, portfolio_share_details = (
            self.servicecatalog_backend.describe_portfolio_shares(
                portfolio_id=params.get("PortfolioId"),
                share_type=params.get("Type"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
            )
        )
        return ActionResult(
            {
                "NextPageToken": next_page_token,
                "PortfolioShareDetails": portfolio_share_details,
            }
        )

    def describe_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        portfolio_detail, tags, tag_options, budgets = (
            self.servicecatalog_backend.describe_portfolio(
                accept_language=params.get("AcceptLanguage"),
                portfolio_id=params.get("Id"),
            )
        )
        return ActionResult(
            {
                "PortfolioDetail": portfolio_detail,
                "Tags": tags,
                "TagOptions": tag_options,
                "Budgets": budgets,
            }
        )

    def update_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        portfolio_detail, tags = self.servicecatalog_backend.update_portfolio(
            portfolio_id=params.get("Id"),
            display_name=params.get("DisplayName"),
            description=params.get("Description"),
            provider_name=params.get("ProviderName"),
            add_tags=params.get("AddTags"),
            remove_tags=params.get("RemoveTags"),
            accept_language=params.get("AcceptLanguage"),
        )
        return ActionResult({"PortfolioDetail": portfolio_detail, "Tags": tags})

    def update_portfolio_share(self) -> ActionResult:
        params = json.loads(self.body)
        portfolio_share_token, status = (
            self.servicecatalog_backend.update_portfolio_share(
                accept_language=params.get("AcceptLanguage"),
                portfolio_id=params.get("PortfolioId"),
                account_id=params.get("AccountId"),
                organization_node=params.get("OrganizationNode"),
                share_tag_options=params.get("ShareTagOptions"),
                share_principals=params.get("SharePrincipals"),
            )
        )
        response: dict = {"Status": status}
        if portfolio_share_token:
            response["PortfolioShareToken"] = portfolio_share_token
        return ActionResult(response)

    def describe_portfolio_share_status(self) -> ActionResult:
        params = json.loads(self.body)
        result = self.servicecatalog_backend.describe_portfolio_share_status(
            portfolio_share_token=params.get("PortfolioShareToken"),
        )
        return ActionResult(result)

    def accept_portfolio_share(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.accept_portfolio_share(
            accept_language=params.get("AcceptLanguage"),
            portfolio_id=params.get("PortfolioId"),
            portfolio_share_type=params.get("PortfolioShareType"),
        )
        return EmptyResult()

    def reject_portfolio_share(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.reject_portfolio_share(
            accept_language=params.get("AcceptLanguage"),
            portfolio_id=params.get("PortfolioId"),
            portfolio_share_type=params.get("PortfolioShareType"),
        )
        return EmptyResult()

    def list_accepted_portfolio_shares(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.list_accepted_portfolio_shares(
                accept_language=params.get("AcceptLanguage"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
                portfolio_share_type=params.get("PortfolioShareType"),
            )
        )
        return ActionResult(
            {"PortfolioDetails": details, "NextPageToken": next_page_token}
        )

    def list_portfolios_for_product(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.list_portfolios_for_product(
                accept_language=params.get("AcceptLanguage"),
                product_id=params.get("ProductId"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
            )
        )
        return ActionResult(
            {"PortfolioDetails": details, "NextPageToken": next_page_token}
        )

    def list_organization_portfolio_access(self) -> ActionResult:
        params = json.loads(self.body)
        org_nodes, next_page_token = (
            self.servicecatalog_backend.list_organization_portfolio_access(
                accept_language=params.get("AcceptLanguage"),
                portfolio_id=params.get("PortfolioId"),
                organization_node_type=params.get("OrganizationNodeType"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
            )
        )
        return ActionResult(
            {"OrganizationNodes": org_nodes, "NextPageToken": next_page_token}
        )

    # ---- Product operations ----

    def create_product(self) -> ActionResult:
        params = json.loads(self.body)
        response = self.servicecatalog_backend.create_product(
            name=params.get("Name"),
            owner=params.get("Owner"),
            description=params.get("Description"),
            distributor=params.get("Distributor"),
            support_description=params.get("SupportDescription"),
            support_email=params.get("SupportEmail"),
            support_url=params.get("SupportUrl"),
            product_type=params.get("ProductType"),
            tags=params.get("Tags", []),
            provisioning_artifact_parameters=params.get(
                "ProvisioningArtifactParameters"
            ),
            idempotency_token=params.get("IdempotencyToken"),
            source_connection=params.get("SourceConnection"),
            accept_language=params.get("AcceptLanguage"),
        )
        product_view = {
            "ProductViewSummary": response.to_dict(),
            "Status": "AVAILABLE",
            "ProductARN": response.arn,
            "CreatedTime": response.created_time,
            "SourceConnection": response.source_connection,
        }
        return ActionResult(
            {
                "ProductViewDetail": product_view,
                "ProvisioningArtifactDetail": {},
                "Tags": response.tags,
            }
        )

    def describe_product(self) -> ActionResult:
        params = json.loads(self.body)
        response = self.servicecatalog_backend.describe_product(
            accept_language=params.get("AcceptLanguage"),
            product_id=params.get("Id"),
            name=params.get("Name"),
        )
        return ActionResult(
            {
                "ProductViewSummary": response.to_dict(),
                "ProvisioningArtifacts": [],
                "Budgets": [],
                "LaunchPaths": [],
            }
        )

    def describe_product_as_admin(self) -> ActionResult:
        params = json.loads(self.body)
        pv_detail, artifacts, tags, budgets = (
            self.servicecatalog_backend.describe_product_as_admin(
                accept_language=params.get("AcceptLanguage"),
                product_id=params.get("Id"),
                name=params.get("Name"),
                source_portfolio_id=params.get("SourcePortfolioId"),
            )
        )
        return ActionResult(
            {
                "ProductViewDetail": pv_detail,
                "ProvisioningArtifactSummaries": artifacts,
                "Tags": tags,
                "Budgets": budgets,
            }
        )

    def describe_product_view(self) -> ActionResult:
        params = json.loads(self.body)
        pv_detail = self.servicecatalog_backend.describe_product_view(
            accept_language=params.get("AcceptLanguage"),
            product_view_id=params.get("Id"),
        )
        return ActionResult({"ProductViewSummary": pv_detail})

    def delete_product(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.delete_product(
            accept_language=params.get("AcceptLanguage"),
            product_id=params.get("Id"),
        )
        return EmptyResult()

    def update_product(self) -> ActionResult:
        params = json.loads(self.body)
        product = self.servicecatalog_backend.update_product(
            product_id=params.get("Id"),
            accept_language=params.get("AcceptLanguage"),
            name=params.get("Name"),
            owner=params.get("Owner"),
            description=params.get("Description"),
            distributor=params.get("Distributor"),
            support_description=params.get("SupportDescription"),
            support_email=params.get("SupportEmail"),
            support_url=params.get("SupportUrl"),
            add_tags=params.get("AddTags"),
            remove_tags=params.get("RemoveTags"),
            source_connection=params.get("SourceConnection"),
        )
        return ActionResult(
            {
                "ProductViewDetail": product.to_product_view_detail(),
                "Tags": product.tags,
            }
        )

    def copy_product(self) -> ActionResult:
        params = json.loads(self.body)
        copy_token = self.servicecatalog_backend.copy_product(
            accept_language=params.get("AcceptLanguage"),
            source_product_arn=params.get("SourceProductArn"),
            target_product_id=params.get("TargetProductId"),
            target_product_name=params.get("TargetProductName"),
            source_provisioning_artifact_identifiers=params.get(
                "SourceProvisioningArtifactIdentifiers"
            ),
            copy_options=params.get("CopyOptions"),
            idempotency_token=params.get("IdempotencyToken"),
        )
        return ActionResult({"CopyProductToken": copy_token})

    def describe_copy_product_status(self) -> ActionResult:
        params = json.loads(self.body)
        result = self.servicecatalog_backend.describe_copy_product_status(
            accept_language=params.get("AcceptLanguage"),
            copy_product_token=params.get("CopyProductToken"),
        )
        return ActionResult(result)

    def search_products(self) -> ActionResult:
        params = json.loads(self.body)
        summaries, aggregations, next_page_token = (
            self.servicecatalog_backend.search_products(
                accept_language=params.get("AcceptLanguage"),
                filters=params.get("Filters"),
                page_size=params.get("PageSize"),
                sort_by=params.get("SortBy"),
                sort_order=params.get("SortOrder"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {
                "ProductViewSummaries": summaries,
                "ProductViewAggregations": aggregations,
                "NextPageToken": next_page_token,
            }
        )

    def search_products_as_admin(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.search_products_as_admin(
                accept_language=params.get("AcceptLanguage"),
                portfolio_id=params.get("PortfolioId"),
                filters=params.get("Filters"),
                sort_by=params.get("SortBy"),
                sort_order=params.get("SortOrder"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
                product_source=params.get("ProductSource"),
            )
        )
        return ActionResult(
            {"ProductViewDetails": details, "NextPageToken": next_page_token}
        )

    # ---- Association operations ----

    def associate_product_with_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.associate_product_with_portfolio(
            accept_language=params.get("AcceptLanguage"),
            product_id=params.get("ProductId"),
            portfolio_id=params.get("PortfolioId"),
            source_portfolio_id=params.get("SourcePortfolioId"),
        )
        return EmptyResult()

    def disassociate_product_from_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.disassociate_product_from_portfolio(
            accept_language=params.get("AcceptLanguage"),
            product_id=params.get("ProductId"),
            portfolio_id=params.get("PortfolioId"),
        )
        return EmptyResult()

    def associate_principal_with_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.associate_principal_with_portfolio(
            accept_language=params.get("AcceptLanguage"),
            portfolio_id=params.get("PortfolioId"),
            principal_arn=params.get("PrincipalARN"),
            principal_type=params.get("PrincipalType"),
        )
        return EmptyResult()

    def disassociate_principal_from_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.disassociate_principal_from_portfolio(
            accept_language=params.get("AcceptLanguage"),
            portfolio_id=params.get("PortfolioId"),
            principal_arn=params.get("PrincipalARN"),
            principal_type=params.get("PrincipalType"),
        )
        return EmptyResult()

    def list_principals_for_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        principals, next_page_token = (
            self.servicecatalog_backend.list_principals_for_portfolio(
                accept_language=params.get("AcceptLanguage"),
                portfolio_id=params.get("PortfolioId"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {"Principals": principals, "NextPageToken": next_page_token}
        )

    def associate_budget_with_resource(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.associate_budget_with_resource(
            budget_name=params.get("BudgetName"),
            resource_id=params.get("ResourceId"),
        )
        return EmptyResult()

    def disassociate_budget_from_resource(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.disassociate_budget_from_resource(
            budget_name=params.get("BudgetName"),
            resource_id=params.get("ResourceId"),
        )
        return EmptyResult()

    def list_budgets_for_resource(self) -> ActionResult:
        params = json.loads(self.body)
        budgets, next_page_token = (
            self.servicecatalog_backend.list_budgets_for_resource(
                accept_language=params.get("AcceptLanguage"),
                resource_id=params.get("ResourceId"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {"Budgets": budgets, "NextPageToken": next_page_token}
        )

    # ---- Provisioning Artifact operations ----

    def create_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        detail, info, status = (
            self.servicecatalog_backend.create_provisioning_artifact(
                accept_language=params.get("AcceptLanguage"),
                product_id=params.get("ProductId"),
                parameters=params.get("Parameters", {}),
                idempotency_token=params.get("IdempotencyToken"),
            )
        )
        return ActionResult(
            {
                "ProvisioningArtifactDetail": detail,
                "Info": info,
                "Status": status,
            }
        )

    def describe_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        detail, info, status = (
            self.servicecatalog_backend.describe_provisioning_artifact(
                accept_language=params.get("AcceptLanguage"),
                provisioning_artifact_id=params.get("ProvisioningArtifactId"),
                product_id=params.get("ProductId"),
                provisioning_artifact_name=params.get("ProvisioningArtifactName"),
                product_name=params.get("ProductName"),
                verbose=params.get("Verbose"),
            )
        )
        return ActionResult(
            {
                "ProvisioningArtifactDetail": detail,
                "Info": info,
                "Status": status,
            }
        )

    def update_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        detail, info, status = (
            self.servicecatalog_backend.update_provisioning_artifact(
                accept_language=params.get("AcceptLanguage"),
                product_id=params.get("ProductId"),
                provisioning_artifact_id=params.get("ProvisioningArtifactId"),
                name=params.get("Name"),
                description=params.get("Description"),
                active=params.get("Active"),
                guidance=params.get("Guidance"),
            )
        )
        return ActionResult(
            {
                "ProvisioningArtifactDetail": detail,
                "Info": info,
                "Status": status,
            }
        )

    def delete_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.delete_provisioning_artifact(
            accept_language=params.get("AcceptLanguage"),
            product_id=params.get("ProductId"),
            provisioning_artifact_id=params.get("ProvisioningArtifactId"),
        )
        return EmptyResult()

    def list_provisioning_artifacts(self) -> ActionResult:
        params = json.loads(self.body)
        details = self.servicecatalog_backend.list_provisioning_artifacts(
            accept_language=params.get("AcceptLanguage"),
            product_id=params.get("ProductId"),
        )
        return ActionResult(
            {"ProvisioningArtifactDetails": details, "NextPageToken": None}
        )

    def describe_provisioning_parameters(self) -> ActionResult:
        params = json.loads(self.body)
        pa_params, constraints, usage, tag_opts = (
            self.servicecatalog_backend.describe_provisioning_parameters(
                accept_language=params.get("AcceptLanguage"),
                product_id=params.get("ProductId"),
                product_name=params.get("ProductName"),
                provisioning_artifact_id=params.get("ProvisioningArtifactId"),
                provisioning_artifact_name=params.get("ProvisioningArtifactName"),
                path_id=params.get("PathId"),
                path_name=params.get("PathName"),
            )
        )
        return ActionResult(
            {
                "ProvisioningArtifactParameters": pa_params,
                "ConstraintSummaries": constraints,
                "UsageInstructions": usage,
                "TagOptions": tag_opts,
                "ProvisioningArtifactPreferences": {},
                "ProvisioningArtifactOutputs": [],
                "ProvisioningArtifactOutputKeys": [],
            }
        )

    def list_provisioning_artifacts_for_service_action(self) -> ActionResult:
        params = json.loads(self.body)
        results, next_page_token = (
            self.servicecatalog_backend.list_provisioning_artifacts_for_service_action(
                service_action_id=params.get("ServiceActionId"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
                accept_language=params.get("AcceptLanguage"),
            )
        )
        return ActionResult(
            {
                "ProvisioningArtifactViews": results,
                "NextPageToken": next_page_token,
            }
        )

    # ---- Constraint operations ----

    def create_constraint(self) -> ActionResult:
        params = json.loads(self.body)
        detail, constraint_parameters, status = (
            self.servicecatalog_backend.create_constraint(
                accept_language=params.get("AcceptLanguage"),
                portfolio_id=params.get("PortfolioId"),
                product_id=params.get("ProductId"),
                parameters=params.get("Parameters", "{}"),
                constraint_type=params.get("Type"),
                description=params.get("Description"),
                idempotency_token=params.get("IdempotencyToken"),
            )
        )
        return ActionResult(
            {
                "ConstraintDetail": detail,
                "ConstraintParameters": constraint_parameters,
                "Status": status,
            }
        )

    def describe_constraint(self) -> ActionResult:
        params = json.loads(self.body)
        detail, constraint_parameters, status = (
            self.servicecatalog_backend.describe_constraint(
                accept_language=params.get("AcceptLanguage"),
                constraint_id=params.get("Id"),
            )
        )
        return ActionResult(
            {
                "ConstraintDetail": detail,
                "ConstraintParameters": constraint_parameters,
                "Status": status,
            }
        )

    def update_constraint(self) -> ActionResult:
        params = json.loads(self.body)
        detail, constraint_parameters, status = (
            self.servicecatalog_backend.update_constraint(
                accept_language=params.get("AcceptLanguage"),
                constraint_id=params.get("Id"),
                description=params.get("Description"),
                parameters=params.get("Parameters"),
            )
        )
        return ActionResult(
            {
                "ConstraintDetail": detail,
                "ConstraintParameters": constraint_parameters,
                "Status": status,
            }
        )

    def delete_constraint(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.delete_constraint(
            accept_language=params.get("AcceptLanguage"),
            constraint_id=params.get("Id"),
        )
        return EmptyResult()

    def list_constraints_for_portfolio(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.list_constraints_for_portfolio(
                accept_language=params.get("AcceptLanguage"),
                portfolio_id=params.get("PortfolioId"),
                product_id=params.get("ProductId"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {"ConstraintDetails": details, "NextPageToken": next_page_token}
        )

    # ---- Service Action operations ----

    def create_service_action(self) -> ActionResult:
        params = json.loads(self.body)
        detail = self.servicecatalog_backend.create_service_action(
            name=params.get("Name"),
            definition_type=params.get("DefinitionType"),
            definition=params.get("Definition", {}),
            description=params.get("Description"),
            accept_language=params.get("AcceptLanguage"),
            idempotency_token=params.get("IdempotencyToken"),
        )
        return ActionResult({"ServiceActionDetail": detail})

    def describe_service_action(self) -> ActionResult:
        params = json.loads(self.body)
        detail = self.servicecatalog_backend.describe_service_action(
            service_action_id=params.get("Id"),
            accept_language=params.get("AcceptLanguage"),
        )
        return ActionResult({"ServiceActionDetail": detail})

    def describe_service_action_execution_parameters(self) -> ActionResult:
        params = json.loads(self.body)
        execution_params = (
            self.servicecatalog_backend.describe_service_action_execution_parameters(
                provisioned_product_id=params.get("ProvisionedProductId"),
                service_action_id=params.get("ServiceActionId"),
                accept_language=params.get("AcceptLanguage"),
            )
        )
        return ActionResult(
            {"ServiceActionParameters": execution_params}
        )

    def update_service_action(self) -> ActionResult:
        params = json.loads(self.body)
        detail = self.servicecatalog_backend.update_service_action(
            service_action_id=params.get("Id"),
            name=params.get("Name"),
            definition=params.get("Definition"),
            description=params.get("Description"),
            accept_language=params.get("AcceptLanguage"),
        )
        return ActionResult({"ServiceActionDetail": detail})

    def delete_service_action(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.delete_service_action(
            service_action_id=params.get("Id"),
            accept_language=params.get("AcceptLanguage"),
        )
        return EmptyResult()

    def list_service_actions(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.list_service_actions(
                accept_language=params.get("AcceptLanguage"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {"ServiceActionSummaries": details, "NextPageToken": next_page_token}
        )

    def list_service_actions_for_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.list_service_actions_for_provisioning_artifact(
                product_id=params.get("ProductId"),
                provisioning_artifact_id=params.get("ProvisioningArtifactId"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
                accept_language=params.get("AcceptLanguage"),
            )
        )
        return ActionResult(
            {
                "ServiceActionSummaries": details,
                "NextPageToken": next_page_token,
            }
        )

    def associate_service_action_with_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.associate_service_action_with_provisioning_artifact(
            product_id=params.get("ProductId"),
            provisioning_artifact_id=params.get("ProvisioningArtifactId"),
            service_action_id=params.get("ServiceActionId"),
            accept_language=params.get("AcceptLanguage"),
        )
        return EmptyResult()

    def disassociate_service_action_from_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.disassociate_service_action_from_provisioning_artifact(
            product_id=params.get("ProductId"),
            provisioning_artifact_id=params.get("ProvisioningArtifactId"),
            service_action_id=params.get("ServiceActionId"),
            accept_language=params.get("AcceptLanguage"),
        )
        return EmptyResult()

    def batch_associate_service_action_with_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        failed = self.servicecatalog_backend.batch_associate_service_action_with_provisioning_artifact(
            service_action_associations=params.get("ServiceActionAssociations", []),
            accept_language=params.get("AcceptLanguage"),
        )
        return ActionResult({"FailedServiceActionAssociations": failed})

    def batch_disassociate_service_action_from_provisioning_artifact(self) -> ActionResult:
        params = json.loads(self.body)
        failed = self.servicecatalog_backend.batch_disassociate_service_action_from_provisioning_artifact(
            service_action_associations=params.get("ServiceActionAssociations", []),
            accept_language=params.get("AcceptLanguage"),
        )
        return ActionResult({"FailedServiceActionAssociations": failed})

    # ---- TagOption operations ----

    def create_tag_option(self) -> ActionResult:
        params = json.loads(self.body)
        detail = self.servicecatalog_backend.create_tag_option(
            key=params.get("Key"),
            value=params.get("Value"),
        )
        return ActionResult({"TagOptionDetail": detail})

    def describe_tag_option(self) -> ActionResult:
        params = json.loads(self.body)
        detail = self.servicecatalog_backend.describe_tag_option(
            tag_option_id=params.get("Id"),
        )
        return ActionResult({"TagOptionDetail": detail})

    def update_tag_option(self) -> ActionResult:
        params = json.loads(self.body)
        detail = self.servicecatalog_backend.update_tag_option(
            tag_option_id=params.get("Id"),
            value=params.get("Value"),
            active=params.get("Active"),
        )
        return ActionResult({"TagOptionDetail": detail})

    def delete_tag_option(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.delete_tag_option(
            tag_option_id=params.get("Id"),
        )
        return EmptyResult()

    def list_tag_options(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = self.servicecatalog_backend.list_tag_options(
            filters=params.get("Filters"),
            page_size=params.get("PageSize"),
            page_token=params.get("PageToken"),
        )
        return ActionResult(
            {"TagOptionDetails": details, "PageToken": next_page_token}
        )

    def associate_tag_option_with_resource(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.associate_tag_option_with_resource(
            resource_id=params.get("ResourceId"),
            tag_option_id=params.get("TagOptionId"),
        )
        return EmptyResult()

    def disassociate_tag_option_from_resource(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.disassociate_tag_option_from_resource(
            resource_id=params.get("ResourceId"),
            tag_option_id=params.get("TagOptionId"),
        )
        return EmptyResult()

    def list_resources_for_tag_option(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.list_resources_for_tag_option(
                tag_option_id=params.get("TagOptionId"),
                resource_type=params.get("ResourceType"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {"ResourceDetails": details, "PageToken": next_page_token}
        )

    # ---- Provisioned Product operations ----

    def provision_product(self) -> ActionResult:
        params = json.loads(self.body)
        pp_detail, record_detail = self.servicecatalog_backend.provision_product(
            accept_language=params.get("AcceptLanguage"),
            product_id=params.get("ProductId"),
            product_name=params.get("ProductName"),
            provisioning_artifact_id=params.get("ProvisioningArtifactId"),
            provisioning_artifact_name=params.get("ProvisioningArtifactName"),
            path_id=params.get("PathId"),
            path_name=params.get("PathName"),
            provisioned_product_name=params.get("ProvisionedProductName"),
            provisioning_parameters=params.get("ProvisioningParameters"),
            provisioning_preferences=params.get("ProvisioningPreferences"),
            tags=params.get("Tags"),
            notification_arns=params.get("NotificationArns"),
            provision_token=params.get("ProvisionToken"),
        )
        return ActionResult({"RecordDetail": record_detail})

    def describe_provisioned_product(self) -> ActionResult:
        params = json.loads(self.body)
        detail = self.servicecatalog_backend.describe_provisioned_product(
            accept_language=params.get("AcceptLanguage"),
            provisioned_product_id=params.get("Id"),
            name=params.get("Name"),
        )
        return ActionResult(
            {"ProvisionedProductDetail": detail, "CloudWatchDashboards": []}
        )

    def update_provisioned_product(self) -> ActionResult:
        params = json.loads(self.body)
        pp_detail, record_detail = (
            self.servicecatalog_backend.update_provisioned_product(
                accept_language=params.get("AcceptLanguage"),
                provisioned_product_name=params.get("ProvisionedProductName"),
                provisioned_product_id=params.get("ProvisionedProductId"),
                product_id=params.get("ProductId"),
                product_name=params.get("ProductName"),
                provisioning_artifact_id=params.get("ProvisioningArtifactId"),
                provisioning_artifact_name=params.get("ProvisioningArtifactName"),
                path_id=params.get("PathId"),
                path_name=params.get("PathName"),
                provisioning_parameters=params.get("ProvisioningParameters"),
                provisioning_preferences=params.get("ProvisioningPreferences"),
                tags=params.get("Tags"),
                update_token=params.get("UpdateToken"),
            )
        )
        return ActionResult({"RecordDetail": record_detail})

    def update_provisioned_product_properties(self) -> ActionResult:
        params = json.loads(self.body)
        pp_id, status, properties = (
            self.servicecatalog_backend.update_provisioned_product_properties(
                accept_language=params.get("AcceptLanguage"),
                provisioned_product_id=params.get("ProvisionedProductId"),
                provisioned_product_properties=params.get(
                    "ProvisionedProductProperties", {}
                ),
                idempotency_token=params.get("IdempotencyToken"),
            )
        )
        return ActionResult(
            {
                "ProvisionedProductId": pp_id,
                "ProvisionedProductProperties": properties,
                "RecordId": f"rec-{pp_id}",
                "Status": status,
            }
        )

    def terminate_provisioned_product(self) -> ActionResult:
        params = json.loads(self.body)
        record_detail = self.servicecatalog_backend.terminate_provisioned_product(
            provisioned_product_name=params.get("ProvisionedProductName"),
            provisioned_product_id=params.get("ProvisionedProductId"),
            terminate_token=params.get("TerminateToken"),
            ignore_errors=params.get("IgnoreErrors"),
            accept_language=params.get("AcceptLanguage"),
            retain_physical_resources=params.get("RetainPhysicalResources"),
        )
        return ActionResult({"RecordDetail": record_detail})

    def scan_provisioned_products(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.scan_provisioned_products(
                accept_language=params.get("AcceptLanguage"),
                access_level_filter=params.get("AccessLevelFilter"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {
                "ProvisionedProducts": details,
                "NextPageToken": next_page_token,
            }
        )

    def search_provisioned_products(self) -> ActionResult:
        params = json.loads(self.body)
        details, total_results_count, next_page_token = (
            self.servicecatalog_backend.search_provisioned_products(
                accept_language=params.get("AcceptLanguage"),
                access_level_filter=params.get("AccessLevelFilter"),
                filters=params.get("Filters"),
                sort_by=params.get("SortBy"),
                sort_order=params.get("SortOrder"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {
                "ProvisionedProducts": details,
                "TotalResultsCount": total_results_count,
                "NextPageToken": next_page_token,
            }
        )

    def get_provisioned_product_outputs(self) -> ActionResult:
        params = json.loads(self.body)
        outputs, next_page_token = (
            self.servicecatalog_backend.get_provisioned_product_outputs(
                accept_language=params.get("AcceptLanguage"),
                provisioned_product_id=params.get("ProvisionedProductId"),
                provisioned_product_name=params.get("ProvisionedProductName"),
                output_keys=params.get("OutputKeys"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {"Outputs": outputs, "NextPageToken": next_page_token}
        )

    def import_as_provisioned_product(self) -> ActionResult:
        params = json.loads(self.body)
        record_detail = self.servicecatalog_backend.import_as_provisioned_product(
            accept_language=params.get("AcceptLanguage"),
            product_id=params.get("ProductId"),
            provisioning_artifact_id=params.get("ProvisioningArtifactId"),
            provisioned_product_name=params.get("ProvisionedProductName"),
            physical_id=params.get("PhysicalId"),
            idempotency_token=params.get("IdempotencyToken"),
        )
        return ActionResult({"RecordDetail": record_detail})

    def execute_provisioned_product_service_action(self) -> ActionResult:
        params = json.loads(self.body)
        record_detail = (
            self.servicecatalog_backend.execute_provisioned_product_service_action(
                provisioned_product_id=params.get("ProvisionedProductId"),
                service_action_id=params.get("ServiceActionId"),
                execute_token=params.get("ExecuteToken"),
                accept_language=params.get("AcceptLanguage"),
                parameters=params.get("Parameters"),
            )
        )
        return ActionResult({"RecordDetail": record_detail})

    # ---- ProvisionedProductPlan operations ----

    def create_provisioned_product_plan(self) -> ActionResult:
        params = json.loads(self.body)
        plan_id, plan_name, pp_id, pa_id = (
            self.servicecatalog_backend.create_provisioned_product_plan(
                accept_language=params.get("AcceptLanguage"),
                plan_name=params.get("PlanName"),
                plan_type=params.get("PlanType"),
                notification_arns=params.get("NotificationArns"),
                path_id=params.get("PathId"),
                product_id=params.get("ProductId"),
                provisioned_product_name=params.get("ProvisionedProductName"),
                provisioning_artifact_id=params.get("ProvisioningArtifactId"),
                provisioning_parameters=params.get("ProvisioningParameters"),
                idempotency_token=params.get("IdempotencyToken"),
                tags=params.get("Tags"),
            )
        )
        return ActionResult(
            {
                "PlanName": plan_name,
                "PlanId": plan_id,
                "ProvisionProductId": pp_id,
                "ProvisioningArtifactId": pa_id,
            }
        )

    def describe_provisioned_product_plan(self) -> ActionResult:
        params = json.loads(self.body)
        detail, next_page_token, resource_changes = (
            self.servicecatalog_backend.describe_provisioned_product_plan(
                accept_language=params.get("AcceptLanguage"),
                plan_id=params.get("PlanId"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {
                "ProvisionedProductPlanDetails": detail,
                "ResourceChanges": resource_changes,
                "NextPageToken": next_page_token,
            }
        )

    def delete_provisioned_product_plan(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.delete_provisioned_product_plan(
            accept_language=params.get("AcceptLanguage"),
            plan_id=params.get("PlanId"),
            ignore_errors=params.get("IgnoreErrors"),
        )
        return EmptyResult()

    def execute_provisioned_product_plan(self) -> ActionResult:
        params = json.loads(self.body)
        record_detail = (
            self.servicecatalog_backend.execute_provisioned_product_plan(
                accept_language=params.get("AcceptLanguage"),
                plan_id=params.get("PlanId"),
                idempotency_token=params.get("IdempotencyToken"),
            )
        )
        return ActionResult({"RecordDetail": record_detail})

    def list_provisioned_product_plans(self) -> ActionResult:
        params = json.loads(self.body)
        summaries, next_page_token = (
            self.servicecatalog_backend.list_provisioned_product_plans(
                accept_language=params.get("AcceptLanguage"),
                provision_product_id=params.get("ProvisionProductId"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
                access_level_filter=params.get("AccessLevelFilter"),
            )
        )
        return ActionResult(
            {
                "ProvisionedProductPlans": summaries,
                "NextPageToken": next_page_token,
            }
        )

    # ---- Record operations ----

    def describe_record(self) -> ActionResult:
        params = json.loads(self.body)
        detail, next_page_token, outputs = (
            self.servicecatalog_backend.describe_record(
                accept_language=params.get("AcceptLanguage"),
                record_id=params.get("Id"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
            )
        )
        return ActionResult(
            {
                "RecordDetail": detail,
                "RecordOutputs": outputs,
                "NextPageToken": next_page_token,
            }
        )

    def list_record_history(self) -> ActionResult:
        params = json.loads(self.body)
        details, next_page_token = (
            self.servicecatalog_backend.list_record_history(
                accept_language=params.get("AcceptLanguage"),
                access_level_filter=params.get("AccessLevelFilter"),
                search_filter=params.get("SearchFilter"),
                sort_by=params.get("SortBy"),
                sort_order=params.get("SortOrder"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {"RecordDetails": details, "NextPageToken": next_page_token}
        )

    # ---- Launch Path operations ----

    def list_launch_paths(self) -> ActionResult:
        params = json.loads(self.body)
        summaries, next_page_token = (
            self.servicecatalog_backend.list_launch_paths(
                accept_language=params.get("AcceptLanguage"),
                product_id=params.get("ProductId"),
                page_size=params.get("PageSize"),
                page_token=params.get("PageToken"),
            )
        )
        return ActionResult(
            {
                "LaunchPathSummaries": summaries,
                "NextPageToken": next_page_token,
            }
        )

    # ---- Stack instances ----

    def list_stack_instances_for_provisioned_product(self) -> ActionResult:
        params = json.loads(self.body)
        instances, next_page_token = (
            self.servicecatalog_backend.list_stack_instances_for_provisioned_product(
                accept_language=params.get("AcceptLanguage"),
                provisioned_product_id=params.get("ProvisionedProductId"),
                page_token=params.get("PageToken"),
                page_size=params.get("PageSize"),
            )
        )
        return ActionResult(
            {
                "StackInstances": instances,
                "NextPageToken": next_page_token,
            }
        )

    # ---- AWS Organizations Access ----

    def enable_a_w_s_organizations_access(self) -> ActionResult:
        self.servicecatalog_backend.enable_aws_organizations_access()
        return EmptyResult()

    def disable_a_w_s_organizations_access(self) -> ActionResult:
        self.servicecatalog_backend.disable_aws_organizations_access()
        return EmptyResult()

    def get_a_w_s_organizations_access_status(self) -> ActionResult:
        status = self.servicecatalog_backend.get_aws_organizations_access_status()
        return ActionResult({"AccessStatus": status})

    # camelcase_to_underscores produces get_aws_organizations_access_status (not get_a_w_s_...)
    def enable_aws_organizations_access(self) -> ActionResult:
        return self.enable_a_w_s_organizations_access()

    def disable_aws_organizations_access(self) -> ActionResult:
        return self.disable_a_w_s_organizations_access()

    def get_aws_organizations_access_status(self) -> ActionResult:
        return self.get_a_w_s_organizations_access_status()

    # ---- Notify engine workflow results ----

    def notify_provision_product_engine_workflow_result(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.notify_provision_product_engine_workflow_result(
            workflow_token=params.get("WorkflowToken"),
            record_id=params.get("RecordId"),
            status=params.get("Status"),
            failure_reason=params.get("FailureReason"),
            resource_identifier=params.get("ResourceIdentifier"),
            outputs=params.get("Outputs"),
            idempotency_token=params.get("IdempotencyToken"),
        )
        return EmptyResult()

    def notify_terminate_provisioned_product_engine_workflow_result(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.notify_terminate_provisioned_product_engine_workflow_result(
            workflow_token=params.get("WorkflowToken"),
            record_id=params.get("RecordId"),
            status=params.get("Status"),
            failure_reason=params.get("FailureReason"),
            idempotency_token=params.get("IdempotencyToken"),
        )
        return EmptyResult()

    def notify_update_provisioned_product_engine_workflow_result(self) -> ActionResult:
        params = json.loads(self.body)
        self.servicecatalog_backend.notify_update_provisioned_product_engine_workflow_result(
            workflow_token=params.get("WorkflowToken"),
            record_id=params.get("RecordId"),
            status=params.get("Status"),
            failure_reason=params.get("FailureReason"),
            outputs=params.get("Outputs"),
            idempotency_token=params.get("IdempotencyToken"),
        )
        return EmptyResult()
