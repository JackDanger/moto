"""Handles incoming servicequotas requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import ServiceQuotasBackend, servicequotas_backends


class ServiceQuotasResponse(BaseResponse):
    """Handler for ServiceQuotas requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="service-quotas")

    @property
    def backend(self) -> ServiceQuotasBackend:
        """Return backend instance specific for this region."""
        return servicequotas_backends[self.current_account][self.region]

    def list_aws_default_service_quotas(self) -> str:
        params = json.loads(self.body)
        service_code = str(params.get("ServiceCode"))
        quotas = self.backend.list_aws_default_service_quotas(service_code)
        return json.dumps({"Quotas": quotas})

    def get_aws_default_service_quota(self) -> str:
        params = json.loads(self.body)
        service_code = str(params.get("ServiceCode"))
        quota_code = str(params.get("QuotaCode"))
        quota = self.backend.get_aws_default_service_quota(
            service_code=service_code,
            quota_code=quota_code,
        )
        return json.dumps({"Quota": quota})

    def get_service_quota(self) -> str:
        params = json.loads(self.body)
        service_code = str(params.get("ServiceCode"))
        quota_code = str(params.get("QuotaCode"))
        quota = self.backend.get_service_quota(
            service_code=service_code,
            quota_code=quota_code,
        )
        return json.dumps({"Quota": quota})

    def list_service_quotas(self) -> str:
        params = json.loads(self.body)
        service_code = str(params.get("ServiceCode"))
        quota_code = params.get("QuotaCode")
        quotas = self.backend.list_service_quotas(
            service_code=service_code,
            quota_code=quota_code,
        )
        return json.dumps({"Quotas": quotas})

    def list_services(self) -> str:
        services = self.backend.list_services()
        return json.dumps({"Services": services})

    def request_service_quota_increase(self) -> str:
        params = json.loads(self.body)
        service_code = str(params.get("ServiceCode"))
        quota_code = str(params.get("QuotaCode"))
        desired_value = float(params.get("DesiredValue"))
        request = self.backend.request_service_quota_increase(
            service_code=service_code,
            quota_code=quota_code,
            desired_value=desired_value,
        )
        return json.dumps({"RequestedQuota": request})

    def get_requested_service_quota_change(self) -> str:
        params = json.loads(self.body)
        request_id = str(params.get("RequestId"))
        request = self.backend.get_requested_service_quota_change(request_id)
        return json.dumps({"RequestedQuota": request})

    def list_requested_service_quota_change_history(self) -> str:
        params = json.loads(self.body)
        service_code = params.get("ServiceCode")
        status = params.get("Status")
        requests = self.backend.list_requested_service_quota_change_history(
            service_code=service_code,
            status=status,
        )
        return json.dumps({"RequestedQuotas": requests})

    def list_requested_service_quota_change_history_by_quota(self) -> str:
        params = json.loads(self.body)
        service_code = str(params.get("ServiceCode"))
        quota_code = str(params.get("QuotaCode"))
        status = params.get("Status")
        requests = self.backend.list_requested_service_quota_change_history_by_quota(
            service_code=service_code,
            quota_code=quota_code,
            status=status,
        )
        return json.dumps({"RequestedQuotas": requests})

    def associate_service_quota_template(self) -> str:
        self.backend.associate_service_quota_template()
        return json.dumps({})

    def disassociate_service_quota_template(self) -> str:
        self.backend.disassociate_service_quota_template()
        return json.dumps({})

    def get_association_for_service_quota_template(self) -> str:
        result = self.backend.get_association_for_service_quota_template()
        return json.dumps(result)

    def put_service_quota_increase_request_into_template(self) -> str:
        params = json.loads(self.body)
        quota_code = str(params.get("QuotaCode"))
        service_code = str(params.get("ServiceCode"))
        aws_region = str(params.get("AwsRegion"))
        desired_value = float(params.get("DesiredValue"))
        item = self.backend.put_service_quota_increase_request_into_template(
            quota_code=quota_code,
            service_code=service_code,
            aws_region=aws_region,
            desired_value=desired_value,
        )
        return json.dumps({"ServiceQuotaIncreaseRequestInTemplate": item})

    def list_service_quota_increase_requests_in_template(self) -> str:
        params = json.loads(self.body)
        service_code = params.get("ServiceCode")
        aws_region = params.get("AwsRegion")
        items = self.backend.list_service_quota_increase_requests_in_template(
            service_code=service_code,
            aws_region=aws_region,
        )
        return json.dumps({"ServiceQuotaIncreaseRequestInTemplateList": items})

    def delete_service_quota_increase_request_from_template(self) -> str:
        params = json.loads(self.body)
        service_code = str(params.get("ServiceCode"))
        quota_code = str(params.get("QuotaCode"))
        aws_region = str(params.get("AwsRegion"))
        self.backend.delete_service_quota_increase_request_from_template(
            service_code=service_code,
            quota_code=quota_code,
            aws_region=aws_region,
        )
        return json.dumps({})

    def get_auto_management_configuration(self) -> str:
        result = self.backend.get_auto_management_configuration()
        return json.dumps(result)

    def start_auto_management(self) -> str:
        self.backend.start_auto_management()
        return json.dumps({})

    def stop_auto_management(self) -> str:
        self.backend.stop_auto_management()
        return json.dumps({})

    def update_auto_management(self) -> str:
        params = json.loads(self.body)
        enable = bool(params.get("Enable", False))
        result = self.backend.update_auto_management(enable=enable)
        return json.dumps(result)

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = str(params.get("ResourceARN"))
        tags = params.get("Tags") or {}
        self.backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = str(params.get("ResourceARN"))
        tag_keys = params.get("TagKeys") or []
        self.backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = str(params.get("ResourceARN"))
        tags = self.backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"Tags": tags})

    def get_quota_utilization_report(self) -> str:
        # Stub - return empty report
        return json.dumps({"RequestId": ""})

    def start_quota_utilization_report(self) -> str:
        return json.dumps({})

    def create_support_case(self) -> str:
        return json.dumps({})
