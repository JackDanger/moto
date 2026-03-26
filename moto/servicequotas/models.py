"""ServiceQuotasBackend class with methods for supported APIs."""

import datetime
import uuid
from typing import Any

from moto.core.base_backend import BackendDict, BaseBackend
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import NoSuchResource
from .resources.default_quotas.vpc import VPC_DEFAULT_QUOTAS

# Known services list (simplified)
KNOWN_SERVICES = [
    {"ServiceCode": "vpc", "ServiceName": "Amazon Virtual Private Cloud (Amazon VPC)"},
    {"ServiceCode": "ec2", "ServiceName": "Amazon Elastic Compute Cloud (Amazon EC2)"},
    {"ServiceCode": "s3", "ServiceName": "Amazon Simple Storage Service (Amazon S3)"},
    {"ServiceCode": "iam", "ServiceName": "AWS Identity and Access Management (IAM)"},
    {"ServiceCode": "lambda", "ServiceName": "AWS Lambda"},
    {"ServiceCode": "dynamodb", "ServiceName": "Amazon DynamoDB"},
    {"ServiceCode": "kinesis", "ServiceName": "Amazon Kinesis"},
    {"ServiceCode": "sqs", "ServiceName": "Amazon Simple Queue Service (Amazon SQS)"},
    {"ServiceCode": "sns", "ServiceName": "Amazon Simple Notification Service (Amazon SNS)"},
]


class ServiceQuotasBackend(BaseBackend):
    """Implementation of ServiceQuotas APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.tagger = TaggingService()
        self._quota_change_requests: dict[str, dict[str, Any]] = {}
        self._template_requests: dict[str, dict[str, Any]] = {}
        self._template_associated: bool = False
        self._auto_management_enabled: bool = False

    def _get_quota_arn(self, service_code: str, quota_code: str) -> str:
        partition = get_partition(self.region_name)
        return f"arn:{partition}:servicequotas:{self.region_name}:{self.account_id}:{service_code}/{quota_code}"

    def list_services(self) -> list[dict[str, Any]]:
        return KNOWN_SERVICES

    def list_aws_default_service_quotas(
        self, service_code: str
    ) -> list[dict[str, Any]]:
        """
        The ServiceCodes that are currently implemented are: vpc
        Pagination is not yet implemented.
        """
        if service_code == "vpc":
            return VPC_DEFAULT_QUOTAS
        raise NoSuchResource

    def get_aws_default_service_quota(
        self, service_code: str, quota_code: str
    ) -> dict[str, Any]:
        if service_code == "vpc":
            for quota in VPC_DEFAULT_QUOTAS:
                if quota["QuotaCode"] == quota_code:
                    return quota
        raise NoSuchResource

    def list_service_quotas(
        self, service_code: str, quota_code: str | None = None
    ) -> list[dict[str, Any]]:
        """List applied service quotas (same as defaults for mock purposes)."""
        if service_code == "vpc":
            quotas = list(VPC_DEFAULT_QUOTAS)
            if quota_code:
                quotas = [q for q in quotas if q["QuotaCode"] == quota_code]
            return quotas
        # Return empty list for unknown services (rather than error)
        return []

    def get_service_quota(self, service_code: str, quota_code: str) -> dict[str, Any]:
        if service_code == "vpc":
            for quota in VPC_DEFAULT_QUOTAS:
                if quota["QuotaCode"] == quota_code:
                    return quota
        raise NoSuchResource

    def request_service_quota_increase(
        self,
        service_code: str,
        quota_code: str,
        desired_value: float,
    ) -> dict[str, Any]:
        request_id = str(uuid.uuid4())
        request = {
            "Id": request_id,
            "CaseId": f"case-{request_id[:8]}",
            "ServiceCode": service_code,
            "ServiceName": next(
                (s["ServiceName"] for s in KNOWN_SERVICES if s["ServiceCode"] == service_code),
                service_code,
            ),
            "QuotaCode": quota_code,
            "QuotaName": f"Quota {quota_code}",
            "DesiredValue": desired_value,
            "Status": "PENDING",
            "Created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "LastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "Requester": f"{self.account_id}",
            "QuotaArn": self._get_quota_arn(service_code, quota_code),
            "GlobalQuota": False,
            "Unit": "None",
            "QuotaContext": {"ContextLevel": "ACCOUNT"},
        }
        self._quota_change_requests[request_id] = request
        return request

    def get_requested_service_quota_change(self, request_id: str) -> dict[str, Any]:
        if request_id not in self._quota_change_requests:
            raise NoSuchResource
        return self._quota_change_requests[request_id]

    def list_requested_service_quota_change_history(
        self,
        service_code: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        requests = list(self._quota_change_requests.values())
        if service_code:
            requests = [r for r in requests if r["ServiceCode"] == service_code]
        if status:
            requests = [r for r in requests if r["Status"] == status]
        return requests

    def list_requested_service_quota_change_history_by_quota(
        self,
        service_code: str,
        quota_code: str,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        requests = list(self._quota_change_requests.values())
        requests = [
            r for r in requests
            if r["ServiceCode"] == service_code and r["QuotaCode"] == quota_code
        ]
        if status:
            requests = [r for r in requests if r["Status"] == status]
        return requests

    def associate_service_quota_template(self) -> None:
        self._template_associated = True

    def disassociate_service_quota_template(self) -> None:
        self._template_associated = False

    def get_association_for_service_quota_template(self) -> dict[str, Any]:
        return {
            "ServiceQuotaTemplateAssociationStatus": "ASSOCIATED" if self._template_associated else "DISASSOCIATED"
        }

    def put_service_quota_increase_request_into_template(
        self,
        quota_code: str,
        service_code: str,
        aws_region: str,
        desired_value: float,
    ) -> dict[str, Any]:
        key = f"{service_code}/{quota_code}/{aws_region}"
        item = {
            "ServiceCode": service_code,
            "ServiceName": next(
                (s["ServiceName"] for s in KNOWN_SERVICES if s["ServiceCode"] == service_code),
                service_code,
            ),
            "QuotaCode": quota_code,
            "QuotaName": f"Quota {quota_code}",
            "DesiredValue": desired_value,
            "AwsRegion": aws_region,
            "Unit": "None",
            "GlobalQuota": False,
        }
        self._template_requests[key] = item
        return item

    def list_service_quota_increase_requests_in_template(
        self,
        service_code: str | None = None,
        aws_region: str | None = None,
    ) -> list[dict[str, Any]]:
        items = list(self._template_requests.values())
        if service_code:
            items = [i for i in items if i["ServiceCode"] == service_code]
        if aws_region:
            items = [i for i in items if i["AwsRegion"] == aws_region]
        return items

    def get_service_quota_increase_request_from_template(
        self,
        service_code: str,
        quota_code: str,
        aws_region: str,
    ) -> dict[str, Any]:
        key = f"{service_code}/{quota_code}/{aws_region}"
        if key not in self._template_requests:
            raise NoSuchResource
        return self._template_requests[key]

    def delete_service_quota_increase_request_from_template(
        self,
        service_code: str,
        quota_code: str,
        aws_region: str,
    ) -> None:
        key = f"{service_code}/{quota_code}/{aws_region}"
        if key not in self._template_requests:
            raise NoSuchResource
        del self._template_requests[key]

    def get_auto_management_configuration(self) -> dict[str, Any]:
        return {
            "AutoManagementEnabled": self._auto_management_enabled,
        }

    def start_auto_management(self) -> None:
        self._auto_management_enabled = True

    def stop_auto_management(self) -> None:
        self._auto_management_enabled = False

    def update_auto_management(self, enable: bool) -> dict[str, Any]:
        self._auto_management_enabled = enable
        return {"AutoManagementEnabled": self._auto_management_enabled}

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(
            resource_arn, TaggingService.convert_dict_to_tags_input(tags)
        )

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)


servicequotas_backends = BackendDict(ServiceQuotasBackend, "service-quotas")
