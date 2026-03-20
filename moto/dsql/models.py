"""AuroraDSQLBackend class with methods for supported APIs."""

from collections import OrderedDict
from typing import Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.moto_api._internal import mock_random
from moto.moto_api._internal.managed_state_model import ManagedState
from moto.utilities.utils import get_partition

from .exceptions import ResourceNotFoundException


class Cluster(BaseModel, ManagedState):
    """Model for an AuroraDSQL cluster."""

    def __init__(
        self,
        region_name: str,
        account_id: str,
        deletion_protection_enabled: Optional[bool],
        tags: Optional[dict[str, str]],
        client_token: Optional[str],
    ):
        ManagedState.__init__(
            self, "dsql::cluster", transitions=[("CREATING", "ACTIVE")]
        )
        self.region_name = region_name
        self.account_id = account_id
        self.identifier = mock_random.get_random_hex(26)
        self.arn = f"arn:{get_partition(self.region_name)}:dsql:{self.region_name}:{self.account_id}:cluster/{self.identifier}"
        self.creation_time = utcnow()
        self.deletion_protection_enabled = deletion_protection_enabled
        self.tags = tags
        self.client_token = client_token
        self.endpoint = f"{self.identifier}.{self.region_name}.on.aws"
        self.endpoint_service_name = f"com.amazonaws.{self.region_name}.dsql-7cwu"
        self.encryption_details = {
            "encryptionStatus": "ENABLED",
            "encryptionType": "AWS_OWNED_KMS_KEY",
        }


class AuroraDSQLBackend(BaseBackend):
    """Implementation of AuroraDSQL APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.region_name = region_name
        self.account_id = account_id
        self.partition = get_partition(region_name)
        self.clusters: dict[str, Cluster] = OrderedDict()

    def create_cluster(
        self,
        deletion_protection_enabled: bool,
        tags: Optional[dict[str, str]],
        client_token: Optional[str],
    ) -> Cluster:
        cluster = Cluster(
            self.region_name,
            self.account_id,
            deletion_protection_enabled,
            tags,
            client_token,
        )
        self.clusters[cluster.identifier] = cluster
        return cluster

    def delete_cluster(self, identifier: str) -> Cluster:
        if identifier not in self.clusters:
            arn = f"arn:{get_partition(self.region_name)}:dsql:{self.region_name}:{self.account_id}:cluster/{identifier}"
            raise ResourceNotFoundException(arn, identifier, "cluster")
        cluster = self.clusters.pop(identifier)
        return cluster

    def get_cluster(self, identifier: str) -> Cluster:
        if identifier not in self.clusters:
            arn = f"arn:{get_partition(self.region_name)}:dsql:{self.region_name}:{self.account_id}:cluster/{identifier}"
            raise ResourceNotFoundException(arn, identifier, "cluster")
        cluster = self.clusters[identifier]
        cluster.advance()
        return cluster

    def get_vpc_endpoint_service_name(self, identifier: str) -> dict[str, str]:
        cluster = self.get_cluster(identifier=identifier)
        return {
            "serviceName": cluster.endpoint_service_name,
            "clusterVpcEndpoint": cluster.endpoint,
        }

    def list_tags_for_resource(self, identifier: str) -> dict[str, str]:
        cluster = self.get_cluster(identifier=identifier)
        return cluster.tags or {}

    def list_clusters(self) -> list[Cluster]:
        return list(self.clusters.values())

    def update_cluster(
        self,
        identifier: str,
        deletion_protection_enabled: Optional[bool],
        client_token: Optional[str],
    ) -> Cluster:
        cluster = self.get_cluster(identifier=identifier)
        if deletion_protection_enabled is not None:
            cluster.deletion_protection_enabled = deletion_protection_enabled
        return cluster

    def get_cluster_policy(self, identifier: str) -> Optional[str]:
        cluster = self.get_cluster(identifier=identifier)
        return getattr(cluster, "policy", None)

    def put_cluster_policy(self, identifier: str, policy: str) -> str:
        cluster = self.get_cluster(identifier=identifier)
        cluster.policy = policy  # type: ignore[attr-defined]
        return policy

    def delete_cluster_policy(self, identifier: str) -> None:
        cluster = self.get_cluster(identifier=identifier)
        cluster.policy = None  # type: ignore[attr-defined]

    def tag_resource(self, identifier: str, tags: dict[str, str]) -> None:
        cluster = self.get_cluster(identifier=identifier)
        existing = dict(cluster.tags or {})
        existing.update(tags)
        cluster.tags = existing

    def untag_resource(self, identifier: str, tag_keys: list[str]) -> None:
        cluster = self.get_cluster(identifier=identifier)
        existing = dict(cluster.tags or {})
        for key in tag_keys:
            existing.pop(key, None)
        cluster.tags = existing


dsql_backends = BackendDict(
    AuroraDSQLBackend,
    "dsql",
    # currently botocore does not provide a dsql endpoint
    # https://github.com/boto/botocore/blob/e07cddc333fe4fb90efcd5d04324dd83f9cc3a57/botocore/data/endpoints.json
    use_boto3_regions=False,
    additional_regions=["us-east-1", "us-east-2"],
)
