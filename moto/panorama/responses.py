import json
import urllib

from moto.core.responses import BaseResponse

from .models import PanoramaBackend, panorama_backends


class PanoramaResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="panorama")

    @property
    def panorama_backend(self) -> PanoramaBackend:
        return panorama_backends[self.current_account][self.region]

    def provision_device(self) -> str:
        description = self._get_param("Description")
        name = self._get_param("Name")
        networking_configuration = self._get_param("NetworkingConfiguration")
        tags = self._get_param("Tags")
        device = self.panorama_backend.provision_device(
            description=description, name=name,
            networking_configuration=networking_configuration, tags=tags,
        )
        return json.dumps(device.response_provision)

    def describe_device(self) -> str:
        device_id = urllib.parse.unquote(self._get_param("DeviceId"))
        device = self.panorama_backend.describe_device(device_id=device_id)
        return json.dumps(device.response_object())

    def list_devices(self) -> str:
        device_aggregated_status_filter = self._get_param("DeviceAggregatedStatusFilter")
        max_results = self._get_int_param("MaxResults")
        name_filter = self._get_param("NameFilter")
        next_token = self._get_param("NextToken")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        list_devices, next_token = self.panorama_backend.list_devices(
            device_aggregated_status_filter=device_aggregated_status_filter,
            max_results=max_results, name_filter=name_filter,
            next_token=next_token, sort_by=sort_by, sort_order=sort_order,
        )
        return json.dumps({
            "Devices": [device.response_listed() for device in list_devices],
            "NextToken": next_token,
        })

    def update_device_metadata(self) -> str:
        device_id = urllib.parse.unquote(self._get_param("DeviceId"))
        description = self._get_param("Description")
        device = self.panorama_backend.update_device_metadata(
            device_id=device_id, description=description
        )
        return json.dumps(device.response_updated)

    def delete_device(self) -> str:
        device_id = urllib.parse.unquote(self._get_param("DeviceId"))
        device = self.panorama_backend.delete_device(device_id=device_id)
        return json.dumps(device.response_deleted)

    def create_node_from_template_job(self) -> str:
        job_tags = self._get_param("JobTags")
        node_description = self._get_param("NodeDescription")
        node_name = self._get_param("NodeName")
        output_package_name = self._get_param("OutputPackageName")
        output_package_version = self._get_param("OutputPackageVersion")
        template_parameters = self._get_param("TemplateParameters")
        template_type = self._get_param("TemplateType")
        node = self.panorama_backend.create_node_from_template_job(
            job_tags=job_tags, node_description=node_description,
            node_name=node_name, output_package_name=output_package_name,
            output_package_version=output_package_version,
            template_parameters=template_parameters, template_type=template_type,
        )
        return json.dumps(node.response_created())

    def describe_node_from_template_job(self) -> str:
        job_id = self._get_param("JobId")
        node = self.panorama_backend.describe_node_from_template_job(job_id=job_id)
        return json.dumps(node.response_described())

    def list_node_from_template_jobs(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        jobs, next_token = self.panorama_backend.list_node_from_template_jobs(
            max_results=max_results, next_token=next_token,
        )
        return json.dumps({
            "NodeFromTemplateJobs": [job.response_listed() for job in jobs],
            "NextToken": next_token,
        })

    def list_nodes(self) -> str:
        category = self._get_param("category")
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        list_nodes, next_token = self.panorama_backend.list_nodes(
            category=category, max_results=max_results, next_token=next_token
        )
        return json.dumps({
            "Nodes": [node.response_listed() for node in list_nodes],
            "NextToken": next_token,
        })

    def describe_node(self) -> str:
        node_id = urllib.parse.unquote(self._get_param("NodeId"))
        node = self.panorama_backend.describe_node(node_id=node_id)
        return json.dumps(node.response_object())

    def create_application_instance(self) -> str:
        application_instance_id_to_replace = self._get_param("ApplicationInstanceIdToReplace")
        default_runtime_context_device = self._get_param("DefaultRuntimeContextDevice")
        description = self._get_param("Description")
        manifest_overrides_payload = self._get_param("ManifestOverridesPayload")
        manifest_payload = self._get_param("ManifestPayload")
        name = self._get_param("Name")
        runtime_role_arn = self._get_param("RuntimeRoleArn")
        tags = self._get_param("Tags")
        application_instance = self.panorama_backend.create_application_instance(
            application_instance_id_to_replace=application_instance_id_to_replace,
            default_runtime_context_device=default_runtime_context_device,
            description=description, manifest_overrides_payload=manifest_overrides_payload,
            manifest_payload=manifest_payload, name=name,
            runtime_role_arn=runtime_role_arn, tags=tags,
        )
        return json.dumps(application_instance.response_created())

    def describe_application_instance(self) -> str:
        application_instance_id = self._get_param("ApplicationInstanceId")
        application_instance = self.panorama_backend.describe_application_instance(
            application_instance_id=application_instance_id
        )
        return json.dumps(application_instance.response_describe())

    def describe_application_instance_details(self) -> str:
        return self.describe_application_instance()

    def remove_application_instance(self) -> str:
        application_instance_id = urllib.parse.unquote(
            self._get_param("ApplicationInstanceId")
        )
        self.panorama_backend.remove_application_instance(
            application_instance_id=application_instance_id
        )
        return json.dumps({})

    def list_application_instances(self) -> str:
        device_id = self._get_param("deviceId")
        max_results = self._get_int_param("maxResults")
        status_filter = self._get_param("statusFilter")
        next_token = self._get_param("nextToken")
        list_application_instances, next_token = (
            self.panorama_backend.list_application_instances(
                device_id=device_id, max_results=max_results,
                status_filter=status_filter, next_token=next_token,
            )
        )
        return json.dumps({
            "ApplicationInstances": [
                ai.response_describe() for ai in list_application_instances
            ],
            "NextToken": next_token,
        })

    def create_package(self) -> str:
        package_name = self._get_param("PackageName")
        tags = self._get_param("Tags")
        pkg = self.panorama_backend.create_package(package_name=package_name, tags=tags)
        return json.dumps(pkg.response_created())

    def describe_package(self) -> str:
        package_id = urllib.parse.unquote(self._get_param("PackageId"))
        pkg = self.panorama_backend.describe_package(package_id=package_id)
        return json.dumps(pkg.response_describe())

    def delete_package(self) -> str:
        package_id = urllib.parse.unquote(self._get_param("PackageId"))
        self.panorama_backend.delete_package(package_id=package_id)
        return json.dumps({})

    def list_packages(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        packages, next_token = self.panorama_backend.list_packages(
            max_results=max_results, next_token=next_token,
        )
        return json.dumps({
            "Packages": [pkg.response_listed() for pkg in packages],
            "NextToken": next_token,
        })

    def create_package_import_job(self) -> str:
        client_token = self._get_param("ClientToken")
        input_config = self._get_param("InputConfig")
        job_type = self._get_param("JobType")
        output_config = self._get_param("OutputConfig")
        job_tags = self._get_param("JobTags")
        job = self.panorama_backend.create_package_import_job(
            client_token=client_token, input_config=input_config,
            job_type=job_type, output_config=output_config, job_tags=job_tags,
        )
        return json.dumps(job.response_created())

    def describe_package_import_job(self) -> str:
        job_id = urllib.parse.unquote(self._get_param("JobId"))
        job = self.panorama_backend.describe_package_import_job(job_id=job_id)
        return json.dumps(job.response_describe())

    def list_package_import_jobs(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        jobs, next_token = self.panorama_backend.list_package_import_jobs(
            max_results=max_results, next_token=next_token,
        )
        return json.dumps({
            "PackageImportJobs": [job.response_listed() for job in jobs],
            "NextToken": next_token,
        })

    def create_job_for_devices(self) -> str:
        device_ids = self._get_param("DeviceIds")
        device_job_config = self._get_param("DeviceJobConfig")
        job_type = self._get_param("JobType")
        jobs = self.panorama_backend.create_job_for_devices(
            device_ids=device_ids,
            device_job_config=device_job_config,
            job_type=job_type,
        )
        return json.dumps({"Jobs": [{"DeviceId": j.device_id, "JobId": j.job_id} for j in jobs]})

    def describe_device_job(self) -> str:
        job_id = urllib.parse.unquote(self._get_param("JobId"))
        job = self.panorama_backend.describe_device_job(job_id=job_id)
        return json.dumps(job.response_object())

    def list_devices_jobs(self) -> str:
        device_id = self._get_param("DeviceId")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        jobs, next_token = self.panorama_backend.list_devices_jobs(
            device_id=device_id,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({
            "DeviceJobs": [j.response_listed() for j in jobs],
            "NextToken": next_token,
        })

    def register_package_version(self) -> str:
        owner_account = self._get_param("OwnerAccount")
        package_id = urllib.parse.unquote(self._get_param("PackageId"))
        package_version = urllib.parse.unquote(self._get_param("PackageVersion"))
        patch_version = urllib.parse.unquote(self._get_param("PatchVersion"))
        mark_latest = self._get_param("MarkLatest") or False
        self.panorama_backend.register_package_version(
            owner_account=owner_account,
            package_id=package_id,
            package_version=package_version,
            patch_version=patch_version,
            mark_latest=mark_latest,
        )
        return json.dumps({})

    def deregister_package_version(self) -> str:
        owner_account = self._get_param("OwnerAccount")
        package_id = urllib.parse.unquote(self._get_param("PackageId"))
        package_version = urllib.parse.unquote(self._get_param("PackageVersion"))
        patch_version = urllib.parse.unquote(self._get_param("PatchVersion"))
        updated_latest_patch_version = self._get_param("UpdatedLatestPatchVersion")
        self.panorama_backend.deregister_package_version(
            owner_account=owner_account,
            package_id=package_id,
            package_version=package_version,
            patch_version=patch_version,
            updated_latest_patch_version=updated_latest_patch_version,
        )
        return json.dumps({})

    def describe_package_version(self) -> str:
        owner_account = self._get_param("ownerAccount")
        package_id = urllib.parse.unquote(self._get_param("PackageId"))
        package_version = urllib.parse.unquote(self._get_param("PackageVersion"))
        patch_version = self._get_param("PatchVersion")
        if patch_version:
            patch_version = urllib.parse.unquote(patch_version)
        pv = self.panorama_backend.describe_package_version(
            owner_account=owner_account,
            package_id=package_id,
            package_version=package_version,
            patch_version=patch_version,
        )
        return json.dumps(pv.response_object())

    def list_application_instance_dependencies(self) -> str:
        application_instance_id = urllib.parse.unquote(
            self._get_param("ApplicationInstanceId")
        )
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        deps, next_token = self.panorama_backend.list_application_instance_dependencies(
            application_instance_id=application_instance_id,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"PackageObjects": deps, "NextToken": next_token})

    def list_application_instance_node_instances(self) -> str:
        application_instance_id = urllib.parse.unquote(
            self._get_param("ApplicationInstanceId")
        )
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        nodes, next_token = self.panorama_backend.list_application_instance_node_instances(
            application_instance_id=application_instance_id,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"NodeInstances": nodes, "NextToken": next_token})

    def signal_application_instance_node_instances(self) -> str:
        application_instance_id = urllib.parse.unquote(
            self._get_param("ApplicationInstanceId")
        )
        node_signals = self._get_param("NodeSignals")
        result_id = self.panorama_backend.signal_application_instance_node_instances(
            application_instance_id=application_instance_id,
            node_signals=node_signals,
        )
        return json.dumps({"ApplicationInstanceId": result_id})

    def list_tags_for_resource(self) -> str:
        resource_arn = urllib.parse.unquote(self._get_param("ResourceArn"))
        tags = self.panorama_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"Tags": tags})

    def tag_resource(self) -> str:
        resource_arn = urllib.parse.unquote(self._get_param("ResourceArn"))
        tags = self._get_param("Tags")
        self.panorama_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = urllib.parse.unquote(self._get_param("ResourceArn"))
        tag_keys = self._get_param("tagKeys")
        if tag_keys is None:
            tag_keys = []
        self.panorama_backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)
        return json.dumps({})
