from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Optional, Union

from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random


class UserHomeDirectoryType(str, Enum):
    PATH = "PATH"
    LOGICAL = "LOGICAL"


class UserHomeDirectoryMappingType(str, Enum):
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"


@dataclass
class User(BaseModel):
    region_name: str
    account_id: str
    server_id: str
    home_directory: Optional[str]
    home_directory_type: Optional[UserHomeDirectoryType]
    policy: Optional[str]
    role: str
    user_name: str
    arn: str = field(default="", init=False)
    home_directory_mappings: list[dict[str, Optional[str]]] = field(
        default_factory=list
    )
    posix_profile: dict[str, Optional[Union[str, list[str]]]] = field(
        default_factory=dict
    )
    ssh_public_keys: list[dict[str, str]] = field(default_factory=list)
    tags: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:user/{self.server_id}/{self.user_name}"

    def to_dict(self) -> dict[str, Any]:
        user = {
            "HomeDirectory": self.home_directory,
            "HomeDirectoryType": self.home_directory_type,
            "Policy": self.policy,
            "Role": self.role,
            "UserName": self.user_name,
            "Arn": self.arn,
            "HomeDirectoryMappings": [
                {
                    "Entry": mapping.get("entry"),
                    "Target": mapping.get("target"),
                    "Type": mapping.get("type"),
                }
                for mapping in self.home_directory_mappings
            ],
            "SshPublicKeys": [
                {
                    "DateImported": key.get("date_imported"),
                    "SshPublicKeyBody": key.get("ssh_public_key_body"),
                    "SshPublicKeyId": key.get("ssh_public_key_id"),
                }
                for key in self.ssh_public_keys
            ],
            "PosixProfile": {
                "Uid": self.posix_profile.get("uid"),
                "Gid": self.posix_profile.get("gid"),
                "SecondaryGids": self.posix_profile.get("secondary_gids"),
            },
            "Tags": self.tags,
        }

        return user

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "HomeDirectory": self.home_directory,
            "HomeDirectoryType": self.home_directory_type,
            "Role": self.role,
            "SshPublicKeyCount": len(self.ssh_public_keys),
            "UserName": self.user_name,
        }


class ServerDomain(str, Enum):
    S3 = "S3"
    EFS = "EFS"


class ServerEndpointType(str, Enum):
    PUBLIC = "PUBLIC"
    VPC = "VPC"
    VPC_ENDPOINT = "VPC_ENDPOINT"


class ServerIdentityProviderSftpAuthenticationMethods(str, Enum):
    PASSWORD = "PASSWORD"
    PUBLIC_KEY = "PUBLIC_KEY"
    PUBLIC_KEY_OR_PASSWORD = "PUBLIC_KEY_OR_PASSWORD"
    PUBLIC_KEY_AND_PASSWORD = "PUBLIC_KEY_AND_PASSWORD"


class ServerIdentityProviderType(str, Enum):
    SERVICE_MANAGED = "SERVICE_MANAGED"
    API_GATEWAY = "API_GATEWAY"
    AWS_DIRECTORY_SERVICE = "AWS_DIRECTORY_SERVICE"
    AWS_LAMBDA = "AWS_LAMBDA"


class ServerProtocols(str, Enum):
    SFTP = "SFTP"
    FTP = "FTP"
    FTPS = "FTPS"
    AS2 = "AS2"


class ServerState(str, Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    STARTING = "STARTING"
    STOPPING = "STOPPING"
    START_FAILED = "START_FAILED"
    STOP_FAILED = "STOP_FAILED"


AS2_TRANSPORTS_TYPE = list[Literal["HTTP"]]


@dataclass
class Server(BaseModel):
    region_name: str
    account_id: str
    certificate: Optional[str]
    domain: Optional[ServerDomain]
    endpoint_type: Optional[ServerEndpointType]
    host_key_fingerprint: Optional[str]
    identity_provider_type: Optional[ServerIdentityProviderType]
    logging_role: Optional[str]
    post_authentication_login_banner: Optional[str]
    pre_authentication_login_banner: Optional[str]
    protocols: Optional[list[ServerProtocols]]
    security_policy_name: Optional[str]
    structured_log_destinations: Optional[list[str]]
    arn: str = field(default="", init=False)
    as2_service_managed_egress_ip_addresses: list[str] = field(default_factory=list)
    endpoint_details: dict[str, str] = field(default_factory=dict)
    identity_provider_details: dict[str, str] = field(default_factory=dict)
    protocol_details: dict[str, str] = field(default_factory=dict)
    s3_storage_options: dict[str, Optional[str]] = field(default_factory=dict)
    server_id: str = field(default="", init=False)
    state: Optional[ServerState] = ServerState.ONLINE
    tags: list[dict[str, str]] = field(default_factory=list)
    user_count: int = field(default=0)
    workflow_details: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    _users: list[User] = field(default_factory=list, repr=False)
    _accesses: list["Access"] = field(default_factory=list, repr=False)
    _agreements: list["Agreement"] = field(default_factory=list, repr=False)
    _host_keys: list["HostKey"] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if self.server_id == "":
            self.server_id = f"s-{mock_random.get_random_hex(17)}"
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:server/{self.server_id}"
        if self.as2_service_managed_egress_ip_addresses == []:
            self.as2_service_managed_egress_ip_addresses.append("0.0.0.0/0")

    def to_dict(self) -> dict[str, Any]:
        on_upload = []
        on_partial_upload = []
        if self.workflow_details is not None:
            on_upload_workflows = self.workflow_details.get("on_upload")

            if on_upload_workflows is not None:
                for workflow in on_upload_workflows:
                    workflow_id = workflow.get("workflow_id")
                    execution_role = workflow.get("execution_role")
                    if workflow_id and execution_role:
                        on_upload.append(
                            {"WorkflowId": workflow_id, "ExecutionRole": execution_role}
                        )
            on_partial_upload_workflows = self.workflow_details.get("on_partial_upload")
            if on_partial_upload_workflows is not None:
                for workflow in on_partial_upload_workflows:
                    workflow_id = workflow.get("workflow_id")
                    execution_role = workflow.get("execution_role")
                    if workflow_id and execution_role:
                        on_partial_upload.append(
                            {"WorkflowId": workflow_id, "ExecutionRole": execution_role}
                        )
        server = {
            "Certificate": self.certificate,
            "Domain": self.domain,
            "EndpointType": self.endpoint_type,
            "HostKeyFingerprint": self.host_key_fingerprint,
            "IdentityProviderType": self.identity_provider_type,
            "LoggingRole": self.logging_role,
            "PostAuthenticationLoginBanner": self.post_authentication_login_banner,
            "PreAuthenticationLoginBanner": self.pre_authentication_login_banner,
            "Protocols": self.protocols,
            "SecurityPolicyName": self.security_policy_name,
            "StructuredLogDestinations": self.structured_log_destinations,
            "Arn": self.arn,
            "As2ServiceManagedEgressIpAddresses": self.as2_service_managed_egress_ip_addresses,
            "ServerId": self.server_id,
            "State": self.state,
            "Tags": self.tags,
            "UserCount": self.user_count,
            "EndpointDetails": {
                "AddressAllocationIds": self.endpoint_details.get(
                    "address_allocation_ids"
                ),
                "SubnetIds": self.endpoint_details.get("subnet_ids"),
                "VpcEndpointId": self.endpoint_details.get("vpc_endpoint_id"),
                "VpcId": self.endpoint_details.get("vpc_id"),
                "SecurityGroupIds": self.endpoint_details.get("security_group_ids"),
            },
            "IdentityProviderDetails": {
                "Url": self.identity_provider_details.get("url"),
                "InvocationRole": self.identity_provider_details.get("invocation_role"),
                "DirectoryId": self.identity_provider_details.get("directory_id"),
                "Function": self.identity_provider_details.get("function"),
                "SftpAuthenticationMethods": self.identity_provider_details.get(
                    "sftp_authentication_methods"
                ),
            },
            "ProtocolDetails": {
                "PassiveIp": self.protocol_details.get("passive_ip"),
                "TlsSessionResumptionMode": self.protocol_details.get(
                    "tls_session_resumption_mode"
                ),
                "SetStatOption": self.protocol_details.get("set_stat_option"),
                "As2Transports": self.protocol_details.get("as2_transports"),
            },
            "S3StorageOptions": {
                "DirectoryListingOptimization": self.s3_storage_options.get(
                    "directory_listing_optimization"
                )
            },
            "WorkflowDetails": {
                "OnUpload": on_upload,
                "OnPartialUpload": on_partial_upload,
            },
        }
        return server

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "Domain": self.domain,
            "EndpointType": self.endpoint_type,
            "IdentityProviderType": self.identity_provider_type,
            "LoggingRole": self.logging_role,
            "ServerId": self.server_id,
            "State": self.state,
            "UserCount": self.user_count,
        }


@dataclass
class Access(BaseModel):
    region_name: str
    account_id: str
    server_id: str
    external_id: str
    home_directory: Optional[str] = None
    home_directory_type: Optional[str] = None
    home_directory_mappings: list[dict[str, Optional[str]]] = field(default_factory=list)
    policy: Optional[str] = None
    posix_profile: Optional[dict[str, Any]] = None
    role: str = ""

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ExternalId": self.external_id,
            "Role": self.role,
        }
        if self.home_directory is not None:
            result["HomeDirectory"] = self.home_directory
        if self.home_directory_type is not None:
            result["HomeDirectoryType"] = self.home_directory_type
        if self.home_directory_mappings:
            result["HomeDirectoryMappings"] = [
                {
                    "Entry": m.get("entry"),
                    "Target": m.get("target"),
                }
                for m in self.home_directory_mappings
            ]
        if self.policy is not None:
            result["Policy"] = self.policy
        if self.posix_profile is not None:
            result["PosixProfile"] = {
                "Uid": self.posix_profile.get("uid"),
                "Gid": self.posix_profile.get("gid"),
                "SecondaryGids": self.posix_profile.get("secondary_gids"),
            }
        return result

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "ExternalId": self.external_id,
            "HomeDirectory": self.home_directory,
            "HomeDirectoryType": self.home_directory_type,
            "Role": self.role,
        }


@dataclass
class Agreement(BaseModel):
    region_name: str
    account_id: str
    server_id: str
    local_profile_id: str
    partner_profile_id: str
    access_role: str
    description: Optional[str] = None
    base_directory: Optional[str] = None
    status: str = "ACTIVE"
    preserve_filename: Optional[str] = None
    enforce_message_signing: Optional[str] = None
    custom_directories: Optional[dict[str, Any]] = None
    tags: list[dict[str, str]] = field(default_factory=list)
    arn: str = field(default="", init=False)
    agreement_id: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.agreement_id == "":
            self.agreement_id = f"a-{mock_random.get_random_hex(17)}"
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:agreement/{self.server_id}/{self.agreement_id}"

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "Arn": self.arn,
            "AgreementId": self.agreement_id,
            "Description": self.description,
            "Status": self.status,
            "ServerId": self.server_id,
            "LocalProfileId": self.local_profile_id,
            "PartnerProfileId": self.partner_profile_id,
            "BaseDirectory": self.base_directory,
            "AccessRole": self.access_role,
            "Tags": self.tags,
        }
        if self.preserve_filename is not None:
            result["PreserveFilename"] = self.preserve_filename
        if self.enforce_message_signing is not None:
            result["EnforceMessageSigning"] = self.enforce_message_signing
        if self.custom_directories is not None:
            result["CustomDirectories"] = self.custom_directories
        return result

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "AgreementId": self.agreement_id,
            "Description": self.description,
            "Status": self.status,
            "ServerId": self.server_id,
            "LocalProfileId": self.local_profile_id,
            "PartnerProfileId": self.partner_profile_id,
        }


@dataclass
class Certificate(BaseModel):
    region_name: str
    account_id: str
    usage: str
    certificate: str
    certificate_chain: Optional[str] = None
    private_key: Optional[str] = None
    active_date: Optional[str] = None
    inactive_date: Optional[str] = None
    description: Optional[str] = None
    tags: list[dict[str, str]] = field(default_factory=list)
    arn: str = field(default="", init=False)
    certificate_id: str = field(default="", init=False)
    status: str = "ACTIVE"
    cert_type: str = "CERTIFICATE"

    def __post_init__(self) -> None:
        if self.certificate_id == "":
            self.certificate_id = f"cert-{mock_random.get_random_hex(17)}"
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:certificate/{self.certificate_id}"
        if self.certificate_chain:
            self.cert_type = "CERTIFICATE_WITH_CHAIN"

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "CertificateId": self.certificate_id,
            "Usage": self.usage,
            "Status": self.status,
            "Certificate": self.certificate,
            "CertificateChain": self.certificate_chain,
            "ActiveDate": self.active_date,
            "InactiveDate": self.inactive_date,
            "Description": self.description,
            "Type": self.cert_type,
            "Tags": self.tags,
        }

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "CertificateId": self.certificate_id,
            "Usage": self.usage,
            "Status": self.status,
            "ActiveDate": self.active_date,
            "InactiveDate": self.inactive_date,
            "Description": self.description,
            "Type": self.cert_type,
        }


@dataclass
class Connector(BaseModel):
    region_name: str
    account_id: str
    access_role: str
    url: Optional[str] = None
    as2_config: Optional[dict[str, Any]] = None
    logging_role: Optional[str] = None
    sftp_config: Optional[dict[str, Any]] = None
    security_policy_name: Optional[str] = None
    egress_config: Optional[dict[str, Any]] = None
    tags: list[dict[str, str]] = field(default_factory=list)
    arn: str = field(default="", init=False)
    connector_id: str = field(default="", init=False)
    service_managed_egress_ip_addresses: list[str] = field(default_factory=list)


    def __post_init__(self) -> None:
        if self.connector_id == "":
            self.connector_id = f"c-{mock_random.get_random_hex(17)}"
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:connector/{self.connector_id}"

    def to_dict(self) -> dict[str, Any]:
        # Set to mock values. Actual AWS values used were not validated.
        if not self.service_managed_egress_ip_addresses:
            self.service_managed_egress_ip_addresses = ["127.0.0.1", "127.0.0.2"]
        result: dict[str, Any] = {
            "Arn": self.arn,
            "ConnectorId": self.connector_id,
            "Url": self.url,
            "AccessRole": self.access_role,
            "LoggingRole": self.logging_role,
            "Tags": self.tags,
            "ServiceManagedEgressIpAddresses": self.service_managed_egress_ip_addresses,
            "SecurityPolicyName": self.security_policy_name,
        }
        if self.as2_config is not None:
            result["As2Config"] = self.as2_config
        if self.sftp_config is not None:
            result["SftpConfig"] = self.sftp_config
        if self.egress_config is not None:
            result["EgressConfig"] = self.egress_config
        return result

    def to_short_dict(self) -> dict[str, Any]:

        return {
            "Arn": self.arn,
            "ConnectorId": self.connector_id,
            "Url": self.url,
        }


@dataclass
class Profile(BaseModel):
    region_name: str
    account_id: str
    as2_id: str
    profile_type: str
    certificate_ids: Optional[list[str]] = None
    tags: list[dict[str, str]] = field(default_factory=list)
    arn: str = field(default="", init=False)
    profile_id: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.profile_id == "":
            self.profile_id = f"p-{mock_random.get_random_hex(17)}"
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:profile/{self.profile_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "ProfileId": self.profile_id,
            "ProfileType": self.profile_type,
            "As2Id": self.as2_id,
            "CertificateIds": self.certificate_ids or [],
            "Tags": self.tags,
        }

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "ProfileId": self.profile_id,
            "ProfileType": self.profile_type,
            "As2Id": self.as2_id,
        }


@dataclass
class Workflow(BaseModel):
    region_name: str
    account_id: str
    steps: list[dict[str, Any]]
    description: Optional[str] = None
    on_exception_steps: Optional[list[dict[str, Any]]] = None
    tags: list[dict[str, str]] = field(default_factory=list)
    arn: str = field(default="", init=False)
    workflow_id: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.workflow_id == "":
            self.workflow_id = f"w-{mock_random.get_random_hex(17)}"
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:workflow/{self.workflow_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "WorkflowId": self.workflow_id,
            "Description": self.description,
            "Steps": self.steps,
            "OnExceptionSteps": self.on_exception_steps or [],
            "Tags": self.tags,
        }

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "WorkflowId": self.workflow_id,
            "Description": self.description,
        }


@dataclass
class HostKey(BaseModel):
    region_name: str
    account_id: str
    server_id: str
    host_key_body: str
    description: Optional[str] = None
    tags: list[dict[str, str]] = field(default_factory=list)
    arn: str = field(default="", init=False)
    host_key_id: str = field(default="", init=False)
    host_key_fingerprint: str = field(default="", init=False)
    date_imported: str = field(default="", init=False)
    key_type: str = "RSA"

    def __post_init__(self) -> None:
        if self.host_key_id == "":
            self.host_key_id = f"hostkey-{mock_random.get_random_hex(20)}"
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:host-key/{self.server_id}/{self.host_key_id}"
        if self.host_key_fingerprint == "":
            self.host_key_fingerprint = f"SHA256:{mock_random.get_random_hex(32)}"
        if self.date_imported == "":
            self.date_imported = str(unix_time())

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "HostKeyId": self.host_key_id,
            "HostKeyFingerprint": self.host_key_fingerprint,
            "Description": self.description,
            "Type": self.key_type,
            "DateImported": self.date_imported,
            "Tags": self.tags,
        }

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "HostKeyId": self.host_key_id,
            "Description": self.description,
            "DateImported": self.date_imported,
            "Type": self.key_type,
        }


@dataclass
class WebApp(BaseModel):
    region_name: str
    account_id: str
    identity_provider_details: dict[str, Any]
    access_endpoint: Optional[str] = None
    web_app_units: Optional[dict[str, Any]] = None
    web_app_endpoint_policy: Optional[str] = None
    endpoint_details: Optional[dict[str, Any]] = None
    tags: list[dict[str, str]] = field(default_factory=list)
    arn: str = field(default="", init=False)
    web_app_id: str = field(default="", init=False)
    web_app_endpoint: str = field(default="", init=False)
    customization: Optional["WebAppCustomization"] = None

    def __post_init__(self) -> None:
        if self.web_app_id == "":
            self.web_app_id = f"webapp-{mock_random.get_random_hex(20)}"
        if self.arn == "":
            self.arn = f"arn:aws:transfer:{self.region_name}:{self.account_id}:webapp/{self.web_app_id}"
        if self.web_app_endpoint == "":
            self.web_app_endpoint = f"https://{self.web_app_id}.transfer.{self.region_name}.amazonaws.com"

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "Arn": self.arn,
            "WebAppId": self.web_app_id,
            "DescribedIdentityProviderDetails": self.identity_provider_details,
            "AccessEndpoint": self.access_endpoint,
            "WebAppEndpoint": self.web_app_endpoint,
            "WebAppUnits": self.web_app_units,
            "Tags": self.tags,
            "WebAppEndpointPolicy": self.web_app_endpoint_policy,
        }
        if self.endpoint_details is not None:
            result["DescribedEndpointDetails"] = self.endpoint_details
        return result

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "WebAppId": self.web_app_id,
            "AccessEndpoint": self.access_endpoint,
            "WebAppEndpoint": self.web_app_endpoint,
        }


@dataclass
class WebAppCustomization(BaseModel):
    web_app_id: str
    arn: str
    title: Optional[str] = None
    logo_file: Optional[bytes] = None
    favicon_file: Optional[bytes] = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "Arn": self.arn,
            "WebAppId": self.web_app_id,
        }
        if self.title is not None:
            result["Title"] = self.title
        if self.logo_file is not None:
            import base64

            result["LogoFile"] = base64.b64encode(self.logo_file).decode("utf-8")
        if self.favicon_file is not None:
            import base64

            result["FaviconFile"] = base64.b64encode(self.favicon_file).decode("utf-8")
        return result


# Well-known security policies
SECURITY_POLICIES: dict[str, dict[str, Any]] = {
    "TransferSecurityPolicy-2018-11": {
        "SecurityPolicyName": "TransferSecurityPolicy-2018-11",
        "Fips": False,
        "SshCiphers": [
            "aes128-ctr",
            "aes192-ctr",
            "aes256-ctr",
            "aes128-gcm@openssh.com",
            "aes256-gcm@openssh.com",
        ],
        "SshKexs": [
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "diffie-hellman-group-exchange-sha256",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
            "diffie-hellman-group14-sha256",
        ],
        "SshMacs": [
            "hmac-sha2-256-etm@openssh.com",
            "hmac-sha2-512-etm@openssh.com",
            "hmac-sha2-256",
            "hmac-sha2-512",
        ],
        "TlsCiphers": [
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
        ],
        "SshHostKeyAlgorithms": [
            "ssh-rsa",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        ],
        "Type": "SERVER",
        "Protocols": ["SFTP", "FTPS"],
    },
    "TransferSecurityPolicy-2020-06": {
        "SecurityPolicyName": "TransferSecurityPolicy-2020-06",
        "Fips": False,
        "SshCiphers": [
            "aes128-ctr",
            "aes192-ctr",
            "aes256-ctr",
            "aes128-gcm@openssh.com",
            "aes256-gcm@openssh.com",
        ],
        "SshKexs": [
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "diffie-hellman-group-exchange-sha256",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
            "diffie-hellman-group14-sha256",
        ],
        "SshMacs": [
            "hmac-sha2-256-etm@openssh.com",
            "hmac-sha2-512-etm@openssh.com",
            "hmac-sha2-256",
            "hmac-sha2-512",
        ],
        "TlsCiphers": [
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        ],
        "SshHostKeyAlgorithms": [
            "rsa-sha2-256",
            "rsa-sha2-512",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        ],
        "Type": "SERVER",
        "Protocols": ["SFTP", "FTPS"],
    },
    "TransferSecurityPolicy-2022-03": {
        "SecurityPolicyName": "TransferSecurityPolicy-2022-03",
        "Fips": False,
        "SshCiphers": [
            "aes128-ctr",
            "aes192-ctr",
            "aes256-ctr",
            "aes128-gcm@openssh.com",
            "aes256-gcm@openssh.com",
        ],
        "SshKexs": [
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
        ],
        "SshMacs": [
            "hmac-sha2-256-etm@openssh.com",
            "hmac-sha2-512-etm@openssh.com",
        ],
        "TlsCiphers": [
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        ],
        "SshHostKeyAlgorithms": [
            "rsa-sha2-256",
            "rsa-sha2-512",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
            "ssh-ed25519",
        ],
        "Type": "SERVER",
        "Protocols": ["SFTP", "FTPS"],
    },
    "TransferSecurityPolicy-2024-01": {
        "SecurityPolicyName": "TransferSecurityPolicy-2024-01",
        "Fips": False,
        "SshCiphers": [
            "aes128-gcm@openssh.com",
            "aes256-gcm@openssh.com",
            "chacha20-poly1305@openssh.com",
        ],
        "SshKexs": [
            "curve25519-sha256",
            "curve25519-sha256@libssh.org",
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
        ],
        "SshMacs": [
            "hmac-sha2-256-etm@openssh.com",
            "hmac-sha2-512-etm@openssh.com",
        ],
        "TlsCiphers": [
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        ],
        "SshHostKeyAlgorithms": [
            "rsa-sha2-256",
            "rsa-sha2-512",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
            "ssh-ed25519",
        ],
        "Type": "SERVER",
        "Protocols": ["SFTP", "FTPS"],
    },
    "TransferSecurityPolicy-FIPS-2020-06": {
        "SecurityPolicyName": "TransferSecurityPolicy-FIPS-2020-06",
        "Fips": True,
        "SshCiphers": [
            "aes128-ctr",
            "aes192-ctr",
            "aes256-ctr",
            "aes128-gcm@openssh.com",
            "aes256-gcm@openssh.com",
        ],
        "SshKexs": [
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "diffie-hellman-group-exchange-sha256",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
            "diffie-hellman-group14-sha256",
        ],
        "SshMacs": [
            "hmac-sha2-256-etm@openssh.com",
            "hmac-sha2-512-etm@openssh.com",
            "hmac-sha2-256",
            "hmac-sha2-512",
        ],
        "TlsCiphers": [
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        ],
        "SshHostKeyAlgorithms": [
            "rsa-sha2-256",
            "rsa-sha2-512",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        ],
        "Type": "SERVER",
        "Protocols": ["SFTP", "FTPS"],
    },
    "TransferSecurityPolicy-FIPS-2024-01": {
        "SecurityPolicyName": "TransferSecurityPolicy-FIPS-2024-01",
        "Fips": True,
        "SshCiphers": [
            "aes128-gcm@openssh.com",
            "aes256-gcm@openssh.com",
        ],
        "SshKexs": [
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
        ],
        "SshMacs": [
            "hmac-sha2-256-etm@openssh.com",
            "hmac-sha2-512-etm@openssh.com",
        ],
        "TlsCiphers": [
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        ],
        "SshHostKeyAlgorithms": [
            "rsa-sha2-256",
            "rsa-sha2-512",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        ],
        "Type": "SERVER",
        "Protocols": ["SFTP", "FTPS"],
    },
    "TransferSecurityPolicy-PQ-SSH-Experimental-2023-04": {
        "SecurityPolicyName": "TransferSecurityPolicy-PQ-SSH-Experimental-2023-04",
        "Fips": False,
        "SshCiphers": [
            "aes256-gcm@openssh.com",
        ],
        "SshKexs": [
            "ecdh-nistp384-kyber-768r3-sha384-d00@openquantumsafe.org",
            "curve25519-sha256",
        ],
        "SshMacs": [
            "hmac-sha2-512-etm@openssh.com",
        ],
        "TlsCiphers": [],
        "SshHostKeyAlgorithms": [
            "ssh-ed25519",
            "ecdsa-sha2-nistp256",
            "rsa-sha2-256",
            "rsa-sha2-512",
        ],
        "Type": "SERVER",
        "Protocols": ["SFTP"],
    },
    "TransferSecurityPolicy-PQ-SSH-FIPS-Experimental-2023-04": {
        "SecurityPolicyName": "TransferSecurityPolicy-PQ-SSH-FIPS-Experimental-2023-04",
        "Fips": True,
        "SshCiphers": [
            "aes256-gcm@openssh.com",
        ],
        "SshKexs": [
            "ecdh-nistp384-kyber-768r3-sha384-d00@openquantumsafe.org",
        ],
        "SshMacs": [
            "hmac-sha2-512-etm@openssh.com",
        ],
        "TlsCiphers": [],
        "SshHostKeyAlgorithms": [
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
            "rsa-sha2-256",
            "rsa-sha2-512",
        ],
        "Type": "SERVER",
        "Protocols": ["SFTP"],
    },
}

