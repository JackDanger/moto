import base64
import json
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    ApiAssociationNotFound,
    BadRequestException,
    DataSourceNotFound,
    DomainNameNotFound,
    EventsAPINotFound,
    FunctionNotFound,
    GraphqlAPICacheNotFound,
    GraphqlAPINotFound,
    GraphQLSchemaException,
    ResolverNotFound,
    TypeNotFound,
)

# AWS custom scalars and directives
# https://github.com/dotansimha/graphql-code-generator/discussions/4311#discussioncomment-2921796
AWS_CUSTOM_GRAPHQL = """scalar AWSTime
scalar AWSDateTime
scalar AWSTimestamp
scalar AWSEmail
scalar AWSJSON
scalar AWSURL
scalar AWSPhone
scalar AWSIPAddress
scalar BigInt
scalar Double

directive @aws_subscribe(mutations: [String!]!) on FIELD_DEFINITION

# Allows transformer libraries to deprecate directive arguments.
directive @deprecated(reason: String!) on INPUT_FIELD_DEFINITION | ENUM

directive @aws_auth(cognito_groups: [String!]!) on FIELD_DEFINITION
directive @aws_api_key on FIELD_DEFINITION | OBJECT
directive @aws_iam on FIELD_DEFINITION | OBJECT
directive @aws_oidc on FIELD_DEFINITION | OBJECT
directive @aws_cognito_user_pools(
  cognito_groups: [String!]
) on FIELD_DEFINITION | OBJECT
"""


# region: APICache
class APICache(BaseModel):
    def __init__(
        self,
        ttl: int,
        api_caching_behavior: str,
        type_: str,
        transit_encryption_enabled: Optional[bool] = None,
        at_rest_encryption_enabled: Optional[bool] = None,
        health_metrics_config: Optional[str] = None,
    ):
        self.ttl = ttl
        self.api_caching_behavior = api_caching_behavior
        self.type = type_
        self.transit_encryption_enabled = transit_encryption_enabled or False
        self.at_rest_encryption_enabled = at_rest_encryption_enabled or False
        self.health_metrics_config = health_metrics_config or "DISABLED"
        self.status = "AVAILABLE"

    def update(
        self,
        ttl: int,
        api_caching_behavior: str,
        type: str,
        health_metrics_config: Optional[str] = None,
    ) -> None:
        self.ttl = ttl
        self.api_caching_behavior = api_caching_behavior
        self.type = type
        if health_metrics_config is not None:
            self.health_metrics_config = health_metrics_config

    def to_json(self) -> dict[str, Any]:
        return {
            "ttl": self.ttl,
            "transitEncryptionEnabled": self.transit_encryption_enabled,
            "atRestEncryptionEnabled": self.at_rest_encryption_enabled,
            "apiCachingBehavior": self.api_caching_behavior,
            "type": self.type,
            "healthMetricsConfig": self.health_metrics_config,
            "status": self.status,
        }


# endregion


# region: DataSource
class DataSource(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        api_id: str,
        name: str,
        type_: str,
        description: Optional[str] = None,
        service_role_arn: Optional[str] = None,
        dynamodb_config: Optional[dict[str, Any]] = None,
        lambda_config: Optional[dict[str, Any]] = None,
        elasticsearch_config: Optional[dict[str, Any]] = None,
        open_search_service_config: Optional[dict[str, Any]] = None,
        http_config: Optional[dict[str, Any]] = None,
        relational_database_config: Optional[dict[str, Any]] = None,
        event_bridge_config: Optional[dict[str, Any]] = None,
        metrics_config: Optional[str] = None,
    ) -> None:
        self.name = name
        self.type = type_
        self.description = description
        self.service_role_arn = service_role_arn
        self.dynamodb_config = dynamodb_config
        self.lambda_config = lambda_config
        self.elasticsearch_config = elasticsearch_config
        self.open_search_service_config = open_search_service_config
        self.http_config = http_config
        self.relational_database_config = relational_database_config
        self.event_bridge_config = event_bridge_config
        self.metrics_config = metrics_config or "DISABLED"
        self.data_source_arn = (
            f"arn:{get_partition(region)}:appsync:{region}:{account_id}"
            f":apis/{api_id}/datasources/{name}"
        )

    def update(
        self,
        type_: Optional[str] = None,
        description: Optional[str] = None,
        service_role_arn: Optional[str] = None,
        dynamodb_config: Optional[dict[str, Any]] = None,
        lambda_config: Optional[dict[str, Any]] = None,
        elasticsearch_config: Optional[dict[str, Any]] = None,
        open_search_service_config: Optional[dict[str, Any]] = None,
        http_config: Optional[dict[str, Any]] = None,
        relational_database_config: Optional[dict[str, Any]] = None,
        event_bridge_config: Optional[dict[str, Any]] = None,
        metrics_config: Optional[str] = None,
    ) -> None:
        if type_ is not None:
            self.type = type_
        if description is not None:
            self.description = description
        if service_role_arn is not None:
            self.service_role_arn = service_role_arn
        if dynamodb_config is not None:
            self.dynamodb_config = dynamodb_config
        if lambda_config is not None:
            self.lambda_config = lambda_config
        if elasticsearch_config is not None:
            self.elasticsearch_config = elasticsearch_config
        if open_search_service_config is not None:
            self.open_search_service_config = open_search_service_config
        if http_config is not None:
            self.http_config = http_config
        if relational_database_config is not None:
            self.relational_database_config = relational_database_config
        if event_bridge_config is not None:
            self.event_bridge_config = event_bridge_config
        if metrics_config is not None:
            self.metrics_config = metrics_config

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "dataSourceArn": self.data_source_arn,
            "name": self.name,
            "type": self.type,
            "metricsConfig": self.metrics_config,
        }
        if self.description is not None:
            result["description"] = self.description
        if self.service_role_arn is not None:
            result["serviceRoleArn"] = self.service_role_arn
        if self.dynamodb_config is not None:
            result["dynamodbConfig"] = self.dynamodb_config
        if self.lambda_config is not None:
            result["lambdaConfig"] = self.lambda_config
        if self.elasticsearch_config is not None:
            result["elasticsearchConfig"] = self.elasticsearch_config
        if self.open_search_service_config is not None:
            result["openSearchServiceConfig"] = self.open_search_service_config
        if self.http_config is not None:
            result["httpConfig"] = self.http_config
        if self.relational_database_config is not None:
            result["relationalDatabaseConfig"] = self.relational_database_config
        if self.event_bridge_config is not None:
            result["eventBridgeConfig"] = self.event_bridge_config
        return result


# endregion


# region: AppSyncType
class AppSyncType(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        api_id: str,
        definition: str,
        format_: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.definition = definition
        self.format = format_
        self.name = name or self._extract_name(definition)
        self.description = description
        self.arn = (
            f"arn:{get_partition(region)}:appsync:{region}:{account_id}"
            f":apis/{api_id}/types/{self.name}"
        )

    @staticmethod
    def _extract_name(definition: str) -> str:
        """Extract type name from SDL definition like 'type Foo { ... }'."""
        parts = definition.strip().split()
        if len(parts) >= 2:
            return parts[1].rstrip("{").strip()
        return "Unknown"

    def update(
        self,
        definition: Optional[str] = None,
        format_: Optional[str] = None,
    ) -> None:
        if definition is not None:
            self.definition = definition
            self.name = self._extract_name(definition)
        if format_ is not None:
            self.format = format_

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "arn": self.arn,
            "definition": self.definition,
            "format": self.format,
        }
        if self.description is not None:
            result["description"] = self.description
        return result


# endregion


# region: Resolver
class Resolver(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        api_id: str,
        type_name: str,
        field_name: str,
        data_source_name: Optional[str] = None,
        request_mapping_template: Optional[str] = None,
        response_mapping_template: Optional[str] = None,
        kind: Optional[str] = None,
        pipeline_config: Optional[dict[str, Any]] = None,
        sync_config: Optional[dict[str, Any]] = None,
        caching_config: Optional[dict[str, Any]] = None,
        max_batch_size: Optional[int] = None,
        runtime: Optional[dict[str, Any]] = None,
        code: Optional[str] = None,
        metrics_config: Optional[str] = None,
    ) -> None:
        self.type_name = type_name
        self.field_name = field_name
        self.data_source_name = data_source_name
        self.request_mapping_template = request_mapping_template
        self.response_mapping_template = response_mapping_template
        self.kind = kind or "UNIT"
        self.pipeline_config = pipeline_config
        self.sync_config = sync_config
        self.caching_config = caching_config
        self.max_batch_size = max_batch_size or 0
        self.runtime = runtime
        self.code = code
        self.metrics_config = metrics_config or "DISABLED"
        self.resolver_arn = (
            f"arn:{get_partition(region)}:appsync:{region}:{account_id}"
            f":apis/{api_id}/types/{type_name}/resolvers/{field_name}"
        )

    def update(
        self,
        data_source_name: Optional[str] = None,
        request_mapping_template: Optional[str] = None,
        response_mapping_template: Optional[str] = None,
        kind: Optional[str] = None,
        pipeline_config: Optional[dict[str, Any]] = None,
        sync_config: Optional[dict[str, Any]] = None,
        caching_config: Optional[dict[str, Any]] = None,
        max_batch_size: Optional[int] = None,
        runtime: Optional[dict[str, Any]] = None,
        code: Optional[str] = None,
        metrics_config: Optional[str] = None,
    ) -> None:
        if data_source_name is not None:
            self.data_source_name = data_source_name
        if request_mapping_template is not None:
            self.request_mapping_template = request_mapping_template
        if response_mapping_template is not None:
            self.response_mapping_template = response_mapping_template
        if kind is not None:
            self.kind = kind
        if pipeline_config is not None:
            self.pipeline_config = pipeline_config
        if sync_config is not None:
            self.sync_config = sync_config
        if caching_config is not None:
            self.caching_config = caching_config
        if max_batch_size is not None:
            self.max_batch_size = max_batch_size
        if runtime is not None:
            self.runtime = runtime
        if code is not None:
            self.code = code
        if metrics_config is not None:
            self.metrics_config = metrics_config

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "typeName": self.type_name,
            "fieldName": self.field_name,
            "resolverArn": self.resolver_arn,
            "kind": self.kind,
            "maxBatchSize": self.max_batch_size,
            "metricsConfig": self.metrics_config,
        }
        if self.data_source_name is not None:
            result["dataSourceName"] = self.data_source_name
        if self.request_mapping_template is not None:
            result["requestMappingTemplate"] = self.request_mapping_template
        if self.response_mapping_template is not None:
            result["responseMappingTemplate"] = self.response_mapping_template
        if self.pipeline_config is not None:
            result["pipelineConfig"] = self.pipeline_config
        if self.sync_config is not None:
            result["syncConfig"] = self.sync_config
        if self.caching_config is not None:
            result["cachingConfig"] = self.caching_config
        if self.runtime is not None:
            result["runtime"] = self.runtime
        if self.code is not None:
            result["code"] = self.code
        return result


# endregion


# region: Function
class AppSyncFunction(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        api_id: str,
        name: str,
        data_source_name: str,
        description: Optional[str] = None,
        request_mapping_template: Optional[str] = None,
        response_mapping_template: Optional[str] = None,
        function_version: Optional[str] = None,
        sync_config: Optional[dict[str, Any]] = None,
        max_batch_size: Optional[int] = None,
        runtime: Optional[dict[str, Any]] = None,
        code: Optional[str] = None,
    ) -> None:
        self.function_id = str(mock_random.uuid4())
        self.name = name
        self.data_source_name = data_source_name
        self.description = description
        self.request_mapping_template = request_mapping_template
        self.response_mapping_template = response_mapping_template
        self.function_version = function_version or "2018-05-29"
        self.sync_config = sync_config
        self.max_batch_size = max_batch_size or 0
        self.runtime = runtime
        self.code = code
        self.function_arn = (
            f"arn:{get_partition(region)}:appsync:{region}:{account_id}"
            f":apis/{api_id}/functions/{self.function_id}"
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        data_source_name: Optional[str] = None,
        request_mapping_template: Optional[str] = None,
        response_mapping_template: Optional[str] = None,
        function_version: Optional[str] = None,
        sync_config: Optional[dict[str, Any]] = None,
        max_batch_size: Optional[int] = None,
        runtime: Optional[dict[str, Any]] = None,
        code: Optional[str] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if data_source_name is not None:
            self.data_source_name = data_source_name
        if request_mapping_template is not None:
            self.request_mapping_template = request_mapping_template
        if response_mapping_template is not None:
            self.response_mapping_template = response_mapping_template
        if function_version is not None:
            self.function_version = function_version
        if sync_config is not None:
            self.sync_config = sync_config
        if max_batch_size is not None:
            self.max_batch_size = max_batch_size
        if runtime is not None:
            self.runtime = runtime
        if code is not None:
            self.code = code

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "functionId": self.function_id,
            "functionArn": self.function_arn,
            "name": self.name,
            "dataSourceName": self.data_source_name,
            "functionVersion": self.function_version,
            "maxBatchSize": self.max_batch_size,
        }
        if self.description is not None:
            result["description"] = self.description
        if self.request_mapping_template is not None:
            result["requestMappingTemplate"] = self.request_mapping_template
        if self.response_mapping_template is not None:
            result["responseMappingTemplate"] = self.response_mapping_template
        if self.sync_config is not None:
            result["syncConfig"] = self.sync_config
        if self.runtime is not None:
            result["runtime"] = self.runtime
        if self.code is not None:
            result["code"] = self.code
        return result


# endregion


# region: DomainName
class DomainNameConfig(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        domain_name: str,
        certificate_arn: str,
        description: Optional[str] = None,
    ) -> None:
        self.domain_name = domain_name
        self.certificate_arn = certificate_arn
        self.description = description or ""
        self.appsync_domain_name = (
            f"{str(mock_random.uuid4())[:8]}.appsync-api.{region}.amazonaws.com"
        )
        self.hosted_zone_id = f"Z{str(mock_random.uuid4())[:12].upper()}"
        self.domain_name_arn = (
            f"arn:{get_partition(region)}:appsync:{region}:{account_id}"
            f":domainnames/{domain_name}"
        )

    def update(self, description: Optional[str] = None) -> None:
        if description is not None:
            self.description = description

    def to_json(self) -> dict[str, Any]:
        return {
            "domainName": self.domain_name,
            "description": self.description,
            "certificateArn": self.certificate_arn,
            "appsyncDomainName": self.appsync_domain_name,
            "hostedZoneId": self.hosted_zone_id,
            "domainNameArn": self.domain_name_arn,
        }


# endregion


# region: ApiAssociation
class ApiAssociation(BaseModel):
    def __init__(self, domain_name: str, api_id: str) -> None:
        self.domain_name = domain_name
        self.api_id = api_id
        self.association_status = "SUCCESS"
        self.deployment_detail = ""

    def to_json(self) -> dict[str, Any]:
        return {
            "domainName": self.domain_name,
            "apiId": self.api_id,
            "associationStatus": self.association_status,
            "deploymentDetail": self.deployment_detail,
        }


# endregion


# region: GraphqlAPI
class GraphqlSchema(BaseModel):
    def __init__(self, definition: Any, region_name: str):
        self.definition = definition
        self.region_name = region_name
        # [graphql.language.ast.ObjectTypeDefinitionNode, ..]
        self.types: list[Any] = []

        self.status = "PROCESSING"
        self.parse_error: Optional[str] = None
        self._parse_graphql_definition()

    def get_type(self, name: str) -> Optional[dict[str, Any]]:  # type: ignore[return]
        for graphql_type in self.types:
            if graphql_type.name.value == name:
                return {
                    "name": name,
                    "description": graphql_type.description.value
                    if graphql_type.description
                    else None,
                    "arn": f"arn:{get_partition(self.region_name)}:appsync:graphql_type/{name}",
                    "definition": "NotYetImplemented",
                }

    def get_status(self) -> tuple[str, Optional[str]]:
        return self.status, self.parse_error

    def _parse_graphql_definition(self) -> None:
        try:
            from graphql import parse
            from graphql.error.graphql_error import GraphQLError
            from graphql.language.ast import ObjectTypeDefinitionNode

            res = parse(self.definition)
            for definition in res.definitions:
                if isinstance(definition, ObjectTypeDefinitionNode):
                    self.types.append(definition)
            self.status = "SUCCESS"
        except GraphQLError as e:
            self.status = "FAILED"
            self.parse_error = str(e)

    def get_introspection_schema(self, format_: str, include_directives: bool) -> str:
        from graphql import (
            build_client_schema,
            build_schema,
            introspection_from_schema,
            print_schema,
        )

        schema = build_schema(self.definition + AWS_CUSTOM_GRAPHQL)
        introspection_data = introspection_from_schema(schema, descriptions=False)

        if not include_directives:
            introspection_data["__schema"]["directives"] = []

        if format_ == "SDL":
            return print_schema(build_client_schema(introspection_data))
        elif format_ == "JSON":
            return json.dumps(introspection_data)
        else:
            raise BadRequestException(message=f"Invalid format {format_} given")


class GraphqlAPIKey(BaseModel):
    def __init__(self, description: str, expires: Optional[int]):
        self.key_id = str(mock_random.uuid4())[0:6]
        self.description = description
        if not expires:
            default_expiry = datetime.now(timezone.utc)
            default_expiry = default_expiry.replace(
                minute=0, second=0, microsecond=0, tzinfo=None
            )
            default_expiry = default_expiry + timedelta(days=7)
            self.expires = unix_time(default_expiry)
        else:
            self.expires = expires

    def update(self, description: Optional[str], expires: Optional[int]) -> None:
        if description:
            self.description = description
        if expires:
            self.expires = expires

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.key_id,
            "description": self.description,
            "expires": self.expires,
            "deletes": self.expires,
        }


class GraphqlAPI(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        authentication_type: str,
        additional_authentication_providers: Optional[list[str]],
        log_config: str,
        xray_enabled: str,
        user_pool_config: str,
        open_id_connect_config: str,
        lambda_authorizer_config: str,
        visibility: str,
        backend: "AppSyncBackend",
    ) -> None:
        self.region = region
        self.name = name
        self.api_id = str(mock_random.uuid4())
        self.authentication_type = authentication_type
        self.additional_authentication_providers = additional_authentication_providers
        self.lambda_authorizer_config = lambda_authorizer_config
        self.log_config = log_config
        self.open_id_connect_config = open_id_connect_config
        self.user_pool_config = user_pool_config
        self.xray_enabled = xray_enabled
        self.visibility = visibility or "GLOBAL"  # Default to Global if not provided

        self.arn = f"arn:{get_partition(self.region)}:appsync:{self.region}:{account_id}:apis/{self.api_id}"
        self.graphql_schema: Optional[GraphqlSchema] = None

        self.api_keys: dict[str, GraphqlAPIKey] = {}
        self.data_sources: dict[str, DataSource] = {}
        self.custom_types: dict[str, AppSyncType] = {}
        # resolvers keyed by (typeName, fieldName)
        self.resolvers: dict[tuple[str, str], Resolver] = {}
        self.functions: dict[str, AppSyncFunction] = {}

        self.api_cache: Optional[APICache] = None
        self.backend = backend

    def update(
        self,
        name: str,
        additional_authentication_providers: Optional[list[str]],
        authentication_type: str,
        lambda_authorizer_config: str,
        log_config: str,
        open_id_connect_config: str,
        user_pool_config: str,
        xray_enabled: str,
    ) -> None:
        if name:
            self.name = name
        if additional_authentication_providers:
            self.additional_authentication_providers = (
                additional_authentication_providers
            )
        if authentication_type:
            self.authentication_type = authentication_type
        if lambda_authorizer_config:
            self.lambda_authorizer_config = lambda_authorizer_config
        if log_config:
            self.log_config = log_config
        if open_id_connect_config:
            self.open_id_connect_config = open_id_connect_config
        if user_pool_config:
            self.user_pool_config = user_pool_config
        if xray_enabled is not None:
            self.xray_enabled = xray_enabled

    def create_api_key(self, description: str, expires: Optional[int]) -> GraphqlAPIKey:
        api_key = GraphqlAPIKey(description, expires)
        self.api_keys[api_key.key_id] = api_key
        return api_key

    def list_api_keys(self) -> Iterable[GraphqlAPIKey]:
        return self.api_keys.values()

    def delete_api_key(self, api_key_id: str) -> None:
        self.api_keys.pop(api_key_id)

    def update_api_key(
        self, api_key_id: str, description: str, expires: Optional[int]
    ) -> GraphqlAPIKey:
        api_key = self.api_keys[api_key_id]
        api_key.update(description, expires)
        return api_key

    def start_schema_creation(self, definition: str) -> None:
        graphql_definition = base64.b64decode(definition).decode("utf-8")

        self.graphql_schema = GraphqlSchema(graphql_definition, region_name=self.region)

    def get_schema_status(self) -> Any:
        return self.graphql_schema.get_status()  # type: ignore[union-attr]

    def get_type(self, type_name: str, type_format: str) -> Any:
        graphql_type = self.graphql_schema.get_type(type_name)  # type: ignore[union-attr]
        graphql_type["format"] = type_format  # type: ignore[index]
        return graphql_type

    def create_api_cache(
        self,
        ttl: int,
        api_caching_behavior: str,
        type: str,
        transit_encryption_enabled: Optional[bool] = None,
        at_rest_encryption_enabled: Optional[bool] = None,
        health_metrics_config: Optional[str] = None,
    ) -> APICache:
        self.api_cache = APICache(
            ttl,
            api_caching_behavior,
            type,
            transit_encryption_enabled,
            at_rest_encryption_enabled,
            health_metrics_config,
        )
        return self.api_cache

    def update_api_cache(
        self,
        ttl: int,
        api_caching_behavior: str,
        type: str,
        health_metrics_config: Optional[str] = None,
    ) -> APICache:
        self.api_cache.update(ttl, api_caching_behavior, type, health_metrics_config)  # type: ignore[union-attr]
        return self.api_cache  # type: ignore[return-value]

    def delete_api_cache(self) -> None:
        self.api_cache = None

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "apiId": self.api_id,
            "authenticationType": self.authentication_type,
            "arn": self.arn,
            "uris": {"GRAPHQL": "http://graphql.uri"},
            "additionalAuthenticationProviders": self.additional_authentication_providers,
            "lambdaAuthorizerConfig": self.lambda_authorizer_config,
            "logConfig": self.log_config,
            "openIDConnectConfig": self.open_id_connect_config,
            "userPoolConfig": self.user_pool_config,
            "xrayEnabled": self.xray_enabled,
            "visibility": self.visibility,
            "tags": self.backend.list_tags_for_resource(self.arn),
        }


# endregion


# region: EventsAPI
class EventsAPIKey(BaseModel):
    def __init__(self, description: str, expires: Optional[int]):
        self.key_id = str(mock_random.uuid4())[0:6]
        self.description = description
        if not expires:
            default_expiry = datetime.now(timezone.utc)
            default_expiry = default_expiry.replace(
                minute=0, second=0, microsecond=0, tzinfo=None
            )
            default_expiry = default_expiry + timedelta(days=7)
            self.expires = unix_time(default_expiry)
        else:
            self.expires = expires

    def update(self, description: Optional[str], expires: Optional[int]) -> None:
        if description:
            self.description = description
        if expires:
            self.expires = expires

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.key_id,
            "description": self.description,
            "expires": self.expires,
            "deletes": self.expires,
        }


class ChannelNamespace(BaseModel):
    def __init__(
        self,
        api_id: str,
        name: str,
        subscribe_auth_modes: list[dict[str, str]],
        publish_auth_modes: list[dict[str, str]],
        code_handlers: Optional[list[dict[str, Any]]] = None,
        handler_configs: Optional[dict[str, Any]] = None,
        account_id: str = "",
        region: str = "",
        backend: Optional["AppSyncBackend"] = None,
    ) -> None:
        self.api_id = api_id
        self.name = name
        self.subscribe_auth_modes = subscribe_auth_modes
        self.publish_auth_modes = publish_auth_modes
        self.code_handlers = code_handlers or []
        self.handler_configs = handler_configs or {}

        self.channel_namespace_arn = f"arn:{get_partition(region)}:appsync:{region}:{account_id}:apis/{api_id}/channelNamespace/{name}"

        now = datetime.now(timezone.utc).isoformat()
        self.created = now
        self.last_modified = now

        self.backend = backend

    def to_json(self) -> dict[str, Any]:
        response = {
            "apiId": self.api_id,
            "name": self.name,
            "subscribeAuthModes": self.subscribe_auth_modes,
            "publishAuthModes": self.publish_auth_modes,
            "channelNamespaceArn": self.channel_namespace_arn,
            "created": self.created,
            "lastModified": self.last_modified,
            "handlerConfigs": self.handler_configs,
        }

        if self.code_handlers:
            response["codeHandlers"] = self.code_handlers

        if self.backend:
            response["tags"] = self.backend.list_tags_for_resource(
                self.channel_namespace_arn
            )

        return response


class EventsAPI(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        owner_contact: Optional[str],
        event_config: Optional[dict[str, Any]],
        backend: "AppSyncBackend",
    ) -> None:
        self.region = region
        self.name = name
        self.api_id = str(mock_random.get_random_string(length=26))
        self.owner_contact = owner_contact
        self.event_config = event_config

        self.api_arn = f"arn:{get_partition(self.region)}:appsync:{self.region}:{account_id}:apis/{self.api_id}"

        self.api_keys: dict[str, EventsAPIKey] = {}
        self.channel_namespaces: list[ChannelNamespace] = []

        dns_prefix = str(mock_random.get_random_string(length=26))
        self.dns = {
            "REALTIME": f"{dns_prefix}.appsync-realtime-api.{self.region}.amazonaws.com",
            "HTTP": f"{dns_prefix}.appsync-api.{self.region}.amazonaws.com",
        }

        self.created = datetime.now(timezone.utc).isoformat()

        self.backend = backend

    def to_json(self) -> dict[str, Any]:
        response = {
            "apiId": self.api_id,
            "name": self.name,
            "tags": self.backend.list_tags_for_resource(self.api_arn),
            "dns": self.dns,
            "apiArn": self.api_arn,
            "created": self.created,
            "eventConfig": self.event_config or {},  # Default to empty dict if None
        }

        if self.owner_contact:
            response["ownerContact"] = self.owner_contact

        return response

    def create_api_key(self, description: str, expires: Optional[int]) -> EventsAPIKey:
        api_key = EventsAPIKey(description, expires)
        self.api_keys[api_key.key_id] = api_key
        return api_key

    def list_api_keys(self) -> Iterable[EventsAPIKey]:
        return self.api_keys.values()

    def delete_api_key(self, api_key_id: str) -> None:
        self.api_keys.pop(api_key_id)

    def update_api_key(
        self, api_key_id: str, description: str, expires: Optional[int]
    ) -> EventsAPIKey:
        api_key = self.api_keys[api_key_id]
        api_key.update(description, expires)
        return api_key


# endregion


# region: AppSyncBackend
class AppSyncBackend(BaseBackend):
    """Implementation of AppSync APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.graphql_apis: dict[str, GraphqlAPI] = {}
        self.events_apis: dict[str, EventsAPI] = {}
        self.domain_names: dict[str, DomainNameConfig] = {}
        self.api_associations: dict[str, ApiAssociation] = {}
        self.tagger = TaggingService()

    def create_graphql_api(
        self,
        name: str,
        log_config: str,
        authentication_type: str,
        user_pool_config: str,
        open_id_connect_config: str,
        additional_authentication_providers: Optional[list[str]],
        xray_enabled: str,
        lambda_authorizer_config: str,
        tags: dict[str, str],
        visibility: str,
    ) -> GraphqlAPI:
        graphql_api = GraphqlAPI(
            account_id=self.account_id,
            region=self.region_name,
            name=name,
            authentication_type=authentication_type,
            additional_authentication_providers=additional_authentication_providers,
            log_config=log_config,
            xray_enabled=xray_enabled,
            user_pool_config=user_pool_config,
            open_id_connect_config=open_id_connect_config,
            lambda_authorizer_config=lambda_authorizer_config,
            visibility=visibility,
            backend=self,
        )
        self.graphql_apis[graphql_api.api_id] = graphql_api
        self.tagger.tag_resource(
            graphql_api.arn, TaggingService.convert_dict_to_tags_input(tags)
        )
        return graphql_api

    def update_graphql_api(
        self,
        api_id: str,
        name: str,
        log_config: str,
        authentication_type: str,
        user_pool_config: str,
        open_id_connect_config: str,
        additional_authentication_providers: Optional[list[str]],
        xray_enabled: str,
        lambda_authorizer_config: str,
    ) -> GraphqlAPI:
        graphql_api = self.graphql_apis[api_id]
        graphql_api.update(
            name,
            additional_authentication_providers,
            authentication_type,
            lambda_authorizer_config,
            log_config,
            open_id_connect_config,
            user_pool_config,
            xray_enabled,
        )
        return graphql_api

    def get_graphql_api(self, api_id: str) -> GraphqlAPI:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        return self.graphql_apis[api_id]

    def get_graphql_schema(self, api_id: str) -> GraphqlSchema:
        graphql_api = self.get_graphql_api(api_id)
        if not graphql_api.graphql_schema:
            # When calling get_introspetion_schema without a graphql schema
            # the response GraphQLSchemaException exception includes InvalidSyntaxError
            # in the message. This might not be the case for other methods.
            raise GraphQLSchemaException(message="InvalidSyntaxError")
        return graphql_api.graphql_schema

    def delete_graphql_api(self, api_id: str) -> None:
        self.graphql_apis.pop(api_id)

    def list_graphql_apis(self) -> Iterable[GraphqlAPI]:
        """
        Pagination or the maxResults-parameter have not yet been implemented.
        """
        return self.graphql_apis.values()

    def create_api_key(
        self, api_id: str, description: str, expires: Optional[int]
    ) -> Union[GraphqlAPIKey, EventsAPIKey]:
        if api_id in self.graphql_apis:
            return self.graphql_apis[api_id].create_api_key(description, expires)
        else:
            return self.events_apis[api_id].create_api_key(description, expires)

    def delete_api_key(self, api_id: str, api_key_id: str) -> None:
        if api_id in self.graphql_apis:
            self.graphql_apis[api_id].delete_api_key(api_key_id)
        else:
            self.events_apis[api_id].delete_api_key(api_key_id)

    def list_api_keys(
        self, api_id: str
    ) -> Iterable[Union[GraphqlAPIKey, EventsAPIKey]]:
        """
        Pagination or the maxResults-parameter have not yet been implemented.
        """
        if api_id in self.graphql_apis:
            return self.graphql_apis[api_id].list_api_keys()
        elif api_id in self.events_apis:
            return self.events_apis[api_id].list_api_keys()
        else:
            return []

    def update_api_key(
        self,
        api_id: str,
        api_key_id: str,
        description: str,
        expires: Optional[int],
    ) -> Union[GraphqlAPIKey, EventsAPIKey]:
        if api_id in self.graphql_apis:
            return self.graphql_apis[api_id].update_api_key(
                api_key_id, description, expires
            )
        else:
            return self.events_apis[api_id].update_api_key(
                api_key_id, description, expires
            )

    def start_schema_creation(self, api_id: str, definition: str) -> str:
        self.graphql_apis[api_id].start_schema_creation(definition)
        return "PROCESSING"

    def get_schema_creation_status(self, api_id: str) -> Any:
        return self.graphql_apis[api_id].get_schema_status()

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(
            resource_arn, TaggingService.convert_dict_to_tags_input(tags)
        )

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def get_type(self, api_id: str, type_name: str, type_format: str) -> Any:
        return self.graphql_apis[api_id].get_type(type_name, type_format)

    def get_api_cache(self, api_id: str) -> APICache:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        api_cache = self.graphql_apis[api_id].api_cache
        if api_cache is None:
            raise GraphqlAPICacheNotFound("get")
        return api_cache

    def delete_api_cache(self, api_id: str) -> None:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        if self.graphql_apis[api_id].api_cache is None:
            raise GraphqlAPICacheNotFound("delete")
        self.graphql_apis[api_id].delete_api_cache()
        return

    def create_api_cache(
        self,
        api_id: str,
        ttl: int,
        api_caching_behavior: str,
        type: str,
        transit_encryption_enabled: Optional[bool] = None,
        at_rest_encryption_enabled: Optional[bool] = None,
        health_metrics_config: Optional[str] = None,
    ) -> APICache:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        graphql_api = self.graphql_apis[api_id]
        if graphql_api.api_cache is not None:
            raise BadRequestException(message="The API has already enabled caching.")
        api_cache = graphql_api.create_api_cache(
            ttl,
            api_caching_behavior,
            type,
            transit_encryption_enabled,
            at_rest_encryption_enabled,
            health_metrics_config,
        )
        return api_cache

    def update_api_cache(
        self,
        api_id: str,
        ttl: int,
        api_caching_behavior: str,
        type: str,
        health_metrics_config: Optional[str] = None,
    ) -> APICache:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        graphql_api = self.graphql_apis[api_id]
        if graphql_api.api_cache is None:
            raise GraphqlAPICacheNotFound("update")
        api_cache = graphql_api.update_api_cache(
            ttl, api_caching_behavior, type, health_metrics_config
        )
        return api_cache

    def flush_api_cache(self, api_id: str) -> None:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        if self.graphql_apis[api_id].api_cache is None:
            raise GraphqlAPICacheNotFound("flush")
        return

    # region: DataSource operations
    def create_data_source(
        self,
        api_id: str,
        name: str,
        type_: str,
        description: Optional[str] = None,
        service_role_arn: Optional[str] = None,
        dynamodb_config: Optional[dict[str, Any]] = None,
        lambda_config: Optional[dict[str, Any]] = None,
        elasticsearch_config: Optional[dict[str, Any]] = None,
        open_search_service_config: Optional[dict[str, Any]] = None,
        http_config: Optional[dict[str, Any]] = None,
        relational_database_config: Optional[dict[str, Any]] = None,
        event_bridge_config: Optional[dict[str, Any]] = None,
        metrics_config: Optional[str] = None,
    ) -> DataSource:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        ds = DataSource(
            account_id=self.account_id,
            region=self.region_name,
            api_id=api_id,
            name=name,
            type_=type_,
            description=description,
            service_role_arn=service_role_arn,
            dynamodb_config=dynamodb_config,
            lambda_config=lambda_config,
            elasticsearch_config=elasticsearch_config,
            open_search_service_config=open_search_service_config,
            http_config=http_config,
            relational_database_config=relational_database_config,
            event_bridge_config=event_bridge_config,
            metrics_config=metrics_config,
        )
        self.graphql_apis[api_id].data_sources[name] = ds
        return ds

    def get_data_source(self, api_id: str, name: str) -> DataSource:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        if name not in self.graphql_apis[api_id].data_sources:
            raise DataSourceNotFound(name)
        return self.graphql_apis[api_id].data_sources[name]

    def update_data_source(
        self,
        api_id: str,
        name: str,
        type_: Optional[str] = None,
        description: Optional[str] = None,
        service_role_arn: Optional[str] = None,
        dynamodb_config: Optional[dict[str, Any]] = None,
        lambda_config: Optional[dict[str, Any]] = None,
        elasticsearch_config: Optional[dict[str, Any]] = None,
        open_search_service_config: Optional[dict[str, Any]] = None,
        http_config: Optional[dict[str, Any]] = None,
        relational_database_config: Optional[dict[str, Any]] = None,
        event_bridge_config: Optional[dict[str, Any]] = None,
        metrics_config: Optional[str] = None,
    ) -> DataSource:
        ds = self.get_data_source(api_id, name)
        ds.update(
            type_=type_,
            description=description,
            service_role_arn=service_role_arn,
            dynamodb_config=dynamodb_config,
            lambda_config=lambda_config,
            elasticsearch_config=elasticsearch_config,
            open_search_service_config=open_search_service_config,
            http_config=http_config,
            relational_database_config=relational_database_config,
            event_bridge_config=event_bridge_config,
            metrics_config=metrics_config,
        )
        return ds

    def delete_data_source(self, api_id: str, name: str) -> None:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        if name not in self.graphql_apis[api_id].data_sources:
            raise DataSourceNotFound(name)
        del self.graphql_apis[api_id].data_sources[name]

    def list_data_sources(self, api_id: str) -> Iterable[DataSource]:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        return self.graphql_apis[api_id].data_sources.values()

    # endregion

    # region: Type operations
    def create_type(
        self,
        api_id: str,
        definition: str,
        format_: str,
    ) -> AppSyncType:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        t = AppSyncType(
            account_id=self.account_id,
            region=self.region_name,
            api_id=api_id,
            definition=definition,
            format_=format_,
        )
        self.graphql_apis[api_id].custom_types[t.name] = t
        return t

    def update_type(
        self,
        api_id: str,
        type_name: str,
        definition: Optional[str] = None,
        format_: Optional[str] = None,
    ) -> AppSyncType:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        if type_name not in self.graphql_apis[api_id].custom_types:
            raise TypeNotFound(type_name)
        t = self.graphql_apis[api_id].custom_types[type_name]
        t.update(definition=definition, format_=format_)
        # If the name changed due to definition update, re-key
        if t.name != type_name:
            del self.graphql_apis[api_id].custom_types[type_name]
            self.graphql_apis[api_id].custom_types[t.name] = t
        return t

    def delete_type(self, api_id: str, type_name: str) -> None:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        if type_name not in self.graphql_apis[api_id].custom_types:
            raise TypeNotFound(type_name)
        del self.graphql_apis[api_id].custom_types[type_name]

    def list_types(self, api_id: str, format_: str) -> Iterable[AppSyncType]:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        return self.graphql_apis[api_id].custom_types.values()

    # endregion

    # region: Resolver operations
    def create_resolver(
        self,
        api_id: str,
        type_name: str,
        field_name: str,
        data_source_name: Optional[str] = None,
        request_mapping_template: Optional[str] = None,
        response_mapping_template: Optional[str] = None,
        kind: Optional[str] = None,
        pipeline_config: Optional[dict[str, Any]] = None,
        sync_config: Optional[dict[str, Any]] = None,
        caching_config: Optional[dict[str, Any]] = None,
        max_batch_size: Optional[int] = None,
        runtime: Optional[dict[str, Any]] = None,
        code: Optional[str] = None,
        metrics_config: Optional[str] = None,
    ) -> Resolver:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        resolver = Resolver(
            account_id=self.account_id,
            region=self.region_name,
            api_id=api_id,
            type_name=type_name,
            field_name=field_name,
            data_source_name=data_source_name,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
            kind=kind,
            pipeline_config=pipeline_config,
            sync_config=sync_config,
            caching_config=caching_config,
            max_batch_size=max_batch_size,
            runtime=runtime,
            code=code,
            metrics_config=metrics_config,
        )
        self.graphql_apis[api_id].resolvers[(type_name, field_name)] = resolver
        return resolver

    def get_resolver(
        self, api_id: str, type_name: str, field_name: str
    ) -> Resolver:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        key = (type_name, field_name)
        if key not in self.graphql_apis[api_id].resolvers:
            raise ResolverNotFound(type_name, field_name)
        return self.graphql_apis[api_id].resolvers[key]

    def update_resolver(
        self,
        api_id: str,
        type_name: str,
        field_name: str,
        data_source_name: Optional[str] = None,
        request_mapping_template: Optional[str] = None,
        response_mapping_template: Optional[str] = None,
        kind: Optional[str] = None,
        pipeline_config: Optional[dict[str, Any]] = None,
        sync_config: Optional[dict[str, Any]] = None,
        caching_config: Optional[dict[str, Any]] = None,
        max_batch_size: Optional[int] = None,
        runtime: Optional[dict[str, Any]] = None,
        code: Optional[str] = None,
        metrics_config: Optional[str] = None,
    ) -> Resolver:
        resolver = self.get_resolver(api_id, type_name, field_name)
        resolver.update(
            data_source_name=data_source_name,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
            kind=kind,
            pipeline_config=pipeline_config,
            sync_config=sync_config,
            caching_config=caching_config,
            max_batch_size=max_batch_size,
            runtime=runtime,
            code=code,
            metrics_config=metrics_config,
        )
        return resolver

    def delete_resolver(
        self, api_id: str, type_name: str, field_name: str
    ) -> None:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        key = (type_name, field_name)
        if key not in self.graphql_apis[api_id].resolvers:
            raise ResolverNotFound(type_name, field_name)
        del self.graphql_apis[api_id].resolvers[key]

    def list_resolvers(
        self, api_id: str, type_name: str
    ) -> Iterable[Resolver]:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        return [
            r
            for (tn, _), r in self.graphql_apis[api_id].resolvers.items()
            if tn == type_name
        ]

    # endregion

    # region: Function operations
    def create_function(
        self,
        api_id: str,
        name: str,
        data_source_name: str,
        description: Optional[str] = None,
        request_mapping_template: Optional[str] = None,
        response_mapping_template: Optional[str] = None,
        function_version: Optional[str] = None,
        sync_config: Optional[dict[str, Any]] = None,
        max_batch_size: Optional[int] = None,
        runtime: Optional[dict[str, Any]] = None,
        code: Optional[str] = None,
    ) -> AppSyncFunction:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        fn = AppSyncFunction(
            account_id=self.account_id,
            region=self.region_name,
            api_id=api_id,
            name=name,
            data_source_name=data_source_name,
            description=description,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
            function_version=function_version,
            sync_config=sync_config,
            max_batch_size=max_batch_size,
            runtime=runtime,
            code=code,
        )
        self.graphql_apis[api_id].functions[fn.function_id] = fn
        return fn

    def get_function(self, api_id: str, function_id: str) -> AppSyncFunction:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        if function_id not in self.graphql_apis[api_id].functions:
            raise FunctionNotFound(function_id)
        return self.graphql_apis[api_id].functions[function_id]

    def update_function(
        self,
        api_id: str,
        function_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        data_source_name: Optional[str] = None,
        request_mapping_template: Optional[str] = None,
        response_mapping_template: Optional[str] = None,
        function_version: Optional[str] = None,
        sync_config: Optional[dict[str, Any]] = None,
        max_batch_size: Optional[int] = None,
        runtime: Optional[dict[str, Any]] = None,
        code: Optional[str] = None,
    ) -> AppSyncFunction:
        fn = self.get_function(api_id, function_id)
        fn.update(
            name=name,
            description=description,
            data_source_name=data_source_name,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
            function_version=function_version,
            sync_config=sync_config,
            max_batch_size=max_batch_size,
            runtime=runtime,
            code=code,
        )
        return fn

    def delete_function(self, api_id: str, function_id: str) -> None:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        if function_id not in self.graphql_apis[api_id].functions:
            raise FunctionNotFound(function_id)
        del self.graphql_apis[api_id].functions[function_id]

    def list_functions(self, api_id: str) -> Iterable[AppSyncFunction]:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        return self.graphql_apis[api_id].functions.values()

    # endregion

    # region: DomainName operations
    def create_domain_name(
        self,
        domain_name: str,
        certificate_arn: str,
        description: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> DomainNameConfig:
        dn = DomainNameConfig(
            account_id=self.account_id,
            region=self.region_name,
            domain_name=domain_name,
            certificate_arn=certificate_arn,
            description=description,
        )
        self.domain_names[domain_name] = dn
        if tags:
            self.tagger.tag_resource(
                dn.domain_name_arn,
                TaggingService.convert_dict_to_tags_input(tags),
            )
        return dn

    def get_domain_name(self, domain_name: str) -> DomainNameConfig:
        if domain_name not in self.domain_names:
            raise DomainNameNotFound(domain_name)
        return self.domain_names[domain_name]

    def update_domain_name(
        self, domain_name: str, description: Optional[str] = None
    ) -> DomainNameConfig:
        dn = self.get_domain_name(domain_name)
        dn.update(description=description)
        return dn

    def delete_domain_name(self, domain_name: str) -> None:
        if domain_name not in self.domain_names:
            raise DomainNameNotFound(domain_name)
        del self.domain_names[domain_name]
        # Also remove any association
        self.api_associations.pop(domain_name, None)

    def list_domain_names(self) -> Iterable[DomainNameConfig]:
        return self.domain_names.values()

    # endregion

    # region: ApiAssociation operations
    def associate_api(self, domain_name: str, api_id: str) -> ApiAssociation:
        if domain_name not in self.domain_names:
            raise DomainNameNotFound(domain_name)
        assoc = ApiAssociation(domain_name=domain_name, api_id=api_id)
        self.api_associations[domain_name] = assoc
        return assoc

    def disassociate_api(self, domain_name: str) -> None:
        if domain_name not in self.domain_names:
            raise DomainNameNotFound(domain_name)
        if domain_name not in self.api_associations:
            raise ApiAssociationNotFound(domain_name)
        del self.api_associations[domain_name]

    def get_api_association(self, domain_name: str) -> ApiAssociation:
        if domain_name not in self.domain_names:
            raise DomainNameNotFound(domain_name)
        if domain_name not in self.api_associations:
            raise ApiAssociationNotFound(domain_name)
        return self.api_associations[domain_name]

    # endregion

    def create_api(
        self,
        name: str,
        owner_contact: Optional[str],
        tags: Optional[dict[str, str]],
        event_config: Optional[dict[str, Any]],
    ) -> EventsAPI:
        events_api = EventsAPI(
            account_id=self.account_id,
            region=self.region_name,
            name=name,
            owner_contact=owner_contact,
            event_config=event_config,
            backend=self,
        )

        self.events_apis[events_api.api_id] = events_api

        self.tagger.tag_resource(
            events_api.api_arn, TaggingService.convert_dict_to_tags_input(tags)
        )

        return events_api

    def list_apis(self) -> Iterable[EventsAPI]:
        """
        Pagination or the maxResults-parameter have not yet been implemented.
        """
        return self.events_apis.values()

    def delete_api(self, api_id: str) -> None:
        self.events_apis.pop(api_id)

    def create_channel_namespace(
        self,
        api_id: str,
        name: str,
        subscribe_auth_modes: list[dict[str, str]],
        publish_auth_modes: list[dict[str, str]],
        code_handlers: Optional[list[dict[str, Any]]] = None,
        tags: Optional[dict[str, str]] = None,
        handler_configs: Optional[dict[str, Any]] = None,
    ) -> ChannelNamespace:
        # Check if API exists
        if api_id not in self.events_apis:
            raise EventsAPINotFound(api_id)

        channel_namespace = ChannelNamespace(
            api_id=api_id,
            name=name,
            subscribe_auth_modes=subscribe_auth_modes,
            publish_auth_modes=publish_auth_modes,
            code_handlers=code_handlers,
            handler_configs=handler_configs,
            account_id=self.account_id,
            region=self.region_name,
            backend=self,
        )

        for api in self.events_apis.values():
            if api.api_id == api_id:
                api.channel_namespaces.append(channel_namespace)

        if tags:
            self.tagger.tag_resource(
                channel_namespace.channel_namespace_arn,
                TaggingService.convert_dict_to_tags_input(tags),
            )

        return channel_namespace

    def list_channel_namespaces(self, api_id: str) -> Iterable[ChannelNamespace]:
        if api_id not in self.events_apis:
            raise EventsAPINotFound(api_id)
        return self.events_apis[api_id].channel_namespaces

    def delete_channel_namespace(self, api_id: str, name: str) -> None:
        if api_id not in self.events_apis:
            raise EventsAPINotFound(api_id)
        for channel_namespace in self.events_apis[api_id].channel_namespaces:
            if channel_namespace.name == name:
                self.events_apis[api_id].channel_namespaces.remove(channel_namespace)
                return

    def get_api(self, api_id: str) -> EventsAPI:
        if api_id not in self.events_apis:
            raise EventsAPINotFound(api_id)
        return self.events_apis[api_id]

    def update_api(
        self,
        api_id: str,
        name: Optional[str] = None,
        owner_contact: Optional[str] = None,
        event_config: Optional[dict[str, Any]] = None,
    ) -> EventsAPI:
        if api_id not in self.events_apis:
            raise EventsAPINotFound(api_id)
        api = self.events_apis[api_id]
        if name is not None:
            api.name = name
        if owner_contact is not None:
            api.owner_contact = owner_contact
        if event_config is not None:
            api.event_config = event_config
        return api

    def get_channel_namespace(self, api_id: str, name: str) -> ChannelNamespace:
        if api_id not in self.events_apis:
            raise EventsAPINotFound(api_id)
        for ns in self.events_apis[api_id].channel_namespaces:
            if ns.name == name:
                return ns
        raise BadRequestException(f"Channel namespace {name} not found for API {api_id}")

    def update_channel_namespace(
        self,
        api_id: str,
        name: str,
        subscribe_auth_modes: Optional[list[dict[str, str]]] = None,
        publish_auth_modes: Optional[list[dict[str, str]]] = None,
        code_handlers: Optional[list[dict[str, Any]]] = None,
        handler_configs: Optional[dict[str, Any]] = None,
    ) -> ChannelNamespace:
        ns = self.get_channel_namespace(api_id, name)
        if subscribe_auth_modes is not None:
            ns.subscribe_auth_modes = subscribe_auth_modes
        if publish_auth_modes is not None:
            ns.publish_auth_modes = publish_auth_modes
        if code_handlers is not None:
            ns.code_handlers = code_handlers
        if handler_configs is not None:
            ns.handler_configs = handler_configs
        ns.last_modified = datetime.now(timezone.utc).isoformat()
        return ns

    # region: Merged/Source GraphQL API stubs
    def associate_merged_graphql_api(
        self, source_api_identifier: str, merged_api_identifier: str
    ) -> dict[str, Any]:
        assoc_id = str(mock_random.uuid4())
        return {
            "sourceApiAssociation": {
                "associationId": assoc_id,
                "sourceApiId": source_api_identifier,
                "mergedApiId": merged_api_identifier,
                "sourceApiAssociationConfig": {},
                "sourceApiAssociationStatus": "MERGE_SUCCESS",
            }
        }

    def disassociate_merged_graphql_api(
        self, source_api_identifier: str, association_id: str
    ) -> dict[str, Any]:
        return {
            "sourceApiAssociationStatus": "DELETION_IN_PROGRESS",
        }

    def associate_source_graphql_api(
        self, merged_api_identifier: str, source_api_identifier: str
    ) -> dict[str, Any]:
        assoc_id = str(mock_random.uuid4())
        return {
            "sourceApiAssociation": {
                "associationId": assoc_id,
                "sourceApiId": source_api_identifier,
                "mergedApiId": merged_api_identifier,
                "sourceApiAssociationConfig": {},
                "sourceApiAssociationStatus": "MERGE_SUCCESS",
            }
        }

    def disassociate_source_graphql_api(
        self, merged_api_identifier: str, association_id: str
    ) -> dict[str, Any]:
        return {
            "sourceApiAssociationStatus": "DELETION_IN_PROGRESS",
        }

    def get_source_api_association(
        self, merged_api_identifier: str, association_id: str
    ) -> dict[str, Any]:
        return {
            "sourceApiAssociation": {
                "associationId": association_id,
                "mergedApiId": merged_api_identifier,
                "sourceApiAssociationConfig": {},
                "sourceApiAssociationStatus": "MERGE_SUCCESS",
            }
        }

    def update_source_api_association(
        self, merged_api_identifier: str, association_id: str, **kwargs: Any
    ) -> dict[str, Any]:
        return {
            "sourceApiAssociation": {
                "associationId": association_id,
                "mergedApiId": merged_api_identifier,
                "sourceApiAssociationConfig": {},
                "sourceApiAssociationStatus": "MERGE_SUCCESS",
            }
        }

    def list_source_api_associations(
        self, api_id: str
    ) -> list[dict[str, Any]]:
        return []

    def start_schema_merge(
        self, association_id: str, merged_api_identifier: str
    ) -> dict[str, Any]:
        return {"sourceApiAssociationStatus": "MERGE_IN_PROGRESS"}

    # endregion

    # region: Resolver by function
    def list_resolvers_by_function(
        self, api_id: str, function_id: str
    ) -> list[dict[str, Any]]:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        api = self.graphql_apis[api_id]
        result = []
        for resolver in api.resolvers.values():
            pipeline_config = resolver.pipeline_config or {}
            functions = pipeline_config.get("functions", [])
            if function_id in functions:
                result.append(resolver.to_json())
        return result

    # endregion

    # region: Environment variables
    def get_graphql_api_environment_variables(
        self, api_id: str
    ) -> dict[str, str]:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        api = self.graphql_apis[api_id]
        if not hasattr(api, "environment_variables"):
            api.environment_variables: dict[str, str] = {}
        return api.environment_variables

    def put_graphql_api_environment_variables(
        self, api_id: str, environment_variables: dict[str, str]
    ) -> dict[str, str]:
        if api_id not in self.graphql_apis:
            raise GraphqlAPINotFound(api_id)
        api = self.graphql_apis[api_id]
        api.environment_variables = environment_variables
        return environment_variables

    # endregion

    # region: Evaluate code / mapping template stubs
    def evaluate_code(
        self, runtime: dict[str, str], code: str, context: str, function_name: str
    ) -> dict[str, Any]:
        return {
            "evaluationResult": "{}",
            "error": None,
            "logs": [],
        }

    def evaluate_mapping_template(
        self, template: str, context: str
    ) -> dict[str, Any]:
        return {
            "evaluationResult": "{}",
            "error": None,
            "logs": [],
        }

    # endregion

    # region: DataSource introspection stubs
    def start_data_source_introspection(
        self, rds_data_api_config: Optional[dict[str, Any]] = None
    ) -> str:
        introspection_id = str(mock_random.uuid4())
        return introspection_id

    def get_data_source_introspection(
        self, introspection_id: str
    ) -> dict[str, Any]:
        return {
            "introspectionId": introspection_id,
            "introspectionStatus": "SUCCESS",
            "introspectionStatusDetail": None,
            "introspectionResult": {
                "models": [],
            },
        }

    # endregion

    # region: ListTypesByAssociation stub
    def list_types_by_association(
        self, merged_api_identifier: str, association_id: str, format_: str
    ) -> list[dict[str, Any]]:
        return []

    # endregion


# endregion


appsync_backends = BackendDict(AppSyncBackend, "appsync")
