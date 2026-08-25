"""Handles incoming cloudhsmv2 requests, invokes methods, returns responses."""

import json
from datetime import datetime
from typing import Any

from moto.core.responses import BaseResponse

from .models import CloudHSMV2Backend, cloudhsmv2_backends


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)


class CloudHSMV2Response(BaseResponse):
    """Handler for CloudHSMV2 requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="cloudhsmv2")

    @property
    def cloudhsmv2_backend(self) -> CloudHSMV2Backend:
        """Return backend instance specific for this region."""
        return cloudhsmv2_backends[self.current_account][self.region]

    def list_tags(self) -> str:
        params = json.loads(self.body)

        resource_id = params.get("ResourceId")
        next_token = params.get("NextToken")
        max_results = params.get("MaxResults")

        tag_list, next_token = self.cloudhsmv2_backend.list_tags(
            resource_id=resource_id,
            next_token=next_token,
            max_results=max_results,
        )

        return json.dumps({"TagList": tag_list, "NextToken": next_token})

    def tag_resource(self) -> str:
        params = json.loads(self.body)

        resource_id = params.get("ResourceId")
        tag_list = params.get("TagList")

        self.cloudhsmv2_backend.tag_resource(
            resource_id=resource_id,
            tag_list=tag_list,
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)

        resource_id = params.get("ResourceId")
        tag_key_list = params.get("TagKeyList")
        self.cloudhsmv2_backend.untag_resource(
            resource_id=resource_id,
            tag_key_list=tag_key_list,
        )
        return json.dumps({})

    def create_cluster(self) -> str:
        backup_retention_policy = self._get_param("BackupRetentionPolicy", {})
        hsm_type = self._get_param("HsmType")
        source_backup_id = self._get_param("SourceBackupId")
        subnet_ids = self._get_param("SubnetIds", [])
        network_type = self._get_param("NetworkType")
        tag_list = self._get_param("TagList")
        mode = self._get_param("Mode")

        cluster = self.cloudhsmv2_backend.create_cluster(
            backup_retention_policy=backup_retention_policy,
            hsm_type=hsm_type,
            source_backup_id=source_backup_id,
            subnet_ids=subnet_ids,
            network_type=network_type,
            tag_list=tag_list,
            mode=mode,
        )
        return json.dumps({"Cluster": cluster}, cls=DateTimeEncoder)

    def delete_cluster(self) -> str:
        params = json.loads(self.body)

        cluster_id = params.get("ClusterId")

        cluster = self.cloudhsmv2_backend.delete_cluster(cluster_id=cluster_id)
        return json.dumps({"Cluster": cluster}, cls=DateTimeEncoder)

    def describe_clusters(self) -> str:
        params = json.loads(self.body)

        filters = params.get("Filters", {})
        next_token = params.get("NextToken")
        max_results = params.get("MaxResults")

        clusters, next_token = self.cloudhsmv2_backend.describe_clusters(
            filters=filters,
            next_token=next_token,
            max_results=max_results,
        )

        response = {"Clusters": clusters, "NextToken": next_token}

        return json.dumps(response, cls=DateTimeEncoder)

    def get_resource_policy(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        policy = self.cloudhsmv2_backend.get_resource_policy(
            resource_arn=resource_arn,
        )
        return json.dumps({"Policy": policy})

    def describe_backups(self) -> str:
        params = json.loads(self.body)

        next_token = params.get("NextToken")
        max_results = params.get("MaxResults")
        filters_raw = params.get("Filters", {})
        filters = (
            json.loads(filters_raw) if isinstance(filters_raw, str) else filters_raw
        )
        shared = params.get("Shared")
        sort_ascending = params.get("SortAscending")

        backups, next_token = self.cloudhsmv2_backend.describe_backups(
            next_token=next_token,
            max_results=max_results,
            filters=filters,
            shared=shared,
            sort_ascending=sort_ascending,
        )

        response = {"Backups": [b.to_dict() for b in backups], "NextToken": next_token}

        return json.dumps(response, cls=DateTimeEncoder)

    def put_resource_policy(self) -> str:
        params = json.loads(self.body)

        resource_arn = params.get("ResourceArn")
        policy = params.get("Policy")

        result = self.cloudhsmv2_backend.put_resource_policy(
            resource_arn=resource_arn,
            policy=policy,
        )
        return json.dumps(result)

    def delete_resource_policy(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        result = self.cloudhsmv2_backend.delete_resource_policy(
            resource_arn=resource_arn,
        )
        return json.dumps(result)

    def create_hsm(self) -> str:
        params = json.loads(self.body)
        cluster_id = params.get("ClusterId")
        availability_zone = params.get("AvailabilityZone")
        ip_address = params.get("IpAddress")

        hsm = self.cloudhsmv2_backend.create_hsm(
            cluster_id=cluster_id,
            availability_zone=availability_zone,
            ip_address=ip_address,
        )
        return json.dumps({"Hsm": hsm})

    def delete_hsm(self) -> str:
        params = json.loads(self.body)
        cluster_id = params.get("ClusterId")
        hsm_id = params.get("HsmId")
        eni_id = params.get("EniId")
        eni_ip = params.get("EniIp")

        deleted_hsm_id = self.cloudhsmv2_backend.delete_hsm(
            cluster_id=cluster_id,
            hsm_id=hsm_id,
            eni_id=eni_id,
            eni_ip=eni_ip,
        )
        return json.dumps({"HsmId": deleted_hsm_id})

    def delete_backup(self) -> str:
        params = json.loads(self.body)
        backup_id = params.get("BackupId")

        backup = self.cloudhsmv2_backend.delete_backup(backup_id=backup_id)
        return json.dumps({"Backup": backup.to_dict()}, cls=DateTimeEncoder)

    def copy_backup_to_region(self) -> str:
        params = json.loads(self.body)
        destination_region = params.get("DestinationRegion")
        backup_id = params.get("BackupId")
        tag_list = params.get("TagList")

        result = self.cloudhsmv2_backend.copy_backup_to_region(
            destination_region=destination_region,
            backup_id=backup_id,
            tag_list=tag_list,
        )
        return json.dumps(result, cls=DateTimeEncoder)

    def initialize_cluster(self) -> str:
        params = json.loads(self.body)
        cluster_id = params.get("ClusterId")
        signed_cert = params.get("SignedCert")
        trust_anchor = params.get("TrustAnchor")

        result = self.cloudhsmv2_backend.initialize_cluster(
            cluster_id=cluster_id,
            signed_cert=signed_cert,
            trust_anchor=trust_anchor,
        )
        return json.dumps(result)

    def modify_backup_attributes(self) -> str:
        params = json.loads(self.body)
        backup_id = params.get("BackupId")
        never_expires = params.get("NeverExpires")

        backup = self.cloudhsmv2_backend.modify_backup_attributes(
            backup_id=backup_id,
            never_expires=never_expires,
        )
        return json.dumps({"Backup": backup.to_dict()}, cls=DateTimeEncoder)

    def modify_cluster(self) -> str:
        params = json.loads(self.body)
        cluster_id = params.get("ClusterId")
        backup_retention_policy = params.get("BackupRetentionPolicy")
        hsm_type = params.get("HsmType")

        cluster = self.cloudhsmv2_backend.modify_cluster(
            cluster_id=cluster_id,
            backup_retention_policy=backup_retention_policy,
            hsm_type=hsm_type,
        )
        return json.dumps({"Cluster": cluster}, cls=DateTimeEncoder)

    def restore_backup(self) -> str:
        params = json.loads(self.body)
        backup_id = params.get("BackupId")

        backup = self.cloudhsmv2_backend.restore_backup(backup_id=backup_id)
        return json.dumps({"Backup": backup.to_dict()}, cls=DateTimeEncoder)
