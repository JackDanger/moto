"""Handles incoming kinesisanalyticsv2 requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import KinesisAnalyticsV2Backend, kinesisanalyticsv2_backends


class KinesisAnalyticsV2Response(BaseResponse):
    """Handler for KinesisAnalyticsV2 requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="kinesisanalyticsv2")

    @property
    def kinesisanalyticsv2_backend(self) -> KinesisAnalyticsV2Backend:
        """Return backend instance specific for this region."""
        return kinesisanalyticsv2_backends[self.current_account][self.region]

    def create_application(self) -> str:
        application_name = self._get_param("ApplicationName")
        application_description = self._get_param("ApplicationDescription")
        runtime_environment = self._get_param("RuntimeEnvironment")
        service_execution_role = self._get_param("ServiceExecutionRole")
        application_configuration = self._get_param("ApplicationConfiguration")
        cloud_watch_logging_options = self._get_param("CloudWatchLoggingOptions")
        tags = self._get_param("Tags")
        application_mode = self._get_param("ApplicationMode")
        application_detail = self.kinesisanalyticsv2_backend.create_application(
            application_name=application_name,
            application_description=application_description,
            runtime_environment=runtime_environment,
            service_execution_role=service_execution_role,
            application_configuration=application_configuration,
            cloud_watch_logging_options=cloud_watch_logging_options,
            tags=tags,
            application_mode=application_mode,
        )
        return json.dumps({"ApplicationDetail": application_detail})

    def delete_application(self) -> str:
        application_name = self._get_param("ApplicationName")
        create_timestamp = self._get_param("CreateTimestamp")
        self.kinesisanalyticsv2_backend.delete_application(
            application_name=application_name,
            create_timestamp=create_timestamp,
        )
        return json.dumps({})

    def describe_application(self) -> str:
        application_name = self._get_param("ApplicationName")
        application_detail = self.kinesisanalyticsv2_backend.describe_application(
            application_name=application_name,
        )
        return json.dumps({"ApplicationDetail": application_detail})

    def describe_application_version(self) -> str:
        application_name = self._get_param("ApplicationName")
        application_version_id = self._get_int_param("ApplicationVersionId")
        application_detail = (
            self.kinesisanalyticsv2_backend.describe_application_version(
                application_name=application_name,
                application_version_id=application_version_id,
            )
        )
        return json.dumps({"ApplicationVersionDetail": application_detail})

    def update_application(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        app_config_update = self._get_param("ApplicationConfigurationUpdate")
        service_role_update = self._get_param("ServiceExecutionRoleUpdate")
        run_config_update = self._get_param("RunConfigurationUpdate")
        cw_updates = self._get_param("CloudWatchLoggingOptionUpdates")
        conditional_token = self._get_param("ConditionalToken")
        runtime_update = self._get_param("RuntimeEnvironmentUpdate")
        result = self.kinesisanalyticsv2_backend.update_application(
            application_name=application_name,
            current_application_version_id=current_version_id,
            application_configuration_update=app_config_update,
            service_execution_role_update=service_role_update,
            run_configuration_update=run_config_update,
            cloud_watch_logging_option_updates=cw_updates,
            conditional_token=conditional_token,
            runtime_environment_update=runtime_update,
        )
        return json.dumps(result)

    def update_application_maintenance_configuration(self) -> str:
        application_name = self._get_param("ApplicationName")
        config_update = self._get_param(
            "ApplicationMaintenanceConfigurationUpdate"
        )
        result = (
            self.kinesisanalyticsv2_backend.update_application_maintenance_configuration(
                application_name=application_name,
                application_maintenance_configuration_update=config_update,
            )
        )
        return json.dumps(result)

    def list_applications(self) -> str:
        application_summaries = self.kinesisanalyticsv2_backend.list_applications()
        return json.dumps({"ApplicationSummaries": application_summaries})

    def list_application_versions(self) -> str:
        application_name = self._get_param("ApplicationName")
        limit = self._get_int_param("Limit")
        next_token = self._get_param("NextToken")
        result = self.kinesisanalyticsv2_backend.list_application_versions(
            application_name=application_name,
            limit=limit,
            next_token=next_token,
        )
        return json.dumps(result)

    def list_application_snapshots(self) -> str:
        application_name = self._get_param("ApplicationName")
        limit = self._get_int_param("Limit")
        next_token = self._get_param("NextToken")
        result = self.kinesisanalyticsv2_backend.list_application_snapshots(
            application_name=application_name,
            limit=limit,
            next_token=next_token,
        )
        return json.dumps(result)

    def list_application_operations(self) -> str:
        application_name = self._get_param("ApplicationName")
        limit = self._get_int_param("Limit")
        next_token = self._get_param("NextToken")
        operation = self._get_param("Operation")
        operation_status = self._get_param("OperationStatus")
        result = self.kinesisanalyticsv2_backend.list_application_operations(
            application_name=application_name,
            limit=limit,
            next_token=next_token,
            operation=operation,
            operation_status=operation_status,
        )
        return json.dumps(result)

    def describe_application_operation(self) -> str:
        application_name = self._get_param("ApplicationName")
        operation_id = self._get_param("OperationId")
        result = self.kinesisanalyticsv2_backend.describe_application_operation(
            application_name=application_name,
            operation_id=operation_id,
        )
        return json.dumps(result)

    def start_application(self) -> str:
        application_name = self._get_param("ApplicationName")
        run_configuration = self._get_param("RunConfiguration")
        result = self.kinesisanalyticsv2_backend.start_application(
            application_name=application_name,
            run_configuration=run_configuration,
        )
        return json.dumps(result)

    def stop_application(self) -> str:
        application_name = self._get_param("ApplicationName")
        force = self._get_param("Force", False)
        result = self.kinesisanalyticsv2_backend.stop_application(
            application_name=application_name,
            force=force,
        )
        return json.dumps(result)

    def rollback_application(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        result = self.kinesisanalyticsv2_backend.rollback_application(
            application_name=application_name,
            current_application_version_id=current_version_id,
        )
        return json.dumps(result)

    def create_application_snapshot(self) -> str:
        application_name = self._get_param("ApplicationName")
        snapshot_name = self._get_param("SnapshotName")
        self.kinesisanalyticsv2_backend.create_application_snapshot(
            application_name=application_name,
            snapshot_name=snapshot_name,
        )
        return json.dumps({})

    def describe_application_snapshot(self) -> str:
        application_name = self._get_param("ApplicationName")
        snapshot_name = self._get_param("SnapshotName")
        result = self.kinesisanalyticsv2_backend.describe_application_snapshot(
            application_name=application_name,
            snapshot_name=snapshot_name,
        )
        return json.dumps(result)

    def delete_application_snapshot(self) -> str:
        application_name = self._get_param("ApplicationName")
        snapshot_name = self._get_param("SnapshotName")
        snapshot_creation_timestamp = self._get_param("SnapshotCreationTimestamp")
        self.kinesisanalyticsv2_backend.delete_application_snapshot(
            application_name=application_name,
            snapshot_name=snapshot_name,
            snapshot_creation_timestamp=snapshot_creation_timestamp,
        )
        return json.dumps({})

    def create_application_presigned_url(self) -> str:
        application_name = self._get_param("ApplicationName")
        url_type = self._get_param("UrlType")
        session_duration = self._get_int_param(
            "SessionExpirationDurationInSeconds"
        )
        result = self.kinesisanalyticsv2_backend.create_application_presigned_url(
            application_name=application_name,
            url_type=url_type,
            session_expiration_duration_in_seconds=session_duration,
        )
        return json.dumps(result)

    def add_application_cloud_watch_logging_option(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        cloud_watch_logging_option = self._get_param("CloudWatchLoggingOption")
        conditional_token = self._get_param("ConditionalToken")
        result = (
            self.kinesisanalyticsv2_backend.add_application_cloud_watch_logging_option(
                application_name=application_name,
                current_application_version_id=current_version_id,
                cloud_watch_logging_option=cloud_watch_logging_option,
                conditional_token=conditional_token,
            )
        )
        return json.dumps(result)

    def delete_application_cloud_watch_logging_option(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        cloud_watch_logging_option_id = self._get_param("CloudWatchLoggingOptionId")
        conditional_token = self._get_param("ConditionalToken")
        result = self.kinesisanalyticsv2_backend.delete_application_cloud_watch_logging_option(
            application_name=application_name,
            current_application_version_id=current_version_id,
            cloud_watch_logging_option_id=cloud_watch_logging_option_id,
            conditional_token=conditional_token,
        )
        return json.dumps(result)

    def add_application_input(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        app_input = self._get_param("Input")
        result = self.kinesisanalyticsv2_backend.add_application_input(
            application_name=application_name,
            current_application_version_id=current_version_id,
            app_input=app_input,
        )
        return json.dumps(result)

    def add_application_input_processing_configuration(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        input_id = self._get_param("InputId")
        input_processing_configuration = self._get_param(
            "InputProcessingConfiguration"
        )
        result = self.kinesisanalyticsv2_backend.add_application_input_processing_configuration(
            application_name=application_name,
            current_application_version_id=current_version_id,
            input_id=input_id,
            input_processing_configuration=input_processing_configuration,
        )
        return json.dumps(result)

    def delete_application_input_processing_configuration(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        input_id = self._get_param("InputId")
        result = self.kinesisanalyticsv2_backend.delete_application_input_processing_configuration(
            application_name=application_name,
            current_application_version_id=current_version_id,
            input_id=input_id,
        )
        return json.dumps(result)

    def add_application_output(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        output = self._get_param("Output")
        result = self.kinesisanalyticsv2_backend.add_application_output(
            application_name=application_name,
            current_application_version_id=current_version_id,
            output=output,
        )
        return json.dumps(result)

    def delete_application_output(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        output_id = self._get_param("OutputId")
        result = self.kinesisanalyticsv2_backend.delete_application_output(
            application_name=application_name,
            current_application_version_id=current_version_id,
            output_id=output_id,
        )
        return json.dumps(result)

    def add_application_reference_data_source(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        reference_data_source = self._get_param("ReferenceDataSource")
        result = self.kinesisanalyticsv2_backend.add_application_reference_data_source(
            application_name=application_name,
            current_application_version_id=current_version_id,
            reference_data_source=reference_data_source,
        )
        return json.dumps(result)

    def delete_application_reference_data_source(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        reference_id = self._get_param("ReferenceId")
        result = (
            self.kinesisanalyticsv2_backend.delete_application_reference_data_source(
                application_name=application_name,
                current_application_version_id=current_version_id,
                reference_id=reference_id,
            )
        )
        return json.dumps(result)

    def add_application_vpc_configuration(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        vpc_configuration = self._get_param("VpcConfiguration")
        conditional_token = self._get_param("ConditionalToken")
        result = self.kinesisanalyticsv2_backend.add_application_vpc_configuration(
            application_name=application_name,
            current_application_version_id=current_version_id,
            vpc_configuration=vpc_configuration,
            conditional_token=conditional_token,
        )
        return json.dumps(result)

    def delete_application_vpc_configuration(self) -> str:
        application_name = self._get_param("ApplicationName")
        current_version_id = self._get_int_param("CurrentApplicationVersionId")
        vpc_configuration_id = self._get_param("VpcConfigurationId")
        conditional_token = self._get_param("ConditionalToken")
        result = self.kinesisanalyticsv2_backend.delete_application_vpc_configuration(
            application_name=application_name,
            current_application_version_id=current_version_id,
            vpc_configuration_id=vpc_configuration_id,
            conditional_token=conditional_token,
        )
        return json.dumps(result)

    def discover_input_schema(self) -> str:
        resource_arn = self._get_param("ResourceARN")
        service_execution_role = self._get_param("ServiceExecutionRole")
        input_starting_position = self._get_param(
            "InputStartingPositionConfiguration"
        )
        s3_configuration = self._get_param("S3Configuration")
        input_processing_configuration = self._get_param(
            "InputProcessingConfiguration"
        )
        result = self.kinesisanalyticsv2_backend.discover_input_schema(
            resource_arn=resource_arn,
            service_execution_role=service_execution_role,
            input_starting_position_configuration=input_starting_position,
            s3_configuration=s3_configuration,
            input_processing_configuration=input_processing_configuration,
        )
        return json.dumps(result)

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tags = self.kinesisanalyticsv2_backend.list_tags_for_resource(
            resource_arn=resource_arn,
        )
        return json.dumps({"Tags": tags})

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tags = params.get("Tags")
        self.kinesisanalyticsv2_backend.tag_resource(
            resource_arn=resource_arn, tags=tags
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tag_keys = params.get("TagKeys", [])
        self.kinesisanalyticsv2_backend.untag_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )
        return json.dumps({})
