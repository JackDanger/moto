"""DirectoryServiceBackend class with methods for supported APIs."""

import copy
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.ds.exceptions import (
    ClientException,
    DirectoryLimitExceededException,
    EntityAlreadyExistsException,
    EntityDoesNotExistException,
    InvalidParameterException,
    TagLimitExceededException,
    UnsupportedOperationException,
    ValidationException,
)
from moto.ds.utils import PAGINATION_MODEL, SETTINGS_ENTRIES_MODEL
from moto.ds.validations import validate_args
from moto.ec2 import ec2_backends
from moto.ec2.exceptions import InvalidSubnetIdError
from moto.moto_api._internal import mock_random
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService


class LdapsSettingInfo(BaseModel):
    def __init__(self) -> None:
        self.last_updated_date_time = unix_time()
        self.ldaps_status = "Enabled"
        self.ldaps_status_reason = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "LastUpdatedDateTime": self.last_updated_date_time,
            "LDAPSStatus": self.ldaps_status,
            "LDAPSStatusReason": self.ldaps_status_reason,
        }


class LogSubscription(BaseModel):
    def __init__(self, directory_id: str, log_group_name: str) -> None:
        self.directory_id = directory_id
        self.log_group_name = log_group_name
        self.created_date_time = unix_time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "SubscriptionCreatedDateTime": self.created_date_time,
            "DirectoryId": self.directory_id,
            "LogGroupName": self.log_group_name,
        }


class Trust(BaseModel):
    def __init__(
        self,
        directory_id: str,
        remote_domain_name: str,
        trust_password: str,
        trust_direction: str,
        trust_type: Optional[str],
        conditional_forwarder_ip_addrs: Optional[list[str]],
        selective_auth: Optional[str],
    ) -> None:
        self.trust_id = f"t-{mock_random.get_random_hex(10)}"
        self.created_date_time = unix_time()
        self.last_updated_date_time = self.created_date_time
        self.state_last_updated_date_time = self.created_date_time
        self.trust_state = "Creating"
        self.trust_state_reason = ""
        self.directory_id = directory_id
        self.remote_domain_name = remote_domain_name
        self.trust_password = trust_password
        self.trust_direction = trust_direction
        self.trust_type = trust_type
        self.conditional_forwarder_ip_addrs = conditional_forwarder_ip_addrs
        self.selective_auth = selective_auth

    def to_dict(self) -> dict[str, Any]:
        return {
            "CreatedDateTime": self.created_date_time,
            "DirectoryId": self.directory_id,
            "LastUpdatedDateTime": self.last_updated_date_time,
            "RemoteDomainName": self.remote_domain_name,
            "SelectiveAuth": self.selective_auth,
            "StateLastUpdatedDateTime": self.state_last_updated_date_time,
            "TrustDirection": self.trust_direction,
            "TrustId": self.trust_id,
            "TrustState": self.trust_state,
            "TrustStateReason": self.trust_state_reason,
            "TrustType": self.trust_type,
        }


class SchemaExtension(BaseModel):
    def __init__(
        self,
        directory_id: str,
        create_snapshot_before_schema_extension: bool,
        ldif_content: str,
        description: str,
    ) -> None:
        self.schema_extension_id = f"e-{mock_random.get_random_hex(10)}"
        self.directory_id = directory_id
        self.create_snapshot_before_schema_extension = (
            create_snapshot_before_schema_extension
        )
        self.ldif_content = ldif_content
        self.description = description
        self.schema_extension_status = "Completed"
        self.schema_extension_status_reason = ""
        self.start_date_time = unix_time()
        self.end_date_time = unix_time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "DirectoryId": self.directory_id,
            "SchemaExtensionId": self.schema_extension_id,
            "Description": self.description,
            "SchemaExtensionStatus": self.schema_extension_status,
            "SchemaExtensionStatusReason": self.schema_extension_status_reason,
            "StartDateTime": self.start_date_time,
            "EndDateTime": self.end_date_time,
        }


class ConditionalForwarder(BaseModel):
    def __init__(
        self,
        directory_id: str,
        remote_domain_name: str,
        dns_ip_addrs: list[str],
    ) -> None:
        self.directory_id = directory_id
        self.remote_domain_name = remote_domain_name
        self.dns_ip_addrs = dns_ip_addrs
        self.replication_scope = "Domain"

    def to_dict(self) -> dict[str, Any]:
        return {
            "RemoteDomainName": self.remote_domain_name,
            "DnsIpAddrs": self.dns_ip_addrs,
            "ReplicationScope": self.replication_scope,
        }


class Snapshot(BaseModel):
    def __init__(self, directory_id: str, name: Optional[str] = None) -> None:
        self.snapshot_id = f"s-{mock_random.get_random_hex(10)}"
        self.directory_id = directory_id
        self.name = name or ""
        self.status = "Completed"
        self.type = "Manual"
        self.start_time = unix_time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "SnapshotId": self.snapshot_id,
            "DirectoryId": self.directory_id,
            "Name": self.name,
            "Status": self.status,
            "Type": self.type,
            "StartTime": self.start_time,
        }


class EventTopic(BaseModel):
    def __init__(self, directory_id: str, topic_name: str, sns_topic_arn: str) -> None:
        self.directory_id = directory_id
        self.topic_name = topic_name
        self.sns_topic_arn = sns_topic_arn
        self.created_date_time = unix_time()
        self.status = "Registered"

    def to_dict(self) -> dict[str, Any]:
        return {
            "DirectoryId": self.directory_id,
            "TopicName": self.topic_name,
            "TopicArn": self.sns_topic_arn,
            "CreatedDateTime": self.created_date_time,
            "Status": self.status,
        }


class IpRoute(BaseModel):
    def __init__(
        self,
        directory_id: str,
        cidr_ip: str,
        description: str,
    ) -> None:
        self.directory_id = directory_id
        self.cidr_ip = cidr_ip
        self.description = description
        self.added_date_time = unix_time()
        self.ip_route_status_msg = "Added"

    def to_dict(self) -> dict[str, Any]:
        return {
            "DirectoryId": self.directory_id,
            "CidrIp": self.cidr_ip,
            "IpRouteStatusMsg": self.ip_route_status_msg,
            "AddedDateTime": self.added_date_time,
            "IpRouteStatusReason": "",
            "Description": self.description,
        }


class Certificate(BaseModel):
    def __init__(
        self,
        directory_id: str,
        certificate_data: str,
        client_cert_auth_settings: Optional[dict[str, Any]] = None,
        cert_type: Optional[str] = None,
    ) -> None:
        self.certificate_id = f"c-{mock_random.get_random_hex(10)}"
        self.directory_id = directory_id
        self.certificate_data = certificate_data
        self.client_cert_auth_settings = client_cert_auth_settings
        self.type = cert_type or "ClientCertAuth"
        self.registered_date_time = unix_time()
        self.state = "Registered"
        self.common_name = "MockCertificate"
        self.expiry_date_time = unix_time() + 365 * 24 * 3600

    def to_dict(self) -> dict[str, Any]:
        return {
            "CertificateId": self.certificate_id,
            "State": self.state,
            "CommonName": self.common_name,
            "RegisteredDateTime": self.registered_date_time,
            "ExpiryDateTime": self.expiry_date_time,
            "Type": self.type,
        }

    def to_full_dict(self) -> dict[str, Any]:
        result = self.to_dict()
        result["StateReason"] = ""
        if self.client_cert_auth_settings:
            result["ClientCertAuthSettings"] = self.client_cert_auth_settings
        return result


class Computer(BaseModel):
    def __init__(
        self,
        directory_id: str,
        computer_name: str,
        password: str,
        organizational_unit_distinguished_name: Optional[str],
        computer_attributes: Optional[list[dict[str, str]]],
    ) -> None:
        self.computer_id = f"comp-{mock_random.get_random_hex(10)}"
        self.directory_id = directory_id
        self.computer_name = computer_name
        self.password = password
        self.organizational_unit_distinguished_name = (
            organizational_unit_distinguished_name
        )
        self.computer_attributes = computer_attributes or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "ComputerId": self.computer_id,
            "ComputerName": self.computer_name,
            "ComputerAttributes": self.computer_attributes,
        }


class Directory(BaseModel):
    """Representation of a Simple AD Directory.

    When the "create" API for a Simple AD or a Microsoft AD directory is
    invoked, two domain controllers and a DNS server are supposed to be
    created.  That is NOT done for the fake directories.

    However, the DnsIpAddrs attribute is supposed to contain the IP addresses
    of the DNS servers.  For a AD Connecter, the DnsIpAddrs are provided when
    the directory is created, but the ConnectSettings.ConnectIps values should
    contain the IP addresses of the DNS servers or domain controllers in the
    directory to which the AD connector is connected.

    Instead, the dns_ip_addrs attribute or ConnectIPs attribute for the fake
    directories will contain IPs picked from the subnets' CIDR blocks.
    """

    # The assumption here is that the limits are the same for all regions.
    CLOUDONLY_DIRECTORIES_LIMIT = 10
    CLOUDONLY_MICROSOFT_AD_LIMIT = 20
    CONNECTED_DIRECTORIES_LIMIT = 10

    MAX_TAGS_PER_DIRECTORY = 50

    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        password: str,
        directory_type: str,
        size: Optional[str] = None,
        vpc_settings: Optional[dict[str, Any]] = None,
        connect_settings: Optional[dict[str, Any]] = None,
        short_name: Optional[str] = None,
        description: Optional[str] = None,
        edition: Optional[str] = None,
    ):
        self.account_id = account_id
        self.region = region
        self.name = name
        self.password = password
        self.directory_type = directory_type
        self.size = size
        self.vpc_settings = vpc_settings
        self.connect_settings = connect_settings
        self.short_name = short_name
        self.description = description
        self.edition = edition

        # Calculated or default values for the directory attributes.
        self.directory_id = f"d-{mock_random.get_random_hex(10)}"
        self.access_url = f"{self.directory_id}.awsapps.com"
        self.alias = self.directory_id
        self.desired_number_of_domain_controllers = 0
        self.sso_enabled = False
        self.stage = "Active"
        self.launch_time = unix_time()
        self.stage_last_updated_date_time = unix_time()
        self.ldaps_settings_info: list[LdapsSettingInfo] = []
        self.trusts: list[Trust] = []
        self.settings = (
            copy.deepcopy(SETTINGS_ENTRIES_MODEL)
            if self.directory_type == "MicrosoftAD"
            else []
        )

        if self.directory_type == "ADConnector":
            self.security_group_id = self.create_security_group(
                self.connect_settings["VpcId"]  # type: ignore[index]
            )
            self.eni_ids, self.subnet_ips = self.create_eni(
                self.security_group_id,
                self.connect_settings["SubnetIds"],  # type: ignore[index]
            )
            self.connect_settings["SecurityGroupId"] = self.security_group_id  # type: ignore[index]
            self.connect_settings["ConnectIps"] = self.subnet_ips  # type: ignore[index]
            self.dns_ip_addrs = self.connect_settings["CustomerDnsIps"]  # type: ignore[index]

        else:
            self.security_group_id = self.create_security_group(
                self.vpc_settings["VpcId"]  # type: ignore[index]
            )
            self.eni_ids, self.subnet_ips = self.create_eni(
                self.security_group_id,
                self.vpc_settings["SubnetIds"],  # type: ignore[index]
            )
            self.vpc_settings["SecurityGroupId"] = self.security_group_id  # type: ignore[index]
            self.dns_ip_addrs = self.subnet_ips

    def create_security_group(self, vpc_id: str) -> str:
        """Create security group for the network interface."""
        security_group_info = ec2_backends[self.account_id][
            self.region
        ].create_security_group(
            name=f"{self.directory_id}_controllers",
            description=(
                f"AWS created security group for {self.directory_id} "
                f"directory controllers"
            ),
            vpc_id=vpc_id,
        )
        return security_group_info.id

    def delete_security_group(self) -> None:
        """Delete the given security group."""
        ec2_backends[self.account_id][self.region].delete_security_group(
            group_id=self.security_group_id
        )

    def create_eni(
        self, security_group_id: str, subnet_ids: list[str]
    ) -> tuple[list[str], list[str]]:
        """Return ENI ids and primary addresses created for each subnet."""
        eni_ids = []
        subnet_ips = []
        for subnet_id in subnet_ids:
            eni_info = ec2_backends[self.account_id][
                self.region
            ].create_network_interface(
                subnet=subnet_id,
                private_ip_address=None,  # type: ignore[arg-type]
                group_ids=[security_group_id],
                description=f"AWS created network interface for {self.directory_id}",
            )
            eni_ids.append(eni_info.id)
            subnet_ips.append(eni_info.private_ip_address)
        return eni_ids, subnet_ips  # type: ignore[return-value]

    def delete_eni(self) -> None:
        """Delete ENI for each subnet and the security group."""
        for eni_id in self.eni_ids:
            ec2_backends[self.account_id][self.region].delete_network_interface(eni_id)

    def update_alias(self, alias: str) -> None:
        """Change default alias to given alias."""
        self.alias = alias
        self.access_url = f"{alias}.awsapps.com"

    def enable_sso(self, new_state: bool) -> None:
        """Enable/disable sso based on whether new_state is True or False."""
        self.sso_enabled = new_state

    def enable_ldaps(self, enable: bool) -> None:
        """Enable/disable ldaps based on whether new_state is True or False.
        This method is only for MicrosoftAD.
        """
        if self.directory_type not in ("MicrosoftAD", "ADConnector"):
            raise UnsupportedOperationException(
                "LDAPS operations are not supported for this Directory Type."
            )
        if enable and len(self.ldaps_settings_info) == 0:
            ldaps_setting = LdapsSettingInfo()
            ldaps_setting.ldaps_status = "Enabled"
            self.ldaps_settings_info.append(ldaps_setting)
        elif not enable and len(self.ldaps_settings_info) > 0:
            for setting in self.ldaps_settings_info:
                setting.ldaps_status = "Disabled"

    def to_dict(self) -> dict[str, Any]:
        """Create a dictionary of attributes for Directory."""
        attributes = {
            "AccessUrl": self.access_url,
            "Alias": self.alias,
            "DirectoryId": self.directory_id,
            "DesiredNumberOfDomainControllers": self.desired_number_of_domain_controllers,
            "DnsIpAddrs": self.dns_ip_addrs,
            "LaunchTime": self.launch_time,
            "Name": self.name,
            "SsoEnabled": self.sso_enabled,
            "Stage": self.stage,
            "StageLastUpdatedDateTime": self.stage_last_updated_date_time,
            "Type": self.directory_type,
        }

        if self.edition:
            attributes["Edition"] = self.edition
        if self.size:
            attributes["Size"] = self.size
        if self.short_name:
            attributes["ShortName"] = self.short_name
        if self.description:
            attributes["Description"] = self.description

        if self.vpc_settings:
            attributes["VpcSettings"] = self.vpc_settings
        else:
            attributes["ConnectSettings"] = self.connect_settings
            attributes["ConnectSettings"]["CustomerDnsIps"] = None
        return attributes


class DirectoryServiceBackend(BaseBackend):
    """Implementation of DirectoryService APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.directories: dict[str, Directory] = {}
        self.log_subscriptions: dict[str, LogSubscription] = {}
        self.tagger = TaggingService()
        # Keyed by (directory_id, remote_domain_name)
        self.conditional_forwarders: dict[tuple[str, str], ConditionalForwarder] = {}
        # Keyed by snapshot_id
        self.snapshots: dict[str, Snapshot] = {}
        # Keyed by (directory_id, topic_name)
        self.event_topics: dict[tuple[str, str], EventTopic] = {}
        # Keyed by (directory_id, cidr_ip)
        self.ip_routes: dict[tuple[str, str], IpRoute] = {}
        # Keyed by certificate_id
        self.certificates: dict[str, Certificate] = {}
        # Keyed by directory_id -> {type -> enabled}
        self.radius_settings: dict[str, dict[str, Any]] = {}
        # Keyed by directory_id -> {type -> status}
        self.client_auth_settings: dict[str, dict[str, str]] = {}
        # Keyed by directory_id -> list of Computer
        self.computers: dict[str, list[Computer]] = {}
        # Keyed by schema_extension_id
        self.schema_extensions: dict[str, SchemaExtension] = {}
        # Keyed by assessment_id
        self.ad_assessments: dict[str, dict[str, Any]] = {}

    def _verify_subnets(self, region: str, vpc_settings: dict[str, Any]) -> None:
        """Verify subnets are valid, else raise an exception.

        If settings are valid, add AvailabilityZones to vpc_settings.
        """
        if len(vpc_settings["SubnetIds"]) != 2:
            raise InvalidParameterException(
                "Invalid subnet ID(s). They must correspond to two subnets "
                "in different Availability Zones."
            )

        # Subnet IDs are checked before the VPC ID.  The Subnet IDs must
        # be valid and in different availability zones.
        try:
            subnets = ec2_backends[self.account_id][region].describe_subnets(
                subnet_ids=vpc_settings["SubnetIds"]
            )
        except InvalidSubnetIdError as exc:
            raise InvalidParameterException(
                "Invalid subnet ID(s). They must correspond to two subnets "
                "in different Availability Zones."
            ) from exc

        regions = [subnet.availability_zone for subnet in subnets]
        if regions[0] == regions[1]:
            raise ClientException(
                "Invalid subnet ID(s). The two subnets must be in "
                "different Availability Zones."
            )

        vpcs = ec2_backends[self.account_id][region].describe_vpcs()
        if vpc_settings["VpcId"] not in [x.id for x in vpcs]:
            raise ClientException("Invalid VPC ID.")
        vpc_settings["AvailabilityZones"] = regions

    def connect_directory(
        self,
        region: str,
        name: str,
        short_name: str,
        password: str,
        description: str,
        size: str,
        connect_settings: dict[str, Any],
        tags: list[dict[str, str]],
    ) -> str:
        """Create a fake AD Connector."""
        if len(self.directories) > Directory.CONNECTED_DIRECTORIES_LIMIT:
            raise DirectoryLimitExceededException(
                f"Directory limit exceeded. A maximum of "
                f"{Directory.CONNECTED_DIRECTORIES_LIMIT} directories may be created"
            )

        validate_args(
            [
                ("password", password),
                ("size", size),
                ("name", name),
                ("description", description),
                ("shortName", short_name),
                (
                    "connectSettings.vpcSettings.subnetIds",
                    connect_settings["SubnetIds"],
                ),
                (
                    "connectSettings.customerUserName",
                    connect_settings["CustomerUserName"],
                ),
                ("connectSettings.customerDnsIps", connect_settings["CustomerDnsIps"]),
            ]
        )
        # ConnectSettings and VpcSettings both have a VpcId and Subnets.
        self._verify_subnets(region, connect_settings)

        errmsg = self.tagger.validate_tags(tags or [])
        if errmsg:
            raise ValidationException(errmsg)
        if len(tags) > Directory.MAX_TAGS_PER_DIRECTORY:
            raise DirectoryLimitExceededException("Tag Limit is exceeding")

        directory = Directory(
            self.account_id,
            region,
            name,
            password,
            "ADConnector",
            size=size,
            connect_settings=connect_settings,
            short_name=short_name,
            description=description,
        )
        self.directories[directory.directory_id] = directory
        self.tagger.tag_resource(directory.directory_id, tags or [])
        return directory.directory_id

    def create_directory(
        self,
        region: str,
        name: str,
        short_name: str,
        password: str,
        description: str,
        size: str,
        vpc_settings: dict[str, Any],
        tags: list[dict[str, str]],
    ) -> str:
        """Create a fake Simple Ad Directory."""
        if len(self.directories) > Directory.CLOUDONLY_DIRECTORIES_LIMIT:
            raise DirectoryLimitExceededException(
                f"Directory limit exceeded. A maximum of "
                f"{Directory.CLOUDONLY_DIRECTORIES_LIMIT} directories may be created"
            )

        # botocore doesn't look for missing vpc_settings, but boto3 does.
        if not vpc_settings:
            raise InvalidParameterException("VpcSettings must be specified.")
        validate_args(
            [
                ("password", password),
                ("size", size),
                ("name", name),
                ("description", description),
                ("shortName", short_name),
                ("vpcSettings.subnetIds", vpc_settings["SubnetIds"]),
            ]
        )
        self._verify_subnets(region, vpc_settings)

        errmsg = self.tagger.validate_tags(tags or [])
        if errmsg:
            raise ValidationException(errmsg)
        if len(tags) > Directory.MAX_TAGS_PER_DIRECTORY:
            raise DirectoryLimitExceededException("Tag Limit is exceeding")

        directory = Directory(
            self.account_id,
            region,
            name,
            password,
            "SimpleAD",
            size=size,
            vpc_settings=vpc_settings,
            short_name=short_name,
            description=description,
        )
        self.directories[directory.directory_id] = directory
        self.tagger.tag_resource(directory.directory_id, tags or [])
        return directory.directory_id

    def _validate_directory_id(self, directory_id: str) -> None:
        """Raise an exception if the directory id is invalid or unknown."""
        # Validation of ID takes precedence over a check for its existence.
        validate_args([("directoryId", directory_id)])
        if directory_id not in self.directories:
            raise EntityDoesNotExistException(
                f"Directory {directory_id} does not exist"
            )

    def create_alias(self, directory_id: str, alias: str) -> dict[str, str]:
        """Create and assign an alias to a directory."""
        self._validate_directory_id(directory_id)

        # The default alias name is the same as the directory name.  Check
        # whether this directory was already given an alias.
        directory = self.directories[directory_id]
        if directory.alias != directory_id:
            raise InvalidParameterException(
                "The directory in the request already has an alias. That "
                "alias must be deleted before a new alias can be created."
            )

        # Is the alias already in use?
        if alias in [x.alias for x in self.directories.values()]:
            raise EntityAlreadyExistsException(f"Alias '{alias}' already exists.")
        validate_args([("alias", alias)])

        directory.update_alias(alias)
        return {"DirectoryId": directory_id, "Alias": alias}

    def create_microsoft_ad(
        self,
        region: str,
        name: str,
        short_name: str,
        password: str,
        description: str,
        vpc_settings: dict[str, Any],
        edition: str,
        tags: list[dict[str, str]],
    ) -> str:
        """Create a fake Microsoft Ad Directory."""
        if len(self.directories) > Directory.CLOUDONLY_MICROSOFT_AD_LIMIT:
            raise DirectoryLimitExceededException(
                f"Directory limit exceeded. A maximum of "
                f"{Directory.CLOUDONLY_MICROSOFT_AD_LIMIT} directories may be created"
            )

        # boto3 looks for missing vpc_settings for create_microsoft_ad().
        validate_args(
            [
                ("password", password),
                ("edition", edition),
                ("name", name),
                ("description", description),
                ("shortName", short_name),
                ("vpcSettings.subnetIds", vpc_settings["SubnetIds"]),
            ]
        )
        self._verify_subnets(region, vpc_settings)

        errmsg = self.tagger.validate_tags(tags or [])
        if errmsg:
            raise ValidationException(errmsg)
        if len(tags) > Directory.MAX_TAGS_PER_DIRECTORY:
            raise DirectoryLimitExceededException("Tag Limit is exceeding")

        directory = Directory(
            self.account_id,
            region,
            name,
            password,
            "MicrosoftAD",
            vpc_settings=vpc_settings,
            short_name=short_name,
            description=description,
            edition=edition,
        )
        self.directories[directory.directory_id] = directory
        self.tagger.tag_resource(directory.directory_id, tags or [])
        return directory.directory_id

    def delete_directory(self, directory_id: str) -> str:
        """Delete directory with the matching ID."""
        self._validate_directory_id(directory_id)
        self.directories[directory_id].delete_eni()
        self.directories[directory_id].delete_security_group()
        self.tagger.delete_all_tags_for_resource(directory_id)
        self.directories.pop(directory_id)
        return directory_id

    def disable_sso(
        self,
        directory_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Disable single-sign on for a directory."""
        self._validate_directory_id(directory_id)
        validate_args([("ssoPassword", password), ("userName", username)])
        directory = self.directories[directory_id]
        directory.enable_sso(False)

    def enable_sso(
        self,
        directory_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Enable single-sign on for a directory."""
        self._validate_directory_id(directory_id)
        validate_args([("ssoPassword", password), ("userName", username)])

        directory = self.directories[directory_id]
        if directory.alias == directory_id:
            raise ClientException(
                f"An alias is required before enabling SSO. DomainId={directory_id}"
            )

        directory = self.directories[directory_id]
        directory.enable_sso(True)

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_directories(
        self, directory_ids: Optional[list[str]] = None
    ) -> list[Directory]:
        """Return info on all directories or directories with matching IDs."""
        for directory_id in directory_ids or self.directories:
            self._validate_directory_id(directory_id)

        directories = list(self.directories.values())
        if directory_ids:
            directories = [x for x in directories if x.directory_id in directory_ids]
        return sorted(directories, key=lambda x: x.launch_time)

    def get_directory_limits(self) -> dict[str, Any]:
        """Return hard-coded limits for the directories."""
        counts = {"SimpleAD": 0, "MicrosoftAD": 0, "ConnectedAD": 0}
        for directory in self.directories.values():
            if directory.directory_type == "SimpleAD":
                counts["SimpleAD"] += 1
            elif directory.directory_type in ["MicrosoftAD", "SharedMicrosoftAD"]:
                counts["MicrosoftAD"] += 1
            elif directory.directory_type == "ADConnector":
                counts["ConnectedAD"] += 1

        return {
            "CloudOnlyDirectoriesLimit": Directory.CLOUDONLY_DIRECTORIES_LIMIT,
            "CloudOnlyDirectoriesCurrentCount": counts["SimpleAD"],
            "CloudOnlyDirectoriesLimitReached": counts["SimpleAD"]
            == Directory.CLOUDONLY_DIRECTORIES_LIMIT,
            "CloudOnlyMicrosoftADLimit": Directory.CLOUDONLY_MICROSOFT_AD_LIMIT,
            "CloudOnlyMicrosoftADCurrentCount": counts["MicrosoftAD"],
            "CloudOnlyMicrosoftADLimitReached": counts["MicrosoftAD"]
            == Directory.CLOUDONLY_MICROSOFT_AD_LIMIT,
            "ConnectedDirectoriesLimit": Directory.CONNECTED_DIRECTORIES_LIMIT,
            "ConnectedDirectoriesCurrentCount": counts["ConnectedAD"],
            "ConnectedDirectoriesLimitReached": counts["ConnectedAD"]
            == Directory.CONNECTED_DIRECTORIES_LIMIT,
        }

    def add_tags_to_resource(
        self, resource_id: str, tags: list[dict[str, str]]
    ) -> None:
        """Add or overwrite one or more tags for specified directory."""
        self._validate_directory_id(resource_id)
        errmsg = self.tagger.validate_tags(tags)
        if errmsg:
            raise ValidationException(errmsg)
        if len(tags) > Directory.MAX_TAGS_PER_DIRECTORY:
            raise TagLimitExceededException("Tag limit exceeded")
        self.tagger.tag_resource(resource_id, tags)

    def remove_tags_from_resource(self, resource_id: str, tag_keys: list[str]) -> None:
        """Removes tags from a directory."""
        self._validate_directory_id(resource_id)
        self.tagger.untag_resource_using_names(resource_id, tag_keys)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_tags_for_resource(self, resource_id: str) -> list[dict[str, str]]:
        """List all tags on a directory."""
        self._validate_directory_id(resource_id)
        return self.tagger.list_tags_for_resource(resource_id).get("Tags")  # type: ignore[return-value]

    def create_trust(
        self,
        directory_id: str,
        remote_domain_name: str,
        trust_password: str,
        trust_direction: str,
        trust_type: Optional[str],
        conditional_forwarder_ip_addrs: Optional[list[str]],
        selective_auth: Optional[str],
    ) -> str:
        self._validate_directory_id(directory_id)
        validate_args(
            [
                ("ssoPassword", trust_password),
                ("trustDirection", trust_direction),
                ("remoteDomainName", remote_domain_name),
            ]
        )
        directory = self.directories[directory_id]
        trust = Trust(
            directory_id=directory_id,
            remote_domain_name=remote_domain_name,
            trust_password=trust_password,
            trust_direction=trust_direction,
            trust_type=trust_type,
            conditional_forwarder_ip_addrs=conditional_forwarder_ip_addrs,
            selective_auth=selective_auth,
        )
        directory.trusts.append(trust)
        return trust.trust_id

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_trusts(
        self, directory_id: Optional[str], trust_ids: Optional[list[str]]
    ) -> list[Trust]:
        if directory_id:
            self._validate_directory_id(directory_id)
            directory = self.directories[directory_id]
            trusts = directory.trusts
        else:
            trusts = [
                trust
                for directory in self.directories.values()
                for trust in directory.trusts
            ]
        if trust_ids:
            queried_trusts = [t for t in trusts if t.trust_id in trust_ids]
        else:
            queried_trusts = trusts
        return queried_trusts

    def delete_trust(
        self, trust_id: str, delete_associated_conditional_forwarder: Optional[bool]
    ) -> str:
        # TODO: Implement handle for delete_associated_conditional_forwarder once conditional forwarder is implemented
        delete_associated_conditional_forwarder = (
            delete_associated_conditional_forwarder or False
        )
        for directory in self.directories.values():
            for trust in directory.trusts:
                if trust.trust_id == trust_id:
                    directory.trusts.remove(trust)
                    return trust_id
        raise EntityDoesNotExistException(f"Trust {trust_id} does not exist")

    def verify_trust(self, trust_id: str) -> str:
        """Verify a trust relationship. Sets trust state to Verified."""
        for directory in self.directories.values():
            for trust in directory.trusts:
                if trust.trust_id == trust_id:
                    trust.trust_state = "Verified"
                    trust.last_updated_date_time = unix_time()
                    trust.state_last_updated_date_time = unix_time()
                    return trust_id
        raise EntityDoesNotExistException(f"Trust {trust_id} does not exist")

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_ldaps_settings(
        self, directory_id: str, type: str
    ) -> list[LdapsSettingInfo]:
        """Describe LDAPS settings for a Directory"""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        if directory.directory_type not in ("MicrosoftAD", "ADConnector"):
            raise UnsupportedOperationException(
                "LDAPS operations are not supported for this Directory Type."
            )

        return directory.ldaps_settings_info

    def enable_ldaps(self, directory_id: str, type: str) -> None:
        """Enable LDAPS for a Directory"""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        directory.enable_ldaps(True)

    def disable_ldaps(self, directory_id: str, type: str) -> None:
        """Disable LDAPS for a Directory"""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        directory.enable_ldaps(False)

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_settings(
        self, directory_id: str, status: Optional[str]
    ) -> list[dict[str, str]]:
        """Describe settings for a Directory"""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        if directory.directory_type not in ("MicrosoftAD"):
            raise InvalidParameterException(
                "This operation is only supported for Microsoft AD"
            )
        if status:
            queried_settings = [
                setting
                for setting in directory.settings
                if setting["RequestStatus"] == status
            ]
        else:
            queried_settings = directory.settings
        return queried_settings

    def update_settings(self, directory_id: str, settings: list[dict[str, Any]]) -> str:
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        if directory.directory_type not in ("MicrosoftAD"):
            raise InvalidParameterException(
                "This operation is only supported for Microsoft AD"
            )
        for s in settings:
            for setting in directory.settings:
                if setting["Name"] == s["Name"]:
                    # TODO: Add validation for the value
                    setting["AppliedValue"] = s["Value"]

        return directory_id

    def describe_ad_assessment(
        self, assessment_id: str
    ) -> dict[str, Any]:
        """Describe an AD assessment."""
        if assessment_id not in self.ad_assessments:
            raise EntityDoesNotExistException(
                f"Assessment {assessment_id} does not exist"
            )
        return self.ad_assessments[assessment_id]

    def describe_ca_enrollment_policy(
        self, directory_id: str
    ) -> dict[str, Any]:
        """Describe CA enrollment policy — returns disabled state."""
        self._validate_directory_id(directory_id)
        return {
            "DirectoryId": directory_id,
            "CaEnrollmentPolicyStatus": "Disabled",
        }

    def create_conditional_forwarder(
        self,
        directory_id: str,
        remote_domain_name: str,
        dns_ip_addrs: list[str],
    ) -> None:
        """Create a conditional forwarder for a directory."""
        self._validate_directory_id(directory_id)
        key = (directory_id, remote_domain_name)
        if key in self.conditional_forwarders:
            raise EntityAlreadyExistsException(
                f"Conditional forwarder for domain {remote_domain_name} already exists"
            )
        forwarder = ConditionalForwarder(
            directory_id=directory_id,
            remote_domain_name=remote_domain_name,
            dns_ip_addrs=dns_ip_addrs,
        )
        self.conditional_forwarders[key] = forwarder

    def delete_conditional_forwarder(
        self,
        directory_id: str,
        remote_domain_name: str,
    ) -> None:
        """Delete a conditional forwarder."""
        self._validate_directory_id(directory_id)
        key = (directory_id, remote_domain_name)
        if key not in self.conditional_forwarders:
            raise EntityDoesNotExistException(
                f"Conditional forwarder for domain {remote_domain_name} does not exist"
            )
        self.conditional_forwarders.pop(key)

    def update_conditional_forwarder(
        self,
        directory_id: str,
        remote_domain_name: str,
        dns_ip_addrs: list[str],
    ) -> None:
        """Update a conditional forwarder's DNS IP addresses."""
        self._validate_directory_id(directory_id)
        key = (directory_id, remote_domain_name)
        if key not in self.conditional_forwarders:
            raise EntityDoesNotExistException(
                f"Conditional forwarder for domain {remote_domain_name} does not exist"
            )
        self.conditional_forwarders[key].dns_ip_addrs = dns_ip_addrs

    def describe_conditional_forwarders(
        self, directory_id: str, remote_domain_names: Optional[list[str]]
    ) -> list[dict[str, Any]]:
        """Describe conditional forwarders for a directory."""
        self._validate_directory_id(directory_id)
        forwarders = [
            f.to_dict()
            for key, f in self.conditional_forwarders.items()
            if key[0] == directory_id
        ]
        if remote_domain_names:
            forwarders = [
                f for f in forwarders if f["RemoteDomainName"] in remote_domain_names
            ]
        return forwarders

    def describe_domain_controllers(
        self, directory_id: str, domain_controller_ids: Optional[list[str]]
    ) -> list[dict[str, Any]]:
        """Describe domain controllers for a directory."""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        # Generate two fake domain controllers for Microsoft AD directories
        if directory.directory_type != "MicrosoftAD":
            raise UnsupportedOperationException(
                "Domain controllers are not supported for this Directory Type."
            )
        controllers = []
        for i, subnet_ip in enumerate(directory.dns_ip_addrs):
            dc_id = f"{directory_id}-dc-{mock_random.get_random_hex(8)}-{i}"
            vpc_id = directory.vpc_settings["VpcId"] if directory.vpc_settings else ""
            subnet_id = (
                directory.vpc_settings["SubnetIds"][i]
                if directory.vpc_settings and i < len(directory.vpc_settings["SubnetIds"])
                else ""
            )
            az = (
                directory.vpc_settings["AvailabilityZones"][i]
                if directory.vpc_settings
                and "AvailabilityZones" in directory.vpc_settings
                and i < len(directory.vpc_settings["AvailabilityZones"])
                else f"{self.region_name}a"
            )
            controllers.append(
                {
                    "DirectoryId": directory_id,
                    "DomainControllerId": dc_id,
                    "DnsIpAddr": subnet_ip,
                    "VpcId": vpc_id,
                    "SubnetId": subnet_id,
                    "AvailabilityZone": az,
                    "Status": "Active",
                    "StatusReason": "",
                    "LaunchTime": directory.launch_time,
                    "StatusLastUpdatedDateTime": directory.stage_last_updated_date_time,
                }
            )
        if domain_controller_ids:
            controllers = [
                c for c in controllers if c["DomainControllerId"] in domain_controller_ids
            ]
        return controllers

    def register_event_topic(
        self,
        directory_id: str,
        topic_name: str,
        sns_topic_arn: str,
    ) -> None:
        """Register an event topic for a directory."""
        self._validate_directory_id(directory_id)
        key = (directory_id, topic_name)
        topic = EventTopic(
            directory_id=directory_id,
            topic_name=topic_name,
            sns_topic_arn=sns_topic_arn,
        )
        self.event_topics[key] = topic

    def deregister_event_topic(
        self,
        directory_id: str,
        topic_name: str,
    ) -> None:
        """Deregister an event topic."""
        self._validate_directory_id(directory_id)
        key = (directory_id, topic_name)
        if key not in self.event_topics:
            raise EntityDoesNotExistException(
                f"Topic {topic_name} does not exist for directory {directory_id}"
            )
        self.event_topics.pop(key)

    def describe_event_topics(
        self, directory_id: Optional[str], topic_names: Optional[list[str]]
    ) -> list[dict[str, Any]]:
        """Describe event topics for a directory."""
        if directory_id:
            self._validate_directory_id(directory_id)
        topics = list(self.event_topics.values())
        if directory_id:
            topics = [t for t in topics if t.directory_id == directory_id]
        if topic_names:
            topics = [t for t in topics if t.topic_name in topic_names]
        return [t.to_dict() for t in topics]

    def create_snapshot(
        self,
        directory_id: str,
        name: Optional[str] = None,
    ) -> str:
        """Create a snapshot of a directory."""
        self._validate_directory_id(directory_id)
        snapshot = Snapshot(directory_id=directory_id, name=name)
        self.snapshots[snapshot.snapshot_id] = snapshot
        return snapshot.snapshot_id

    def delete_snapshot(self, snapshot_id: str) -> str:
        """Delete a directory snapshot."""
        if snapshot_id not in self.snapshots:
            raise EntityDoesNotExistException(
                f"Snapshot {snapshot_id} does not exist"
            )
        self.snapshots[snapshot_id].status = "Deleted"
        self.snapshots.pop(snapshot_id)
        return snapshot_id

    def restore_from_snapshot(self, snapshot_id: str) -> None:
        """Restore a directory from a snapshot (no-op in mock)."""
        if snapshot_id not in self.snapshots:
            raise EntityDoesNotExistException(
                f"Snapshot {snapshot_id} does not exist"
            )

    def describe_snapshots(
        self, directory_id: Optional[str], snapshot_ids: Optional[list[str]]
    ) -> list[dict[str, Any]]:
        """Describe snapshots for a directory."""
        if directory_id:
            self._validate_directory_id(directory_id)
        snapshots = list(self.snapshots.values())
        if directory_id:
            snapshots = [s for s in snapshots if s.directory_id == directory_id]
        if snapshot_ids:
            snapshots = [s for s in snapshots if s.snapshot_id in snapshot_ids]
        return [s.to_dict() for s in snapshots]

    def describe_shared_directories(
        self, owner_directory_id: str, shared_directory_ids: Optional[list[str]]
    ) -> list[dict[str, Any]]:
        """Describe shared directories — returns empty list."""
        self._validate_directory_id(owner_directory_id)
        return []

    def describe_regions(
        self, directory_id: str, region_name: Optional[str]
    ) -> list[dict[str, Any]]:
        """Describe regions for a directory."""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        vpc_id = ""
        subnet_ids: list[str] = []
        if directory.vpc_settings:
            vpc_id = directory.vpc_settings.get("VpcId", "")
            subnet_ids = directory.vpc_settings.get("SubnetIds", [])
        elif directory.connect_settings:
            vpc_id = directory.connect_settings.get("VpcId", "")
            subnet_ids = directory.connect_settings.get("SubnetIds", [])
        regions_info = [
            {
                "DirectoryId": directory_id,
                "RegionName": self.region_name,
                "RegionType": "Primary",
                "Status": "Active",
                "VpcSettings": {
                    "VpcId": vpc_id,
                    "SubnetIds": subnet_ids,
                },
                "DesiredNumberOfDomainControllers": directory.desired_number_of_domain_controllers,
                "LaunchTime": directory.launch_time,
                "StatusLastUpdatedDateTime": directory.stage_last_updated_date_time,
                "LastUpdatedDateTime": directory.stage_last_updated_date_time,
            }
        ]
        if region_name:
            regions_info = [r for r in regions_info if r["RegionName"] == region_name]
        return regions_info

    def enable_radius(
        self,
        directory_id: str,
        radius_settings: dict[str, Any],
    ) -> None:
        """Enable multi-factor authentication (MFA) with RADIUS."""
        self._validate_directory_id(directory_id)
        self.radius_settings[directory_id] = radius_settings

    def disable_radius(self, directory_id: str) -> None:
        """Disable multi-factor authentication (MFA) with RADIUS."""
        self._validate_directory_id(directory_id)
        self.radius_settings.pop(directory_id, None)

    def update_radius(
        self,
        directory_id: str,
        radius_settings: dict[str, Any],
    ) -> None:
        """Update the RADIUS server information for a directory."""
        self._validate_directory_id(directory_id)
        if directory_id not in self.radius_settings:
            raise EntityDoesNotExistException(
                f"RADIUS is not enabled for directory {directory_id}"
            )
        self.radius_settings[directory_id] = radius_settings

    def enable_client_authentication(
        self,
        directory_id: str,
        type: str,
    ) -> None:
        """Enable client authentication for a directory."""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        if directory.directory_type != "MicrosoftAD":
            raise UnsupportedOperationException(
                "Client authentication is only supported for Microsoft AD directories."
            )
        if directory_id not in self.client_auth_settings:
            self.client_auth_settings[directory_id] = {}
        self.client_auth_settings[directory_id][type] = "Enabled"

    def disable_client_authentication(
        self,
        directory_id: str,
        type: str,
    ) -> None:
        """Disable client authentication for a directory."""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        if directory.directory_type != "MicrosoftAD":
            raise UnsupportedOperationException(
                "Client authentication is only supported for Microsoft AD directories."
            )
        if directory_id in self.client_auth_settings:
            self.client_auth_settings[directory_id].pop(type, None)

    def describe_client_authentication_settings(
        self, directory_id: str, type: Optional[str]
    ) -> list[dict[str, Any]]:
        """Describe client authentication settings for a directory."""
        self._validate_directory_id(directory_id)
        settings = self.client_auth_settings.get(directory_id, {})
        result = []
        for auth_type, status in settings.items():
            if type and auth_type != type:
                continue
            result.append(
                {
                    "Type": auth_type,
                    "Status": status,
                    "LastUpdatedDateTime": unix_time(),
                }
            )
        return result

    def describe_update_directory(
        self, directory_id: str, update_type: Optional[str]
    ) -> list[dict[str, Any]]:
        """Describe update directory activities — returns empty list."""
        self._validate_directory_id(directory_id)
        return []

    def register_certificate(
        self,
        directory_id: str,
        certificate_data: str,
        client_cert_auth_settings: Optional[dict[str, Any]] = None,
        cert_type: Optional[str] = None,
    ) -> str:
        """Register a certificate for a directory."""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        if directory.directory_type != "MicrosoftAD":
            raise UnsupportedOperationException(
                "Certificates are only supported for Microsoft AD directories."
            )
        cert = Certificate(
            directory_id=directory_id,
            certificate_data=certificate_data,
            client_cert_auth_settings=client_cert_auth_settings,
            cert_type=cert_type,
        )
        self.certificates[cert.certificate_id] = cert
        return cert.certificate_id

    def deregister_certificate(
        self,
        directory_id: str,
        certificate_id: str,
    ) -> None:
        """Deregister a certificate."""
        self._validate_directory_id(directory_id)
        if certificate_id not in self.certificates:
            raise EntityDoesNotExistException(
                f"Certificate {certificate_id} does not exist"
            )
        cert = self.certificates[certificate_id]
        if cert.directory_id != directory_id:
            raise EntityDoesNotExistException(
                f"Certificate {certificate_id} does not exist"
            )
        self.certificates.pop(certificate_id)

    def list_certificates(
        self,
        directory_id: str,
    ) -> list[dict[str, Any]]:
        """List certificates for a directory."""
        self._validate_directory_id(directory_id)
        certs = [
            c.to_dict()
            for c in self.certificates.values()
            if c.directory_id == directory_id
        ]
        return certs

    def describe_certificate(
        self, directory_id: str, certificate_id: str
    ) -> dict[str, Any]:
        """Describe a certificate."""
        self._validate_directory_id(directory_id)
        if certificate_id not in self.certificates:
            raise EntityDoesNotExistException(
                f"Certificate {certificate_id} does not exist"
            )
        cert = self.certificates[certificate_id]
        if cert.directory_id != directory_id:
            raise EntityDoesNotExistException(
                f"Certificate {certificate_id} does not exist"
            )
        return cert.to_full_dict()

    def get_snapshot_limits(self, directory_id: str) -> dict[str, Any]:
        """Return snapshot limits for a directory."""
        self._validate_directory_id(directory_id)
        return {
            "ManualSnapshotsLimit": 5,
            "ManualSnapshotsCurrentCount": 0,
            "ManualSnapshotsLimitReached": False,
        }

    def add_ip_routes(
        self,
        directory_id: str,
        ip_routes: list[dict[str, str]],
        update_security_group_for_directory_controllers: bool,
    ) -> None:
        """Add IP address routes to the directory."""
        self._validate_directory_id(directory_id)
        for route_info in ip_routes:
            cidr_ip = route_info["CidrIp"]
            description = route_info.get("Description", "")
            key = (directory_id, cidr_ip)
            if key in self.ip_routes:
                raise EntityAlreadyExistsException(
                    f"IP route {cidr_ip} already exists for directory {directory_id}"
                )
            ip_route = IpRoute(
                directory_id=directory_id,
                cidr_ip=cidr_ip,
                description=description,
            )
            self.ip_routes[key] = ip_route

    def remove_ip_routes(
        self,
        directory_id: str,
        cidr_ips: list[str],
    ) -> None:
        """Remove IP address routes from the directory."""
        self._validate_directory_id(directory_id)
        for cidr_ip in cidr_ips:
            key = (directory_id, cidr_ip)
            if key not in self.ip_routes:
                raise EntityDoesNotExistException(
                    f"IP route {cidr_ip} does not exist for directory {directory_id}"
                )
            self.ip_routes.pop(key)

    def list_ip_routes(self, directory_id: str) -> list[dict[str, Any]]:
        """List IP routes for a directory."""
        self._validate_directory_id(directory_id)
        routes = [
            r.to_dict()
            for key, r in self.ip_routes.items()
            if key[0] == directory_id
        ]
        return routes

    def start_schema_extension(
        self,
        directory_id: str,
        create_snapshot_before_schema_extension: bool,
        ldif_content: str,
        description: str,
    ) -> str:
        """Apply a schema extension to a Microsoft AD directory."""
        self._validate_directory_id(directory_id)
        directory = self.directories[directory_id]
        if directory.directory_type != "MicrosoftAD":
            raise UnsupportedOperationException(
                "Schema extensions are only supported for Microsoft AD directories."
            )
        ext = SchemaExtension(
            directory_id=directory_id,
            create_snapshot_before_schema_extension=create_snapshot_before_schema_extension,
            ldif_content=ldif_content,
            description=description,
        )
        self.schema_extensions[ext.schema_extension_id] = ext
        return ext.schema_extension_id

    def cancel_schema_extension(
        self,
        directory_id: str,
        schema_extension_id: str,
    ) -> None:
        """Cancel a schema extension."""
        self._validate_directory_id(directory_id)
        if schema_extension_id not in self.schema_extensions:
            raise EntityDoesNotExistException(
                f"Schema extension {schema_extension_id} does not exist"
            )
        ext = self.schema_extensions[schema_extension_id]
        if ext.directory_id != directory_id:
            raise EntityDoesNotExistException(
                f"Schema extension {schema_extension_id} does not exist"
            )
        ext.schema_extension_status = "CancelledByUser"
        ext.end_date_time = unix_time()

    def list_schema_extensions(self, directory_id: str) -> list[dict[str, Any]]:
        """List schema extensions for a directory."""
        self._validate_directory_id(directory_id)
        return [
            ext.to_dict()
            for ext in self.schema_extensions.values()
            if ext.directory_id == directory_id
        ]

    def create_computer(
        self,
        directory_id: str,
        computer_name: str,
        password: str,
        organizational_unit_distinguished_name: Optional[str],
        computer_attributes: Optional[list[dict[str, str]]],
    ) -> dict[str, Any]:
        """Create a computer account in the directory."""
        self._validate_directory_id(directory_id)
        computer = Computer(
            directory_id=directory_id,
            computer_name=computer_name,
            password=password,
            organizational_unit_distinguished_name=organizational_unit_distinguished_name,
            computer_attributes=computer_attributes,
        )
        if directory_id not in self.computers:
            self.computers[directory_id] = []
        self.computers[directory_id].append(computer)
        return computer.to_dict()

    def reset_user_password(
        self,
        directory_id: str,
        user_name: str,
        new_password: str,
    ) -> None:
        """Reset a user password (no-op in mock)."""
        self._validate_directory_id(directory_id)
        # In a real implementation this would reset the user's password.
        # For mock purposes, we just validate the directory exists.

    def create_log_subscription(self, directory_id: str, log_group_name: str) -> None:
        self._validate_directory_id(directory_id)
        log_subscription = LogSubscription(directory_id, log_group_name)
        if directory_id not in self.log_subscriptions:
            self.log_subscriptions[directory_id] = log_subscription
        else:
            raise EntityAlreadyExistsException("Log subscription already exists")
        return

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_log_subscriptions(
        self,
        directory_id: str,
    ) -> list[LogSubscription]:
        if directory_id:
            self._validate_directory_id(directory_id)
            log_subscription = self.log_subscriptions.get(directory_id, None)
            if log_subscription:
                log_subscriptions = [log_subscription]
            else:
                log_subscriptions = []
        else:
            log_subscriptions = list(self.log_subscriptions.values())
        return log_subscriptions

    def delete_log_subscription(self, directory_id: str) -> None:
        self._validate_directory_id(directory_id)
        if directory_id in self.log_subscriptions:
            self.log_subscriptions.pop(directory_id)
        else:
            raise EntityDoesNotExistException(
                f"Log subscription for {directory_id} does not exist"
            )
        return


    def start_ad_assessment(self, directory_id: str) -> str:
        """Start an AD assessment and return a new assessment ID."""
        self._validate_directory_id(directory_id)
        from datetime import datetime, timezone

        assessment_id = str(mock_random.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        self.ad_assessments[assessment_id] = {
            "AssessmentId": assessment_id,
            "DirectoryId": directory_id,
            "Status": "InProgress",
            "StartTime": now,
            "LastUpdateDateTime": now,
        }
        return assessment_id

    def list_ad_assessments(self, directory_id: Optional[str] = None) -> list[dict[str, Any]]:
        """List AD assessments, optionally filtered by directory ID."""
        assessments = list(self.ad_assessments.values())
        if directory_id:
            assessments = [a for a in assessments if a.get("DirectoryId") == directory_id]
        return assessments

    def delete_ad_assessment(self, assessment_id: str) -> None:
        """Delete an AD assessment."""
        if assessment_id not in self.ad_assessments:
            raise EntityDoesNotExistException(f"Assessment {assessment_id} does not exist")
        del self.ad_assessments[assessment_id]

    def enable_directory_data_access(self, directory_id: str) -> None:
        """Enable directory data access for a directory."""
        self._validate_directory_id(directory_id)

    def disable_directory_data_access(self, directory_id: str) -> None:
        """Disable directory data access for a directory."""
        self._validate_directory_id(directory_id)

    def describe_directory_data_access(self, directory_id: str) -> dict[str, Any]:
        """Describe directory data access status."""
        self._validate_directory_id(directory_id)
        return {"DirectoryId": directory_id, "DataAccessStatus": "Disabled"}

    def enable_ca_enrollment_policy(self, directory_id: str) -> None:
        """Enable CA enrollment policy for a directory."""
        self._validate_directory_id(directory_id)

    def disable_ca_enrollment_policy(self, directory_id: str) -> None:
        """Disable CA enrollment policy for a directory."""
        self._validate_directory_id(directory_id)

    def add_region(
        self,
        directory_id: str,
        region_name: str,
        vpc_settings: dict[str, Any],
    ) -> None:
        """Add a region to a directory — stub."""
        self._validate_directory_id(directory_id)

    def remove_region(self, directory_id: str) -> None:
        """Remove a region from a directory — stub."""
        self._validate_directory_id(directory_id)

    def update_directory_setup(
        self,
        directory_id: str,
        update_type: str,
        os_update_settings: Optional[dict[str, Any]] = None,
        create_snapshot_before_update: bool = False,
    ) -> None:
        """Update directory setup — stub."""
        self._validate_directory_id(directory_id)

    def update_number_of_domain_controllers(
        self, directory_id: str, desired_number: int
    ) -> None:
        """Update number of domain controllers — stub."""
        self._validate_directory_id(directory_id)

    def share_directory(
        self,
        directory_id: str,
        share_target: dict[str, Any],
        share_method: str,
        share_notes: Optional[str] = None,
    ) -> str:
        """Share a directory — stub returns a synthetic shared directory ID."""
        self._validate_directory_id(directory_id)
        import uuid

        return str(uuid.uuid4())

    def unshare_directory(
        self,
        directory_id: str,
        unshare_target: dict[str, Any],
    ) -> str:
        """Unshare a directory — stub."""
        self._validate_directory_id(directory_id)
        import uuid

        return str(uuid.uuid4())


ds_backends = BackendDict(DirectoryServiceBackend, service_name="ds")
