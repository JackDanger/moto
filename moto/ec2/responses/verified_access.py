from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class VerifiedAccessResponse(EC2BaseResponse):
    def create_verified_access_instance(self) -> str:
        description = self._get_param("Description", "")
        fips_enabled = str2bool(self._get_param("FIPSEnabled", "false"))
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        instance = self.ec2_backend.create_verified_access_instance(
            description=description,
            fips_enabled=fips_enabled,
            tags=tags,
        )
        template = self.response_template(CREATE_VERIFIED_ACCESS_INSTANCE)
        return template.render(instance=instance)

    def delete_verified_access_instance(self) -> str:
        instance_id = self._get_param("VerifiedAccessInstanceId")
        instance = self.ec2_backend.delete_verified_access_instance(instance_id)
        template = self.response_template(DELETE_VERIFIED_ACCESS_INSTANCE)
        return template.render(instance=instance)

    def describe_verified_access_instances(self) -> str:
        instance_ids = self._get_param("VerifiedAccessInstanceIds", [])
        filters = self._filters_from_querystring()
        instances = self.ec2_backend.describe_verified_access_instances(
            verified_access_instance_ids=instance_ids or None,
            filters=filters,
        )
        template = self.response_template(DESCRIBE_VERIFIED_ACCESS_INSTANCES)
        return template.render(instances=instances)

    def create_verified_access_trust_provider(self) -> str:
        trust_provider_type = self._get_param("TrustProviderType", "user")
        policy_reference_name = self._get_param("PolicyReferenceName", "")
        user_trust_provider_type = self._get_param("UserTrustProviderType")
        device_trust_provider_type = self._get_param("DeviceTrustProviderType")
        oidc_options = self._get_param("OidcOptions")
        device_options = self._get_param("DeviceOptions")
        description = self._get_param("Description", "")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        provider = self.ec2_backend.create_verified_access_trust_provider(
            trust_provider_type=trust_provider_type,
            policy_reference_name=policy_reference_name,
            user_trust_provider_type=user_trust_provider_type,
            device_trust_provider_type=device_trust_provider_type,
            oidc_options=oidc_options,
            device_options=device_options,
            description=description,
            tags=tags,
        )
        template = self.response_template(CREATE_VERIFIED_ACCESS_TRUST_PROVIDER)
        return template.render(provider=provider)

    def delete_verified_access_trust_provider(self) -> str:
        provider_id = self._get_param("VerifiedAccessTrustProviderId")
        provider = self.ec2_backend.delete_verified_access_trust_provider(provider_id)
        template = self.response_template(DELETE_VERIFIED_ACCESS_TRUST_PROVIDER)
        return template.render(provider=provider)

    def describe_verified_access_trust_providers(self) -> str:
        provider_ids = self._get_param("VerifiedAccessTrustProviderIds", [])
        filters = self._filters_from_querystring()
        providers = self.ec2_backend.describe_verified_access_trust_providers(
            verified_access_trust_provider_ids=provider_ids or None,
            filters=filters,
        )
        template = self.response_template(DESCRIBE_VERIFIED_ACCESS_TRUST_PROVIDERS)
        return template.render(providers=providers)

    def create_verified_access_group(self) -> str:
        instance_id = self._get_param("VerifiedAccessInstanceId")
        description = self._get_param("Description", "")
        policy_document = self._get_param("PolicyDocument", "")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        group = self.ec2_backend.create_verified_access_group(
            verified_access_instance_id=instance_id,
            description=description,
            policy_document=policy_document,
            tags=tags,
        )
        template = self.response_template(CREATE_VERIFIED_ACCESS_GROUP)
        return template.render(group=group)

    def delete_verified_access_group(self) -> str:
        group_id = self._get_param("VerifiedAccessGroupId")
        group = self.ec2_backend.delete_verified_access_group(group_id)
        template = self.response_template(DELETE_VERIFIED_ACCESS_GROUP)
        return template.render(group=group)

    def describe_verified_access_groups(self) -> str:
        group_ids = self._get_param("VerifiedAccessGroupIds", [])
        instance_id = self._get_param("VerifiedAccessInstanceId")
        filters = self._filters_from_querystring()
        groups = self.ec2_backend.describe_verified_access_groups(
            verified_access_group_ids=group_ids or None,
            verified_access_instance_id=instance_id,
            filters=filters,
        )
        template = self.response_template(DESCRIBE_VERIFIED_ACCESS_GROUPS)
        return template.render(groups=groups)

    def create_verified_access_endpoint(self) -> str:
        group_id = self._get_param("VerifiedAccessGroupId")
        endpoint_type = self._get_param("EndpointType", "load-balancer")
        attachment_type = self._get_param("AttachmentType", "vpc")
        domain_certificate_arn = self._get_param("DomainCertificateArn", "")
        application_domain = self._get_param("ApplicationDomain", "")
        endpoint_domain_prefix = self._get_param("EndpointDomainPrefix", "")
        security_group_ids = self._get_param("SecurityGroupIds", [])
        load_balancer_options = self._get_param("LoadBalancerOptions")
        network_interface_options = self._get_param("NetworkInterfaceOptions")
        description = self._get_param("Description", "")
        policy_document = self._get_param("PolicyDocument", "")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        endpoint = self.ec2_backend.create_verified_access_endpoint(
            verified_access_group_id=group_id,
            endpoint_type=endpoint_type,
            attachment_type=attachment_type,
            domain_certificate_arn=domain_certificate_arn,
            application_domain=application_domain,
            endpoint_domain_prefix=endpoint_domain_prefix,
            security_group_ids=security_group_ids,
            load_balancer_options=load_balancer_options,
            network_interface_options=network_interface_options,
            description=description,
            policy_document=policy_document,
            tags=tags,
        )
        template = self.response_template(CREATE_VERIFIED_ACCESS_ENDPOINT)
        return template.render(endpoint=endpoint)

    def delete_verified_access_endpoint(self) -> str:
        endpoint_id = self._get_param("VerifiedAccessEndpointId")
        endpoint = self.ec2_backend.delete_verified_access_endpoint(endpoint_id)
        template = self.response_template(DELETE_VERIFIED_ACCESS_ENDPOINT)
        return template.render(endpoint=endpoint)

    def describe_verified_access_endpoints(self) -> str:
        endpoint_ids = self._get_param("VerifiedAccessEndpointIds", [])
        group_id = self._get_param("VerifiedAccessGroupId")
        instance_id = self._get_param("VerifiedAccessInstanceId")
        filters = self._filters_from_querystring()
        endpoints = self.ec2_backend.describe_verified_access_endpoints(
            verified_access_endpoint_ids=endpoint_ids or None,
            verified_access_group_id=group_id,
            verified_access_instance_id=instance_id,
            filters=filters,
        )
        template = self.response_template(DESCRIBE_VERIFIED_ACCESS_ENDPOINTS)
        return template.render(endpoints=endpoints)


CREATE_VERIFIED_ACCESS_INSTANCE = """<CreateVerifiedAccessInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessInstance>
    <verifiedAccessInstanceId>{{ instance.id }}</verifiedAccessInstanceId>
    <description>{{ instance.description }}</description>
    <verifiedAccessTrustProviderSet>
      {% for tp_id in instance.verified_access_trust_provider_ids %}
      <item>
        <verifiedAccessTrustProviderId>{{ tp_id }}</verifiedAccessTrustProviderId>
      </item>
      {% endfor %}
    </verifiedAccessTrustProviderSet>
    <creationTime>{{ instance.creation_time }}</creationTime>
    <lastUpdatedTime>{{ instance.last_updated_time }}</lastUpdatedTime>
    <fipsEnabled>{{ 'true' if instance.fips_enabled else 'false' }}</fipsEnabled>
    <tagSet>
      {% for tag in instance.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </verifiedAccessInstance>
</CreateVerifiedAccessInstanceResponse>"""


DELETE_VERIFIED_ACCESS_INSTANCE = """<DeleteVerifiedAccessInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessInstance>
    <verifiedAccessInstanceId>{{ instance.id }}</verifiedAccessInstanceId>
  </verifiedAccessInstance>
</DeleteVerifiedAccessInstanceResponse>"""


DESCRIBE_VERIFIED_ACCESS_INSTANCES = """<DescribeVerifiedAccessInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessInstanceSet>
    {% for instance in instances %}
    <item>
      <verifiedAccessInstanceId>{{ instance.id }}</verifiedAccessInstanceId>
      <description>{{ instance.description }}</description>
      <verifiedAccessTrustProviderSet>
        {% for tp_id in instance.verified_access_trust_provider_ids %}
        <item>
          <verifiedAccessTrustProviderId>{{ tp_id }}</verifiedAccessTrustProviderId>
        </item>
        {% endfor %}
      </verifiedAccessTrustProviderSet>
      <creationTime>{{ instance.creation_time }}</creationTime>
      <lastUpdatedTime>{{ instance.last_updated_time }}</lastUpdatedTime>
      <fipsEnabled>{{ 'true' if instance.fips_enabled else 'false' }}</fipsEnabled>
      <tagSet>
        {% for tag in instance.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </verifiedAccessInstanceSet>
</DescribeVerifiedAccessInstancesResponse>"""


CREATE_VERIFIED_ACCESS_TRUST_PROVIDER = """<CreateVerifiedAccessTrustProviderResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessTrustProvider>
    <verifiedAccessTrustProviderId>{{ provider.id }}</verifiedAccessTrustProviderId>
    <description>{{ provider.description }}</description>
    <trustProviderType>{{ provider.trust_provider_type }}</trustProviderType>
    {% if provider.user_trust_provider_type %}
    <userTrustProviderType>{{ provider.user_trust_provider_type }}</userTrustProviderType>
    {% endif %}
    {% if provider.device_trust_provider_type %}
    <deviceTrustProviderType>{{ provider.device_trust_provider_type }}</deviceTrustProviderType>
    {% endif %}
    <policyReferenceName>{{ provider.policy_reference_name }}</policyReferenceName>
    <creationTime>{{ provider.creation_time }}</creationTime>
    <lastUpdatedTime>{{ provider.last_updated_time }}</lastUpdatedTime>
    <tagSet>
      {% for tag in provider.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </verifiedAccessTrustProvider>
</CreateVerifiedAccessTrustProviderResponse>"""


DELETE_VERIFIED_ACCESS_TRUST_PROVIDER = """<DeleteVerifiedAccessTrustProviderResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessTrustProvider>
    <verifiedAccessTrustProviderId>{{ provider.id }}</verifiedAccessTrustProviderId>
  </verifiedAccessTrustProvider>
</DeleteVerifiedAccessTrustProviderResponse>"""


DESCRIBE_VERIFIED_ACCESS_TRUST_PROVIDERS = """<DescribeVerifiedAccessTrustProvidersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessTrustProviderSet>
    {% for provider in providers %}
    <item>
      <verifiedAccessTrustProviderId>{{ provider.id }}</verifiedAccessTrustProviderId>
      <description>{{ provider.description }}</description>
      <trustProviderType>{{ provider.trust_provider_type }}</trustProviderType>
      {% if provider.user_trust_provider_type %}
      <userTrustProviderType>{{ provider.user_trust_provider_type }}</userTrustProviderType>
      {% endif %}
      {% if provider.device_trust_provider_type %}
      <deviceTrustProviderType>{{ provider.device_trust_provider_type }}</deviceTrustProviderType>
      {% endif %}
      <policyReferenceName>{{ provider.policy_reference_name }}</policyReferenceName>
      <creationTime>{{ provider.creation_time }}</creationTime>
      <lastUpdatedTime>{{ provider.last_updated_time }}</lastUpdatedTime>
      <tagSet>
        {% for tag in provider.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </verifiedAccessTrustProviderSet>
</DescribeVerifiedAccessTrustProvidersResponse>"""


CREATE_VERIFIED_ACCESS_GROUP = """<CreateVerifiedAccessGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessGroup>
    <verifiedAccessGroupId>{{ group.id }}</verifiedAccessGroupId>
    <verifiedAccessGroupArn>{{ group.arn }}</verifiedAccessGroupArn>
    <verifiedAccessInstanceId>{{ group.verified_access_instance_id }}</verifiedAccessInstanceId>
    <description>{{ group.description }}</description>
    <owner>{{ group.owner_id }}</owner>
    <creationTime>{{ group.creation_time }}</creationTime>
    <lastUpdatedTime>{{ group.last_updated_time }}</lastUpdatedTime>
    <tagSet>
      {% for tag in group.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </verifiedAccessGroup>
</CreateVerifiedAccessGroupResponse>"""


DELETE_VERIFIED_ACCESS_GROUP = """<DeleteVerifiedAccessGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessGroup>
    <verifiedAccessGroupId>{{ group.id }}</verifiedAccessGroupId>
  </verifiedAccessGroup>
</DeleteVerifiedAccessGroupResponse>"""


DESCRIBE_VERIFIED_ACCESS_GROUPS = """<DescribeVerifiedAccessGroupsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessGroupSet>
    {% for group in groups %}
    <item>
      <verifiedAccessGroupId>{{ group.id }}</verifiedAccessGroupId>
      <verifiedAccessGroupArn>{{ group.arn }}</verifiedAccessGroupArn>
      <verifiedAccessInstanceId>{{ group.verified_access_instance_id }}</verifiedAccessInstanceId>
      <description>{{ group.description }}</description>
      <owner>{{ group.owner_id }}</owner>
      <creationTime>{{ group.creation_time }}</creationTime>
      <lastUpdatedTime>{{ group.last_updated_time }}</lastUpdatedTime>
      <tagSet>
        {% for tag in group.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </verifiedAccessGroupSet>
</DescribeVerifiedAccessGroupsResponse>"""


CREATE_VERIFIED_ACCESS_ENDPOINT = """<CreateVerifiedAccessEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessEndpoint>
    <verifiedAccessEndpointId>{{ endpoint.id }}</verifiedAccessEndpointId>
    <verifiedAccessGroupId>{{ endpoint.verified_access_group_id }}</verifiedAccessGroupId>
    <verifiedAccessInstanceId>{{ endpoint.verified_access_instance_id }}</verifiedAccessInstanceId>
    <endpointType>{{ endpoint.endpoint_type }}</endpointType>
    <attachmentType>{{ endpoint.attachment_type }}</attachmentType>
    <domainCertificateArn>{{ endpoint.domain_certificate_arn }}</domainCertificateArn>
    <applicationDomain>{{ endpoint.application_domain }}</applicationDomain>
    <endpointDomain>{{ endpoint.endpoint_domain }}</endpointDomain>
    <description>{{ endpoint.description }}</description>
    <status>
      <code>{{ endpoint.state }}</code>
    </status>
    <creationTime>{{ endpoint.creation_time }}</creationTime>
    <lastUpdatedTime>{{ endpoint.last_updated_time }}</lastUpdatedTime>
    <tagSet>
      {% for tag in endpoint.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </verifiedAccessEndpoint>
</CreateVerifiedAccessEndpointResponse>"""


DELETE_VERIFIED_ACCESS_ENDPOINT = """<DeleteVerifiedAccessEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessEndpoint>
    <verifiedAccessEndpointId>{{ endpoint.id }}</verifiedAccessEndpointId>
  </verifiedAccessEndpoint>
</DeleteVerifiedAccessEndpointResponse>"""


DESCRIBE_VERIFIED_ACCESS_ENDPOINTS = """<DescribeVerifiedAccessEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <verifiedAccessEndpointSet>
    {% for endpoint in endpoints %}
    <item>
      <verifiedAccessEndpointId>{{ endpoint.id }}</verifiedAccessEndpointId>
      <verifiedAccessGroupId>{{ endpoint.verified_access_group_id }}</verifiedAccessGroupId>
      <verifiedAccessInstanceId>{{ endpoint.verified_access_instance_id }}</verifiedAccessInstanceId>
      <endpointType>{{ endpoint.endpoint_type }}</endpointType>
      <attachmentType>{{ endpoint.attachment_type }}</attachmentType>
      <domainCertificateArn>{{ endpoint.domain_certificate_arn }}</domainCertificateArn>
      <applicationDomain>{{ endpoint.application_domain }}</applicationDomain>
      <endpointDomain>{{ endpoint.endpoint_domain }}</endpointDomain>
      <description>{{ endpoint.description }}</description>
      <status>
        <code>{{ endpoint.state }}</code>
      </status>
      <creationTime>{{ endpoint.creation_time }}</creationTime>
      <lastUpdatedTime>{{ endpoint.last_updated_time }}</lastUpdatedTime>
      <tagSet>
        {% for tag in endpoint.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </verifiedAccessEndpointSet>
</DescribeVerifiedAccessEndpointsResponse>"""
