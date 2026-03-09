import json
from typing import Any
from urllib.parse import parse_qs

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import GlacierBackend, glacier_backends
from .utils import vault_from_glacier_url


class GlacierResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="glacier")

    def setup_class(
        self, request: Any, full_url: str, headers: Any, use_raw_body: bool = False
    ) -> None:
        super().setup_class(request, full_url, headers, use_raw_body=True)

    def _get_action(self) -> str:
        """Override action resolution to handle Glacier's query-string-based routing.

        Glacier uses ?operation=add and ?operation=remove query params to distinguish
        AddTagsToVault from RemoveTagsFromVault, which share the same path and method.
        The base class regex matching can't handle these static query params.
        """
        # Check for the special query-string-based operations first
        qs = parse_qs(self.parsed_url.query)
        operation = qs.get("operation", [None])[0]
        path = self.parsed_url.path

        if path.endswith("/tags") and operation == "add":
            return "AddTagsToVault"
        if path.endswith("/tags") and operation == "remove":
            return "RemoveTagsFromVault"

        # Fall back to the default action resolution
        return super()._get_action()

    @property
    def glacier_backend(self) -> GlacierBackend:
        return glacier_backends[self.current_account][self.region]

    def list_vaults(self) -> TYPE_RESPONSE:
        vaults = self.glacier_backend.list_vaults()
        response = json.dumps(
            {"Marker": None, "VaultList": [vault.to_dict() for vault in vaults]}
        )

        headers = {"content-type": "application/json"}
        return 200, headers, response

    def describe_vault(self) -> TYPE_RESPONSE:
        vault_name = vault_from_glacier_url(self.uri)
        vault = self.glacier_backend.describe_vault(vault_name)
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps(vault.to_dict())

    def create_vault(self) -> TYPE_RESPONSE:
        vault_name = vault_from_glacier_url(self.uri)
        self.glacier_backend.create_vault(vault_name)
        return 201, {"status": 201}, ""

    def delete_vault(self) -> TYPE_RESPONSE:
        vault_name = vault_from_glacier_url(self.uri)
        self.glacier_backend.delete_vault(vault_name)
        return 204, {"status": 204}, ""

    def upload_archive(self) -> TYPE_RESPONSE:
        description = self.headers.get("x-amz-archive-description") or ""
        vault_name = self.parsed_url.path.split("/")[-2]
        vault = self.glacier_backend.upload_archive(vault_name, self.body, description)
        headers = {
            "x-amz-archive-id": vault["archive_id"],
            "x-amz-sha256-tree-hash": vault["sha256"],
            "status": 201,
        }
        return 201, headers, ""

    def delete_archive(self) -> TYPE_RESPONSE:
        vault_name = self.parsed_url.path.split("/")[-3]
        archive_id = self.parsed_url.path.split("/")[-1]

        self.glacier_backend.delete_archive(vault_name, archive_id)
        return 204, {"status": 204}, ""

    def list_jobs(self) -> TYPE_RESPONSE:
        vault_name = self.parsed_url.path.split("/")[-2]
        jobs = self.glacier_backend.list_jobs(vault_name)
        headers = {"content-type": "application/json"}
        response = json.dumps(
            {"JobList": [job.to_dict() for job in jobs], "Marker": None}
        )
        return 200, headers, response

    def initiate_job(self) -> TYPE_RESPONSE:
        account_id = self.uri.split("/")[1]
        vault_name = self.parsed_url.path.split("/")[-2]
        body_bytes = self.body if isinstance(self.body, bytes) else self.body.encode("utf-8")
        json_body = json.loads(body_bytes)
        job_type = json_body.get("Type", "inventory-retrieval")
        archive_id = json_body.get("ArchiveId")
        tier = json_body.get("Tier") or "Standard"
        job_id = self.glacier_backend.initiate_job(
            vault_name, job_type, tier, archive_id
        )
        headers = {
            "x-amz-job-id": job_id,
            "Location": f"/{account_id}/vaults/{vault_name}/jobs/{job_id}",
            "status": 202,
        }
        return 202, headers, ""

    def describe_job(self) -> str:
        vault_name = self.parsed_url.path.split("/")[-3]
        archive_id = self.parsed_url.path.split("/")[-1]

        job = self.glacier_backend.describe_job(vault_name, archive_id)
        return json.dumps(job.to_dict())  # type: ignore

    def get_job_output(self) -> TYPE_RESPONSE:
        vault_name = self.parsed_url.path.split("/")[-4]
        job_id = self.parsed_url.path.split("/")[-2]
        output = self.glacier_backend.get_job_output(vault_name, job_id)
        if output is None:
            return 404, {"status": 404}, "404 Not Found"
        if isinstance(output, dict):
            headers = {"content-type": "application/json"}
            return 200, headers, json.dumps(output)
        else:
            headers = {"content-type": "application/octet-stream"}
            return 200, headers, output

    # --- Data Retrieval Policy ---

    def get_data_retrieval_policy(self) -> TYPE_RESPONSE:
        result = self.glacier_backend.get_data_retrieval_policy()
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps(result)

    def set_data_retrieval_policy(self) -> TYPE_RESPONSE:
        body_bytes = self.body if isinstance(self.body, bytes) else self.body.encode("utf-8")
        json_body = json.loads(body_bytes)
        policy = json_body.get("Policy", {})
        self.glacier_backend.set_data_retrieval_policy(policy)
        return 204, {"status": 204}, ""

    # --- Tags ---

    def add_tags_to_vault(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        body_bytes = self.body if isinstance(self.body, bytes) else self.body.encode("utf-8")
        json_body = json.loads(body_bytes)
        tags = json_body.get("Tags", {})
        self.glacier_backend.add_tags_to_vault(vault_name, tags)
        return 204, {"status": 204}, ""

    def remove_tags_from_vault(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        body_bytes = self.body if isinstance(self.body, bytes) else self.body.encode("utf-8")
        json_body = json.loads(body_bytes)
        tag_keys = json_body.get("TagKeys", [])
        self.glacier_backend.remove_tags_from_vault(vault_name, tag_keys)
        return 204, {"status": 204}, ""

    def list_tags_for_vault(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        tags = self.glacier_backend.list_tags_for_vault(vault_name)
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps({"Tags": tags})

    # --- Vault Notifications ---

    def set_vault_notifications(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        body_bytes = self.body if isinstance(self.body, bytes) else self.body.encode("utf-8")
        json_body = json.loads(body_bytes)
        config = json_body.get("vaultNotificationConfig", json_body)
        self.glacier_backend.set_vault_notifications(vault_name, config)
        return 204, {"status": 204}, ""

    def get_vault_notifications(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        config = self.glacier_backend.get_vault_notifications(vault_name)
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps({"vaultNotificationConfig": config})

    def delete_vault_notifications(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        self.glacier_backend.delete_vault_notifications(vault_name)
        return 204, {"status": 204}, ""

    # --- Vault Access Policy ---

    def set_vault_access_policy(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        body_bytes = self.body if isinstance(self.body, bytes) else self.body.encode("utf-8")
        json_body = json.loads(body_bytes)
        policy_obj = json_body.get("policy", json_body)
        policy_str = policy_obj.get("Policy", "") if isinstance(policy_obj, dict) else str(policy_obj)
        self.glacier_backend.set_vault_access_policy(vault_name, policy_str)
        return 204, {"status": 204}, ""

    def get_vault_access_policy(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        policy = self.glacier_backend.get_vault_access_policy(vault_name)
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps({"policy": {"Policy": policy}})

    def delete_vault_access_policy(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        self.glacier_backend.delete_vault_access_policy(vault_name)
        return 204, {"status": 204}, ""

    # --- Vault Lock ---

    def initiate_vault_lock(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        body_bytes = self.body if isinstance(self.body, bytes) else self.body.encode("utf-8")
        json_body = json.loads(body_bytes)
        lock_id = self.glacier_backend.initiate_vault_lock(vault_name, json_body)
        headers = {
            "x-amz-lock-id": lock_id,
            "status": 201,
        }
        return 201, headers, ""

    def get_vault_lock(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        lock = self.glacier_backend.get_vault_lock(vault_name)
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps(lock)

    def complete_vault_lock(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        lock_id = self.parsed_url.path.split("/")[-1]
        self.glacier_backend.complete_vault_lock(vault_name, lock_id)
        return 204, {"status": 204}, ""

    def abort_vault_lock(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        self.glacier_backend.abort_vault_lock(vault_name)
        return 204, {"status": 204}, ""

    # --- Provisioned Capacity ---

    def list_provisioned_capacity(self) -> TYPE_RESPONSE:
        caps = self.glacier_backend.list_provisioned_capacity()
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps({"ProvisionedCapacityList": caps})

    def purchase_provisioned_capacity(self) -> TYPE_RESPONSE:
        result = self.glacier_backend.purchase_provisioned_capacity()
        headers = {
            "x-amz-capacity-id": result["capacityId"],
            "status": 201,
        }
        return 201, headers, ""

    # --- Multipart Upload ---

    def initiate_multipart_upload(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        part_size = int(self.headers.get("x-amz-part-size", "1048576"))
        description = self.headers.get("x-amz-archive-description", "")
        upload_id = self.glacier_backend.initiate_multipart_upload(
            vault_name, part_size, description
        )
        account_id = self.parsed_url.path.split("/")[1]
        headers = {
            "x-amz-multipart-upload-id": upload_id,
            "Location": f"/{account_id}/vaults/{vault_name}/multipart-uploads/{upload_id}",
            "status": 201,
        }
        return 201, headers, ""

    def upload_multipart_part(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        upload_id = self.parsed_url.path.split("/")[-1]
        range_header = self.headers.get("Content-Range", "")
        sha256 = self.glacier_backend.upload_multipart_part(
            vault_name, upload_id, range_header, self.body
        )
        headers = {
            "x-amz-sha256-tree-hash": sha256,
            "status": 204,
        }
        return 204, headers, ""

    def complete_multipart_upload(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        upload_id = self.parsed_url.path.split("/")[-1]
        archive_size = int(self.headers.get("x-amz-archive-size", "0"))
        archive = self.glacier_backend.complete_multipart_upload(
            vault_name, upload_id, archive_size
        )
        headers = {
            "x-amz-archive-id": archive["archive_id"],
            "x-amz-sha256-tree-hash": archive["sha256"],
            "Location": f"/{self.parsed_url.path.split('/')[1]}/vaults/{vault_name}/archives/{archive['archive_id']}",
            "status": 201,
        }
        return 201, headers, ""

    def abort_multipart_upload(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        upload_id = self.parsed_url.path.split("/")[-1]
        self.glacier_backend.abort_multipart_upload(vault_name, upload_id)
        return 204, {"status": 204}, ""

    def list_multipart_uploads(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        uploads = self.glacier_backend.list_multipart_uploads(vault_name)
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps(
            {"Marker": None, "UploadsList": uploads}
        )

    def list_parts(self) -> TYPE_RESPONSE:
        vault_name = self._vault_name_from_path()
        upload_id = self.parsed_url.path.split("/")[-1]
        result = self.glacier_backend.list_parts(vault_name, upload_id)
        headers = {"content-type": "application/json"}
        return 200, headers, json.dumps(result)

    # --- Helpers ---

    def _vault_name_from_path(self) -> str:
        """Extract vault name from URL path.

        Handles various URL patterns:
        - /{account}/vaults/{vault}/tags
        - /{account}/vaults/{vault}/notification-configuration
        - /{account}/vaults/{vault}/access-policy
        - /{account}/vaults/{vault}/lock-policy
        - /{account}/vaults/{vault}/lock-policy/{lockId}
        - /{account}/vaults/{vault}/multipart-uploads
        - /{account}/vaults/{vault}/multipart-uploads/{uploadId}
        """
        parts = self.parsed_url.path.split("/")
        # Find "vaults" in path and return the next segment
        for i, part in enumerate(parts):
            if part == "vaults" and i + 1 < len(parts):
                return parts[i + 1]
        return parts[-1]
