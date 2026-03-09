"""Handles incoming appsync requests, invokes methods, returns responses."""

import json
import re
from typing import Any
from urllib.parse import unquote
from uuid import uuid4

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse
from moto.core.utils import unix_time

from .exceptions import ApiKeyValidityOutOfBoundsException, AWSValidationException
from .models import AppSyncBackend, appsync_backends


class AppSyncResponse(BaseResponse):
    """Handler for AppSync requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="appsync")

    @staticmethod
    def dns_event_response(request: Any, url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore[misc]
        data = json.loads(request.data.decode("utf-8"))

        response: dict[str, list[Any]] = {"failed": [], "successful": []}
        for idx in range(len(data.get("events", []))):
            response["successful"].append({"identifier": str(uuid4()), "index": idx})

        return 200, {}, json.dumps(response).encode("utf-8")

    @property
    def appsync_backend(self) -> AppSyncBackend:
        """Return backend instance specific for this region."""
        return appsync_backends[self.current_account][self.region]

    def create_graphql_api(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        log_config = params.get("logConfig")
        authentication_type = params.get("authenticationType")
        user_pool_config = params.get("userPoolConfig")
        open_id_connect_config = params.get("openIDConnectConfig")
        tags = params.get("tags")
        additional_authentication_providers = params.get(
            "additionalAuthenticationProviders"
        )
        xray_enabled = params.get("xrayEnabled", False)
        lambda_authorizer_config = params.get("lambdaAuthorizerConfig")
        visibility = params.get("visibility")
        graphql_api = self.appsync_backend.create_graphql_api(
            name=name,
            log_config=log_config,
            authentication_type=authentication_type,
            user_pool_config=user_pool_config,
            open_id_connect_config=open_id_connect_config,
            additional_authentication_providers=additional_authentication_providers,
            xray_enabled=xray_enabled,
            lambda_authorizer_config=lambda_authorizer_config,
            tags=tags,
            visibility=visibility,
        )
        response = graphql_api.to_json()
        response["tags"] = self.appsync_backend.list_tags_for_resource(graphql_api.arn)
        return json.dumps({"graphqlApi": response})

    def get_graphql_api(self) -> str:
        api_id = self.path.split("/")[-1]

        graphql_api = self.appsync_backend.get_graphql_api(api_id=api_id)
        response = graphql_api.to_json()
        response["tags"] = self.appsync_backend.list_tags_for_resource(graphql_api.arn)
        return json.dumps({"graphqlApi": response})

    def delete_graphql_api(self) -> str:
        api_id = self.path.split("/")[-1]
        self.appsync_backend.delete_graphql_api(api_id=api_id)
        return "{}"

    def update_graphql_api(self) -> str:
        api_id = self.path.split("/")[-1]

        params = json.loads(self.body)
        name = params.get("name")
        log_config = params.get("logConfig")
        authentication_type = params.get("authenticationType")
        user_pool_config = params.get("userPoolConfig")
        open_id_connect_config = params.get("openIDConnectConfig")
        additional_authentication_providers = params.get(
            "additionalAuthenticationProviders"
        )
        xray_enabled = params.get("xrayEnabled", False)
        lambda_authorizer_config = params.get("lambdaAuthorizerConfig")

        api = self.appsync_backend.update_graphql_api(
            api_id=api_id,
            name=name,
            log_config=log_config,
            authentication_type=authentication_type,
            user_pool_config=user_pool_config,
            open_id_connect_config=open_id_connect_config,
            additional_authentication_providers=additional_authentication_providers,
            xray_enabled=xray_enabled,
            lambda_authorizer_config=lambda_authorizer_config,
        )
        return json.dumps({"graphqlApi": api.to_json()})

    def list_graphql_apis(self) -> str:
        graphql_apis = self.appsync_backend.list_graphql_apis()
        return json.dumps({"graphqlApis": [api.to_json() for api in graphql_apis]})

    def create_api_key(self) -> str:
        params = json.loads(self.body)
        # /v1/apis/[api_id]/apikeys
        api_id = self.path.split("/")[-2]
        description = params.get("description")
        expires = params.get("expires")

        if expires:
            current_time = int(unix_time())
            min_validity = current_time + 86400  # 1 day in seconds
            if expires < min_validity:
                raise ApiKeyValidityOutOfBoundsException(
                    "API key must be valid for a minimum of 1 days."
                )

        api_key = self.appsync_backend.create_api_key(
            api_id=api_id, description=description, expires=expires
        )
        return json.dumps({"apiKey": api_key.to_json()})

    def delete_api_key(self) -> str:
        api_id = self.path.split("/")[-3]
        api_key_id = self.path.split("/")[-1]
        self.appsync_backend.delete_api_key(api_id=api_id, api_key_id=api_key_id)
        return "{}"

    def list_api_keys(self) -> str:
        # /v1/apis/[api_id]/apikeys
        api_id = self.path.split("/")[-2]
        api_keys = self.appsync_backend.list_api_keys(api_id=api_id)
        return json.dumps({"apiKeys": [key.to_json() for key in api_keys]})

    def update_api_key(self) -> str:
        api_id = self.path.split("/")[-3]
        api_key_id = self.path.split("/")[-1]
        params = json.loads(self.body)
        description = params.get("description")
        expires = params.get("expires")

        # Validate that API key expires at least 1 day from now
        if expires:
            current_time = int(unix_time())
            min_validity = current_time + 86400  # 1 day in seconds
            if expires < min_validity:
                raise ApiKeyValidityOutOfBoundsException(
                    "API key must be valid for a minimum of 1 days."
                )

        api_key = self.appsync_backend.update_api_key(
            api_id=api_id,
            api_key_id=api_key_id,
            description=description,
            expires=expires,
        )
        return json.dumps({"apiKey": api_key.to_json()})

    def start_schema_creation(self) -> str:
        params = json.loads(self.body)
        api_id = self.path.split("/")[-2]
        definition = params.get("definition")
        status = self.appsync_backend.start_schema_creation(
            api_id=api_id, definition=definition
        )
        return json.dumps({"status": status})

    def get_schema_creation_status(self) -> str:
        api_id = self.path.split("/")[-2]
        status, details = self.appsync_backend.get_schema_creation_status(api_id=api_id)
        return json.dumps({"status": status, "details": details})

    def tag_resource(self) -> str:
        resource_arn = self._extract_arn_from_path()
        params = json.loads(self.body)
        tags = params.get("tags")
        self.appsync_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return "{}"

    def untag_resource(self) -> str:
        resource_arn = self._extract_arn_from_path()
        tag_keys = self.querystring.get("tagKeys", [])
        self.appsync_backend.untag_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )
        return "{}"

    def list_tags_for_resource(self) -> str:
        resource_arn = self._extract_arn_from_path()
        tags = self.appsync_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"tags": tags})

    def _extract_arn_from_path(self) -> str:
        # /v1/tags/arn_that_may_contain_a_slash
        path = unquote(self.path)
        return "/".join(path.split("/")[3:])

    def get_type(self) -> str:
        api_id = unquote(self.path.split("/")[-3])
        type_name = self.path.split("/")[-1]
        type_format = self.querystring.get("format")[0]  # type: ignore[index]
        graphql_type = self.appsync_backend.get_type(
            api_id=api_id, type_name=type_name, type_format=type_format
        )
        return json.dumps({"type": graphql_type})

    def get_introspection_schema(self) -> str:
        api_id = self.path.split("/")[-2]
        format_ = self.querystring.get("format")[0]  # type: ignore[index]
        if self.querystring.get("includeDirectives"):
            include_directives = (
                self.querystring.get("includeDirectives")[0].lower() == "true"  # type: ignore[index]
            )
        else:
            include_directives = True
        graphql_schema = self.appsync_backend.get_graphql_schema(api_id=api_id)

        schema = graphql_schema.get_introspection_schema(
            format_=format_, include_directives=include_directives
        )
        return schema

    def get_api_cache(self) -> str:
        api_id = self.path.split("/")[-2]
        api_cache = self.appsync_backend.get_api_cache(
            api_id=api_id,
        )
        return json.dumps({"apiCache": api_cache.to_json()})

    def delete_api_cache(self) -> str:
        api_id = self.path.split("/")[-2]
        self.appsync_backend.delete_api_cache(
            api_id=api_id,
        )
        return "{}"

    def create_api_cache(self) -> str:
        params = json.loads(self.body)
        api_id = self.path.split("/")[-2]
        ttl = params.get("ttl")
        transit_encryption_enabled = params.get("transitEncryptionEnabled")
        at_rest_encryption_enabled = params.get("atRestEncryptionEnabled")
        api_caching_behavior = params.get("apiCachingBehavior")
        type = params.get("type")
        health_metrics_config = params.get("healthMetricsConfig")
        api_cache = self.appsync_backend.create_api_cache(
            api_id=api_id,
            ttl=ttl,
            transit_encryption_enabled=transit_encryption_enabled,
            at_rest_encryption_enabled=at_rest_encryption_enabled,
            api_caching_behavior=api_caching_behavior,
            type=type,
            health_metrics_config=health_metrics_config,
        )
        return json.dumps({"apiCache": api_cache.to_json()})

    def update_api_cache(self) -> str:
        api_id = self.path.split("/")[-3]
        params = json.loads(self.body)
        ttl = params.get("ttl")
        api_caching_behavior = params.get("apiCachingBehavior")
        type = params.get("type")
        health_metrics_config = params.get("healthMetricsConfig")
        api_cache = self.appsync_backend.update_api_cache(
            api_id=api_id,
            ttl=ttl,
            api_caching_behavior=api_caching_behavior,
            type=type,
            health_metrics_config=health_metrics_config,
        )
        return json.dumps({"apiCache": api_cache.to_json()})

    def flush_api_cache(self) -> str:
        api_id = self.path.split("/")[-2]
        self.appsync_backend.flush_api_cache(
            api_id=api_id,
        )
        return "{}"

    # region: DataSource handlers
    def create_data_source(self) -> str:
        params = json.loads(self.body)
        # /v1/apis/{apiId}/datasources
        api_id = self.path.split("/")[-2]
        ds = self.appsync_backend.create_data_source(
            api_id=api_id,
            name=params.get("name"),
            type_=params.get("type"),
            description=params.get("description"),
            service_role_arn=params.get("serviceRoleArn"),
            dynamodb_config=params.get("dynamodbConfig"),
            lambda_config=params.get("lambdaConfig"),
            elasticsearch_config=params.get("elasticsearchConfig"),
            open_search_service_config=params.get("openSearchServiceConfig"),
            http_config=params.get("httpConfig"),
            relational_database_config=params.get("relationalDatabaseConfig"),
            event_bridge_config=params.get("eventBridgeConfig"),
            metrics_config=params.get("metricsConfig"),
        )
        return json.dumps({"dataSource": ds.to_json()})

    def get_data_source(self) -> str:
        # /v1/apis/{apiId}/datasources/{name}
        parts = self.path.split("/")
        api_id = parts[-3]
        name = unquote(parts[-1])
        ds = self.appsync_backend.get_data_source(api_id=api_id, name=name)
        return json.dumps({"dataSource": ds.to_json()})

    def update_data_source(self) -> str:
        # /v1/apis/{apiId}/datasources/{name}
        parts = self.path.split("/")
        api_id = parts[-3]
        name = unquote(parts[-1])
        params = json.loads(self.body)
        ds = self.appsync_backend.update_data_source(
            api_id=api_id,
            name=name,
            type_=params.get("type"),
            description=params.get("description"),
            service_role_arn=params.get("serviceRoleArn"),
            dynamodb_config=params.get("dynamodbConfig"),
            lambda_config=params.get("lambdaConfig"),
            elasticsearch_config=params.get("elasticsearchConfig"),
            open_search_service_config=params.get("openSearchServiceConfig"),
            http_config=params.get("httpConfig"),
            relational_database_config=params.get("relationalDatabaseConfig"),
            event_bridge_config=params.get("eventBridgeConfig"),
            metrics_config=params.get("metricsConfig"),
        )
        return json.dumps({"dataSource": ds.to_json()})

    def delete_data_source(self) -> str:
        # /v1/apis/{apiId}/datasources/{name}
        parts = self.path.split("/")
        api_id = parts[-3]
        name = unquote(parts[-1])
        self.appsync_backend.delete_data_source(api_id=api_id, name=name)
        return "{}"

    def list_data_sources(self) -> str:
        # /v1/apis/{apiId}/datasources
        api_id = self.path.split("/")[-2]
        data_sources = self.appsync_backend.list_data_sources(api_id=api_id)
        return json.dumps({"dataSources": [ds.to_json() for ds in data_sources]})

    # endregion

    # region: Type handlers
    def create_type(self) -> str:
        params = json.loads(self.body)
        # /v1/apis/{apiId}/types
        api_id = self.path.split("/")[-2]
        t = self.appsync_backend.create_type(
            api_id=api_id,
            definition=params.get("definition"),
            format_=params.get("format"),
        )
        return json.dumps({"type": t.to_json()})

    def update_type(self) -> str:
        # /v1/apis/{apiId}/types/{typeName}
        parts = self.path.split("/")
        api_id = parts[-3]
        type_name = unquote(parts[-1])
        params = json.loads(self.body)
        t = self.appsync_backend.update_type(
            api_id=api_id,
            type_name=type_name,
            definition=params.get("definition"),
            format_=params.get("format"),
        )
        return json.dumps({"type": t.to_json()})

    def delete_type(self) -> str:
        # /v1/apis/{apiId}/types/{typeName}
        parts = self.path.split("/")
        api_id = parts[-3]
        type_name = unquote(parts[-1])
        self.appsync_backend.delete_type(api_id=api_id, type_name=type_name)
        return "{}"

    def list_types(self) -> str:
        # /v1/apis/{apiId}/types?format=SDL
        api_id = self.path.split("/")[-2]
        format_ = self.querystring.get("format", ["SDL"])[0]
        types = self.appsync_backend.list_types(api_id=api_id, format_=format_)
        return json.dumps({"types": [t.to_json() for t in types]})

    # endregion

    # region: Resolver handlers
    def create_resolver(self) -> str:
        params = json.loads(self.body)
        # /v1/apis/{apiId}/types/{typeName}/resolvers
        parts = self.path.split("/")
        api_id = parts[-4]
        type_name = unquote(parts[-2])
        resolver = self.appsync_backend.create_resolver(
            api_id=api_id,
            type_name=type_name,
            field_name=params.get("fieldName"),
            data_source_name=params.get("dataSourceName"),
            request_mapping_template=params.get("requestMappingTemplate"),
            response_mapping_template=params.get("responseMappingTemplate"),
            kind=params.get("kind"),
            pipeline_config=params.get("pipelineConfig"),
            sync_config=params.get("syncConfig"),
            caching_config=params.get("cachingConfig"),
            max_batch_size=params.get("maxBatchSize"),
            runtime=params.get("runtime"),
            code=params.get("code"),
            metrics_config=params.get("metricsConfig"),
        )
        return json.dumps({"resolver": resolver.to_json()})

    def get_resolver(self) -> str:
        # /v1/apis/{apiId}/types/{typeName}/resolvers/{fieldName}
        parts = self.path.split("/")
        api_id = parts[-5]
        type_name = unquote(parts[-3])
        field_name = unquote(parts[-1])
        resolver = self.appsync_backend.get_resolver(
            api_id=api_id, type_name=type_name, field_name=field_name
        )
        return json.dumps({"resolver": resolver.to_json()})

    def update_resolver(self) -> str:
        # /v1/apis/{apiId}/types/{typeName}/resolvers/{fieldName}
        parts = self.path.split("/")
        api_id = parts[-5]
        type_name = unquote(parts[-3])
        field_name = unquote(parts[-1])
        params = json.loads(self.body)
        resolver = self.appsync_backend.update_resolver(
            api_id=api_id,
            type_name=type_name,
            field_name=field_name,
            data_source_name=params.get("dataSourceName"),
            request_mapping_template=params.get("requestMappingTemplate"),
            response_mapping_template=params.get("responseMappingTemplate"),
            kind=params.get("kind"),
            pipeline_config=params.get("pipelineConfig"),
            sync_config=params.get("syncConfig"),
            caching_config=params.get("cachingConfig"),
            max_batch_size=params.get("maxBatchSize"),
            runtime=params.get("runtime"),
            code=params.get("code"),
            metrics_config=params.get("metricsConfig"),
        )
        return json.dumps({"resolver": resolver.to_json()})

    def delete_resolver(self) -> str:
        # /v1/apis/{apiId}/types/{typeName}/resolvers/{fieldName}
        parts = self.path.split("/")
        api_id = parts[-5]
        type_name = unquote(parts[-3])
        field_name = unquote(parts[-1])
        self.appsync_backend.delete_resolver(
            api_id=api_id, type_name=type_name, field_name=field_name
        )
        return "{}"

    def list_resolvers(self) -> str:
        # /v1/apis/{apiId}/types/{typeName}/resolvers
        parts = self.path.split("/")
        api_id = parts[-4]
        type_name = unquote(parts[-2])
        resolvers = self.appsync_backend.list_resolvers(
            api_id=api_id, type_name=type_name
        )
        return json.dumps({"resolvers": [r.to_json() for r in resolvers]})

    # endregion

    # region: Function handlers
    def create_function(self) -> str:
        params = json.loads(self.body)
        # /v1/apis/{apiId}/functions
        api_id = self.path.split("/")[-2]
        fn = self.appsync_backend.create_function(
            api_id=api_id,
            name=params.get("name"),
            data_source_name=params.get("dataSourceName"),
            description=params.get("description"),
            request_mapping_template=params.get("requestMappingTemplate"),
            response_mapping_template=params.get("responseMappingTemplate"),
            function_version=params.get("functionVersion"),
            sync_config=params.get("syncConfig"),
            max_batch_size=params.get("maxBatchSize"),
            runtime=params.get("runtime"),
            code=params.get("code"),
        )
        return json.dumps({"functionConfiguration": fn.to_json()})

    def get_function(self) -> str:
        # /v1/apis/{apiId}/functions/{functionId}
        parts = self.path.split("/")
        api_id = parts[-3]
        function_id = parts[-1]
        fn = self.appsync_backend.get_function(
            api_id=api_id, function_id=function_id
        )
        return json.dumps({"functionConfiguration": fn.to_json()})

    def update_function(self) -> str:
        # /v1/apis/{apiId}/functions/{functionId}
        parts = self.path.split("/")
        api_id = parts[-3]
        function_id = parts[-1]
        params = json.loads(self.body)
        fn = self.appsync_backend.update_function(
            api_id=api_id,
            function_id=function_id,
            name=params.get("name"),
            description=params.get("description"),
            data_source_name=params.get("dataSourceName"),
            request_mapping_template=params.get("requestMappingTemplate"),
            response_mapping_template=params.get("responseMappingTemplate"),
            function_version=params.get("functionVersion"),
            sync_config=params.get("syncConfig"),
            max_batch_size=params.get("maxBatchSize"),
            runtime=params.get("runtime"),
            code=params.get("code"),
        )
        return json.dumps({"functionConfiguration": fn.to_json()})

    def delete_function(self) -> str:
        # /v1/apis/{apiId}/functions/{functionId}
        parts = self.path.split("/")
        api_id = parts[-3]
        function_id = parts[-1]
        self.appsync_backend.delete_function(
            api_id=api_id, function_id=function_id
        )
        return "{}"

    def list_functions(self) -> str:
        # /v1/apis/{apiId}/functions
        api_id = self.path.split("/")[-2]
        functions = self.appsync_backend.list_functions(api_id=api_id)
        return json.dumps(
            {"functions": [fn.to_json() for fn in functions]}
        )

    # endregion

    # region: DomainName handlers
    def create_domain_name(self) -> str:
        params = json.loads(self.body)
        dn = self.appsync_backend.create_domain_name(
            domain_name=params.get("domainName"),
            certificate_arn=params.get("certificateArn"),
            description=params.get("description"),
            tags=params.get("tags"),
        )
        return json.dumps({"domainNameConfig": dn.to_json()})

    def get_domain_name(self) -> str:
        # /v1/domainnames/{domainName}
        domain_name = unquote(self.path.split("/")[-1])
        dn = self.appsync_backend.get_domain_name(domain_name=domain_name)
        return json.dumps({"domainNameConfig": dn.to_json()})

    def update_domain_name(self) -> str:
        # /v1/domainnames/{domainName}
        domain_name = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        dn = self.appsync_backend.update_domain_name(
            domain_name=domain_name,
            description=params.get("description"),
        )
        return json.dumps({"domainNameConfig": dn.to_json()})

    def delete_domain_name(self) -> str:
        # /v1/domainnames/{domainName}
        domain_name = unquote(self.path.split("/")[-1])
        self.appsync_backend.delete_domain_name(domain_name=domain_name)
        return "{}"

    def list_domain_names(self) -> str:
        domain_names = self.appsync_backend.list_domain_names()
        return json.dumps(
            {"domainNameConfigs": [dn.to_json() for dn in domain_names]}
        )

    # endregion

    # region: ApiAssociation handlers
    def associate_api(self) -> str:
        # /v1/domainnames/{domainName}/apiassociation
        domain_name = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        assoc = self.appsync_backend.associate_api(
            domain_name=domain_name,
            api_id=params.get("apiId"),
        )
        return json.dumps({"apiAssociation": assoc.to_json()})

    def disassociate_api(self) -> str:
        # /v1/domainnames/{domainName}/apiassociation
        domain_name = unquote(self.path.split("/")[-2])
        self.appsync_backend.disassociate_api(domain_name=domain_name)
        return "{}"

    def get_api_association(self) -> str:
        # /v1/domainnames/{domainName}/apiassociation
        domain_name = unquote(self.path.split("/")[-2])
        assoc = self.appsync_backend.get_api_association(domain_name=domain_name)
        return json.dumps({"apiAssociation": assoc.to_json()})

    # endregion

    def create_api(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")

        if name:
            pattern = r"^[A-Za-z0-9_\-\ ]+$"
            if not re.match(pattern, name):
                raise AWSValidationException(
                    "1 validation error detected: "
                    "Value at 'name' failed to satisfy constraint: "
                    "Member must satisfy regular expression pattern: "
                    "[A-Za-z0-9_\\-\\ ]+"
                )

        owner_contact = params.get("ownerContact")
        tags = params.get("tags", {})
        event_config = params.get("eventConfig")

        api = self.appsync_backend.create_api(
            name=name,
            owner_contact=owner_contact,
            tags=tags,
            event_config=event_config,
        )

        response = api.to_json()
        return json.dumps({"api": response})

    def list_apis(self) -> str:
        apis = self.appsync_backend.list_apis()
        return json.dumps({"apis": [api.to_json() for api in apis]})

    def delete_api(self) -> str:
        api_id = self.path.split("/")[-1]
        self.appsync_backend.delete_api(api_id=api_id)
        return "{}"

    def create_channel_namespace(self) -> str:
        params = json.loads(self.body)
        api_id = self.path.split("/")[-2]
        name = params.get("name")

        if name:
            pattern = r"^[A-Za-z0-9](?:[A-Za-z0-9\-]{0,48}[A-Za-z0-9])?$"
            if not re.match(pattern, name):
                raise AWSValidationException(
                    "1 validation error detected: "
                    "Value at 'name' failed to satisfy constraint: "
                    "Member must satisfy regular expression pattern: "
                    "([A-Za-z0-9](?:[A-Za-z0-9\\-]{0,48}[A-Za-z0-9])?)"
                )

        subscribe_auth_modes = params.get("subscribeAuthModes")
        publish_auth_modes = params.get("publishAuthModes")
        code_handlers = params.get("codeHandlers")
        tags = params.get("tags", {})
        handler_configs = params.get("handlerConfigs", {})

        channel_namespace = self.appsync_backend.create_channel_namespace(
            api_id=api_id,
            name=name,
            subscribe_auth_modes=subscribe_auth_modes,
            publish_auth_modes=publish_auth_modes,
            code_handlers=code_handlers,
            tags=tags,
            handler_configs=handler_configs,
        )

        return json.dumps({"channelNamespace": channel_namespace.to_json()})

    def list_channel_namespaces(self) -> str:
        api_id = self.path.split("/")[-2]
        channel_namespaces = self.appsync_backend.list_channel_namespaces(api_id=api_id)
        return json.dumps(
            {
                "channelNamespaces": [
                    channel_namespace.to_json()
                    for channel_namespace in channel_namespaces
                ]
            }
        )

    def delete_channel_namespace(self) -> str:
        path_parts = self.path.split("/")
        api_id = path_parts[-3]
        name = path_parts[-1]

        self.appsync_backend.delete_channel_namespace(
            api_id=api_id,
            name=name,
        )
        return "{}"

    def get_api(self) -> str:
        api_id = self.path.split("/")[-1]

        api = self.appsync_backend.get_api(api_id=api_id)
        response = api.to_json()
        response["tags"] = self.appsync_backend.list_tags_for_resource(api.api_arn)
        return json.dumps({"api": response})

    def update_api(self) -> str:
        api_id = self.path.split("/")[-1]
        params = json.loads(self.body)
        api = self.appsync_backend.update_api(
            api_id=api_id,
            name=params.get("name"),
            owner_contact=params.get("ownerContact"),
            event_config=params.get("eventConfig"),
        )
        response = api.to_json()
        return json.dumps({"api": response})

    def get_channel_namespace(self) -> str:
        path_parts = self.path.split("/")
        api_id = path_parts[-3]
        name = path_parts[-1]
        ns = self.appsync_backend.get_channel_namespace(api_id=api_id, name=name)
        return json.dumps({"channelNamespace": ns.to_json()})

    def update_channel_namespace(self) -> str:
        path_parts = self.path.split("/")
        api_id = path_parts[-3]
        name = path_parts[-1]
        params = json.loads(self.body)
        ns = self.appsync_backend.update_channel_namespace(
            api_id=api_id,
            name=name,
            subscribe_auth_modes=params.get("subscribeAuthModes"),
            publish_auth_modes=params.get("publishAuthModes"),
            code_handlers=params.get("codeHandlers"),
            handler_configs=params.get("handlerConfigs"),
        )
        return json.dumps({"channelNamespace": ns.to_json()})

    # region: Merged/Source GraphQL API handlers
    def associate_merged_graphql_api(self) -> str:
        # POST /v1/sourceApis/{sourceApiIdentifier}/mergedApiAssociations
        source_api_identifier = self.path.split("/")[-2]
        params = json.loads(self.body)
        result = self.appsync_backend.associate_merged_graphql_api(
            source_api_identifier=source_api_identifier,
            merged_api_identifier=params.get("mergedApiIdentifier"),
        )
        return json.dumps(result)

    def disassociate_merged_graphql_api(self) -> str:
        # DELETE /v1/sourceApis/{sourceApiIdentifier}/mergedApiAssociations/{associationId}
        parts = self.path.split("/")
        source_api_identifier = parts[-3]
        association_id = parts[-1]
        result = self.appsync_backend.disassociate_merged_graphql_api(
            source_api_identifier=source_api_identifier,
            association_id=association_id,
        )
        return json.dumps(result)

    def associate_source_graphql_api(self) -> str:
        # POST /v1/mergedApis/{mergedApiIdentifier}/sourceApiAssociations
        merged_api_identifier = self.path.split("/")[-2]
        params = json.loads(self.body)
        result = self.appsync_backend.associate_source_graphql_api(
            merged_api_identifier=merged_api_identifier,
            source_api_identifier=params.get("sourceApiIdentifier"),
        )
        return json.dumps(result)

    def disassociate_source_graphql_api(self) -> str:
        # DELETE /v1/mergedApis/{mergedApiIdentifier}/sourceApiAssociations/{associationId}
        parts = self.path.split("/")
        merged_api_identifier = parts[-3]
        association_id = parts[-1]
        result = self.appsync_backend.disassociate_source_graphql_api(
            merged_api_identifier=merged_api_identifier,
            association_id=association_id,
        )
        return json.dumps(result)

    def get_source_api_association(self) -> str:
        # GET /v1/mergedApis/{mergedApiIdentifier}/sourceApiAssociations/{associationId}
        parts = self.path.split("/")
        merged_api_identifier = parts[-3]
        association_id = parts[-1]
        result = self.appsync_backend.get_source_api_association(
            merged_api_identifier=merged_api_identifier,
            association_id=association_id,
        )
        return json.dumps(result)

    def update_source_api_association(self) -> str:
        # POST /v1/mergedApis/{mergedApiIdentifier}/sourceApiAssociations/{associationId}
        parts = self.path.split("/")
        merged_api_identifier = parts[-3]
        association_id = parts[-1]
        params = json.loads(self.body)
        result = self.appsync_backend.update_source_api_association(
            merged_api_identifier=merged_api_identifier,
            association_id=association_id,
            **params,
        )
        return json.dumps(result)

    def list_source_api_associations(self) -> str:
        # GET /v1/apis/{apiId}/sourceApiAssociations
        api_id = self.path.split("/")[-2]
        associations = self.appsync_backend.list_source_api_associations(api_id=api_id)
        return json.dumps({"sourceApiAssociationSummaries": associations})

    def start_schema_merge(self) -> str:
        # POST /v1/mergedApis/{mergedApiIdentifier}/sourceApiAssociations/{associationId}/merge
        parts = self.path.split("/")
        merged_api_identifier = parts[-4]
        association_id = parts[-2]
        result = self.appsync_backend.start_schema_merge(
            association_id=association_id,
            merged_api_identifier=merged_api_identifier,
        )
        return json.dumps(result)

    # endregion

    # region: Resolvers by function
    def list_resolvers_by_function(self) -> str:
        # GET /v1/apis/{apiId}/functions/{functionId}/resolvers
        parts = self.path.split("/")
        api_id = parts[-4]
        function_id = parts[-2]
        resolvers = self.appsync_backend.list_resolvers_by_function(
            api_id=api_id, function_id=function_id
        )
        return json.dumps({"resolvers": resolvers})

    # endregion

    # region: Environment variables
    def get_graphql_api_environment_variables(self) -> str:
        # GET /v1/apis/{apiId}/environmentVariables
        api_id = self.path.split("/")[-2]
        env_vars = self.appsync_backend.get_graphql_api_environment_variables(api_id=api_id)
        return json.dumps({"environmentVariables": env_vars})

    def put_graphql_api_environment_variables(self) -> str:
        # PUT /v1/apis/{apiId}/environmentVariables
        api_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        env_vars = self.appsync_backend.put_graphql_api_environment_variables(
            api_id=api_id,
            environment_variables=params.get("environmentVariables", {}),
        )
        return json.dumps({"environmentVariables": env_vars})

    # endregion

    # region: Evaluate code / mapping template
    def evaluate_code(self) -> str:
        params = json.loads(self.body)
        result = self.appsync_backend.evaluate_code(
            runtime=params.get("runtime", {}),
            code=params.get("code", ""),
            context=params.get("context", ""),
            function_name=params.get("function", "request"),
        )
        return json.dumps(result)

    def evaluate_mapping_template(self) -> str:
        params = json.loads(self.body)
        result = self.appsync_backend.evaluate_mapping_template(
            template=params.get("template", ""),
            context=params.get("context", ""),
        )
        return json.dumps(result)

    # endregion

    # region: DataSource introspection
    def start_data_source_introspection(self) -> str:
        params = json.loads(self.body)
        introspection_id = self.appsync_backend.start_data_source_introspection(
            rds_data_api_config=params.get("rdsDataApiConfig"),
        )
        return json.dumps({"introspectionId": introspection_id, "introspectionStatus": "PROCESSING"})

    def get_data_source_introspection(self) -> str:
        # GET /v1/datasources/introspections/{introspectionId}
        introspection_id = self.path.split("/")[-1]
        result = self.appsync_backend.get_data_source_introspection(
            introspection_id=introspection_id,
        )
        return json.dumps(result)

    # endregion

    # region: ListTypesByAssociation
    def list_types_by_association(self) -> str:
        # GET /v1/mergedApis/{mergedApiIdentifier}/sourceApiAssociations/{associationId}/types
        parts = self.path.split("/")
        merged_api_identifier = parts[-5]
        association_id = parts[-3]
        format_ = self.querystring.get("format", ["SDL"])[0]
        types = self.appsync_backend.list_types_by_association(
            merged_api_identifier=merged_api_identifier,
            association_id=association_id,
            format_=format_,
        )
        return json.dumps({"types": types})

    # endregion
