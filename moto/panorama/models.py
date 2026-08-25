import base64
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.moto_api._internal.managed_state_model import ManagedState
from moto.panorama.utils import (
    arn_formatter,
    deep_convert_datetime_to_isoformat,
    generate_package_id,
    hash_name,
)
from moto.utilities.paginator import paginate

from .exceptions import (
    ResourceNotFoundException,
    ValidationError,
)

PAGINATION_MODEL = {
    "list_devices": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 123,
        "unique_attribute": "device_id",
    },
    "list_nodes": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 123,
        "unique_attribute": "package_id",
    },
    "list_application_instances": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 123,
        "unique_attribute": "application_instance_id",
    },
    "list_packages": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 123,
        "unique_attribute": "package_id",
    },
    "list_package_import_jobs": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 123,
        "unique_attribute": "job_id",
    },
    "list_node_from_template_jobs": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 123,
        "unique_attribute": "job_id",
    },
}


class BaseObject(BaseModel):
    def camelCase(self, key: str) -> str:
        words = []
        for word in key.split("_"):
            words.append(word.title())
        return "".join(words)

    def update(self, details_json: str) -> None:
        details = json.loads(details_json)
        for k in details.keys():
            setattr(self, k, details[k])

    def gen_response_object(self) -> dict[str, Any]:
        response_object: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if "_" in key:
                response_object[self.camelCase(key)] = value
            else:
                response_object[key[0].upper() + key[1:]] = value
        return response_object

    def response_object(self) -> dict[str, Any]:
        return self.gen_response_object()


class Device(BaseObject):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        description: Optional[str],
        name: str,
        network_configuration: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> None:
        self.__device_aggregated_status_manager = ManagedState(
            model_name=f"panorama::device_{name}_aggregated_status",
            transitions=[
                ("NOT-A-STATUS", "AWAITING_PROVISIONING"),
                ("AWAITING_PROVISIONING", "PENDING"),
                ("PENDING", "ONLINE"),
            ],
        )
        self.__device_provisioning_status_manager = ManagedState(
            model_name=f"panorama::device_{name}_provisioning_status",
            transitions=[
                ("NOT-A-STATUS", "AWAITING_PROVISIONING"),
                ("AWAITING_PROVISIONING", "PENDING"),
                ("PENDING", "SUCCEEDED"),
            ],
        )
        self.account_id = account_id
        self.region_name = region_name
        self.description = description
        self.name = name
        self.network_configuration = network_configuration
        self.tags = tags

        self.certificates = base64.b64encode(b"certificate").decode("utf-8")
        self.arn = arn_formatter("device", self.name, self.account_id, self.region_name)
        self.device_id = f"device-{hash_name(name)}"
        self.iot_thing_name = ""

        self.alternate_softwares = [{"Version": "0.2.1"}]
        self.brand: str = "AWS_PANORAMA"
        self.created_time = datetime.now(timezone.utc)
        self.last_updated_time = datetime.now(timezone.utc)
        self.current_networking_status = {
            "Ethernet0Status": {
                "ConnectionStatus": "CONNECTED",
                "HwAddress": "8C:0F:5F:60:F5:C4",
                "IpAddress": "192.168.1.300/24",
            },
            "Ethernet1Status": {
                "ConnectionStatus": "NOT_CONNECTED",
                "HwAddress": "8C:0F:6F:60:F4:F1",
                "IpAddress": "--",
            },
            "LastUpdatedTime": datetime.now(timezone.utc),
            "NtpStatus": {
                "ConnectionStatus": "CONNECTED",
                "IpAddress": "91.224.149.41:123",
                "NtpServerName": "0.pool.ntp.org",
            },
        }
        self.current_software = "6.2.1"
        self.device_connection_status: str = "ONLINE"
        self.latest_device_job = {"JobType": "REBOOT", "Status": "COMPLETED"}
        self.latest_software = "6.2.1"
        self.lease_expiration_time = datetime.now(timezone.utc) + timedelta(days=5)
        self.serial_number = "GAD81E29013274749"
        self.type: str = "PANORAMA_APPLIANCE"

    @property
    def device_aggregated_status(self) -> str:
        self.__device_aggregated_status_manager.advance()
        return self.__device_aggregated_status_manager.status  # type: ignore[return-value]

    @property
    def provisioning_status(self) -> str:
        self.__device_provisioning_status_manager.advance()
        return self.__device_provisioning_status_manager.status  # type: ignore[return-value]

    def response_object(self) -> dict[str, Any]:
        response_object = super().gen_response_object()
        response_object = deep_convert_datetime_to_isoformat(response_object)
        static_response_fields = [
            "AlternateSoftwares", "Arn", "Brand", "CreatedTime",
            "CurrentNetworkingStatus", "CurrentSoftware", "Description",
            "DeviceConnectionStatus", "DeviceId", "LatestAlternateSoftware",
            "LatestDeviceJob", "LatestSoftware", "LeaseExpirationTime",
            "Name", "NetworkConfiguration", "SerialNumber", "Tags", "Type",
        ]
        return {
            **{k: v for k, v in response_object.items() if v is not None and k in static_response_fields},
            **{"DeviceAggregatedStatus": self.device_aggregated_status, "ProvisioningStatus": self.provisioning_status},
        }

    def response_listed(self) -> dict[str, Any]:
        response_object = super().gen_response_object()
        response_object = deep_convert_datetime_to_isoformat(response_object)
        static_response_fields = [
            "Brand", "CreatedTime", "CurrentSoftware", "Description",
            "DeviceId", "LastUpdatedTime", "LatestDeviceJob",
            "LeaseExpirationTime", "Name", "Tags", "Type",
        ]
        return {
            **{k: v for k, v in response_object.items() if v is not None and k in static_response_fields},
            **{"DeviceAggregatedStatus": self.device_aggregated_status, "ProvisioningStatus": self.provisioning_status},
        }

    @property
    def response_provision(self) -> dict[str, Union[str, bytes]]:
        return {
            "Arn": self.arn, "Certificates": self.certificates,
            "DeviceId": self.device_id, "IotThingName": self.iot_thing_name,
            "Status": self.provisioning_status,
        }

    @property
    def response_updated(self) -> dict[str, str]:
        return {"DeviceId": self.device_id}

    @property
    def response_deleted(self) -> dict[str, str]:
        return {"DeviceId": self.device_id}


class Package(BaseObject):
    def __init__(
        self, category: str, description: str, name: str,
        account_id: str, region_name: str, package_name: str, package_version: str,
    ):
        self.category = category
        self.description = description
        self.name = name
        now = datetime.now(timezone.utc)
        self.created_time = now
        self.last_updated_time = now
        self.package_name = package_name
        self.patch_version = generate_package_id(self.package_name)
        self.package_version = package_version
        self.output_package_name = f"{self.package_name}-{self.package_version}-{self.patch_version[:8]}-{self.name}"
        self.owner_account = account_id
        self.package_id = f"package-{hash_name(package_name)}"
        self.package_arn = arn_formatter("package", self.package_id, account_id, region_name)
        self.tags: Optional[dict[str, str]] = None
        self.storage_location: dict[str, str] = {
            "BinaryPrefixLocation": f"s3://panorama-{region_name}/{account_id}/binaries/",
            "Bucket": f"panorama-{region_name}",
            "GeneratedPrefixLocation": f"s3://panorama-{region_name}/{account_id}/generated/",
            "ManifestPrefixLocation": f"s3://panorama-{region_name}/{account_id}/manifests/",
            "RepoPrefixLocation": f"s3://panorama-{region_name}/{account_id}/repo/",
        }

    def response_object(self) -> dict[str, Any]:
        response_object = super().gen_response_object()
        response_object = deep_convert_datetime_to_isoformat(response_object)
        return response_object

    def response_listed(self) -> dict[str, Any]:
        return self.response_object()

    def response_created(self) -> dict[str, Any]:
        return {"Arn": self.package_arn, "PackageId": self.package_id, "StorageLocation": self.storage_location}

    def response_describe(self) -> dict[str, Any]:
        result = {
            "Arn": self.package_arn,
            "CreatedTime": deep_convert_datetime_to_isoformat(self.created_time),
            "PackageId": self.package_id,
            "PackageName": self.package_name,
            "StorageLocation": self.storage_location,
        }
        if self.tags:
            result["Tags"] = self.tags
        return result


class PackageImportJob(BaseObject):
    def __init__(
        self, account_id: str, region_name: str, client_token: str,
        input_config: dict[str, Any], job_type: str, output_config: dict[str, Any],
        job_tags: Optional[list[dict[str, Any]]],
    ):
        self.job_id = str(uuid.uuid4()).lower()
        self.client_token = client_token
        self.input_config = input_config
        self.job_type = job_type
        self.output_config = output_config
        self.job_tags = job_tags or []
        now = datetime.now(timezone.utc)
        self.created_time = now
        self.last_updated_time = now
        self.status = "SUCCEEDED"
        self.status_message = ""
        self.output = {
            "OutputS3Location": {
                "BucketName": f"panorama-{region_name}",
                "ObjectKey": f"{account_id}/packages/{self.job_id}",
            },
            "PackageId": f"package-{hash_name(self.job_id)}",
            "PackageVersion": "1.0",
            "PatchVersion": generate_package_id(self.job_id)[:16],
        }

    def response_created(self) -> dict[str, str]:
        return {"JobId": self.job_id}

    def response_describe(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ClientToken": self.client_token,
            "CreatedTime": deep_convert_datetime_to_isoformat(self.created_time),
            "InputConfig": self.input_config,
            "JobId": self.job_id,
            "JobType": self.job_type,
            "LastUpdatedTime": deep_convert_datetime_to_isoformat(self.last_updated_time),
            "Output": self.output,
            "OutputConfig": self.output_config,
            "Status": self.status,
            "StatusMessage": self.status_message,
        }
        if self.job_tags:
            result["JobTags"] = self.job_tags
        return result

    def response_listed(self) -> dict[str, Any]:
        return {
            "CreatedTime": deep_convert_datetime_to_isoformat(self.created_time),
            "JobId": self.job_id, "JobType": self.job_type,
            "LastUpdatedTime": deep_convert_datetime_to_isoformat(self.last_updated_time),
            "Status": self.status, "StatusMessage": self.status_message,
        }


class ApplicationInstance(BaseObject):
    def __init__(
        self, account_id: str, region_name: str,
        default_runtime_context_device: str, default_runtime_context_device_name: str,
        description: str, manifest_overrides_payload: dict[str, str],
        manifest_payload: dict[str, str], name: str,
        runtime_role_arn: str, tags: dict[str, str],
    ) -> None:
        self.default_runtime_context_device = default_runtime_context_device
        self.default_runtime_context_device_name = default_runtime_context_device_name
        self.description = description
        self.manifest_overrides_payload = manifest_overrides_payload
        self.manifest_payload = manifest_payload
        self.name = name
        self.runtime_role_arn = runtime_role_arn
        self.tags = tags
        now = datetime.now(timezone.utc)
        self.created_time = now
        self.last_updated_time = now
        name = f"{self.name}-{self.created_time}"
        self.application_instance_id = f"applicationInstance-{hash_name(name).lower()}"
        self.arn = arn_formatter(
            "application-instance", self.application_instance_id,
            account_id=account_id, region_name=region_name,
        )
        self.health_status = "RUNNING"
        self.status = "DEPLOYMENT_SUCCEEDED"
        self.status_description = "string"
        self.runtime_context_states = [{
            "DesiredState": "RUNNING", "DeviceReportedStatus": "RUNNING",
            "DeviceReportedTime": now, "RuntimeContextName": "string",
        }]

    def add_new_runtime_context_states(self, desired_state: str, device_reported_status: str) -> None:
        now = datetime.now(timezone.utc)
        self.runtime_context_states.append({
            "DesiredState": desired_state, "DeviceReportedStatus": device_reported_status,
            "DeviceReportedTime": now, "RuntimeContextName": "string",
        })

    def response_object(self) -> dict[str, Any]:
        response_object = super().gen_response_object()
        response_object = deep_convert_datetime_to_isoformat(response_object)
        return response_object

    def response_listed(self) -> dict[str, Any]:
        return self.response_object()

    def response_created(self) -> dict[str, str]:
        return {"ApplicationInstanceId": self.application_instance_id}

    def response_describe(self) -> dict[str, str]:
        return self.response_object()


class Node(BaseObject):
    def __init__(
        self, job_id: str, job_tags: list[dict[str, Union[str, dict[str, str]]]],
        node_description: str, node_name: str, output_package_name: str,
        output_package_version: str, template_parameters: dict[str, str], template_type: str,
    ) -> None:
        self.job_id = job_id
        now = datetime.now(timezone.utc)
        self.created_time = now
        self.last_updated_time = now
        self.job_tags = job_tags
        self.node_description = node_name
        self.status = "PENDING"
        self.node_name = node_name
        self.output_package_name = output_package_name
        self.output_package_version = output_package_version
        self.template_parameters = self.protect_secrets(template_parameters)
        self.template_type = template_type

    def response_object(self) -> dict[str, Any]:
        response_object = super().gen_response_object()
        response_object = deep_convert_datetime_to_isoformat(response_object)
        return response_object

    def response_created(self) -> dict[str, str]:
        return {"JobId": self.job_id}

    def response_described(self) -> dict[str, Any]:
        return self.response_object()

    def response_listed(self) -> dict[str, Any]:
        return {
            "CreatedTime": deep_convert_datetime_to_isoformat(self.created_time),
            "JobId": self.job_id, "NodeName": self.node_name,
            "Status": self.status, "TemplateType": self.template_type,
        }

    @staticmethod
    def protect_secrets(template_parameters: dict[str, str]) -> dict[str, str]:
        for key in template_parameters.keys():
            if key.lower() == "password":
                template_parameters[key] = "SAVED_AS_SECRET"
            if key.lower() == "username":
                template_parameters[key] = "SAVED_AS_SECRET"
        return template_parameters


class PanoramaBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.devices_memory: dict[str, Device] = {}
        self.node_from_template_memory: dict[str, Node] = {}
        self.nodes_memory: dict[str, Package] = {}
        self.packages_memory: dict[str, Package] = {}
        self.package_import_jobs_memory: dict[str, PackageImportJob] = {}
        self.application_instances_memory: dict[str, ApplicationInstance] = {}

    def provision_device(
        self, description: Optional[str], name: str,
        networking_configuration: Optional[dict[str, Any]], tags: Optional[dict[str, str]],
    ) -> Device:
        device_obj = Device(
            account_id=self.account_id, region_name=self.region_name,
            description=description, name=name,
            network_configuration=networking_configuration, tags=tags,
        )
        self.devices_memory[device_obj.device_id] = device_obj
        return device_obj

    def describe_device(self, device_id: str) -> Device:
        device = self.devices_memory.get(device_id)
        if device is None:
            raise ValidationError(f"Device {device_id} not found")
        return device

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_devices(
        self, device_aggregated_status_filter: str, name_filter: str,
        sort_by: str, sort_order: str,
    ) -> list[Device]:
        devices_list = list(filter(
            lambda x: (name_filter is None or x.name.startswith(name_filter))
            and (device_aggregated_status_filter is None or x.device_aggregated_status == device_aggregated_status_filter),
            self.devices_memory.values(),
        ))
        devices_list = sorted(
            devices_list,
            key={
                "DEVICE_ID": lambda x: x.device_id,
                "CREATED_TIME": lambda x: x.created_time,
                "NAME": lambda x: x.name,
                "DEVICE_AGGREGATED_STATUS": lambda x: x.device_aggregated_status,
                None: lambda x: x.created_time,
            }[sort_by],
            reverse=sort_order == "DESCENDING",
        )
        return devices_list

    def update_device_metadata(self, device_id: str, description: str) -> Device:
        self.devices_memory[device_id].description = description
        return self.devices_memory[device_id]

    def delete_device(self, device_id: str) -> Device:
        return self.devices_memory.pop(device_id)

    def create_node_from_template_job(
        self, job_tags: list[dict[str, Union[str, dict[str, str]]]],
        node_description: str, node_name: str, output_package_name: str,
        output_package_version: str, template_parameters: dict[str, str], template_type: str,
    ) -> Node:
        job_id = str(uuid.uuid4()).lower()
        self.node_from_template_memory[job_id] = Node(
            job_id=job_id, job_tags=job_tags, node_description=node_description,
            node_name=node_name, output_package_name=output_package_name,
            output_package_version=output_package_version,
            template_parameters=template_parameters, template_type=template_type,
        )
        if template_type == "RTSP_CAMERA_STREAM":
            package = Package(
                category="MEDIA_SOURCE", description=node_description, name=node_name,
                account_id=self.account_id, region_name=self.region_name,
                package_name=output_package_name, package_version=output_package_version,
            )
            self.nodes_memory[package.package_id] = package
        return self.node_from_template_memory[job_id]

    def describe_node_from_template_job(self, job_id: str) -> Node:
        if job_id not in self.node_from_template_memory:
            raise ResourceNotFoundException(f"Job {job_id} not found")
        return self.node_from_template_memory[job_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_node_from_template_jobs(self) -> list[Node]:
        return list(self.node_from_template_memory.values())

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_nodes(self, category: str) -> list[Package]:
        return list(filter(lambda x: x.category == category, self.nodes_memory.values()))

    def describe_node(self, node_id: str) -> Package:
        node = self.nodes_memory.get(node_id)
        if node is None:
            raise ResourceNotFoundException(f"Node {node_id} not found")
        return node

    def create_package(self, package_name: str, tags: Optional[dict[str, str]]) -> Package:
        pkg = Package(
            category="BUSINESS_LOGIC", description="", name=package_name,
            account_id=self.account_id, region_name=self.region_name,
            package_name=package_name, package_version="1.0",
        )
        pkg.tags = tags
        self.packages_memory[pkg.package_id] = pkg
        return pkg

    def describe_package(self, package_id: str) -> Package:
        pkg = self.packages_memory.get(package_id)
        if pkg is None:
            raise ResourceNotFoundException(f"Package {package_id} not found")
        return pkg

    def delete_package(self, package_id: str) -> None:
        if package_id not in self.packages_memory:
            raise ResourceNotFoundException(f"Package {package_id} not found")
        del self.packages_memory[package_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_packages(self) -> list[Package]:
        return list(self.packages_memory.values())

    def create_package_import_job(
        self, client_token: str, input_config: dict[str, Any],
        job_type: str, output_config: dict[str, Any],
        job_tags: Optional[list[dict[str, Any]]],
    ) -> PackageImportJob:
        job = PackageImportJob(
            account_id=self.account_id, region_name=self.region_name,
            client_token=client_token, input_config=input_config,
            job_type=job_type, output_config=output_config, job_tags=job_tags,
        )
        self.package_import_jobs_memory[job.job_id] = job
        return job

    def describe_package_import_job(self, job_id: str) -> PackageImportJob:
        job = self.package_import_jobs_memory.get(job_id)
        if job is None:
            raise ResourceNotFoundException(f"PackageImportJob {job_id} not found")
        return job

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_package_import_jobs(self) -> list[PackageImportJob]:
        return list(self.package_import_jobs_memory.values())

    def create_application_instance(
        self, application_instance_id_to_replace: Optional[str],
        default_runtime_context_device: str, description: str,
        manifest_overrides_payload: dict[str, str], manifest_payload: dict[str, str],
        name: str, runtime_role_arn: str, tags: dict[str, str],
    ) -> ApplicationInstance:
        device = self.devices_memory.get(default_runtime_context_device)
        if device is None:
            raise ValidationError(f"Device {default_runtime_context_device} not found")
        if (
            application_instance_id_to_replace
            and application_instance_id_to_replace in self.application_instances_memory
        ):
            removed = self.application_instances_memory[application_instance_id_to_replace]
            removed.status = "REMOVAL_SUCCEEDED"
            removed.add_new_runtime_context_states(
                desired_state="REMOVED", device_reported_status="REMOVAL_IN_PROGRESS"
            )
        application_instance = ApplicationInstance(
            account_id=self.account_id, region_name=self.region_name,
            default_runtime_context_device=default_runtime_context_device,
            default_runtime_context_device_name=device.name,
            description=description, manifest_overrides_payload=manifest_overrides_payload,
            manifest_payload=manifest_payload, name=name,
            runtime_role_arn=runtime_role_arn, tags=tags,
        )
        self.application_instances_memory[application_instance.application_instance_id] = application_instance
        return application_instance

    def describe_application_instance(self, application_instance_id: str) -> ApplicationInstance:
        if application_instance_id not in self.application_instances_memory:
            raise ResourceNotFoundException(f"ApplicationInstance {application_instance_id} not found")
        return self.application_instances_memory[application_instance_id]

    def remove_application_instance(self, application_instance_id: str) -> None:
        if application_instance_id not in self.application_instances_memory:
            raise ResourceNotFoundException(f"ApplicationInstance {application_instance_id} not found")
        instance = self.application_instances_memory[application_instance_id]
        instance.status = "REMOVAL_SUCCEEDED"
        instance.add_new_runtime_context_states(
            desired_state="REMOVED", device_reported_status="REMOVAL_IN_PROGRESS"
        )
        del self.application_instances_memory[application_instance_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_application_instances(
        self, device_id: Optional[str], status_filter: Optional[str],
    ) -> list[ApplicationInstance]:
        filtered = filter(
            lambda x: x.status == status_filter if status_filter else True,
            filter(
                lambda x: x.default_runtime_context_device == device_id if device_id else True,
                self.application_instances_memory.values(),
            ),
        )
        return list(filtered)


panorama_backends = BackendDict(
    PanoramaBackend, "panorama", False,
    additional_regions=["us-east-1", "us-west-2", "ca-central-1", "eu-west-1", "ap-southeast-2", "ap-southeast-1"],
)
