from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .models import CloudFrontBackend, cloudfront_backends, random_id


class CloudFrontResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="cloudfront")
        self.automated_parameter_parsing = True

    @property
    def backend(self) -> CloudFrontBackend:
        return cloudfront_backends[self.current_account][self.partition]

    def _get_action(self) -> str:
        # This is needed because the uri matcher doesn't take queryargs into account
        action = super()._get_action()
        if action == "CreateDistribution" and "WithTags" in self.querystring:
            action = "CreateDistributionWithTags"
        elif action is None and "Operation" in self.querystring:
            op_to_action = {"Tag": "TagResource", "Untag": "UntagResource"}
            operation = self.querystring.get("Operation")[0]
            action = op_to_action.get(operation, action)
        return action

    def create_distribution(self) -> ActionResult:
        distribution_config = self._get_param("DistributionConfig", {})
        distribution, location, e_tag = self.backend.create_distribution(
            distribution_config=distribution_config,
            tags=[],
        )
        result = {"Distribution": distribution, "ETag": e_tag, "Location": location}
        return ActionResult(result)

    def create_distribution_with_tags(self) -> ActionResult:
        distribution_config = self._get_param(
            "DistributionConfigWithTags.DistributionConfig", {}
        )
        tags = self._get_param("DistributionConfigWithTags.Tags.Items", [])
        distribution, location, e_tag = self.backend.create_distribution(
            distribution_config=distribution_config,
            tags=tags,
        )
        result = {"Distribution": distribution, "ETag": e_tag, "Location": location}
        return ActionResult(result)

    def list_distributions(self) -> ActionResult:
        distributions = self.backend.list_distributions()
        result = {
            "DistributionList": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": len(distributions),
                "Items": distributions if distributions else None,
            }
        }
        return ActionResult(result)

    def delete_distribution(self) -> ActionResult:
        distribution_id = self._get_param("Id")
        if_match = self._get_param("IfMatch")
        self.backend.delete_distribution(distribution_id, if_match)
        return EmptyResult()

    def get_distribution(self) -> ActionResult:
        distribution_id = self._get_param("Id")
        dist, etag = self.backend.get_distribution(distribution_id)
        result = {"Distribution": dist, "ETag": etag}
        return ActionResult(result)

    def get_distribution_config(self) -> ActionResult:
        dist_id = self._get_param("Id")
        distribution_config, etag = self.backend.get_distribution_config(dist_id)
        result = {"DistributionConfig": distribution_config, "ETag": etag}
        return ActionResult(result)

    def update_distribution(self) -> ActionResult:
        dist_id = self._get_param("Id")
        dist_config = self._get_param("DistributionConfig", {})
        if_match = self._get_param("IfMatch")
        dist, location, e_tag = self.backend.update_distribution(
            dist_config=dist_config,
            _id=dist_id,
            if_match=if_match,
        )
        result = {"Distribution": dist, "ETag": e_tag, "Location": location}
        return ActionResult(result)

    def create_invalidation(self) -> ActionResult:
        dist_id = self._get_param("DistributionId")
        paths = self._get_param("InvalidationBatch.Paths.Items", [])
        caller_ref = self._get_param("InvalidationBatch.CallerReference")
        invalidation = self.backend.create_invalidation(dist_id, paths, caller_ref)
        result = {"Invalidation": invalidation, "Location": invalidation.location}
        return ActionResult(result)

    def list_invalidations(self) -> ActionResult:
        dist_id = self._get_param("DistributionId")
        invalidations = self.backend.list_invalidations(dist_id)
        result = {
            "InvalidationList": {
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": len(invalidations),
                "Items": invalidations if invalidations else None,
            }
        }
        return ActionResult(result)

    def get_invalidation(self) -> ActionResult:
        invalidation_id = self._get_param("Id")
        dist_id = self._get_param("DistributionId")
        invalidation = self.backend.get_invalidation(dist_id, invalidation_id)
        result = {"Invalidation": invalidation}
        return ActionResult(result)

    def list_tags_for_resource(self) -> ActionResult:
        resource = self._get_param("Resource")
        tags = self.backend.list_tags_for_resource(resource=resource)["Tags"]
        result = {"Tags": {"Items": tags}}
        return ActionResult(result)

    def tag_resource(self) -> ActionResult:
        resource = self._get_param("Resource")
        tags = self._get_param("Tags.Items", [])
        self.backend.tag_resource(resource=resource, tags=tags)
        return EmptyResult()

    def untag_resource(self) -> ActionResult:
        resource = self._get_param("Resource")
        tag_keys_data = self._get_param("TagKeys.Items", [])
        self.backend.untag_resource(resource=resource, tag_keys=tag_keys_data)
        return EmptyResult()

    def create_origin_access_control(self) -> ActionResult:
        config = self._get_param("OriginAccessControlConfig", {})
        control = self.backend.create_origin_access_control(config)
        result = {
            "OriginAccessControl": {
                "Id": control.id,
                "OriginAccessControlConfig": control,
            },
            "ETag": control.etag,
        }
        return ActionResult(result)

    def get_origin_access_control(self) -> ActionResult:
        control_id = self._get_param("Id")
        control = self.backend.get_origin_access_control(control_id)
        result = {
            "OriginAccessControl": {
                "Id": control.id,
                "OriginAccessControlConfig": control,
            },
            "ETag": control.etag,
        }
        return ActionResult(result)

    def list_origin_access_controls(self) -> ActionResult:
        controls = self.backend.list_origin_access_controls()
        result = {
            "OriginAccessControlList": {
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": len(controls),
                "Items": controls,
            }
        }
        return ActionResult(result)

    def update_origin_access_control(self) -> ActionResult:
        control_id = self._get_param("Id")
        config = self._get_param("OriginAccessControlConfig", {})
        control = self.backend.update_origin_access_control(control_id, config)
        result = {
            "OriginAccessControl": {
                "Id": control.id,
                "OriginAccessControlConfig": control,
            },
            "ETag": control.etag,
        }
        return ActionResult(result)

    def delete_origin_access_control(self) -> ActionResult:
        control_id = self._get_param("Id")
        self.backend.delete_origin_access_control(control_id)
        return EmptyResult()

    def create_public_key(self) -> ActionResult:
        config = self._get_param("PublicKeyConfig")
        caller_ref = config["CallerReference"]
        name = config["Name"]
        encoded_key = config["EncodedKey"]
        public_key = self.backend.create_public_key(
            caller_ref=caller_ref, name=name, encoded_key=encoded_key
        )
        result = {
            "PublicKey": public_key,
            "Location": public_key.location,
            "ETag": public_key.etag,
        }
        return ActionResult(result)

    def get_public_key(self) -> ActionResult:
        key_id = self._get_param("Id")
        public_key = self.backend.get_public_key(key_id=key_id)
        result = {"PublicKey": public_key, "ETag": public_key.etag}
        return ActionResult(result)

    def delete_public_key(self) -> ActionResult:
        key_id = self._get_param("Id")
        self.backend.delete_public_key(key_id=key_id)
        return EmptyResult()

    def list_public_keys(self) -> ActionResult:
        keys = self.backend.list_public_keys()
        result = {
            "PublicKeyList": {
                "MaxItems": 100,
                "Quantity": len(keys),
                "Items": keys if keys else None,
            }
        }
        return ActionResult(result)

    def create_key_group(self) -> ActionResult:
        name = self._get_param("KeyGroupConfig.Name")
        items = self._get_param("KeyGroupConfig.Items", [])
        key_group = self.backend.create_key_group(name=name, items=items)
        result = {
            "KeyGroup": key_group,
            "Location": key_group.location,
            "ETag": key_group.etag,
        }
        return ActionResult(result)

    def get_key_group(self) -> ActionResult:
        group_id = self._get_param("Id")
        key_group = self.backend.get_key_group(group_id=group_id)
        result = {"KeyGroup": key_group, "ETag": key_group.etag}
        return ActionResult(result)

    def list_key_groups(self) -> ActionResult:
        groups = self.backend.list_key_groups()
        result = {
            "KeyGroupList": {
                "Quantity": len(groups),
                "Items": [{"KeyGroup": key_group} for key_group in groups],
            }
        }
        return ActionResult(result)

    # VPC Origins
    def create_vpc_origin(self) -> ActionResult:
        config = self._get_param("VpcOriginEndpointConfig", {})
        vo = self.backend.create_vpc_origin(config)
        result = {"VpcOrigin": vo, "ETag": vo.etag}
        return ActionResult(result, status_code=202)

    def get_vpc_origin(self) -> ActionResult:
        vpc_id = self._get_param("Id")
        vo = self.backend.get_vpc_origin(vpc_id)
        result = {"VpcOrigin": vo, "ETag": vo.etag}
        return ActionResult(result)

    def update_vpc_origin(self) -> ActionResult:
        vpc_id = self._get_param("Id")
        config = self._get_param("VpcOriginEndpointConfig", {})
        vo = self.backend.update_vpc_origin(vpc_id, config)
        result = {"VpcOrigin": vo, "ETag": vo.etag}
        return ActionResult(result)

    def delete_vpc_origin(self) -> ActionResult:
        vpc_id = self._get_param("Id")
        self.backend.delete_vpc_origin(vpc_id)
        return EmptyResult(status_code=202)

    def list_vpc_origins(self) -> ActionResult:
        origins = self.backend.list_vpc_origins()
        items = [
            {
                "Id": vo.id,
                "Name": vo.vpc_origin_endpoint_config.get("Name", ""),
                "Status": vo.status,
                "CreatedTime": vo.created_time,
                "LastModifiedTime": vo.last_modified_time,
                "Arn": vo.arn,
                "AccountId": vo.account_id,
                "OriginEndpointArn": vo.vpc_origin_endpoint_config.get("Arn", ""),
            }
            for vo in origins
        ]
        result = {
            "VpcOriginList": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": len(items),
                "Items": items if items else None,
            }
        }
        return ActionResult(result)

    # Trust Stores
    def create_trust_store(self) -> ActionResult:
        name = self._get_param("Name", "")
        ts = self.backend.create_trust_store(name)
        result = {"TrustStore": ts, "ETag": ts.etag}
        return ActionResult(result, status_code=201)

    def get_trust_store(self) -> ActionResult:
        store_id = self._get_param("Id")
        ts = self.backend.get_trust_store(store_id)
        result = {"TrustStore": ts, "ETag": ts.etag}
        return ActionResult(result)

    def update_trust_store(self) -> ActionResult:
        store_id = self._get_param("Id")
        ts = self.backend.update_trust_store(store_id)
        result = {"TrustStore": ts, "ETag": ts.etag}
        return ActionResult(result)

    def delete_trust_store(self) -> ActionResult:
        store_id = self._get_param("Id")
        self.backend.delete_trust_store(store_id)
        return EmptyResult()

    def list_trust_stores(self) -> ActionResult:
        stores = self.backend.list_trust_stores()
        result = {"TrustStoreList": stores if stores else None}
        return ActionResult(result)

    # Anycast IP Lists
    def create_anycast_ip_list(self) -> ActionResult:
        name = self._get_param("Name", "")
        aip = self.backend.create_anycast_ip_list(name)
        result = {"AnycastIpList": aip, "ETag": aip.etag}
        return ActionResult(result, status_code=201)

    def get_anycast_ip_list(self) -> ActionResult:
        list_id = self._get_param("Id")
        aip = self.backend.get_anycast_ip_list(list_id)
        result = {"AnycastIpList": aip, "ETag": aip.etag}
        return ActionResult(result)

    def delete_anycast_ip_list(self) -> ActionResult:
        list_id = self._get_param("Id")
        self.backend.delete_anycast_ip_list(list_id)
        return EmptyResult()

    def list_anycast_ip_lists(self) -> ActionResult:
        lists = self.backend.list_anycast_ip_lists()
        items = [
            {
                "Id": a.id,
                "Name": a.name,
                "Status": a.status,
                "Arn": a.arn,
                "IpCount": a.ip_count,
                "LastModifiedTime": a.last_modified_time,
            }
            for a in lists
        ]
        result = {
            "AnycastIpLists": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": len(items),
                "Items": items if items else None,
            }
        }
        return ActionResult(result)

    # Connection Groups
    def create_connection_group(self) -> ActionResult:
        name = self._get_param("Name", "")
        cg = self.backend.create_connection_group(name)
        result = {"ConnectionGroup": cg, "ETag": cg.etag}
        return ActionResult(result, status_code=201)

    def get_connection_group(self) -> ActionResult:
        group_id = self._get_param("Id")
        cg = self.backend.get_connection_group(group_id)
        result = {"ConnectionGroup": cg, "ETag": cg.etag}
        return ActionResult(result)

    def update_connection_group(self) -> ActionResult:
        group_id = self._get_param("Id")
        cg = self.backend.get_connection_group(group_id)
        cg.etag = random_id(length=14)
        result = {"ConnectionGroup": cg, "ETag": cg.etag}
        return ActionResult(result)

    def delete_connection_group(self) -> ActionResult:
        group_id = self._get_param("Id")
        self.backend.delete_connection_group(group_id)
        return EmptyResult()

    def list_connection_groups(self) -> ActionResult:
        groups = self.backend.list_connection_groups()
        result = {"ConnectionGroups": groups if groups else None}
        return ActionResult(result)

    # Connection Functions
    def create_connection_function(self) -> ActionResult:
        name = self._get_param("Name", "")
        cf = self.backend.create_connection_function(name)
        result = {"ConnectionFunctionSummary": cf, "ETag": cf.etag}
        return ActionResult(result, status_code=201)

    def describe_connection_function(self) -> ActionResult:
        name = self._get_param("Name")
        cf = self.backend.get_connection_function(name)
        result = {"ConnectionFunctionSummary": cf, "ETag": cf.etag}
        return ActionResult(result)

    def update_connection_function(self) -> ActionResult:
        name = self._get_param("Name")
        cf = self.backend.get_connection_function(name)
        cf.etag = random_id(length=14)
        result = {"ConnectionFunctionSummary": cf, "ETag": cf.etag}
        return ActionResult(result)

    def publish_connection_function(self) -> ActionResult:
        name = self._get_param("Name")
        cf = self.backend.get_connection_function(name)
        cf.stage = "LIVE"
        cf.etag = random_id(length=14)
        result = {"ConnectionFunctionSummary": cf, "ETag": cf.etag}
        return ActionResult(result)

    def delete_connection_function(self) -> ActionResult:
        name = self._get_param("Name")
        self.backend.delete_connection_function(name)
        return EmptyResult()

    def list_connection_functions(self) -> ActionResult:
        funcs = self.backend.list_connection_functions()
        result = {"ConnectionFunctions": funcs if funcs else None}
        return ActionResult(result)

    def test_connection_function(self) -> ActionResult:
        result = {
            "TestResult": {
                "FunctionOutput": '{"response":{"statusCode":200}}',
                "ComputeUtilization": "12",
            }
        }
        return ActionResult(result)

    # Distribution Tenants
    def create_distribution_tenant(self) -> ActionResult:
        name = self._get_param("Name", "")
        dist_id = self._get_param("DistributionId", "")
        dt = self.backend.create_distribution_tenant(name, dist_id)
        result = {"DistributionTenant": dt, "ETag": dt.etag}
        return ActionResult(result, status_code=201)

    def get_distribution_tenant(self) -> ActionResult:
        dt_id = self._get_param("Id")
        dt = self.backend.get_distribution_tenant(dt_id)
        result = {"DistributionTenant": dt, "ETag": dt.etag}
        return ActionResult(result)

    def update_distribution_tenant(self) -> ActionResult:
        dt_id = self._get_param("Id")
        dt = self.backend.get_distribution_tenant(dt_id)
        dt.etag = random_id(length=14)
        result = {"DistributionTenant": dt, "ETag": dt.etag}
        return ActionResult(result)

    def delete_distribution_tenant(self) -> ActionResult:
        dt_id = self._get_param("Id")
        self.backend.delete_distribution_tenant(dt_id)
        return EmptyResult()

    def list_distribution_tenants(self) -> ActionResult:
        tenants = self.backend.list_distribution_tenants()
        result = {"DistributionTenantList": tenants if tenants else None}
        return ActionResult(result)

    def list_distribution_tenants_by_customization(self) -> ActionResult:
        result = {"DistributionTenantList": None}
        return ActionResult(result)

    def create_invalidation_for_distribution_tenant(self) -> ActionResult:
        inv_id = random_id()
        result = {
            "Invalidation": {
                "Id": inv_id,
                "Status": "COMPLETED",
                "CreateTime": "2021-01-01T00:00:00.000Z",
                "InvalidationBatch": {
                    "Paths": {"Quantity": 0},
                    "CallerReference": "ref",
                },
            }
        }
        return ActionResult(result, status_code=201)

    def get_invalidation_for_distribution_tenant(self) -> ActionResult:
        inv_id = self._get_param("Id")
        result = {
            "Invalidation": {
                "Id": inv_id,
                "Status": "COMPLETED",
                "CreateTime": "2021-01-01T00:00:00.000Z",
                "InvalidationBatch": {
                    "Paths": {"Quantity": 0},
                    "CallerReference": "ref",
                },
            }
        }
        return ActionResult(result)

    def list_invalidations_for_distribution_tenant(self) -> ActionResult:
        result = {
            "InvalidationList": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": 0,
            }
        }
        return ActionResult(result)

    # Resource Policy
    def get_resource_policy(self) -> ActionResult:
        return ActionResult({}, status_code=200)

    def put_resource_policy(self) -> ActionResult:
        return ActionResult({}, status_code=200)

    def delete_resource_policy(self) -> ActionResult:
        return EmptyResult()

    # Other stubs
    def list_domain_conflicts(self) -> ActionResult:
        return ActionResult({})

    def verify_dns_configuration(self) -> ActionResult:
        return ActionResult({})

    def get_managed_certificate_details(self) -> ActionResult:
        result = {"ManagedCertificateDetails": {"CertificateStatus": "ISSUED"}}
        return ActionResult(result)

    def list_distributions_by_vpc_origin_id(self) -> ActionResult:
        result = {
            "DistributionIdList": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": 0,
            }
        }
        return ActionResult(result)

    def list_distributions_by_anycast_ip_list_id(self) -> ActionResult:
        result = {
            "DistributionIdList": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": 0,
            }
        }
        return ActionResult(result)

    def list_distributions_by_trust_store(self) -> ActionResult:
        result = {
            "DistributionIdList": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": 0,
            }
        }
        return ActionResult(result)

    def list_distributions_by_connection_function(self) -> ActionResult:
        result = {
            "DistributionIdList": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": 0,
            }
        }
        return ActionResult(result)

    def list_distributions_by_owned_resource(self) -> ActionResult:
        result = {
            "DistributionIdList": {
                "Marker": "",
                "MaxItems": 100,
                "IsTruncated": False,
                "Quantity": 0,
            }
        }
        return ActionResult(result)

    def get_distribution_tenant_by_domain(self) -> ActionResult:
        return ActionResult({}, status_code=404)

    def get_connection_group_by_routing_endpoint(self) -> ActionResult:
        return ActionResult({}, status_code=404)
