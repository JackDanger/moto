"""TransferBackend class with methods for supported APIs."""

from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.utils import camelcase_to_underscores, unix_time
from moto.moto_api._internal import mock_random
from moto.transfer.exceptions import (
    AccessNotFound,
    ConnectorNotFound,
    InvalidRequestError,
    PublicKeyNotFound,
    ResourceNotFound,

    ServerNotFound,
    UserNotFound,
)

from .types import (
    Access,
    Agreement,
    Certificate,
    Connector,
    HostKey,
    Profile,
    SECURITY_POLICIES,

    Server,
    ServerDomain,
    ServerEndpointType,
    ServerIdentityProviderType,
    ServerProtocols,
    ServerState,
    User,
    UserHomeDirectoryType,
    WebApp,
    WebAppCustomization,
    Workflow,
)


class TransferBackend(BaseBackend):
    """Implementation of Transfer APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.servers: dict[str, Server] = {}
        self.certificates: dict[str, Certificate] = {}
        self.connectors: dict[str, Connector] = {}
        self.profiles: dict[str, Profile] = {}
        self.workflows: dict[str, Workflow] = {}
        self.web_apps: dict[str, WebApp] = {}
        # Tag store keyed by ARN
        self.tagger: dict[str, list[dict[str, str]]] = {}

    # ---- Helper to find taggable resource by ARN ----
    def _get_tags_for_arn(self, arn: str) -> list[dict[str, str]]:
        return self.tagger.get(arn, [])

    def _set_tags_for_arn(self, arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger[arn] = tags

    def _add_tags(self, arn: str, tags: list[dict[str, str]]) -> None:
        existing = {t["Key"]: t for t in self.tagger.get(arn, [])}
        for tag in tags:
            existing[tag["Key"]] = tag
        self.tagger[arn] = list(existing.values())

    def _remove_tags(self, arn: str, tag_keys: list[str]) -> None:
        self.tagger[arn] = [
            t for t in self.tagger.get(arn, []) if t["Key"] not in tag_keys
        ]

    def _get_server(self, server_id: str) -> Server:
        if server_id not in self.servers:
            raise ServerNotFound(server_id=server_id)
        return self.servers[server_id]

    # ======== Server operations =

    def create_server(
        self,
        certificate: Optional[str],
        domain: Optional[ServerDomain],
        endpoint_details: Optional[dict[str, Any]],
        endpoint_type: Optional[ServerEndpointType],
        host_key: str,
        identity_provider_details: Optional[dict[str, Any]],
        identity_provider_type: Optional[ServerIdentityProviderType],
        logging_role: Optional[str],
        post_authentication_login_banner: Optional[str],
        pre_authentication_login_banner: Optional[str],
        protocols: Optional[list[ServerProtocols]],
        protocol_details: Optional[dict[str, Any]],
        security_policy_name: Optional[str],
        tags: Optional[list[dict[str, str]]],
        workflow_details: Optional[dict[str, Any]],
        structured_log_destinations: Optional[list[str]],
        s3_storage_options: Optional[dict[str, Optional[str]]],
    ) -> str:
        server = Server(
            region_name=self.region_name,
            account_id=self.account_id,
            certificate=certificate,
            domain=domain,
            endpoint_type=endpoint_type,
            host_key_fingerprint=host_key,
            identity_provider_type=identity_provider_type,
            logging_role=logging_role,
            post_authentication_login_banner=post_authentication_login_banner,
            pre_authentication_login_banner=pre_authentication_login_banner,
            protocols=protocols,
            security_policy_name=security_policy_name,
            structured_log_destinations=structured_log_destinations,
            tags=(tags or []),
        )
        if endpoint_details is not None:
            endpoint_details = {
                "address_allocation_ids": endpoint_details.get("AddressAllocationIds"),
                "subnet_ids": endpoint_details.get("SubnetIds"),
                "vpc_endpoint_id": endpoint_details.get("VpcEndpointId"),
                "vpc_id": endpoint_details.get("VpcId"),
                "security_group_ids": endpoint_details.get("SecurityGroupIds"),
            }
            server.endpoint_details = endpoint_details
        if identity_provider_details is not None:
            identity_provider_details = {
                "url": identity_provider_details.get("Url"),
                "invocation_role": identity_provider_details.get("InvocationRole"),
                "directory_id": identity_provider_details.get("DirectoryId"),
                "function": identity_provider_details.get("Function"),
                "sftp_authentication_methods": identity_provider_details.get(
                    "SftpAuthenticationMethods"
                ),
            }
            server.identity_provider_details = identity_provider_details
        if protocol_details is not None:
            protocol_details = {
                "passive_ip": protocol_details.get("PassiveIp"),
                "tls_session_resumption_mode": protocol_details.get(
                    "TlsSessionResumptionMode"
                ),
                "set_stat_option": protocol_details.get("SetStatOption"),
                "as2_transports": protocol_details.get("As2Transports"),
            }
            server.protocol_details = protocol_details
        if s3_storage_options is not None:
            server.s3_storage_options = {
                "directory_listing_optimization": s3_storage_options.get(
                    "DirectoryListingOptimization"
                )
            }
        if workflow_details is not None:
            server.workflow_details = {
                "on_upload": [
                    {
                        "workflow_id": workflow.get("WorkflowId"),
                        "execution_role": workflow.get("ExecutionRole"),
                    }
                    for workflow in (workflow_details.get("OnUpload") or [])
                ],
                "on_partial_upload": [
                    {
                        "workflow_id": workflow.get("WorkflowId"),
                        "execution_role": workflow.get("ExecutionRole"),
                    }
                    for workflow in (workflow_details.get("OnPartialUpload") or [])
                ],
            }
        server_id = server.server_id
        self.servers[server_id] = server
        if tags:
            self._add_tags(server.arn, tags)
        return server_id

    def describe_server(self, server_id: str) -> Server:
        return self._get_server(server_id)

    def delete_server(self, server_id: str) -> None:
        server = self._get_server(server_id)
        self.tagger.pop(server.arn, None)
        del self.servers[server_id]

    def update_server(
        self,
        server_id: str,
        certificate: Optional[str],
        protocol_details: Optional[dict[str, Any]],
        endpoint_details: Optional[dict[str, Any]],
        endpoint_type: Optional[str],
        host_key: Optional[str],
        identity_provider_details: Optional[dict[str, Any]],
        logging_role: Optional[str],
        post_authentication_login_banner: Optional[str],
        pre_authentication_login_banner: Optional[str],
        protocols: Optional[list[str]],
        security_policy_name: Optional[str],
        workflow_details: Optional[dict[str, Any]],
        structured_log_destinations: Optional[list[str]],
        s3_storage_options: Optional[dict[str, Optional[str]]],
    ) -> str:
        server = self._get_server(server_id)
        if certificate is not None:
            server.certificate = certificate
        if endpoint_type is not None:
            server.endpoint_type = endpoint_type
        if host_key is not None:
            server.host_key_fingerprint = host_key
        if logging_role is not None:
            server.logging_role = logging_role
        if post_authentication_login_banner is not None:
            server.post_authentication_login_banner = post_authentication_login_banner
        if pre_authentication_login_banner is not None:
            server.pre_authentication_login_banner = pre_authentication_login_banner
        if protocols is not None:
            server.protocols = protocols
        if security_policy_name is not None:
            server.security_policy_name = security_policy_name
        if structured_log_destinations is not None:
            server.structured_log_destinations = structured_log_destinations
        if endpoint_details is not None:
            server.endpoint_details = {
                "address_allocation_ids": endpoint_details.get("AddressAllocationIds"),
                "subnet_ids": endpoint_details.get("SubnetIds"),
                "vpc_endpoint_id": endpoint_details.get("VpcEndpointId"),
                "vpc_id": endpoint_details.get("VpcId"),
                "security_group_ids": endpoint_details.get("SecurityGroupIds"),
            }
        if identity_provider_details is not None:
            server.identity_provider_details = {
                "url": identity_provider_details.get("Url"),
                "invocation_role": identity_provider_details.get("InvocationRole"),
                "directory_id": identity_provider_details.get("DirectoryId"),
                "function": identity_provider_details.get("Function"),
                "sftp_authentication_methods": identity_provider_details.get(
                    "SftpAuthenticationMethods"
                ),
            }
        if protocol_details is not None:
            server.protocol_details = {
                "passive_ip": protocol_details.get("PassiveIp"),
                "tls_session_resumption_mode": protocol_details.get(
                    "TlsSessionResumptionMode"
                ),
                "set_stat_option": protocol_details.get("SetStatOption"),
                "as2_transports": protocol_details.get("As2Transports"),
            }
        if s3_storage_options is not None:
            server.s3_storage_options = {
                "directory_listing_optimization": s3_storage_options.get(
                    "DirectoryListingOptimization"
                )
            }
        if workflow_details is not None:
            server.workflow_details = {
                "on_upload": [
                    {
                        "workflow_id": w.get("WorkflowId"),
                        "execution_role": w.get("ExecutionRole"),
                    }
                    for w in (workflow_details.get("OnUpload") or [])
                ],
                "on_partial_upload": [
                    {
                        "workflow_id": w.get("WorkflowId"),
                        "execution_role": w.get("ExecutionRole"),
                    }
                    for w in (workflow_details.get("OnPartialUpload") or [])
                ],
            }
        return server_id

    def start_server(self, server_id: str) -> None:
        server = self._get_server(server_id)
        server.state = ServerState.ONLINE

    def stop_server(self, server_id: str) -> None:
        server = self._get_server(server_id)
        server.state = ServerState.OFFLINE

    def list_servers(self) -> list[Server]:
        return list(self.servers.values())

    # ======== User operations ========

    def create_user(
        self,
        home_directory: Optional[str],
        home_directory_type: Optional[UserHomeDirectoryType],
        home_directory_mappings: Optional[list[dict[str, Optional[str]]]],
        policy: Optional[str],
        posix_profile: Optional[dict[str, Any]],
        role: str,
        server_id: str,
        ssh_public_key_body: Optional[str],
        tags: Optional[list[dict[str, str]]],
        user_name: str,
    ) -> tuple[str, str]:
        server = self._get_server(server_id)
        user = User(
            region_name=self.region_name,
            account_id=self.account_id,
            server_id=server_id,
            home_directory=home_directory,
            home_directory_type=home_directory_type,
            policy=policy,
            role=role,
            tags=(tags or []),
            user_name=user_name,
        )
        if home_directory_mappings:
            for mapping in home_directory_mappings:
                user.home_directory_mappings.append(
                    {
                        "entry": mapping.get("Entry"),
                        "target": mapping.get("Target"),
                        "type": mapping.get("Type"),
                    }
                )
        if posix_profile is not None:
            posix_profile = {
                "gid": posix_profile.get("Gid"),
                "uid": posix_profile.get("Uid"),
                "secondary_gids": posix_profile.get("SecondaryGids"),
            }
            user.posix_profile = posix_profile
        if ssh_public_key_body is not None:
            now = unix_time()
            ssh_public_keys = [
                {
                    "date_imported": str(now),
                    "ssh_public_key_body": ssh_public_key_body,
                    "ssh_public_key_id": "mock_ssh_public_key_id_{ssh_public_key_body}_{now}",
                }
            ]
            user.ssh_public_keys = ssh_public_keys
        server._users.append(user)
        server.user_count += 1
        if tags:
            self._add_tags(user.arn, tags)
        return server_id, user_name

    def describe_user(self, server_id: str, user_name: str) -> tuple[str, User]:
        server = self._get_server(server_id)
        for user in server._users:
            if user.user_name == user_name:
                return server_id, user
        raise UserNotFound(user_name=user_name, server_id=server_id)

    def delete_user(self, server_id: str, user_name: str) -> None:
        server = self._get_server(server_id)
        for i, user in enumerate(server._users):
            if user.user_name == user_name:
                self.tagger.pop(user.arn, None)
                del server._users[i]
                server.user_count -= 1
                return
        raise UserNotFound(server_id=server_id, user_name=user_name)

    def update_user(
        self,
        server_id: str,
        user_name: str,
        home_directory: Optional[str],
        home_directory_type: Optional[str],
        home_directory_mappings: Optional[list[dict[str, Optional[str]]]],
        policy: Optional[str],
        posix_profile: Optional[dict[str, Any]],
        role: Optional[str],
    ) -> tuple[str, str]:
        server = self._get_server(server_id)
        for user in server._users:
            if user.user_name == user_name:
                if home_directory is not None:
                    user.home_directory = home_directory
                if home_directory_type is not None:
                    user.home_directory_type = home_directory_type
                if home_directory_mappings is not None:
                    user.home_directory_mappings = [
                        {
                            "entry": m.get("Entry"),
                            "target": m.get("Target"),
                            "type": m.get("Type"),
                        }
                        for m in home_directory_mappings
                    ]
                if policy is not None:
                    user.policy = policy
                if posix_profile is not None:
                    user.posix_profile = {
                        "gid": posix_profile.get("Gid"),
                        "uid": posix_profile.get("Uid"),
                        "secondary_gids": posix_profile.get("SecondaryGids"),
                    }
                if role is not None:
                    user.role = role
                return server_id, user_name
        raise UserNotFound(user_name=user_name, server_id=server_id)

    def list_users(self, server_id: str) -> tuple[str, list[User]]:
        server = self._get_server(server_id)
        return server_id, server._users

    # ======== SSH Public Key operations ========

    def import_ssh_public_key(
        self, server_id: str, ssh_public_key_body: str, user_name: str
    ) -> tuple[str, str, str]:
        server = self._get_server(server_id)
        for user in server._users:
            if user.user_name == user_name:
                date_imported = unix_time()
                ssh_public_key_id = (
                    f"{server_id}:{user_name}:public_key:{date_imported}"
                )
                key = {
                    "ssh_public_key_id": ssh_public_key_id,
                    "ssh_public_key_body": ssh_public_key_body,
                    "date_imported": str(date_imported),
                }
                user.ssh_public_keys.append(key)
                return server_id, ssh_public_key_id, user_name
        raise UserNotFound(user_name=user_name, server_id=server_id)

    def delete_ssh_public_key(
        self, server_id: str, ssh_public_key_id: str, user_name: str
    ) -> None:
        server = self._get_server(server_id)
        for i, user in enumerate(server._users):
            if user.user_name == user_name:
                for j, key in enumerate(
                    server._users[i].ssh_public_keys
                ):
                    if key["ssh_public_key_id"] == ssh_public_key_id:
                        del user.ssh_public_keys[j]
                        return
                raise PublicKeyNotFound(
                    user_name=user_name,
                    server_id=server_id,
                    ssh_public_key_id=ssh_public_key_id,
                )
        raise UserNotFound(user_name=user_name, server_id=server_id)

    # ======== Access operations ========

    def create_access(
        self,
        server_id: str,
        external_id: str,
        home_directory: Optional[str],
        home_directory_type: Optional[str],
        home_directory_mappings: Optional[list[dict[str, Optional[str]]]],
        policy: Optional[str],
        posix_profile: Optional[dict[str, Any]],
        role: str,
    ) -> tuple[str, str]:
        server = self._get_server(server_id)
        access = Access(
            region_name=self.region_name,
            account_id=self.account_id,
            server_id=server_id,
            external_id=external_id,
            home_directory=home_directory,
            home_directory_type=home_directory_type,
            policy=policy,
            role=role,
        )
        if home_directory_mappings:
            access.home_directory_mappings = [
                {"entry": m.get("Entry"), "target": m.get("Target")}
                for m in home_directory_mappings
            ]
        if posix_profile is not None:
            access.posix_profile = {
                "uid": posix_profile.get("Uid"),
                "gid": posix_profile.get("Gid"),
                "secondary_gids": posix_profile.get("SecondaryGids"),
            }
        server._accesses.append(access)
        return server_id, external_id

    def describe_access(self, server_id: str, external_id: str) -> tuple[str, Access]:
        server = self._get_server(server_id)
        for access in server._accesses:
            if access.external_id == external_id:
                return server_id, access
        raise AccessNotFound(server_id=server_id, external_id=external_id)

    def delete_access(self, server_id: str, external_id: str) -> None:
        server = self._get_server(server_id)
        for i, access in enumerate(server._accesses):
            if access.external_id == external_id:
                del server._accesses[i]
                return
        raise AccessNotFound(server_id=server_id, external_id=external_id)

    def update_access(
        self,
        server_id: str,
        external_id: str,
        home_directory: Optional[str],
        home_directory_type: Optional[str],
        home_directory_mappings: Optional[list[dict[str, Optional[str]]]],
        policy: Optional[str],
        posix_profile: Optional[dict[str, Any]],
        role: Optional[str],
    ) -> tuple[str, str]:
        server = self._get_server(server_id)
        for access in server._accesses:
            if access.external_id == external_id:
                if home_directory is not None:
                    access.home_directory = home_directory
                if home_directory_type is not None:
                    access.home_directory_type = home_directory_type
                if home_directory_mappings is not None:
                    access.home_directory_mappings = [
                        {"entry": m.get("Entry"), "target": m.get("Target")}
                        for m in home_directory_mappings
                    ]
                if policy is not None:
                    access.policy = policy
                if posix_profile is not None:
                    access.posix_profile = {
                        "uid": posix_profile.get("Uid"),
                        "gid": posix_profile.get("Gid"),
                        "secondary_gids": posix_profile.get("SecondaryGids"),
                    }
                if role is not None:
                    access.role = role
                return server_id, external_id
        raise AccessNotFound(server_id=server_id, external_id=external_id)

    def list_accesses(self, server_id: str) -> tuple[str, list[Access]]:
        server = self._get_server(server_id)
        return server_id, server._accesses

    # ======== Agreement operations ========

    def create_agreement(
        self,
        server_id: str,
        local_profile_id: str,
        partner_profile_id: str,
        access_role: str,
        description: Optional[str],
        base_directory: Optional[str],
        status: Optional[str],
        tags: Optional[list[dict[str, str]]],
        preserve_filename: Optional[str],
        enforce_message_signing: Optional[str],
        custom_directories: Optional[dict[str, Any]],
    ) -> str:
        server = self._get_server(server_id)
        agreement = Agreement(
            region_name=self.region_name,
            account_id=self.account_id,
            server_id=server_id,
            local_profile_id=local_profile_id,
            partner_profile_id=partner_profile_id,
            access_role=access_role,
            description=description,
            base_directory=base_directory,
            status=status or "ACTIVE",
            tags=(tags or []),
            preserve_filename=preserve_filename,
            enforce_message_signing=enforce_message_signing,
            custom_directories=custom_directories,
        )
        server._agreements.append(agreement)
        if tags:
            self._add_tags(agreement.arn, tags)
        return agreement.agreement_id

    def describe_agreement(
        self, agreement_id: str, server_id: str
    ) -> Agreement:
        server = self._get_server(server_id)
        for agreement in server._agreements:
            if agreement.agreement_id == agreement_id:
                return agreement
        raise ResourceNotFound("Agreement", agreement_id)

    def delete_agreement(self, agreement_id: str, server_id: str) -> None:
        server = self._get_server(server_id)
        for i, agreement in enumerate(server._agreements):
            if agreement.agreement_id == agreement_id:
                self.tagger.pop(agreement.arn, None)
                del server._agreements[i]
                return
        raise ResourceNotFound("Agreement", agreement_id)

    def update_agreement(
        self,
        agreement_id: str,
        server_id: str,
        description: Optional[str],
        status: Optional[str],
        local_profile_id: Optional[str],
        partner_profile_id: Optional[str],
        base_directory: Optional[str],
        access_role: Optional[str],
        preserve_filename: Optional[str],
        enforce_message_signing: Optional[str],
        custom_directories: Optional[dict[str, Any]],
    ) -> str:
        server = self._get_server(server_id)
        for agreement in server._agreements:
            if agreement.agreement_id == agreement_id:
                if description is not None:
                    agreement.description = description
                if status is not None:
                    agreement.status = status
                if local_profile_id is not None:
                    agreement.local_profile_id = local_profile_id
                if partner_profile_id is not None:
                    agreement.partner_profile_id = partner_profile_id
                if base_directory is not None:
                    agreement.base_directory = base_directory
                if access_role is not None:
                    agreement.access_role = access_role
                if preserve_filename is not None:
                    agreement.preserve_filename = preserve_filename
                if enforce_message_signing is not None:
                    agreement.enforce_message_signing = enforce_message_signing
                if custom_directories is not None:
                    agreement.custom_directories = custom_directories
                return agreement_id
        raise ResourceNotFound("Agreement", agreement_id)

    def list_agreements(self, server_id: str) -> list[Agreement]:
        server = self._get_server(server_id)
        return server._agreements

    # ======== Certificate operations ========

    def import_certificate(
        self,
        usage: str,
        certificate: str,
        certificate_chain: Optional[str],
        private_key: Optional[str],
        active_date: Optional[str],
        inactive_date: Optional[str],
        description: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> str:
        cert = Certificate(
            region_name=self.region_name,
            account_id=self.account_id,
            usage=usage,
            certificate=certificate,
            certificate_chain=certificate_chain,
            private_key=private_key,
            active_date=active_date,
            inactive_date=inactive_date,
            description=description,
            tags=(tags or []),
        )
        self.certificates[cert.certificate_id] = cert
        if tags:
            self._add_tags(cert.arn, tags)
        return cert.certificate_id

    def describe_certificate(self, certificate_id: str) -> Certificate:
        if certificate_id not in self.certificates:
            raise ResourceNotFound("Certificate", certificate_id)
        return self.certificates[certificate_id]

    def delete_certificate(self, certificate_id: str) -> None:
        if certificate_id not in self.certificates:
            raise ResourceNotFound("Certificate", certificate_id)
        cert = self.certificates.pop(certificate_id)
        self.tagger.pop(cert.arn, None)

    def update_certificate(
        self,
        certificate_id: str,
        active_date: Optional[str],
        inactive_date: Optional[str],
        description: Optional[str],
    ) -> str:
        if certificate_id not in self.certificates:
            raise ResourceNotFound("Certificate", certificate_id)
        cert = self.certificates[certificate_id]
        if active_date is not None:
            cert.active_date = active_date
        if inactive_date is not None:
            cert.inactive_date = inactive_date
        if description is not None:
            cert.description = description
        return certificate_id

    def list_certificates(self) -> list[Certificate]:
        return list(self.certificates.values())

    # ======== Connector operations ========

    def create_connector(
        self,
        url: Optional[str],
        as2_config: Optional[dict[str, Any]],
        access_role: str,
        logging_role: Optional[str],
        tags: Optional[list[dict[str, str]]],
        sftp_config: Optional[dict[str, Any]],
        security_policy_name: Optional[str],
        egress_config: Optional[dict[str, Any]],
    ) -> str:
        connector = Connector(
            region_name=self.region_name,
            account_id=self.account_id,
            url=url,
            as2_config=as2_config,
            access_role=access_role,
            logging_role=logging_role,
            sftp_config=sftp_config,
            security_policy_name=security_policy_name,
            egress_config=egress_config,
            tags=(tags or []),
        )
        self.connectors[connector.connector_id] = connector
        if tags:
            self._add_tags(connector.arn, tags)
        return connector.connector_id

    def describe_connector(self, connector_id: str) -> Connector:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        return self.connectors[connector_id]

    def delete_connector(self, connector_id: str) -> None:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        conn = self.connectors.pop(connector_id)
        self.tagger.pop(conn.arn, None)

    def update_connector(
        self,
        connector_id: str,
        url: Optional[str],
        as2_config: Optional[dict[str, Any]],
        access_role: Optional[str],
        logging_role: Optional[str],
        sftp_config: Optional[dict[str, Any]],
        security_policy_name: Optional[str],
        egress_config: Optional[dict[str, Any]],
    ) -> str:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        conn = self.connectors[connector_id]
        if url is not None:
            conn.url = url
        if as2_config is not None:
            conn.as2_config = as2_config
        if access_role is not None:
            conn.access_role = access_role
        if logging_role is not None:
            conn.logging_role = logging_role
        if sftp_config is not None:
            conn.sftp_config = sftp_config
        if security_policy_name is not None:
            conn.security_policy_name = security_policy_name
        if egress_config is not None:
            conn.egress_config = egress_config
        return connector_id

    def list_connectors(self) -> list[Connector]:
        return list(self.connectors.values())

    def test_connection(self, connector_id: str) -> tuple[str, str, str]:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        return connector_id, "OK", ""

    # ======== Profile operations ========

    def create_profile(
        self,
        as2_id: str,
        profile_type: str,
        certificate_ids: Optional[list[str]],
        tags: Optional[list[dict[str, str]]],
    ) -> str:
        profile = Profile(
            region_name=self.region_name,
            account_id=self.account_id,
            as2_id=as2_id,
            profile_type=profile_type,
            certificate_ids=certificate_ids,
            tags=(tags or []),
        )
        self.profiles[profile.profile_id] = profile
        if tags:
            self._add_tags(profile.arn, tags)
        return profile.profile_id

    def describe_profile(self, profile_id: str) -> Profile:
        if profile_id not in self.profiles:
            raise ResourceNotFound("Profile", profile_id)
        return self.profiles[profile_id]

    def delete_profile(self, profile_id: str) -> None:
        if profile_id not in self.profiles:
            raise ResourceNotFound("Profile", profile_id)
        prof = self.profiles.pop(profile_id)
        self.tagger.pop(prof.arn, None)

    def update_profile(
        self,
        profile_id: str,
        certificate_ids: Optional[list[str]],
    ) -> str:
        if profile_id not in self.profiles:
            raise ResourceNotFound("Profile", profile_id)
        prof = self.profiles[profile_id]
        if certificate_ids is not None:
            prof.certificate_ids = certificate_ids
        return profile_id

    def list_profiles(self, profile_type: Optional[str]) -> list[Profile]:
        profiles = list(self.profiles.values())
        if profile_type:
            profiles = [p for p in profiles if p.profile_type == profile_type]
        return profiles

    # ======== Workflow operations ========

    def create_workflow(
        self,
        description: Optional[str],
        steps: list[dict[str, Any]],
        on_exception_steps: Optional[list[dict[str, Any]]],
        tags: Optional[list[dict[str, str]]],
    ) -> str:
        workflow = Workflow(
            region_name=self.region_name,
            account_id=self.account_id,
            steps=steps,
            description=description,
            on_exception_steps=on_exception_steps,
            tags=(tags or []),
        )
        self.workflows[workflow.workflow_id] = workflow
        if tags:
            self._add_tags(workflow.arn, tags)
        return workflow.workflow_id

    def describe_workflow(self, workflow_id: str) -> Workflow:
        if workflow_id not in self.workflows:
            raise ResourceNotFound("Workflow", workflow_id)
        return self.workflows[workflow_id]

    def delete_workflow(self, workflow_id: str) -> None:
        if workflow_id not in self.workflows:
            raise ResourceNotFound("Workflow", workflow_id)
        wf = self.workflows.pop(workflow_id)
        self.tagger.pop(wf.arn, None)

    def list_workflows(self) -> list[Workflow]:
        return list(self.workflows.values())

    def send_workflow_step_state(
        self,
        workflow_id: str,
        execution_id: str,
        token: str,
        status: str,
    ) -> None:
        if workflow_id not in self.workflows:
            raise ResourceNotFound("Workflow", workflow_id)
        # In a real implementation this would signal the execution engine.
        # For mock purposes, we just validate the workflow exists.

    def describe_execution(
        self, workflow_id: str, execution_id: str
    ) -> tuple[str, dict[str, Any]]:
        if workflow_id not in self.workflows:
            raise ResourceNotFound("Workflow", workflow_id)
        # Return a mock execution
        execution = {
            "ExecutionId": execution_id,
            "Status": "COMPLETED",
            "Results": {},
        }
        return workflow_id, execution

    def list_executions(self, workflow_id: str) -> tuple[str, list[dict[str, Any]]]:
        if workflow_id not in self.workflows:
            raise ResourceNotFound("Workflow", workflow_id)
        return workflow_id, []

    # ======== HostKey operations ========

    def import_host_key(
        self,
        server_id: str,
        host_key_body: str,
        description: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> tuple[str, str]:
        server = self._get_server(server_id)
        host_key = HostKey(
            region_name=self.region_name,
            account_id=self.account_id,
            server_id=server_id,
            host_key_body=host_key_body,
            description=description,
            tags=(tags or []),
        )
        server._host_keys.append(host_key)
        if tags:
            self._add_tags(host_key.arn, tags)
        return server_id, host_key.host_key_id

    def describe_host_key(self, server_id: str, host_key_id: str) -> HostKey:
        server = self._get_server(server_id)
        for hk in server._host_keys:
            if hk.host_key_id == host_key_id:
                return hk
        raise ResourceNotFound("HostKey", host_key_id)

    def delete_host_key(self, server_id: str, host_key_id: str) -> None:
        server = self._get_server(server_id)
        for i, hk in enumerate(server._host_keys):
            if hk.host_key_id == host_key_id:
                self.tagger.pop(hk.arn, None)
                del server._host_keys[i]
                return
        raise ResourceNotFound("HostKey", host_key_id)

    def update_host_key(
        self, server_id: str, host_key_id: str, description: str
    ) -> tuple[str, str]:
        server = self._get_server(server_id)
        for hk in server._host_keys:
            if hk.host_key_id == host_key_id:
                hk.description = description
                return server_id, host_key_id
        raise ResourceNotFound("HostKey", host_key_id)

    def list_host_keys(self, server_id: str) -> tuple[str, list[HostKey]]:
        server = self._get_server(server_id)
        return server_id, server._host_keys

    # ======== WebApp operations ========

    def create_web_app(
        self,
        identity_provider_details: dict[str, Any],
        access_endpoint: Optional[str],
        web_app_units: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
        web_app_endpoint_policy: Optional[str],
        endpoint_details: Optional[dict[str, Any]],
    ) -> str:
        web_app = WebApp(
            region_name=self.region_name,
            account_id=self.account_id,
            identity_provider_details=identity_provider_details,
            access_endpoint=access_endpoint,
            web_app_units=web_app_units,
            web_app_endpoint_policy=web_app_endpoint_policy,
            endpoint_details=endpoint_details,
            tags=(tags or []),
        )
        self.web_apps[web_app.web_app_id] = web_app
        if tags:
            self._add_tags(web_app.arn, tags)
        return web_app.web_app_id

    def describe_web_app(self, web_app_id: str) -> WebApp:
        if web_app_id not in self.web_apps:
            raise ResourceNotFound("WebApp", web_app_id)
        return self.web_apps[web_app_id]

    def delete_web_app(self, web_app_id: str) -> None:
        if web_app_id not in self.web_apps:
            raise ResourceNotFound("WebApp", web_app_id)
        wa = self.web_apps.pop(web_app_id)
        self.tagger.pop(wa.arn, None)

    def update_web_app(
        self,
        web_app_id: str,
        identity_provider_details: Optional[dict[str, Any]],
        access_endpoint: Optional[str],
        web_app_units: Optional[dict[str, Any]],
        endpoint_details: Optional[dict[str, Any]],
    ) -> str:
        if web_app_id not in self.web_apps:
            raise ResourceNotFound("WebApp", web_app_id)
        wa = self.web_apps[web_app_id]
        if identity_provider_details is not None:
            wa.identity_provider_details = identity_provider_details
        if access_endpoint is not None:
            wa.access_endpoint = access_endpoint
        if web_app_units is not None:
            wa.web_app_units = web_app_units
        if endpoint_details is not None:
            wa.endpoint_details = endpoint_details
        return web_app_id

    def list_web_apps(self) -> list[WebApp]:
        return list(self.web_apps.values())

    # ======== WebApp Customization operations ========

    def update_web_app_customization(
        self,
        web_app_id: str,
        title: Optional[str],
        logo_file: Optional[bytes],
        favicon_file: Optional[bytes],
    ) -> str:
        if web_app_id not in self.web_apps:
            raise ResourceNotFound("WebApp", web_app_id)
        wa = self.web_apps[web_app_id]
        customization = WebAppCustomization(
            web_app_id=web_app_id,
            arn=f"{wa.arn}/customization",
            title=title,
            logo_file=logo_file,
            favicon_file=favicon_file,
        )
        wa.customization = customization
        return web_app_id

    def describe_web_app_customization(self, web_app_id: str) -> WebAppCustomization:
        if web_app_id not in self.web_apps:
            raise ResourceNotFound("WebApp", web_app_id)
        wa = self.web_apps[web_app_id]
        if wa.customization is None:
            raise ResourceNotFound("WebAppCustomization", web_app_id)
        return wa.customization

    def delete_web_app_customization(self, web_app_id: str) -> None:
        if web_app_id not in self.web_apps:
            raise ResourceNotFound("WebApp", web_app_id)
        self.web_apps[web_app_id].customization = None

    # ======== Security Policy operations ========

    def describe_security_policy(self, security_policy_name: str) -> dict[str, Any]:
        if security_policy_name not in SECURITY_POLICIES:
            raise ResourceNotFound("SecurityPolicy", security_policy_name)
        return SECURITY_POLICIES[security_policy_name]

    def list_security_policies(self) -> list[str]:
        return sorted(SECURITY_POLICIES.keys())

    # ======== Tag operations ========

    def tag_resource(self, arn: str, tags: list[dict[str, str]]) -> None:
        self._add_tags(arn, tags)
        # Also update in-object tags for resources that carry them
        self._sync_tags_to_resource(arn, self._get_tags_for_arn(arn))

    def untag_resource(self, arn: str, tag_keys: list[str]) -> None:
        self._remove_tags(arn, tag_keys)
        self._sync_tags_to_resource(arn, self._get_tags_for_arn(arn))

    def list_tags_for_resource(self, arn: str) -> tuple[str, list[dict[str, str]]]:
        return arn, self._get_tags_for_arn(arn)

    def _sync_tags_to_resource(self, arn: str, tags: list[dict[str, str]]) -> None:
        """Sync tag store back to the resource object's .tags field."""
        # Servers
        for server in self.servers.values():
            if server.arn == arn:
                server.tags = tags
                return
            for user in server._users:
                if user.arn == arn:
                    user.tags = tags
                    return
            for agreement in server._agreements:
                if agreement.arn == arn:
                    agreement.tags = tags
                    return
            for hk in server._host_keys:
                if hk.arn == arn:
                    hk.tags = tags
                    return
        for cert in self.certificates.values():
            if cert.arn == arn:
                cert.tags = tags
                return
        for conn in self.connectors.values():
            if conn.arn == arn:
                conn.tags = tags
                return
        for prof in self.profiles.values():
            if prof.arn == arn:
                prof.tags = tags
                return
        for wf in self.workflows.values():
            if wf.arn == arn:
                wf.tags = tags
                return
        for wa in self.web_apps.values():
            if wa.arn == arn:
                wa.tags = tags
                return

    # ======== Test Identity Provider ========

    def test_identity_provider(
        self,
        server_id: str,
        server_protocol: Optional[str],
        source_ip: Optional[str],
        user_name: str,
        user_password: Optional[str],
    ) -> dict[str, Any]:
        self._get_server(server_id)
        return {
            "Response": "",
            "StatusCode": 200,
            "Message": "",
            "Url": "",
        }

    # ======== Connector file operations (stubs) ========

    def start_file_transfer(
        self,
        connector_id: str,
        send_file_paths: Optional[list[str]],
        retrieve_file_paths: Optional[list[str]],
        local_directory_path: Optional[str],
        remote_directory_path: Optional[str],
    ) -> str:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        transfer_id = f"t-{mock_random.get_random_hex(17)}"
        return transfer_id

    def start_directory_listing(
        self,
        connector_id: str,
        remote_directory_path: str,
        max_items: Optional[int],
        output_directory_path: str,
    ) -> tuple[str, str]:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        listing_id = f"listing-{mock_random.get_random_hex(17)}"
        output_file_name = f"{output_directory_path}/{listing_id}.json"
        return listing_id, output_file_name

    def start_remote_delete(
        self, connector_id: str, delete_path: str
    ) -> str:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        return f"delete-{mock_random.get_random_hex(17)}"

    def start_remote_move(
        self, connector_id: str, source_path: str, target_path: str
    ) -> str:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        return f"move-{mock_random.get_random_hex(17)}"

    def list_file_transfer_results(
        self, connector_id: str, transfer_id: str
    ) -> list[dict[str, Any]]:
        if connector_id not in self.connectors:
            raise ResourceNotFound("Connector", connector_id)
        return []

    # TODO: EgressConfig (VpcLattice) not implemented
    def create_connector(
        self,
        url: str,
        access_role: str,
        logging_role: Optional[str],
        tags: Optional[list[dict[str, str]]],
        as2_config: Optional[dict[str, Any]],
        sftp_config: Optional[dict[str, Any]],
        security_policy_name: Optional[str],
    ) -> str:
        connector = Connector(
            region_name=self.region_name,
            account_id=self.account_id,
            url=url,
            access_role=access_role,
            logging_role=logging_role,
            as2_config={camelcase_to_underscores(k): v for k, v in as2_config.items()}
            if as2_config
            else None,
            sftp_config={camelcase_to_underscores(k): v for k, v in sftp_config.items()}
            if sftp_config
            else None,
            security_policy_name=security_policy_name,
            tags=(tags or []),
        )
        connector_id = connector.connector_id
        self.connectors[connector_id] = connector
        return connector_id

    def describe_connector(self, connector_id: str) -> Connector:
        if connector_id not in self.connectors:
            raise ConnectorNotFound(connector_id=connector_id)
        return self.connectors[connector_id]

    # TODO: EgressConfig (VpcLattice) not implemented
    def update_connector(
        self,
        connector_id: str,
        url: Optional[str],
        access_role: Optional[str],
        logging_role: Optional[str],
        as2_config: Optional[dict[str, Any]],
        sftp_config: Optional[dict[str, Any]],
        security_policy_name: Optional[str],
    ) -> str:
        if connector_id not in self.connectors:
            raise ConnectorNotFound(connector_id=connector_id)
        connector = self.connectors[connector_id]
        if url is not None:
            connector.url = url
        if access_role is not None:
            connector.access_role = access_role
        if logging_role is not None:
            connector.logging_role = logging_role
        if security_policy_name is not None:
            connector.security_policy_name = security_policy_name
        if as2_config is not None:
            connector.as2_config = {
                camelcase_to_underscores(k): v for k, v in as2_config.items()
            }
        if sftp_config is not None:
            connector.sftp_config = {
                camelcase_to_underscores(k): v for k, v in sftp_config.items()
            }
        return connector_id

    def delete_connector(self, connector_id: str) -> None:
        if connector_id not in self.connectors:
            raise ConnectorNotFound(connector_id=connector_id)
        del self.connectors[connector_id]

    # TODO: implement pagination
    def list_connectors(self) -> list[Connector]:
        return list(self.connectors.values())


transfer_backends = BackendDict(TransferBackend, "transfer")
