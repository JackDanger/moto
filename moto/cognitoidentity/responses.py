from moto.core.responses import BaseResponse

from .models import CognitoIdentityBackend, cognitoidentity_backends
from .utils import get_random_identity_id


class CognitoIdentityResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="cognito-identity")

    @property
    def backend(self) -> CognitoIdentityBackend:
        return cognitoidentity_backends[self.current_account][self.region]

    def create_identity_pool(self) -> str:
        identity_pool_name = self._get_param("IdentityPoolName")
        allow_unauthenticated_identities = self._get_param(
            "AllowUnauthenticatedIdentities"
        )
        supported_login_providers = self._get_param("SupportedLoginProviders")
        developer_provider_name = self._get_param("DeveloperProviderName")
        open_id_connect_provider_arns = self._get_param("OpenIdConnectProviderARNs")
        cognito_identity_providers = self._get_param("CognitoIdentityProviders")
        saml_provider_arns = self._get_param("SamlProviderARNs")
        pool_tags = self._get_param("IdentityPoolTags")

        return self.backend.create_identity_pool(
            identity_pool_name=identity_pool_name,
            allow_unauthenticated_identities=allow_unauthenticated_identities,
            supported_login_providers=supported_login_providers,
            developer_provider_name=developer_provider_name,
            open_id_connect_provider_arns=open_id_connect_provider_arns,
            cognito_identity_providers=cognito_identity_providers,
            saml_provider_arns=saml_provider_arns,
            tags=pool_tags,
        )

    def update_identity_pool(self) -> str:
        pool_id = self._get_param("IdentityPoolId")
        pool_name = self._get_param("IdentityPoolName")
        allow_unauthenticated = self._get_bool_param("AllowUnauthenticatedIdentities")
        login_providers = self._get_param("SupportedLoginProviders")
        provider_name = self._get_param("DeveloperProviderName")
        provider_arns = self._get_param("OpenIdConnectProviderARNs")
        identity_providers = self._get_param("CognitoIdentityProviders")
        saml_providers = self._get_param("SamlProviderARNs")
        pool_tags = self._get_param("IdentityPoolTags")

        return self.backend.update_identity_pool(
            identity_pool_id=pool_id,
            identity_pool_name=pool_name,
            allow_unauthenticated=allow_unauthenticated,
            login_providers=login_providers,
            provider_name=provider_name,
            provider_arns=provider_arns,
            identity_providers=identity_providers,
            saml_providers=saml_providers,
            tags=pool_tags,
        )

    def get_id(self) -> str:
        return self.backend.get_id(identity_pool_id=self._get_param("IdentityPoolId"))

    def describe_identity_pool(self) -> str:
        return self.backend.describe_identity_pool(self._get_param("IdentityPoolId"))

    def get_credentials_for_identity(self) -> str:
        return self.backend.get_credentials_for_identity(self._get_param("IdentityId"))

    def get_open_id_token_for_developer_identity(self) -> str:
        return self.backend.get_open_id_token_for_developer_identity(
            self._get_param("IdentityId") or get_random_identity_id(self.region)
        )

    def get_open_id_token(self) -> str:
        return self.backend.get_open_id_token(
            self._get_param("IdentityId") or get_random_identity_id(self.region)
        )

    def list_identities(self) -> str:
        return self.backend.list_identities(
            self._get_param("IdentityPoolId") or get_random_identity_id(self.region)
        )

    def list_identity_pools(self) -> str:
        return self.backend.list_identity_pools()

    def delete_identity_pool(self) -> str:
        identity_pool_id = self._get_param("IdentityPoolId")
        self.backend.delete_identity_pool(
            identity_pool_id=identity_pool_id,
        )
        return ""

    def describe_identity(self) -> str:
        identity_id = self._get_param("IdentityId")
        return self.backend.describe_identity(identity_id=identity_id)

    def delete_identities(self) -> str:
        identity_ids_to_delete = self._get_param("IdentityIdsToDelete") or []
        return self.backend.delete_identities(
            identity_ids_to_delete=identity_ids_to_delete
        )

    def get_identity_pool_roles(self) -> str:
        identity_pool_id = self._get_param("IdentityPoolId")
        return self.backend.get_identity_pool_roles(identity_pool_id=identity_pool_id)

    def set_identity_pool_roles(self) -> str:
        identity_pool_id = self._get_param("IdentityPoolId")
        roles = self._get_param("Roles") or {}
        role_mappings = self._get_param("RoleMappings")
        self.backend.set_identity_pool_roles(
            identity_pool_id=identity_pool_id,
            roles=roles,
            role_mappings=role_mappings,
        )
        return ""

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        return self.backend.list_tags_for_resource(resource_arn=resource_arn)

    def tag_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags") or {}
        return self.backend.tag_resource(resource_arn=resource_arn, tags=tags)

    def untag_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys") or []
        return self.backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)

    def lookup_developer_identity(self) -> str:
        identity_pool_id = self._get_param("IdentityPoolId")
        identity_id = self._get_param("IdentityId")
        developer_user_identifier = self._get_param("DeveloperUserIdentifier")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        return self.backend.lookup_developer_identity(
            identity_pool_id=identity_pool_id,
            identity_id=identity_id,
            developer_user_identifier=developer_user_identifier,
            max_results=max_results,
            next_token=next_token,
        )

    def merge_developer_identities(self) -> str:
        source_user_identifier = self._get_param("SourceUserIdentifier")
        destination_user_identifier = self._get_param("DestinationUserIdentifier")
        developer_provider_name = self._get_param("DeveloperProviderName")
        identity_pool_id = self._get_param("IdentityPoolId")
        return self.backend.merge_developer_identities(
            source_user_identifier=source_user_identifier,
            destination_user_identifier=destination_user_identifier,
            developer_provider_name=developer_provider_name,
            identity_pool_id=identity_pool_id,
        )

    def unlink_developer_identity(self) -> str:
        identity_id = self._get_param("IdentityId")
        identity_pool_id = self._get_param("IdentityPoolId")
        developer_provider_name = self._get_param("DeveloperProviderName")
        developer_user_identifier = self._get_param("DeveloperUserIdentifier")
        self.backend.unlink_developer_identity(
            identity_id=identity_id,
            identity_pool_id=identity_pool_id,
            developer_provider_name=developer_provider_name,
            developer_user_identifier=developer_user_identifier,
        )
        return ""

    def unlink_identity(self) -> str:
        identity_id = self._get_param("IdentityId")
        logins = self._get_param("Logins") or {}
        logins_to_remove = self._get_param("LoginsToRemove") or []
        self.backend.unlink_identity(
            identity_id=identity_id,
            logins=logins,
            logins_to_remove=logins_to_remove,
        )
        return ""

    def get_principal_tag_attribute_map(self) -> str:
        identity_pool_id = self._get_param("IdentityPoolId")
        identity_provider_name = self._get_param("IdentityProviderName")
        return self.backend.get_principal_tag_attribute_map(
            identity_pool_id=identity_pool_id,
            identity_provider_name=identity_provider_name,
        )

    def set_principal_tag_attribute_map(self) -> str:
        identity_pool_id = self._get_param("IdentityPoolId")
        identity_provider_name = self._get_param("IdentityProviderName")
        use_defaults = self._get_param("UseDefaults")
        principal_tags = self._get_param("PrincipalTags")
        return self.backend.set_principal_tag_attribute_map(
            identity_pool_id=identity_pool_id,
            identity_provider_name=identity_provider_name,
            use_defaults=use_defaults,
            principal_tags=principal_tags,
        )
