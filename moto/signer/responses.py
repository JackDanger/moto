"""Handles incoming signer requests, invokes methods, returns responses."""

import json
from typing import Any
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import SignerBackend, signer_backends


class SignerResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="signer")

    @property
    def signer_backend(self) -> SignerBackend:
        """Return backend instance specific for this region."""
        return signer_backends[self.current_account][self.region]

    def cancel_signing_profile(self) -> str:
        profile_name = self.path.split("/")[-1]
        self.signer_backend.cancel_signing_profile(profile_name=profile_name)
        return "{}"

    def get_signing_profile(self) -> str:
        profile_name = self.path.split("/")[-1]
        profile = self.signer_backend.get_signing_profile(profile_name=profile_name)
        return json.dumps(profile.to_dict())

    def put_signing_profile(self) -> str:
        params = json.loads(self.body)
        profile_name = self.path.split("/")[-1]
        signature_validity_period = params.get("signatureValidityPeriod")
        platform_id = params.get("platformId")
        tags = params.get("tags")
        signing_material = params.get("signingMaterial")
        profile = self.signer_backend.put_signing_profile(
            profile_name=profile_name,
            signature_validity_period=signature_validity_period,
            platform_id=platform_id,
            signing_material=signing_material,
            tags=tags,
        )
        return json.dumps(profile.to_dict(full=False))

    def list_signing_platforms(self) -> str:
        platforms = self.signer_backend.list_signing_platforms()
        return json.dumps({"platforms": platforms})

    def get_signing_platform(self) -> str:
        platform_id = self.path.split("/")[-1]
        platform = self.signer_backend.get_signing_platform(platform_id=platform_id)
        return json.dumps(platform)

    def list_signing_profiles(self) -> str:
        include_canceled = self.querystring.get("includeCanceled", [False])[0]
        if isinstance(include_canceled, str):
            include_canceled = include_canceled.lower() == "true"
        platform_id = self._get_param("platformId")
        statuses_raw = self.querystring.get("statuses", None)
        statuses = statuses_raw if statuses_raw else None

        profiles = self.signer_backend.list_signing_profiles(
            include_canceled=include_canceled,
            platform_id=platform_id,
            statuses=statuses,
        )
        return json.dumps({"profiles": [p.to_dict() for p in profiles]})

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        return json.dumps(
            {"tags": self.signer_backend.list_tags_for_resource(resource_arn)}
        )

    def tag_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tags = self._get_param("tags")
        self.signer_backend.tag_resource(resource_arn, tags)
        return "{}"

    def untag_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tag_keys = self.querystring.get("tagKeys")
        self.signer_backend.untag_resource(resource_arn, tag_keys)  # type: ignore
        return "{}"

    def tags(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.list_tags_for_resource()
        if request.method == "POST":
            return self.tag_resource()
        if request.method == "DELETE":
            return self.untag_resource()

    def signing_jobs(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return self._start_signing_job()
        if request.method == "GET":
            return self._list_signing_jobs()

    def signing_job(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self._describe_signing_job()

    def signing_job_revoke(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "PUT":
            return self._revoke_signature()

    def signing_profile_revoke(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "PUT":
            return self._revoke_signing_profile()

    def signing_profiles(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.list_signing_profiles()

    def signing_profile(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.get_signing_profile()
        if request.method == "PUT":
            return self.put_signing_profile()
        if request.method == "DELETE":
            return self.cancel_signing_profile()

    def signing_platform(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.get_signing_platform()

    def profile_permissions(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return self._add_profile_permission()
        if request.method == "GET":
            return self._list_profile_permissions()

    def profile_permission(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "DELETE":
            return self._remove_profile_permission()

    def sign_payload(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return self._sign_payload()

    def revocations(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self._get_revocation_status()

    def _start_signing_job(self) -> str:
        params = json.loads(self.body)
        source = params.get("source", {})
        destination = params.get("destination", {})
        profile_name = params.get("profileName", "")
        client_request_token = params.get("clientRequestToken", "")
        profile_owner = params.get("profileOwner")

        job = self.signer_backend.start_signing_job(
            source=source,
            destination=destination,
            profile_name=profile_name,
            client_request_token=client_request_token,
            profile_owner=profile_owner,
        )
        return json.dumps({"jobId": job.job_id, "jobOwner": job.job_owner})

    def _describe_signing_job(self) -> str:
        job_id = self.path.split("/")[-1]
        job = self.signer_backend.describe_signing_job(job_id=job_id)
        return json.dumps(job.to_dict(full=True))

    def _list_signing_jobs(self) -> str:
        status = self._get_param("status")
        platform_id = self._get_param("platformId")
        requested_by = self._get_param("requestedBy")
        is_revoked_str = self._get_param("isRevoked")
        is_revoked = None
        if is_revoked_str is not None:
            is_revoked = is_revoked_str.lower() == "true" if isinstance(is_revoked_str, str) else bool(is_revoked_str)

        jobs = self.signer_backend.list_signing_jobs(
            status=status,
            platform_id=platform_id,
            requested_by=requested_by,
            is_revoked=is_revoked,
        )
        return json.dumps({"jobs": [j.to_dict(full=False) for j in jobs]})

    def _revoke_signature(self) -> str:
        parts = self.path.split("/")
        # path: /signing-jobs/{jobId}/revoke
        job_id = parts[-2]
        params = json.loads(self.body)
        reason = params.get("reason", "")
        job_owner = params.get("jobOwner")

        self.signer_backend.revoke_signature(
            job_id=job_id,
            reason=reason,
            job_owner=job_owner,
        )
        return "{}"

    def _revoke_signing_profile(self) -> str:
        parts = self.path.split("/")
        # path: /signing-profiles/{profileName}/revoke
        profile_name = parts[-2]
        params = json.loads(self.body)
        profile_version = params.get("profileVersion", "")
        reason = params.get("reason", "")
        effective_time = params.get("effectiveTime")

        self.signer_backend.revoke_signing_profile(
            profile_name=profile_name,
            profile_version=profile_version,
            reason=reason,
            effective_time=effective_time,
        )
        return "{}"

    def _add_profile_permission(self) -> str:
        parts = self.path.split("/")
        # path: /signing-profiles/{profileName}/permissions
        profile_name = parts[-2]
        params = json.loads(self.body)
        action = params.get("action", "")
        principal = params.get("principal", "")
        statement_id = params.get("statementId", "")
        profile_version = params.get("profileVersion")
        revision_id = params.get("revisionId")

        new_revision_id = self.signer_backend.add_profile_permission(
            profile_name=profile_name,
            action=action,
            principal=principal,
            statement_id=statement_id,
            profile_version=profile_version,
            revision_id=revision_id,
        )
        return json.dumps({"revisionId": new_revision_id})

    def _list_profile_permissions(self) -> str:
        parts = self.path.split("/")
        # path: /signing-profiles/{profileName}/permissions
        profile_name = parts[-2]
        result = self.signer_backend.list_profile_permissions(profile_name=profile_name)
        return json.dumps(result)

    def _remove_profile_permission(self) -> str:
        parts = self.path.split("/")
        # path: /signing-profiles/{profileName}/permissions/{statementId}
        statement_id = parts[-1]
        profile_name = parts[-3]
        revision_id = self._get_param("revisionId") or ""

        new_revision_id = self.signer_backend.remove_profile_permission(
            profile_name=profile_name,
            statement_id=statement_id,
            revision_id=revision_id,
        )
        return json.dumps({"revisionId": new_revision_id})

    def _sign_payload(self) -> str:
        params = json.loads(self.body)
        profile_name = params.get("profileName", "")
        profile_owner = params.get("profileOwner")
        payload = params.get("payload", "")
        payload_format = params.get("payloadFormat", "")

        result = self.signer_backend.sign_payload(
            profile_name=profile_name,
            profile_owner=profile_owner,
            payload=payload,
            payload_format=payload_format,
        )
        return json.dumps(result)

    def _get_revocation_status(self) -> str:
        signature_timestamp = self._get_param("signatureTimestamp") or ""
        platform_id = self._get_param("platformId") or ""
        profile_version_arn = self._get_param("profileVersionArn") or ""
        job_arn = self._get_param("jobArn") or ""
        certificate_hashes = self.querystring.get("certificateHashes", [])

        result = self.signer_backend.get_revocation_status(
            signature_timestamp=signature_timestamp,
            platform_id=platform_id,
            profile_version_arn=profile_version_arn,
            job_arn=job_arn,
            certificate_hashes=certificate_hashes,
        )
        return json.dumps(result)
