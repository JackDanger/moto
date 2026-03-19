from typing import Any

import xmltodict

from moto.core.responses import ActionResult, BaseResponse, EmptyResult, TYPE_RESPONSE


from .models import CloudFrontBackend, cloudfront_backends, random_id


class CloudFrontResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="cloudfront")
        self.automated_parameter_parsing = True

    def _get_xml_body(self) -> dict[str, Any]:
        return xmltodict.parse(self.body, dict_constructor=dict, force_list="Path")

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
    def create_function(self) -> TYPE_RESPONSE:
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
        template = self.response_template(FUNCTION_SUMMARY_TEMPLATE)
        headers = {
            "ETag": func.etag,
            "Location": (
                "https://cloudfront.amazonaws.com/2020-05-31"
                f"/function/{func.name}"
            ),
            "status": 201,
        }
        return 201, headers, template.render(func=func)

    def describe_function(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-2]
        func = self.backend.describe_function(name)
        template = self.response_template(FUNCTION_SUMMARY_TEMPLATE)
        return 200, {"ETag": func.etag}, template.render(func=func)

    def get_function(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-1]
        func = self.backend.get_function(name)
        headers = {"ETag": func.etag, "Content-Type": "application/octet-stream"}
        return 200, headers, func.function_code

    def update_function(self) -> TYPE_RESPONSE:
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
        template = self.response_template(FUNCTION_SUMMARY_TEMPLATE)
        return 200, {"ETtag": func.etag}, template.render(func=func)

    def delete_function(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-1]
        if_match = self.headers.get("If-Match", "")
        self.backend.delete_function(name=name, if_match=if_match)
        return 204, {"status": 204}, ""

    def publish_function(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-2]
        if_match = self.headers.get("If-Match", "")
        func = self.backend.publish_function(name=name, if_match=if_match)
        template = self.response_template(FUNCTION_SUMMARY_TEMPLATE)
        return 200, {"ETag": func.etag}, template.render(func=func)

    def list_functions(self) -> TYPE_RESPONSE:
        functions = self.backend.list_functions()
        template = self.response_template(LIST_FUNCTIONS_TEMPLATE)
        return 200, {}, template.render(functions=functions)

    # Cache Policies
    def create_cache_policy(self) -> TYPE_RESPONSE:
        config = self._get_xml_body().get("CachePolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.create_cache_policy(config)
        template = self.response_template(CACHE_POLICY_TEMPLATE)
        headers = {
            "ETag": policy.etag,
            "Location": (
                "https://cloudfront.amazonaws.com/2020-05-31"
                f"/cache-policy/{policy.id}"
            ),
            "status": 201,
        }
        return 201, headers, template.render(policy=policy)

    def get_cache_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        policy = self.backend.get_cache_policy(policy_id)
        template = self.response_template(CACHE_POLICY_TEMPLATE)
        return 200, {"ETag": policy.etag}, template.render(policy=policy)

    def update_cache_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        config = self._get_xml_body().get("CachePolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.update_cache_policy(policy_id, config)
        template = self.response_template(CACHE_POLICY_TEMPLATE)
        return 200, {"ETag": policy.etag}, template.render(policy=policy)

    def delete_cache_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        self.backend.delete_cache_policy(policy_id)
        return 204, {"status": 204}, ""

    def list_cache_policies(self) -> TYPE_RESPONSE:
        policies = self.backend.list_cache_policies()
        template = self.response_template(LIST_CACHE_POLICIES_TEMPLATE)
        return 200, {}, template.render(policies=policies)

    # Response Headers Policies
    def create_response_headers_policy(self) -> TYPE_RESPONSE:
        config = self._get_xml_body().get("ResponseHeadersPolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.create_response_headers_policy(config)
        template = self.response_template(RESPONSE_HEADERS_POLICY_TEMPLATE)
        headers = {
            "ETag": policy.etag,
            "Location": (
                "https://cloudfront.amazonaws.com/2020-05-31"
                f"/response-headers-policy/{policy.id}"
            ),
            "status": 201,
        }
        return 201, headers, template.render(policy=policy)

    def get_response_headers_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        policy = self.backend.get_response_headers_policy(policy_id)
        template = self.response_template(RESPONSE_HEADERS_POLICY_TEMPLATE)
        return 200, {"ETag": policy.etag}, template.render(policy=policy)

    def update_response_headers_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        config = self._get_xml_body().get("ResponseHeadersPolicyConfig", {})
        config.pop("@xmlns", None)
        policy = self.backend.update_response_headers_policy(policy_id, config)
        template = self.response_template(RESPONSE_HEADERS_POLICY_TEMPLATE)
        return 200, {"ETag": policy.etag}, template.render(policy=policy)

    def delete_response_headers_policy(self) -> TYPE_RESPONSE:
        policy_id = self.path.split("/")[-1]
        self.backend.delete_response_headers_policy(policy_id)
        return 204, {"status": 204}, ""

    def list_response_headers_policies(self) -> TYPE_RESPONSE:
        policies = self.backend.list_response_headers_policies()
        template = self.response_template(LIST_RESPONSE_HEADERS_POLICIES_TEMPLATE)
        return 200, {}, template.render(policies=policies)


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

