"""CloudHSMV2Backend class with methods for supported APIs."""

import uuid
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.utils import utcnow
from moto.utilities.paginator import paginate

from .exceptions import ResourceNotFoundException


class Hsm:
    def __init__(
        self,
        cluster_id: str,
        availability_zone: str,
        ip_address: Optional[str] = None,
        hsm_type: str = "hsm1.medium",
        subnet_id: str = "",
    ):
        self.hsm_id = "hsm-" + str(uuid.uuid4())[:17]
        self.cluster_id = cluster_id
        self.availability_zone = availability_zone
        self.ip_address = ip_address or "10.0.0.1"
        self.hsm_type = hsm_type
        self.state = "ACTIVE"
        self.state_message = "HSM created."
        self.subnet_id = subnet_id
        self.eni_id = "eni-" + str(uuid.uuid4())[:8]
        self.eni_ip = self.ip_address

    def to_dict(self) -> dict[str, Any]:
        return {
            "AvailabilityZone": self.availability_zone,
            "ClusterId": self.cluster_id,
            "SubnetId": self.subnet_id,
            "EniId": self.eni_id,
            "EniIp": self.eni_ip,
            "HsmId": self.hsm_id,
            "HsmType": self.hsm_type,
            "State": self.state,
            "StateMessage": self.state_message,
        }


class Cluster:
    def __init__(
        self,
        backup_retention_policy: Optional[dict[str, str]],
        hsm_type: str,
        source_backup_id: Optional[str],
        subnet_ids: list[str],
        network_type: str = "IPV4",
        tag_list: Optional[list[dict[str, str]]] = None,
        mode: str = "DEFAULT",
        region_name: str = "us-east-1",
    ):
        self.cluster_id = str(uuid.uuid4())
        self.backup_policy = "DEFAULT"
        self.backup_retention_policy = backup_retention_policy
        self.create_timestamp = utcnow()
        self.hsms: list[Hsm] = []
        self.hsm_type = hsm_type
        self.source_backup_id = source_backup_id
        self.state = "ACTIVE"
        self.state_message = "The cluster is ready for use."
        # XXX - This should map the availability zone to subnet in that zone
        # Mapping it to the region is wrong, as this map will only have a single item
        # Note: AWS probably has validation that each subnet_id *has* to be in a unique zone
        self.subnet_mapping = {region_name: subnet_id for subnet_id in subnet_ids}  # noqa: B035
        self.vpc_id = "vpc-" + str(uuid.uuid4())[:8]
        self.network_type = network_type
        self.certificates = {
            "ClusterCsr": "",
            "HsmCertificate": "",
            "AwsHardwareCertificate": "",
            "ManufacturerHardwareCertificate": "",
            "ClusterCertificate": "",
        }
        self.tag_list = tag_list or []
        self.mode = mode

    def to_dict(self) -> dict[str, Any]:
        return {
            "BackupPolicy": self.backup_policy,
            "BackupRetentionPolicy": self.backup_retention_policy,
            "ClusterId": self.cluster_id,
            "CreateTimestamp": self.create_timestamp,
            "Hsms": [h.to_dict() for h in self.hsms],
            "HsmType": self.hsm_type,
            "SourceBackupId": self.source_backup_id,
            "State": self.state,
            "StateMessage": self.state_message,
            "SubnetMapping": self.subnet_mapping,
            "VpcId": self.vpc_id,
            "NetworkType": self.network_type,
            "Certificates": self.certificates,
            "TagList": self.tag_list,
            "Mode": self.mode,
        }


class Backup:
    def __init__(
        self,
        cluster_id: str,
        hsm_type: str,
        mode: str,
        tag_list: Optional[list[dict[str, str]]],
        source_backup: Optional[str] = None,
        source_cluster: Optional[str] = None,
        source_region: Optional[str] = None,
        never_expires: bool = False,
        region_name: str = "us-east-1",
    ):
        self.backup_id = str(uuid.uuid4())
        self.backup_arn = (
            f"arn:aws:cloudhsm:{region_name}:123456789012:backup/{self.backup_id}"
        )
        self.backup_state = "READY"
        self.cluster_id = cluster_id
        self.create_timestamp = utcnow()
        self.copy_timestamp = utcnow() if source_backup else None
        self.never_expires = never_expires
        self.source_region = source_region
        self.source_backup = source_backup
        self.source_cluster = source_cluster
        self.delete_timestamp = None
        self.tag_list = tag_list or []
        self.hsm_type = hsm_type
        self.mode = mode

    def to_dict(self) -> dict[str, Any]:
        result = {
            "BackupId": self.backup_id,
            "BackupArn": self.backup_arn,
            "BackupState": self.backup_state,
            "ClusterId": self.cluster_id,
            "CreateTimestamp": self.create_timestamp,
            "NeverExpires": self.never_expires,
            "TagList": self.tag_list,
            "HsmType": self.hsm_type,
            "Mode": self.mode,
        }

        if self.copy_timestamp:
            result["CopyTimestamp"] = self.copy_timestamp
        if self.source_region:
            result["SourceRegion"] = self.source_region
        if self.source_backup:
            result["SourceBackup"] = self.source_backup
        if self.source_cluster:
            result["SourceCluster"] = self.source_cluster
        if self.delete_timestamp:
            result["DeleteTimestamp"] = self.delete_timestamp

        return result


class CloudHSMV2Backend(BaseBackend):
    """Implementation of CloudHSMV2 APIs."""

    PAGINATION_MODEL = {
        "describe_backups": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "backup_id",
            "fail_on_invalid_token": False,
        },
        "describe_clusters": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "ClusterId",
            "fail_on_invalid_token": False,
        },
    }

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.tags: dict[str, list[dict[str, str]]] = {}
        self.clusters: dict[str, Cluster] = {}
        self.resource_policies: dict[str, str] = {}
        self.backups: dict[str, Backup] = {}

    def list_tags(
        self, resource_id: str, next_token: str, max_results: int
    ) -> tuple[list[dict[str, str]], Optional[str]]:
        """
        Pagination is not yet implemented
        """
        if resource_id not in self.tags:
            return [], None

        tags = sorted(self.tags.get(resource_id, []), key=lambda x: x["Key"])

        return tags, None

    def tag_resource(
        self, resource_id: str, tag_list: list[dict[str, str]]
    ) -> dict[str, Any]:
        if resource_id not in self.tags:
            self.tags[resource_id] = []

        for new_tag in tag_list:
            tag_exists = False
            for existing_tag in self.tags[resource_id]:
                if existing_tag["Key"] == new_tag["Key"]:
                    existing_tag["Value"] = new_tag["Value"]
                    tag_exists = True
                    break
            if not tag_exists:
                self.tags[resource_id].append(new_tag)

        return {}

    def untag_resource(
        self, resource_id: str, tag_key_list: list[str]
    ) -> dict[str, Any]:
        if resource_id in self.tags:
            self.tags[resource_id] = [
                tag for tag in self.tags[resource_id] if tag["Key"] not in tag_key_list
            ]

        return {}

    def create_cluster(
        self,
        backup_retention_policy: Optional[dict[str, str]],
        hsm_type: str,
        source_backup_id: Optional[str],
        subnet_ids: list[str],
        network_type: Optional[str],
        tag_list: Optional[list[dict[str, str]]],
        mode: Optional[str],
    ) -> dict[str, Any]:
        cluster = Cluster(
            backup_retention_policy=backup_retention_policy,
            hsm_type=hsm_type,
            source_backup_id=source_backup_id,
            subnet_ids=subnet_ids,
            network_type=network_type or "IPV4",
            tag_list=tag_list,
            mode=mode or "DEFAULT",
            region_name=self.region_name,
        )
        self.clusters[cluster.cluster_id] = cluster

        backup = Backup(
            cluster_id=cluster.cluster_id,
            hsm_type=hsm_type,
            mode=mode or "DEFAULT",
            tag_list=tag_list,
            region_name=self.region_name,
        )
        self.backups[backup.backup_id] = backup

        return cluster.to_dict()

    def delete_cluster(self, cluster_id: str) -> dict[str, Any]:
        if cluster_id not in self.clusters:
            raise ResourceNotFoundException(f"Cluster {cluster_id} not found")

        cluster = self.clusters[cluster_id]
        cluster.state = "DELETED"
        cluster.state_message = "Cluster deleted"
        del self.clusters[cluster_id]
        return cluster.to_dict()

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_clusters(
        self, filters: Optional[dict[str, list[str]]] = None
    ) -> list[dict[str, str]]:
        clusters = list(self.clusters.values())

        if filters:
            for key, values in filters.items():
                if key == "clusterIds":
                    clusters = [c for c in clusters if c.cluster_id in values]
                elif key == "states":
                    clusters = [c for c in clusters if c.state in values]
                elif key == "vpcIds":
                    clusters = [c for c in clusters if c.vpc_id in values]

        clusters = sorted(clusters, key=lambda x: x.create_timestamp)
        return [c.to_dict() for c in clusters]

    def get_resource_policy(self, resource_arn: str) -> Optional[str]:
        return self.resource_policies.get(resource_arn)

    @paginate(PAGINATION_MODEL)
    def describe_backups(
        self,
        filters: Optional[dict[str, list[str]]],
        shared: Optional[bool],
        sort_ascending: Optional[bool],
    ) -> list[Backup]:
        backups = list(self.backups.values())

        if filters:
            for key, values in filters.items():
                if key == "backupIds":
                    backups = [b for b in backups if b.backup_id in values]
                elif key == "sourceBackupIds":
                    backups = [b for b in backups if b.source_backup in values]
                elif key == "clusterIds":
                    backups = [b for b in backups if b.cluster_id in values]
                elif key == "states":
                    backups = [b for b in backups if b.backup_state in values]
                elif key == "neverExpires":
                    never_expires = values[0].lower() == "true"
                    backups = [b for b in backups if b.never_expires == never_expires]

        backups.sort(
            key=lambda x: x.create_timestamp,
            reverse=not sort_ascending if sort_ascending is not None else True,
        )
        return backups

    def put_resource_policy(self, resource_arn: str, policy: str) -> dict[str, str]:
        self.resource_policies[resource_arn] = policy
        return {"ResourceArn": resource_arn, "Policy": policy}

    def delete_resource_policy(self, resource_arn: str) -> dict[str, Any]:
        policy = self.resource_policies.pop(resource_arn, None)
        result: dict[str, Any] = {}
        if resource_arn:
            result["ResourceArn"] = resource_arn
        if policy:
            result["Policy"] = policy
        return result

    def create_hsm(
        self,
        cluster_id: str,
        availability_zone: str,
        ip_address: Optional[str],
    ) -> dict[str, Any]:
        if cluster_id not in self.clusters:
            raise ResourceNotFoundException(f"Cluster {cluster_id} not found")

        cluster = self.clusters[cluster_id]
        subnet_id = next(iter(cluster.subnet_mapping.values()), "")

        hsm = Hsm(
            cluster_id=cluster_id,
            availability_zone=availability_zone,
            ip_address=ip_address,
            hsm_type=cluster.hsm_type,
            subnet_id=subnet_id,
        )
        cluster.hsms.append(hsm)
        return hsm.to_dict()

    def delete_hsm(
        self,
        cluster_id: str,
        hsm_id: Optional[str],
        eni_id: Optional[str],
        eni_ip: Optional[str],
    ) -> Optional[str]:
        if cluster_id not in self.clusters:
            raise ResourceNotFoundException(f"Cluster {cluster_id} not found")

        cluster = self.clusters[cluster_id]

        for i, hsm in enumerate(cluster.hsms):
            if hsm_id and hsm.hsm_id == hsm_id:
                cluster.hsms.pop(i)
                return hsm.hsm_id
            if eni_id and hsm.eni_id == eni_id:
                cluster.hsms.pop(i)
                return hsm.hsm_id
            if eni_ip and hsm.eni_ip == eni_ip:
                cluster.hsms.pop(i)
                return hsm.hsm_id

        # If no specific identifier given, delete first HSM
        if not hsm_id and not eni_id and not eni_ip and cluster.hsms:
            hsm = cluster.hsms.pop(0)
            return hsm.hsm_id

        raise ResourceNotFoundException("HSM not found")

    def delete_backup(self, backup_id: str) -> Backup:
        if backup_id not in self.backups:
            raise ResourceNotFoundException(f"Backup {backup_id} not found")

        backup = self.backups[backup_id]
        backup.backup_state = "PENDING_DELETION"
        backup.delete_timestamp = utcnow()
        return backup

    def copy_backup_to_region(
        self,
        destination_region: str,
        backup_id: str,
        tag_list: Optional[list[dict[str, str]]],
    ) -> dict[str, Any]:
        if backup_id not in self.backups:
            raise ResourceNotFoundException(f"Backup {backup_id} not found")

        source_backup = self.backups[backup_id]
        return {
            "DestinationBackup": {
                "CreateTimestamp": utcnow().isoformat(),
                "SourceRegion": self.region_name,
                "SourceBackup": backup_id,
                "SourceCluster": source_backup.cluster_id,
            }
        }

    def initialize_cluster(
        self,
        cluster_id: str,
        signed_cert: str,
        trust_anchor: str,
    ) -> dict[str, Any]:
        if cluster_id not in self.clusters:
            raise ResourceNotFoundException(f"Cluster {cluster_id} not found")

        cluster = self.clusters[cluster_id]
        cluster.state = "INITIALIZE_IN_PROGRESS"
        cluster.state_message = "Cluster is initializing. State will change to INITIALIZED upon completion."
        cluster.certificates["ClusterCertificate"] = signed_cert
        return {
            "State": cluster.state,
            "StateMessage": cluster.state_message,
        }

    def modify_backup_attributes(
        self,
        backup_id: str,
        never_expires: bool,
    ) -> Backup:
        if backup_id not in self.backups:
            raise ResourceNotFoundException(f"Backup {backup_id} not found")

        backup = self.backups[backup_id]
        backup.never_expires = never_expires
        return backup

    def modify_cluster(
        self,
        cluster_id: str,
        backup_retention_policy: Optional[dict[str, str]],
        hsm_type: Optional[str],
    ) -> dict[str, Any]:
        if cluster_id not in self.clusters:
            raise ResourceNotFoundException(f"Cluster {cluster_id} not found")

        cluster = self.clusters[cluster_id]
        if backup_retention_policy is not None:
            cluster.backup_retention_policy = backup_retention_policy
        if hsm_type is not None:
            cluster.hsm_type = hsm_type
        return cluster.to_dict()

    def restore_backup(self, backup_id: str) -> Backup:
        if backup_id not in self.backups:
            raise ResourceNotFoundException(f"Backup {backup_id} not found")

        backup = self.backups[backup_id]
        backup.backup_state = "READY"
        backup.delete_timestamp = None
        return backup


cloudhsmv2_backends = BackendDict(CloudHSMV2Backend, "cloudhsmv2")
