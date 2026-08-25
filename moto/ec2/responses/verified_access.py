from moto.core.responses import ActionResult
from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class VerifiedAccessResponse(EC2BaseResponse):
    def create_verified_access_instance(self) -> ActionResult:
        description = self._get_param("Description", "")
        fips_enabled = str2bool(self._get_param("FIPSEnabled", "false"))
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        instance = self.ec2_backend.create_verified_access_instance(
            description=description,
            fips_enabled=fips_enabled,
            tags=tags,
        )
        result = {
            "VerifiedAccessInstance": {
                "VerifiedAccessInstanceId": instance.id,
                "Description": instance.description,
                "VerifiedAccessTrustProviderSet": [
                    {"VerifiedAccessTrustProviderId": tp_id}
                    for tp_id in instance.verified_access_trust_provider_ids
                ],
                "CreationTime": instance.creation_time,
                "LastUpdatedTime": instance.last_updated_time,
                "FipsEnabled": instance.fips_enabled,
                "Tags": [
                    {"Key": tag.key, "Value": tag.value}
                    for tag in instance.get_tags()
                ],
            }
        }
        return ActionResult(result)

    def delete_verified_access_instance(self) -> ActionResult:
        instance_id = self._get_param("VerifiedAccessInstanceId")
        instance = self.ec2_backend.delete_verified_access_instance(instance_id)
        result = {
            "VerifiedAccessInstance": {
                "VerifiedAccessInstanceId": instance.id,
            }
        }
        return ActionResult(result)

    def describe_verified_access_instances(self) -> ActionResult:
        instance_ids = self._get_param("VerifiedAccessInstanceIds", [])
        filters = self._filters_from_querystring()
        instances = self.ec2_backend.describe_verified_access_instances(
            verified_access_instance_ids=instance_ids or None,
            filters=filters,
        )
        result = {
            "VerifiedAccessInstances": [
                {
                    "VerifiedAccessInstanceId": instance.id,
                    "Description": instance.description,
                    "VerifiedAccessTrustProviderSet": [
                        {"VerifiedAccessTrustProviderId": tp_id}
                        for tp_id in instance.verified_access_trust_provider_ids
                    ],
                    "CreationTime": instance.creation_time,
                    "LastUpdatedTime": instance.last_updated_time,
                    "FipsEnabled": instance.fips_enabled,
                    "Tags": [
                        {"Key": tag.key, "Value": tag.value}
                        for tag in instance.get_tags()
                    ],
                }
                for instance in instances
            ]
        }
        return ActionResult(result)

    def create_verified_access_trust_provider(self) -> ActionResult:
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
        provider_dict = {
            "VerifiedAccessTrustProviderId": provider.id,
            "Description": provider.description,
            "TrustProviderType": provider.trust_provider_type,
            "PolicyReferenceName": provider.policy_reference_name,
            "CreationTime": provider.creation_time,
            "LastUpdatedTime": provider.last_updated_time,
            "Tags": [
                {"Key": tag.key, "Value": tag.value}
                for tag in provider.get_tags()
            ],
        }
        if provider.user_trust_provider_type:
            provider_dict["UserTrustProviderType"] = provider.user_trust_provider_type
        if provider.device_trust_provider_type:
            provider_dict["DeviceTrustProviderType"] = provider.device_trust_provider_type

        result = {"VerifiedAccessTrustProvider": provider_dict}
        return ActionResult(result)

    def delete_verified_access_trust_provider(self) -> ActionResult:
        provider_id = self._get_param("VerifiedAccessTrustProviderId")
        provider = self.ec2_backend.delete_verified_access_trust_provider(provider_id)
        result = {
            "VerifiedAccessTrustProvider": {
                "VerifiedAccessTrustProviderId": provider.id,
            }
        }
        return ActionResult(result)

    def describe_verified_access_trust_providers(self) -> ActionResult:
        provider_ids = self._get_param("VerifiedAccessTrustProviderIds", [])
        filters = self._filters_from_querystring()
        providers = self.ec2_backend.describe_verified_access_trust_providers(
            verified_access_trust_provider_ids=provider_ids or None,
            filters=filters,
        )
        result = {
            "VerifiedAccessTrustProviders": [
                {
                    "VerifiedAccessTrustProviderId": provider.id,
                    "Description": provider.description,
                    "TrustProviderType": provider.trust_provider_type,
                    "PolicyReferenceName": provider.policy_reference_name,
                    "CreationTime": provider.creation_time,
                    "LastUpdatedTime": provider.last_updated_time,
                    "Tags": [
                        {"Key": tag.key, "Value": tag.value}
                        for tag in provider.get_tags()
                    ],
                }
                for provider in providers
            ]
        }
        return ActionResult(result)

    def create_verified_access_group(self) -> ActionResult:
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
        result = {
            "VerifiedAccessGroup": {
                "VerifiedAccessGroupId": group.id,
                "VerifiedAccessGroupArn": group.arn,
                "VerifiedAccessInstanceId": group.verified_access_instance_id,
                "Description": group.description,
                "Owner": group.owner_id,
                "CreationTime": group.creation_time,
                "LastUpdatedTime": group.last_updated_time,
                "Tags": [
                    {"Key": tag.key, "Value": tag.value}
                    for tag in group.get_tags()
                ],
            }
        }
        return ActionResult(result)

    def delete_verified_access_group(self) -> ActionResult:
        group_id = self._get_param("VerifiedAccessGroupId")
        group = self.ec2_backend.delete_verified_access_group(group_id)
        result = {
            "VerifiedAccessGroup": {
                "VerifiedAccessGroupId": group.id,
            }
        }
        return ActionResult(result)

    def describe_verified_access_groups(self) -> ActionResult:
        group_ids = self._get_param("VerifiedAccessGroupIds", [])
        instance_id = self._get_param("VerifiedAccessInstanceId")
        filters = self._filters_from_querystring()
        groups = self.ec2_backend.describe_verified_access_groups(
            verified_access_group_ids=group_ids or None,
            verified_access_instance_id=instance_id,
            filters=filters,
        )
        result = {
            "VerifiedAccessGroups": [
                {
                    "VerifiedAccessGroupId": group.id,
                    "VerifiedAccessGroupArn": group.arn,
                    "VerifiedAccessInstanceId": group.verified_access_instance_id,
                    "Description": group.description,
                    "Owner": group.owner_id,
                    "CreationTime": group.creation_time,
                    "LastUpdatedTime": group.last_updated_time,
                    "Tags": [
                        {"Key": tag.key, "Value": tag.value}
                        for tag in group.get_tags()
                    ],
                }
                for group in groups
            ]
        }
        return ActionResult(result)

    def create_verified_access_endpoint(self) -> ActionResult:
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
        result = {
            "VerifiedAccessEndpoint": {
                "VerifiedAccessEndpointId": endpoint.id,
                "VerifiedAccessGroupId": endpoint.verified_access_group_id,
                "VerifiedAccessInstanceId": endpoint.verified_access_instance_id,
                "EndpointType": endpoint.endpoint_type,
                "AttachmentType": endpoint.attachment_type,
                "DomainCertificateArn": endpoint.domain_certificate_arn,
                "ApplicationDomain": endpoint.application_domain,
                "EndpointDomain": endpoint.endpoint_domain,
                "Description": endpoint.description,
                "Status": {"Code": endpoint.state},
                "CreationTime": endpoint.creation_time,
                "LastUpdatedTime": endpoint.last_updated_time,
                "Tags": [
                    {"Key": tag.key, "Value": tag.value}
                    for tag in endpoint.get_tags()
                ],
            }
        }
        return ActionResult(result)

    def delete_verified_access_endpoint(self) -> ActionResult:
        endpoint_id = self._get_param("VerifiedAccessEndpointId")
        endpoint = self.ec2_backend.delete_verified_access_endpoint(endpoint_id)
        result = {
            "VerifiedAccessEndpoint": {
                "VerifiedAccessEndpointId": endpoint.id,
            }
        }
        return ActionResult(result)

    def modify_verified_access_instance(self) -> ActionResult:
        instance_id = self._get_param("VerifiedAccessInstanceId")
        description = self._get_param("Description")
        instance = self.ec2_backend.modify_verified_access_instance(
            verified_access_instance_id=instance_id,
            description=description,
        )
        result = {
            "VerifiedAccessInstance": {
                "VerifiedAccessInstanceId": instance.id,
                "Description": instance.description,
                "FipsEnabled": instance.fips_enabled,
                "CreationTime": instance.creation_time,
                "LastUpdatedTime": instance.last_updated_time,
            }
        }
        return ActionResult(result)

    def modify_verified_access_instance_logging_configuration(self) -> ActionResult:
        instance_id = self._get_param("VerifiedAccessInstanceId")
        instance = self.ec2_backend.get_verified_access_instance(instance_id)
        result = {
            "LoggingConfiguration": {
                "VerifiedAccessInstanceId": instance.id,
                "AccessLogs": {
                    "CloudWatchLogs": {"Enabled": False},
                    "KinesisDataFirehose": {"Enabled": False},
                    "S3": {"Enabled": False},
                },
            }
        }
        return ActionResult(result)

    def modify_verified_access_trust_provider(self) -> ActionResult:
        provider_id = self._get_param("VerifiedAccessTrustProviderId")
        description = self._get_param("Description")
        provider = self.ec2_backend.modify_verified_access_trust_provider(
            verified_access_trust_provider_id=provider_id,
            description=description,
        )
        result = {
            "VerifiedAccessTrustProvider": {
                "VerifiedAccessTrustProviderId": provider.id,
                "Description": provider.description,
                "TrustProviderType": provider.trust_provider_type,
                "PolicyReferenceName": provider.policy_reference_name,
                "CreationTime": provider.creation_time,
                "LastUpdatedTime": provider.last_updated_time,
            }
        }
        return ActionResult(result)

    def modify_verified_access_group(self) -> ActionResult:
        group_id = self._get_param("VerifiedAccessGroupId")
        description = self._get_param("Description")
        group = self.ec2_backend.modify_verified_access_group(
            verified_access_group_id=group_id,
            description=description,
        )
        result = {
            "VerifiedAccessGroup": {
                "VerifiedAccessGroupId": group.id,
                "VerifiedAccessGroupArn": group.arn,
                "VerifiedAccessInstanceId": group.verified_access_instance_id,
                "Description": group.description,
                "CreationTime": group.creation_time,
                "LastUpdatedTime": group.last_updated_time,
            }
        }
        return ActionResult(result)

    def modify_verified_access_group_policy(self) -> ActionResult:
        group_id = self._get_param("VerifiedAccessGroupId")
        policy_document = self._get_param("PolicyDocument", "")
        policy_enabled = self._get_param("PolicyEnabled")
        group = self.ec2_backend.modify_verified_access_group_policy(
            verified_access_group_id=group_id,
            policy_document=policy_document,
            policy_enabled=policy_enabled,
        )
        result = {
            "PolicyEnabled": group.policy_enabled,
            "PolicyDocument": group.policy_document,
        }
        return ActionResult(result)

    def modify_verified_access_endpoint(self) -> ActionResult:
        endpoint_id = self._get_param("VerifiedAccessEndpointId")
        description = self._get_param("Description")
        endpoint = self.ec2_backend.modify_verified_access_endpoint(
            verified_access_endpoint_id=endpoint_id,
            description=description,
        )
        result = {
            "VerifiedAccessEndpoint": {
                "VerifiedAccessEndpointId": endpoint.id,
                "VerifiedAccessGroupId": endpoint.verified_access_group_id,
                "VerifiedAccessInstanceId": endpoint.verified_access_instance_id,
                "EndpointType": endpoint.endpoint_type,
                "Description": endpoint.description,
                "Status": {"Code": endpoint.state},
                "CreationTime": endpoint.creation_time,
                "LastUpdatedTime": endpoint.last_updated_time,
            }
        }
        return ActionResult(result)

    def modify_verified_access_endpoint_policy(self) -> ActionResult:
        endpoint_id = self._get_param("VerifiedAccessEndpointId")
        policy_document = self._get_param("PolicyDocument", "")
        policy_enabled = self._get_param("PolicyEnabled")
        endpoint = self.ec2_backend.modify_verified_access_endpoint_policy(
            verified_access_endpoint_id=endpoint_id,
            policy_document=policy_document,
            policy_enabled=policy_enabled,
        )
        result = {
            "PolicyEnabled": endpoint.policy_enabled,
            "PolicyDocument": endpoint.policy_document,
        }
        return ActionResult(result)

    def describe_verified_access_endpoints(self) -> ActionResult:
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
        result = {
            "VerifiedAccessEndpoints": [
                {
                    "VerifiedAccessEndpointId": endpoint.id,
                    "VerifiedAccessGroupId": endpoint.verified_access_group_id,
                    "VerifiedAccessInstanceId": endpoint.verified_access_instance_id,
                    "EndpointType": endpoint.endpoint_type,
                    "AttachmentType": endpoint.attachment_type,
                    "DomainCertificateArn": endpoint.domain_certificate_arn,
                    "ApplicationDomain": endpoint.application_domain,
                    "EndpointDomain": endpoint.endpoint_domain,
                    "Description": endpoint.description,
                    "Status": {"Code": endpoint.state},
                    "CreationTime": endpoint.creation_time,
                    "LastUpdatedTime": endpoint.last_updated_time,
                    "Tags": [
                        {"Key": tag.key, "Value": tag.value}
                        for tag in endpoint.get_tags()
                    ],
                }
                for endpoint in endpoints
            ]
        }
        return ActionResult(result)

    def attach_verified_access_trust_provider(self) -> ActionResult:
        verified_access_instance_id = self._get_param("VerifiedAccessInstanceId")
        verified_access_trust_provider_id = self._get_param(
            "VerifiedAccessTrustProviderId"
        )
        result = self.ec2_backend.attach_verified_access_trust_provider(
            verified_access_instance_id=verified_access_instance_id,
            verified_access_trust_provider_id=verified_access_trust_provider_id,
        )
        return ActionResult(result)

    def detach_verified_access_trust_provider(self) -> ActionResult:
        verified_access_instance_id = self._get_param("VerifiedAccessInstanceId")
        verified_access_trust_provider_id = self._get_param(
            "VerifiedAccessTrustProviderId"
        )
        result = self.ec2_backend.detach_verified_access_trust_provider(
            verified_access_instance_id=verified_access_instance_id,
            verified_access_trust_provider_id=verified_access_trust_provider_id,
        )
        return ActionResult(result)
