"""Handles incoming emrcontainers requests, invokes methods, returns responses."""

import json

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import EMRContainersBackend, emrcontainers_backends

DEFAULT_MAX_RESULTS = 100
DEFAULT_NEXT_TOKEN = ""
DEFAULT_CONTAINER_PROVIDER_TYPE = "EKS"


class EMRContainersResponse(BaseResponse):
    """Handler for EMRContainers requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="emr-containers")

    @property
    def emrcontainers_backend(self) -> EMRContainersBackend:
        """Return backend instance specific for this region."""
        return emrcontainers_backends[self.current_account][self.region]

    def create_virtual_cluster(self) -> TYPE_RESPONSE:
        name = self._get_param("name")
        container_provider = self._get_param("containerProvider")
        client_token = self._get_param("clientToken")
        tags = self._get_param("tags")

        virtual_cluster = self.emrcontainers_backend.create_virtual_cluster(
            name=name,
            container_provider=container_provider,
            client_token=client_token,
            tags=tags,
        )
        return 200, {}, json.dumps(dict(virtual_cluster))

    def delete_virtual_cluster(self) -> TYPE_RESPONSE:
        cluster_id = self._get_param("virtualClusterId")

        virtual_cluster = self.emrcontainers_backend.delete_virtual_cluster(
            cluster_id=cluster_id
        )
        return 200, {}, json.dumps(dict(virtual_cluster))

    def describe_virtual_cluster(self) -> TYPE_RESPONSE:
        cluster_id = self._get_param("virtualClusterId")

        virtual_cluster = self.emrcontainers_backend.describe_virtual_cluster(
            cluster_id=cluster_id
        )
        response = {"virtualCluster": virtual_cluster}
        return 200, {}, json.dumps(response)

    def list_virtual_clusters(self) -> TYPE_RESPONSE:
        container_provider_id = self._get_param("containerProviderId")
        container_provider_type = self._get_param(
            "containerProviderType", DEFAULT_CONTAINER_PROVIDER_TYPE
        )
        created_after = self._get_param("createdAfter")
        created_before = self._get_param("createdBefore")
        states = self.querystring.get("states", [])
        max_results = self._get_int_param("maxResults", DEFAULT_MAX_RESULTS)
        next_token = self._get_param("nextToken", DEFAULT_NEXT_TOKEN)

        virtual_clusters, next_token = self.emrcontainers_backend.list_virtual_clusters(
            container_provider_id=container_provider_id,
            container_provider_type=container_provider_type,
            created_after=created_after,
            created_before=created_before,
            states=states,
            max_results=max_results,
            next_token=next_token,
        )

        response = {"virtualClusters": virtual_clusters, "nextToken": next_token}
        return 200, {}, json.dumps(response)

    def start_job_run(self) -> TYPE_RESPONSE:
        name = self._get_param("name")
        virtual_cluster_id = self._get_param("virtualClusterId")
        client_token = self._get_param("clientToken")
        execution_role_arn = self._get_param("executionRoleArn")
        release_label = self._get_param("releaseLabel")
        job_driver = self._get_param("jobDriver")
        configuration_overrides = self._get_param("configurationOverrides")
        tags = self._get_param("tags")

        job = self.emrcontainers_backend.start_job_run(
            name=name,
            virtual_cluster_id=virtual_cluster_id,
            client_token=client_token,
            execution_role_arn=execution_role_arn,
            release_label=release_label,
            job_driver=job_driver,
            configuration_overrides=configuration_overrides,
            tags=tags,
        )
        return 200, {}, json.dumps(dict(job))

    def cancel_job_run(self) -> TYPE_RESPONSE:
        job_id = self._get_param("jobRunId")
        virtual_cluster_id = self._get_param("virtualClusterId")

        job = self.emrcontainers_backend.cancel_job_run(
            job_id=job_id, virtual_cluster_id=virtual_cluster_id
        )
        return 200, {}, json.dumps(dict(job))

    def list_job_runs(self) -> TYPE_RESPONSE:
        virtual_cluster_id = self._get_param("virtualClusterId")
        created_before = self._get_param("createdBefore")
        created_after = self._get_param("createdAfter")
        name = self._get_param("name")
        states = self.querystring.get("states", [])
        max_results = self._get_int_param("maxResults", DEFAULT_MAX_RESULTS)
        next_token = self._get_param("nextToken", DEFAULT_NEXT_TOKEN)

        job_runs, next_token = self.emrcontainers_backend.list_job_runs(
            virtual_cluster_id=virtual_cluster_id,
            created_before=created_before,
            created_after=created_after,
            name=name,
            states=states,
            max_results=max_results,
            next_token=next_token,
        )

        response = {"jobRuns": job_runs, "nextToken": next_token}
        return 200, {}, json.dumps(response)

    def describe_job_run(self) -> TYPE_RESPONSE:
        job_id = self._get_param("jobRunId")
        virtual_cluster_id = self._get_param("virtualClusterId")

        job_run = self.emrcontainers_backend.describe_job_run(
            job_id=job_id, virtual_cluster_id=virtual_cluster_id
        )

        response = {"jobRun": job_run}
        return 200, {}, json.dumps(response)

    # --- JobTemplate ---

    def create_job_template(self) -> TYPE_RESPONSE:
        name = self._get_param("name")
        client_token = self._get_param("clientToken")
        job_template_data = self._get_param("jobTemplateData")
        tags = self._get_param("tags")
        kms_key_arn = self._get_param("kmsKeyArn")

        template = self.emrcontainers_backend.create_job_template(
            name=name,
            client_token=client_token,
            job_template_data=job_template_data or {},
            tags=tags,
            kms_key_arn=kms_key_arn,
        )
        return 200, {}, json.dumps({"id": template.id, "name": template.name, "arn": template.arn})

    def delete_job_template(self) -> TYPE_RESPONSE:
        template_id = self._get_param("templateId")
        template = self.emrcontainers_backend.delete_job_template(
            template_id=template_id
        )
        return 200, {}, json.dumps({"id": template.id})

    def describe_job_template(self) -> TYPE_RESPONSE:
        template_id = self._get_param("templateId")
        template = self.emrcontainers_backend.describe_job_template(
            template_id=template_id
        )
        return 200, {}, json.dumps({"jobTemplate": template})

    def list_job_templates(self) -> TYPE_RESPONSE:
        created_after = self._get_param("createdAfter")
        created_before = self._get_param("createdBefore")
        max_results = self._get_int_param("maxResults", DEFAULT_MAX_RESULTS)
        next_token = self._get_param("nextToken", DEFAULT_NEXT_TOKEN)

        templates, next_token = self.emrcontainers_backend.list_job_templates(
            created_after=created_after,
            created_before=created_before,
            max_results=max_results,
            next_token=next_token,
        )
        return 200, {}, json.dumps({"templates": templates, "nextToken": next_token})

    # --- ManagedEndpoint ---

    def create_managed_endpoint(self) -> TYPE_RESPONSE:
        name = self._get_param("name")
        virtual_cluster_id = self._get_param("virtualClusterId")
        endpoint_type = self._get_param("type")
        release_label = self._get_param("releaseLabel")
        execution_role_arn = self._get_param("executionRoleArn")
        client_token = self._get_param("clientToken")
        certificate_arn = self._get_param("certificateArn")
        configuration_overrides = self._get_param("configurationOverrides")
        tags = self._get_param("tags")

        endpoint = self.emrcontainers_backend.create_managed_endpoint(
            name=name,
            virtual_cluster_id=virtual_cluster_id,
            endpoint_type=endpoint_type,
            release_label=release_label,
            execution_role_arn=execution_role_arn,
            client_token=client_token,
            certificate_arn=certificate_arn,
            configuration_overrides=configuration_overrides,
            tags=tags,
        )
        return 200, {}, json.dumps({
            "id": endpoint.id,
            "name": endpoint.name,
            "arn": endpoint.arn,
            "virtualClusterId": endpoint.virtual_cluster_id,
        })

    def delete_managed_endpoint(self) -> TYPE_RESPONSE:
        endpoint_id = self._get_param("endpointId")
        virtual_cluster_id = self._get_param("virtualClusterId")

        endpoint = self.emrcontainers_backend.delete_managed_endpoint(
            endpoint_id=endpoint_id, virtual_cluster_id=virtual_cluster_id
        )
        return 200, {}, json.dumps({"id": endpoint.id, "virtualClusterId": endpoint.virtual_cluster_id})

    def describe_managed_endpoint(self) -> TYPE_RESPONSE:
        endpoint_id = self._get_param("endpointId")
        virtual_cluster_id = self._get_param("virtualClusterId")

        endpoint = self.emrcontainers_backend.describe_managed_endpoint(
            endpoint_id=endpoint_id, virtual_cluster_id=virtual_cluster_id
        )
        return 200, {}, json.dumps({"endpoint": endpoint})

    def list_managed_endpoints(self) -> TYPE_RESPONSE:
        virtual_cluster_id = self._get_param("virtualClusterId")
        created_after = self._get_param("createdAfter")
        created_before = self._get_param("createdBefore")
        states = self.querystring.get("states", [])
        max_results = self._get_int_param("maxResults", DEFAULT_MAX_RESULTS)
        next_token = self._get_param("nextToken", DEFAULT_NEXT_TOKEN)

        endpoints, next_token = self.emrcontainers_backend.list_managed_endpoints(
            virtual_cluster_id=virtual_cluster_id,
            created_after=created_after,
            created_before=created_before,
            states=states,
            max_results=max_results,
            next_token=next_token,
        )
        return 200, {}, json.dumps({"endpoints": endpoints, "nextToken": next_token})

    # --- SecurityConfiguration ---

    def create_security_configuration(self) -> TYPE_RESPONSE:
        name = self._get_param("name")
        client_token = self._get_param("clientToken")
        security_configuration_data = self._get_param("securityConfigurationData")
        tags = self._get_param("tags")

        config = self.emrcontainers_backend.create_security_configuration(
            name=name,
            client_token=client_token,
            security_configuration_data=security_configuration_data or {},
            tags=tags,
        )
        return 200, {}, json.dumps({"id": config.id, "name": config.name, "arn": config.arn})

    def delete_security_configuration(self) -> TYPE_RESPONSE:
        security_configuration_id = self._get_param("securityConfigurationId")
        config = self.emrcontainers_backend.delete_security_configuration(
            security_configuration_id=security_configuration_id
        )
        return 200, {}, json.dumps({"id": config.id})

    def describe_security_configuration(self) -> TYPE_RESPONSE:
        security_configuration_id = self._get_param("securityConfigurationId")
        config = self.emrcontainers_backend.describe_security_configuration(
            security_configuration_id=security_configuration_id
        )
        return 200, {}, json.dumps({"securityConfiguration": config})

    def list_security_configurations(self) -> TYPE_RESPONSE:
        created_after = self._get_param("createdAfter")
        created_before = self._get_param("createdBefore")
        max_results = self._get_int_param("maxResults", DEFAULT_MAX_RESULTS)
        next_token = self._get_param("nextToken", DEFAULT_NEXT_TOKEN)

        configs, next_token = self.emrcontainers_backend.list_security_configurations(
            created_after=created_after,
            created_before=created_before,
            max_results=max_results,
            next_token=next_token,
        )
        return 200, {}, json.dumps({"securityConfigurations": configs, "nextToken": next_token})
