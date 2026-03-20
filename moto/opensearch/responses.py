"""Handles incoming opensearch requests, invokes methods, returns responses."""

import json
import re
from typing import Any

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse
from moto.es.exceptions import InvalidDomainName

from .models import OpenSearchServiceBackend, opensearch_backends


class OpenSearchServiceResponse(BaseResponse):
    """Handler for OpenSearchService requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="opensearch")

    @property
    def opensearch_backend(self) -> OpenSearchServiceBackend:
        return opensearch_backends[self.current_account][self.region]

    # ---- Classmethods for explicit ES URL routing (2015-01-01 paths) ----

    @classmethod
    def list_domains(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "GET":
            return 200, {}, response.list_domain_names()
        if request.method == "POST":
            return 200, {}, response.describe_domains()

    @classmethod
    def domains(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "POST":
            return 200, {}, response.create_domain()

    @classmethod
    def domain(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "DELETE":
            return 200, {}, response.delete_domain()
        if request.method == "GET":
            return 200, {}, response.describe_domain()

    @classmethod
    def domain_config(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "GET":
            domain_name = request.url.split("/")[-2]
            config = response.opensearch_backend.describe_domain_config(domain_name)
            return 200, {}, json.dumps({"DomainConfig": config})
        if request.method == "POST":
            return 200, {}, response.update_domain_config()

    @classmethod
    def tags(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "GET":
            return 200, {}, response.list_tags()
        if request.method == "POST":
            return 200, {}, response.add_tags()

    @classmethod
    def tag_removal(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "POST":
            return 200, {}, response.remove_tags()

    @classmethod
    def describe_es_domain_config(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        response = cls()
        response.setup_class(request, full_url, headers)
        domain_name = request.url.split("/")[-2]
        domain_config = response.opensearch_backend.describe_domain_config(
            domain_name=domain_name,
        )
        return 200, {}, json.dumps({"DomainConfig": domain_config})

    @classmethod
    def compatible_versions(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        # ES uses CompatibleElasticsearchVersions key
        domain_name = response._get_param("domainName")
        versions = response.opensearch_backend.get_compatible_versions(
            domain_name=domain_name
        )
        return 200, {}, json.dumps({"CompatibleElasticsearchVersions": versions})

    @classmethod
    def domain_auto_tunes(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_domain_auto_tunes()

    @classmethod
    def domain_change_progress(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_domain_change_progress()

    @classmethod
    def dry_run_progress(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_dry_run_progress()

    @classmethod
    def instance_type_limits_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_instance_type_limits()

    # ---- ES-specific package routes ----

    @classmethod
    def packages_route(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "POST":
            return 200, {}, response.create_package()

    @classmethod
    def packages_describe(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_packages()

    @classmethod
    def package_by_id(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "DELETE":
            return 200, {}, response.delete_package()
        if request.method == "POST":
            return 200, {}, response.update_package()

    @classmethod
    def package_history(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.get_package_version_history()

    @classmethod
    def associate_package_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.associate_package()

    @classmethod
    def dissociate_package_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.dissociate_package()

    @classmethod
    def list_packages_for_domain_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.list_packages_for_domain()

    @classmethod
    def list_domains_for_package_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.list_domains_for_package()

    # ---- ES-specific upgrade and service software update routes ----

    @classmethod
    def es_upgrade_domain_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "POST":
            return 200, {}, response.upgrade_elasticsearch_domain()
        return 200, {}, json.dumps({})

    @classmethod
    def es_upgrade_history_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.get_upgrade_history()

    @classmethod
    def es_upgrade_status_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.get_upgrade_status()

    @classmethod
    def es_service_software_cancel_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.cancel_elasticsearch_service_software_update()

    @classmethod
    def es_service_software_start_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.start_elasticsearch_service_software_update()

    @classmethod
    def es_list_vpc_endpoint_access_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.list_vpc_endpoint_access()

    # ---- ES-specific VPC endpoint routes ----

    @classmethod
    def vpc_endpoints_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "POST":
            return 200, {}, response.create_vpc_endpoint()
        if request.method == "GET":
            return 200, {}, response.list_vpc_endpoints()

    @classmethod
    def vpc_endpoints_describe(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_vpc_endpoints()

    @classmethod
    def vpc_endpoints_update(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.update_vpc_endpoint()

    @classmethod
    def vpc_endpoint_by_id(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "DELETE":
            return 200, {}, response.delete_vpc_endpoint()

    @classmethod
    def vpc_endpoints_for_domain(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.list_vpc_endpoints_for_domain()

    # ---- ES-specific connection routes ----

    @classmethod
    def outbound_connection_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "POST":
            return 200, {}, response.create_outbound_connection()

    @classmethod
    def outbound_connection_search(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_outbound_connections()

    @classmethod
    def outbound_connection_by_id(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "DELETE":
            return 200, {}, response.delete_outbound_connection()

    @classmethod
    def inbound_connection_search(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_inbound_connections()

    @classmethod
    def inbound_connection_accept(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.accept_inbound_connection()

    @classmethod
    def inbound_connection_by_id(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        if request.method == "DELETE":
            return 200, {}, response.delete_inbound_connection()

    # ---- ES-specific reserved instance routes ----

    @classmethod
    def reserved_instance_offerings_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_reserved_instance_offerings()

    @classmethod
    def reserved_instances_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.describe_reserved_instances()

    @classmethod
    def purchase_reserved_instance_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.purchase_reserved_instance_offering()

    # ---- ES-specific version/instance-type routes ----

    @classmethod
    def es_versions_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.list_elasticsearch_versions()

    @classmethod
    def es_instance_types_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.list_elasticsearch_instance_types()

    @classmethod
    def versions_route(cls, request: Any, full_url: str, headers: Any) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.list_versions()

    @classmethod
    def instance_type_details_route(
        cls, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:  # type: ignore
        response = cls()
        response.setup_class(request, full_url, headers)
        return 200, {}, response.list_instance_type_details()

    # ---- Instance methods (called by dispatch for OpenSearch 2021-01-01 paths) ----

    def create_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        if not re.match(r"^[a-z][a-z0-9\-]+$", domain_name):
            raise InvalidDomainName(domain_name)
        engine_version = self._get_param("EngineVersion")
        cluster_config = self._get_param("ClusterConfig")
        ebs_options = self._get_param("EBSOptions")
        access_policies = self._get_param("AccessPolicies")
        snapshot_options = self._get_param("SnapshotOptions")
        vpc_options = self._get_param("VPCOptions")
        cognito_options = self._get_param("CognitoOptions")
        encryption_at_rest_options = self._get_param("EncryptionAtRestOptions")
        node_to_node_encryption_options = self._get_param("NodeToNodeEncryptionOptions")
        advanced_options = self._get_param("AdvancedOptions")
        log_publishing_options = self._get_param("LogPublishingOptions")
        domain_endpoint_options = self._get_param("DomainEndpointOptions")
        advanced_security_options = self._get_param("AdvancedSecurityOptions")
        tag_list = self._get_param("TagList")
        auto_tune_options = self._get_param("AutoTuneOptions")
        off_peak_window_options = self._get_param("OffPeakWindowOptions")
        software_update_options = self._get_param("SoftwareUpdateOptions")
        # ElasticSearch specific options
        is_es = self.parsed_url.path.endswith("/es/domain")
        elasticsearch_version = self._get_param("ElasticsearchVersion")
        elasticsearch_cluster_config = self._get_param("ElasticsearchClusterConfig")
        domain = self.opensearch_backend.create_domain(
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
            tag_list=tag_list,
            auto_tune_options=auto_tune_options,
            off_peak_window_options=off_peak_window_options,
            software_update_options=software_update_options,
            is_es=is_es,
            elasticsearch_version=elasticsearch_version,
            elasticsearch_cluster_config=elasticsearch_cluster_config,
        )
        return json.dumps({"DomainStatus": domain.to_dict()})

    def get_compatible_versions(self) -> str:
        domain_name = self._get_param("domainName")
        compatible_versions = self.opensearch_backend.get_compatible_versions(
            domain_name=domain_name,
        )
        return json.dumps({"CompatibleVersions": compatible_versions})

    def delete_domain(self) -> str:
        domain_name = self.path.split("/")[-1]
        domain = self.opensearch_backend.delete_domain(
            domain_name=domain_name,
        )
        return json.dumps({"DomainStatus": domain.to_dict()})

    def describe_domain(self) -> str:
        domain_name = self.path.split("/")[-1]
        if not re.match(r"^[a-z][a-z0-9\-]+$", domain_name):
            raise InvalidDomainName(domain_name)
        domain = self.opensearch_backend.describe_domain(
            domain_name=domain_name,
        )
        return json.dumps({"DomainStatus": domain.to_dict()})

    def describe_domain_config(self) -> str:
        # Supports both body param and URL form (/domain/{name}/config)
        domain_name = self._get_param("DomainName")
        if not domain_name and self.path:
            parts = [p for p in self.path.split("/") if p]
            if len(parts) >= 2 and parts[-1] == "config":
                domain_name = parts[-2]
        config = self.opensearch_backend.describe_domain_config(domain_name=domain_name)  # type: ignore[arg-type]
        return json.dumps({"DomainConfig": config})

    def update_domain_config(self) -> str:
        domain_name = self._get_param("DomainName")
        if not domain_name and self.path:
            parts = [p for p in self.path.split("/") if p]
            if "config" in parts:
                idx = parts.index("config")
                if idx > 0:
                    domain_name = parts[idx - 1]
        domain = self.opensearch_backend.update_domain_config(
            domain_name=domain_name,
            cluster_config=self._get_param("ClusterConfig"),
            ebs_options=self._get_param("EBSOptions"),
            access_policies=self._get_param("AccessPolicies"),
            snapshot_options=self._get_param("SnapshotOptions"),
            vpc_options=self._get_param("VPCOptions"),
            cognito_options=self._get_param("CognitoOptions"),
            encryption_at_rest_options=self._get_param("EncryptionAtRestOptions"),
            node_to_node_encryption_options=self._get_param(
                "NodeToNodeEncryptionOptions"
            ),
            advanced_options=self._get_param("AdvancedOptions"),
            log_publishing_options=self._get_param("LogPublishingOptions"),
            domain_endpoint_options=self._get_param("DomainEndpointOptions"),
            advanced_security_options=self._get_param("AdvancedSecurityOptions"),
            auto_tune_options=self._get_param("AutoTuneOptions"),
            off_peak_window_options=self._get_param("OffPeakWindowOptions"),
            software_update_options=self._get_param("SoftwareUpdateOptions"),
        )
        return json.dumps({"DomainConfig": domain.to_config_dict()})

    def list_tags(self) -> str:
        arn = self._get_param("arn")
        tags = self.opensearch_backend.list_tags(arn)
        return json.dumps({"TagList": tags})

    def add_tags(self) -> str:
        arn = self._get_param("ARN")
        tags = self._get_param("TagList")
        self.opensearch_backend.add_tags(arn, tags)
        return "{}"

    def remove_tags(self) -> str:
        arn = self._get_param("ARN")
        tag_keys = self._get_param("TagKeys")
        self.opensearch_backend.remove_tags(arn, tag_keys)
        return "{}"

    def list_domain_names(self) -> str:
        engine_type = self._get_param("engineType")
        domain_names = self.opensearch_backend.list_domain_names(
            engine_type=engine_type,
        )
        return json.dumps({"DomainNames": domain_names})

    def describe_domains(self) -> str:
        domain_names = self._get_param("DomainNames")
        domains = self.opensearch_backend.describe_domains(
            domain_names=domain_names,
        )
        domain_list = [domain.to_dict() for domain in domains]
        return json.dumps({"DomainStatusList": domain_list})

    # ---- Packages ----

    def create_package(self) -> str:
        pkg = self.opensearch_backend.create_package(
            package_name=self._get_param("PackageName"),
            package_type=self._get_param("PackageType"),
            package_description=self._get_param("PackageDescription"),
            package_source=self._get_param("PackageSource"),
        )
        return json.dumps({"PackageDetails": pkg.to_dict()})

    def describe_packages(self) -> str:
        filters = self._get_param("DescribePackagesFilters")
        packages = self.opensearch_backend.describe_packages(filters=filters)
        return json.dumps({"PackageDetailsList": packages})

    def delete_package(self) -> str:
        parts = self.path.rstrip("/").split("/")
        package_id = parts[-1]
        result = self.opensearch_backend.delete_package(package_id)
        return json.dumps({"PackageDetails": result})

    def update_package(self) -> str:
        result = self.opensearch_backend.update_package(
            package_id=self._get_param("PackageID"),
            package_source=self._get_param("PackageSource"),
            package_description=self._get_param("PackageDescription"),
            commit_message=self._get_param("CommitMessage"),
        )
        return json.dumps({"PackageDetails": result})

    def associate_package(self) -> str:
        parts = self.path.rstrip("/").split("/")
        # /packages/associate/{package_id}/{domain_name}
        # or /2021-01-01/packages/associate/{package_id}/{domain_name}
        domain_name = parts[-1]
        package_id = parts[-2]
        result = self.opensearch_backend.associate_package(package_id, domain_name)
        return json.dumps({"DomainPackageDetails": result})

    def dissociate_package(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-1]
        package_id = parts[-2]
        result = self.opensearch_backend.dissociate_package(package_id, domain_name)
        return json.dumps({"DomainPackageDetails": result})

    def list_packages_for_domain(self) -> str:
        parts = self.path.rstrip("/").split("/")
        # /domain/{domain_name}/packages
        domain_name = parts[-2]
        results = self.opensearch_backend.list_packages_for_domain(domain_name)
        return json.dumps({"DomainPackageDetailsList": results})

    def list_domains_for_package(self) -> str:
        parts = self.path.rstrip("/").split("/")
        # /packages/{package_id}/domains
        package_id = parts[-2]
        results = self.opensearch_backend.list_domains_for_package(package_id)
        return json.dumps({"DomainPackageDetailsList": results})

    def get_package_version_history(self) -> str:
        parts = self.path.rstrip("/").split("/")
        # /packages/{package_id}/history
        package_id = parts[-2]
        results = self.opensearch_backend.get_package_version_history(package_id)
        return json.dumps(
            {"PackageVersionHistoryList": results, "PackageID": package_id}
        )

    # ---- VPC Endpoints ----

    def create_vpc_endpoint(self) -> str:
        ep = self.opensearch_backend.create_vpc_endpoint(
            domain_arn=self._get_param("DomainArn"),
            vpc_options=self._get_param("VpcOptions"),
        )
        return json.dumps({"VpcEndpoint": ep.to_dict()})

    def describe_vpc_endpoints(self) -> str:
        vpc_endpoint_ids = self._get_param("VpcEndpointIds")
        endpoints, errors = self.opensearch_backend.describe_vpc_endpoints(
            vpc_endpoint_ids or []
        )
        return json.dumps(
            {
                "VpcEndpoints": endpoints,
                "VpcEndpointErrors": errors,
            }
        )

    def update_vpc_endpoint(self) -> str:
        ep = self.opensearch_backend.update_vpc_endpoint(
            vpc_endpoint_id=self._get_param("VpcEndpointId"),
            vpc_options=self._get_param("VpcOptions"),
        )
        return json.dumps({"VpcEndpoint": ep.to_dict()})

    def delete_vpc_endpoint(self) -> str:
        parts = self.path.rstrip("/").split("/")
        vpc_endpoint_id = parts[-1]
        summary = self.opensearch_backend.delete_vpc_endpoint(vpc_endpoint_id)
        return json.dumps({"VpcEndpointSummary": summary})

    def list_vpc_endpoints(self) -> str:
        endpoints = self.opensearch_backend.list_vpc_endpoints()
        return json.dumps({"VpcEndpointSummaryList": endpoints})

    def list_vpc_endpoints_for_domain(self) -> str:
        parts = self.path.rstrip("/").split("/")
        # /domain/{domain_name}/vpcEndpoints
        domain_name = parts[-2]
        endpoints = self.opensearch_backend.list_vpc_endpoints_for_domain(domain_name)
        return json.dumps({"VpcEndpointSummaryList": endpoints})

    # ---- Connections ----

    def create_outbound_connection(self) -> str:
        conn = self.opensearch_backend.create_outbound_connection(
            local_domain_info=self._get_param("LocalDomainInfo"),
            remote_domain_info=self._get_param("RemoteDomainInfo"),
            connection_alias=self._get_param("ConnectionAlias"),
            connection_mode=self._get_param("ConnectionMode"),
        )
        return json.dumps(conn.to_dict())

    def describe_outbound_connections(self) -> str:
        filters = self._get_param("Filters")
        connections = self.opensearch_backend.describe_outbound_connections(
            filters=filters
        )
        return json.dumps({"Connections": connections})

    def delete_outbound_connection(self) -> str:
        parts = self.path.rstrip("/").split("/")
        connection_id = parts[-1]
        result = self.opensearch_backend.delete_outbound_connection(connection_id)
        return json.dumps({"Connection": result})

    def accept_inbound_connection(self) -> str:
        parts = self.path.rstrip("/").split("/")
        connection_id = parts[-2]
        result = self.opensearch_backend.accept_inbound_connection(connection_id)
        return json.dumps({"Connection": result})

    def describe_inbound_connections(self) -> str:
        filters = self._get_param("Filters")
        connections = self.opensearch_backend.describe_inbound_connections(
            filters=filters
        )
        return json.dumps({"Connections": connections})

    def delete_inbound_connection(self) -> str:
        parts = self.path.rstrip("/").split("/")
        connection_id = parts[-1]
        result = self.opensearch_backend.delete_inbound_connection(connection_id)
        return json.dumps({"Connection": result})

    # ---- Reserved Instances ----

    def describe_reserved_instance_offerings(self) -> str:
        offerings = self.opensearch_backend.describe_reserved_instance_offerings()
        return json.dumps({"ReservedInstanceOfferings": offerings})

    def describe_reserved_instances(self) -> str:
        instances = self.opensearch_backend.describe_reserved_instances()
        return json.dumps({"ReservedInstances": instances})

    def purchase_reserved_instance_offering(self) -> str:
        result = self.opensearch_backend.purchase_reserved_instance_offering(
            reserved_instance_offering_id=self._get_param("ReservedInstanceOfferingId"),
            reservation_name=self._get_param("ReservationName"),
            instance_count=self._get_param("InstanceCount"),
        )
        return json.dumps(result)

    # ---- Versions ----

    def list_versions(self) -> str:
        versions = self.opensearch_backend.list_versions()
        return json.dumps({"Versions": versions})

    def list_elasticsearch_versions(self) -> str:
        versions = self.opensearch_backend.list_elasticsearch_versions()
        return json.dumps({"ElasticsearchVersions": versions})

    # ---- Instance Types ----

    def list_instance_type_details(self) -> str:
        parts = self.path.rstrip("/").split("/")
        # /opensearch/instanceTypeDetails/{engine_version}
        engine_version = parts[-1]
        details = self.opensearch_backend.list_instance_type_details(engine_version)
        return json.dumps({"InstanceTypeDetails": details})

    def list_elasticsearch_instance_types(self) -> str:
        parts = self.path.rstrip("/").split("/")
        # /es/instanceTypes/{version}
        version = parts[-1]
        types = self.opensearch_backend.list_elasticsearch_instance_types(version)
        return json.dumps({"ElasticsearchInstanceTypes": types})

    # ---- Domain sub-resources ----

    def describe_domain_auto_tunes(self) -> str:
        domain_name = self.path.split("/")[-2]
        auto_tunes = self.opensearch_backend.describe_domain_auto_tunes(domain_name)
        return json.dumps({"AutoTunes": auto_tunes})

    def describe_domain_change_progress(self) -> str:
        domain_name = self.path.split("/")[-2]
        result = self.opensearch_backend.describe_domain_change_progress(domain_name)
        return json.dumps(result)

    def describe_domain_health(self) -> str:
        domain_name = self.path.split("/")[-2]
        health = self.opensearch_backend.describe_domain_health(domain_name)
        return json.dumps(health)

    def describe_domain_nodes(self) -> str:
        domain_name = self.path.split("/")[-2]
        nodes = self.opensearch_backend.describe_domain_nodes(domain_name)
        return json.dumps({"DomainNodesStatusList": nodes})

    def describe_dry_run_progress(self) -> str:
        domain_name = self.path.split("/")[-2]
        result = self.opensearch_backend.describe_dry_run_progress(domain_name)
        return json.dumps(result)

    def describe_instance_type_limits(self) -> str:
        parts = self.path.rstrip("/").split("/")
        instance_type = parts[-1]
        engine_version = parts[-2]
        result = self.opensearch_backend.describe_instance_type_limits(
            instance_type, engine_version
        )
        return json.dumps(result)

    def get_default_application_setting(self) -> str:
        return json.dumps({})

    # ---- Applications (CRUD) ----

    def create_application(self) -> str:
        app = self.opensearch_backend.create_application(
            name=self._get_param("name"),
            endpoint=self._get_param("endpoint"),
            iam_identity_center_options=self._get_param("iamIdentityCenterOptions"),
            data_sources=self._get_param("dataSources"),
            app_configs=self._get_param("appConfigs"),
        )
        return json.dumps(app)

    def get_application(self) -> str:
        parts = self.path.rstrip("/").split("/")
        app_id = parts[-1]
        app = self.opensearch_backend.get_application(app_id)
        return json.dumps(app)

    def delete_application(self) -> str:
        parts = self.path.rstrip("/").split("/")
        app_id = parts[-1]
        self.opensearch_backend.delete_application(app_id)
        return "{}"

    def update_application(self) -> str:
        parts = self.path.rstrip("/").split("/")
        app_id = parts[-1]
        app = self.opensearch_backend.update_application(
            app_id=app_id,
            data_sources=self._get_param("dataSources"),
            app_configs=self._get_param("appConfigs"),
        )
        return json.dumps(app)

    def list_applications(self) -> str:
        applications = self.opensearch_backend.list_applications()
        return json.dumps({"ApplicationSummaries": applications})

    # ---- Direct Query Data Sources ----

    def create_direct_query_data_source(self) -> str:
        result = self.opensearch_backend.create_direct_query_data_source(
            data_source_name=self._get_param("DataSourceName"),
            data_source_type=self._get_param("DataSourceType"),
            description=self._get_param("Description", ""),
            open_data_filter_pattern=self._get_param("OpenDataFilterPattern", ""),
        )
        return json.dumps(result)

    def get_direct_query_data_source(self) -> str:
        parts = self.path.rstrip("/").split("/")
        data_source_name = parts[-1]
        ds = self.opensearch_backend.get_direct_query_data_source(data_source_name)
        return json.dumps(ds)

    def delete_direct_query_data_source(self) -> str:
        parts = self.path.rstrip("/").split("/")
        data_source_name = parts[-1]
        self.opensearch_backend.delete_direct_query_data_source(data_source_name)
        return "{}"

    # ---- DataSources (domain-scoped) ----

    def add_data_source(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        result = self.opensearch_backend.add_data_source(
            domain_name=domain_name,
            name=self._get_param("Name"),
            data_source_type=self._get_param("DataSourceType"),
            description=self._get_param("Description", ""),
        )
        return json.dumps(result)

    def get_data_source(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-3]
        name = parts[-1]
        ds = self.opensearch_backend.get_data_source(
            domain_name=domain_name,
            name=name,
        )
        return json.dumps(ds)

    def list_data_sources(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        data_sources = self.opensearch_backend.list_data_sources(
            domain_name=domain_name,
        )
        return json.dumps({"DataSources": data_sources})

    def update_data_source(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-3]
        name = parts[-1]
        result = self.opensearch_backend.update_data_source(
            domain_name=domain_name,
            name=name,
            data_source_type=self._get_param("DataSourceType"),
            description=self._get_param("Description"),
            status=self._get_param("Status"),
        )
        return json.dumps(result)

    def delete_data_source(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-3]
        name = parts[-1]
        result = self.opensearch_backend.delete_data_source(
            domain_name=domain_name,
            name=name,
        )
        return json.dumps(result)

    # ---- VPC Endpoint Access ----

    def authorize_vpc_endpoint_access(self) -> str:
        parts = self.path.rstrip("/").split("/")
        # /2021-01-01/opensearch/domain/{domain_name}/authorizeVpcEndpointAccess
        domain_name = parts[-2]
        result = self.opensearch_backend.authorize_vpc_endpoint_access(
            domain_name=domain_name,
            account=self._get_param("Account"),
        )
        return json.dumps(result)

    def revoke_vpc_endpoint_access(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        self.opensearch_backend.revoke_vpc_endpoint_access(
            domain_name=domain_name,
            account=self._get_param("Account"),
        )
        return "{}"

    # ---- Scheduled Actions ----

    def update_scheduled_action(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        result = self.opensearch_backend.update_scheduled_action(
            domain_name=domain_name,
            action_id=self._get_param("ActionID"),
            action_type=self._get_param("ActionType"),
            schedule_at=self._get_param("ScheduleAt"),
            desired_start_time=self._get_param("DesiredStartTime"),
        )
        return json.dumps(result)

    def list_scheduled_actions(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        actions = self.opensearch_backend.list_scheduled_actions(domain_name)
        return json.dumps({"ScheduledActions": actions})

    # ---- Domain Maintenances ----

    def start_domain_maintenance(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        result = self.opensearch_backend.start_domain_maintenance(
            domain_name=domain_name,
            action=self._get_param("Action"),
            node_id=self._get_param("NodeId"),
        )
        return json.dumps(result)

    def get_domain_maintenance_status(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        maintenance_id = self._get_param("maintenanceId")
        result = self.opensearch_backend.get_domain_maintenance_status(
            domain_name, maintenance_id
        )
        return json.dumps(result)

    def list_domain_maintenances(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        maintenances = self.opensearch_backend.list_domain_maintenances(domain_name)
        return json.dumps({"DomainMaintenances": maintenances})

    def get_upgrade_history(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        return json.dumps({"UpgradeHistories": [], "NextToken": None})

    def get_upgrade_status(self) -> str:
        parts = self.path.rstrip("/").split("/")
        domain_name = parts[-2]
        return json.dumps({"UpgradeName": "", "StepStatus": "SUCCEEDED", "UpgradeStep": "SNAPSHOT"})

    def cancel_service_software_update(self) -> str:
        body = json.loads(self.body)
        domain_name = body.get("DomainName", "")
        return json.dumps({"ServiceSoftwareOptions": {"CurrentVersion": "", "NewVersion": "", "UpdateAvailable": False, "Cancellable": False, "UpdateStatus": "COMPLETED", "Description": "", "AutomatedUpdateDate": "1970-01-01T00:00:00Z", "OptionalDeployment": False}})

    def start_service_software_update(self) -> str:
        body = json.loads(self.body)
        domain_name = body.get("DomainName", "")
        return json.dumps({"ServiceSoftwareOptions": {"CurrentVersion": "", "NewVersion": "", "UpdateAvailable": False, "Cancellable": True, "UpdateStatus": "PENDING_UPDATE", "Description": "Update pending", "AutomatedUpdateDate": "1970-01-01T00:00:00Z", "OptionalDeployment": False}})

    def list_vpc_endpoint_access(self) -> str:
        return json.dumps({"AuthorizedPrincipalList": [], "NextToken": None})

    def upgrade_domain(self) -> str:
        body = json.loads(self.body)
        domain_name = body.get("DomainName", "")
        return json.dumps({"DomainName": domain_name, "TargetVersion": body.get("TargetVersion", ""), "PerformCheckOnly": body.get("PerformCheckOnly", False), "AdvancedOptions": {}, "ChangeProgressDetails": {}})

    def list_direct_query_data_sources(self) -> str:
        sources = self.opensearch_backend.list_direct_query_data_sources()
        return json.dumps({"DirectQueryDataSources": sources})

    def get_index(self) -> str:
        return json.dumps({"Indices": []})

    def create_index(self) -> str:
        return json.dumps({})

    def delete_index(self) -> str:
        return json.dumps({})

    def update_index(self) -> str:
        return json.dumps({})

    def update_direct_query_data_source(self) -> str:
        return json.dumps({})

    def reject_inbound_connection(self) -> str:
        # ConnectionId is in the URL path: /2021-01-01/opensearch/cc/inboundConnection/{ConnectionId}/reject
        path_parts = self.path.split("/")
        connection_id = path_parts[-2] if len(path_parts) >= 2 else ""
        return json.dumps({
            "Connection": {
                "ConnectionId": connection_id,
                "ConnectionStatus": {"StatusCode": "REJECTED"},
            }
        })

    def cancel_domain_config_change(self) -> str:
        # DomainName is in the URL path: /2021-01-01/opensearch/domain/{DomainName}/config/cancel
        path_parts = self.path.split("/")
        domain_name = path_parts[-3] if len(path_parts) >= 3 else ""
        body = json.loads(self.body) if self.body else {}
        return json.dumps({
            "DryRun": body.get("DryRun", False),
            "CancelledChangeIds": [],
            "CancelledChangeProperties": [],
        })

    def associate_packages(self) -> str:
        return json.dumps({"DomainPackageDetailsList": []})

    def dissociate_packages(self) -> str:
        return json.dumps({"DomainPackageDetailsList": []})

    def put_default_application_setting(self) -> str:
        return json.dumps({})

    def update_package_scope(self) -> str:
        return json.dumps({})

    def add_direct_query_data_source(self) -> str:
        return json.dumps({})

    # ES-specific operation name aliases
    def upgrade_elasticsearch_domain(self) -> str:
        return self.upgrade_domain()

    def cancel_elasticsearch_service_software_update(self) -> str:
        return self.cancel_service_software_update()

    def start_elasticsearch_service_software_update(self) -> str:
        return self.start_service_software_update()
