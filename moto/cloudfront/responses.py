from typing import Any

import xmltodict

from moto.core.responses import (
    TYPE_RESPONSE,
    ActionResult,
    BaseResponse,
    EmptyResult,
)
from moto.core.utils import iso_8601_datetime_with_milliseconds

from .models import CloudFrontBackend, cloudfront_backends, random_id

XMLNS = "http://cloudfront.amazonaws.com/doc/2020-05-31/"


class CloudFrontResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="cloudfront")
        self.automated_parameter_parsing = True

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

    def _get_xml_body(self) -> dict[str, Any]:
        return xmltodict.parse(self.body, dict_constructor=dict, force_list="Path")

    @property
    def backend(self) -> CloudFrontBackend:
        return cloudfront_backends[self.current_account][self.partition]

    @classmethod
    def tagging(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        operation = response._get_param("Operation")
        if operation == "Tag":
            return 204, {}, response.tag_resource()[2]
        if operation == "Untag":
            return 204, {}, response.untag_resource()[2]
        if request.method == "GET":
            return 200, {}, response.list_tags_for_resource()[2]

    def create_distribution(self) -> ActionResult:
        distribution_config = self._get_param("DistributionConfig", {})
        distribution, location, e_tag = self.backend.create_distribution(
            distribution_config=distribution_config,
            tags=[],
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
        tags = self._get_param("Tags.Items", []) or []
        tags = {tag["Key"]: tag.get("Value") for tag in tags}
        self.backend.tag_resource(resource, tags)
        return EmptyResult()

    def untag_resource(self) -> ActionResult:
        resource = self._get_param("Resource")
        tag_keys_data = self._get_param("TagKeys.Items", []) or []
        self.backend.untag_resource(resource, tag_keys_data)
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

    def update_key_group(self) -> ActionResult:
        group_id = self._get_param("Id")
        name = self._get_param("KeyGroupConfig.Name")
        items = self._get_param("KeyGroupConfig.Items", [])
        key_group = self.backend.update_key_group(
            group_id=group_id, name=name, items=items
        )
        result = {"KeyGroup": key_group, "ETag": key_group.etag}
        return ActionResult(result)

    def delete_key_group(self) -> ActionResult:
        group_id = self._get_param("Id")
        self.backend.delete_key_group(group_id=group_id)
        return EmptyResult()

    # CloudFront Functions
    def create_function(self) -> ActionResult:
        params = self._get_xml_body().get("CreateFunctionRequest", {})
        params.pop("@xmlns", None)
        name = params.get("Name", "")
        function_code = params.get("FunctionCode", "")
        function_config = params.get("FunctionConfig", {})
        func = self.backend.create_function(
            name=name,
            function_code=function_code,
            function_config=function_config,
        )
        return ActionResult(
            {
                "FunctionSummary": func,
                "ETag": func.etag,
                "Location": f"https://cloudfront.amazonaws.com/2020-05-31/function/{func.name}",
            }
        )

    def describe_function(self) -> ActionResult:
        name = self.path.split("/")[-2]
        func = self.backend.describe_function(name)
        return ActionResult(
            {
                "FunctionSummary": func,
                "ETag": func.etag,
            }
        )

    def get_function(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-1]
        func = self.backend.get_function(name)
        headers = {"ETag": func.etag, "Content-Type": "application/octet-stream"}
        return 200, headers, func.function_code

    def update_function(self) -> ActionResult:
        name = self.path.split("/")[-1]
        if_match = self.headers.get("If-Match", "")
        params = self._get_xml_body().get("UpdateFunctionRequest", {})
        params.pop("@xmlns", None)
        function_code = params.get("FunctionCode", "")
        function_config = params.get("FunctionConfig", {})
        func = self.backend.update_function(
            name=name,
            function_code=function_code,
            function_config=function_config,
            if_match=if_match,
        )
        return ActionResult(
            {
                "FunctionSummary": func,
                "ETag": func.etag,
            }
        )

    def delete_function(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-1]
        if_match = self.headers.get("If-Match", "")
        self.backend.delete_function(name=name, if_match=if_match)
        return 204, {"status": 204}, ""

    def publish_function(self) -> ActionResult:
        name = self.path.split("/")[-2]
        if_match = self.headers.get("If-Match", "")
        func = self.backend.publish_function(name=name, if_match=if_match)
        return ActionResult(
            {
                "FunctionSummary": func,
            }
        )

    def list_functions(self) -> ActionResult:
        functions = self.backend.list_functions()
        return ActionResult(
            {
                "FunctionList": {
                    "Items": functions,
                    "Quantity": len(functions),
                    "MaxItems": 100,
                },
            }
        )

    # Cache Policies
    def create_cache_policy(self) -> ActionResult:
        config = self._get_xml_body().get("CachePolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.create_cache_policy(config)
        return ActionResult(
            {
                "CachePolicy": policy,
                "ETag": policy.etag,
                "Location": f"https://cloudfront.amazonaws.com/2020-05-31/cache-policy/{policy.id}",
            }
        )

    def get_cache_policy(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        policy = self.backend.get_cache_policy(policy_id)
        return ActionResult(
            {
                "CachePolicy": policy,
                "ETag": policy.etag,
            }
        )

    def update_cache_policy(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        config = self._get_xml_body().get("CachePolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.update_cache_policy(policy_id, config)
        return ActionResult(
            {
                "CachePolicy": policy,
                "ETag": policy.etag,
            }
        )

    def delete_cache_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        self.backend.delete_cache_policy(policy_id)
        return 204, {"status": 204}, ""

    def list_cache_policies(self) -> ActionResult:
        policies = self.backend.list_cache_policies()
        return ActionResult(
            {
                "CachePolicyList": {
                    "Items": policies,
                    "Quantity": len(policies),
                    "MaxItems": 100,
                },
            }
        )

    # Response Headers Policies
    def create_response_headers_policy(self) -> ActionResult:
        config = self._get_xml_body().get("ResponseHeadersPolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.create_response_headers_policy(config)
        return ActionResult(
            {
                "ResponseHeadersPolicy": policy,
                "ETag": policy.etag,
                "Location": "https://cloudfront.amazonaws.com/2020-05-31",
            }
        )

    def get_response_headers_policy(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        policy = self.backend.get_response_headers_policy(policy_id)
        return ActionResult(
            {
                "ResponseHeadersPolicy": policy,
                "ETag": policy.etag,
            }
        )

    def update_response_headers_policy(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        config = self._get_xml_body().get("ResponseHeadersPolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.update_response_headers_policy(policy_id, config)
        return ActionResult(
            {
                "ResponseHeadersPolicy": policy,
                "ETag": policy.etag,
            }
        )

    def delete_response_headers_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        self.backend.delete_response_headers_policy(policy_id)
        return 204, {"status": 204}, ""

    def list_response_headers_policies(self) -> ActionResult:
        policies = self.backend.list_response_headers_policies()
        return ActionResult(
            {
                "ResponseHeadersPolicyList": {
                    "Items": policies,
                    "Quantity": len(policies),
                    "MaxItems": 100,
                },
            }
        )

    # Origin Access Identities
    def create_cloud_front_origin_access_identity(self) -> ActionResult:
        params = self._get_xml_body()
        config = params.get("CloudFrontOriginAccessIdentityConfig", {})
        config.pop("@xmlns", None)
        caller_reference = config.get("CallerReference", "")
        comment = config.get("Comment", "")
        oai = self.backend.create_cloud_front_origin_access_identity(
            caller_reference=caller_reference, comment=comment
        )
        return ActionResult(
            {
                "CloudFrontOriginAccessIdentity": oai,
                "ETag": oai.etag,
                "Location": f"https://cloudfront.amazonaws.com/2020-05-31/origin-access-identity/cloudfront/{oai.id}",
            }
        )

    def get_cloud_front_origin_access_identity(self) -> ActionResult:
        identity_id = self.path.split("/")[-1]
        oai = self.backend.get_cloud_front_origin_access_identity(identity_id)
        return ActionResult(
            {
                "CloudFrontOriginAccessIdentity": oai,
                "ETag": oai.etag,
            }
        )

    def get_cloud_front_origin_access_identity_config(self) -> ActionResult:
        identity_id = self.path.split("/")[-2]
        oai = self.backend.get_cloud_front_origin_access_identity_config(identity_id)
        return ActionResult(
            {
                "CloudFrontOriginAccessIdentityConfig": oai,
                "ETag": oai.etag,
            }
        )

    def update_cloud_front_origin_access_identity(self) -> ActionResult:
        identity_id = self.path.split("/")[-2]
        params = self._get_xml_body()
        config = params.get("CloudFrontOriginAccessIdentityConfig", {})
        config.pop("@xmlns", None)
        oai = self.backend.update_cloud_front_origin_access_identity(
            identity_id, config.get("CallerReference", ""), config.get("Comment", "")
        )
        return ActionResult(
            {
                "CloudFrontOriginAccessIdentity": oai,
                "ETag": oai.etag,
            }
        )

    def delete_cloud_front_origin_access_identity(self) -> TYPE_RESPONSE:
        identity_id = self.path.split("/")[-1]
        self.backend.delete_cloud_front_origin_access_identity(identity_id)
        return 204, {"status": 204}, ""

    def list_cloud_front_origin_access_identities(self) -> ActionResult:
        oais = self.backend.list_cloud_front_origin_access_identities()
        return ActionResult(
            {
                "CloudFrontOriginAccessIdentityList": {
                    "Items": oais,
                    "Quantity": len(oais),
                    "MaxItems": 100,
                },
            }
        )

    # Streaming Distributions
    def create_streaming_distribution(self) -> ActionResult:
        params = self._get_xml_body()
        if "StreamingDistributionConfigWithTags" in params:
            wrapper = params["StreamingDistributionConfigWithTags"] or {}
            wrapper.pop("@xmlns", None)
            config = wrapper.get("StreamingDistributionConfig") or {}
            tags_items = (wrapper.get("Tags") or {}).get("Items") or {}
            tags = tags_items.get("Tag") or []
            if not isinstance(tags, list):
                tags = [tags]
        else:
            config = params.get("StreamingDistributionConfig") or {}
            tags = []
        config.pop("@xmlns", None)
        dist = self.backend.create_streaming_distribution(config, tags)
        return ActionResult(
            {
                "StreamingDistribution": dist,
                "ETag": dist.etag,
            }
        )

    def create_streaming_distribution_with_tags(self) -> TYPE_RESPONSE:
        return self.create_streaming_distribution()

    def get_streaming_distribution(self) -> ActionResult:
        dist_id = self.path.split("/")[-1]
        dist = self.backend.get_streaming_distribution(dist_id)
        return ActionResult(
            {
                "StreamingDistribution": dist,
                "ETag": dist.etag,
            }
        )

    def get_streaming_distribution_config(self) -> ActionResult:
        dist_id = self.path.split("/")[-2]
        dist = self.backend.get_streaming_distribution_config(dist_id)
        return ActionResult(
            {
                "StreamingDistributionConfig": dist,
                "ETag": dist.etag,
            }
        )

    def update_streaming_distribution(self) -> ActionResult:
        dist_id = self.path.split("/")[-2]
        params = self._get_xml_body()
        config = params.get("StreamingDistributionConfig", {})
        config.pop("@xmlns", None)
        dist = self.backend.update_streaming_distribution(dist_id, config)
        return ActionResult(
            {
                "StreamingDistribution": dist,
                "ETag": dist.etag,
            }
        )

    def delete_streaming_distribution(self) -> TYPE_RESPONSE:
        dist_id = self.path.split("/")[-1]
        self.backend.delete_streaming_distribution(dist_id)
        return 204, {"status": 204}, ""

    def list_streaming_distributions(self) -> ActionResult:
        dists = self.backend.list_streaming_distributions()
        return ActionResult(
            {
                "StreamingDistributionList": {
                    "Items": dists,
                    "Quantity": len(dists),
                    "MaxItems": 100,
                },
            }
        )

    # Origin Request Policies
    def create_origin_request_policy(self) -> ActionResult:
        config = self._get_xml_body().get("OriginRequestPolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.create_origin_request_policy(config)
        return ActionResult(
            {
                "OriginRequestPolicy": policy,
                "ETag": policy.etag,
                "Location": f"https://cloudfront.amazonaws.com/2020-05-31/origin-request-policy/{policy.id}",
            }
        )

    def get_origin_request_policy(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        policy = self.backend.get_origin_request_policy(policy_id)
        return ActionResult(
            {
                "OriginRequestPolicy": policy,
                "ETag": policy.etag,
            }
        )

    def get_origin_request_policy_config(self) -> ActionResult:
        policy_id = self.path.split("/")[-2]
        policy = self.backend.get_origin_request_policy_config(policy_id)
        return ActionResult(
            {
                "OriginRequestPolicyConfig": policy,
                "ETag": policy.etag,
            }
        )

    def update_origin_request_policy(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        config = self._get_xml_body().get("OriginRequestPolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.update_origin_request_policy(policy_id, config)
        return ActionResult(
            {
                "OriginRequestPolicy": policy,
                "ETag": policy.etag,
            }
        )

    def delete_origin_request_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        self.backend.delete_origin_request_policy(policy_id)
        return 204, {"status": 204}, ""

    def list_origin_request_policies(self) -> ActionResult:
        policies = self.backend.list_origin_request_policies()
        return ActionResult(
            {
                "OriginRequestPolicyList": {
                    "Items": policies,
                    "Quantity": len(policies),
                    "MaxItems": 100,
                },
            }
        )

    # Field Level Encryption
    def create_field_level_encryption_config(self) -> ActionResult:
        config = self._get_xml_body().get("FieldLevelEncryptionConfig", {})
        config.pop("@xmlns", None)
        fle = self.backend.create_field_level_encryption_config(config)
        return ActionResult(
            {
                "FieldLevelEncryption": fle,
                "ETag": fle.etag,
                "Location": f"https://cloudfront.amazonaws.com/2020-05-31/field-level-encryption/{fle.id}",
            }
        )

    def get_field_level_encryption(self) -> ActionResult:
        config_id = self.path.split("/")[-1]
        fle = self.backend.get_field_level_encryption(config_id)
        return ActionResult(
            {
                "FieldLevelEncryption": fle,
                "ETag": fle.etag,
            }
        )

    def get_field_level_encryption_config(self) -> ActionResult:
        config_id = self.path.split("/")[-2]
        fle = self.backend.get_field_level_encryption_config(config_id)
        return ActionResult(
            {
                "FieldLevelEncryptionConfig": fle,
                "ETag": fle.etag,
            }
        )

    def update_field_level_encryption_config(self) -> ActionResult:
        config_id = self.path.split("/")[-2]
        config = self._get_xml_body().get("FieldLevelEncryptionConfig", {})
        config.pop("@xmlns", None)
        fle = self.backend.update_field_level_encryption_config(config_id, config)
        return ActionResult(
            {
                "FieldLevelEncryption": fle,
                "ETag": fle.etag,
            }
        )

    def delete_field_level_encryption_config(self) -> TYPE_RESPONSE:
        config_id = self.path.split("/")[-1]
        self.backend.delete_field_level_encryption_config(config_id)
        return 204, {"status": 204}, ""

    def list_field_level_encryption_configs(self) -> ActionResult:
        configs = self.backend.list_field_level_encryption_configs()
        return ActionResult(
            {
                "FieldLevelEncryptionList": {
                    "Items": configs,
                    "Quantity": len(configs),
                    "MaxItems": 100,
                },
            }
        )

    # Field Level Encryption Profiles
    def create_field_level_encryption_profile(self) -> ActionResult:
        config = self._get_xml_body().get("FieldLevelEncryptionProfileConfig", {})
        config.pop("@xmlns", None)
        profile = self.backend.create_field_level_encryption_profile(config)
        return ActionResult(
            {
                "FieldLevelEncryptionProfile": profile,
                "ETag": profile.etag,
                "Location": f"https://cloudfront.amazonaws.com/2020-05-31/field-level-encryption-profile/{profile.id}",
            }
        )

    def get_field_level_encryption_profile(self) -> ActionResult:
        profile_id = self.path.split("/")[-1]
        profile = self.backend.get_field_level_encryption_profile(profile_id)
        return ActionResult(
            {
                "FieldLevelEncryptionProfile": profile,
                "ETag": profile.etag,
            }
        )

    def get_field_level_encryption_profile_config(self) -> ActionResult:
        profile_id = self.path.split("/")[-2]
        profile = self.backend.get_field_level_encryption_profile_config(profile_id)
        return ActionResult(
            {
                "FieldLevelEncryptionProfileConfig": profile,
                "ETag": profile.etag,
            }
        )

    def update_field_level_encryption_profile(self) -> ActionResult:
        profile_id = self.path.split("/")[-2]
        config = self._get_xml_body().get("FieldLevelEncryptionProfileConfig", {})
        config.pop("@xmlns", None)
        profile = self.backend.update_field_level_encryption_profile(profile_id, config)
        return ActionResult(
            {
                "FieldLevelEncryptionProfile": profile,
                "ETag": profile.etag,
            }
        )

    def delete_field_level_encryption_profile(self) -> TYPE_RESPONSE:
        profile_id = self.path.split("/")[-1]
        self.backend.delete_field_level_encryption_profile(profile_id)
        return 204, {"status": 204}, ""

    def list_field_level_encryption_profiles(self) -> ActionResult:
        profiles = self.backend.list_field_level_encryption_profiles()
        return ActionResult(
            {
                "FieldLevelEncryptionProfileList": {
                    "Items": profiles,
                    "Quantity": len(profiles),
                    "MaxItems": 100,
                },
            }
        )

    # Continuous Deployment Policies
    def create_continuous_deployment_policy(self) -> ActionResult:
        config = self._get_xml_body().get("ContinuousDeploymentPolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.create_continuous_deployment_policy(config)
        return ActionResult(
            {
                "ContinuousDeploymentPolicy": policy,
                "ETag": policy.etag,
                "Location": f"https://cloudfront.amazonaws.com/2020-05-31/continuous-deployment-policy/{policy.id}",
            }
        )

    def get_continuous_deployment_policy(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        policy = self.backend.get_continuous_deployment_policy(policy_id)
        return ActionResult(
            {
                "ContinuousDeploymentPolicy": policy,
                "ETag": policy.etag,
            }
        )

    def get_continuous_deployment_policy_config(self) -> ActionResult:
        policy_id = self.path.split("/")[-2]
        policy = self.backend.get_continuous_deployment_policy_config(policy_id)
        return ActionResult(
            {
                "ContinuousDeploymentPolicyConfig": policy,
                "ETag": policy.etag,
            }
        )

    def update_continuous_deployment_policy(self) -> ActionResult:
        policy_id = self.path.split("/")[-2]
        config = self._get_xml_body().get("ContinuousDeploymentPolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.update_continuous_deployment_policy(policy_id, config)
        return ActionResult(
            {
                "ContinuousDeploymentPolicy": policy,
                "ETag": policy.etag,
            }
        )

    def delete_continuous_deployment_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        self.backend.delete_continuous_deployment_policy(policy_id)
        return 204, {"status": 204}, ""

    def list_continuous_deployment_policies(self) -> ActionResult:
        policies = self.backend.list_continuous_deployment_policies()
        return ActionResult(
            {
                "ContinuousDeploymentPolicyList": {
                    "Items": policies,
                    "Quantity": len(policies),
                    "MaxItems": 100,
                },
            }
        )

    # Monitoring Subscriptions
    def create_monitoring_subscription(self) -> ActionResult:
        dist_id = self.path.split("/")[-2]
        params = self._get_xml_body()
        ms_config = params.get("MonitoringSubscription", {})
        ms_config.pop("@xmlns", None)
        realtime_config = ms_config.get("RealtimeMetricsSubscriptionConfig", {})
        sub = self.backend.create_monitoring_subscription(dist_id, realtime_config)
        return ActionResult(
            {
                "MonitoringSubscription": sub,
            }
        )

    def get_monitoring_subscription(self) -> ActionResult:
        dist_id = self.path.split("/")[-2]
        sub = self.backend.get_monitoring_subscription(dist_id)
        return ActionResult(
            {
                "MonitoringSubscription": sub,
            }
        )

    def delete_monitoring_subscription(self) -> TYPE_RESPONSE:
        dist_id = self.path.split("/")[-2]
        self.backend.delete_monitoring_subscription(dist_id)
        return 200, {}, ""

    # Realtime Log Configs
    def _parse_realtime_body(self) -> dict[str, Any]:
        """Parse body as XML (botocore sends XML for CloudFront rest-xml protocol)."""
        body = self._get_xml_body()
        # Unwrap the request wrapper element if present
        for key in (
            "CreateRealtimeLogConfigRequest",
            "UpdateRealtimeLogConfigRequest",
            "GetRealtimeLogConfigRequest",
            "DeleteRealtimeLogConfigRequest",
        ):
            if key in body:
                body = body[key] or {}
                break
        body.pop("@xmlns", None)
        return body

    @staticmethod
    def _extract_endpoints(body: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract EndPoints from parsed XML body."""
        eps_raw = (body.get("EndPoints") or {}).get("member") or []
        if isinstance(eps_raw, dict):
            eps_raw = [eps_raw]
        end_points = []
        for ep in eps_raw:
            entry: dict[str, Any] = {"StreamType": ep.get("StreamType", "Kinesis")}
            kinesis = ep.get("KinesisStreamConfig") or {}
            if kinesis:
                entry["KinesisStreamConfig"] = {
                    "RoleARN": kinesis.get("RoleARN", ""),
                    "StreamARN": kinesis.get("StreamARN", ""),
                }
            end_points.append(entry)
        return end_points

    @staticmethod
    def _extract_fields(body: dict[str, Any]) -> list[str]:
        """Extract Fields from parsed XML body."""
        fields_raw = (body.get("Fields") or {}).get("Field") or []
        if isinstance(fields_raw, str):
            fields_raw = [fields_raw]
        return fields_raw

    def create_realtime_log_config(self) -> ActionResult:
        body = self._parse_realtime_body()
        name = body.get("Name", "")
        sampling_rate = int(body.get("SamplingRate", 100))
        end_points = self._extract_endpoints(body)
        fields = self._extract_fields(body)
        config = self.backend.create_realtime_log_config(
            name=name,
            sampling_rate=sampling_rate,
            end_points=end_points,
            fields=fields,
        )
        return ActionResult(
            {
                "RealtimeLogConfig": config,
            }
        )

    def get_realtime_log_config(self) -> ActionResult:
        body = self._parse_realtime_body() if self.body else {}
        config = self.backend.get_realtime_log_config(
            name=body.get("Name"), arn=body.get("ARN")
        )
        return ActionResult(
            {
                "RealtimeLogConfig": config,
            }
        )

    def update_realtime_log_config(self) -> ActionResult:
        body = self._parse_realtime_body() if self.body else {}
        sr = body.get("SamplingRate")
        end_points = self._extract_endpoints(body) if "EndPoints" in body else None
        fields = self._extract_fields(body) if "Fields" in body else None
        config = self.backend.update_realtime_log_config(
            name=body.get("Name"),
            arn=body.get("ARN"),
            sampling_rate=int(sr) if sr is not None else None,
            end_points=end_points,
            fields=fields,
        )
        return ActionResult(
            {
                "RealtimeLogConfig": config,
            }
        )

    def delete_realtime_log_config(self) -> TYPE_RESPONSE:
        body = self._parse_realtime_body() if self.body else {}
        self.backend.delete_realtime_log_config(
            name=body.get("Name"), arn=body.get("ARN")
        )
        return 204, {"status": 204}, ""

    def list_realtime_log_configs(self) -> ActionResult:
        configs = self.backend.list_realtime_log_configs()
        return ActionResult(
            {
                "RealtimeLogConfigs": {
                    "Items": configs,
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                },
            }
        )

    # Distribution query operations
    def list_distributions_by_web_acl_id(self) -> ActionResult:
        web_acl_id = self.path.split("/")[-1]
        distributions = self.backend.list_distributions_by_web_acl_id(web_acl_id)
        return ActionResult(
            {
                "DistributionList": {
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                    "Quantity": len(distributions),
                    "Items": distributions if distributions else None,
                },
            }
        )

    def list_distributions_by_web_a_c_l_id(self) -> TYPE_RESPONSE:
        return self.list_distributions_by_web_acl_id()

    def list_distributions_by_cache_policy_id(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        dist_ids = self.backend.list_distributions_by_cache_policy_id(policy_id)
        return ActionResult(
            {
                "DistributionIdList": {
                    "Items": dist_ids,
                    "Quantity": len(dist_ids),
                    "MaxItems": 100,
                },
            }
        )

    def list_distributions_by_origin_request_policy_id(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        dist_ids = self.backend.list_distributions_by_origin_request_policy_id(
            policy_id
        )
        return ActionResult(
            {
                "DistributionIdList": {
                    "Items": dist_ids,
                    "Quantity": len(dist_ids),
                    "MaxItems": 100,
                },
            }
        )

    def list_distributions_by_response_headers_policy_id(self) -> ActionResult:
        policy_id = self.path.split("/")[-1]
        dist_ids = self.backend.list_distributions_by_response_headers_policy_id(
            policy_id
        )
        return ActionResult(
            {
                "DistributionIdList": {
                    "Items": dist_ids,
                    "Quantity": len(dist_ids),
                    "MaxItems": 100,
                },
            }
        )

    def list_distributions_by_key_group(self) -> ActionResult:
        key_group_id = self.path.split("/")[-1]
        dist_ids = self.backend.list_distributions_by_key_group(key_group_id)
        return ActionResult(
            {
                "DistributionIdList": {
                    "Items": dist_ids,
                    "Quantity": len(dist_ids),
                    "MaxItems": 100,
                },
            }
        )

    def list_distributions_by_realtime_log_config(self) -> ActionResult:
        body = self._parse_realtime_body() if self.body else {}
        distributions = self.backend.list_distributions_by_realtime_log_config(
            body.get("RealtimeLogConfigArn", "")
        )
        return ActionResult(
            {
                "DistributionList": {
                    "Items": distributions,
                    "Quantity": len(distributions),
                    "MaxItems": 100,
                },
            }
        )

    # Config-only getters
    def get_cache_policy_config(self) -> ActionResult:
        policy_id = self.path.split("/")[-2]
        policy = self.backend.get_cache_policy_config(policy_id)
        return ActionResult(
            {
                "CachePolicyConfig": policy,
                "ETag": policy.etag,
            }
        )

    def get_key_group_config(self) -> ActionResult:
        group_id = self.path.split("/")[-2]
        group = self.backend.get_key_group_config(group_id)
        return ActionResult(
            {
                "KeyGroupConfig": group,
                "ETag": group.etag,
            }
        )

    def get_origin_access_control_config(self) -> ActionResult:
        control_id = self.path.split("/")[-2]
        control = self.backend.get_origin_access_control_config(control_id)
        return ActionResult(
            {
                "OriginAccessControlConfig": control,
                "ETag": control.etag,
            }
        )

    def get_public_key_config(self) -> ActionResult:
        key_id = self.path.split("/")[-2]
        key = self.backend.get_public_key_config(key_id)
        return ActionResult(
            {
                "PublicKeyConfig": key,
                "ETag": key.etag,
            }
        )

    def get_response_headers_policy_config(self) -> ActionResult:
        policy_id = self.path.split("/")[-2]
        policy = self.backend.get_response_headers_policy_config(policy_id)
        return ActionResult(
            {
                "ResponseHeadersPolicyConfig": policy,
                "ETag": policy.etag,
            }
        )

    def update_public_key(self) -> ActionResult:
        key_id = self.path.split("/")[-2]
        key = self.backend.update_public_key(key_id)
        return ActionResult(
            {
                "PublicKey": key,
                "ETag": key.etag,
            }
        )

    # Alias operations
    def associate_alias(self) -> TYPE_RESPONSE:
        dist_id = self.path.split("/")[-2]
        alias = self._get_param("Alias")
        self.backend.associate_alias(dist_id, alias)
        return 200, {}, ""

    def test_function(self) -> ActionResult:
        name = self.path.split("/")[-2]
        result = self.backend.test_function(name, event_object="")
        return ActionResult(
            {
                "TestResult": result,
            }
        )

    def list_conflicting_aliases(self) -> ActionResult:
        dist_id = self._get_param("DistributionId")
        alias = self._get_param("Alias")
        items = self.backend.list_conflicting_aliases(dist_id, alias)
        return ActionResult(
            {
                "ConflictingAliasesList": {
                    "Items": items,
                    "Quantity": len(items),
                    "MaxItems": 100,
                },
            }
        )

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

    # Stub operations for newer/niche APIs
    def associate_distribution_web_acl(self) -> TYPE_RESPONSE:
        return 200, {}, ""

    # Alias for Moto dispatch compatibility
    associate_distribution_web_a_c_l = associate_distribution_web_acl

    def disassociate_distribution_web_acl(self) -> TYPE_RESPONSE:
        return 200, {}, ""

    disassociate_distribution_web_a_c_l = disassociate_distribution_web_acl

    def associate_distribution_tenant_web_acl(self) -> TYPE_RESPONSE:
        return 200, {}, ""

    associate_distribution_tenant_web_a_c_l = associate_distribution_tenant_web_acl

    def disassociate_distribution_tenant_web_acl(self) -> TYPE_RESPONSE:
        return 200, {}, ""

    disassociate_distribution_tenant_web_a_c_l = (
        disassociate_distribution_tenant_web_acl
    )

    def create_key_value_store(self) -> ActionResult:
        body = self._get_xml_body()
        req = body.get("CreateKeyValueStoreRequest") or body
        if isinstance(req, dict):
            req.pop("@xmlns", None)
        else:
            req = {}
        name = req.get("Name", "")
        comment = req.get("Comment", "")
        kvs = self.backend.create_key_value_store(name=name, comment=comment)
        return ActionResult(
            {
                "KeyValueStore": kvs,
                "ETag": kvs.etag,
                "Location": f"https://cloudfront.amazonaws.com/2020-05-31/key-value-store/{name}",
            }
        )

    def describe_key_value_store(self) -> ActionResult:
        name = self.path.split("/")[-1]
        kvs = self.backend.describe_key_value_store(name)
        return ActionResult(
            {
                "KeyValueStore": kvs,
                "ETag": kvs.etag,
            }
        )

    def delete_key_value_store(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-1]
        self.backend.delete_key_value_store(name)
        return 204, {"status": 204}, ""

    def update_key_value_store(self) -> ActionResult:
        name = self.path.split("/")[-1]
        body = self._get_xml_body()
        req = body.get("UpdateKeyValueStoreRequest") or body
        if isinstance(req, dict):
            req.pop("@xmlns", None)
        else:
            req = {}
        comment = req.get("Comment", "")
        kvs = self.backend.update_key_value_store(name=name, comment=comment)
        return ActionResult(
            {
                "KeyValueStore": kvs,
                "ETag": kvs.etag,
            }
        )

    def list_key_value_stores(self) -> ActionResult:
        stores = self.backend.list_key_value_stores()
        return ActionResult(
            {
                "KeyValueStoreList": {
                    "Items": stores,
                    "Quantity": len(stores),
                    "MaxItems": 100,
                },
            }
        )

    # VPC Origins
    def create_vpc_origin(self) -> ActionResult:
        params = self._get_xml_body()
        root = params.get("CreateVpcOriginRequest", params)
        config = root.get("VpcOriginEndpointConfig", {})
        config.pop("@xmlns", None)
        vo = self.backend.create_vpc_origin(config)
        return ActionResult(
            {
                "VpcOrigin": vo,
                "ETag": vo.etag,
            }
        )

    def get_vpc_origin(self) -> ActionResult:
        vpc_id = self.path.split("/")[-1]
        vo = self.backend.get_vpc_origin(vpc_id)
        return ActionResult(
            {
                "VpcOrigin": vo,
                "ETag": vo.etag,
            }
        )

    def delete_vpc_origin(self) -> TYPE_RESPONSE:
        vpc_id = self.path.split("/")[-1]
        self.backend.delete_vpc_origin(vpc_id)
        return 202, {"status": 202}, ""

    def update_vpc_origin(self) -> ActionResult:
        vpc_id = self.path.split("/")[-1]
        params = self._get_xml_body()
        root = params.get("UpdateVpcOriginRequest", params)
        config = root.get("VpcOriginEndpointConfig", {})
        config.pop("@xmlns", None)
        vo = self.backend.update_vpc_origin(vpc_id, config)
        return ActionResult(
            {
                "VpcOrigin": vo,
                "ETag": vo.etag,
            }
        )

    def list_vpc_origins(self) -> ActionResult:
        origins = self.backend.list_vpc_origins()
        return ActionResult(
            {
                "VpcOriginList": {
                    "Items": origins,
                    "Quantity": len(origins),
                    "MaxItems": 100,
                },
            }
        )

    # Trust Stores
    def create_trust_store(self) -> ActionResult:
        params = self._get_xml_body()
        root = params.get("CreateTrustStoreRequest", params)
        root.pop("@xmlns", None)
        name = root.get("Name", "")
        ts = self.backend.create_trust_store(name)
        return ActionResult(
            {
                "TrustStore": ts,
                "ETag": ts.etag,
            }
        )

    def get_trust_store(self) -> ActionResult:
        store_id = self.path.split("/")[-1]
        ts = self.backend.get_trust_store(store_id)
        return ActionResult(
            {
                "TrustStore": ts,
                "ETag": ts.etag,
            }
        )

    def delete_trust_store(self) -> TYPE_RESPONSE:
        store_id = self.path.split("/")[-1]
        self.backend.delete_trust_store(store_id)
        return 204, {"status": 204}, ""

    def update_trust_store(self) -> ActionResult:
        store_id = self.path.split("/")[-1]
        ts = self.backend.update_trust_store(store_id)
        return ActionResult(
            {
                "TrustStore": ts,
                "ETag": ts.etag,
            }
        )

    def list_trust_stores(self) -> ActionResult:
        stores = self.backend.list_trust_stores()
        return ActionResult(
            {
                "TrustStoreList": stores,
            }
        )

    # Resource Policy
    def get_resource_policy(self) -> ActionResult:
        return ActionResult({"ResourceArn": "", "PolicyDocument": ""})

    def put_resource_policy(self) -> ActionResult:
        return ActionResult(
            {
                "ResourceArn": "",
            }
        )

    def delete_resource_policy(self) -> TYPE_RESPONSE:
        return 204, {"status": 204}, ""

    # Anycast IP Lists
    def create_anycast_ip_list(self) -> ActionResult:
        params = self._get_xml_body()
        root = params.get("CreateAnycastIpListRequest", params)
        root.pop("@xmlns", None)
        name = root.get("Name", "")
        aip = self.backend.create_anycast_ip_list(name)
        return ActionResult(
            {
                "AnycastIpList": aip,
                "ETag": aip.etag,
            }
        )

    def get_anycast_ip_list(self) -> ActionResult:
        list_id = self.path.split("/")[-1]
        aip = self.backend.get_anycast_ip_list(list_id)
        return ActionResult(
            {
                "AnycastIpList": aip,
                "ETag": aip.etag,
            }
        )

    def delete_anycast_ip_list(self) -> TYPE_RESPONSE:
        list_id = self.path.split("/")[-1]
        self.backend.delete_anycast_ip_list(list_id)
        return 204, {"status": 204}, ""

    def update_anycast_ip_list(self) -> TYPE_RESPONSE:
        return self.get_anycast_ip_list()

    def list_anycast_ip_lists(self) -> ActionResult:
        lists = self.backend.list_anycast_ip_lists()
        return ActionResult(
            {
                "AnycastIpLists": {
                    "Items": lists,
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                    "Quantity": len(lists),
                },
            }
        )

    # Connection Groups
    def create_connection_group(self) -> ActionResult:
        params = self._get_xml_body()
        root = params.get("CreateConnectionGroupRequest", params)
        root.pop("@xmlns", None)
        name = root.get("Name", "")
        cg = self.backend.create_connection_group(name)
        return ActionResult(
            {
                "ConnectionGroup": cg,
                "ETag": cg.etag,
            }
        )

    def get_connection_group(self) -> ActionResult:
        cg_id = self.path.split("/")[-1]
        cg = self.backend.get_connection_group(cg_id)
        return ActionResult(
            {
                "ConnectionGroup": cg,
                "ETag": cg.etag,
            }
        )

    def delete_connection_group(self) -> TYPE_RESPONSE:
        cg_id = self.path.split("/")[-1]
        self.backend.delete_connection_group(cg_id)
        return 204, {"status": 204}, ""

    def update_connection_group(self) -> ActionResult:
        cg_id = self.path.split("/")[-1]
        cg = self.backend.get_connection_group(cg_id)
        cg.etag = random_id(length=14)
        return ActionResult(
            {
                "ConnectionGroup": cg,
                "ETag": cg.etag,
            }
        )

    def list_connection_groups(self) -> ActionResult:
        groups = self.backend.list_connection_groups()
        return ActionResult(
            {
                "ConnectionGroups": groups,
            }
        )

    def get_connection_group_by_routing_endpoint(self) -> ActionResult:
        return ActionResult(
            {
                "ConnectionGroup": {},
            }
        )

    # Distribution Tenants
    def create_distribution_tenant(self) -> ActionResult:
        params = self._get_xml_body()
        root = params.get("CreateDistributionTenantRequest", params)
        root.pop("@xmlns", None)
        name = root.get("Name", "")
        dist_id = root.get("DistributionId", "")
        dt = self.backend.create_distribution_tenant(name, dist_id)
        return ActionResult(
            {
                "DistributionTenant": dt,
                "ETag": dt.etag,
            }
        )

    def get_distribution_tenant(self) -> ActionResult:
        dt_id = self.path.split("/")[-1]
        dt = self.backend.get_distribution_tenant(dt_id)
        return ActionResult(
            {
                "DistributionTenant": dt,
                "ETag": dt.etag,
            }
        )

    def delete_distribution_tenant(self) -> TYPE_RESPONSE:
        dt_id = self.path.split("/")[-1]
        self.backend.delete_distribution_tenant(dt_id)
        return 204, {"status": 204}, ""

    def update_distribution_tenant(self) -> ActionResult:
        dt_id = self.path.split("/")[-1]
        dt = self.backend.get_distribution_tenant(dt_id)
        dt.etag = random_id(length=14)
        return ActionResult(
            {
                "DistributionTenant": dt,
                "ETag": dt.etag,
            }
        )

    def list_distribution_tenants(self) -> ActionResult:
        tenants = self.backend.list_distribution_tenants()
        return ActionResult(
            {
                "DistributionTenantList": tenants,
            }
        )

    def get_distribution_tenant_by_domain(self) -> ActionResult:
        return ActionResult(
            {
                "DistributionTenant": {},
            }
        )

    def list_distribution_tenants_by_customization(self) -> ActionResult:
        return ActionResult(
            {
                "NextMarker": "",
                "DistributionTenantList": [],
            }
        )

    def create_invalidation_for_distribution_tenant(self) -> ActionResult:
        inv_id = random_id()
        # Invalidation is a structure, not a bare id.
        return ActionResult(
            {
                "Invalidation": self._tenant_invalidation(inv_id),
                "Location": (
                    "https://cloudfront.amazonaws.com/2020-05-31/distribution-tenant/"
                    f"{self.path.split('/')[-2]}/invalidation/{inv_id}"
                ),
            }
        )

    def get_invalidation_for_distribution_tenant(self) -> ActionResult:
        inv_id = self.path.split("/")[-1]
        return ActionResult({"Invalidation": self._tenant_invalidation(inv_id)})

    @staticmethod
    def _tenant_invalidation(inv_id: str) -> dict[str, Any]:
        """Every member of the Invalidation shape is required."""
        return {
            "Id": inv_id,
            "Status": "Completed",
            "CreateTime": iso_8601_datetime_with_milliseconds(),
            "InvalidationBatch": {
                "Paths": {"Quantity": 0, "Items": None},
                "CallerReference": inv_id,
            },
        }

    def list_invalidations_for_distribution_tenant(self) -> ActionResult:
        return ActionResult(
            {
                "InvalidationList": {"Items": [], "Quantity": 0, "MaxItems": 100},
            }
        )

    # Connection Functions
    def create_connection_function(self) -> ActionResult:
        params = self._get_xml_body()
        root = params.get("CreateConnectionFunctionRequest", params)
        root.pop("@xmlns", None)
        name = root.get("Name", "")
        cf = self.backend.create_connection_function(name)
        return ActionResult(
            {
                "ConnectionFunctionSummary": cf,
                "ETag": cf.etag,
            }
        )

    def get_connection_function(self) -> ActionResult:
        name = self.path.split("/")[-1]
        cf = self.backend.get_connection_function(name)
        return ActionResult(
            {
                "ConnectionFunctionCode": b"",
                "ETag": cf.etag,
                "ContentType": "application/octet-stream",
            }
        )

    def describe_connection_function(self) -> ActionResult:
        name = self.path.split("/")[-2]
        cf = self.backend.get_connection_function(name)
        return ActionResult(
            {
                "ConnectionFunctionSummary": cf,
                "ETag": cf.etag,
            }
        )

    def delete_connection_function(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-1]
        self.backend.delete_connection_function(name)
        return 204, {"status": 204}, ""

    def update_connection_function(self) -> ActionResult:
        name = self.path.split("/")[-1]
        cf = self.backend.get_connection_function(name)
        cf.etag = random_id(length=14)
        return ActionResult(
            {
                "ConnectionFunctionSummary": cf,
                "ETag": cf.etag,
            }
        )

    def publish_connection_function(self) -> ActionResult:
        name = self.path.split("/")[-2]
        cf = self.backend.get_connection_function(name)
        cf.stage = "LIVE"
        cf.etag = random_id(length=14)
        return ActionResult(
            {
                "ConnectionFunctionSummary": cf,
            }
        )

    def test_connection_function(self) -> ActionResult:
        name = self.path.split("/")[-2]
        return ActionResult(
            {
                "ConnectionFunctionTestResult": {
                    "ConnectionFunctionSummary": {
                        "Name": name,
                        "Status": "UNASSOCIATED",
                    },
                    "ComputeUtilization": "12",
                    "ConnectionFunctionExecutionLogs": [],
                    "ConnectionFunctionErrorMessage": "",
                    "ConnectionFunctionOutput": '{"response":{"statusCode":200}}',
                },
            }
        )

    def list_connection_functions(self) -> ActionResult:
        funcs = self.backend.list_connection_functions()
        return ActionResult(
            {
                "ConnectionFunctions": funcs,
            }
        )

    def copy_distribution(self) -> TYPE_RESPONSE:
        return self.get_distribution()

    def list_distributions_by_anycast_ip_list_id(self) -> ActionResult:
        return ActionResult(
            {
                "DistributionList": {
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                    "Quantity": 0,
                    "Items": None,
                },
            }
        )

    def list_distributions_by_connection_function(self) -> ActionResult:
        return ActionResult(
            {
                "DistributionList": {
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                    "Quantity": 0,
                    "Items": None,
                },
            }
        )

    def list_distributions_by_connection_mode(self) -> ActionResult:
        return ActionResult(
            {
                "DistributionList": {
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                    "Quantity": 0,
                    "Items": None,
                },
            }
        )

    def list_distributions_by_owned_resource(self) -> ActionResult:
        return ActionResult(
            {
                "DistributionList": {
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                    "Quantity": 0,
                    "Items": None,
                },
            }
        )

    def list_distributions_by_trust_store(self) -> ActionResult:
        return ActionResult(
            {
                "DistributionList": {
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                    "Quantity": 0,
                    "Items": None,
                },
            }
        )

    def list_distributions_by_vpc_origin_id(self) -> ActionResult:
        return ActionResult(
            {
                "DistributionIdList": {
                    "Marker": "",
                    "MaxItems": 100,
                    "IsTruncated": False,
                    "Quantity": 0,
                    "Items": None,
                },
            }
        )

    def list_domain_conflicts(self) -> ActionResult:
        return ActionResult(
            {
                "DomainConflicts": [],
                "NextMarker": "",
            }
        )

    def update_distribution_with_staging_config(self) -> ActionResult:
        dist_id = self.path.split("/")[-2]
        dist, etag = self.backend.get_distribution(dist_id)
        return ActionResult(
            {
                "Distribution": dist,
            }
        )

    def update_domain_association(self) -> TYPE_RESPONSE:
        return 200, {}, ""

    def get_managed_certificate_details(self) -> ActionResult:
        identifier = self.path.split("/")[-1]
        return ActionResult(
            {
                "ManagedCertificateDetails": {
                    "CertificateArn": (
                        f"arn:aws:acm:us-east-1:{self.current_account}:certificate/{identifier}"
                    ),
                    "CertificateStatus": "issued",
                    "ValidationTokenHost": "cloudfront",
                    "ValidationTokenDetails": [],
                },
            }
        )

    def verify_dns_configuration(self) -> ActionResult:
        return ActionResult(
            {
                "DnsConfigurationList": [],
            }
        )


DIST_META_TEMPLATE = """
    <Id>{{ distribution.distribution_id }}</Id>
    <ARN>{{ distribution.arn }}</ARN>
    <Status>{{ distribution.status }}</Status>
    <LastModifiedTime>{{ distribution.last_modified_time }}</LastModifiedTime>
    <InProgressInvalidationBatches>{{ distribution.in_progress_invalidation_batches }}</InProgressInvalidationBatches>
    <DomainName>{{ distribution.domain_name }}</DomainName>
"""


DIST_CONFIG_TEMPLATE = """
      <CallerReference>{{ distribution.distribution_config.caller_reference }}</CallerReference>
      <Aliases>
        <Quantity>{{ distribution.distribution_config.aliases|length }}</Quantity>
        <Items>
          {% for alias  in distribution.distribution_config.aliases %}
            <CNAME>{{ alias }}</CNAME>
          {% endfor %}
        </Items>
      </Aliases>
      <DefaultRootObject>{{ distribution.distribution_config.default_root_object }}</DefaultRootObject>
      <Origins>
        <Quantity>{{ distribution.distribution_config.origins|length }}</Quantity>
        <Items>
          {% for origin  in distribution.distribution_config.origins %}
          <Origin>
            <Id>{{ origin.id }}</Id>
            <DomainName>{{ origin.domain_name }}</DomainName>
            <OriginPath>{{ origin.origin_path }}</OriginPath>
            <CustomHeaders>
              <Quantity>{{ origin.custom_headers|length }}</Quantity>
              <Items>
                {% for header  in origin.custom_headers %}
                  <OriginCustomHeader>
                  <HeaderName>{{ header['HeaderName'] }}</HeaderName>
                  <HeaderValue>{{ header['HeaderValue'] }}</HeaderValue>
                  </OriginCustomHeader>
                {% endfor %}
              </Items>
            </CustomHeaders>
            {% if origin.s3_access_identity %}
            <S3OriginConfig>
              <OriginAccessIdentity>{{ origin.s3_access_identity }}</OriginAccessIdentity>
            </S3OriginConfig>
            {% endif %}
            {% if origin.custom_origin %}
            <CustomOriginConfig>
              <HTTPPort>{{ origin.custom_origin.http_port }}</HTTPPort>
              <HTTPSPort>{{ origin.custom_origin.https_port }}</HTTPSPort>
              <OriginProtocolPolicy>{{ origin.custom_origin.protocol_policy }}</OriginProtocolPolicy>
              <OriginSslProtocols>
                <Quantity>{{ origin.custom_origin.ssl_protocols|length }}</Quantity>
                <Items>
                  {% for protocol  in origin.custom_origin.ssl_protocols %}
                  <SslProtocol>{{ protocol }}</SslProtocol>
                  {% endfor %}
                </Items>
              </OriginSslProtocols>
              <OriginReadTimeout>{{ origin.custom_origin.read_timeout }}</OriginReadTimeout>
              <OriginKeepaliveTimeout>{{ origin.custom_origin.keep_alive }}</OriginKeepaliveTimeout>
            </CustomOriginConfig>
            {% endif %}
            <ConnectionAttempts>{{ origin.connection_attempts }}</ConnectionAttempts>
            <ConnectionTimeout>{{ origin.connection_timeout }}</ConnectionTimeout>
            {% if origin.origin_shield %}
            <OriginShield>
              <Enabled>{{ origin.origin_shield.get("Enabled") }}</Enabled>
              <OriginShieldRegion>{{ origin.origin_shield.get("OriginShieldRegion") }}</OriginShieldRegion>
            </OriginShield>
            {% else %}
            <OriginShield>
              <Enabled>false</Enabled>
            </OriginShield>
            {% endif %}
            </Origin>
          {% endfor %}
        </Items>
      </Origins>
      <OriginGroups>
        <Quantity>{{ distribution.distribution_config.origin_groups|length }}</Quantity>
        {% if distribution.distribution_config.origin_groups %}
        <Items>
          {% for origin_group  in distribution.distribution_config.origin_groups %}
            <Id>{{ origin_group.id }}</Id>
            <FailoverCriteria>
              <StatusCodes>
                <Quantity>{{ origin_group.failover_criteria.status_codes.quantity }}</Quantity>
                <Items>
                  {% for status_code_list  in origin_group_list.failover_criteria.status_codes.StatusCodeList %}
                    <StatusCode>{{ status_code_list.status_code }}</StatusCode>
                  {% endfor %}
                </Items>
              </StatusCodes>
            </FailoverCriteria>
            <Members>
              <Quantity>{{ origin_group.members.quantity }}</Quantity>
              <Items>
                {% for origin_group_member_list  in origin_group.members.OriginGroupMemberList %}
                  <OriginId>{{ origin_group_member_list.origin_id }}</OriginId>
                {% endfor %}
              </Items>
            </Members>
          {% endfor %}
        </Items>
        {% endif %}
      </OriginGroups>
      <DefaultCacheBehavior>
        <TargetOriginId>{{ distribution.distribution_config.default_cache_behavior.target_origin_id }}</TargetOriginId>
        <TrustedSigners>
          <Enabled>{{ 'true' if distribution.distribution_config.default_cache_behavior.trusted_signers.acct_nums|length > 0 else 'false' }}</Enabled>
          <Quantity>{{ distribution.distribution_config.default_cache_behavior.trusted_signers.acct_nums|length }}</Quantity>
          <Items>
            {% for aws_account_number  in distribution.distribution_config.default_cache_behavior.trusted_signers.acct_nums %}
              <AwsAccountNumber>{{ aws_account_number }}</AwsAccountNumber>
            {% endfor %}
          </Items>
        </TrustedSigners>
        <TrustedKeyGroups>
          <Enabled>{{ 'true' if distribution.distribution_config.default_cache_behavior.trusted_key_groups.group_ids|length > 0 else 'false' }}</Enabled>
          <Quantity>{{ distribution.distribution_config.default_cache_behavior.trusted_key_groups.group_ids|length }}</Quantity>
          <Items>
            {% for group_id  in distribution.distribution_config.default_cache_behavior.trusted_key_groups.group_ids %}
              <KeyGroup>{{ group_id }}</KeyGroup>
            {% endfor %}
          </Items>
        </TrustedKeyGroups>
        <ViewerProtocolPolicy>{{ distribution.distribution_config.default_cache_behavior.viewer_protocol_policy }}</ViewerProtocolPolicy>
        <AllowedMethods>
          <Quantity>{{ distribution.distribution_config.default_cache_behavior.allowed_methods|length }}</Quantity>
          <Items>
            {% for method in distribution.distribution_config.default_cache_behavior.allowed_methods %}
            <Method>{{ method }}</Method>
            {% endfor %}
          </Items>
          <CachedMethods>
            <Quantity>{{ distribution.distribution_config.default_cache_behavior.cached_methods|length }}</Quantity>
            <Items>
              {% for method in distribution.distribution_config.default_cache_behavior.cached_methods %}
              <Method>{{ method }}</Method>
              {% endfor %}
            </Items>
          </CachedMethods>
        </AllowedMethods>
        <SmoothStreaming>{{ distribution.distribution_config.default_cache_behavior.smooth_streaming }}</SmoothStreaming>
        <Compress>{{ 'true' if distribution.distribution_config.default_cache_behavior.compress else 'false' }}</Compress>
        <LambdaFunctionAssociations>
          <Quantity>{{ distribution.distribution_config.default_cache_behavior.lambda_function_associations|length }}</Quantity>
          {% if distribution.distribution_config.default_cache_behavior.lambda_function_associations %}
          <Items>
            {% for func in distribution.distribution_config.default_cache_behavior.lambda_function_associations %}
              <LambdaFunctionARN>{{ func.arn }}</LambdaFunctionARN>
              <EventType>{{ func.event_type }}</EventType>
              <IncludeBody>{{ func.include_body }}</IncludeBody>
            {% endfor %}
          </Items>
          {% endif %}
        </LambdaFunctionAssociations>
        <FunctionAssociations>
          <Quantity>{{ distribution.distribution_config.default_cache_behavior.function_associations|length }}</Quantity>
          {% if distribution.distribution_config.default_cache_behavior.function_associations %}
          <Items>
            {% for func in distribution.distribution_config.default_cache_behavior.function_associations %}
              <FunctionARN>{{ func.arn }}</FunctionARN>
              <EventType>{{ func.event_type }}</EventType>
            {% endfor %}
          </Items>
          {% endif %}
        </FunctionAssociations>
        <FieldLevelEncryptionId>{{ distribution.distribution_config.default_cache_behavior.field_level_encryption_id }}</FieldLevelEncryptionId>
        <RealtimeLogConfigArn>{{ distribution.distribution_config.default_cache_behavior.realtime_log_config_arn }}</RealtimeLogConfigArn>
        <CachePolicyId>{{ distribution.distribution_config.default_cache_behavior.cache_policy_id }}</CachePolicyId>
        <OriginRequestPolicyId>{{ distribution.distribution_config.default_cache_behavior.origin_request_policy_id }}</OriginRequestPolicyId>
        <ResponseHeadersPolicyId>{{ distribution.distribution_config.default_cache_behavior.response_headers_policy_id }}</ResponseHeadersPolicyId>
        <ForwardedValues>
          <QueryString>{{ distribution.distribution_config.default_cache_behavior.forwarded_values.query_string }}</QueryString>
          <Cookies>
            <Forward>{{ distribution.distribution_config.default_cache_behavior.forwarded_values.cookie_forward }}</Forward>
            <WhitelistedNames>
              <Quantity>{{ distribution.distribution_config.default_cache_behavior.forwarded_values.whitelisted_names|length }}</Quantity>
              <Items>
                {% for name  in distribution.distribution_config.default_cache_behavior.forwarded_values.whitelisted_names %}
                  <Name>{{ name }}</Name>
                {% endfor %}
              </Items>
            </WhitelistedNames>
          </Cookies>
          <Headers>
            <Quantity>{{ distribution.distribution_config.default_cache_behavior.forwarded_values.headers|length }}</Quantity>
            <Items>
              {% for h  in distribution.distribution_config.default_cache_behavior.forwarded_values.headers %}
                <Name>{{ h }}</Name>
              {% endfor %}
            </Items>
          </Headers>
          <QueryStringCacheKeys>
            <Quantity>{{ distribution.distribution_config.default_cache_behavior.forwarded_values.query_string_cache_keys|length }}</Quantity>
            <Items>
              {% for key  in distribution.distribution_config.default_cache_behavior.forwarded_values.query_string_cache_keys %}
                <Name>{{ key }}</Name>
              {% endfor %}
            </Items>
          </QueryStringCacheKeys>
        </ForwardedValues>
        <MinTTL>{{ distribution.distribution_config.default_cache_behavior.min_ttl }}</MinTTL>
        <DefaultTTL>{{ distribution.distribution_config.default_cache_behavior.default_ttl }}</DefaultTTL>
        <MaxTTL>{{ distribution.distribution_config.default_cache_behavior.max_ttl }}</MaxTTL>
      </DefaultCacheBehavior>
      <CacheBehaviors>
        <Quantity>{{ distribution.distribution_config.cache_behaviors|length }}</Quantity>
        {% if distribution.distribution_config.cache_behaviors %}
        <Items>
          {% for behaviour in distribution.distribution_config.cache_behaviors %}
            <CacheBehavior>
                <PathPattern>{{ behaviour.path_pattern }}</PathPattern>
                <TargetOriginId>{{ behaviour.target_origin_id }}</TargetOriginId>
                <TrustedSigners>
                  <Enabled>{{ 'true' if behaviour.trusted_signers.acct_nums|length > 0 else 'false' }}</Enabled>
                  <Quantity>{{ behaviour.trusted_signers.acct_nums | length }}</Quantity>
                  <Items>
                    {% for account_nr  in behaviour.trusted_signers.acct_nums %}
                      <AwsAccountNumber>{{ account_nr }}</AwsAccountNumber>
                    {% endfor %}
                  </Items>
                </TrustedSigners>
                <TrustedKeyGroups>
                  <Enabled>{{ 'true' if behaviour.trusted_key_groups.group_ids|length > 0 else 'false' }}</Enabled>
                  <Quantity>{{ behaviour.trusted_key_groups.group_ids | length }}</Quantity>
                  <Items>
                    {% for group_id  in behaviour.trusted_key_groups.group_ids %}
                      <KeyGroup>{{ group_id }}</KeyGroup>
                    {% endfor %}
                  </Items>
                </TrustedKeyGroups>
                <ViewerProtocolPolicy>{{ behaviour.viewer_protocol_policy }}</ViewerProtocolPolicy>
                <AllowedMethods>
                  <Quantity>{{ behaviour.allowed_methods | length }}</Quantity>
                  <Items>
                    {% for method in behaviour.allowed_methods %}<Method>{{ method }}</Method>{% endfor %}
                  </Items>
                  <CachedMethods>
                    <Quantity>{{ behaviour.cached_methods|length }}</Quantity>
                    <Items>
                      {% for method in behaviour.cached_methods %}<Method>{{ method }}</Method>{% endfor %}
                    </Items>
                  </CachedMethods>
                </AllowedMethods>
                <SmoothStreaming>{{ behaviour.smooth_streaming }}</SmoothStreaming>
                <Compress>{{ behaviour.compress }}</Compress>
                <LambdaFunctionAssociations>
                  <Quantity>{{ behaviour.lambda_function_associations | length }}</Quantity>
                  <Items>
                    {% for lambda_function_association_list in behaviour.lambda_function_associations %}
                      <LambdaFunctionARN>{{ LambdaFunctionARN }}</LambdaFunctionARN>
                      <EventType>{{ EventType }}</EventType>
                      <IncludeBody>{{ lambda_function_association_list.include_body }}</IncludeBody>
                    {% endfor %}
                  </Items>
                </LambdaFunctionAssociations>
                <FunctionAssociations>
                  <Quantity>{{ behaviour.function_associations | length }}</Quantity>
                  <Items>
                    {% for function_association_list  in behaviour.function_associations %}
                      <FunctionARN>{{ FunctionARN }}</FunctionARN>
                      <EventType>{{ EventType }}</EventType>
                    {% endfor %}
                  </Items>
                </FunctionAssociations>
                <FieldLevelEncryptionId>{{ behaviour.field_level_encryption_id }}</FieldLevelEncryptionId>
                <RealtimeLogConfigArn>{{ behaviour.realtime_log_config_arn }}</RealtimeLogConfigArn>
                <CachePolicyId>{{ behaviour.cache_policy_id }}</CachePolicyId>
                <OriginRequestPolicyId>{{ behaviour.origin_request_policy_id }}</OriginRequestPolicyId>
                <ResponseHeadersPolicyId>{{ behaviour.response_headers_policy_id }}</ResponseHeadersPolicyId>
                <ForwardedValues>
                  <QueryString>{{ behaviour.forwarded_values.query_string }}</QueryString>
                  <Cookies>
                    <Forward>{{ behaviour.forwarded_values.cookie_forward }}</Forward>
                    <WhitelistedNames>
                      <Quantity>{{ behaviour.forwarded_values.whitelisted_names| length }}</Quantity>
                      <Items>
                        {% for wl_name in behaviour.forwarded_values.whitelisted_names %}
                          <Name>{{ wl_name }}</Name>
                        {% endfor %}
                      </Items>
                    </WhitelistedNames>
                  </Cookies>
                  <Headers>
                    <Quantity>{{ behaviour.forwarded_values.headers | length }}</Quantity>
                    <Items>
                      {% for header_list in behaviour.forwarded_values.headers %}
                        <Name>{{ header_list.name }}</Name>
                      {% endfor %}
                    </Items>
                  </Headers>
                  <QueryStringCacheKeys>
                    <Quantity>{{ behaviour.forwarded_values.query_string_cache_keys | length }}</Quantity>
                    <Items>
                      {% for query_string_cache_keys_list in behaviour.forwarded_values.query_string_cache_keys %}
                        <Name>{{ query_string_cache_keys_list.name }}</Name>
                      {% endfor %}
                    </Items>
                  </QueryStringCacheKeys>
                </ForwardedValues>
                <MinTTL>{{ behaviour.min_ttl }}</MinTTL>
                <DefaultTTL>{{ behaviour.default_ttl }}</DefaultTTL>
                <MaxTTL>{{ behaviour.max_ttl }}</MaxTTL>
            </CacheBehavior>
          {% endfor %}
        </Items>
        {% endif %}
      </CacheBehaviors>
      <CustomErrorResponses>
        <Quantity>{{ distribution.distribution_config.custom_error_responses|length }}</Quantity>
        {% if distribution.distribution_config.custom_error_responses %}
        <Items>
          {% for response  in distribution.distribution_config.custom_error_responses %}
            <ErrorCode>{{ response.error_code }}</ErrorCode>
            <ResponsePagePath>{{ response.response_page_path }}</ResponsePagePath>
            <ResponseCode>{{ response.response_code }}</ResponseCode>
            <ErrorCachingMinTTL>{{ response.error_caching_min_ttl }}</ErrorCachingMinTTL>
          {% endfor %}
        </Items>
        {% endif %}
      </CustomErrorResponses>
      <Comment>{{ distribution.distribution_config.comment }}</Comment>
      <Logging>
        <Enabled>{{ distribution.distribution_config.logging.enabled }}</Enabled>
        <IncludeCookies>{{ distribution.distribution_config.logging.include_cookies }}</IncludeCookies>
        <Bucket>{{ distribution.distribution_config.logging.bucket }}</Bucket>
        <Prefix>{{ distribution.distribution_config.logging.prefix }}</Prefix>
      </Logging>
      <PriceClass>{{ distribution.distribution_config.price_class }}</PriceClass>
      <Enabled>{{ distribution.distribution_config.enabled }}</Enabled>
      <ViewerCertificate>
        <CloudFrontDefaultCertificate>{{ 'true' if distribution.distribution_config.viewer_certificate.cloud_front_default_certificate == True else 'false' }}</CloudFrontDefaultCertificate>
        <IAMCertificateId>{{ distribution.distribution_config.viewer_certificate.iam_certificate_id }}</IAMCertificateId>
        <ACMCertificateArn>{{ distribution.distribution_config.viewer_certificate.acm_certificate_arn }}</ACMCertificateArn>
        <SSLSupportMethod>{{ distribution.distribution_config.viewer_certificate.ssl_support_method }}</SSLSupportMethod>
        <MinimumProtocolVersion>{{ distribution.distribution_config.viewer_certificate.min_protocol_version }}</MinimumProtocolVersion>
        <Certificate>{{ distribution.distribution_config.viewer_certificate.certificate }}</Certificate>
        <CertificateSource>{{ distribution.distribution_config.viewer_certificate.certificate_source }}</CertificateSource>
      </ViewerCertificate>
      <Restrictions>
        <GeoRestriction>
          <RestrictionType>{{ distribution.distribution_config.geo_restriction._type }}</RestrictionType>
          <Quantity>{{ distribution.distribution_config.geo_restriction.restrictions|length }}</Quantity>
          {% if distribution.distribution_config.geo_restriction.restrictions %}
          <Items>
            {% for location  in distribution.distribution_config.geo_restriction.restrictions %}
              <Location>{{ location }}</Location>
            {% endfor %}
          </Items>
          {% endif %}
        </GeoRestriction>
      </Restrictions>
      <WebACLId>{{ distribution.distribution_config.web_acl_id }}</WebACLId>
      <HttpVersion>{{ distribution.distribution_config.http_version }}</HttpVersion>
      <IsIPV6Enabled>{{ 'true' if distribution.distribution_config.is_ipv6_enabled else 'false' }}</IsIPV6Enabled>
"""


DISTRIBUTION_TEMPLATE = (
    DIST_META_TEMPLATE
    + """
    <ActiveTrustedSigners>
      <Enabled>{{ distribution.active_trusted_signers.enabled }}</Enabled>
      <Quantity>{{ distribution.active_trusted_signers.quantity }}</Quantity>
      <Items>
        {% for signer  in distribution.active_trusted_signers.signers %}
          <AwsAccountNumber>{{ signer.aws_account_number }}</AwsAccountNumber>
          <KeyPairIds>
            <Quantity>{{ signer.key_pair_ids.quantity }}</Quantity>
            <Items>
              {% for key_pair_id_list  in signer.key_pair_ids.KeyPairIdList %}
                <KeyPairId>{{ key_pair_id_list.key_pair_id }}</KeyPairId>
              {% endfor %}
            </Items>
          </KeyPairIds>
        {% endfor %}
      </Items>
    </ActiveTrustedSigners>
    <ActiveTrustedKeyGroups>
      <Enabled>{{ distribution.active_trusted_key_groups.enabled }}</Enabled>
      <Quantity>{{ distribution.active_trusted_key_groups.quantity }}</Quantity>
      <Items>
        {% for kg_key_pair_id  in distribution.active_trusted_key_groups.kg_key_pair_ids %}
          <KeyGroupId>{{ kg_key_pair_id.key_group_id }}</KeyGroupId>
          <KeyPairIds>
            <Quantity>{{ kg_key_pair_id.key_pair_ids.quantity }}</Quantity>
            <Items>
              {% for key_pair_id_list  in kg_key_pair_ids_list.key_pair_ids.KeyPairIdList %}
                <KeyPairId>{{ key_pair_id_list.key_pair_id }}</KeyPairId>
              {% endfor %}
            </Items>
          </KeyPairIds>
        {% endfor %}
      </Items>
    </ActiveTrustedKeyGroups>
    <DistributionConfig>
      """
    + DIST_CONFIG_TEMPLATE
    + """
    </DistributionConfig>
    <AliasICPRecordals>
      {% for a  in distribution.alias_icp_recordals %}
        <CNAME>{{ a.cname }}</CNAME>
        <ICPRecordalStatus>{{ a.status }}</ICPRecordalStatus>
      {% endfor %}
    </AliasICPRecordals>"""
)

CREATE_DISTRIBUTION_TEMPLATE = (
    """<?xml version="1.0"?>
  <CreateDistributionResult xmlns="{{ xmlns }}">
"""
    + DISTRIBUTION_TEMPLATE
    + """
  </CreateDistributionResult>
"""
)

GET_DISTRIBUTION_TEMPLATE = (
    """<?xml version="1.0"?>
  <Distribution xmlns="{{ xmlns }}">
"""
    + DISTRIBUTION_TEMPLATE
    + """
  </Distribution>
"""
)

GET_DISTRIBUTION_CONFIG_TEMPLATE = (
    """<?xml version="1.0"?>
  <DistributionConfig>
"""
    + DIST_CONFIG_TEMPLATE
    + """
  </DistributionConfig>
"""
)


LIST_TEMPLATE = (
    """<?xml version="1.0"?>
<DistributionList xmlns="http://cloudfront.amazonaws.com/doc/2020-05-31/">
  <Marker></Marker>
  <MaxItems>100</MaxItems>
  <IsTruncated>false</IsTruncated>
  <Quantity>{{ distributions|length }}</Quantity>
  {% if distributions %}
  <Items>
      {% for distribution in distributions %}
      <DistributionSummary>
      """
    + DIST_META_TEMPLATE
    + """
      """
    + DIST_CONFIG_TEMPLATE
    + """
      </DistributionSummary>
      {% endfor %}
  </Items>
  {% endif %}
</DistributionList>"""
)

UPDATE_DISTRIBUTION_TEMPLATE = (
    """<?xml version="1.0"?>
  <Distribution xmlns="{{ xmlns }}">
"""
    + DISTRIBUTION_TEMPLATE
    + """
  </Distribution>
"""
)

CREATE_INVALIDATION_TEMPLATE = """<?xml version="1.0"?>
<Invalidation>
  <Id>{{ invalidation.invalidation_id }}</Id>
  <Status>{{ invalidation.status }}</Status>
  <CreateTime>{{ invalidation.create_time }}</CreateTime>
  <InvalidationBatch>
    <CallerReference>{{ invalidation.caller_ref }}</CallerReference>
    <Paths>
      <Quantity>{{ invalidation.paths|length }}</Quantity>
      <Items>
        {% for path in invalidation.paths %}<Path>{{ path }}</Path>{% endfor %}
      </Items>
    </Paths>
  </InvalidationBatch>
</Invalidation>
"""

GET_INVALIDATION_TEMPLATE = CREATE_INVALIDATION_TEMPLATE

INVALIDATIONS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<InvalidationList>
   <IsTruncated>false</IsTruncated>
   {% if invalidations %}
   <Items>
      {% for invalidation in invalidations %}
      <InvalidationSummary>
         <CreateTime>{{ invalidation.create_time }}</CreateTime>
         <Id>{{ invalidation.invalidation_id }}</Id>
         <Status>{{ invalidation.status }}</Status>
      </InvalidationSummary>
      {% endfor %}
   </Items>
   {% endif %}
   <Marker></Marker>
   <MaxItems>100</MaxItems>
   <Quantity>{{ invalidations|length }}</Quantity>
</InvalidationList>
"""

TAGS_TEMPLATE = """<?xml version="1.0"?>
<Tags>
  <Items>
    {% for tag in tags %}
      <Tag>
      <Key>{{ tag["Key"] }}</Key>
      <Value>{{ tag["Value"] }}</Value>
      </Tag>
    {% endfor %}
  </Items>
</Tags>
"""


ORIGIN_ACCESS_CONTROl = """<?xml version="1.0"?>
<OriginAccessControl>
  <Id>{{ control.id }}</Id>
  <OriginAccessControlConfig>
    <Name>{{ control.name }}</Name>
    {% if control.description %}
    <Description>{{ control.description }}</Description>
    {% endif %}
    <SigningProtocol>{{ control.signing_protocol }}</SigningProtocol>
    <SigningBehavior>{{ control.signing_behaviour }}</SigningBehavior>
    <OriginAccessControlOriginType>{{ control.origin_type }}</OriginAccessControlOriginType>
  </OriginAccessControlConfig>
</OriginAccessControl>
"""


LIST_ORIGIN_ACCESS_CONTROl = """<?xml version="1.0"?>
<OriginAccessControlList>
  <Items>
  {% for control in controls %}
    <OriginAccessControlSummary>
      <Id>{{ control.id }}</Id>
      <Name>{{ control.name }}</Name>
      {% if control.description %}
      <Description>{{ control.description }}</Description>
      {% endif %}
      <SigningProtocol>{{ control.signing_protocol }}</SigningProtocol>
      <SigningBehavior>{{ control.signing_behaviour }}</SigningBehavior>
      <OriginAccessControlOriginType>{{ control.origin_type }}</OriginAccessControlOriginType>
    </OriginAccessControlSummary>
  {% endfor %}
  </Items>
</OriginAccessControlList>
"""


PUBLIC_KEY_TEMPLATE = """<?xml version="1.0"?>
<PublicKey>
    <Id>{{ key.id }}</Id>
    <CreatedTime>{{ key.created }}</CreatedTime>
    <PublicKeyConfig>
        <CallerReference>{{ key.caller_ref }}</CallerReference>
        <Name>{{ key.name }}</Name>
        <EncodedKey>{{ key.encoded_key }}</EncodedKey>
        <Comment></Comment>
    </PublicKeyConfig>
</PublicKey>
"""


LIST_PUBLIC_KEYS = """<?xml version="1.0"?>
<PublicKeyList>
    <MaxItems>100</MaxItems>
    <Quantity>{{ keys|length }}</Quantity>
    {% if keys %}
    <Items>
        {% for key in keys %}
        <PublicKeySummary>
            <Id>{{ key.id }}</Id>
            <Name>{{ key.name }}</Name>
            <CreatedTime>{{ key.created }}</CreatedTime>
            <EncodedKey>{{ key.encoded_key }}</EncodedKey>
            <Comment></Comment>
        </PublicKeySummary>
        {% endfor %}
    </Items>
    {% endif %}
</PublicKeyList>
"""


KEY_GROUP_TEMPLATE = """<?xml version="1.0"?>
<KeyGroup>
  <Id>{{ group.id }}</Id>
  <KeyGroupConfig>
    <Name>{{ group.name }}</Name>
    <Items>
     {% for item in group.items %}<PublicKey>{{ item }}</PublicKey>{% endfor %}
    </Items>
  </KeyGroupConfig>
</KeyGroup>
"""


LIST_KEY_GROUPS_TEMPLATE = """<?xml version="1.0"?>
<KeyGroupList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ groups|length }}</Quantity>
  {% if groups %}
  <Items>
    {% for group in groups %}
    <KeyGroupSummary>
      <KeyGroup>
        <Id>{{ group.id }}</Id>
        <KeyGroupConfig>
          <Name>{{ group.name }}</Name>
          <Items>
           {% for item in group.items %}<PublicKey>{{ item }}</PublicKey>{% endfor %}
          </Items>
        </KeyGroupConfig>
      </KeyGroup>
    </KeyGroupSummary>
    {% endfor %}
  </Items>
  {% endif %}
</KeyGroupList>"""


FUNCTION_SUMMARY_TEMPLATE = """<?xml version="1.0"?>
<FunctionSummary>
  <Name>{{ func.name }}</Name>
  <Status>{{ func.status }}</Status>
  <FunctionConfig>
    <Comment>{{ func.function_config.get("Comment", "") }}</Comment>
    <Runtime>{{ func.function_config.get("Runtime", "cloudfront-js-1.0") }}</Runtime>
  </FunctionConfig>
  <FunctionMetadata>
    <FunctionARN>{{ func.function_arn }}</FunctionARN>
    <Stage>{{ func.stage }}</Stage>
    <CreatedTime>{{ func.created_time }}</CreatedTime>
    <LastModifiedTime>{{ func.last_modified_time }}</LastModifiedTime>
  </FunctionMetadata>
</FunctionSummary>
"""


LIST_FUNCTIONS_TEMPLATE = """<?xml version="1.0"?>
<FunctionList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ functions|length }}</Quantity>
  {% if functions %}
  <Items>
    {% for func in functions %}
    <FunctionSummary>
      <Name>{{ func.name }}</Name>
      <Status>{{ func.status }}</Status>
      <FunctionConfig>
        <Comment>{{ func.function_config.get("Comment", "") }}</Comment>
        <Runtime>{{ func.function_config.get("Runtime", "cloudfront-js-1.0") }}</Runtime>
      </FunctionConfig>
      <FunctionMetadata>
        <FunctionARN>{{ func.function_arn }}</FunctionARN>
        <Stage>{{ func.stage }}</Stage>
        <CreatedTime>{{ func.created_time }}</CreatedTime>
        <LastModifiedTime>{{ func.last_modified_time }}</LastModifiedTime>
      </FunctionMetadata>
    </FunctionSummary>
    {% endfor %}
  </Items>
  {% endif %}
</FunctionList>
"""


CACHE_POLICY_TEMPLATE = """<?xml version="1.0"?>
<CachePolicy>
  <Id>{{ policy.id }}</Id>
  <LastModifiedTime>{{ policy.last_modified_time }}</LastModifiedTime>
  <CachePolicyConfig>
    <Name>{{ policy.name }}</Name>
    <Comment>{{ policy.comment }}</Comment>
    <DefaultTTL>{{ policy.default_ttl }}</DefaultTTL>
    <MaxTTL>{{ policy.max_ttl }}</MaxTTL>
    <MinTTL>{{ policy.min_ttl }}</MinTTL>
  </CachePolicyConfig>
</CachePolicy>
"""


LIST_CACHE_POLICIES_TEMPLATE = """<?xml version="1.0"?>
<CachePolicyList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ policies|length }}</Quantity>
  {% if policies %}
  <Items>
    {% for policy in policies %}
    <CachePolicySummary>
      <Type>custom</Type>
      <CachePolicy>
        <Id>{{ policy.id }}</Id>
        <LastModifiedTime>{{ policy.last_modified_time }}</LastModifiedTime>
        <CachePolicyConfig>
          <Name>{{ policy.name }}</Name>
          <Comment>{{ policy.comment }}</Comment>
          <DefaultTTL>{{ policy.default_ttl }}</DefaultTTL>
          <MaxTTL>{{ policy.max_ttl }}</MaxTTL>
          <MinTTL>{{ policy.min_ttl }}</MinTTL>
        </CachePolicyConfig>
      </CachePolicy>
    </CachePolicySummary>
    {% endfor %}
  </Items>
  {% endif %}
</CachePolicyList>
"""


RESPONSE_HEADERS_POLICY_TEMPLATE = """<?xml version="1.0"?>
<ResponseHeadersPolicy>
  <Id>{{ policy.id }}</Id>
  <LastModifiedTime>{{ policy.last_modified_time }}</LastModifiedTime>
  <ResponseHeadersPolicyConfig>
    <Name>{{ policy.name }}</Name>
    <Comment>{{ policy.comment }}</Comment>
  </ResponseHeadersPolicyConfig>
</ResponseHeadersPolicy>
"""


LIST_RESPONSE_HEADERS_POLICIES_TEMPLATE = """<?xml version="1.0"?>
<ResponseHeadersPolicyList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ policies|length }}</Quantity>
  {% if policies %}
  <Items>
    {% for policy in policies %}
    <ResponseHeadersPolicySummary>
      <Type>custom</Type>
      <ResponseHeadersPolicy>
        <Id>{{ policy.id }}</Id>
        <LastModifiedTime>{{ policy.last_modified_time }}</LastModifiedTime>
        <ResponseHeadersPolicyConfig>
          <Name>{{ policy.name }}</Name>
          <Comment>{{ policy.comment }}</Comment>
        </ResponseHeadersPolicyConfig>
      </ResponseHeadersPolicy>
    </ResponseHeadersPolicySummary>
    {% endfor %}
  </Items>
  {% endif %}
</ResponseHeadersPolicyList>
"""


# Origin Access Identity templates
OAI_TEMPLATE = """<?xml version="1.0"?>
<CloudFrontOriginAccessIdentity>
  <Id>{{ oai.id }}</Id>
  <S3CanonicalUserId>{{ oai.s3_canonical_user_id }}</S3CanonicalUserId>
  <CloudFrontOriginAccessIdentityConfig>
    <CallerReference>{{ oai.caller_reference }}</CallerReference>
    <Comment>{{ oai.comment }}</Comment>
  </CloudFrontOriginAccessIdentityConfig>
</CloudFrontOriginAccessIdentity>
"""

OAI_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<CloudFrontOriginAccessIdentityConfig>
  <CallerReference>{{ oai.caller_reference }}</CallerReference>
  <Comment>{{ oai.comment }}</Comment>
</CloudFrontOriginAccessIdentityConfig>
"""

LIST_OAI_TEMPLATE = """<?xml version="1.0"?>
<CloudFrontOriginAccessIdentityList>
  <Marker></Marker>
  <MaxItems>100</MaxItems>
  <IsTruncated>false</IsTruncated>
  <Quantity>{{ oais|length }}</Quantity>
  {% if oais %}
  <Items>
    {% for oai in oais %}
    <CloudFrontOriginAccessIdentitySummary>
      <Id>{{ oai.id }}</Id>
      <S3CanonicalUserId>{{ oai.s3_canonical_user_id }}</S3CanonicalUserId>
      <Comment>{{ oai.comment }}</Comment>
    </CloudFrontOriginAccessIdentitySummary>
    {% endfor %}
  </Items>
  {% endif %}
</CloudFrontOriginAccessIdentityList>
"""


STREAMING_DIST_CONFIG_INNER = """
  <CallerReference>{{ dist.streaming_distribution_config.caller_reference }}</CallerReference>
  <S3Origin>
    <DomainName>{{ dist.streaming_distribution_config.s3_origin_dns_name }}</DomainName>
    <OriginAccessIdentity>{{ dist.streaming_distribution_config.s3_origin_access_identity }}</OriginAccessIdentity>
  </S3Origin>
  <Aliases>
    <Quantity>{{ dist.streaming_distribution_config.aliases|length }}</Quantity>
    {% if dist.streaming_distribution_config.aliases %}
    <Items>
      {% for alias in dist.streaming_distribution_config.aliases %}
      <CNAME>{{ alias }}</CNAME>
      {% endfor %}
    </Items>
    {% endif %}
  </Aliases>
  <Comment>{{ dist.streaming_distribution_config.comment }}</Comment>
  <Logging>
    <Enabled>{{ dist.streaming_distribution_config.logging.enabled }}</Enabled>
    <Bucket>{{ dist.streaming_distribution_config.logging.bucket }}</Bucket>
    <Prefix>{{ dist.streaming_distribution_config.logging.prefix }}</Prefix>
  </Logging>
  <TrustedSigners>
    <Enabled>{{ 'true' if dist.streaming_distribution_config.trusted_signers_enabled else 'false' }}</Enabled>
    <Quantity>{{ dist.streaming_distribution_config.trusted_signers|length }}</Quantity>
    {% if dist.streaming_distribution_config.trusted_signers %}
    <Items>
      {% for signer in dist.streaming_distribution_config.trusted_signers %}
      <AwsAccountNumber>{{ signer }}</AwsAccountNumber>
      {% endfor %}
    </Items>
    {% endif %}
  </TrustedSigners>
  <PriceClass>{{ dist.streaming_distribution_config.price_class }}</PriceClass>
  <Enabled>{{ dist.streaming_distribution_config.enabled }}</Enabled>
"""

STREAMING_DIST_TEMPLATE = (
    """<?xml version="1.0"?>
<StreamingDistribution>
  <Id>{{ dist.streaming_distribution_id }}</Id>
  <ARN>{{ dist.arn }}</ARN>
  <Status>{{ dist.status }}</Status>
  <LastModifiedTime>{{ dist.last_modified_time }}</LastModifiedTime>
  <DomainName>{{ dist.domain_name }}</DomainName>
  <ActiveTrustedSigners><Enabled>false</Enabled><Quantity>0</Quantity></ActiveTrustedSigners>
  <StreamingDistributionConfig>
"""
    + STREAMING_DIST_CONFIG_INNER
    + """
  </StreamingDistributionConfig>
</StreamingDistribution>
"""
)

STREAMING_DIST_CONFIG_TEMPLATE = (
    """<?xml version="1.0"?>
<StreamingDistributionConfig>
"""
    + STREAMING_DIST_CONFIG_INNER
    + """
</StreamingDistributionConfig>
"""
)

LIST_STREAMING_DISTS_TEMPLATE = (
    """<?xml version="1.0"?>
<StreamingDistributionList>
  <Marker></Marker>
  <MaxItems>100</MaxItems>
  <IsTruncated>false</IsTruncated>
  <Quantity>{{ dists|length }}</Quantity>
  {% if dists %}
  <Items>
    {% for dist in dists %}
    <StreamingDistributionSummary>
      <Id>{{ dist.streaming_distribution_id }}</Id>
      <ARN>{{ dist.arn }}</ARN>
      <Status>{{ dist.status }}</Status>
      <LastModifiedTime>{{ dist.last_modified_time }}</LastModifiedTime>
      <DomainName>{{ dist.domain_name }}</DomainName>
"""
    + STREAMING_DIST_CONFIG_INNER
    + """
    </StreamingDistributionSummary>
    {% endfor %}
  </Items>
  {% endif %}
</StreamingDistributionList>
"""
)


ORIGIN_REQUEST_POLICY_TEMPLATE = """<?xml version="1.0"?>
<OriginRequestPolicy>
  <Id>{{ policy.id }}</Id>
  <LastModifiedTime>{{ policy.last_modified_time }}</LastModifiedTime>
  <OriginRequestPolicyConfig>
    <Name>{{ policy.name }}</Name>
    <Comment>{{ policy.comment }}</Comment>
    <HeadersConfig><HeaderBehavior>{{ policy.headers_config.get("HeaderBehavior", "none") }}</HeaderBehavior></HeadersConfig>
    <CookiesConfig><CookieBehavior>{{ policy.cookies_config.get("CookieBehavior", "none") }}</CookieBehavior></CookiesConfig>
    <QueryStringsConfig><QueryStringBehavior>{{ policy.query_strings_config.get("QueryStringBehavior", "none") }}</QueryStringBehavior></QueryStringsConfig>
  </OriginRequestPolicyConfig>
</OriginRequestPolicy>
"""

ORIGIN_REQUEST_POLICY_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<OriginRequestPolicyConfig>
  <Name>{{ policy.name }}</Name>
  <Comment>{{ policy.comment }}</Comment>
  <HeadersConfig><HeaderBehavior>{{ policy.headers_config.get("HeaderBehavior", "none") }}</HeaderBehavior></HeadersConfig>
  <CookiesConfig><CookieBehavior>{{ policy.cookies_config.get("CookieBehavior", "none") }}</CookieBehavior></CookiesConfig>
  <QueryStringsConfig><QueryStringBehavior>{{ policy.query_strings_config.get("QueryStringBehavior", "none") }}</QueryStringBehavior></QueryStringsConfig>
</OriginRequestPolicyConfig>
"""

LIST_ORIGIN_REQUEST_POLICIES_TEMPLATE = """<?xml version="1.0"?>
<OriginRequestPolicyList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ policies|length }}</Quantity>
  {% if policies %}
  <Items>
    {% for policy in policies %}
    <OriginRequestPolicySummary>
      <Type>custom</Type>
      <OriginRequestPolicy>
        <Id>{{ policy.id }}</Id>
        <LastModifiedTime>{{ policy.last_modified_time }}</LastModifiedTime>
        <OriginRequestPolicyConfig>
          <Name>{{ policy.name }}</Name>
          <Comment>{{ policy.comment }}</Comment>
        </OriginRequestPolicyConfig>
      </OriginRequestPolicy>
    </OriginRequestPolicySummary>
    {% endfor %}
  </Items>
  {% endif %}
</OriginRequestPolicyList>
"""


FIELD_LEVEL_ENCRYPTION_TEMPLATE = """<?xml version="1.0"?>
<FieldLevelEncryption>
  <Id>{{ fle.id }}</Id>
  <LastModifiedTime>{{ fle.last_modified_time }}</LastModifiedTime>
  <FieldLevelEncryptionConfig>
    <CallerReference>{{ fle.caller_reference }}</CallerReference>
    <Comment>{{ fle.comment }}</Comment>
  </FieldLevelEncryptionConfig>
</FieldLevelEncryption>
"""

FIELD_LEVEL_ENCRYPTION_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<FieldLevelEncryptionConfig>
  <CallerReference>{{ fle.caller_reference }}</CallerReference>
  <Comment>{{ fle.comment }}</Comment>
</FieldLevelEncryptionConfig>
"""

LIST_FIELD_LEVEL_ENCRYPTION_TEMPLATE = """<?xml version="1.0"?>
<FieldLevelEncryptionList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ configs|length }}</Quantity>
  {% if configs %}
  <Items>
    {% for fle in configs %}
    <FieldLevelEncryptionSummary>
      <Id>{{ fle.id }}</Id>
      <LastModifiedTime>{{ fle.last_modified_time }}</LastModifiedTime>
      <Comment>{{ fle.comment }}</Comment>
    </FieldLevelEncryptionSummary>
    {% endfor %}
  </Items>
  {% endif %}
</FieldLevelEncryptionList>
"""


FLE_PROFILE_TEMPLATE = """<?xml version="1.0"?>
<FieldLevelEncryptionProfile>
  <Id>{{ profile.id }}</Id>
  <LastModifiedTime>{{ profile.last_modified_time }}</LastModifiedTime>
  <FieldLevelEncryptionProfileConfig>
    <Name>{{ profile.name }}</Name>
    <CallerReference>{{ profile.caller_reference }}</CallerReference>
    <Comment>{{ profile.comment }}</Comment>
  </FieldLevelEncryptionProfileConfig>
</FieldLevelEncryptionProfile>
"""

FLE_PROFILE_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<FieldLevelEncryptionProfileConfig>
  <Name>{{ profile.name }}</Name>
  <CallerReference>{{ profile.caller_reference }}</CallerReference>
  <Comment>{{ profile.comment }}</Comment>
</FieldLevelEncryptionProfileConfig>
"""

LIST_FLE_PROFILES_TEMPLATE = """<?xml version="1.0"?>
<FieldLevelEncryptionProfileList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ profiles|length }}</Quantity>
  {% if profiles %}
  <Items>
    {% for profile in profiles %}
    <FieldLevelEncryptionProfileSummary>
      <Id>{{ profile.id }}</Id>
      <LastModifiedTime>{{ profile.last_modified_time }}</LastModifiedTime>
      <Name>{{ profile.name }}</Name>
      <Comment>{{ profile.comment }}</Comment>
    </FieldLevelEncryptionProfileSummary>
    {% endfor %}
  </Items>
  {% endif %}
</FieldLevelEncryptionProfileList>
"""


CDP_TEMPLATE = """<?xml version="1.0"?>
<ContinuousDeploymentPolicy>
  <Id>{{ policy.id }}</Id>
  <LastModifiedTime>{{ policy.last_modified_time }}</LastModifiedTime>
  <ContinuousDeploymentPolicyConfig>
    <StagingDistributionDnsNames><Quantity>0</Quantity></StagingDistributionDnsNames>
    <Enabled>{{ policy.enabled }}</Enabled>
  </ContinuousDeploymentPolicyConfig>
</ContinuousDeploymentPolicy>
"""

CDP_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<ContinuousDeploymentPolicyConfig>
  <StagingDistributionDnsNames><Quantity>0</Quantity></StagingDistributionDnsNames>
  <Enabled>{{ policy.enabled }}</Enabled>
</ContinuousDeploymentPolicyConfig>
"""

LIST_CDP_TEMPLATE = """<?xml version="1.0"?>
<ContinuousDeploymentPolicyList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ policies|length }}</Quantity>
  {% if policies %}
  <Items>
    {% for policy in policies %}
    <ContinuousDeploymentPolicySummary>
      <ContinuousDeploymentPolicy>
        <Id>{{ policy.id }}</Id>
        <LastModifiedTime>{{ policy.last_modified_time }}</LastModifiedTime>
        <ContinuousDeploymentPolicyConfig>
          <StagingDistributionDnsNames><Quantity>0</Quantity></StagingDistributionDnsNames>
          <Enabled>{{ policy.enabled }}</Enabled>
        </ContinuousDeploymentPolicyConfig>
      </ContinuousDeploymentPolicy>
    </ContinuousDeploymentPolicySummary>
    {% endfor %}
  </Items>
  {% endif %}
</ContinuousDeploymentPolicyList>
"""


MONITORING_SUB_TEMPLATE = """<?xml version="1.0"?>
<MonitoringSubscription>
  <RealtimeMetricsSubscriptionConfig>
    <RealtimeMetricsSubscriptionStatus>{{ sub.realtime_metrics_subscription_status }}</RealtimeMetricsSubscriptionStatus>
  </RealtimeMetricsSubscriptionConfig>
</MonitoringSubscription>
"""


REALTIME_LOG_CONFIG_INNER = """
  <RealtimeLogConfig>
    <ARN>{{ config.arn }}</ARN>
    <Name>{{ config.name }}</Name>
    <SamplingRate>{{ config.sampling_rate }}</SamplingRate>
    <EndPoints>
      {% for ep in config.end_points %}
      <member>
        <StreamType>{{ ep.get("StreamType", "Kinesis") }}</StreamType>
        <KinesisStreamConfig>
          <RoleARN>{{ ep.get("KinesisStreamConfig", {}).get("RoleARN", "") }}</RoleARN>
          <StreamARN>{{ ep.get("KinesisStreamConfig", {}).get("StreamARN", "") }}</StreamARN>
        </KinesisStreamConfig>
      </member>
      {% endfor %}
    </EndPoints>
    <Fields>
      {% for field in config.fields %}
      <member>{{ field }}</member>
      {% endfor %}
    </Fields>
  </RealtimeLogConfig>
"""

CREATE_REALTIME_LOG_CONFIG_RESULT = (
    """<?xml version="1.0"?><CreateRealtimeLogConfigResult>"""
    + REALTIME_LOG_CONFIG_INNER
    + """</CreateRealtimeLogConfigResult>"""
)

GET_REALTIME_LOG_CONFIG_RESULT = (
    """<?xml version="1.0"?><GetRealtimeLogConfigResult>"""
    + REALTIME_LOG_CONFIG_INNER
    + """</GetRealtimeLogConfigResult>"""
)

UPDATE_REALTIME_LOG_CONFIG_RESULT = (
    """<?xml version="1.0"?><UpdateRealtimeLogConfigResult>"""
    + REALTIME_LOG_CONFIG_INNER
    + """</UpdateRealtimeLogConfigResult>"""
)

# Keep for backward compat
REALTIME_LOG_CONFIG_TEMPLATE = CREATE_REALTIME_LOG_CONFIG_RESULT

LIST_REALTIME_LOG_CONFIGS_TEMPLATE = """<?xml version="1.0"?>
<RealtimeLogConfigs>
  <MaxItems>100</MaxItems>
  <IsTruncated>false</IsTruncated>
  {% if configs %}
  <Items>
    {% for config in configs %}
    <member>
      <ARN>{{ config.arn }}</ARN>
      <Name>{{ config.name }}</Name>
      <SamplingRate>{{ config.sampling_rate }}</SamplingRate>
    </member>
    {% endfor %}
  </Items>
  {% endif %}
</RealtimeLogConfigs>
"""


DISTRIBUTION_ID_LIST_TEMPLATE = """<?xml version="1.0"?>
<DistributionIdList>
  <Marker></Marker>
  <MaxItems>100</MaxItems>
  <IsTruncated>false</IsTruncated>
  <Quantity>{{ dist_ids|length }}</Quantity>
  {% if dist_ids %}
  <Items>
    {% for dist_id in dist_ids %}
    <DistributionId>{{ dist_id }}</DistributionId>
    {% endfor %}
  </Items>
  {% endif %}
</DistributionIdList>
"""


CACHE_POLICY_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<CachePolicyConfig>
  <Name>{{ policy.name }}</Name>
  <Comment>{{ policy.comment }}</Comment>
  <DefaultTTL>{{ policy.default_ttl }}</DefaultTTL>
  <MaxTTL>{{ policy.max_ttl }}</MaxTTL>
  <MinTTL>{{ policy.min_ttl }}</MinTTL>
</CachePolicyConfig>
"""

KEY_GROUP_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<KeyGroupConfig>
  <Name>{{ group.name }}</Name>
  <Items>
    {% for item in group.items %}<PublicKey>{{ item }}</PublicKey>{% endfor %}
  </Items>
</KeyGroupConfig>
"""

OAC_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<OriginAccessControlConfig>
  <Name>{{ control.name }}</Name>
  {% if control.description %}
  <Description>{{ control.description }}</Description>
  {% endif %}
  <SigningProtocol>{{ control.signing_protocol }}</SigningProtocol>
  <SigningBehavior>{{ control.signing_behaviour }}</SigningBehavior>
  <OriginAccessControlOriginType>{{ control.origin_type }}</OriginAccessControlOriginType>
</OriginAccessControlConfig>
"""

PUBLIC_KEY_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<PublicKeyConfig>
  <CallerReference>{{ key.caller_ref }}</CallerReference>
  <Name>{{ key.name }}</Name>
  <EncodedKey>{{ key.encoded_key }}</EncodedKey>
  <Comment></Comment>
</PublicKeyConfig>
"""

RESPONSE_HEADERS_POLICY_CONFIG_TEMPLATE = """<?xml version="1.0"?>
<ResponseHeadersPolicyConfig>
  <Name>{{ policy.name }}</Name>
  <Comment>{{ policy.comment }}</Comment>
</ResponseHeadersPolicyConfig>
"""


TEST_FUNCTION_TEMPLATE = """<?xml version="1.0"?>
<TestResult>
  <FunctionSummary>
    <Name>{{ result.FunctionSummary.Name }}</Name>
    <Status>{{ result.FunctionSummary.Status }}</Status>
  </FunctionSummary>
  <ComputeUtilization>{{ result.ComputeUtilization }}</ComputeUtilization>
  <FunctionExecutionLogs></FunctionExecutionLogs>
  <FunctionErrorMessage>{{ result.FunctionErrorMessage }}</FunctionErrorMessage>
  <FunctionOutput>{{ result.FunctionOutput }}</FunctionOutput>
</TestResult>
"""


CONFLICTING_ALIASES_TEMPLATE = """<?xml version="1.0"?>
<ConflictingAliasesList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ items|length }}</Quantity>
  {% if items %}
  <Items>
    {% for item in items %}
    <ConflictingAlias>
      <Alias>{{ item.Alias }}</Alias>
      <DistributionId>{{ item.DistributionId }}</DistributionId>
      <AccountId>{{ item.AccountId }}</AccountId>
    </ConflictingAlias>
    {% endfor %}
  </Items>
  {% endif %}
</ConflictingAliasesList>
"""

KEY_VALUE_STORE_TEMPLATE = """<?xml version="1.0"?>
<KeyValueStore>
  <Name>{{ name }}</Name>
  <Id>{{ kvs_id }}</Id>
  <Comment>{{ comment }}</Comment>
  <ARN>{{ arn }}</ARN>
  <Status>{{ status }}</Status>
  <LastModifiedTime>{{ last_modified }}</LastModifiedTime>
</KeyValueStore>
"""

LIST_KEY_VALUE_STORES_TEMPLATE = """<?xml version="1.0"?>
<KeyValueStoreList>
  <MaxItems>100</MaxItems>
  <Quantity>{{ stores|length }}</Quantity>
  {% if stores %}
  <Items>
    {% for s in stores %}
    <KeyValueStore>
      <Name>{{ s.name }}</Name>
      <Id>{{ s.id }}</Id>
      <Comment>{{ s.comment }}</Comment>
      <ARN>{{ s.arn }}</ARN>
      <Status>{{ s.status }}</Status>
      <LastModifiedTime>{{ s.last_modified_time }}</LastModifiedTime>
    </KeyValueStore>
    {% endfor %}
  </Items>
  {% endif %}
</KeyValueStoreList>
"""

VPC_ORIGIN_TEMPLATE = """<?xml version="1.0"?>
<VpcOrigin xmlns="{{ xmlns }}">
  <Id>{{ vo.id }}</Id>
  <Arn>{{ vo.arn }}</Arn>
  <AccountId>{{ vo.account_id }}</AccountId>
  <Status>{{ vo.status }}</Status>
  <CreatedTime>{{ vo.created_time }}</CreatedTime>
  <LastModifiedTime>{{ vo.last_modified_time }}</LastModifiedTime>
  <VpcOriginEndpointConfig>
    <Name>{{ vo.vpc_origin_endpoint_config.get('Name', '') }}</Name>
    <Arn>{{ vo.vpc_origin_endpoint_config.get('Arn', '') }}</Arn>
    <HTTPPort>{{ vo.vpc_origin_endpoint_config.get('HTTPPort', 80) }}</HTTPPort>
    <HTTPSPort>{{ vo.vpc_origin_endpoint_config.get('HTTPSPort', 443) }}</HTTPSPort>
    <OriginProtocolPolicy>{{ vo.vpc_origin_endpoint_config.get('OriginProtocolPolicy', 'https-only') }}</OriginProtocolPolicy>
    <OriginSslProtocols>
      <Quantity>0</Quantity>
      <Items/>
    </OriginSslProtocols>
  </VpcOriginEndpointConfig>
</VpcOrigin>
"""

LIST_VPC_ORIGINS_TEMPLATE = """<?xml version="1.0"?>
<VpcOriginList xmlns="{{ xmlns }}">
  <Marker></Marker>
  <MaxItems>100</MaxItems>
  <IsTruncated>false</IsTruncated>
  <Quantity>{{ origins|length }}</Quantity>
  {% if origins %}
  <Items>
    {% for vo in origins %}
    <VpcOriginSummary>
      <Id>{{ vo.id }}</Id>
      <Name>{{ vo.vpc_origin_endpoint_config.get('Name', '') }}</Name>
      <Status>{{ vo.status }}</Status>
      <CreatedTime>{{ vo.created_time }}</CreatedTime>
      <LastModifiedTime>{{ vo.last_modified_time }}</LastModifiedTime>
      <Arn>{{ vo.arn }}</Arn>
      <AccountId>{{ vo.account_id }}</AccountId>
      <OriginEndpointArn>{{ vo.vpc_origin_endpoint_config.get('Arn', '') }}</OriginEndpointArn>
    </VpcOriginSummary>
    {% endfor %}
  </Items>
  {% endif %}
</VpcOriginList>
"""

TRUST_STORE_TEMPLATE = """<?xml version="1.0"?>
<TrustStore xmlns="{{ xmlns }}">
  <Id>{{ ts.id }}</Id>
  <Arn>{{ ts.arn }}</Arn>
  <Name>{{ ts.name }}</Name>
  <Status>{{ ts.status }}</Status>
  <NumberOfCaCertificates>{{ ts.number_of_ca_certificates }}</NumberOfCaCertificates>
  <LastModifiedTime>{{ ts.last_modified_time }}</LastModifiedTime>
</TrustStore>
"""

LIST_TRUST_STORES_TEMPLATE = """<?xml version="1.0"?>
<TrustStoreList xmlns="{{ xmlns }}">
  {% for ts in stores %}
  <TrustStoreSummary>
    <Id>{{ ts.id }}</Id>
    <Arn>{{ ts.arn }}</Arn>
    <Name>{{ ts.name }}</Name>
    <Status>{{ ts.status }}</Status>
    <LastModifiedTime>{{ ts.last_modified_time }}</LastModifiedTime>
  </TrustStoreSummary>
  {% endfor %}
</TrustStoreList>
"""

ANYCAST_IP_LIST_TEMPLATE = """<?xml version="1.0"?>
<AnycastIpList xmlns="{{ xmlns }}">
  <Id>{{ aip.id }}</Id>
  <Name>{{ aip.name }}</Name>
  <Status>{{ aip.status }}</Status>
  <Arn>{{ aip.arn }}</Arn>
  <AnycastIps/>
  <IpCount>{{ aip.ip_count }}</IpCount>
  <LastModifiedTime>{{ aip.last_modified_time }}</LastModifiedTime>
</AnycastIpList>
"""

LIST_ANYCAST_IP_LISTS_TEMPLATE = """<?xml version="1.0"?>
<AnycastIpLists xmlns="{{ xmlns }}">
  <Marker></Marker>
  <MaxItems>100</MaxItems>
  <IsTruncated>false</IsTruncated>
  <Quantity>{{ lists|length }}</Quantity>
  {% if lists %}
  <Items>
    {% for a in lists %}
    <AnycastIpListSummary>
      <Id>{{ a.id }}</Id>
      <Name>{{ a.name }}</Name>
      <Status>{{ a.status }}</Status>
      <Arn>{{ a.arn }}</Arn>
      <IpCount>{{ a.ip_count }}</IpCount>
      <LastModifiedTime>{{ a.last_modified_time }}</LastModifiedTime>
    </AnycastIpListSummary>
    {% endfor %}
  </Items>
  {% endif %}
</AnycastIpLists>
"""

CONNECTION_GROUP_TEMPLATE = """<?xml version="1.0"?>
<ConnectionGroup xmlns="{{ xmlns }}">
  <Id>{{ cg.id }}</Id>
  <Name>{{ cg.name }}</Name>
  <Arn>{{ cg.arn }}</Arn>
  <CreatedTime>{{ cg.created_time }}</CreatedTime>
  <LastModifiedTime>{{ cg.last_modified_time }}</LastModifiedTime>
  <Status>{{ cg.status }}</Status>
  <Enabled>true</Enabled>
  <IsDefault>false</IsDefault>
</ConnectionGroup>
"""

LIST_CONNECTION_GROUPS_TEMPLATE = """<?xml version="1.0"?>
<ConnectionGroups xmlns="{{ xmlns }}">
  {% for cg in groups %}
  <ConnectionGroupSummary>
    <Id>{{ cg.id }}</Id>
    <Name>{{ cg.name }}</Name>
    <Arn>{{ cg.arn }}</Arn>
    <CreatedTime>{{ cg.created_time }}</CreatedTime>
    <LastModifiedTime>{{ cg.last_modified_time }}</LastModifiedTime>
    <Status>{{ cg.status }}</Status>
  </ConnectionGroupSummary>
  {% endfor %}
</ConnectionGroups>
"""

DISTRIBUTION_TENANT_TEMPLATE = """<?xml version="1.0"?>
<DistributionTenant xmlns="{{ xmlns }}">
  <Id>{{ dt.id }}</Id>
  <DistributionId>{{ dt.distribution_id }}</DistributionId>
  <Name>{{ dt.name }}</Name>
  <Arn>{{ dt.arn }}</Arn>
  <Status>{{ dt.status }}</Status>
  <Enabled>true</Enabled>
  <CreatedTime>{{ dt.created_time }}</CreatedTime>
  <LastModifiedTime>{{ dt.last_modified_time }}</LastModifiedTime>
</DistributionTenant>
"""

LIST_DISTRIBUTION_TENANTS_TEMPLATE = """<?xml version="1.0"?>
<DistributionTenantList xmlns="{{ xmlns }}">
  {% for dt in tenants %}
  <DistributionTenantSummary>
    <Id>{{ dt.id }}</Id>
    <Name>{{ dt.name }}</Name>
    <Arn>{{ dt.arn }}</Arn>
    <Status>{{ dt.status }}</Status>
  </DistributionTenantSummary>
  {% endfor %}
</DistributionTenantList>
"""

TENANT_INVALIDATION_TEMPLATE = """<?xml version="1.0"?>
<Invalidation xmlns="{{ xmlns }}">
  <Id>{{ inv_id }}</Id>
  <Status>COMPLETED</Status>
  <CreateTime>2021-01-01T00:00:00.000Z</CreateTime>
  <InvalidationBatch>
    <Paths><Quantity>0</Quantity></Paths>
    <CallerReference>ref</CallerReference>
  </InvalidationBatch>
</Invalidation>
"""

TENANT_INVALIDATION_LIST_TEMPLATE = """<?xml version="1.0"?>
<InvalidationList xmlns="{{ xmlns }}">
  <Marker></Marker>
  <MaxItems>100</MaxItems>
  <IsTruncated>false</IsTruncated>
  <Quantity>0</Quantity>
</InvalidationList>
"""

CONNECTION_FUNCTION_TEMPLATE = """<?xml version="1.0"?>
<ConnectionFunctionSummary xmlns="{{ xmlns }}">
  <Name>{{ cf.name }}</Name>
  <Id>{{ cf.id }}</Id>
  <ConnectionFunctionArn>{{ cf.connection_function_arn }}</ConnectionFunctionArn>
  <Status>{{ cf.status }}</Status>
  <Stage>{{ cf.stage }}</Stage>
  <CreatedTime>{{ cf.created_time }}</CreatedTime>
  <LastModifiedTime>{{ cf.last_modified_time }}</LastModifiedTime>
</ConnectionFunctionSummary>
"""

LIST_CONNECTION_FUNCTIONS_TEMPLATE = """<?xml version="1.0"?>
<ConnectionFunctions xmlns="{{ xmlns }}">
  {% for cf in funcs %}
  <ConnectionFunctionSummary>
    <Name>{{ cf.name }}</Name>
    <Id>{{ cf.id }}</Id>
    <ConnectionFunctionArn>{{ cf.connection_function_arn }}</ConnectionFunctionArn>
    <Status>{{ cf.status }}</Status>
    <Stage>{{ cf.stage }}</Stage>
    <CreatedTime>{{ cf.created_time }}</CreatedTime>
    <LastModifiedTime>{{ cf.last_modified_time }}</LastModifiedTime>
  </ConnectionFunctionSummary>
  {% endfor %}
</ConnectionFunctions>
"""

TEST_CONNECTION_FUNCTION_TEMPLATE = """<?xml version="1.0"?>
<TestResult xmlns="{{ xmlns }}">
  <FunctionOutput>{"response":{"statusCode":200}}</FunctionOutput>
  <ComputeUtilization>12</ComputeUtilization>
</TestResult>
"""

ERROR_TEMPLATE = """<?xml version="1.0"?>
<ErrorResponse xmlns="{{ xmlns }}">
  <Error>
    <Type>Sender</Type>
    <Code>{{ code }}</Code>
    <Message>{{ message }}</Message>
  </Error>
</ErrorResponse>
"""

RESOURCE_POLICY_TEMPLATE = """<?xml version="1.0"?>
<GetResourcePolicyResult xmlns="{{ xmlns }}">
</GetResourcePolicyResult>
"""

EMPTY_LIST_TEMPLATE = """<?xml version="1.0"?>
<{{ root_tag }} xmlns="{{ xmlns }}">
</{{ root_tag }}>
"""

MANAGED_CERTIFICATE_TEMPLATE = """<?xml version="1.0"?>
<ManagedCertificateDetails xmlns="{{ xmlns }}">
  <CertificateStatus>ISSUED</CertificateStatus>
</ManagedCertificateDetails>
"""

VERIFY_DNS_TEMPLATE = """<?xml version="1.0"?>
<VerifyDnsConfigurationResult xmlns="{{ xmlns }}">
</VerifyDnsConfigurationResult>
"""
