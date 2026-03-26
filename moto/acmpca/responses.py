"""Handles incoming acmpca requests, invokes methods, returns responses."""

import base64
import binascii
import json

from moto.core.responses import BaseResponse

from .models import ACMPCABackend, acmpca_backends


class ACMPCAResponse(BaseResponse):
    """Handler for ACMPCA requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="acmpca")

    @property
    def acmpca_backend(self) -> ACMPCABackend:
        """Return backend instance specific for this region."""
        return acmpca_backends[self.current_account][self.region]

    def create_certificate_authority(self) -> str:
        params = json.loads(self.body)
        certificate_authority_configuration = params.get(
            "CertificateAuthorityConfiguration"
        )
        revocation_configuration = params.get("RevocationConfiguration")
        certificate_authority_type = params.get("CertificateAuthorityType")
        security_standard = params.get("KeyStorageSecurityStandard")
        tags = params.get("Tags")
        certificate_authority_arn = self.acmpca_backend.create_certificate_authority(
            certificate_authority_configuration=certificate_authority_configuration,
            revocation_configuration=revocation_configuration,
            certificate_authority_type=certificate_authority_type,
            security_standard=security_standard,
            tags=tags,
        )
        return json.dumps({"CertificateAuthorityArn": certificate_authority_arn})

    def describe_certificate_authority(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        certificate_authority = self.acmpca_backend.describe_certificate_authority(
            certificate_authority_arn=certificate_authority_arn,
        )
        return json.dumps({"CertificateAuthority": certificate_authority.to_json()})

    def get_certificate_authority_certificate(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        (
            certificate,
            certificate_chain,
        ) = self.acmpca_backend.get_certificate_authority_certificate(
            certificate_authority_arn=certificate_authority_arn,
        )
        response = {"Certificate": certificate.decode("utf-8")}
        if certificate_chain:
            try:
                decoded_chain = base64.b64decode(certificate_chain)
                response["CertificateChain"] = decoded_chain.decode("utf-8")
            except (binascii.Error, AttributeError):
                response["CertificateChain"] = (
                    certificate_chain.decode("utf-8")
                    if isinstance(certificate_chain, bytes)
                    else certificate_chain
                )
        return json.dumps(response)

    def get_certificate_authority_csr(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        csr = self.acmpca_backend.get_certificate_authority_csr(
            certificate_authority_arn=certificate_authority_arn,
        )
        return json.dumps({"Csr": csr.decode("utf-8").strip()})

    def list_tags(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        tags = self.acmpca_backend.list_tags(
            certificate_authority_arn=certificate_authority_arn
        )
        return json.dumps(tags)

    def update_certificate_authority(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        revocation_configuration = params.get("RevocationConfiguration")
        status = params.get("Status")
        self.acmpca_backend.update_certificate_authority(
            certificate_authority_arn=certificate_authority_arn,
            revocation_configuration=revocation_configuration,
            status=status,
        )
        return "{}"

    def delete_certificate_authority(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        self.acmpca_backend.delete_certificate_authority(
            certificate_authority_arn=certificate_authority_arn
        )
        return "{}"

    def issue_certificate(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        template_arn = params.get("TemplateArn")
        csr = params.get("Csr").encode("utf-8")
        certificate_arn = self.acmpca_backend.issue_certificate(
            certificate_authority_arn=certificate_authority_arn,
            csr=csr,
            template_arn=template_arn,
        )
        return json.dumps({"CertificateArn": certificate_arn})

    def get_certificate(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        certificate_arn = params.get("CertificateArn")
        certificate, certificate_chain = self.acmpca_backend.get_certificate(
            certificate_authority_arn=certificate_authority_arn,
            certificate_arn=certificate_arn,
        )

        response = {"Certificate": certificate.decode("utf-8").strip()}

        # Include CertificateChain if it exists (non-root certificates)
        if certificate_chain:
            response["CertificateChain"] = certificate_chain.decode("utf-8").strip()

        return json.dumps(response)

    def import_certificate_authority_certificate(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        certificate = params.get("Certificate")
        certificate_bytes = base64.b64decode(certificate)
        certificate_chain = params.get("CertificateChain")
        self.acmpca_backend.import_certificate_authority_certificate(
            certificate_authority_arn=certificate_authority_arn,
            certificate=certificate_bytes,
            certificate_chain=certificate_chain,
        )
        return "{}"

    def revoke_certificate(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        certificate_serial = params.get("CertificateSerial")
        revocation_reason = params.get("RevocationReason")
        self.acmpca_backend.revoke_certificate(
            certificate_authority_arn=certificate_authority_arn,
            certificate_serial=certificate_serial,
            revocation_reason=revocation_reason,
        )
        return "{}"

    def tag_certificate_authority(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        tags = params.get("Tags")
        self.acmpca_backend.tag_certificate_authority(
            certificate_authority_arn=certificate_authority_arn,
            tags=tags,
        )
        return "{}"

    def untag_certificate_authority(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        tags = params.get("Tags")
        self.acmpca_backend.untag_certificate_authority(
            certificate_authority_arn=certificate_authority_arn,
            tags=tags,
        )
        return "{}"

    def put_policy(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        policy = params.get("Policy")
        self.acmpca_backend.put_policy(resource_arn=resource_arn, policy=policy)
        return "{}"

    def get_policy(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        policy = self.acmpca_backend.get_policy(resource_arn=resource_arn)
        return json.dumps({"Policy": policy})

    def delete_policy(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        self.acmpca_backend.delete_policy(resource_arn=resource_arn)
        return "{}"

    def restore_certificate_authority(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        self.acmpca_backend.restore_certificate_authority(
            certificate_authority_arn=certificate_authority_arn,
        )
        return "{}"

    def create_permission(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        principal = params.get("Principal")
        source_account = params.get("SourceAccount", "")
        actions = params.get("Actions", [])
        self.acmpca_backend.create_permission(
            certificate_authority_arn=certificate_authority_arn,
            principal=principal,
            source_account=source_account,
            actions=actions,
        )
        return "{}"

    def delete_permission(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        principal = params.get("Principal")
        source_account = params.get("SourceAccount")
        self.acmpca_backend.delete_permission(
            certificate_authority_arn=certificate_authority_arn,
            principal=principal,
            source_account=source_account,
        )
        return "{}"

    def list_permissions(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        permissions = self.acmpca_backend.list_permissions(
            certificate_authority_arn=certificate_authority_arn,
        )
        return json.dumps({"Permissions": [p.to_json() for p in permissions]})

    def create_certificate_authority_audit_report(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        s3_bucket_name = params.get("S3BucketName")
        audit_report_response_format = params.get("AuditReportResponseFormat")
        audit_report_id, s3_key = (
            self.acmpca_backend.create_certificate_authority_audit_report(
                certificate_authority_arn=certificate_authority_arn,
                s3_bucket_name=s3_bucket_name,
                audit_report_response_format=audit_report_response_format,
            )
        )
        return json.dumps({"AuditReportId": audit_report_id, "S3Key": s3_key})

    def describe_certificate_authority_audit_report(self) -> str:
        params = json.loads(self.body)
        certificate_authority_arn = params.get("CertificateAuthorityArn")
        audit_report_id = params.get("AuditReportId")
        report = self.acmpca_backend.describe_certificate_authority_audit_report(
            certificate_authority_arn=certificate_authority_arn,
            audit_report_id=audit_report_id,
        )
        return json.dumps({
            "AuditReportId": report["AuditReportId"],
            "S3BucketName": report["S3BucketName"],
            "S3Key": report["S3Key"],
            "CreatedAt": report["CreatedAt"],
            "AuditReportStatus": report["Status"],
        })

    def list_certificate_authorities(self) -> str:
        """
        Handler for ListCertificateAuthorities API request
        """
        params = json.loads(self.body)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        resource_owner = params.get("ResourceOwner")

        # Get paginated results and next token from backend
        cas, next_token = self.acmpca_backend.list_certificate_authorities(
            max_results=max_results,
            next_token=next_token,
            resource_owner=resource_owner,
        )

        response = {
            "CertificateAuthorities": [ca.to_json() for ca in cas],
            "NextToken": next_token,
        }

        return json.dumps(response)
