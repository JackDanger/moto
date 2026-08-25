from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import (
    random_verified_access_endpoint_id,
    random_verified_access_group_id,
    random_verified_access_instance_id,
    random_verified_access_trust_provider_id,
)
from .core import TaggedEC2Resource


class VerifiedAccessInstance(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        description: str = "",
        fips_enabled: bool = False,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_verified_access_instance_id()
        self.description = description
        self.fips_enabled = fips_enabled
        self.state = "active"
        self.verified_access_trust_provider_ids: list[str] = []
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def last_updated_time(self) -> str:
        return self.creation_time

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id


class VerifiedAccessTrustProvider(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        trust_provider_type: str,
        policy_reference_name: str,
        user_trust_provider_type: Optional[str] = None,
        device_trust_provider_type: Optional[str] = None,
        oidc_options: Optional[dict[str, str]] = None,
        device_options: Optional[dict[str, str]] = None,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_verified_access_trust_provider_id()
        self.trust_provider_type = trust_provider_type
        self.policy_reference_name = policy_reference_name
        self.user_trust_provider_type = user_trust_provider_type
        self.device_trust_provider_type = device_trust_provider_type
        self.oidc_options = oidc_options
        self.device_options = device_options
        self.description = description
        self.state = "active"
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def last_updated_time(self) -> str:
        return self.creation_time


class VerifiedAccessGroup(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        verified_access_instance_id: str,
        description: str = "",
        policy_document: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_verified_access_group_id()
        self.verified_access_instance_id = verified_access_instance_id
        self.description = description
        self.policy_document = policy_document
        self.policy_enabled: bool = False
        self.state = "active"
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def last_updated_time(self) -> str:
        return self.creation_time

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:verified-access-group/{self.id}"
        )


class VerifiedAccessEndpoint(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        verified_access_group_id: str,
        endpoint_type: str,
        attachment_type: str = "vpc",
        domain_certificate_arn: str = "",
        application_domain: str = "",
        endpoint_domain_prefix: str = "",
        security_group_ids: Optional[list[str]] = None,
        load_balancer_options: Optional[dict[str, Any]] = None,
        network_interface_options: Optional[dict[str, Any]] = None,
        description: str = "",
        policy_document: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_verified_access_endpoint_id()
        self.verified_access_group_id = verified_access_group_id
        self.endpoint_type = endpoint_type
        self.attachment_type = attachment_type
        self.domain_certificate_arn = domain_certificate_arn
        self.application_domain = application_domain
        self.endpoint_domain_prefix = endpoint_domain_prefix
        self.endpoint_domain = f"{self.id}.prod.verified-access.{backend.region_name}.amazonaws.com"
        self.security_group_ids = security_group_ids or []
        self.load_balancer_options = load_balancer_options
        self.network_interface_options = network_interface_options
        self.description = description
        self.policy_document = policy_document
        self.policy_enabled: bool = False
        self.state = "active"
        self._created_at = utcnow()
        self.add_tags(tags or {})

        # Look up the instance ID from the group
        group = backend.verified_access_groups.get(verified_access_group_id)
        self.verified_access_instance_id = (
            group.verified_access_instance_id if group else ""
        )

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def last_updated_time(self) -> str:
        return self.creation_time


class VerifiedAccessBackend:
    def __init__(self) -> None:
        self.verified_access_instances: dict[str, VerifiedAccessInstance] = {}
        self.verified_access_trust_providers: dict[str, VerifiedAccessTrustProvider] = {}
        self.verified_access_groups: dict[str, VerifiedAccessGroup] = {}
        self.verified_access_endpoints: dict[str, VerifiedAccessEndpoint] = {}

    def create_verified_access_instance(
        self,
        description: str = "",
        fips_enabled: bool = False,
        tags: Optional[dict[str, str]] = None,
    ) -> VerifiedAccessInstance:
        instance = VerifiedAccessInstance(
            self, description=description, fips_enabled=fips_enabled, tags=tags
        )
        self.verified_access_instances[instance.id] = instance
        return instance

    def delete_verified_access_instance(
        self, verified_access_instance_id: str
    ) -> VerifiedAccessInstance:
        instance = self.verified_access_instances.get(verified_access_instance_id)
        if not instance:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessInstanceId.NotFound",
                f"The verified access instance ID '{verified_access_instance_id}' does not exist",
            )
        return self.verified_access_instances.pop(verified_access_instance_id)

    def describe_verified_access_instances(
        self,
        verified_access_instance_ids: Optional[list[str]] = None,
        filters: Any = None,
    ) -> list[VerifiedAccessInstance]:
        instances = list(self.verified_access_instances.values())
        if verified_access_instance_ids:
            instances = [i for i in instances if i.id in verified_access_instance_ids]
        return instances

    def create_verified_access_trust_provider(
        self,
        trust_provider_type: str,
        policy_reference_name: str,
        user_trust_provider_type: Optional[str] = None,
        device_trust_provider_type: Optional[str] = None,
        oidc_options: Optional[dict[str, str]] = None,
        device_options: Optional[dict[str, str]] = None,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> VerifiedAccessTrustProvider:
        provider = VerifiedAccessTrustProvider(
            self,
            trust_provider_type=trust_provider_type,
            policy_reference_name=policy_reference_name,
            user_trust_provider_type=user_trust_provider_type,
            device_trust_provider_type=device_trust_provider_type,
            oidc_options=oidc_options,
            device_options=device_options,
            description=description,
            tags=tags,
        )
        self.verified_access_trust_providers[provider.id] = provider
        return provider

    def delete_verified_access_trust_provider(
        self, verified_access_trust_provider_id: str
    ) -> VerifiedAccessTrustProvider:
        provider = self.verified_access_trust_providers.get(
            verified_access_trust_provider_id
        )
        if not provider:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessTrustProviderId.NotFound",
                f"The verified access trust provider ID '{verified_access_trust_provider_id}' does not exist",
            )
        return self.verified_access_trust_providers.pop(
            verified_access_trust_provider_id
        )

    def describe_verified_access_trust_providers(
        self,
        verified_access_trust_provider_ids: Optional[list[str]] = None,
        filters: Any = None,
    ) -> list[VerifiedAccessTrustProvider]:
        providers = list(self.verified_access_trust_providers.values())
        if verified_access_trust_provider_ids:
            providers = [
                p for p in providers if p.id in verified_access_trust_provider_ids
            ]
        return providers

    def create_verified_access_group(
        self,
        verified_access_instance_id: str,
        description: str = "",
        policy_document: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> VerifiedAccessGroup:
        group = VerifiedAccessGroup(
            self,
            verified_access_instance_id=verified_access_instance_id,
            description=description,
            policy_document=policy_document,
            tags=tags,
        )
        self.verified_access_groups[group.id] = group
        return group

    def delete_verified_access_group(
        self, verified_access_group_id: str
    ) -> VerifiedAccessGroup:
        group = self.verified_access_groups.get(verified_access_group_id)
        if not group:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessGroupId.NotFound",
                f"The verified access group ID '{verified_access_group_id}' does not exist",
            )
        return self.verified_access_groups.pop(verified_access_group_id)

    def describe_verified_access_groups(
        self,
        verified_access_group_ids: Optional[list[str]] = None,
        verified_access_instance_id: Optional[str] = None,
        filters: Any = None,
    ) -> list[VerifiedAccessGroup]:
        groups = list(self.verified_access_groups.values())
        if verified_access_group_ids:
            groups = [g for g in groups if g.id in verified_access_group_ids]
        if verified_access_instance_id:
            groups = [
                g
                for g in groups
                if g.verified_access_instance_id == verified_access_instance_id
            ]
        return groups

    def create_verified_access_endpoint(
        self,
        verified_access_group_id: str,
        endpoint_type: str,
        attachment_type: str = "vpc",
        domain_certificate_arn: str = "",
        application_domain: str = "",
        endpoint_domain_prefix: str = "",
        security_group_ids: Optional[list[str]] = None,
        load_balancer_options: Optional[dict[str, Any]] = None,
        network_interface_options: Optional[dict[str, Any]] = None,
        description: str = "",
        policy_document: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> VerifiedAccessEndpoint:
        endpoint = VerifiedAccessEndpoint(
            self,
            verified_access_group_id=verified_access_group_id,
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
        self.verified_access_endpoints[endpoint.id] = endpoint
        return endpoint

    def delete_verified_access_endpoint(
        self, verified_access_endpoint_id: str
    ) -> VerifiedAccessEndpoint:
        endpoint = self.verified_access_endpoints.get(verified_access_endpoint_id)
        if not endpoint:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessEndpointId.NotFound",
                f"The verified access endpoint ID '{verified_access_endpoint_id}' does not exist",
            )
        return self.verified_access_endpoints.pop(verified_access_endpoint_id)

    def describe_verified_access_endpoints(
        self,
        verified_access_endpoint_ids: Optional[list[str]] = None,
        verified_access_group_id: Optional[str] = None,
        verified_access_instance_id: Optional[str] = None,
        filters: Any = None,
    ) -> list[VerifiedAccessEndpoint]:
        endpoints = list(self.verified_access_endpoints.values())
        if verified_access_endpoint_ids:
            endpoints = [e for e in endpoints if e.id in verified_access_endpoint_ids]
        if verified_access_group_id:
            endpoints = [
                e
                for e in endpoints
                if e.verified_access_group_id == verified_access_group_id
            ]
        if verified_access_instance_id:
            endpoints = [
                e
                for e in endpoints
                if e.verified_access_instance_id == verified_access_instance_id
            ]
        return endpoints

    def get_verified_access_instance(
        self, verified_access_instance_id: str
    ) -> VerifiedAccessInstance:
        instance = self.verified_access_instances.get(verified_access_instance_id)
        if not instance:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessInstanceId.NotFound",
                f"The verified access instance ID '{verified_access_instance_id}' does not exist",
            )
        return instance

    def modify_verified_access_instance(
        self,
        verified_access_instance_id: str,
        description: Optional[str] = None,
    ) -> VerifiedAccessInstance:
        instance = self.get_verified_access_instance(verified_access_instance_id)
        if description is not None:
            instance.description = description
        return instance

    def modify_verified_access_trust_provider(
        self,
        verified_access_trust_provider_id: str,
        description: Optional[str] = None,
        oidc_options: Optional[dict[str, str]] = None,
        device_options: Optional[dict[str, str]] = None,
    ) -> VerifiedAccessTrustProvider:
        provider = self.verified_access_trust_providers.get(
            verified_access_trust_provider_id
        )
        if not provider:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessTrustProviderId.NotFound",
                f"The verified access trust provider ID '{verified_access_trust_provider_id}' does not exist",
            )
        if description is not None:
            provider.description = description
        if oidc_options is not None:
            provider.oidc_options = oidc_options
        if device_options is not None:
            provider.device_options = device_options
        return provider

    def modify_verified_access_group(
        self,
        verified_access_group_id: str,
        verified_access_instance_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> VerifiedAccessGroup:
        group = self.verified_access_groups.get(verified_access_group_id)
        if not group:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessGroupId.NotFound",
                f"The verified access group ID '{verified_access_group_id}' does not exist",
            )
        if verified_access_instance_id is not None:
            group.verified_access_instance_id = verified_access_instance_id
        if description is not None:
            group.description = description
        return group

    def modify_verified_access_group_policy(
        self,
        verified_access_group_id: str,
        policy_enabled: Optional[bool] = None,
        policy_document: Optional[str] = None,
    ) -> VerifiedAccessGroup:
        group = self.verified_access_groups.get(verified_access_group_id)
        if not group:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessGroupId.NotFound",
                f"The verified access group ID '{verified_access_group_id}' does not exist",
            )
        if policy_enabled is not None:
            group.policy_enabled = policy_enabled
        if policy_document is not None:
            group.policy_document = policy_document
        return group

    def modify_verified_access_endpoint(
        self,
        verified_access_endpoint_id: str,
        verified_access_group_id: Optional[str] = None,
        description: Optional[str] = None,
        load_balancer_options: Optional[dict[str, Any]] = None,
        network_interface_options: Optional[dict[str, Any]] = None,
    ) -> VerifiedAccessEndpoint:
        endpoint = self.verified_access_endpoints.get(verified_access_endpoint_id)
        if not endpoint:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessEndpointId.NotFound",
                f"The verified access endpoint ID '{verified_access_endpoint_id}' does not exist",
            )
        if verified_access_group_id is not None:
            endpoint.verified_access_group_id = verified_access_group_id
        if description is not None:
            endpoint.description = description
        if load_balancer_options is not None:
            endpoint.load_balancer_options = load_balancer_options
        if network_interface_options is not None:
            endpoint.network_interface_options = network_interface_options
        return endpoint

    def modify_verified_access_endpoint_policy(
        self,
        verified_access_endpoint_id: str,
        policy_enabled: Optional[bool] = None,
        policy_document: Optional[str] = None,
    ) -> VerifiedAccessEndpoint:
        endpoint = self.verified_access_endpoints.get(verified_access_endpoint_id)
        if not endpoint:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessEndpointId.NotFound",
                f"The verified access endpoint ID '{verified_access_endpoint_id}' does not exist",
            )
        if policy_enabled is not None:
            endpoint.policy_enabled = policy_enabled
        if policy_document is not None:
            endpoint.policy_document = policy_document
        return endpoint

    def attach_verified_access_trust_provider(
        self,
        verified_access_instance_id: str,
        verified_access_trust_provider_id: str,
    ) -> dict[str, Any]:
        instance = self.get_verified_access_instance(verified_access_instance_id)
        provider = self.verified_access_trust_providers.get(
            verified_access_trust_provider_id
        )
        if not provider:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessTrustProviderId.NotFound",
                f"The verified access trust provider ID '{verified_access_trust_provider_id}' does not exist",
            )
        if verified_access_trust_provider_id not in instance.verified_access_trust_provider_ids:
            instance.verified_access_trust_provider_ids.append(verified_access_trust_provider_id)
        return {
            "VerifiedAccessTrustProvider": {
                "VerifiedAccessTrustProviderId": provider.id,
                "TrustProviderType": provider.trust_provider_type,
                "PolicyReferenceName": provider.policy_reference_name,
                "Description": provider.description,
            },
            "VerifiedAccessInstance": {
                "VerifiedAccessInstanceId": instance.id,
                "Description": instance.description,
            },
        }

    def detach_verified_access_trust_provider(
        self,
        verified_access_instance_id: str,
        verified_access_trust_provider_id: str,
    ) -> dict[str, Any]:
        instance = self.get_verified_access_instance(verified_access_instance_id)
        provider = self.verified_access_trust_providers.get(
            verified_access_trust_provider_id
        )
        if not provider:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidVerifiedAccessTrustProviderId.NotFound",
                f"The verified access trust provider ID '{verified_access_trust_provider_id}' does not exist",
            )
        if verified_access_trust_provider_id in instance.verified_access_trust_provider_ids:
            instance.verified_access_trust_provider_ids.remove(verified_access_trust_provider_id)
        return {
            "VerifiedAccessTrustProvider": {
                "VerifiedAccessTrustProviderId": provider.id,
                "TrustProviderType": provider.trust_provider_type,
                "PolicyReferenceName": provider.policy_reference_name,
                "Description": provider.description,
            },
            "VerifiedAccessInstance": {
                "VerifiedAccessInstanceId": instance.id,
                "Description": instance.description,
            },
        }
