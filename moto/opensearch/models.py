import datetime
import uuid
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .data import (
    compatible_versions,
    elasticsearch_instance_types,
    elasticsearch_versions,
    opensearch_instance_types,
    opensearch_versions,
    reserved_instance_offerings,
)
from .exceptions import (
    EngineTypeNotFoundException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
)

default_cluster_config = {
    "InstanceType": "t3.small.search",
    "InstanceCount": 1,
    "DedicatedMasterEnabled": False,
    "ZoneAwarenessEnabled": False,
    "WarmEnabled": False,
    "ColdStorageOptions": {"Enabled": False},
}
default_advanced_security_options = {
    "Enabled": False,
    "InternalUserDatabaseEnabled": False,
    "AnonymousAuthEnabled": False,
}
default_domain_endpoint_options = {
    "EnforceHTTPS": False,
    "TLSSecurityPolicy": "Policy-Min-TLS-1-0-2019-07",
    "CustomEndpointEnabled": False,
}
default_software_update_options = {
    "CurrentVersion": "",
    "NewVersion": "",
    "UpdateAvailable": False,
    "Cancellable": False,
    "UpdateStatus": "COMPLETED",
    "Description": "There is no software update available for this domain.",
    "AutomatedUpdateDate": "1969-12-31T23:00:00-01:00",
    "OptionalDeployment": True,
}
default_advanced_options = {
    "override_main_response_version": "false",
    "rest.action.multi.allow_explicit_index": "true",
}


class EngineVersion(BaseModel):
    def __init__(self, options: str, create_time: datetime.datetime) -> None:
        self.options = options or "OpenSearch_2.5"
        self.create_time = unix_time(create_time)
        self.update_time = self.create_time

    def to_dict(self) -> dict[str, Any]:
        return {
            "Options": self.options,
            "Status": {
                "CreationDate": self.create_time,
                "PendingDeletion": False,
                "State": "Active",
                "UpdateDate": self.update_time,
                "UpdateVersion": 28,
            },
        }


class OpenSearchPackage(BaseModel):
    def __init__(
        self,
        package_name: str,
        package_type: str,
        package_description: str,
        package_source: dict[str, str],
        account_id: str,
        region: str,
    ) -> None:
        self.package_id = f"pkg-{uuid.uuid4().hex[:12]}"
        self.package_name = package_name
        self.package_type = package_type
        self.package_description = package_description
        self.package_source = package_source
        self.created_at = unix_time(datetime.datetime.now())
        self.last_updated_at = self.created_at
        self.status = "AVAILABLE"
        self.error_details: dict[str, str] = {}
        self.associated_domains: dict[str, str] = {}  # domain_name -> status
        self.available_package_version = "1"
        self.arn = f"arn:{get_partition(region)}:es:{region}:{account_id}:package/{self.package_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "PackageID": self.package_id,
            "PackageName": self.package_name,
            "PackageType": self.package_type,
            "PackageDescription": self.package_description,
            "PackageStatus": self.status,
            "CreatedAt": self.created_at,
            "LastUpdatedAt": self.last_updated_at,
            "AvailablePackageVersion": self.available_package_version,
            "ErrorDetails": self.error_details,
        }

    def to_domain_package_dict(self, domain_name: str) -> dict[str, Any]:
        return {
            "PackageID": self.package_id,
            "PackageName": self.package_name,
            "PackageType": self.package_type,
            "DomainName": domain_name,
            "DomainPackageStatus": self.associated_domains.get(domain_name, "ACTIVE"),
            "PackageVersion": self.available_package_version,
            "LastUpdated": self.last_updated_at,
        }


class VpcEndpointModel(BaseModel):
    def __init__(
        self,
        domain_arn: str,
        vpc_options: dict[str, Any],
        account_id: str,
        region: str,
    ) -> None:
        self.vpc_endpoint_id = f"aos-{uuid.uuid4().hex[:17]}"
        self.domain_arn = domain_arn
        self.vpc_options = vpc_options or {}
        self.status = "ACTIVE"
        self.endpoint = f"vpc-{self.vpc_endpoint_id}.{region}.es.amazonaws.com"
        self.arn = (
            f"arn:{get_partition(region)}:es:{region}:{account_id}"
            f":vpc-endpoint/{self.vpc_endpoint_id}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "VpcEndpointId": self.vpc_endpoint_id,
            "VpcEndpointOwner": "",
            "DomainArn": self.domain_arn,
            "VpcOptions": self.vpc_options,
            "Status": self.status,
            "Endpoint": self.endpoint,
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "VpcEndpointId": self.vpc_endpoint_id,
            "VpcEndpointOwner": "",
            "DomainArn": self.domain_arn,
            "Status": self.status,
        }


class OutboundConnection(BaseModel):
    def __init__(
        self,
        local_domain_info: dict[str, Any],
        remote_domain_info: dict[str, Any],
        connection_alias: str,
        connection_mode: str,
    ) -> None:
        self.connection_id = str(uuid.uuid4())
        self.local_domain_info = local_domain_info
        self.remote_domain_info = remote_domain_info
        self.connection_alias = connection_alias
        self.connection_mode = connection_mode or "DIRECT"
        self.status = {
            "StatusCode": "ACTIVE",
            "Message": "Connection is active",
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "ConnectionId": self.connection_id,
            "LocalDomainInfo": self.local_domain_info,
            "RemoteDomainInfo": self.remote_domain_info,
            "ConnectionAlias": self.connection_alias,
            "ConnectionMode": self.connection_mode,
            "ConnectionStatus": self.status,
        }


class InboundConnection(BaseModel):
    def __init__(
        self,
        connection_id: str,
        local_domain_info: dict[str, Any],
        remote_domain_info: dict[str, Any],
    ) -> None:
        self.connection_id = connection_id
        self.local_domain_info = local_domain_info
        self.remote_domain_info = remote_domain_info
        self.status = {
            "StatusCode": "PENDING_ACCEPTANCE",
            "Message": "Pending acceptance by destination domain owner",
        }

    def accept(self) -> None:
        self.status = {
            "StatusCode": "ACTIVE",
            "Message": "Connection is active",
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "ConnectionId": self.connection_id,
            "LocalDomainInfo": self.local_domain_info,
            "RemoteDomainInfo": self.remote_domain_info,
            "ConnectionStatus": self.status,
        }


class ReservedInstance(BaseModel):
    def __init__(
        self,
        reserved_instance_offering_id: str,
        reservation_name: str,
        instance_count: int,
        offering: dict[str, Any],
    ) -> None:
        self.reserved_instance_id = str(uuid.uuid4())
        self.reserved_instance_offering_id = reserved_instance_offering_id
        self.reservation_name = reservation_name
        self.instance_count = instance_count
        self.instance_type = offering["InstanceType"]
        self.duration = offering["Duration"]
        self.fixed_price = offering["FixedPrice"]
        self.usage_price = offering["UsagePrice"]
        self.currency_code = offering["CurrencyCode"]
        self.payment_option = offering["PaymentOption"]
        self.recurring_charges = offering.get("RecurringCharges", [])
        self.state = "active"
        self.start_time = unix_time(datetime.datetime.now())
        self.billing_subscription_id = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ReservedInstanceId": self.reserved_instance_id,
            "ReservedInstanceOfferingId": self.reserved_instance_offering_id,
            "ReservationName": self.reservation_name,
            "InstanceType": self.instance_type,
            "InstanceCount": self.instance_count,
            "Duration": self.duration,
            "FixedPrice": self.fixed_price,
            "UsagePrice": self.usage_price,
            "CurrencyCode": self.currency_code,
            "PaymentOption": self.payment_option,
            "RecurringCharges": self.recurring_charges,
            "State": self.state,
            "StartTime": self.start_time,
            "BillingSubscriptionId": self.billing_subscription_id,
        }


class OpenSearchDomain(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        domain_name: str,
        engine_version: str,
        cluster_config: dict[str, Any],
        ebs_options: dict[str, Any],
        access_policies: str,
        snapshot_options: dict[str, int],
        vpc_options: dict[str, list[str]],
        cognito_options: dict[str, Any],
        encryption_at_rest_options: dict[str, Any],
        node_to_node_encryption_options: dict[str, bool],
        advanced_options: dict[str, str],
        log_publishing_options: dict[str, Any],
        domain_endpoint_options: dict[str, Any],
        advanced_security_options: dict[str, Any],
        auto_tune_options: dict[str, Any],
        off_peak_window_options: dict[str, Any],
        software_update_options: dict[str, bool],
        is_es: bool,
        elasticsearch_version: Optional[str],
        elasticsearch_cluster_config: Optional[str],
    ):
        # Add creation_date attribute
        self.creation_date = unix_time(datetime.datetime.now())

        self.domain_id = f"{account_id}/{domain_name}"
        self.domain_name = domain_name
        self.arn = (
            f"arn:{get_partition(region)}:es:{region}:{account_id}:domain/{domain_name}"
        )
        self.engine_version = EngineVersion(engine_version, datetime.datetime.now())
        self.cluster_config = cluster_config or {}
        self.ebs_options = ebs_options or {"EBSEnabled": False}
        self.access_policies = access_policies or ""
        self.snapshot_options = snapshot_options or {"AutomatedSnapshotStartHour": 0}
        self.vpc_options = vpc_options
        self.cognito_options = cognito_options or {"Enabled": False}
        self.encryption_at_rest_options = encryption_at_rest_options or {
            "Enabled": False
        }
        self.node_to_node_encryption_options = node_to_node_encryption_options or {
            "Enabled": False
        }
        self.advanced_options = advanced_options or default_advanced_options
        self.log_publishing_options = log_publishing_options
        self.domain_endpoint_options = (
            domain_endpoint_options or default_domain_endpoint_options
        )
        self.advanced_security_options = (
            advanced_security_options or default_advanced_security_options
        )
        self.auto_tune_options = auto_tune_options or {"State": "ENABLE_IN_PROGRESS"}
        if not self.auto_tune_options.get("State"):
            self.auto_tune_options["State"] = "ENABLED"
        # Rename to singular everywhere
        self.off_peak_window_options = off_peak_window_options
        self.software_update_options = (
            software_update_options or default_software_update_options
        )
        self.engine_type = (
            "Elasticsearch"
            if is_es or engine_version.startswith("Elasticsearch_")
            else "OpenSearch"
        )
        self.is_es = is_es
        self.elasticsearch_version = elasticsearch_version
        self.elasticsearch_cluster_config = elasticsearch_cluster_config

        self.deleted = False
        self.processing = False
        self.associated_packages: dict[str, str] = {}  # package_id -> status

        # Defaults
        for key, value in default_cluster_config.items():
            if key not in self.cluster_config:
                self.cluster_config[key] = value

        if self.vpc_options is None:
            self.endpoint: Optional[str] = f"{domain_name}.{region}.es.amazonaws.com"
            self.endpoints: Optional[dict[str, str]] = None
        else:
            self.endpoint = None
            self.endpoints = {"vpc": f"{domain_name}.{region}.es.amazonaws.com"}

    def delete(self) -> None:
        self.deleted = True
        self.processing = True

    def dct_options(self) -> dict[str, Any]:
        return {
            "Endpoint": self.endpoint,
            "Endpoints": self.endpoints,
            "ClusterConfig": self.cluster_config,
            "EBSOptions": self.ebs_options,
            "AccessPolicies": self.access_policies,
            "SnapshotOptions": self.snapshot_options,
            "VPCOptions": self.vpc_options,
            "CognitoOptions": self.cognito_options,
            "EncryptionAtRestOptions": self.encryption_at_rest_options,
            "NodeToNodeEncryptionOptions": self.node_to_node_encryption_options,
            "AdvancedOptions": self.advanced_options,
            "LogPublishingOptions": self.log_publishing_options,
            "DomainEndpointOptions": self.domain_endpoint_options,
            "AdvancedSecurityOptions": self.advanced_security_options,
            "AutoTuneOptions": self.auto_tune_options,
            # Use singular key and attribute
            "OffPeakWindowOptions": self.off_peak_window_options,
            "SoftwareUpdateOptions": self.software_update_options,
            "ElasticsearchVersion": self.elasticsearch_version,
            "ElasticsearchClusterConfig": self.elasticsearch_cluster_config,
        }

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "DomainId": self.domain_id,
            "DomainName": self.domain_name,
            "ARN": self.arn,
            "Created": True,
            "Deleted": self.deleted,
            "EngineVersion": self.engine_version.options,
            "Processing": self.processing,
            "UpgradeProcessing": False,
        }
        for key, value in self.dct_options().items():
            if value is not None:
                dct[key] = value
        return dct

    def _status_block(self) -> dict[str, Any]:
        return {
            "State": "Active",
            "CreationDate": self.creation_date,
            "UpdateDate": self.creation_date,
            "UpdateVersion": 1,
            "PendingDeletion": False,
        }

    def _wrap(self, options: Any) -> dict[str, Any]:
        # Most DomainConfig sections only need {"Options": ...}
        return {"Options": options}

    def to_config_dict(self) -> dict[str, Any]:
        cfg: dict[str, Any] = {}

        # Cluster config section (key differs for ES vs OS)
        cluster_key = "ElasticsearchClusterConfig" if self.is_es else "ClusterConfig"
        cluster_opts = (
            self.elasticsearch_cluster_config
            if (self.is_es and self.elasticsearch_cluster_config)
            else (self.cluster_config or default_cluster_config)
        )
        cfg[cluster_key] = self._wrap(cluster_opts)

        # Version section:
        # - OpenSearch expects Status for EngineVersion (use EngineVersion.to_dict()).
        # - ES expects only Options for ElasticsearchVersion.
        if self.is_es:
            cfg["ElasticsearchVersion"] = self._wrap(
                self.elasticsearch_version or self.engine_version.options
            )
        else:
            cfg["EngineVersion"] = self.engine_version.to_dict()

        # EBSOptions: default to minimal disabled if not provided
        ebs_opts = (
            self.ebs_options if self.ebs_options is not None else {"EBSEnabled": False}
        )
        cfg["EBSOptions"] = self._wrap(ebs_opts)

        # Node-to-node encryption: default minimal
        n2n_opts = (
            self.node_to_node_encryption_options
            if self.node_to_node_encryption_options is not None
            else {"Enabled": False}
        )
        cfg["NodeToNodeEncryptionOptions"] = self._wrap(n2n_opts)

        # Encryption at rest: default minimal
        ear_opts = (
            self.encryption_at_rest_options
            if self.encryption_at_rest_options is not None
            else {"Enabled": False}
        )
        cfg["EncryptionAtRestOptions"] = self._wrap(ear_opts)

        # Access policies: default empty string
        cfg["AccessPolicies"] = self._wrap(self.access_policies or "")

        # Optional passthrough sections
        if self.snapshot_options is not None:
            cfg["SnapshotOptions"] = self._wrap(self.snapshot_options)
        if self.vpc_options is not None:
            cfg["VPCOptions"] = self._wrap(self.vpc_options)
        if self.cognito_options is not None:
            cfg["CognitoOptions"] = self._wrap(self.cognito_options)
        if self.log_publishing_options is not None:
            cfg["LogPublishingOptions"] = self._wrap(self.log_publishing_options)
        if self.auto_tune_options is not None:
            cfg["AutoTuneOptions"] = self._wrap(self.auto_tune_options)
        if self.off_peak_window_options is not None:
            cfg["OffPeakWindowOptions"] = self._wrap(self.off_peak_window_options)

        # Always include with sensible defaults
        cfg["AdvancedOptions"] = self._wrap(
            self.advanced_options or default_advanced_options
        )
        cfg["DomainEndpointOptions"] = self._wrap(
            self.domain_endpoint_options or default_domain_endpoint_options
        )
        cfg["AdvancedSecurityOptions"] = self._wrap(
            self.advanced_security_options or default_advanced_security_options
        )
        cfg["SoftwareUpdateOptions"] = self._wrap(
            self.software_update_options or default_software_update_options
        )

        return cfg

    def update(
        self,
        cluster_config: dict[str, Any],
        ebs_options: dict[str, Any],
        access_policies: str,
        snapshot_options: dict[str, int],
        vpc_options: dict[str, list[str]],
        cognito_options: dict[str, Any],
        encryption_at_rest_options: dict[str, Any],
        node_to_node_encryption_options: dict[str, bool],
        advanced_options: dict[str, str],
        log_publishing_options: dict[str, Any],
        domain_endpoint_options: dict[str, Any],
        advanced_security_options: dict[str, Any],
        auto_tune_options: dict[str, Any],
        off_peak_window_options: dict[str, Any],
        software_update_options: dict[str, bool],
    ) -> None:
        self.cluster_config = cluster_config or self.cluster_config
        self.ebs_options = ebs_options or self.ebs_options
        self.access_policies = access_policies or self.access_policies
        self.snapshot_options = snapshot_options or self.snapshot_options
        self.vpc_options = vpc_options or self.vpc_options
        self.cognito_options = cognito_options or self.cognito_options
        self.encryption_at_rest_options = (
            encryption_at_rest_options or self.encryption_at_rest_options
        )
        self.node_to_node_encryption_options = (
            node_to_node_encryption_options or self.node_to_node_encryption_options
        )
        self.advanced_options = advanced_options or self.advanced_options
        self.log_publishing_options = (
            log_publishing_options or self.log_publishing_options
        )
        self.domain_endpoint_options = (
            domain_endpoint_options or self.domain_endpoint_options
        )
        self.advanced_security_options = (
            advanced_security_options or self.advanced_security_options
        )
        self.auto_tune_options = auto_tune_options or self.auto_tune_options
        # Fix attribute name (singular)
        self.off_peak_window_options = (
            off_peak_window_options or self.off_peak_window_options
        )
        self.software_update_options = (
            software_update_options or self.software_update_options
        )
        self.engine_version.update_time = unix_time(datetime.datetime.now())


class OpenSearchServiceBackend(BaseBackend):
    """Implementation of OpenSearchService APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.domains: dict[str, OpenSearchDomain] = {}
        self.tagger = TaggingService()
        self.packages: dict[str, OpenSearchPackage] = {}
        self.vpc_endpoints: dict[str, VpcEndpointModel] = {}
        self.outbound_connections: dict[str, OutboundConnection] = {}
        self.inbound_connections: dict[str, InboundConnection] = {}
        self.reserved_instances: dict[str, ReservedInstance] = {}
        self.applications: dict[str, dict[str, Any]] = {}
        self.direct_query_data_sources: dict[str, dict[str, Any]] = {}
        self.data_sources: dict[tuple[str, str], dict[str, Any]] = {}
        self.scheduled_actions: dict[str, dict[str, Any]] = {}
        self.domain_maintenances: dict[str, list[dict[str, Any]]] = {}
        self.vpc_endpoint_access: dict[str, list[dict[str, Any]]] = {}

    def create_domain(
        self,
        domain_name: str,
        engine_version: str,
        cluster_config: dict[str, Any],
        ebs_options: dict[str, Any],
        access_policies: str,
        snapshot_options: dict[str, Any],
        vpc_options: dict[str, Any],
        cognito_options: dict[str, Any],
        encryption_at_rest_options: dict[str, Any],
        node_to_node_encryption_options: dict[str, Any],
        advanced_options: dict[str, Any],
        log_publishing_options: dict[str, Any],
        domain_endpoint_options: dict[str, Any],
        advanced_security_options: dict[str, Any],
        tag_list: list[dict[str, str]],
        auto_tune_options: dict[str, Any],
        off_peak_window_options: dict[str, Any],
        software_update_options: dict[str, Any],
        is_es: bool,
        elasticsearch_version: Optional[str],
        elasticsearch_cluster_config: Optional[str],
    ) -> OpenSearchDomain:
        if domain_name in self.domains:
            raise ResourceAlreadyExistsException(domain_name)
        domain = OpenSearchDomain(
            account_id=self.account_id,
            region=self.region_name,
            domain_name=domain_name,
            engine_version=engine_version,
            cluster_config=cluster_config,
            ebs_options=ebs_options,
            access_policies=access_policies,
            snapshot_options=snapshot_options,
            vpc_options=vpc_options,
            cognito_options=cognito_options,
            encryption_at_rest_options=encryption_at_rest_options,
            node_to_node_encryption_options=node_to_node_encryption_options,
            advanced_options=advanced_options,
            log_publishing_options=log_publishing_options,
            domain_endpoint_options=domain_endpoint_options,
            advanced_security_options=advanced_security_options,
            auto_tune_options=auto_tune_options,
            off_peak_window_options=off_peak_window_options,
            software_update_options=software_update_options,
            is_es=is_es,
            elasticsearch_version=elasticsearch_version,
            elasticsearch_cluster_config=elasticsearch_cluster_config,
        )
        self.domains[domain_name] = domain
        if tag_list:
            self.add_tags(domain.arn, tag_list)
        return domain

    def get_compatible_versions(
        self, domain_name: Optional[str]
    ) -> list[dict[str, Any]]:
        if domain_name and domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        return compatible_versions

    def delete_domain(self, domain_name: str) -> OpenSearchDomain:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        self.domains[domain_name].delete()
        return self.domains.pop(domain_name)

    def describe_domain(self, domain_name: str) -> OpenSearchDomain:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        return self.domains[domain_name]

    def describe_domain_config(self, domain_name: str) -> dict[str, Any]:
        domain = self.describe_domain(domain_name)
        return domain.to_config_dict()

    def update_domain_config(
        self,
        domain_name: str,
        cluster_config: dict[str, Any],
        ebs_options: dict[str, Any],
        access_policies: str,
        snapshot_options: dict[str, Any],
        vpc_options: dict[str, Any],
        cognito_options: dict[str, Any],
        encryption_at_rest_options: dict[str, Any],
        node_to_node_encryption_options: dict[str, Any],
        advanced_options: dict[str, Any],
        log_publishing_options: dict[str, Any],
        domain_endpoint_options: dict[str, Any],
        advanced_security_options: dict[str, Any],
        auto_tune_options: dict[str, Any],
        off_peak_window_options: dict[str, Any],
        software_update_options: dict[str, Any],
    ) -> "OpenSearchDomain":
        domain = self.describe_domain(domain_name)
        domain.cluster_config = cluster_config or domain.cluster_config
        domain.ebs_options = ebs_options or domain.ebs_options
        domain.access_policies = access_policies or domain.access_policies
        domain.snapshot_options = snapshot_options or domain.snapshot_options
        domain.vpc_options = vpc_options or domain.vpc_options
        domain.cognito_options = cognito_options or domain.cognito_options
        domain.encryption_at_rest_options = (
            encryption_at_rest_options or domain.encryption_at_rest_options
        )
        domain.node_to_node_encryption_options = (
            node_to_node_encryption_options or domain.node_to_node_encryption_options
        )
        domain.advanced_options = advanced_options or domain.advanced_options
        domain.log_publishing_options = (
            log_publishing_options or domain.log_publishing_options
        )
        domain.domain_endpoint_options = (
            domain_endpoint_options or domain.domain_endpoint_options
        )
        domain.advanced_security_options = (
            advanced_security_options or domain.advanced_security_options
        )
        domain.auto_tune_options = auto_tune_options or domain.auto_tune_options
        # Fix attribute name (singular)
        domain.off_peak_window_options = (
            off_peak_window_options or domain.off_peak_window_options
        )
        domain.software_update_options = (
            software_update_options or domain.software_update_options
        )
        return domain

    def add_tags(self, arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(arn, tags)

    def list_tags(self, arn: str) -> list[dict[str, str]]:
        return self.tagger.list_tags_for_resource(arn)["Tags"]

    def remove_tags(self, arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(arn, tag_keys)

    def list_domain_names(self, engine_type: str) -> list[dict[str, str]]:
        domains = []
        if engine_type and engine_type not in ["Elasticsearch", "OpenSearch"]:
            raise EngineTypeNotFoundException(engine_type)
        for domain in self.domains.values():
            if engine_type:
                if engine_type == domain.engine_type:
                    domains.append(
                        {"DomainName": domain.domain_name, "EngineType": engine_type}
                    )
            else:
                domains.append(
                    {"DomainName": domain.domain_name, "EngineType": domain.engine_type}
                )
        return domains

    def describe_domains(self, domain_names: list[str]) -> list[OpenSearchDomain]:
        queried_domains = []
        for domain_name in domain_names:
            if domain_name in self.domains:
                queried_domains.append(self.domains[domain_name])
        return queried_domains

    # ---- Packages ----

    def create_package(
        self,
        package_name: str,
        package_type: str,
        package_description: str,
        package_source: dict[str, str],
    ) -> OpenSearchPackage:
        pkg = OpenSearchPackage(
            package_name=package_name,
            package_type=package_type,
            package_description=package_description,
            package_source=package_source,
            account_id=self.account_id,
            region=self.region_name,
        )
        self.packages[pkg.package_id] = pkg
        return pkg

    def describe_packages(
        self, filters: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        results = list(self.packages.values())
        if filters:
            for f in filters:
                name = f.get("Name", "")
                values = f.get("Value", [])
                if name == "PackageID" and values:
                    results = [p for p in results if p.package_id in values]
                elif name == "PackageName" and values:
                    results = [p for p in results if p.package_name in values]
                elif name == "PackageType" and values:
                    results = [p for p in results if p.package_type in values]
                elif name == "PackageStatus" and values:
                    results = [p for p in results if p.status in values]
        return [p.to_dict() for p in results]

    def delete_package(self, package_id: str) -> dict[str, Any]:
        if package_id not in self.packages:
            raise ResourceNotFoundException(package_id)
        pkg = self.packages.pop(package_id)
        pkg.status = "DELETING"
        return pkg.to_dict()

    def update_package(
        self,
        package_id: str,
        package_source: dict[str, str],
        package_description: Optional[str],
        commit_message: Optional[str],
    ) -> dict[str, Any]:
        if package_id not in self.packages:
            raise ResourceNotFoundException(package_id)
        pkg = self.packages[package_id]
        pkg.package_source = package_source
        if package_description is not None:
            pkg.package_description = package_description
        pkg.last_updated_at = unix_time(datetime.datetime.now())
        return pkg.to_dict()

    def associate_package(self, package_id: str, domain_name: str) -> dict[str, Any]:
        if package_id not in self.packages:
            raise ResourceNotFoundException(package_id)
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        pkg = self.packages[package_id]
        pkg.associated_domains[domain_name] = "ACTIVE"
        self.domains[domain_name].associated_packages[package_id] = "ACTIVE"
        return pkg.to_domain_package_dict(domain_name)

    def dissociate_package(self, package_id: str, domain_name: str) -> dict[str, Any]:
        if package_id not in self.packages:
            raise ResourceNotFoundException(package_id)
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        pkg = self.packages[package_id]
        pkg.associated_domains.pop(domain_name, None)
        self.domains[domain_name].associated_packages.pop(package_id, None)
        result = pkg.to_domain_package_dict(domain_name)
        result["DomainPackageStatus"] = "DISSOCIATING"
        return result

    def list_packages_for_domain(self, domain_name: str) -> list[dict[str, Any]]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        domain = self.domains[domain_name]
        results = []
        for pkg_id in domain.associated_packages:
            if pkg_id in self.packages:
                results.append(
                    self.packages[pkg_id].to_domain_package_dict(domain_name)
                )
        return results

    def list_domains_for_package(self, package_id: str) -> list[dict[str, Any]]:
        if package_id not in self.packages:
            raise ResourceNotFoundException(package_id)
        pkg = self.packages[package_id]
        results = []
        for dname in pkg.associated_domains:
            results.append(pkg.to_domain_package_dict(dname))
        return results

    def get_package_version_history(self, package_id: str) -> list[dict[str, Any]]:
        if package_id not in self.packages:
            raise ResourceNotFoundException(package_id)
        pkg = self.packages[package_id]
        return [
            {
                "PackageVersion": pkg.available_package_version,
                "CreatedAt": pkg.created_at,
                "CommitMessage": "Initial version",
            }
        ]

    # ---- VPC Endpoints ----

    def create_vpc_endpoint(
        self, domain_arn: str, vpc_options: dict[str, Any]
    ) -> VpcEndpointModel:
        ep = VpcEndpointModel(
            domain_arn=domain_arn,
            vpc_options=vpc_options,
            account_id=self.account_id,
            region=self.region_name,
        )
        self.vpc_endpoints[ep.vpc_endpoint_id] = ep
        return ep

    def describe_vpc_endpoints(
        self, vpc_endpoint_ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        endpoints: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        for eid in vpc_endpoint_ids or []:
            if eid in self.vpc_endpoints:
                endpoints.append(self.vpc_endpoints[eid].to_dict())
            else:
                errors.append(
                    {
                        "VpcEndpointId": eid,
                        "ErrorCode": "ENDPOINT_NOT_FOUND",
                        "ErrorMessage": f"VPC Endpoint {eid} not found",
                    }
                )
        return endpoints, errors

    def update_vpc_endpoint(
        self, vpc_endpoint_id: str, vpc_options: dict[str, Any]
    ) -> VpcEndpointModel:
        if vpc_endpoint_id not in self.vpc_endpoints:
            raise ResourceNotFoundException(vpc_endpoint_id)
        ep = self.vpc_endpoints[vpc_endpoint_id]
        ep.vpc_options = vpc_options
        return ep

    def delete_vpc_endpoint(self, vpc_endpoint_id: str) -> dict[str, Any]:
        if vpc_endpoint_id not in self.vpc_endpoints:
            raise ResourceNotFoundException(vpc_endpoint_id)
        ep = self.vpc_endpoints.pop(vpc_endpoint_id)
        return {
            "VpcEndpointId": ep.vpc_endpoint_id,
            "VpcEndpointOwner": "",
            "DomainArn": ep.domain_arn,
            "Status": "DELETING",
        }

    def list_vpc_endpoints(self) -> list[dict[str, Any]]:
        return [ep.to_summary() for ep in self.vpc_endpoints.values()]

    def list_vpc_endpoints_for_domain(self, domain_name: str) -> list[dict[str, Any]]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        domain_arn = self.domains[domain_name].arn
        return [
            ep.to_summary()
            for ep in self.vpc_endpoints.values()
            if ep.domain_arn == domain_arn
        ]

    # ---- Connections ----

    def create_outbound_connection(
        self,
        local_domain_info: dict[str, Any],
        remote_domain_info: dict[str, Any],
        connection_alias: str,
        connection_mode: str,
    ) -> OutboundConnection:
        conn = OutboundConnection(
            local_domain_info=local_domain_info,
            remote_domain_info=remote_domain_info,
            connection_alias=connection_alias,
            connection_mode=connection_mode,
        )
        self.outbound_connections[conn.connection_id] = conn
        # Create a matching inbound connection
        inbound = InboundConnection(
            connection_id=conn.connection_id,
            local_domain_info=remote_domain_info,
            remote_domain_info=local_domain_info,
        )
        self.inbound_connections[conn.connection_id] = inbound
        return conn

    def describe_outbound_connections(
        self, filters: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        return [c.to_dict() for c in self.outbound_connections.values()]

    def delete_outbound_connection(self, connection_id: str) -> dict[str, Any]:
        if connection_id not in self.outbound_connections:
            raise ResourceNotFoundException(connection_id)
        conn = self.outbound_connections.pop(connection_id)
        conn.status = {
            "StatusCode": "DELETED",
            "Message": "Connection has been deleted",
        }
        return conn.to_dict()

    def accept_inbound_connection(self, connection_id: str) -> dict[str, Any]:
        if connection_id not in self.inbound_connections:
            raise ResourceNotFoundException(connection_id)
        conn = self.inbound_connections[connection_id]
        conn.accept()
        return conn.to_dict()

    def describe_inbound_connections(
        self, filters: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        return [c.to_dict() for c in self.inbound_connections.values()]

    def delete_inbound_connection(self, connection_id: str) -> dict[str, Any]:
        if connection_id not in self.inbound_connections:
            raise ResourceNotFoundException(connection_id)
        conn = self.inbound_connections.pop(connection_id)
        conn.status = {
            "StatusCode": "DELETED",
            "Message": "Connection has been deleted",
        }
        return conn.to_dict()

    # ---- Reserved Instances ----

    def describe_reserved_instance_offerings(
        self,
    ) -> list[dict[str, Any]]:
        return reserved_instance_offerings

    def purchase_reserved_instance_offering(
        self,
        reserved_instance_offering_id: str,
        reservation_name: str,
        instance_count: int,
    ) -> dict[str, Any]:
        offering = None
        for o in reserved_instance_offerings:
            if o["ReservedInstanceOfferingId"] == reserved_instance_offering_id:
                offering = o
                break
        if offering is None:
            raise ResourceNotFoundException(reserved_instance_offering_id)
        ri = ReservedInstance(
            reserved_instance_offering_id=reserved_instance_offering_id,
            reservation_name=reservation_name,
            instance_count=instance_count or 1,
            offering=offering,
        )
        self.reserved_instances[ri.reserved_instance_id] = ri
        return {
            "ReservedInstanceId": ri.reserved_instance_id,
            "ReservationName": ri.reservation_name,
        }

    def describe_reserved_instances(self) -> list[dict[str, Any]]:
        return [ri.to_dict() for ri in self.reserved_instances.values()]

    # ---- Versions ----

    def list_versions(self) -> list[str]:
        return opensearch_versions + elasticsearch_versions

    def list_elasticsearch_versions(self) -> list[str]:
        return elasticsearch_versions

    # ---- Instance Types ----

    def list_instance_type_details(self, engine_version: str) -> list[dict[str, Any]]:
        return opensearch_instance_types

    def list_elasticsearch_instance_types(
        self, elasticsearch_version: str
    ) -> list[str]:
        return elasticsearch_instance_types

    # ---- Domain sub-resource operations ----

    def describe_domain_auto_tunes(self, domain_name: str) -> list[dict[str, Any]]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        return []

    def describe_domain_change_progress(
        self, domain_name: str
    ) -> Optional[dict[str, Any]]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        return {
            "ChangeProgressStatus": {
                "ChangeId": "change-id-placeholder",
                "StartTime": unix_time(datetime.datetime.now()),
                "Status": "COMPLETED",
                "PendingProperties": [],
                "CompletedProperties": [],
                "TotalNumberOfStages": 1,
                "ChangeProgressStages": [
                    {
                        "Name": "Update",
                        "Status": "COMPLETED",
                        "Description": "Completed",
                    }
                ],
                "ConfigChangeStatus": "Completed",
                "LastUpdatedTime": unix_time(datetime.datetime.now()),
                "InitiatedBy": "CUSTOMER",
            }
        }

    def describe_domain_health(self, domain_name: str) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        domain = self.domains[domain_name]
        instance_count = domain.cluster_config.get("InstanceCount", 1)
        return {
            "DomainState": "Active",
            "AvailabilityZoneCount": "1",
            "ActiveAvailabilityZoneCount": "1",
            "StandByAvailabilityZoneCount": "0",
            "DataNodeCount": str(instance_count),
            "DedicatedMaster": domain.cluster_config.get(
                "DedicatedMasterEnabled", False
            ),
            "MasterEligibleNodeCount": "0",
            "WarmNodeCount": "0",
            "MasterNode": None,
            "ClusterHealth": "Green",
            "TotalShards": "1",
            "TotalUnAssignedShards": "0",
            "EnvironmentInformation": [],
        }

    def describe_domain_nodes(self, domain_name: str) -> list[dict[str, Any]]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        domain = self.domains[domain_name]
        instance_count = domain.cluster_config.get("InstanceCount", 1)
        instance_type = domain.cluster_config.get("InstanceType", "t3.small.search")
        nodes = []
        for i in range(instance_count):
            nodes.append(
                {
                    "NodeId": f"node-{i}",
                    "NodeType": "Data",
                    "AvailabilityZone": f"{self.region_name}a",
                    "InstanceType": instance_type,
                    "NodeStatus": "Active",
                    "StorageType": "EBS",
                    "StorageVolumeType": "gp2",
                    "StorageSize": "10",
                }
            )
        return nodes

    def describe_dry_run_progress(self, domain_name: str) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        return {
            "DryRunProgressStatus": {
                "DryRunId": "dry-run-id-placeholder",
                "DryRunStatus": "SUCCEEDED",
                "CreationDate": str(unix_time(datetime.datetime.now())),
                "UpdateDate": str(unix_time(datetime.datetime.now())),
                "ValidationFailures": [],
            },
            "DryRunConfig": self.domains[domain_name].to_dict(),
            "DryRunResults": {
                "DeploymentType": "Blue/Green",
                "Message": "This change will cause a Blue/Green deployment.",
            },
        }

    def describe_instance_type_limits(
        self, instance_type: str, engine_version: str
    ) -> dict[str, Any]:
        return {
            "LimitsByRole": {
                "data": {
                    "StorageTypes": [
                        {
                            "StorageTypeName": "ebs",
                            "StorageSubTypeName": "gp2",
                            "StorageTypeLimits": [
                                {
                                    "LimitName": "MinimumVolumeSize",
                                    "LimitValues": ["10"],
                                },
                                {
                                    "LimitName": "MaximumVolumeSize",
                                    "LimitValues": ["16384"],
                                },
                            ],
                        }
                    ],
                    "InstanceLimits": {
                        "InstanceCountLimits": {
                            "MinimumInstanceCount": 1,
                            "MaximumInstanceCount": 80,
                        }
                    },
                    "AdditionalLimits": [
                        {
                            "LimitName": "MaximumNumberOfDataNodesSupported",
                            "LimitValues": ["80"],
                        },
                        {
                            "LimitName": "MaximumNumberOfDataNodesWithoutMasterNode",
                            "LimitValues": ["10"],
                        },
                    ],
                }
            }
        }

    # ---- Applications ----

    def create_application(
        self,
        name: str,
        endpoint: Optional[str] = None,
        iam_identity_center_options: Optional[dict[str, Any]] = None,
        data_sources: Optional[list[dict[str, Any]]] = None,
        app_configs: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        app_id = str(uuid.uuid4())
        arn = f"arn:{get_partition(self.region_name)}:es:{self.region_name}:{self.account_id}:application/{app_id}"
        app: dict[str, Any] = {
            "id": app_id,
            "arn": arn,
            "name": name,
            "endpoint": endpoint
            or f"https://{name}.{self.region_name}.es.amazonaws.com",
            "status": "ACTIVE",
            "iamIdentityCenterOptions": iam_identity_center_options or {},
            "dataSources": data_sources or [],
            "appConfigs": app_configs or [],
            "createdAt": unix_time(datetime.datetime.now()),
            "lastUpdatedAt": unix_time(datetime.datetime.now()),
        }
        self.applications[app_id] = app
        return app

    def get_application(self, app_id: str) -> dict[str, Any]:
        if app_id not in self.applications:
            raise ResourceNotFoundException(f"Application {app_id}")
        return self.applications[app_id]

    def delete_application(self, app_id: str) -> None:
        if app_id not in self.applications:
            raise ResourceNotFoundException(f"Application {app_id}")
        self.applications.pop(app_id)

    def update_application(
        self,
        app_id: str,
        data_sources: Optional[list[dict[str, Any]]] = None,
        app_configs: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        if app_id not in self.applications:
            raise ResourceNotFoundException(f"Application {app_id}")
        app = self.applications[app_id]
        if data_sources is not None:
            app["dataSources"] = data_sources
        if app_configs is not None:
            app["appConfigs"] = app_configs
        app["lastUpdatedAt"] = unix_time(datetime.datetime.now())
        return app

    def list_applications(self) -> list[dict[str, Any]]:
        return [
            {
                "id": a["id"],
                "arn": a["arn"],
                "name": a["name"],
                "endpoint": a["endpoint"],
                "status": a["status"],
                "createdAt": a["createdAt"],
                "lastUpdatedAt": a["lastUpdatedAt"],
            }
            for a in self.applications.values()
        ]

    # ---- Data Sources (per-domain) ----

    def add_data_source(
        self,
        domain_name: str,
        name: str,
        data_source_type: Optional[dict[str, Any]] = None,
        description: str = "",
    ) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        key = (domain_name, name)
        ds: dict[str, Any] = {
            "Name": name,
            "DataSourceType": data_source_type or {},
            "Description": description,
            "Status": "ACTIVE",
        }
        self.data_sources[key] = ds
        return {"Message": f"Data source {name} created successfully."}

    def get_data_source(self, domain_name: str, name: str) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        key = (domain_name, name)
        if key not in self.data_sources:
            raise ResourceNotFoundException(f"Data source {name}")
        return self.data_sources[key]

    def list_data_sources(self, domain_name: str) -> list[dict[str, Any]]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        return [ds for (dn, _), ds in self.data_sources.items() if dn == domain_name]

    def update_data_source(
        self,
        domain_name: str,
        name: str,
        data_source_type: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        key = (domain_name, name)
        if key not in self.data_sources:
            raise ResourceNotFoundException(f"Data source {name}")
        ds = self.data_sources[key]
        if data_source_type is not None:
            ds["DataSourceType"] = data_source_type
        if description is not None:
            ds["Description"] = description
        if status is not None:
            ds["Status"] = status
        return {"Message": f"Data source {name} updated successfully."}

    def delete_data_source(self, domain_name: str, name: str) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        key = (domain_name, name)
        if key not in self.data_sources:
            raise ResourceNotFoundException(f"Data source {name}")
        del self.data_sources[key]
        return {"Message": f"Data source {name} deleted successfully."}

    # ---- Direct Query Data Sources ----

    def create_direct_query_data_source(
        self,
        data_source_name: str,
        data_source_type: Optional[dict[str, Any]] = None,
        description: str = "",
        open_data_filter_pattern: str = "",
    ) -> dict[str, Any]:
        arn = f"arn:{get_partition(self.region_name)}:es:{self.region_name}:{self.account_id}:datasource/{data_source_name}"
        ds: dict[str, Any] = {
            "DataSourceName": data_source_name,
            "DataSourceType": data_source_type or {},
            "Description": description,
            "OpenDataFilterPattern": open_data_filter_pattern,
            "DataSourceArn": arn,
            "Status": "ACTIVE",
        }
        self.direct_query_data_sources[data_source_name] = ds
        return {"DataSourceArn": arn}

    def get_direct_query_data_source(self, data_source_name: str) -> dict[str, Any]:
        if data_source_name not in self.direct_query_data_sources:
            raise ResourceNotFoundException(f"Data source {data_source_name}")
        return self.direct_query_data_sources[data_source_name]

    def delete_direct_query_data_source(self, data_source_name: str) -> None:
        if data_source_name not in self.direct_query_data_sources:
            raise ResourceNotFoundException(f"Data source {data_source_name}")
        self.direct_query_data_sources.pop(data_source_name)

    def list_direct_query_data_sources(self) -> list[dict[str, Any]]:
        return list(self.direct_query_data_sources.values())

    # ---- VPC Endpoint Access ----

    def authorize_vpc_endpoint_access(
        self, domain_name: str, account: str
    ) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        if domain_name not in self.vpc_endpoint_access:
            self.vpc_endpoint_access[domain_name] = []
        principal = {
            "PrincipalType": "AWS_ACCOUNT",
            "Principal": account,
        }
        self.vpc_endpoint_access[domain_name].append(principal)
        return {"AuthorizedPrincipal": principal}

    def revoke_vpc_endpoint_access(self, domain_name: str, account: str) -> None:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        if domain_name in self.vpc_endpoint_access:
            self.vpc_endpoint_access[domain_name] = [
                p
                for p in self.vpc_endpoint_access[domain_name]
                if p["Principal"] != account
            ]

    # ---- Scheduled Actions ----

    def update_scheduled_action(
        self,
        domain_name: str,
        action_id: str,
        action_type: str,
        schedule_at: str,
        desired_start_time: Optional[int] = None,
    ) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        action: dict[str, Any] = {
            "Id": action_id,
            "Type": action_type,
            "Severity": "MEDIUM",
            "ScheduledTime": desired_start_time
            or int(unix_time(datetime.datetime.now())),
            "Description": f"Scheduled action {action_type}",
            "ScheduledBy": "CUSTOMER",
            "Status": "PENDING_UPDATE",
            "Cancellable": True,
        }
        self.scheduled_actions[action_id] = action
        return {"ScheduledAction": action}

    def list_scheduled_actions(self, domain_name: str) -> list[dict[str, Any]]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        return list(self.scheduled_actions.values())

    # ---- Domain Maintenances ----

    def start_domain_maintenance(
        self,
        domain_name: str,
        action: str,
        node_id: Optional[str] = None,
    ) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        maintenance_id = str(uuid.uuid4())
        maintenance: dict[str, Any] = {
            "MaintenanceId": maintenance_id,
            "DomainName": domain_name,
            "Action": action,
            "NodeId": node_id or "",
            "Status": "PENDING",
            "StatusMessage": "",
            "CreatedAt": unix_time(datetime.datetime.now()),
            "UpdatedAt": unix_time(datetime.datetime.now()),
        }
        if domain_name not in self.domain_maintenances:
            self.domain_maintenances[domain_name] = []
        self.domain_maintenances[domain_name].append(maintenance)
        return {"MaintenanceId": maintenance_id}

    def get_domain_maintenance_status(
        self, domain_name: str, maintenance_id: str
    ) -> dict[str, Any]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        for m in self.domain_maintenances.get(domain_name, []):
            if m["MaintenanceId"] == maintenance_id:
                return m
        raise ResourceNotFoundException(f"Maintenance {maintenance_id}")

    def list_domain_maintenances(self, domain_name: str) -> list[dict[str, Any]]:
        if domain_name not in self.domains:
            raise ResourceNotFoundException(domain_name)
        return self.domain_maintenances.get(domain_name, [])


opensearch_backends = BackendDict(OpenSearchServiceBackend, "opensearch")
