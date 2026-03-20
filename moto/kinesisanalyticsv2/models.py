from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService

from .exceptions import (
    ConcurrentModificationException,
    InvalidArgumentException,
    ResourceInUseException,
    ResourceNotFoundException,
)

FAKE_VPC_ID = "vpc-0123456789abcdef0"


class ApplicationSnapshot(BaseModel):
    def __init__(self, application_name: str, snapshot_name: str, version_id: int):
        self.application_name = application_name
        self.snapshot_name = snapshot_name
        self.application_version_id = version_id
        self.snapshot_status = "READY"
        self.snapshot_creation_timestamp = datetime.now().isoformat()


class ApplicationOperation(BaseModel):
    def __init__(self, operation_type: str, operation_id: str):
        self.operation_type = operation_type
        self.operation_id = operation_id
        self.start_time = datetime.now().isoformat()
        self.end_time = datetime.now().isoformat()
        self.operation_status = "SUCCESSFUL"


class Application(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        application_name: str,
        application_description: Optional[str],
        runtime_environment: str,
        service_execution_role: str,
        application_configuration: Optional[dict[str, Any]],
        cloud_watch_logging_options: Optional[list[dict[str, str]]],
        application_mode: Optional[str],
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.application_name = application_name
        self.application_description = application_description
        self.runtime_environment = runtime_environment
        self.service_execution_role = service_execution_role
        self.application_mode = application_mode

        self.app_config_description = (
            self._generate_app_config_description(application_configuration)
            if application_configuration
            else None
        )
        self.cloud_watch_logging_description = self._generate_logging_options(
            cloud_watch_logging_options
        )

        self.application_arn = self._generate_arn()
        self.application_status = "READY"
        self.application_version_id = 1
        self.creation_date_time = datetime.now().isoformat()
        self.last_updated_date_time = datetime.now().isoformat()
        self.conditional_token = str(mock_random.uuid4()).replace("-", "")

        self.maintenance_window_start = "06:00"
        self.maintenance_window_end = "14:00"

        # Storage for inputs, outputs, reference data sources
        self.input_descriptions: list[dict[str, Any]] = []
        self.output_descriptions: list[dict[str, Any]] = []
        self.reference_data_source_descriptions: list[dict[str, Any]] = []

        # Snapshots and operations
        self.snapshots: dict[str, ApplicationSnapshot] = {}
        self.operations: list[ApplicationOperation] = []

        # Version history
        self.version_summaries: list[dict[str, Any]] = [
            {
                "ApplicationVersionId": 1,
                "ApplicationStatus": self.application_status,
            }
        ]

    def _generate_arn(self) -> str:
        return f"arn:aws:kinesisanalytics:{self.region_name}:{self.account_id}:application/{self.application_name}"

    def _generate_logging_options(
        self, cloud_watch_logging_options: Optional[list[dict[str, str]]]
    ) -> list[dict[str, str]] | None:
        cloud_watch_logging_option_descriptions = []
        option_id = f"{str(random.randint(1, 100))}.1"

        if cloud_watch_logging_options:
            for i in cloud_watch_logging_options:
                cloud_watch_logging_option_descriptions.append(
                    {
                        "CloudWatchLoggingOptionId": option_id,
                        "LogStreamARN": i["LogStreamARN"],
                    }
                )
            return cloud_watch_logging_option_descriptions
        else:
            return None

    def _generate_app_config_description(
        self, app_config: dict[str, Any]
    ) -> dict[str, Any]:
        UPDATABLE_APP_CONFIG_TOP_LEVEL_KEYS = {
            "EnvironmentProperties": "EnvironmentPropertyDescriptions",
            "ApplicationSnapshotConfiguration": "ApplicationSnapshotConfigurationDescription",
            "ApplicationSystemRollbackConfiguration": "ApplicationSystemRollbackConfigurationDescription",
            "ZeppelinApplicationConfiguration": "ZeppelinApplicationConfigurationDescription",
        }

        APP_CONFIG_SUBFIELD_KEYS = {
            "PropertyGroups": "PropertyGroupDescriptions",
            "MonitoringConfiguration": "MonitoringConfigurationDescription",
            "CatalogConfiguration": "CatalogConfigurationDescription",
            "DeployAsApplicationConfiguration": "DeployAsApplicationConfigurationDescription",
            "S3ContentLocation": "S3ContentLocationDescription",
            "CustomArtifactsConfiguration": "CustomArtifactsConfigurationDescription",
            "GlueDataCatalogConfiguration": "GlueDataCatalogConfigurationDescription",
            "MavenReference": "MavenReferenceDescription",
        }

        app_config_description = {}
        if app_config:
            if "FlinkApplicationConfiguration" in app_config:
                app_config_description["FlinkApplicationConfigurationDescription"] = (
                    self.__generate_flink_app_description(app_config)
                )

            for old_key, new_key in UPDATABLE_APP_CONFIG_TOP_LEVEL_KEYS.items():
                if old_key in app_config:
                    app_config_description[new_key] = self.__update_keys(
                        app_config[old_key], APP_CONFIG_SUBFIELD_KEYS
                    )

            app_code_config = app_config.get("ApplicationCodeConfiguration")
            if app_code_config:
                new_key = "ApplicationCodeConfigurationDescription"

                app_code_config_keys = {
                    "S3ContentLocation": "S3ApplicationCodeLocationDescription",
                    "CodeContent": "CodeContentDescription",
                }

                app_config_description[new_key] = self.__update_keys(
                    app_code_config, app_code_config_keys
                )

                if app_code_config["CodeContentType"] == "ZIPFILE":
                    app_config_description[new_key]["CodeContentDescription"][
                        "CodeMD5"
                    ] = "fakechecksum"
                    app_config_description[new_key]["CodeContentDescription"][
                        "CodeSize"
                    ] = 123

            if "VpcConfigurations" in app_config:
                app_config_description["VpcConfigurationDescriptions"] = app_config[
                    "VpcConfigurations"
                ]
                for index, vpc_config in enumerate(
                    app_config_description["VpcConfigurationDescriptions"]
                ):
                    vpc_config["VpcConfigurationId"] = str(index + 1.1)
                    vpc_config["VpcId"] = FAKE_VPC_ID

        return app_config_description

    def __generate_flink_app_description(
        self, app_config: dict[str, Any]
    ) -> dict[str, Any]:
        flink_config_description = {}
        flink_config = app_config.get("FlinkApplicationConfiguration")
        if flink_config and isinstance(flink_config, dict):
            checkpoint_config = flink_config.get("CheckpointConfiguration")
            if checkpoint_config and isinstance(checkpoint_config, dict):
                if checkpoint_config.get("ConfigurationType") == "DEFAULT":
                    flink_config_description["CheckpointConfigurationDescription"] = {
                        "ConfigurationType": "DEFAULT",
                        "CheckpointingEnabled": True,
                        "CheckpointInterval": 60000,
                        "MinPauseBetweenCheckpoints": 5000,
                    }
                elif checkpoint_config.get("ConfigurationType") == "CUSTOM":
                    flink_config_description["CheckpointConfigurationDescription"] = {
                        "ConfigurationType": "CUSTOM",
                        "CheckpointingEnabled": checkpoint_config.get(
                            "CheckpointingEnabled", True
                        ),
                        "CheckpointInterval": checkpoint_config.get(
                            "CheckpointInterval", 60000
                        ),
                        "MinPauseBetweenCheckpoints": checkpoint_config.get(
                            "MinPauseBetweenCheckpoints", 5000
                        ),
                    }

            monitoring_config = flink_config.get("MonitoringConfiguration")
            if monitoring_config and isinstance(monitoring_config, dict):
                if monitoring_config.get("ConfigurationType") == "DEFAULT":
                    flink_config_description["MonitoringConfigurationDescription"] = {
                        "ConfigurationType": "DEFAULT",
                        "MetricsLevel": "APPLICATION",
                        "LogLevel": "INFO",
                    }
                elif monitoring_config.get("ConfigurationType") == "CUSTOM":
                    flink_config_description["MonitoringConfigurationDescription"] = {
                        "ConfigurationType": "CUSTOM",
                        "MetricsLevel": monitoring_config.get(
                            "MetricsLevel", "APPLICATION"
                        ),
                        "LogLevel": monitoring_config.get("LogLevel", "INFO"),
                    }
            parallel_config = flink_config.get("ParallelismConfiguration")
            if monitoring_config and isinstance(parallel_config, dict):
                if parallel_config.get("ConfigurationType") == "DEFAULT":
                    flink_config_description["ParallelismConfigurationDescription"] = {
                        "ConfigurationType": "DEFAULT",
                        "Parallelism": 1,
                        "ParallelismPerKPU": 1,
                        "AutoScalingEnabled": False,
                        "CurrentParallelism": 1,
                    }
                elif parallel_config.get("ConfigurationType") == "CUSTOM":
                    flink_config_description["ParallelismConfigurationDescription"] = {
                        "ConfigurationType": "CUSTOM",
                        "Parallelism": parallel_config.get("Parallelism", 1),
                        "ParallelismPerKPU": parallel_config.get(
                            "ParallelismPerKPU", 1
                        ),
                        "AutoScalingEnabled": parallel_config.get(
                            "AutoScalingEnabled", False
                        ),
                        "CurrentParallelism": parallel_config.get("Parallelism", 1),
                    }
        return flink_config_description

    def __update_keys(self, old_dict: Any, key_map: dict[str, str]) -> Any:
        if not isinstance(old_dict, dict):
            return old_dict

        updated_dict = {}
        for old_key, value in old_dict.items():
            new_key = key_map.get(old_key, old_key)

            if isinstance(value, dict):
                updated_dict[new_key] = self.__update_keys(value, key_map)
            elif isinstance(value, list):
                updated_dict[new_key] = [
                    self.__update_keys(list_item, key_map) for list_item in value
                ]
            else:
                updated_dict[new_key] = value
        return updated_dict

    def to_detail_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ApplicationARN": self.application_arn,
            "ApplicationDescription": self.application_description,
            "ApplicationName": self.application_name,
            "RuntimeEnvironment": self.runtime_environment,
            "ServiceExecutionRole": self.service_execution_role,
            "ApplicationStatus": self.application_status,
            "ApplicationVersionId": self.application_version_id,
            "CreateTimestamp": self.creation_date_time,
            "LastUpdateTimestamp": self.last_updated_date_time,
            "ApplicationConfigurationDescription": self.app_config_description,
            "CloudWatchLoggingOptionDescriptions": self.cloud_watch_logging_description,
            "ApplicationMaintenanceConfigurationDescription": {
                "ApplicationMaintenanceWindowStartTime": self.maintenance_window_start,
                "ApplicationMaintenanceWindowEndTime": self.maintenance_window_end,
            },
            "ApplicationVersionCreateTimestamp": str(self.creation_date_time),
            "ConditionalToken": self.conditional_token,
            "ApplicationMode": self.application_mode,
        }
        if self.input_descriptions:
            if result.get("ApplicationConfigurationDescription") is None:
                result["ApplicationConfigurationDescription"] = {}
            result["ApplicationConfigurationDescription"][
                "SqlApplicationConfigurationDescription"
            ] = result["ApplicationConfigurationDescription"].get(
                "SqlApplicationConfigurationDescription", {}
            )
            result["ApplicationConfigurationDescription"][
                "SqlApplicationConfigurationDescription"
            ]["InputDescriptions"] = self.input_descriptions
        if self.output_descriptions:
            if result.get("ApplicationConfigurationDescription") is None:
                result["ApplicationConfigurationDescription"] = {}
            sql = result["ApplicationConfigurationDescription"].get(
                "SqlApplicationConfigurationDescription", {}
            )
            sql["OutputDescriptions"] = self.output_descriptions
            result["ApplicationConfigurationDescription"][
                "SqlApplicationConfigurationDescription"
            ] = sql
        if self.reference_data_source_descriptions:
            if result.get("ApplicationConfigurationDescription") is None:
                result["ApplicationConfigurationDescription"] = {}
            sql = result["ApplicationConfigurationDescription"].get(
                "SqlApplicationConfigurationDescription", {}
            )
            sql["ReferenceDataSourceDescriptions"] = (
                self.reference_data_source_descriptions
            )
            result["ApplicationConfigurationDescription"][
                "SqlApplicationConfigurationDescription"
            ] = sql
        return result

    def _bump_version(self) -> None:
        self.application_version_id += 1
        self.last_updated_date_time = datetime.now().isoformat()
        self.conditional_token = str(mock_random.uuid4()).replace("-", "")
        self.version_summaries.append(
            {
                "ApplicationVersionId": self.application_version_id,
                "ApplicationStatus": self.application_status,
            }
        )

    def _record_operation(self, op_type: str) -> str:
        op_id = str(mock_random.uuid4())
        self.operations.append(ApplicationOperation(op_type, op_id))
        return op_id


class KinesisAnalyticsV2Backend(BaseBackend):
    """Implementation of KinesisAnalyticsV2 APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.applications: dict[str, Application] = {}
        self.tagger = TaggingService(
            tag_name="Tags", key_name="Key", value_name="Value"
        )

    def _get_app(self, application_name: str) -> Application:
        if application_name not in self.applications:
            raise ResourceNotFoundException(
                f"Application {application_name} is not found"
            )
        return self.applications[application_name]

    def create_application(
        self,
        application_name: str,
        application_description: Optional[str],
        runtime_environment: str,
        service_execution_role: str,
        application_configuration: Optional[dict[str, Any]],
        cloud_watch_logging_options: Optional[list[dict[str, str]]],
        tags: Optional[list[dict[str, str]]],
        application_mode: Optional[str],
    ) -> dict[str, Any]:
        if application_name in self.applications:
            raise ResourceInUseException(
                f"Application {application_name} already exists"
            )
        app = Application(
            account_id=self.account_id,
            region_name=self.region_name,
            application_name=application_name,
            application_description=application_description,
            runtime_environment=runtime_environment,
            service_execution_role=service_execution_role,
            application_configuration=application_configuration,
            cloud_watch_logging_options=cloud_watch_logging_options,
            application_mode=application_mode,
        )

        self.applications[application_name] = app

        if tags:
            self.tag_resource(resource_arn=app.application_arn, tags=tags)
        return app.to_detail_dict()

    def delete_application(
        self, application_name: str, create_timestamp: str
    ) -> None:
        self._get_app(application_name)
        del self.applications[application_name]

    def describe_application(
        self,
        application_name: str,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        return app.to_detail_dict()

    def describe_application_version(
        self, application_name: str, application_version_id: int
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        # Return current app detail (simplified — real AWS stores per-version snapshots)
        detail = app.to_detail_dict()
        detail["ApplicationVersionId"] = application_version_id
        return detail

    def update_application(
        self,
        application_name: str,
        current_application_version_id: Optional[int],
        application_configuration_update: Optional[dict[str, Any]],
        service_execution_role_update: Optional[str],
        run_configuration_update: Optional[dict[str, Any]],
        cloud_watch_logging_option_updates: Optional[list[dict[str, Any]]],
        conditional_token: Optional[str],
        runtime_environment_update: Optional[str],
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        if service_execution_role_update:
            app.service_execution_role = service_execution_role_update
        if runtime_environment_update:
            app.runtime_environment = runtime_environment_update
        if application_configuration_update:
            # Merge updates into existing config description
            if app.app_config_description is None:
                app.app_config_description = {}
            # Store raw update for simplicity
            for key, value in application_configuration_update.items():
                app.app_config_description[key] = value
        if cloud_watch_logging_option_updates:
            app.cloud_watch_logging_description = []
            for opt in cloud_watch_logging_option_updates:
                app.cloud_watch_logging_description.append(
                    {
                        "CloudWatchLoggingOptionId": opt.get(
                            "CloudWatchLoggingOptionId", "1.1"
                        ),
                        "LogStreamARN": opt.get("LogStreamARN", ""),
                    }
                )
        app._bump_version()
        op_id = app._record_operation("UpdateApplication")
        detail = app.to_detail_dict()
        return {"ApplicationDetail": detail, "OperationId": op_id}

    def update_application_maintenance_configuration(
        self,
        application_name: str,
        application_maintenance_configuration_update: dict[str, Any],
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        start_time = application_maintenance_configuration_update.get(
            "ApplicationMaintenanceWindowStartTimeUpdate"
        )
        if start_time:
            app.maintenance_window_start = start_time
            # End time is start + 8 hours (simplified)
            h, m = start_time.split(":")
            end_h = (int(h) + 8) % 24
            app.maintenance_window_end = f"{end_h:02d}:{m}"
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationMaintenanceConfigurationDescription": {
                "ApplicationMaintenanceWindowStartTime": app.maintenance_window_start,
                "ApplicationMaintenanceWindowEndTime": app.maintenance_window_end,
            },
        }

    def list_applications(self) -> list[dict[str, Any]]:
        application_summaries = [
            {
                "ApplicationName": app.application_name,
                "ApplicationARN": app.application_arn,
                "ApplicationStatus": app.application_status,
                "ApplicationVersionId": app.application_version_id,
                "RuntimeEnvironment": app.runtime_environment,
                "ApplicationMode": app.application_mode,
            }
            for app in self.applications.values()
        ]
        return application_summaries

    def list_application_versions(
        self,
        application_name: str,
        limit: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        return {"ApplicationVersionSummaries": app.version_summaries}

    def list_application_snapshots(
        self,
        application_name: str,
        limit: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        summaries = [
            {
                "SnapshotName": s.snapshot_name,
                "SnapshotStatus": s.snapshot_status,
                "ApplicationVersionId": s.application_version_id,
                "SnapshotCreationTimestamp": s.snapshot_creation_timestamp,
            }
            for s in app.snapshots.values()
        ]
        return {"SnapshotSummaries": summaries}

    def list_application_operations(
        self,
        application_name: str,
        limit: Optional[int] = None,
        next_token: Optional[str] = None,
        operation: Optional[str] = None,
        operation_status: Optional[str] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        ops = app.operations
        if operation:
            ops = [o for o in ops if o.operation_type == operation]
        if operation_status:
            ops = [o for o in ops if o.operation_status == operation_status]
        info_list = [
            {
                "Operation": o.operation_type,
                "OperationId": o.operation_id,
                "StartTime": o.start_time,
                "EndTime": o.end_time,
                "OperationStatus": o.operation_status,
            }
            for o in ops
        ]
        return {"ApplicationOperationInfoList": info_list}

    def describe_application_operation(
        self, application_name: str, operation_id: str
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        for op in app.operations:
            if op.operation_id == operation_id:
                return {
                    "ApplicationOperationInfoDetails": {
                        "Operation": op.operation_type,
                        "OperationId": op.operation_id,
                        "StartTime": op.start_time,
                        "EndTime": op.end_time,
                        "OperationStatus": op.operation_status,
                    }
                }
        raise ResourceNotFoundException(f"Operation {operation_id} is not found")

    # Start / Stop
    def start_application(
        self,
        application_name: str,
        run_configuration: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        app.application_status = "RUNNING"
        app.last_updated_date_time = datetime.now().isoformat()
        op_id = app._record_operation("StartApplication")
        return {"OperationId": op_id}

    def stop_application(
        self, application_name: str, force: bool = False
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        app.application_status = "READY"
        app.last_updated_date_time = datetime.now().isoformat()
        op_id = app._record_operation("StopApplication")
        return {"OperationId": op_id}

    def rollback_application(
        self, application_name: str, current_application_version_id: int
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        app._bump_version()
        op_id = app._record_operation("RollbackApplication")
        return {"ApplicationDetail": app.to_detail_dict(), "OperationId": op_id}

    # Snapshots
    def create_application_snapshot(
        self, application_name: str, snapshot_name: str
    ) -> None:
        app = self._get_app(application_name)
        snapshot = ApplicationSnapshot(
            application_name, snapshot_name, app.application_version_id
        )
        app.snapshots[snapshot_name] = snapshot

    def describe_application_snapshot(
        self, application_name: str, snapshot_name: str
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        if snapshot_name not in app.snapshots:
            raise ResourceNotFoundException(
                f"Snapshot {snapshot_name} is not found for application {application_name}"
            )
        s = app.snapshots[snapshot_name]
        return {
            "SnapshotDetails": {
                "SnapshotName": s.snapshot_name,
                "SnapshotStatus": s.snapshot_status,
                "ApplicationVersionId": s.application_version_id,
                "SnapshotCreationTimestamp": s.snapshot_creation_timestamp,
            }
        }

    def delete_application_snapshot(
        self,
        application_name: str,
        snapshot_name: str,
        snapshot_creation_timestamp: str,
    ) -> None:
        app = self._get_app(application_name)
        if snapshot_name not in app.snapshots:
            raise ResourceNotFoundException(
                f"Snapshot {snapshot_name} is not found for application {application_name}"
            )
        del app.snapshots[snapshot_name]

    # Presigned URL
    def create_application_presigned_url(
        self,
        application_name: str,
        url_type: str,
        session_expiration_duration_in_seconds: Optional[int] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        url = f"https://flink-ui.kinesisanalytics.{app.region_name}.amazonaws.com/{application_name}?token={mock_random.get_random_hex(32)}"
        return {"AuthorizedUrl": url}

    # CloudWatch Logging
    def add_application_cloud_watch_logging_option(
        self,
        application_name: str,
        current_application_version_id: Optional[int],
        cloud_watch_logging_option: dict[str, str],
        conditional_token: Optional[str] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        option_id = f"{random.randint(1, 100)}.1"
        desc = {
            "CloudWatchLoggingOptionId": option_id,
            "LogStreamARN": cloud_watch_logging_option["LogStreamARN"],
        }
        if app.cloud_watch_logging_description is None:
            app.cloud_watch_logging_description = []
        app.cloud_watch_logging_description.append(desc)
        app._bump_version()
        op_id = app._record_operation("AddApplicationCloudWatchLoggingOption")
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
            "CloudWatchLoggingOptionDescriptions": app.cloud_watch_logging_description,
            "OperationId": op_id,
        }

    def delete_application_cloud_watch_logging_option(
        self,
        application_name: str,
        current_application_version_id: Optional[int],
        cloud_watch_logging_option_id: str,
        conditional_token: Optional[str] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        if app.cloud_watch_logging_description:
            app.cloud_watch_logging_description = [
                d
                for d in app.cloud_watch_logging_description
                if d.get("CloudWatchLoggingOptionId") != cloud_watch_logging_option_id
            ]
        app._bump_version()
        op_id = app._record_operation("DeleteApplicationCloudWatchLoggingOption")
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
            "CloudWatchLoggingOptionDescriptions": app.cloud_watch_logging_description
            or [],
            "OperationId": op_id,
        }

    # Input
    def add_application_input(
        self,
        application_name: str,
        current_application_version_id: int,
        app_input: dict[str, Any],
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        input_id = str(len(app.input_descriptions) + 1) + ".1"
        input_desc: dict[str, Any] = {
            "InputId": input_id,
            "NamePrefix": app_input.get("NamePrefix", ""),
        }
        if "InputSchema" in app_input:
            input_desc["InputSchema"] = app_input["InputSchema"]
        if "InputParallelism" in app_input:
            input_desc["InputParallelism"] = app_input["InputParallelism"]
        if "KinesisStreamsInput" in app_input:
            input_desc["KinesisStreamsInputDescription"] = app_input[
                "KinesisStreamsInput"
            ]
        if "KinesisFirehoseInput" in app_input:
            input_desc["KinesisFirehoseInputDescription"] = app_input[
                "KinesisFirehoseInput"
            ]
        if "InputProcessingConfiguration" in app_input:
            input_desc["InputProcessingConfigurationDescription"] = app_input[
                "InputProcessingConfiguration"
            ]
        app.input_descriptions.append(input_desc)
        app._bump_version()
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
            "InputDescriptions": app.input_descriptions,
        }

    def add_application_input_processing_configuration(
        self,
        application_name: str,
        current_application_version_id: int,
        input_id: str,
        input_processing_configuration: dict[str, Any],
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        for inp in app.input_descriptions:
            if inp.get("InputId") == input_id:
                inp["InputProcessingConfigurationDescription"] = (
                    input_processing_configuration
                )
                break
        app._bump_version()
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
            "InputId": input_id,
            "InputProcessingConfigurationDescription": input_processing_configuration,
        }

    def delete_application_input_processing_configuration(
        self,
        application_name: str,
        current_application_version_id: int,
        input_id: str,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        for inp in app.input_descriptions:
            if inp.get("InputId") == input_id:
                inp.pop("InputProcessingConfigurationDescription", None)
                break
        app._bump_version()
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
        }

    # Output
    def add_application_output(
        self,
        application_name: str,
        current_application_version_id: int,
        output: dict[str, Any],
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        output_id = str(len(app.output_descriptions) + 1) + ".1"
        output_desc: dict[str, Any] = {
            "OutputId": output_id,
            "Name": output.get("Name", ""),
        }
        if "DestinationSchema" in output:
            output_desc["DestinationSchema"] = output["DestinationSchema"]
        if "KinesisStreamsOutput" in output:
            output_desc["KinesisStreamsOutputDescription"] = output[
                "KinesisStreamsOutput"
            ]
        if "KinesisFirehoseOutput" in output:
            output_desc["KinesisFirehoseOutputDescription"] = output[
                "KinesisFirehoseOutput"
            ]
        if "LambdaOutput" in output:
            output_desc["LambdaOutputDescription"] = output["LambdaOutput"]
        app.output_descriptions.append(output_desc)
        app._bump_version()
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
            "OutputDescriptions": app.output_descriptions,
        }

    def delete_application_output(
        self,
        application_name: str,
        current_application_version_id: int,
        output_id: str,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        app.output_descriptions = [
            o for o in app.output_descriptions if o.get("OutputId") != output_id
        ]
        app._bump_version()
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
        }

    # Reference Data Source
    def add_application_reference_data_source(
        self,
        application_name: str,
        current_application_version_id: int,
        reference_data_source: dict[str, Any],
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        ref_id = str(len(app.reference_data_source_descriptions) + 1) + ".1"
        ref_desc: dict[str, Any] = {
            "ReferenceId": ref_id,
            "TableName": reference_data_source.get("TableName", ""),
        }
        if "ReferenceSchema" in reference_data_source:
            ref_desc["ReferenceSchema"] = reference_data_source["ReferenceSchema"]
        if "S3ReferenceDataSource" in reference_data_source:
            ref_desc["S3ReferenceDataSourceDescription"] = reference_data_source[
                "S3ReferenceDataSource"
            ]
        app.reference_data_source_descriptions.append(ref_desc)
        app._bump_version()
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
            "ReferenceDataSourceDescriptions": app.reference_data_source_descriptions,
        }

    def delete_application_reference_data_source(
        self,
        application_name: str,
        current_application_version_id: int,
        reference_id: str,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        app.reference_data_source_descriptions = [
            r
            for r in app.reference_data_source_descriptions
            if r.get("ReferenceId") != reference_id
        ]
        app._bump_version()
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
        }

    # VPC Configuration
    def add_application_vpc_configuration(
        self,
        application_name: str,
        current_application_version_id: Optional[int],
        vpc_configuration: dict[str, Any],
        conditional_token: Optional[str] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        if app.app_config_description is None:
            app.app_config_description = {}
        vpc_descs = app.app_config_description.get("VpcConfigurationDescriptions", [])
        vpc_id = str(len(vpc_descs) + 1) + ".1"
        vpc_desc = {
            "VpcConfigurationId": vpc_id,
            "VpcId": FAKE_VPC_ID,
            **vpc_configuration,
        }
        vpc_descs.append(vpc_desc)
        app.app_config_description["VpcConfigurationDescriptions"] = vpc_descs
        app._bump_version()
        op_id = app._record_operation("AddApplicationVpcConfiguration")
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
            "VpcConfigurationDescription": vpc_desc,
            "OperationId": op_id,
        }

    def delete_application_vpc_configuration(
        self,
        application_name: str,
        current_application_version_id: Optional[int],
        vpc_configuration_id: str,
        conditional_token: Optional[str] = None,
    ) -> dict[str, Any]:
        app = self._get_app(application_name)
        if app.app_config_description:
            vpc_descs = app.app_config_description.get(
                "VpcConfigurationDescriptions", []
            )
            app.app_config_description["VpcConfigurationDescriptions"] = [
                v
                for v in vpc_descs
                if v.get("VpcConfigurationId") != vpc_configuration_id
            ]
        app._bump_version()
        op_id = app._record_operation("DeleteApplicationVpcConfiguration")
        return {
            "ApplicationARN": app.application_arn,
            "ApplicationVersionId": app.application_version_id,
            "OperationId": op_id,
        }

    # Discover Input Schema
    def discover_input_schema(
        self,
        resource_arn: Optional[str],
        service_execution_role: str,
        input_starting_position_configuration: Optional[dict[str, Any]],
        s3_configuration: Optional[dict[str, Any]],
        input_processing_configuration: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        # Return a mock schema
        return {
            "InputSchema": {
                "RecordFormat": {
                    "RecordFormatType": "CSV",
                    "MappingParameters": {
                        "CSVMappingParameters": {
                            "RecordRowDelimiter": "\n",
                            "RecordColumnDelimiter": ",",
                        }
                    },
                },
                "RecordColumns": [
                    {
                        "Name": "Col_1",
                        "SqlType": "VARCHAR(4)",
                        "Mapping": "$.Col_1",
                    }
                ],
            },
            "ParsedInputRecords": [["record1"]],
            "ProcessedInputRecords": ["record1"],
            "RawInputRecords": ["raw_record1"],
        }

    # Tagging
    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        return self.tagger.list_tags_for_resource(resource_arn)["Tags"]


kinesisanalyticsv2_backends = BackendDict(
    KinesisAnalyticsV2Backend, "kinesisanalyticsv2"
)
