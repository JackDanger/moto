from moto.core.base_backend import BackendDict
from moto.opensearch.models import OpenSearchServiceBackend


class ElasticsearchServiceBackend(OpenSearchServiceBackend):
    def create_elasticsearch_domain(self) -> None:
        # Functionality is part of OpenSearch, as that includes all of ES functionality + more
        # Method is kept here to make sure our documentation register this as supported
        pass

    def delete_elasticsearch_domain(self) -> None:
        # Functionality is part of OpenSearch
        pass

    def describe_elasticsearch_domain(self) -> None:
        # Functionality is part of OpenSearch
        pass

    def describe_elasticsearch_domains(self) -> None:
        # Functionality is part of OpenSearch
        pass

    def describe_elasticsearch_domain_config(self) -> None:
        # Functionality is part of OpenSearch
        pass

    def update_elasticsearch_domain_config(self) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def create_package(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def delete_package(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def update_package(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def associate_package(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def dissociate_package(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def create_outbound_cross_cluster_search_connection(self) -> None:
        # Functionality is part of OpenSearch (outbound connections)
        pass

    def delete_outbound_cross_cluster_search_connection(self) -> None:
        # Functionality is part of OpenSearch
        pass

    def accept_inbound_cross_cluster_search_connection(self) -> None:
        # Functionality is part of OpenSearch
        pass

    def delete_inbound_cross_cluster_search_connection(self) -> None:
        # Functionality is part of OpenSearch
        pass

    def create_vpc_endpoint(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def delete_vpc_endpoint(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def update_vpc_endpoint(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def purchase_reserved_elasticsearch_instance_offering(self) -> None:
        # Functionality is part of OpenSearch
        pass

    def list_elasticsearch_versions(self) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass

    def list_elasticsearch_instance_types(self, **kwargs) -> None:  # type: ignore[override]
        # Functionality is part of OpenSearch
        pass


es_backends = BackendDict(ElasticsearchServiceBackend, "es")
