from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import ResourceNotFoundException


class SigningJob(BaseModel):
    def __init__(
        self,
        backend: "SignerBackend",
        source: dict[str, Any],
        destination: dict[str, Any],
        profile_name: str,
        client_request_token: str,
        profile_owner: Optional[str] = None,
    ):
        self.job_id = mock_random.get_random_hex(32)
        self.source = source
        self.destination = destination
        self.profile_name = profile_name
        self.client_request_token = client_request_token
        self.profile_owner = profile_owner or backend.account_id
        self.job_owner = backend.account_id
        self.created_at = utcnow()
        self.completed_at: Any = None
        self.status = "Succeeded"
        self.status_reason = ""
        self.backend = backend

        # Look up profile details
        profile = backend.signing_profiles.get(profile_name)
        self.platform_id = profile.platform_id if profile else ""
        self.platform_display_name = ""
        if profile:
            self.platform_display_name = next(
                (
                    p["displayName"]
                    for p in SignerBackend.platforms
                    if p["platformId"] == profile.platform_id
                ),
                "",
            )
        self.profile_version = profile.profile_version if profile else ""
        self.signing_material = profile.signing_material if profile else {}
        self.signature_expires_at: Any = None
        self.revocation_record: Any = None
        self.signed_object: dict[str, Any] = {}
        if destination and destination.get("s3"):
            s3_dest = destination["s3"]
            self.signed_object = {
                "s3": {
                    "bucketName": s3_dest.get("bucketName", ""),
                    "key": s3_dest.get("prefix", "") + self.job_id + ".zip",
                }
            }
        self.completed_at = utcnow()

    def to_dict(self, full: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "jobId": self.job_id,
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "profileName": self.profile_name,
            "profileVersion": self.profile_version,
            "platformId": self.platform_id,
            "platformDisplayName": self.platform_display_name,
            "jobOwner": self.job_owner,
        }
        if full:
            result.update(
                {
                    "source": self.source,
                    "signingMaterial": self.signing_material,
                    "signedObject": self.signed_object,
                    "requestedBy": self.job_owner,
                    "jobInvoker": self.job_owner,
                }
            )
            if self.status_reason:
                result["statusReason"] = self.status_reason
            if self.completed_at:
                result["completedAt"] = self.completed_at.isoformat()
            if self.signature_expires_at:
                result["signatureExpiresAt"] = self.signature_expires_at.isoformat()
            if self.revocation_record:
                result["revocationRecord"] = self.revocation_record
        else:
            if self.signed_object:
                result["signedObject"] = self.signed_object
            result["isRevoked"] = self.revocation_record is not None
            if self.source:
                result["source"] = self.source
            if self.signing_material:
                result["signingMaterial"] = self.signing_material
        return result


class Permission(BaseModel):
    def __init__(
        self,
        action: str,
        principal: str,
        statement_id: str,
        profile_version: Optional[str] = None,
    ):
        self.action = action
        self.principal = principal
        self.statement_id = statement_id
        self.profile_version = profile_version

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "action": self.action,
            "principal": self.principal,
            "statementId": self.statement_id,
        }
        if self.profile_version:
            result["profileVersion"] = self.profile_version
        return result


class SigningProfile(BaseModel):
    def __init__(
        self,
        backend: "SignerBackend",
        name: str,
        platform_id: str,
        signing_material: dict[str, str],
        signature_validity_period: Optional[dict[str, Any]],
    ):
        self.name = name
        self.platform_id = platform_id
        self.signature_validity_period = signature_validity_period or {
            "value": 135,
            "type": "MONTHS",
        }
        self.backend = backend

        self.status = "Active"
        self.arn = f"arn:{get_partition(backend.region_name)}:signer:{backend.region_name}:{backend.account_id}:/signing-profiles/{name}"
        self.profile_version = mock_random.get_random_hex(10)
        self.profile_version_arn = f"{self.arn}/{self.profile_version}"
        self.signing_material = signing_material
        self.permissions: dict[str, Permission] = {}
        self.revision_id = mock_random.get_random_hex(16)
        self.revoked_at: Any = None
        self.revoked_reason: Optional[str] = None

    def cancel(self) -> None:
        self.status = "Canceled"

    def revoke(self, profile_version: str, reason: str, effective_time: Any) -> None:
        self.status = "Revoked"
        self.revoked_at = effective_time
        self.revoked_reason = reason

    def to_dict(self, full: bool = True) -> dict[str, Any]:
        small: dict[str, Any] = {
            "arn": self.arn,
            "profileVersion": self.profile_version,
            "profileVersionArn": self.profile_version_arn,
        }
        if full:
            small.update(
                {
                    "status": self.status,
                    "profileName": self.name,
                    "platformId": self.platform_id,
                    "signatureValidityPeriod": self.signature_validity_period,
                    "signingMaterial": self.signing_material,
                    "platformDisplayName": next(
                        (
                            p["displayName"]
                            for p in SignerBackend.platforms
                            if p["platformId"] == self.platform_id
                        ),
                        None,
                    ),
                }
            )
            tags = self.backend.list_tags_for_resource(self.arn)
            if tags:
                small.update({"tags": tags})
        return small


class SignerBackend(BaseBackend):
    """Implementation of signer APIs."""

    platforms = [
        {
            "platformId": "AWSIoTDeviceManagement-SHA256-ECDSA",
            "displayName": "AWS IoT Device Management SHA256-ECDSA ",
            "partner": "AWSIoTDeviceManagement",
            "target": "SHA256-ECDSA",
            "category": "AWS",
            "signingConfiguration": {
                "encryptionAlgorithmOptions": {
                    "allowedValues": ["ECDSA"],
                    "defaultValue": "ECDSA",
                },
                "hashAlgorithmOptions": {
                    "allowedValues": ["SHA256"],
                    "defaultValue": "SHA256",
                },
            },
            "signingImageFormat": {
                "supportedFormats": ["JSONDetached"],
                "defaultFormat": "JSONDetached",
            },
            "maxSizeInMB": 2048,
            "revocationSupported": False,
        },
        {
            "platformId": "AWSLambda-SHA384-ECDSA",
            "displayName": "AWS Lambda",
            "partner": "AWSLambda",
            "target": "SHA384-ECDSA",
            "category": "AWS",
            "signingConfiguration": {
                "encryptionAlgorithmOptions": {
                    "allowedValues": ["ECDSA"],
                    "defaultValue": "ECDSA",
                },
                "hashAlgorithmOptions": {
                    "allowedValues": ["SHA384"],
                    "defaultValue": "SHA384",
                },
            },
            "signingImageFormat": {
                "supportedFormats": ["JSONDetached"],
                "defaultFormat": "JSONDetached",
            },
            "maxSizeInMB": 250,
            "revocationSupported": True,
        },
        {
            "platformId": "AmazonFreeRTOS-TI-CC3220SF",
            "displayName": "Amazon FreeRTOS SHA1-RSA CC3220SF-Format",
            "partner": "AmazonFreeRTOS",
            "target": "SHA1-RSA-TISHA1",
            "category": "AWS",
            "signingConfiguration": {
                "encryptionAlgorithmOptions": {
                    "allowedValues": ["RSA"],
                    "defaultValue": "RSA",
                },
                "hashAlgorithmOptions": {
                    "allowedValues": ["SHA1"],
                    "defaultValue": "SHA1",
                },
            },
            "signingImageFormat": {
                "supportedFormats": ["JSONEmbedded"],
                "defaultFormat": "JSONEmbedded",
            },
            "maxSizeInMB": 16,
            "revocationSupported": False,
        },
        {
            "platformId": "AmazonFreeRTOS-Default",
            "displayName": "Amazon FreeRTOS SHA256-ECDSA",
            "partner": "AmazonFreeRTOS",
            "target": "SHA256-ECDSA",
            "category": "AWS",
            "signingConfiguration": {
                "encryptionAlgorithmOptions": {
                    "allowedValues": ["ECDSA", "RSA"],
                    "defaultValue": "ECDSA",
                },
                "hashAlgorithmOptions": {
                    "allowedValues": ["SHA256"],
                    "defaultValue": "SHA256",
                },
            },
            "signingImageFormat": {
                "supportedFormats": ["JSONEmbedded"],
                "defaultFormat": "JSONEmbedded",
            },
            "maxSizeInMB": 16,
            "revocationSupported": False,
        },
    ]

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.signing_profiles: dict[str, SigningProfile] = {}
        self.signing_jobs: dict[str, SigningJob] = {}
        self.tagger = TaggingService()

    def cancel_signing_profile(self, profile_name: str) -> None:
        self.signing_profiles[profile_name].cancel()

    def get_signing_profile(self, profile_name: str) -> SigningProfile:
        if profile_name not in self.signing_profiles:
            raise ResourceNotFoundException(f"A profile with name [{profile_name}] does not exist.")
        return self.signing_profiles[profile_name]

    def put_signing_profile(
        self,
        profile_name: str,
        signature_validity_period: Optional[dict[str, Any]],
        platform_id: str,
        signing_material: dict[str, str],
        tags: dict[str, str],
    ) -> SigningProfile:
        """
        The following parameters are not yet implemented: Overrides, SigningParameters
        """
        profile = SigningProfile(
            backend=self,
            name=profile_name,
            platform_id=platform_id,
            signing_material=signing_material,
            signature_validity_period=signature_validity_period,
        )
        self.signing_profiles[profile_name] = profile
        self.tag_resource(profile.arn, tags)
        return profile

    def list_signing_platforms(self) -> list[dict[str, Any]]:
        """
        Pagination is not yet implemented. The parameters category, partner, target are not yet implemented
        """
        return SignerBackend.platforms

    def get_signing_platform(self, platform_id: str) -> Optional[dict[str, Any]]:
        for platform in SignerBackend.platforms:
            if platform["platformId"] == platform_id:
                return platform
        raise ResourceNotFoundException(f"A platform with platformId [{platform_id}] does not exist.")

    def list_signing_profiles(
        self,
        include_canceled: bool = False,
        platform_id: Optional[str] = None,
        statuses: Optional[list[str]] = None,
    ) -> list[SigningProfile]:
        profiles = list(self.signing_profiles.values())
        if not include_canceled:
            profiles = [p for p in profiles if p.status != "Canceled"]
        if platform_id:
            profiles = [p for p in profiles if p.platform_id == platform_id]
        if statuses:
            profiles = [p for p in profiles if p.status in statuses]
        return profiles

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(
            resource_arn, TaggingService.convert_dict_to_tags_input(tags)
        )

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def start_signing_job(
        self,
        source: dict[str, Any],
        destination: dict[str, Any],
        profile_name: str,
        client_request_token: str,
        profile_owner: Optional[str] = None,
    ) -> SigningJob:
        job = SigningJob(
            backend=self,
            source=source,
            destination=destination,
            profile_name=profile_name,
            client_request_token=client_request_token,
            profile_owner=profile_owner,
        )
        self.signing_jobs[job.job_id] = job
        return job

    def describe_signing_job(self, job_id: str) -> SigningJob:
        if job_id not in self.signing_jobs:
            raise ResourceNotFoundException(f"A signing job with ID [{job_id}] does not exist.")
        return self.signing_jobs[job_id]

    def list_signing_jobs(
        self,
        status: Optional[str] = None,
        platform_id: Optional[str] = None,
        requested_by: Optional[str] = None,
        is_revoked: Optional[bool] = None,
    ) -> list[SigningJob]:
        jobs = list(self.signing_jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        if platform_id:
            jobs = [j for j in jobs if j.platform_id == platform_id]
        if requested_by:
            jobs = [j for j in jobs if j.job_owner == requested_by]
        if is_revoked is not None:
            jobs = [j for j in jobs if (j.revocation_record is not None) == is_revoked]
        return jobs

    def revoke_signature(self, job_id: str, reason: str, job_owner: Optional[str] = None) -> None:
        if job_id not in self.signing_jobs:
            raise ResourceNotFoundException(f"A signing job with ID [{job_id}] does not exist.")
        job = self.signing_jobs[job_id]
        job.status = "Revoked"
        job.revocation_record = {
            "reason": reason,
            "revokedAt": utcnow().isoformat(),
            "revokedBy": job_owner or self.account_id,
        }

    def revoke_signing_profile(
        self,
        profile_name: str,
        profile_version: str,
        reason: str,
        effective_time: Any,
    ) -> None:
        if profile_name not in self.signing_profiles:
            raise ResourceNotFoundException(
                f"A profile with name [{profile_name}] does not exist."
            )
        profile = self.signing_profiles[profile_name]
        profile.revoke(profile_version, reason, effective_time)

    def sign_payload(
        self,
        profile_name: str,
        profile_owner: Optional[str],
        payload: str,
        payload_format: str,
    ) -> dict[str, Any]:
        import base64

        job_id = mock_random.get_random_hex(32)
        # Return a mock signature
        signature = base64.b64encode(mock_random.get_random_hex(64).encode()).decode()
        return {
            "jobId": job_id,
            "jobOwner": self.account_id,
            "metadata": {},
            "signature": signature,
        }

    def add_profile_permission(
        self,
        profile_name: str,
        action: str,
        principal: str,
        statement_id: str,
        profile_version: Optional[str] = None,
        revision_id: Optional[str] = None,
    ) -> str:
        if profile_name not in self.signing_profiles:
            raise ResourceNotFoundException(
                f"A profile with name [{profile_name}] does not exist."
            )
        profile = self.signing_profiles[profile_name]
        perm = Permission(
            action=action,
            principal=principal,
            statement_id=statement_id,
            profile_version=profile_version,
        )
        profile.permissions[statement_id] = perm
        profile.revision_id = mock_random.get_random_hex(16)
        return profile.revision_id

    def list_profile_permissions(self, profile_name: str) -> dict[str, Any]:
        if profile_name not in self.signing_profiles:
            raise ResourceNotFoundException(
                f"A profile with name [{profile_name}] does not exist."
            )
        profile = self.signing_profiles[profile_name]
        permissions = [p.to_dict() for p in profile.permissions.values()]
        return {
            "revisionId": profile.revision_id,
            "policySizeBytes": len(str(permissions)),
            "permissions": permissions,
        }

    def remove_profile_permission(
        self,
        profile_name: str,
        statement_id: str,
        revision_id: str,
    ) -> str:
        if profile_name not in self.signing_profiles:
            raise ResourceNotFoundException(
                f"A profile with name [{profile_name}] does not exist."
            )
        profile = self.signing_profiles[profile_name]
        profile.permissions.pop(statement_id, None)
        profile.revision_id = mock_random.get_random_hex(16)
        return profile.revision_id

    def get_revocation_status(
        self,
        signature_timestamp: str,
        platform_id: str,
        profile_version_arn: str,
        job_arn: str,
        certificate_hashes: list[str],
    ) -> dict[str, Any]:
        return {"revokedEntities": []}


signer_backends = BackendDict(SignerBackend, "signer")
