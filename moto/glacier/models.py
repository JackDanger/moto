import datetime
import hashlib
import uuid
from typing import Any, Optional, Union

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.exceptions import JsonRESTError
from moto.utilities.utils import get_partition, md5_hash

from .utils import get_job_id


class Job(BaseModel):
    def __init__(self, tier: str):
        self.st = datetime.datetime.now()

        if tier.lower() == "expedited":
            self.et = self.st + datetime.timedelta(seconds=2)
        elif tier.lower() == "bulk":
            self.et = self.st + datetime.timedelta(seconds=10)
        else:
            # Standard
            self.et = self.st + datetime.timedelta(seconds=5)

    def to_dict(self) -> dict[str, Any]:
        return {}


class ArchiveJob(Job):
    def __init__(self, job_id: str, tier: str, arn: str, archive_id: Optional[str]):
        self.job_id = job_id
        self.tier = tier
        self.arn = arn
        self.archive_id = archive_id
        Job.__init__(self, tier)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "Action": "ArchiveRetrieval",
            "ArchiveId": self.archive_id,
            "ArchiveSizeInBytes": 0,
            "ArchiveSHA256TreeHash": None,
            "Completed": False,
            "CreationDate": self.st.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "InventorySizeInBytes": 0,
            "JobDescription": None,
            "JobId": self.job_id,
            "RetrievalByteRange": None,
            "SHA256TreeHash": None,
            "SNSTopic": None,
            "StatusCode": "InProgress",
            "StatusMessage": None,
            "VaultARN": self.arn,
            "Tier": self.tier,
        }
        if datetime.datetime.now() > self.et:
            d["Completed"] = True
            d["CompletionDate"] = self.et.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            d["InventorySizeInBytes"] = 10000
            d["StatusCode"] = "Succeeded"
        return d


class InventoryJob(Job):
    def __init__(self, job_id: str, tier: str, arn: str):
        self.job_id = job_id
        self.tier = tier
        self.arn = arn
        Job.__init__(self, tier)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "Action": "InventoryRetrieval",
            "ArchiveSHA256TreeHash": None,
            "Completed": False,
            "CreationDate": self.st.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "InventorySizeInBytes": 0,
            "JobDescription": None,
            "JobId": self.job_id,
            "RetrievalByteRange": None,
            "SHA256TreeHash": None,
            "SNSTopic": None,
            "StatusCode": "InProgress",
            "StatusMessage": None,
            "VaultARN": self.arn,
            "Tier": self.tier,
        }
        if datetime.datetime.now() > self.et:
            d["Completed"] = True
            d["CompletionDate"] = self.et.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            d["InventorySizeInBytes"] = 10000
            d["StatusCode"] = "Succeeded"
        return d


class MultipartUpload(BaseModel):
    def __init__(
        self,
        vault_name: str,
        upload_id: str,
        part_size: int,
        archive_description: str,
    ):
        self.vault_name = vault_name
        self.upload_id = upload_id
        self.part_size = part_size
        self.archive_description = archive_description
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        self.parts: dict[str, bytes] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "ArchiveDescription": self.archive_description,
            "CreationDate": self.creation_date,
            "MultipartUploadId": self.upload_id,
            "PartSizeInBytes": self.part_size,
            "VaultARN": None,
        }


class Vault(BaseModel):
    def __init__(self, vault_name: str, account_id: str, region: str):
        self.st = datetime.datetime.now()
        self.vault_name = vault_name
        self.region = region
        self.account_id = account_id
        self.archives: dict[str, dict[str, Any]] = {}
        self.jobs: dict[str, Job] = {}
        self.tags: dict[str, str] = {}
        self.notification_configuration: Optional[dict[str, Any]] = None
        self.access_policy: Optional[str] = None
        self.vault_lock: Optional[dict[str, Any]] = None
        self.multipart_uploads: dict[str, MultipartUpload] = {}
        self.arn = f"arn:{get_partition(region)}:glacier:{region}:{account_id}:vaults/{vault_name}"

    def to_dict(self) -> dict[str, Any]:
        archives_size = 0
        for k in self.archives:
            archives_size += self.archives[k]["size"]
        d = {
            "CreationDate": self.st.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "LastInventoryDate": self.st.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "NumberOfArchives": len(self.archives),
            "SizeInBytes": archives_size,
            "VaultARN": self.arn,
            "VaultName": self.vault_name,
        }
        return d

    def create_archive(self, body: bytes, description: str) -> dict[str, Any]:
        archive_id = md5_hash(body).hexdigest()
        self.archives[archive_id] = {}
        self.archives[archive_id]["archive_id"] = archive_id
        self.archives[archive_id]["body"] = body
        self.archives[archive_id]["size"] = len(body)
        self.archives[archive_id]["sha256"] = hashlib.sha256(body).hexdigest()
        self.archives[archive_id]["creation_date"] = datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        self.archives[archive_id]["description"] = description
        return self.archives[archive_id]

    def get_archive_body(self, archive_id: str) -> str:
        return self.archives[archive_id]["body"]

    def get_archive_list(self) -> list[dict[str, Any]]:
        archive_list = []
        for a in self.archives:
            archive = self.archives[a]
            aobj = {
                "ArchiveId": a,
                "ArchiveDescription": archive["description"],
                "CreationDate": archive["creation_date"],
                "Size": archive["size"],
                "SHA256TreeHash": archive["sha256"],
            }
            archive_list.append(aobj)
        return archive_list

    def delete_archive(self, archive_id: str) -> None:
        if archive_id not in self.archives:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message=f"Archive not found: {archive_id}",
            )
        self.archives.pop(archive_id)

    def initiate_job(self, job_type: str, tier: str, archive_id: Optional[str]) -> str:
        job_id = get_job_id()

        if job_type == "inventory-retrieval":
            self.jobs[job_id] = InventoryJob(job_id, tier, self.arn)
        elif job_type == "archive-retrieval":
            self.jobs[job_id] = ArchiveJob(job_id, tier, self.arn, archive_id)

        return job_id

    def list_jobs(self) -> list[Job]:
        return list(self.jobs.values())

    def describe_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def job_ready(self, job_id: str) -> str:
        job = self.describe_job(job_id)
        jobj = job.to_dict()  # type: ignore
        return jobj["Completed"]

    def get_job_output(self, job_id: str) -> Union[str, dict[str, Any]]:
        job = self.describe_job(job_id)
        jobj = job.to_dict()  # type: ignore
        if jobj["Action"] == "InventoryRetrieval":
            archives = self.get_archive_list()
            return {
                "VaultARN": self.arn,
                "InventoryDate": jobj["CompletionDate"],
                "ArchiveList": archives,
            }
        else:
            archive_body = self.get_archive_body(job.archive_id)  # type: ignore
            return archive_body


class GlacierBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.vaults: dict[str, Vault] = {}
        self.data_retrieval_policy: dict[str, Any] = {
            "Rules": [{"Strategy": "FreeTier"}]
        }
        self.provisioned_capacity: list[dict[str, Any]] = []

    def describe_vault(self, vault_name: str) -> Vault:
        if vault_name not in self.vaults:
            raise JsonRESTError(error_type="VaultNotFound", message="Vault not found")
        return self.vaults[vault_name]

    def create_vault(self, vault_name: str) -> None:
        self.vaults[vault_name] = Vault(vault_name, self.account_id, self.region_name)

    def list_vaults(self) -> list[Vault]:
        return list(self.vaults.values())

    def delete_vault(self, vault_name: str) -> None:
        self.vaults.pop(vault_name)

    def initiate_job(
        self, vault_name: str, job_type: str, tier: str, archive_id: Optional[str]
    ) -> str:
        vault = self.describe_vault(vault_name)
        job_id = vault.initiate_job(job_type, tier, archive_id)
        return job_id

    def describe_job(self, vault_name: str, archive_id: str) -> Optional[Job]:
        vault = self.describe_vault(vault_name)
        return vault.describe_job(archive_id)

    def list_jobs(self, vault_name: str) -> list[Job]:
        vault = self.describe_vault(vault_name)
        return vault.list_jobs()

    def get_job_output(
        self, vault_name: str, job_id: str
    ) -> Union[str, dict[str, Any], None]:
        vault = self.describe_vault(vault_name)
        if vault.job_ready(job_id):
            return vault.get_job_output(job_id)
        else:
            return None

    def delete_archive(self, vault_name: str, archive_id: str) -> None:
        vault = self.describe_vault(vault_name)
        vault.delete_archive(archive_id)

    def upload_archive(
        self, vault_name: str, body: bytes, description: str
    ) -> dict[str, Any]:
        vault = self.describe_vault(vault_name)
        return vault.create_archive(body, description)

    # --- Data Retrieval Policy ---

    def get_data_retrieval_policy(self) -> dict[str, Any]:
        return {"Policy": self.data_retrieval_policy}

    def set_data_retrieval_policy(self, policy: dict[str, Any]) -> None:
        self.data_retrieval_policy = policy

    # --- Tags ---

    def add_tags_to_vault(self, vault_name: str, tags: dict[str, str]) -> None:
        vault = self.describe_vault(vault_name)
        vault.tags.update(tags)

    def remove_tags_from_vault(self, vault_name: str, tag_keys: list[str]) -> None:
        vault = self.describe_vault(vault_name)
        for key in tag_keys:
            vault.tags.pop(key, None)

    def list_tags_for_vault(self, vault_name: str) -> dict[str, str]:
        vault = self.describe_vault(vault_name)
        return vault.tags

    # --- Vault Notifications ---

    def set_vault_notifications(
        self, vault_name: str, config: dict[str, Any]
    ) -> None:
        vault = self.describe_vault(vault_name)
        vault.notification_configuration = config

    def get_vault_notifications(self, vault_name: str) -> Optional[dict[str, Any]]:
        vault = self.describe_vault(vault_name)
        if vault.notification_configuration is None:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message="No notification configuration is set for vault",
            )
        return vault.notification_configuration

    def delete_vault_notifications(self, vault_name: str) -> None:
        vault = self.describe_vault(vault_name)
        vault.notification_configuration = None

    # --- Vault Access Policy ---

    def set_vault_access_policy(self, vault_name: str, policy: str) -> None:
        vault = self.describe_vault(vault_name)
        vault.access_policy = policy

    def get_vault_access_policy(self, vault_name: str) -> Optional[str]:
        vault = self.describe_vault(vault_name)
        if vault.access_policy is None:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message="No access policy is set for vault",
            )
        return vault.access_policy

    def delete_vault_access_policy(self, vault_name: str) -> None:
        vault = self.describe_vault(vault_name)
        vault.access_policy = None

    # --- Vault Lock ---

    def initiate_vault_lock(
        self, vault_name: str, policy: dict[str, Any]
    ) -> str:
        vault = self.describe_vault(vault_name)
        lock_id = str(uuid.uuid4())
        vault.vault_lock = {
            "Policy": policy.get("Policy", ""),
            "State": "InProgress",
            "LockId": lock_id,
            "CreationDate": datetime.datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S.000Z"
            ),
            "ExpirationDate": (
                datetime.datetime.now() + datetime.timedelta(hours=24)
            ).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        }
        return lock_id

    def get_vault_lock(self, vault_name: str) -> Optional[dict[str, Any]]:
        vault = self.describe_vault(vault_name)
        if vault.vault_lock is None:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message="No vault lock policy is set for vault",
            )
        return vault.vault_lock

    def complete_vault_lock(self, vault_name: str, lock_id: str) -> None:
        vault = self.describe_vault(vault_name)
        if vault.vault_lock is None or vault.vault_lock["LockId"] != lock_id:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message="Vault lock not found",
            )
        vault.vault_lock["State"] = "Locked"
        # Remove expiration once locked
        vault.vault_lock.pop("ExpirationDate", None)

    def abort_vault_lock(self, vault_name: str) -> None:
        vault = self.describe_vault(vault_name)
        vault.vault_lock = None

    # --- Provisioned Capacity ---

    def list_provisioned_capacity(self) -> list[dict[str, Any]]:
        return self.provisioned_capacity

    def purchase_provisioned_capacity(self) -> dict[str, str]:
        cap_id = str(uuid.uuid4())
        self.provisioned_capacity.append(
            {
                "CapacityId": cap_id,
                "StartDate": datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S.000Z"
                ),
                "ExpirationDate": (
                    datetime.datetime.now() + datetime.timedelta(days=30)
                ).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            }
        )
        return {"capacityId": cap_id}

    # --- Multipart Upload ---

    def initiate_multipart_upload(
        self, vault_name: str, part_size: int, archive_description: str
    ) -> str:
        vault = self.describe_vault(vault_name)
        upload_id = str(uuid.uuid4())
        vault.multipart_uploads[upload_id] = MultipartUpload(
            vault_name, upload_id, part_size, archive_description
        )
        return upload_id

    def upload_multipart_part(
        self, vault_name: str, upload_id: str, range_header: str, body: bytes
    ) -> str:
        vault = self.describe_vault(vault_name)
        if upload_id not in vault.multipart_uploads:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message=f"Upload not found: {upload_id}",
            )
        upload = vault.multipart_uploads[upload_id]
        upload.parts[range_header] = body
        return hashlib.sha256(body).hexdigest()

    def complete_multipart_upload(
        self, vault_name: str, upload_id: str, archive_size: int
    ) -> dict[str, Any]:
        vault = self.describe_vault(vault_name)
        if upload_id not in vault.multipart_uploads:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message=f"Upload not found: {upload_id}",
            )
        upload = vault.multipart_uploads.pop(upload_id)
        # Combine all parts into one body
        all_parts = sorted(upload.parts.items())
        body = b"".join(part_body for _, part_body in all_parts)
        archive = vault.create_archive(body, upload.archive_description)
        return archive

    def abort_multipart_upload(self, vault_name: str, upload_id: str) -> None:
        vault = self.describe_vault(vault_name)
        if upload_id not in vault.multipart_uploads:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message=f"Upload not found: {upload_id}",
            )
        vault.multipart_uploads.pop(upload_id)

    def list_multipart_uploads(self, vault_name: str) -> list[dict[str, Any]]:
        vault = self.describe_vault(vault_name)
        return [u.to_dict() for u in vault.multipart_uploads.values()]

    def list_parts(self, vault_name: str, upload_id: str) -> dict[str, Any]:
        vault = self.describe_vault(vault_name)
        if upload_id not in vault.multipart_uploads:
            raise JsonRESTError(
                error_type="ResourceNotFoundException",
                message=f"Upload not found: {upload_id}",
            )
        upload = vault.multipart_uploads[upload_id]
        parts = []
        for range_header, body in sorted(upload.parts.items()):
            parts.append(
                {
                    "RangeInBytes": range_header,
                    "SHA256TreeHash": hashlib.sha256(body).hexdigest(),
                }
            )
        return {
            "ArchiveDescription": upload.archive_description,
            "CreationDate": upload.creation_date,
            "Marker": None,
            "MultipartUploadId": upload_id,
            "PartSizeInBytes": upload.part_size,
            "Parts": parts,
            "VaultARN": vault.arn,
        }


glacier_backends = BackendDict(GlacierBackend, "glacier")
