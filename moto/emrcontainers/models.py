"""EMRContainersBackend class with methods for supported APIs."""

import re
from collections.abc import Iterator
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_without_milliseconds
from moto.utilities.utils import get_partition

from ..config.exceptions import ValidationException
from .exceptions import ResourceNotFoundException
from .utils import paginated_list, random_cluster_id, random_id, random_job_id

VIRTUAL_CLUSTER_ARN_TEMPLATE = "arn:{partition}:emr-containers:{region}:{account_id}:/virtualclusters/{virtual_cluster_id}"

JOB_ARN_TEMPLATE = "arn:{partition}:emr-containers:{region}:{account_id}:/virtualclusters/{virtual_cluster_id}/jobruns/{job_id}"

JOB_TEMPLATE_ARN_TEMPLATE = "arn:{partition}:emr-containers:{region}:{account_id}:/jobtemplates/{job_template_id}"

MANAGED_ENDPOINT_ARN_TEMPLATE = "arn:{partition}:emr-containers:{region}:{account_id}:/virtualclusters/{virtual_cluster_id}/endpoints/{endpoint_id}"

SECURITY_CONFIGURATION_ARN_TEMPLATE = "arn:{partition}:emr-containers:{region}:{account_id}:/securityconfigurations/{security_configuration_id}"

# Defaults used for creating a Virtual cluster
VIRTUAL_CLUSTER_STATUS = "RUNNING"
JOB_STATUS = "RUNNING"
MANAGED_ENDPOINT_STATUS = "ACTIVE"


class FakeCluster(BaseModel):
    def __init__(
        self,
        name: str,
        container_provider: dict[str, Any],
        client_token: str,
        account_id: str,
        region_name: str,
        aws_partition: str,
        tags: Optional[dict[str, str]] = None,
        virtual_cluster_id: Optional[str] = None,
    ):
        self.id = virtual_cluster_id or random_cluster_id()

        self.name = name
        self.client_token = client_token
        self.arn = VIRTUAL_CLUSTER_ARN_TEMPLATE.format(
            partition=aws_partition,
            region=region_name,
            account_id=account_id,
            virtual_cluster_id=self.id,
        )
        self.state = VIRTUAL_CLUSTER_STATUS
        self.container_provider = container_provider
        self.container_provider_id = container_provider["id"]
        self.namespace = container_provider["info"]["eksInfo"]["namespace"]
        self.creation_date = iso_8601_datetime_without_milliseconds(
            datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        self.tags = tags

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield "id", self.id
        yield "name", self.name
        yield "arn", self.arn
        yield "state", self.state
        yield "containerProvider", self.container_provider
        yield "createdAt", self.creation_date
        yield "tags", self.tags

    def to_dict(self) -> dict[str, Any]:
        # Format for summary https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_DescribeVirtualCluster.html
        # (response syntax section)
        return {
            "id": self.id,
            "name": self.name,
            "arn": self.arn,
            "state": self.state,
            "containerProvider": self.container_provider,
            "createdAt": self.creation_date,
            "tags": self.tags,
        }


class FakeJob(BaseModel):
    def __init__(
        self,
        name: str,
        virtual_cluster_id: str,
        client_token: str,
        execution_role_arn: str,
        release_label: str,
        job_driver: str,
        configuration_overrides: dict[str, Any],
        account_id: str,
        region_name: str,
        aws_partition: str,
        tags: Optional[dict[str, str]],
    ):
        self.id = random_job_id()
        self.name = name
        self.virtual_cluster_id = virtual_cluster_id
        self.arn = JOB_ARN_TEMPLATE.format(
            partition=aws_partition,
            region=region_name,
            account_id=account_id,
            virtual_cluster_id=self.virtual_cluster_id,
            job_id=self.id,
        )
        self.state = JOB_STATUS
        self.client_token = client_token
        self.execution_role_arn = execution_role_arn
        self.release_label = release_label
        self.job_driver = job_driver
        self.configuration_overrides = configuration_overrides
        self.created_at = iso_8601_datetime_without_milliseconds(
            datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        self.created_by = None
        self.finished_at: Optional[str] = None
        self.state_details: Optional[str] = None
        self.failure_reason = None
        self.tags = tags

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield "id", self.id
        yield "name", self.name
        yield "virtualClusterId", self.virtual_cluster_id
        yield "arn", self.arn
        yield "state", self.state
        yield "clientToken", self.client_token
        yield "executionRoleArn", self.execution_role_arn
        yield "releaseLabel", self.release_label
        yield "configurationOverrides", self.release_label
        yield "jobDriver", self.job_driver
        yield "createdAt", self.created_at
        yield "createdBy", self.created_by
        yield "finishedAt", self.finished_at
        yield "stateDetails", self.state_details
        yield "failureReason", self.failure_reason
        yield "tags", self.tags

    def to_dict(self) -> dict[str, Any]:
        # Format for summary https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_DescribeJobRun.html
        # (response syntax section)
        return {
            "id": self.id,
            "name": self.name,
            "virtualClusterId": self.virtual_cluster_id,
            "arn": self.arn,
            "state": self.state,
            "clientToken": self.client_token,
            "executionRoleArn": self.execution_role_arn,
            "releaseLabel": self.release_label,
            "configurationOverrides": self.configuration_overrides,
            "jobDriver": self.job_driver,
            "createdAt": self.created_at,
            "createdBy": self.created_by,
            "finishedAt": self.finished_at,
            "stateDetails": self.state_details,
            "failureReason": self.failure_reason,
            "tags": self.tags,
        }


class FakeJobTemplate(BaseModel):
    def __init__(
        self,
        name: str,
        client_token: str,
        job_template_data: dict[str, Any],
        account_id: str,
        region_name: str,
        aws_partition: str,
        tags: Optional[dict[str, str]] = None,
        kms_key_arn: Optional[str] = None,
    ):
        self.id = random_id(size=25)
        self.name = name
        self.client_token = client_token
        self.job_template_data = job_template_data
        self.kms_key_arn = kms_key_arn
        self.arn = JOB_TEMPLATE_ARN_TEMPLATE.format(
            partition=aws_partition,
            region=region_name,
            account_id=account_id,
            job_template_id=self.id,
        )
        self.created_at = iso_8601_datetime_without_milliseconds(
            datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        self.created_by: Optional[str] = None
        self.tags = tags or {}

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "arn": self.arn,
            "createdAt": self.created_at,
            "jobTemplateData": self.job_template_data,
            "tags": self.tags,
        }
        if self.kms_key_arn:
            result["kmsKeyArn"] = self.kms_key_arn
        if self.created_by:
            result["createdBy"] = self.created_by
        return result


class FakeManagedEndpoint(BaseModel):
    def __init__(
        self,
        name: str,
        virtual_cluster_id: str,
        endpoint_type: str,
        release_label: str,
        execution_role_arn: str,
        client_token: str,
        account_id: str,
        region_name: str,
        aws_partition: str,
        certificate_arn: Optional[str] = None,
        configuration_overrides: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = random_id(size=17)
        self.name = name
        self.virtual_cluster_id = virtual_cluster_id
        self.type = endpoint_type
        self.release_label = release_label
        self.execution_role_arn = execution_role_arn
        self.client_token = client_token
        self.certificate_arn = certificate_arn
        self.configuration_overrides = configuration_overrides
        self.state = MANAGED_ENDPOINT_STATUS
        self.arn = MANAGED_ENDPOINT_ARN_TEMPLATE.format(
            partition=aws_partition,
            region=region_name,
            account_id=account_id,
            virtual_cluster_id=virtual_cluster_id,
            endpoint_id=self.id,
        )
        self.created_at = iso_8601_datetime_without_milliseconds(
            datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        self.tags = tags or {}

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "arn": self.arn,
            "virtualClusterId": self.virtual_cluster_id,
            "type": self.type,
            "state": self.state,
            "releaseLabel": self.release_label,
            "executionRoleArn": self.execution_role_arn,
            "createdAt": self.created_at,
            "tags": self.tags,
        }
        if self.certificate_arn:
            result["certificateArn"] = self.certificate_arn
        if self.configuration_overrides:
            result["configurationOverrides"] = self.configuration_overrides
        return result


class FakeSecurityConfiguration(BaseModel):
    def __init__(
        self,
        name: str,
        client_token: str,
        security_configuration_data: dict[str, Any],
        account_id: str,
        region_name: str,
        aws_partition: str,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = random_id(size=25)
        self.name = name
        self.client_token = client_token
        self.security_configuration_data = security_configuration_data
        self.arn = SECURITY_CONFIGURATION_ARN_TEMPLATE.format(
            partition=aws_partition,
            region=region_name,
            account_id=account_id,
            security_configuration_id=self.id,
        )
        self.created_at = iso_8601_datetime_without_milliseconds(
            datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        self.created_by: Optional[str] = None
        self.tags = tags or {}

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "arn": self.arn,
            "createdAt": self.created_at,
            "securityConfigurationData": self.security_configuration_data,
            "tags": self.tags,
        }
        if self.created_by:
            result["createdBy"] = self.created_by
        return result


class EMRContainersBackend(BaseBackend):
    """Implementation of EMRContainers APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.virtual_clusters: dict[str, FakeCluster] = {}
        self.virtual_cluster_count = 0
        self.jobs: dict[str, FakeJob] = {}
        self.job_count = 0
        self.job_templates: dict[str, FakeJobTemplate] = {}
        self.managed_endpoints: dict[str, FakeManagedEndpoint] = {}
        self.security_configurations: dict[str, FakeSecurityConfiguration] = {}
        self.partition = get_partition(region_name)

    def create_virtual_cluster(
        self,
        name: str,
        container_provider: dict[str, Any],
        client_token: str,
        tags: Optional[dict[str, str]] = None,
    ) -> FakeCluster:
        occupied_namespaces = [
            virtual_cluster.namespace
            for virtual_cluster in self.virtual_clusters.values()
        ]

        if container_provider["info"]["eksInfo"]["namespace"] in occupied_namespaces:
            raise ValidationException(
                "A virtual cluster already exists in the given namespace"
            )

        virtual_cluster = FakeCluster(
            name=name,
            container_provider=container_provider,
            client_token=client_token,
            tags=tags,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )

        self.virtual_clusters[virtual_cluster.id] = virtual_cluster
        self.virtual_cluster_count += 1
        return virtual_cluster

    def delete_virtual_cluster(self, cluster_id: str) -> FakeCluster:
        if cluster_id not in self.virtual_clusters:
            raise ValidationException("VirtualCluster does not exist")

        self.virtual_clusters[cluster_id].state = "TERMINATED"
        return self.virtual_clusters[cluster_id]

    def describe_virtual_cluster(self, cluster_id: str) -> dict[str, Any]:
        if cluster_id not in self.virtual_clusters:
            raise ValidationException(f"Virtual cluster {cluster_id} doesn't exist.")

        return self.virtual_clusters[cluster_id].to_dict()

    def list_virtual_clusters(
        self,
        container_provider_id: str,
        container_provider_type: str,
        created_after: str,
        created_before: str,
        states: Optional[list[str]],
        max_results: int,
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        virtual_clusters = [
            virtual_cluster.to_dict()
            for virtual_cluster in self.virtual_clusters.values()
        ]

        if container_provider_id:
            virtual_clusters = [
                virtual_cluster
                for virtual_cluster in virtual_clusters
                if virtual_cluster["containerProvider"]["id"] == container_provider_id
            ]

        if container_provider_type:
            virtual_clusters = [
                virtual_cluster
                for virtual_cluster in virtual_clusters
                if virtual_cluster["containerProvider"]["type"]
                == container_provider_type
            ]

        if created_after:
            virtual_clusters = [
                virtual_cluster
                for virtual_cluster in virtual_clusters
                if virtual_cluster["createdAt"] >= created_after
            ]

        if created_before:
            virtual_clusters = [
                virtual_cluster
                for virtual_cluster in virtual_clusters
                if virtual_cluster["createdAt"] <= created_before
            ]

        if states:
            virtual_clusters = [
                virtual_cluster
                for virtual_cluster in virtual_clusters
                if virtual_cluster["state"] in states
            ]
        sort_key = "name"
        return paginated_list(virtual_clusters, sort_key, max_results, next_token)

    def start_job_run(
        self,
        name: str,
        virtual_cluster_id: str,
        client_token: str,
        execution_role_arn: str,
        release_label: str,
        job_driver: str,
        configuration_overrides: dict[str, Any],
        tags: dict[str, str],
    ) -> FakeJob:
        if virtual_cluster_id not in self.virtual_clusters.keys():
            raise ResourceNotFoundException(
                f"Virtual cluster {virtual_cluster_id} doesn't exist."
            )

        if not re.match(
            r"emr-[0-9]{1}\.[0-9]{1,2}\.0-(latest|[0-9]{8})", release_label
        ):
            raise ResourceNotFoundException(f"Release {release_label} doesn't exist.")

        job = FakeJob(
            name=name,
            virtual_cluster_id=virtual_cluster_id,
            client_token=client_token,
            execution_role_arn=execution_role_arn,
            release_label=release_label,
            job_driver=job_driver,
            configuration_overrides=configuration_overrides,
            tags=tags,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )

        self.jobs[job.id] = job
        self.job_count += 1
        return job

    def cancel_job_run(self, job_id: str, virtual_cluster_id: str) -> FakeJob:
        if not re.match(r"[a-z,A-Z,0-9]{19}", job_id):
            raise ValidationException("Invalid job run short id")

        if job_id not in self.jobs.keys():
            raise ResourceNotFoundException(f"Job run {job_id} doesn't exist.")

        if virtual_cluster_id != self.jobs[job_id].virtual_cluster_id:
            raise ResourceNotFoundException(f"Job run {job_id} doesn't exist.")

        if self.jobs[job_id].state in [
            "FAILED",
            "CANCELLED",
            "CANCEL_PENDING",
            "COMPLETED",
        ]:
            raise ValidationException(f"Job run {job_id} is not in a cancellable state")

        job = self.jobs[job_id]
        job.state = "CANCELLED"
        job.finished_at = iso_8601_datetime_without_milliseconds(
            datetime.today().replace(hour=0, minute=1, second=0, microsecond=0)
        )
        job.state_details = "JobRun CANCELLED successfully."

        return job

    def list_job_runs(
        self,
        virtual_cluster_id: str,
        created_before: str,
        created_after: str,
        name: str,
        states: Optional[list[str]],
        max_results: int,
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        jobs = [job.to_dict() for job in self.jobs.values()]

        jobs = [job for job in jobs if job["virtualClusterId"] == virtual_cluster_id]

        if created_after:
            jobs = [job for job in jobs if job["createdAt"] >= created_after]

        if created_before:
            jobs = [job for job in jobs if job["createdAt"] <= created_before]

        if states:
            jobs = [job for job in jobs if job["state"] in states]

        if name:
            jobs = [job for job in jobs if job["name"] in name]

        sort_key = "id"
        return paginated_list(jobs, sort_key, max_results, next_token)

    def describe_job_run(self, job_id: str, virtual_cluster_id: str) -> dict[str, Any]:
        if not re.match(r"[a-z,A-Z,0-9]{19}", job_id):
            raise ValidationException("Invalid job run short id")

        if job_id not in self.jobs.keys():
            raise ResourceNotFoundException(f"Job run {job_id} doesn't exist.")

        if virtual_cluster_id != self.jobs[job_id].virtual_cluster_id:
            raise ResourceNotFoundException(f"Job run {job_id} doesn't exist.")

        return self.jobs[job_id].to_dict()

    # --- JobTemplate ---

    def create_job_template(
        self,
        name: str,
        client_token: str,
        job_template_data: dict[str, Any],
        tags: Optional[dict[str, str]] = None,
        kms_key_arn: Optional[str] = None,
    ) -> FakeJobTemplate:
        template = FakeJobTemplate(
            name=name,
            client_token=client_token,
            job_template_data=job_template_data,
            tags=tags,
            kms_key_arn=kms_key_arn,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )
        self.job_templates[template.id] = template
        return template

    def delete_job_template(self, template_id: str) -> FakeJobTemplate:
        if template_id not in self.job_templates:
            raise ResourceNotFoundException(
                f"Job template {template_id} doesn't exist."
            )
        return self.job_templates.pop(template_id)

    def describe_job_template(self, template_id: str) -> dict[str, Any]:
        if template_id not in self.job_templates:
            raise ResourceNotFoundException(
                f"Job template {template_id} doesn't exist."
            )
        return self.job_templates[template_id].to_dict()

    def list_job_templates(
        self,
        created_after: Optional[str],
        created_before: Optional[str],
        max_results: int,
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        templates = [t.to_dict() for t in self.job_templates.values()]
        if created_after:
            templates = [t for t in templates if t["createdAt"] >= created_after]
        if created_before:
            templates = [t for t in templates if t["createdAt"] <= created_before]
        return paginated_list(templates, "id", max_results, next_token)

    # --- ManagedEndpoint ---

    def create_managed_endpoint(
        self,
        name: str,
        virtual_cluster_id: str,
        endpoint_type: str,
        release_label: str,
        execution_role_arn: str,
        client_token: str,
        certificate_arn: Optional[str] = None,
        configuration_overrides: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> FakeManagedEndpoint:
        if virtual_cluster_id not in self.virtual_clusters:
            raise ResourceNotFoundException(
                f"Virtual cluster {virtual_cluster_id} doesn't exist."
            )
        endpoint = FakeManagedEndpoint(
            name=name,
            virtual_cluster_id=virtual_cluster_id,
            endpoint_type=endpoint_type,
            release_label=release_label,
            execution_role_arn=execution_role_arn,
            client_token=client_token,
            certificate_arn=certificate_arn,
            configuration_overrides=configuration_overrides,
            tags=tags,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )
        self.managed_endpoints[endpoint.id] = endpoint
        return endpoint

    def delete_managed_endpoint(
        self, endpoint_id: str, virtual_cluster_id: str
    ) -> FakeManagedEndpoint:
        if endpoint_id not in self.managed_endpoints:
            raise ResourceNotFoundException(
                f"Managed endpoint {endpoint_id} doesn't exist."
            )
        endpoint = self.managed_endpoints[endpoint_id]
        if endpoint.virtual_cluster_id != virtual_cluster_id:
            raise ResourceNotFoundException(
                f"Managed endpoint {endpoint_id} doesn't exist."
            )
        self.managed_endpoints.pop(endpoint_id)
        endpoint.state = "TERMINATED"
        return endpoint

    def describe_managed_endpoint(
        self, endpoint_id: str, virtual_cluster_id: str
    ) -> dict[str, Any]:
        if endpoint_id not in self.managed_endpoints:
            raise ResourceNotFoundException(
                f"Managed endpoint {endpoint_id} doesn't exist."
            )
        endpoint = self.managed_endpoints[endpoint_id]
        if endpoint.virtual_cluster_id != virtual_cluster_id:
            raise ResourceNotFoundException(
                f"Managed endpoint {endpoint_id} doesn't exist."
            )
        return endpoint.to_dict()

    def list_managed_endpoints(
        self,
        virtual_cluster_id: str,
        created_after: Optional[str],
        created_before: Optional[str],
        states: Optional[list[str]],
        max_results: int,
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        endpoints = [
            e.to_dict()
            for e in self.managed_endpoints.values()
            if e.virtual_cluster_id == virtual_cluster_id
        ]
        if created_after:
            endpoints = [e for e in endpoints if e["createdAt"] >= created_after]
        if created_before:
            endpoints = [e for e in endpoints if e["createdAt"] <= created_before]
        if states:
            endpoints = [e for e in endpoints if e["state"] in states]
        return paginated_list(endpoints, "id", max_results, next_token)

    # --- SecurityConfiguration ---

    def create_security_configuration(
        self,
        name: str,
        client_token: str,
        security_configuration_data: dict[str, Any],
        tags: Optional[dict[str, str]] = None,
    ) -> FakeSecurityConfiguration:
        config = FakeSecurityConfiguration(
            name=name,
            client_token=client_token,
            security_configuration_data=security_configuration_data,
            tags=tags,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )
        self.security_configurations[config.id] = config
        return config

    def delete_security_configuration(
        self, security_configuration_id: str
    ) -> FakeSecurityConfiguration:
        if security_configuration_id not in self.security_configurations:
            raise ResourceNotFoundException(
                f"Security configuration {security_configuration_id} doesn't exist."
            )
        return self.security_configurations.pop(security_configuration_id)

    def describe_security_configuration(
        self, security_configuration_id: str
    ) -> dict[str, Any]:
        if security_configuration_id not in self.security_configurations:
            raise ResourceNotFoundException(
                f"Security configuration {security_configuration_id} doesn't exist."
            )
        return self.security_configurations[security_configuration_id].to_dict()

    def list_security_configurations(
        self,
        created_after: Optional[str],
        created_before: Optional[str],
        max_results: int,
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        configs = [c.to_dict() for c in self.security_configurations.values()]
        if created_after:
            configs = [c for c in configs if c["createdAt"] >= created_after]
        if created_before:
            configs = [c for c in configs if c["createdAt"] <= created_before]
        return paginated_list(configs, "id", max_results, next_token)


emrcontainers_backends = BackendDict(EMRContainersBackend, "emr-containers")
