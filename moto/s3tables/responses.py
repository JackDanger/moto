"""Handles incoming s3tables requests, invokes methods, returns responses."""

import json
from typing import Any
from urllib.parse import unquote

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import S3TablesBackend, s3tables_backends


def _parse_path(raw_path: str, n_tail: int) -> tuple:
    """Parse an s3tables URL path, handling ARNs that may contain '/'.

    The path format is /{prefix}/{arn}[/{tail_1}/.../{tail_n}].
    The ARN (e.g. arn:aws:s3tables:us-east-1:123456789012:bucket/name)
    contains a '/' that may or may not be percent-encoded depending on
    the HTTP framework.  We parse from the right to safely extract the
    tail segments, leaving the ARN intact.

    Args:
        raw_path: The request path (may have encoded or decoded ARN slashes).
        n_tail: Number of path segments *after* the ARN (0, 1, 2, or 3).

    Returns:
        A tuple of (table_bucket_arn, *tail_segments) where
        table_bucket_arn has been URL-decoded.
    """
    # Strip leading '/' and the first segment (prefix like "namespaces" or "tables")
    path = raw_path.lstrip("/")
    _, _, rest = path.partition("/")

    if n_tail == 0:
        return (unquote(rest),)

    parts = rest.rsplit("/", n_tail)
    # parts[0] is the (possibly encoded) ARN, parts[1:] are the tail segments
    return (unquote(parts[0]),) + tuple(parts[1:])


class S3TablesResponse(BaseResponse):
    """Handler for S3Tables requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="s3tables")
        self.default_response_headers = {"Content-Type": "application/json"}

    @property
    def s3tables_backend(self) -> S3TablesBackend:
        """Return backend instance specific for this region."""
        return s3tables_backends[self.current_account][self.region]

    def create_table_bucket(self) -> TYPE_RESPONSE:
        name = json.loads(self.body)["name"]
        bucket = self.s3tables_backend.create_table_bucket(
            name=name,
        )
        return 200, self.default_response_headers, json.dumps({"arn": bucket.arn})

    def list_table_buckets(self) -> TYPE_RESPONSE:
        params = self._get_params()
        prefix = params.get("prefix")
        continuation_token = params.get("continuationToken")
        max_buckets = params.get("maxBuckets")
        table_buckets, continuation_token = self.s3tables_backend.list_table_buckets(
            prefix=prefix,
            continuation_token=continuation_token,
            max_buckets=int(max_buckets) if max_buckets else None,
        )

        body: dict[str, Any] = {
            "tableBuckets": [
                {
                    "arn": b.arn,
                    "name": b.name,
                    "ownerAccountId": b.account_id,
                    "createdAt": b.creation_date.isoformat(),
                }
                for b in table_buckets
            ]
        }
        if continuation_token:
            body.update(continuationToken=continuation_token)

        return 200, self.default_response_headers, json.dumps(body)

    def get_table_bucket(self) -> TYPE_RESPONSE:
        (table_bucket_arn,) = _parse_path(self.raw_path, 0)
        bucket = self.s3tables_backend.get_table_bucket(
            table_bucket_arn=table_bucket_arn,
        )

        return (
            200,
            self.default_response_headers,
            json.dumps(
                {
                    "arn": bucket.arn,
                    "name": bucket.name,
                    "ownerAccountId": bucket.account_id,
                    "createdAt": bucket.creation_date.isoformat(),
                }
            ),
        )

    def delete_table_bucket(self) -> TYPE_RESPONSE:
        (table_bucket_arn,) = _parse_path(self.raw_path, 0)
        self.s3tables_backend.delete_table_bucket(
            table_bucket_arn=table_bucket_arn,
        )

        return 204, {}, ""

    def create_namespace(self) -> TYPE_RESPONSE:
        (table_bucket_arn,) = _parse_path(self.raw_path, 0)
        name = json.loads(self.body)["namespace"][0]
        namespace = self.s3tables_backend.create_namespace(
            table_bucket_arn=table_bucket_arn,
            namespace=name,
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(
                {"tableBucketArn": table_bucket_arn, "namespace": [namespace.name]}
            ),
        )

    def list_namespaces(self) -> TYPE_RESPONSE:
        (table_bucket_arn,) = _parse_path(self.raw_path, 0)

        params = self._get_params()
        continuation_token = params.get("continuationToken")
        max_namespaces = params.get("maxNamespaces")
        prefix = params.get("prefix")

        namespaces, continuation_token = self.s3tables_backend.list_namespaces(
            table_bucket_arn=table_bucket_arn,
            prefix=prefix,
            continuation_token=continuation_token,
            max_namespaces=int(max_namespaces) if max_namespaces else None,
        )

        body: dict[str, Any] = {
            "namespaces": [
                {
                    "namespace": [ns.name],
                    "createdAt": ns.creation_date.isoformat(),
                    "createdBy": ns.created_by,
                    "ownerAccountId": ns.account_id,
                }
                for ns in namespaces
            ]
        }
        if continuation_token:
            body.update(continuationToken=continuation_token)

        return 200, self.default_response_headers, json.dumps(body)

    def get_namespace(self) -> TYPE_RESPONSE:
        table_bucket_arn, name = _parse_path(self.raw_path, 1)
        namespace = self.s3tables_backend.get_namespace(
            table_bucket_arn=table_bucket_arn,
            namespace=name,
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(
                {
                    "namespace": [namespace.name],
                    "createdAt": namespace.creation_date.isoformat(),
                    "createdBy": namespace.created_by,
                    "ownerAccountId": namespace.account_id,
                }
            ),
        )

    def delete_namespace(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace = _parse_path(self.raw_path, 1)
        self.s3tables_backend.delete_namespace(
            table_bucket_arn=table_bucket_arn,
            namespace=namespace,
        )
        return 204, self.default_response_headers, ""

    def create_table(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace = _parse_path(self.raw_path, 1)
        body = json.loads(self.body)
        name = body["name"]
        format = body["format"]
        table = self.s3tables_backend.create_table(
            table_bucket_arn=table_bucket_arn,
            namespace=namespace,
            name=name,
            format=format,
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"tableARN": table.arn, "versionToken": table.version_token}),
        )

    def get_table(self) -> TYPE_RESPONSE:
        table_bucket_arn = unquote(self._get_param("tableBucketARN"))
        namespace = self._get_param("namespace")
        name = self._get_param("name")
        table = self.s3tables_backend.get_table(
            table_bucket_arn=table_bucket_arn,
            namespace=namespace,
            name=name,
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(
                {
                    "name": table.name,
                    "type": table.type,
                    "tableARN": table.arn,
                    "namespace": [namespace],
                    "versionToken": table.version_token,
                    "metadataLocation": table.metadata_location,
                    "warehouseLocation": table.warehouse_location,
                    "createdAt": table.creation_date.isoformat(),
                    "createdBy": table.account_id,
                    "managedByService": table.managed_by_service,
                    "modifiedAt": table.last_modified.isoformat(),
                    "modifiedBy": table.modified_by,
                    "ownerAccountId": table.account_id,
                    "format": table.format,
                }
            ),
        )

    def list_tables(self) -> TYPE_RESPONSE:
        (table_bucket_arn,) = _parse_path(self.raw_path, 0)
        params = self._get_params()
        namespace = params.get("namespace")
        prefix = params.get("prefix")
        continuation_token = params.get("continuationToken")
        max_tables = params.get("maxTables")
        tables, continuation_token = self.s3tables_backend.list_tables(
            table_bucket_arn=table_bucket_arn,
            namespace=namespace,
            prefix=prefix,
            continuation_token=continuation_token,
            max_tables=int(max_tables) if max_tables else None,
        )
        body: dict[str, Any] = {
            "tables": [
                {
                    "namespace": [table.namespace],
                    "name": table.name,
                    "createdAt": table.creation_date.isoformat(),
                    "modifiedAt": table.last_modified.isoformat(),
                }
                for table in tables
            ]
        }

        if continuation_token:
            body.update(continuationToken=continuation_token)

        return 200, self.default_response_headers, json.dumps(body)

    def delete_table(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name = _parse_path(self.raw_path, 2)
        params = self._get_params()
        version_token = params.get("versionToken")
        self.s3tables_backend.delete_table(
            table_bucket_arn=table_bucket_arn,
            namespace=namespace,
            name=name,
            version_token=version_token,
        )
        return 204, {}, ""

    def get_table_metadata_location(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        table = self.s3tables_backend.get_table(
            table_bucket_arn=table_bucket_arn,
            namespace=namespace,
            name=name,
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(
                {
                    "versionToken": table.version_token,
                    "metadataLocation": table.metadata_location,
                    "warehouseLocation": table.warehouse_location,
                }
            ),
        )

    def update_table_metadata_location(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        body = json.loads(self.body)
        metadata_location = body["metadataLocation"]
        version_token = body["versionToken"]
        table = self.s3tables_backend.update_table_metadata_location(
            table_bucket_arn=table_bucket_arn,
            namespace=namespace,
            name=name,
            version_token=version_token,
            metadata_location=metadata_location,
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(
                {
                    "name": table.name,
                    "tableArn": table.arn,
                    "namespace": namespace,
                    "versionToken": table.version_token,
                    "metadataLocation": table.metadata_location,
                }
            ),
        )

    def rename_table(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        body = json.loads(self.body)
        version_token = body.get("versionToken")
        new_namespace_name = body.get("newNamespaceName")
        new_name = body.get("newName")
        self.s3tables_backend.rename_table(
            table_bucket_arn=table_bucket_arn,
            namespace=namespace,
            name=name,
            new_namespace_name=new_namespace_name,
            new_name=new_name,
            version_token=version_token,
        )
        return 200, {}, ""

    # --- Table Bucket Policy ---

    def get_table_bucket_policy(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        policy = self.s3tables_backend.get_table_bucket_policy(table_bucket_arn)
        return (
            200,
            self.default_response_headers,
            json.dumps({"resourcePolicy": policy}),
        )

    def put_table_bucket_policy(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        body = json.loads(self.body)
        self.s3tables_backend.put_table_bucket_policy(
            table_bucket_arn, body["resourcePolicy"]
        )
        return 200, self.default_response_headers, json.dumps({})

    def delete_table_bucket_policy(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        self.s3tables_backend.delete_table_bucket_policy(table_bucket_arn)
        return 204, {}, ""

    # --- Table Bucket Maintenance Configuration ---

    def get_table_bucket_maintenance_configuration(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        config = self.s3tables_backend.get_table_bucket_maintenance_configuration(
            table_bucket_arn
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(
                {"tableBucketARN": table_bucket_arn, "configuration": config}
            ),
        )

    def put_table_bucket_maintenance_configuration(self) -> TYPE_RESPONSE:
        # URL: /buckets/{arn}/maintenance/{type}
        table_bucket_arn, _, config_type = _parse_path(self.raw_path, 2)
        body = json.loads(self.body)
        value = body.get("value", {})
        self.s3tables_backend.put_table_bucket_maintenance_configuration(
            table_bucket_arn, config_type, value
        )
        return 204, {}, ""

    # --- Table Bucket Encryption ---

    def get_table_bucket_encryption(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        config = self.s3tables_backend.get_table_bucket_encryption(table_bucket_arn)
        return (
            200,
            self.default_response_headers,
            json.dumps({"encryptionConfiguration": config}),
        )

    def put_table_bucket_encryption(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        body = json.loads(self.body)
        self.s3tables_backend.put_table_bucket_encryption(
            table_bucket_arn, body["encryptionConfiguration"]
        )
        return 200, self.default_response_headers, json.dumps({})

    def delete_table_bucket_encryption(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        self.s3tables_backend.delete_table_bucket_encryption(table_bucket_arn)
        return 204, {}, ""

    # --- Table Bucket Metrics Configuration ---

    def get_table_bucket_metrics_configuration(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        metrics_id = self.s3tables_backend.get_table_bucket_metrics_configuration(
            table_bucket_arn
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(
                {"tableBucketARN": table_bucket_arn, "id": metrics_id or ""}
            ),
        )

    def put_table_bucket_metrics_configuration(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        self.s3tables_backend.put_table_bucket_metrics_configuration(table_bucket_arn)
        return 204, {}, ""

    def delete_table_bucket_metrics_configuration(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        self.s3tables_backend.delete_table_bucket_metrics_configuration(
            table_bucket_arn
        )
        return 204, {}, ""

    # --- Table Bucket Storage Class ---

    def get_table_bucket_storage_class(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        config = self.s3tables_backend.get_table_bucket_storage_class(table_bucket_arn)
        return (
            200,
            self.default_response_headers,
            json.dumps({"storageClassConfiguration": config}),
        )

    def put_table_bucket_storage_class(self) -> TYPE_RESPONSE:
        table_bucket_arn, _ = _parse_path(self.raw_path, 1)
        body = json.loads(self.body)
        self.s3tables_backend.put_table_bucket_storage_class(
            table_bucket_arn, body["storageClassConfiguration"]
        )
        return 200, self.default_response_headers, json.dumps({})

    # --- Table Bucket Replication ---

    def get_table_bucket_replication(self) -> TYPE_RESPONSE:
        params = self._get_params()
        table_bucket_arn = unquote(params["tableBucketARN"])
        version_token, config = self.s3tables_backend.get_table_bucket_replication(
            table_bucket_arn
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"versionToken": version_token, "configuration": config}),
        )

    def put_table_bucket_replication(self) -> TYPE_RESPONSE:
        body = json.loads(self.body)
        table_bucket_arn = body["tableBucketARN"]
        version_token, status = self.s3tables_backend.put_table_bucket_replication(
            table_bucket_arn=table_bucket_arn,
            version_token=body.get("versionToken"),
            configuration=body["configuration"],
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"versionToken": version_token, "status": status}),
        )

    def delete_table_bucket_replication(self) -> TYPE_RESPONSE:
        params = self._get_params()
        table_bucket_arn = unquote(params["tableBucketARN"])
        version_token = params.get("versionToken")
        self.s3tables_backend.delete_table_bucket_replication(
            table_bucket_arn, version_token
        )
        return 204, {}, ""

    # --- Table Policy ---

    def get_table_policy(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        policy = self.s3tables_backend.get_table_policy(
            table_bucket_arn, namespace, name
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"resourcePolicy": policy}),
        )

    def put_table_policy(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        body = json.loads(self.body)
        self.s3tables_backend.put_table_policy(
            table_bucket_arn, namespace, name, body["resourcePolicy"]
        )
        return 200, self.default_response_headers, json.dumps({})

    def delete_table_policy(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        self.s3tables_backend.delete_table_policy(
            table_bucket_arn, namespace, name
        )
        return 204, {}, ""

    # --- Table Maintenance Configuration ---

    def get_table_maintenance_configuration(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        table_arn, config = self.s3tables_backend.get_table_maintenance_configuration(
            table_bucket_arn, namespace, name
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"tableARN": table_arn, "configuration": config}),
        )

    def put_table_maintenance_configuration(self) -> TYPE_RESPONSE:
        # URL: /tables/{arn}/{ns}/{name}/maintenance/{type}
        table_bucket_arn, namespace, name, _, config_type = _parse_path(
            self.raw_path, 4
        )
        body = json.loads(self.body)
        value = body.get("value", {})
        self.s3tables_backend.put_table_maintenance_configuration(
            table_bucket_arn, namespace, name, config_type, value
        )
        return 204, {}, ""

    # --- Table Maintenance Job Status ---

    def get_table_maintenance_job_status(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        table_arn, status = self.s3tables_backend.get_table_maintenance_job_status(
            table_bucket_arn, namespace, name
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"tableARN": table_arn, "status": status}),
        )

    # --- Table Encryption ---

    def get_table_encryption(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        config = self.s3tables_backend.get_table_encryption(
            table_bucket_arn, namespace, name
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"encryptionConfiguration": config}),
        )

    # --- Table Storage Class ---

    def get_table_storage_class(self) -> TYPE_RESPONSE:
        table_bucket_arn, namespace, name, _ = _parse_path(self.raw_path, 3)
        config = self.s3tables_backend.get_table_storage_class(
            table_bucket_arn, namespace, name
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"storageClassConfiguration": config}),
        )

    # --- Table Replication ---

    def get_table_replication(self) -> TYPE_RESPONSE:
        params = self._get_params()
        table_arn = unquote(params["tableArn"])
        version_token, config = self.s3tables_backend.get_table_replication(table_arn)
        return (
            200,
            self.default_response_headers,
            json.dumps({"versionToken": version_token, "configuration": config}),
        )

    def put_table_replication(self) -> TYPE_RESPONSE:
        body = json.loads(self.body)
        table_arn = body["tableArn"]
        version_token, status = self.s3tables_backend.put_table_replication(
            table_arn=table_arn,
            version_token=body.get("versionToken"),
            configuration=body["configuration"],
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"versionToken": version_token, "status": status}),
        )

    def delete_table_replication(self) -> TYPE_RESPONSE:
        params = self._get_params()
        table_arn = unquote(params["tableArn"])
        version_token = params.get("versionToken")
        self.s3tables_backend.delete_table_replication(table_arn, version_token)
        return 204, {}, ""

    # --- Table Replication Status ---

    def get_table_replication_status(self) -> TYPE_RESPONSE:
        params = self._get_params()
        table_arn = unquote(params["tableArn"])
        source_arn, destinations = self.s3tables_backend.get_table_replication_status(
            table_arn
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(
                {"sourceTableArn": source_arn, "destinations": destinations}
            ),
        )

    # --- Table Record Expiration ---

    def get_table_record_expiration_configuration(self) -> TYPE_RESPONSE:
        params = self._get_params()
        table_arn = unquote(params["tableArn"])
        config = self.s3tables_backend.get_table_record_expiration_configuration(
            table_arn
        )
        return (
            200,
            self.default_response_headers,
            json.dumps({"configuration": config or {}}),
        )

    def put_table_record_expiration_configuration(self) -> TYPE_RESPONSE:
        params = self._get_params()
        table_arn = unquote(params["tableArn"])
        body = json.loads(self.body)
        self.s3tables_backend.put_table_record_expiration_configuration(
            table_arn, body.get("value", {})
        )
        return 204, {}, ""

    def get_table_record_expiration_job_status(self) -> TYPE_RESPONSE:
        params = self._get_params()
        table_arn = unquote(params["tableArn"])
        result = self.s3tables_backend.get_table_record_expiration_job_status(
            table_arn
        )
        return (
            200,
            self.default_response_headers,
            json.dumps(result),
        )

    # --- Tagging ---

    def list_tags_for_resource(self) -> TYPE_RESPONSE:
        # URL: /tag/{resourceArn}
        path = self.raw_path.lstrip("/")
        _, _, resource_arn = path.partition("/")
        resource_arn = unquote(resource_arn)
        tags = self.s3tables_backend.list_tags_for_resource(resource_arn)
        return (
            200,
            self.default_response_headers,
            json.dumps({"tags": tags}),
        )

    def tag_resource(self) -> TYPE_RESPONSE:
        path = self.raw_path.lstrip("/")
        _, _, resource_arn = path.partition("/")
        resource_arn = unquote(resource_arn)
        body = json.loads(self.body)
        self.s3tables_backend.tag_resource(resource_arn, body.get("tags", {}))
        return 200, self.default_response_headers, json.dumps({})

    def untag_resource(self) -> TYPE_RESPONSE:
        path = self.raw_path.lstrip("/")
        _, _, resource_arn = path.partition("/")
        resource_arn = unquote(resource_arn)
        params = self._get_params()
        tag_keys = params.get("tagKeys", [])
        if isinstance(tag_keys, str):
            tag_keys = [tag_keys]
        self.s3tables_backend.untag_resource(resource_arn, tag_keys)
        return 204, {}, ""
