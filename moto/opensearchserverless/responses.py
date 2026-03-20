"""Handles incoming opensearchserverless requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import OpenSearchServiceServerlessBackend, opensearchserverless_backends


class OpenSearchServiceServerlessResponse(BaseResponse):
    """Handler for OpenSearchServiceServerless requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="opensearchserverless")

    @property
    def opensearchserverless_backend(self) -> OpenSearchServiceServerlessBackend:
        """Return backend instance specific for this region."""

        return opensearchserverless_backends[self.current_account][self.region]

    def create_security_policy(self) -> str:
        params = json.loads(self.body)
        client_token = params.get("clientToken")
        description = params.get("description")
        name = params.get("name")
        policy = params.get("policy")
        type = params.get("type")
        security_policy_detail = (
            self.opensearchserverless_backend.create_security_policy(
                client_token=client_token,
                description=description,
                name=name,
                policy=policy,
                type=type,
            )
        )
        return json.dumps({"securityPolicyDetail": security_policy_detail.to_dict()})

    def get_security_policy(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        type = params.get("type")
        security_policy_detail = self.opensearchserverless_backend.get_security_policy(
            name=name,
            type=type,
        )
        return json.dumps({"securityPolicyDetail": security_policy_detail.to_dict()})

    def list_security_policies(self) -> str:
        params = json.loads(self.body)
        resource = params.get("resource")
        type = params.get("type")
        security_policy_summaries = (
            self.opensearchserverless_backend.list_security_policies(
                resource=resource,
                type=type,
            )
        )
        return json.dumps(
            {
                "securityPolicySummaries": [
                    sp.to_dict_list() for sp in security_policy_summaries
                ]
            }
        )

    def update_security_policy(self) -> str:
        params = json.loads(self.body)
        client_token = params.get("clientToken")
        description = params.get("description")
        name = params.get("name")
        policy = params.get("policy")
        policy_version = params.get("policyVersion")
        type = params.get("type")
        security_policy_detail = (
            self.opensearchserverless_backend.update_security_policy(
                client_token=client_token,
                description=description,
                name=name,
                policy=policy,
                policy_version=policy_version,
                type=type,
            )
        )
        return json.dumps({"securityPolicyDetail": security_policy_detail.to_dict()})

    def create_collection(self) -> str:
        params = json.loads(self.body)
        client_token = params.get("clientToken")
        description = params.get("description")
        name = params.get("name")
        standby_replicas = params.get("standbyReplicas")
        tags = params.get("tags")
        type = params.get("type")
        create_collection_detail = self.opensearchserverless_backend.create_collection(
            client_token=client_token,
            description=description,
            name=name,
            standby_replicas=standby_replicas,
            tags=tags,
            type=type,
        )
        return json.dumps(
            {"createCollectionDetail": create_collection_detail.to_dict()}
        )

    def list_collections(self) -> str:
        params = json.loads(self.body)
        collection_filters = params.get("collectionFilters")
        collection_summaries = self.opensearchserverless_backend.list_collections(
            collection_filters=collection_filters,
        )
        return json.dumps(
            {"collectionSummaries": [cs.to_dict_list() for cs in collection_summaries]}
        )

    def create_vpc_endpoint(self) -> str:
        params = json.loads(self.body)
        client_token = params.get("clientToken")
        name = params.get("name")
        security_group_ids = params.get("securityGroupIds")
        subnet_ids = params.get("subnetIds")
        vpc_id = params.get("vpcId")
        create_vpc_endpoint_detail = (
            self.opensearchserverless_backend.create_vpc_endpoint(
                client_token=client_token,
                name=name,
                security_group_ids=security_group_ids,
                subnet_ids=subnet_ids,
                vpc_id=vpc_id,
            )
        )
        return json.dumps(
            {"createVpcEndpointDetail": create_vpc_endpoint_detail.to_dict()}
        )

    def delete_collection(self) -> str:
        params = json.loads(self.body)
        client_token = params.get("clientToken")
        id = params.get("id")
        delete_collection_detail = self.opensearchserverless_backend.delete_collection(
            client_token=client_token,
            id=id,
        )
        return json.dumps(
            {"deleteCollectionDetail": delete_collection_detail.to_dict()}
        )

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tags = params.get("tags")
        self.opensearchserverless_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tag_keys = params.get("tagKeys")
        self.opensearchserverless_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tags = self.opensearchserverless_backend.list_tags_for_resource(
            resource_arn=resource_arn,
        )
        return json.dumps({"tags": tags})

    def batch_get_collection(self) -> str:
        params = json.loads(self.body)
        ids = params.get("ids")
        names = params.get("names")
        collection_details, collection_error_details = (
            self.opensearchserverless_backend.batch_get_collection(
                ids=ids,
                names=names,
            )
        )
        return json.dumps(
            {
                "collectionDetails": collection_details,
                "collectionErrorDetails": collection_error_details,
            }
        )

    def update_collection(self) -> str:
        params = json.loads(self.body)
        collection = self.opensearchserverless_backend.update_collection(
            id=params.get("id"),
            description=params.get("description"),
        )
        return json.dumps({"updateCollectionDetail": collection.to_dict()})

    def delete_security_policy(self) -> str:
        params = json.loads(self.body)
        self.opensearchserverless_backend.delete_security_policy(
            name=params.get("name"),
            type=params.get("type"),
        )
        return json.dumps({})

    # Access Policy handlers
    def create_access_policy(self) -> str:
        params = json.loads(self.body)
        ap = self.opensearchserverless_backend.create_access_policy(
            description=params.get("description", ""),
            name=params.get("name"),
            policy=params.get("policy"),
            type=params.get("type"),
        )
        return json.dumps({"accessPolicyDetail": ap.to_dict()})

    def get_access_policy(self) -> str:
        params = json.loads(self.body)
        ap = self.opensearchserverless_backend.get_access_policy(
            name=params.get("name"),
            type=params.get("type"),
        )
        return json.dumps({"accessPolicyDetail": ap.to_dict()})

    def list_access_policies(self) -> str:
        params = json.loads(self.body)
        policies = self.opensearchserverless_backend.list_access_policies(
            type=params.get("type"),
        )
        return json.dumps(
            {"accessPolicySummaries": [ap.to_dict_list() for ap in policies]}
        )

    def update_access_policy(self) -> str:
        params = json.loads(self.body)
        ap = self.opensearchserverless_backend.update_access_policy(
            name=params.get("name"),
            type=params.get("type"),
            description=params.get("description"),
            policy=params.get("policy"),
            policy_version=params.get("policyVersion"),
        )
        return json.dumps({"accessPolicyDetail": ap.to_dict()})

    def delete_access_policy(self) -> str:
        params = json.loads(self.body)
        self.opensearchserverless_backend.delete_access_policy(
            name=params.get("name"),
            type=params.get("type"),
        )
        return json.dumps({})

    # Lifecycle Policy handlers
    def create_lifecycle_policy(self) -> str:
        params = json.loads(self.body)
        lp = self.opensearchserverless_backend.create_lifecycle_policy(
            description=params.get("description", ""),
            name=params.get("name"),
            policy=params.get("policy"),
            type=params.get("type"),
        )
        return json.dumps({"lifecyclePolicyDetail": lp.to_dict()})

    def list_lifecycle_policies(self) -> str:
        params = json.loads(self.body)
        policies = self.opensearchserverless_backend.list_lifecycle_policies(
            type=params.get("type"),
        )
        return json.dumps(
            {"lifecyclePolicySummaries": [lp.to_dict_list() for lp in policies]}
        )

    def update_lifecycle_policy(self) -> str:
        params = json.loads(self.body)
        lp = self.opensearchserverless_backend.update_lifecycle_policy(
            name=params.get("name"),
            type=params.get("type"),
            description=params.get("description"),
            policy=params.get("policy"),
            policy_version=params.get("policyVersion"),
        )
        return json.dumps({"lifecyclePolicyDetail": lp.to_dict()})

    def delete_lifecycle_policy(self) -> str:
        params = json.loads(self.body)
        self.opensearchserverless_backend.delete_lifecycle_policy(
            name=params.get("name"),
            type=params.get("type"),
        )
        return json.dumps({})

    def batch_get_lifecycle_policy(self) -> str:
        params = json.loads(self.body)
        details, errors = self.opensearchserverless_backend.batch_get_lifecycle_policy(
            identifiers=params.get("identifiers", []),
        )
        return json.dumps(
            {"lifecyclePolicyDetails": details, "lifecyclePolicyErrorDetails": errors}
        )

    def batch_get_effective_lifecycle_policy(self) -> str:
        params = json.loads(self.body)
        details, errors = (
            self.opensearchserverless_backend.batch_get_effective_lifecycle_policy(
                resource_identifiers=params.get("resourceIdentifiers", []),
            )
        )
        return json.dumps(
            {
                "effectiveLifecyclePolicyDetails": details,
                "effectiveLifecyclePolicyErrorDetails": errors,
            }
        )

    # Security Config handlers
    def create_security_config(self) -> str:
        params = json.loads(self.body)
        sc = self.opensearchserverless_backend.create_security_config(
            description=params.get("description", ""),
            name=params.get("name"),
            saml_options=params.get("samlOptions"),
            type=params.get("type"),
        )
        return json.dumps({"securityConfigDetail": sc.to_dict()})

    def get_security_config(self) -> str:
        params = json.loads(self.body)
        sc = self.opensearchserverless_backend.get_security_config(id=params.get("id"))
        return json.dumps({"securityConfigDetail": sc.to_dict()})

    def list_security_configs(self) -> str:
        params = json.loads(self.body)
        configs = self.opensearchserverless_backend.list_security_configs(
            type=params.get("type")
        )
        return json.dumps(
            {"securityConfigSummaries": [sc.to_dict_list() for sc in configs]}
        )

    def update_security_config(self) -> str:
        params = json.loads(self.body)
        sc = self.opensearchserverless_backend.update_security_config(
            config_version=params.get("configVersion"),
            id=params.get("id"),
            description=params.get("description"),
            saml_options=params.get("samlOptions"),
        )
        return json.dumps({"securityConfigDetail": sc.to_dict()})

    def delete_security_config(self) -> str:
        params = json.loads(self.body)
        self.opensearchserverless_backend.delete_security_config(id=params.get("id"))
        return json.dumps({})

    # VPC Endpoint handlers
    def delete_vpc_endpoint(self) -> str:
        params = json.loads(self.body)
        detail = self.opensearchserverless_backend.delete_vpc_endpoint(
            id=params.get("id")
        )
        return json.dumps({"deleteVpcEndpointDetail": detail})

    def list_vpc_endpoints(self) -> str:
        endpoints = self.opensearchserverless_backend.list_vpc_endpoints()
        return json.dumps({"vpcEndpointSummaries": [ep.to_dict() for ep in endpoints]})

    def update_vpc_endpoint(self) -> str:
        params = json.loads(self.body)
        detail = self.opensearchserverless_backend.update_vpc_endpoint(
            id=params.get("id"),
            add_security_group_ids=params.get("addSecurityGroupIds"),
            add_subnet_ids=params.get("addSubnetIds"),
            remove_security_group_ids=params.get("removeSecurityGroupIds"),
            remove_subnet_ids=params.get("removeSubnetIds"),
        )
        return json.dumps({"UpdateVpcEndpointDetail": detail})

    def batch_get_vpc_endpoint(self) -> str:
        params = json.loads(self.body)
        details, errors = self.opensearchserverless_backend.batch_get_vpc_endpoint(
            ids=params.get("ids", []),
        )
        return json.dumps(
            {"vpcEndpointDetails": details, "vpcEndpointErrorDetails": errors}
        )

    # Account Settings handlers
    def get_account_settings(self) -> str:
        settings = self.opensearchserverless_backend.get_account_settings()
        return json.dumps({"accountSettingsDetail": settings})

    def update_account_settings(self) -> str:
        params = json.loads(self.body)
        settings = self.opensearchserverless_backend.update_account_settings(
            capacity_limits=params.get("capacityLimits"),
        )
        return json.dumps({"accountSettingsDetail": settings})

    # Policies Stats handler
    def get_policies_stats(self) -> str:
        stats = self.opensearchserverless_backend.get_policies_stats()
        return json.dumps(stats)

    # Index CRUD handlers
    def create_index(self) -> str:
        params = json.loads(self.body)
        collection_id = params.get("id")
        index_name = params.get("indexName")
        index_schema = params.get("indexSchema")
        collection_endpoint = params.get("collectionEndpoint")
        if not collection_endpoint and collection_id:
            coll = self.opensearchserverless_backend.collections.get(collection_id)
            collection_endpoint = coll.collection_endpoint if coll else ""
        if not collection_endpoint:
            collection_endpoint = ""
        field_mappings = []
        if isinstance(index_schema, dict) and "fieldMappings" in index_schema:
            field_mappings = index_schema.get("fieldMappings", [])
        result = self.opensearchserverless_backend.create_index(
            collection_endpoint=collection_endpoint,
            name=index_name or "",
            description=params.get("description", ""),
            field_mappings=field_mappings,
        )
        return json.dumps(result)

    def get_index(self) -> str:
        params = json.loads(self.body)
        backend = self.opensearchserverless_backend
        index_id = backend._resolve_index_id(
            params.get("id"),
            params.get("id"),
            params.get("indexName"),
        )
        if not index_id:
            from .exceptions import ResourceNotFoundException

            raise ResourceNotFoundException(
                msg=f"Index {params.get('id') or params.get('indexName') or 'unknown'} not found"
            )
        result = backend.get_index(index_id=index_id)
        return json.dumps(result)

    def update_index(self) -> str:
        params = json.loads(self.body)
        backend = self.opensearchserverless_backend
        index_id = backend._resolve_index_id(
            params.get("id"),
            params.get("id"),
            params.get("indexName"),
        )
        if not index_id:
            from .exceptions import ResourceNotFoundException

            raise ResourceNotFoundException(
                msg=f"Index {params.get('id') or params.get('indexName') or 'unknown'} not found"
            )
        index_schema = params.get("indexSchema")
        field_mappings = None
        if isinstance(index_schema, dict) and "fieldMappings" in index_schema:
            field_mappings = index_schema.get("fieldMappings")
        result = backend.update_index(
            index_id=index_id,
            description=params.get("description"),
            field_mappings=field_mappings,
        )
        return json.dumps(result)

    def delete_index(self) -> str:
        params = json.loads(self.body)
        backend = self.opensearchserverless_backend
        index_id = backend._resolve_index_id(
            params.get("id"),
            params.get("id"),
            params.get("indexName"),
        )
        if not index_id:
            from .exceptions import ResourceNotFoundException

            raise ResourceNotFoundException(
                msg=f"Index {params.get('id') or params.get('indexName') or 'unknown'} not found"
            )
        result = backend.delete_index(index_id=index_id)
        return json.dumps(result)
