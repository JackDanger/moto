"""Handles incoming dsql requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.responses import ActionResult, BaseResponse

from .models import AuroraDSQLBackend, dsql_backends


class AuroraDSQLResponse(BaseResponse):
    """Handler for AuroraDSQL requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="dsql")

    @property
    def dsql_backend(self) -> AuroraDSQLBackend:
        """Return backend instance specific for this region."""
        return dsql_backends[self.current_account][self.region]

    def create_cluster(self) -> ActionResult:
        params = json.loads(self.body)
        deletion_protection_enabled = params.get("deletionProtectionEnabled", True)
        tags = params.get("tags")
        client_token = params.get("clientToken")
        cluster = self.dsql_backend.create_cluster(
            deletion_protection_enabled=deletion_protection_enabled,
            tags=tags,
            client_token=client_token,
        )
        return ActionResult(cluster)

    def delete_cluster(self) -> ActionResult:
        identifier = self.path.split("/")[-1]
        cluster = self.dsql_backend.delete_cluster(identifier=identifier)
        result = {
            "identifier": cluster.identifier,
            "arn": cluster.arn,
            "status": "DELETING",
            "creationTime": cluster.creation_time,
        }
        return ActionResult(result)

    def get_cluster(self) -> ActionResult:
        identifier = self.path.split("/")[-1]
        cluster = self.dsql_backend.get_cluster(identifier=identifier)
        return ActionResult(cluster)

    def get_vpc_endpoint_service_name(self) -> ActionResult:
        identifier = self.path.split("/")[-2]
        result = self.dsql_backend.get_vpc_endpoint_service_name(identifier)
        return ActionResult(result)

    def list_tags_for_resource(self) -> ActionResult:
        arn = unquote(self.path.split("/")[-1])
        identifier = arn.split("/")[-1]
        tags = self.dsql_backend.list_tags_for_resource(identifier)
        return ActionResult({"tags": tags})

    def list_clusters(self) -> ActionResult:
        clusters = self.dsql_backend.list_clusters()
        return ActionResult({"clusters": clusters, "nextToken": None})

    def update_cluster(self) -> ActionResult:
        identifier = self.path.split("/")[-1]
        params = json.loads(self.body) if self.body else {}
        deletion_protection_enabled = params.get("deletionProtectionEnabled")
        client_token = params.get("clientToken")
        cluster = self.dsql_backend.update_cluster(
            identifier=identifier,
            deletion_protection_enabled=deletion_protection_enabled,
            client_token=client_token,
        )
        return ActionResult(cluster)

    def get_cluster_policy(self) -> ActionResult:
        # path: /cluster/{identifier}/policy
        parts = self.path.split("/")
        identifier = parts[-2]
        policy = self.dsql_backend.get_cluster_policy(identifier=identifier)
        return ActionResult({"policy": policy or ""})

    def put_cluster_policy(self) -> ActionResult:
        parts = self.path.split("/")
        identifier = parts[-2]
        params = json.loads(self.body) if self.body else {}
        policy = params.get("policy", "")
        result = self.dsql_backend.put_cluster_policy(
            identifier=identifier, policy=policy
        )
        return ActionResult({"policy": result})

    def delete_cluster_policy(self) -> ActionResult:
        parts = self.path.split("/")
        identifier = parts[-2]
        self.dsql_backend.delete_cluster_policy(identifier=identifier)
        return ActionResult({})

    def tag_resource(self) -> ActionResult:
        arn = unquote(self.path.split("/", 2)[-1])
        identifier = arn.split("/")[-1]
        params = json.loads(self.body) if self.body else {}
        tags = params.get("tags", {})
        self.dsql_backend.tag_resource(identifier=identifier, tags=tags)
        return ActionResult({})

    def untag_resource(self) -> ActionResult:
        arn = unquote(self.path.split("/", 2)[-1])
        identifier = arn.split("/")[-1]
        tag_keys = self.querystring.get("tagKeys", [])
        self.dsql_backend.untag_resource(identifier=identifier, tag_keys=tag_keys)
        return ActionResult({})
