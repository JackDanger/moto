from typing import Any

from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .exceptions import ParameterNotFound, ValidationException
from .models import SimpleSystemManagerBackend, ssm_backends


class SimpleSystemManagerResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="ssm")

    @property
    def ssm_backend(self) -> SimpleSystemManagerBackend:
        return ssm_backends[self.current_account][self.region]

    def create_document(self) -> ActionResult:
        content = self._get_param("Content")
        requires = self._get_param("Requires")
        attachments = self._get_param("Attachments")
        name = self._get_param("Name")
        version_name = self._get_param("VersionName")
        document_type = self._get_param("DocumentType")
        document_format = self._get_param("DocumentFormat", "JSON")
        target_type = self._get_param("TargetType")
        tags = self._get_param("Tags")

        document = self.ssm_backend.create_document(
            content=content,
            requires=requires,
            attachments=attachments,
            name=name,
            version_name=version_name,
            document_type=document_type,
            document_format=document_format,
            target_type=target_type,
            tags=tags,
        )

        return ActionResult({"DocumentDescription": document.describe(tags=tags)})

    def delete_document(self) -> ActionResult:
        name = self._get_param("Name")
        document_version = self._get_param("DocumentVersion")
        version_name = self._get_param("VersionName")
        force = self._get_param("Force", False)
        self.ssm_backend.delete_document(
            name=name,
            document_version=document_version,
            version_name=version_name,
            force=force,
        )

        return EmptyResult()

    def get_document(self) -> ActionResult:
        name = self._get_param("Name")
        version_name = self._get_param("VersionName")
        document_version = self._get_param("DocumentVersion")
        document_format = self._get_param("DocumentFormat", "JSON")

        document = self.ssm_backend.get_document(
            name=name,
            document_version=document_version,
            document_format=document_format,
            version_name=version_name,
        )

        return ActionResult(document)

    def describe_document(self) -> ActionResult:
        name = self._get_param("Name")
        document_version = self._get_param("DocumentVersion")
        version_name = self._get_param("VersionName")

        result = self.ssm_backend.describe_document(
            name=name, document_version=document_version, version_name=version_name
        )

        return ActionResult({"Document": result})

    def update_document(self) -> ActionResult:
        content = self._get_param("Content")
        attachments = self._get_param("Attachments")
        name = self._get_param("Name")
        version_name = self._get_param("VersionName")
        document_version = self._get_param("DocumentVersion")
        document_format = self._get_param("DocumentFormat", "JSON")
        target_type = self._get_param("TargetType")

        result = self.ssm_backend.update_document(
            content=content,
            attachments=attachments,
            name=name,
            version_name=version_name,
            document_version=document_version,
            document_format=document_format,
            target_type=target_type,
        )

        return ActionResult({"DocumentDescription": result})

    def update_document_default_version(self) -> ActionResult:
        name = self._get_param("Name")
        document_version = self._get_param("DocumentVersion")

        result = self.ssm_backend.update_document_default_version(
            name=name, document_version=document_version
        )
        return ActionResult({"Description": result})

    def list_documents(self) -> ActionResult:
        document_filter_list = self._get_param("DocumentFilterList")
        filters = self._get_param("Filters")
        max_results = self._get_param("MaxResults", 10)
        next_token = self._get_param("NextToken", "0")

        documents, token = self.ssm_backend.list_documents(
            document_filter_list=document_filter_list,
            filters=filters,
            max_results=max_results,
            token=next_token,
        )

        return ActionResult({"DocumentIdentifiers": documents, "NextToken": token})

    def describe_document_permission(self) -> ActionResult:
        name = self._get_param("Name")

        result = self.ssm_backend.describe_document_permission(name=name)
        return ActionResult(result)

    def modify_document_permission(self) -> ActionResult:
        account_ids_to_add = self._get_param("AccountIdsToAdd")
        account_ids_to_remove = self._get_param("AccountIdsToRemove")
        name = self._get_param("Name")
        permission_type = self._get_param("PermissionType")
        shared_document_version = self._get_param("SharedDocumentVersion")

        self.ssm_backend.modify_document_permission(
            name=name,
            account_ids_to_add=account_ids_to_add,
            account_ids_to_remove=account_ids_to_remove,
            shared_document_version=shared_document_version,
            permission_type=permission_type,
        )
        return EmptyResult()

    def delete_parameter(self) -> ActionResult:
        name = self._get_param("Name")
        self.ssm_backend.delete_parameter(name)
        return EmptyResult()

    def delete_parameters(self) -> ActionResult:
        names = self._get_param("Names")
        result = self.ssm_backend.delete_parameters(names)

        response: dict[str, Any] = {"DeletedParameters": [], "InvalidParameters": []}

        for name in names:
            if name in result:
                response["DeletedParameters"].append(name)
            else:
                response["InvalidParameters"].append(name)
        return ActionResult(response)

    def get_parameter(self) -> ActionResult:
        name = self._get_param("Name")
        with_decryption = self._get_param("WithDecryption")

        if (
            name.startswith("/aws/reference/secretsmanager/")
            and with_decryption is not True
        ):
            raise ValidationException(
                "WithDecryption flag must be True for retrieving a Secret Manager secret."
            )

        result = self.ssm_backend.get_parameter(name)

        if result is None:
            raise ParameterNotFound(f"Parameter {name} not found.")

        response = {"Parameter": result.response_object(with_decryption, self.region)}
        return ActionResult(response)

    def get_parameters(self) -> ActionResult:
        names = self._get_param("Names")
        with_decryption = self._get_param("WithDecryption")

        result = self.ssm_backend.get_parameters(names)

        response: dict[str, Any] = {"Parameters": [], "InvalidParameters": []}

        for parameter in result.values():
            param_data = parameter.response_object(with_decryption, self.region)
            response["Parameters"].append(param_data)

        valid_param_names = [name for name, parameter in result.items()]
        for name in names:
            if name not in valid_param_names:
                response["InvalidParameters"].append(name)
        return ActionResult(response)

    def get_parameters_by_path(self) -> ActionResult:
        path = self._get_param("Path")
        with_decryption = self._get_param("WithDecryption")
        recursive = self._get_param("Recursive", False)
        filters = self._get_param("ParameterFilters")
        token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults", 10)

        result, next_token = self.ssm_backend.get_parameters_by_path(
            path,
            recursive,
            filters,
            next_token=token,
            max_results=max_results,
        )

        response: dict[str, Any] = {"Parameters": [], "NextToken": next_token}

        for parameter in result:
            param_data = parameter.response_object(with_decryption, self.region)
            response["Parameters"].append(param_data)

        return ActionResult(response)

    def describe_parameters(self) -> ActionResult:
        page_size = 10
        filters = self._get_param("Filters")
        parameter_filters = self._get_param("ParameterFilters")
        token = self._get_param("NextToken")
        if hasattr(token, "strip"):
            token = token.strip()
        if not token:
            token = "0"
        token = int(token)

        result = self.ssm_backend.describe_parameters(filters, parameter_filters)

        response: dict[str, Any] = {"Parameters": []}

        end = token + page_size
        for parameter in result[token:]:
            response["Parameters"].append(parameter.describe_response_object(False))

            token += 1
            if len(response["Parameters"]) == page_size:
                response["NextToken"] = str(end)
                break

        return ActionResult(response)

    def put_parameter(self) -> ActionResult:
        name = self._get_param("Name")
        description = self._get_param("Description")
        value = self._get_param("Value")
        type_ = self._get_param("Type")
        allowed_pattern = self._get_param("AllowedPattern")
        keyid = self._get_param("KeyId")
        overwrite = self._get_param("Overwrite", False)
        tags = self._get_param("Tags")
        data_type = self._get_param("DataType", "text")
        tier = self._get_param("Tier")
        policies = self._get_param("Policies")

        param = self.ssm_backend.put_parameter(
            name,
            description,
            value,
            type_,
            allowed_pattern,
            keyid,
            overwrite,
            tags,
            data_type,
            tier=tier,
            policies=policies,
        )

        response = {"Version": param.version, "Tier": param.tier}
        return ActionResult(response)

    def get_parameter_history(self) -> ActionResult:
        name = self._get_param("Name")
        with_decryption = self._get_param("WithDecryption")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults", 50)

        result, new_next_token = self.ssm_backend.get_parameter_history(
            name, next_token, max_results
        )

        if result is None:
            raise ParameterNotFound(f"Parameter {name} not found.")

        response = {
            "Parameters": [
                p_v.describe_response_object(
                    decrypt=with_decryption, include_labels=True
                )
                for p_v in result
            ],
            "NextToken": new_next_token,
        }

        return ActionResult(response)

    def label_parameter_version(self) -> ActionResult:
        name = self._get_param("Name")
        version = self._get_param("ParameterVersion")
        labels = self._get_param("Labels")

        invalid_labels, version = self.ssm_backend.label_parameter_version(
            name, version, labels
        )

        response = {"InvalidLabels": invalid_labels, "ParameterVersion": version}
        return ActionResult(response)

    def unlabel_parameter_version(self) -> ActionResult:
        name = self._get_param("Name")
        version = self._get_param("ParameterVersion")
        labels = self._get_param("Labels")

        removed_labels, invalid_labels = self.ssm_backend.unlabel_parameter_version(
            name, version, labels
        )

        response = {"RemovedLabels": removed_labels, "InvalidLabels": invalid_labels}
        return ActionResult(response)

    def add_tags_to_resource(self) -> ActionResult:
        resource_id = self._get_param("ResourceId")
        resource_type = self._get_param("ResourceType")
        tags = {t["Key"]: t["Value"] for t in self._get_param("Tags")}
        self.ssm_backend.add_tags_to_resource(
            resource_type=resource_type, resource_id=resource_id, tags=tags
        )
        return EmptyResult()

    def remove_tags_from_resource(self) -> ActionResult:
        resource_id = self._get_param("ResourceId")
        resource_type = self._get_param("ResourceType")
        keys = self._get_param("TagKeys")
        self.ssm_backend.remove_tags_from_resource(
            resource_type=resource_type, resource_id=resource_id, keys=keys
        )
        return EmptyResult()

    def list_tags_for_resource(self) -> ActionResult:
        resource_id = self._get_param("ResourceId")
        resource_type = self._get_param("ResourceType")
        tags = self.ssm_backend.list_tags_for_resource(
            resource_type=resource_type, resource_id=resource_id
        )
        tag_list = [{"Key": k, "Value": v} for (k, v) in tags.items()]
        response = {"TagList": tag_list}
        return ActionResult(response)

    def send_command(self) -> ActionResult:
        comment = self._get_param("Comment", "")
        document_name = self._get_param("DocumentName")
        timeout_seconds = self._get_int_param("TimeoutSeconds")
        instance_ids = self._get_param("InstanceIds", [])
        max_concurrency = self._get_param("MaxConcurrency", "50")
        max_errors = self._get_param("MaxErrors", "0")
        notification_config = self._get_param("NotificationConfig")
        output_s3_bucket_name = self._get_param("OutputS3BucketName", "")
        output_s3_key_prefix = self._get_param("OutputS3KeyPrefix", "")
        output_s3_region = self._get_param("OutputS3Region", "")
        parameters = self._get_param("Parameters", {})
        service_role_arn = self._get_param("ServiceRoleArn", "")
        targets = self._get_param("Targets", [])
        command = self.ssm_backend.send_command(
            comment=comment,
            document_name=document_name,
            timeout_seconds=timeout_seconds,
            instance_ids=instance_ids,
            max_concurrency=max_concurrency,
            max_errors=max_errors,
            notification_config=notification_config,
            output_s3_bucket_name=output_s3_bucket_name,
            output_s3_key_prefix=output_s3_key_prefix,
            output_s3_region=output_s3_region,
            parameters=parameters,
            service_role_arn=service_role_arn,
            targets=targets,
        )
        return ActionResult({"Command": command.response_object()})

    def list_commands(self) -> ActionResult:
        command_id = self._get_param("CommandId")
        instance_id = self._get_param("InstanceId")
        commands = self.ssm_backend.list_commands(command_id, instance_id)
        response = {"Commands": [command.response_object() for command in commands]}
        return ActionResult(response)

    def get_command_invocation(self) -> ActionResult:
        command_id = self._get_param("CommandId")
        instance_id = self._get_param("InstanceId")
        plugin_name = self._get_param("PluginName")
        response = self.ssm_backend.get_command_invocation(
            command_id, instance_id, plugin_name
        )
        return ActionResult(response)

    def create_maintenance_window(self) -> ActionResult:
        name = self._get_param("Name")
        desc = self._get_param("Description", None)
        duration = self._get_int_param("Duration")
        cutoff = self._get_int_param("Cutoff")
        schedule = self._get_param("Schedule")
        schedule_timezone = self._get_param("ScheduleTimezone")
        schedule_offset = self._get_int_param("ScheduleOffset")
        start_date = self._get_param("StartDate")
        end_date = self._get_param("EndDate")
        tags = self._get_param("Tags")
        window_id = self.ssm_backend.create_maintenance_window(
            name=name,
            description=desc,
            duration=duration,
            cutoff=cutoff,
            schedule=schedule,
            schedule_timezone=schedule_timezone,
            schedule_offset=schedule_offset,
            start_date=start_date,
            end_date=end_date,
            tags=tags,
        )
        return ActionResult({"WindowId": window_id})

    def get_maintenance_window(self) -> ActionResult:
        window_id = self._get_param("WindowId")
        window = self.ssm_backend.get_maintenance_window(window_id)
        return ActionResult(window.to_json())

    def register_target_with_maintenance_window(self) -> ActionResult:
        window_target_id = self.ssm_backend.register_target_with_maintenance_window(
            window_id=self._get_param("WindowId"),
            resource_type=self._get_param("ResourceType"),
            targets=self._get_param("Targets"),
            owner_information=self._get_param("OwnerInformation"),
            name=self._get_param("Name"),
            description=self._get_param("Description"),
        )
        return ActionResult({"WindowTargetId": window_target_id})

    def describe_maintenance_window_targets(self) -> ActionResult:
        window_id = self._get_param("WindowId")
        filters = self._get_param("Filters", [])
        targets = [
            target.to_json()
            for target in self.ssm_backend.describe_maintenance_window_targets(
                window_id, filters
            )
        ]
        return ActionResult({"Targets": targets})

    def deregister_target_from_maintenance_window(self) -> ActionResult:
        window_id = self._get_param("WindowId")
        window_target_id = self._get_param("WindowTargetId")
        self.ssm_backend.deregister_target_from_maintenance_window(
            window_id, window_target_id
        )
        return EmptyResult()

    def describe_maintenance_windows(self) -> ActionResult:
        filters = self._get_param("Filters", None)
        windows = [
            window.to_json()
            for window in self.ssm_backend.describe_maintenance_windows(filters)
        ]
        return ActionResult({"WindowIdentities": windows})

    def delete_maintenance_window(self) -> ActionResult:
        window_id = self._get_param("WindowId")
        self.ssm_backend.delete_maintenance_window(window_id)
        return EmptyResult()

    def create_patch_baseline(self) -> ActionResult:
        baseline_id = self.ssm_backend.create_patch_baseline(
            name=self._get_param("Name"),
            operating_system=self._get_param("OperatingSystem"),
            global_filters=self._get_param("GlobalFilters", {}),
            approval_rules=self._get_param("ApprovalRules", {}),
            approved_patches=self._get_param("ApprovedPatches", []),
            approved_patches_compliance_level=self._get_param(
                "ApprovedPatchesComplianceLevel"
            ),
            approved_patches_enable_non_security=self._get_param(
                "ApprovedPatchesEnableNonSecurity"
            ),
            rejected_patches=self._get_param("RejectedPatches", []),
            rejected_patches_action=self._get_param("RejectedPatchesAction"),
            description=self._get_param("Description"),
            sources=self._get_param("Sources", []),
            tags=self._get_param("Tags", []),
        )
        return ActionResult({"BaselineId": baseline_id})

    def describe_patch_baselines(self) -> ActionResult:
        filters = self._get_param("Filters", None)
        baselines = [
            baseline.to_json()
            for baseline in self.ssm_backend.describe_patch_baselines(filters)
        ]
        return ActionResult({"BaselineIdentities": baselines})

    def delete_patch_baseline(self) -> ActionResult:
        baseline_id = self._get_param("BaselineId")
        self.ssm_backend.delete_patch_baseline(baseline_id)
        return EmptyResult()

    def register_task_with_maintenance_window(self) -> ActionResult:
        window_task_id = self.ssm_backend.register_task_with_maintenance_window(
            window_id=self._get_param("WindowId"),
            targets=self._get_param("Targets"),
            task_arn=self._get_param("TaskArn"),
            service_role_arn=self._get_param("ServiceRoleArn"),
            task_type=self._get_param("TaskType"),
            task_parameters=self._get_param("TaskParameters"),
            task_invocation_parameters=self._get_param("TaskInvocationParameters"),
            priority=self._get_param("Priority"),
            max_concurrency=self._get_param("MaxConcurrency"),
            max_errors=self._get_param("MaxErrors"),
            logging_info=self._get_param("LoggingInfo"),
            name=self._get_param("Name"),
            description=self._get_param("Description"),
            cutoff_behavior=self._get_param("CutoffBehavior"),
            alarm_configurations=self._get_param("AlarmConfigurations"),
        )
        return ActionResult({"WindowTaskId": window_task_id})

    def describe_maintenance_window_tasks(self) -> ActionResult:
        window_id = self._get_param("WindowId")
        filters = self._get_param("Filters", [])
        tasks = [
            task.to_json()
            for task in self.ssm_backend.describe_maintenance_window_tasks(
                window_id, filters
            )
        ]
        return ActionResult({"Tasks": tasks})

    def deregister_task_from_maintenance_window(self) -> ActionResult:
        window_id = self._get_param("WindowId")
        window_task_id = self._get_param("WindowTaskId")
        self.ssm_backend.deregister_task_from_maintenance_window(
            window_id, window_task_id
        )
        return EmptyResult()

    def get_patch_baseline_for_patch_group(self) -> ActionResult:
        patch_group = self._get_param("PatchGroup")
        operating_system = self._get_param("OperatingSystem")
        baseline_id, patch_group, operating_system = (
            self.ssm_backend.get_patch_baseline_for_patch_group(
                patch_group=patch_group,
                operating_system=operating_system,
            )
        )
        return ActionResult(
            {
                "BaselineId": baseline_id,
                "PatchGroup": patch_group,
                "OperatingSystem": operating_system,
            }
        )

    def deregister_patch_baseline_for_patch_group(self) -> ActionResult:
        baseline_id = self._get_param("BaselineId")
        patch_group = self._get_param("PatchGroup")
        baseline_id, patch_group = (
            self.ssm_backend.deregister_patch_baseline_for_patch_group(
                baseline_id=baseline_id,
                patch_group=patch_group,
            )
        )
        return ActionResult({"BaselineId": baseline_id, "PatchGroup": patch_group})

    def create_association(self) -> ActionResult:
        name = self._get_param("Name")
        instance_id = self._get_param("InstanceId")
        targets = self._get_param("Targets")
        parameters = self._get_param("Parameters")
        schedule_expression = self._get_param("ScheduleExpression")
        output_location = self._get_param("OutputLocation")
        association_name = self._get_param("AssociationName")
        document_version = self._get_param("DocumentVersion")
        max_errors = self._get_param("MaxErrors")
        max_concurrency = self._get_param("MaxConcurrency")
        compliance_severity = self._get_param("ComplianceSeverity")
        apply_only_at_cron_interval = self._get_param("ApplyOnlyAtCronInterval", False)
        association = self.ssm_backend.create_association(
            name=name,
            instance_id=instance_id,
            targets=targets,
            parameters=parameters,
            schedule_expression=schedule_expression,
            output_location=output_location,
            association_name=association_name,
            document_version=document_version,
            max_errors=max_errors,
            max_concurrency=max_concurrency,
            compliance_severity=compliance_severity,
            apply_only_at_cron_interval=apply_only_at_cron_interval,
        )
        return ActionResult({"AssociationDescription": association.describe()})

    def update_association(self) -> ActionResult:
        association_id = self._get_param("AssociationId")
        parameters = self._get_param("Parameters")
        schedule_expression = self._get_param("ScheduleExpression")
        output_location = self._get_param("OutputLocation")
        association_name = self._get_param("AssociationName")
        document_version = self._get_param("DocumentVersion")
        max_errors = self._get_param("MaxErrors")
        max_concurrency = self._get_param("MaxConcurrency")
        compliance_severity = self._get_param("ComplianceSeverity")
        apply_only_at_cron_interval = self._get_param("ApplyOnlyAtCronInterval")
        name = self._get_param("Name")
        targets = self._get_param("Targets")
        association = self.ssm_backend.update_association(
            association_id=association_id,
            parameters=parameters,
            schedule_expression=schedule_expression,
            output_location=output_location,
            association_name=association_name,
            document_version=document_version,
            max_errors=max_errors,
            max_concurrency=max_concurrency,
            compliance_severity=compliance_severity,
            apply_only_at_cron_interval=apply_only_at_cron_interval,
            name=name,
            targets=targets,
        )
        return ActionResult({"AssociationDescription": association.describe()})

    def delete_association(self) -> ActionResult:
        name = self._get_param("Name")
        association_id = self._get_param("AssociationId")
        self.ssm_backend.delete_association(name=name, association_id=association_id)
        return EmptyResult()

    def describe_activations(self) -> ActionResult:
        activations = self.ssm_backend.describe_activations()
        return ActionResult({"ActivationList": activations})

    def describe_association(self) -> ActionResult:
        name = self._get_param("Name")
        instance_id = self._get_param("InstanceId")
        association_id = self._get_param("AssociationId")
        association_version = self._get_param("AssociationVersion")
        result = self.ssm_backend.describe_association(
            name=name,
            instance_id=instance_id,
            association_id=association_id,
            association_version=association_version,
        )
        return ActionResult({"AssociationDescription": result})

    def describe_automation_executions(self) -> ActionResult:
        executions = self.ssm_backend.describe_automation_executions()
        return ActionResult({"AutomationExecutionMetadataList": executions})

    def describe_available_patches(self) -> ActionResult:
        patches = self.ssm_backend.describe_available_patches()
        return ActionResult({"Patches": patches})

    def describe_instance_information(self) -> ActionResult:
        instances = self.ssm_backend.describe_instance_information()
        return ActionResult({"InstanceInformationList": instances})

    def describe_instance_properties(self) -> ActionResult:
        properties = self.ssm_backend.describe_instance_properties()
        return ActionResult({"InstanceProperties": properties})

    def describe_inventory_deletions(self) -> ActionResult:
        deletions = self.ssm_backend.describe_inventory_deletions()
        return ActionResult({"InventoryDeletions": deletions})

    def describe_maintenance_window_schedule(self) -> ActionResult:
        entries = self.ssm_backend.describe_maintenance_window_schedule()
        return ActionResult({"ScheduledWindowExecutions": entries})

    def describe_ops_items(self) -> ActionResult:
        items = self.ssm_backend.describe_ops_items()
        return ActionResult({"OpsItemSummaries": items})

    def describe_patch_groups(self) -> ActionResult:
        groups = self.ssm_backend.describe_patch_groups()
        return ActionResult({"Mappings": groups})

    def get_default_patch_baseline(self) -> ActionResult:
        operating_system = self._get_param("OperatingSystem")
        result = self.ssm_backend.get_default_patch_baseline(
            operating_system=operating_system
        )
        return ActionResult(result)

    def get_inventory(self) -> ActionResult:
        entities = self.ssm_backend.get_inventory()
        return ActionResult({"Entities": entities})

    def get_inventory_schema(self) -> ActionResult:
        schemas = self.ssm_backend.get_inventory_schema()
        return ActionResult({"Schemas": schemas})

    def get_ops_summary(self) -> ActionResult:
        entities = self.ssm_backend.get_ops_summary()
        return ActionResult({"Entities": entities})

    def get_service_setting(self) -> ActionResult:
        setting_id = self._get_param("SettingId")
        result = self.ssm_backend.get_service_setting(setting_id=setting_id)
        return ActionResult(result)

    def list_associations(self) -> ActionResult:
        associations = self.ssm_backend.list_associations()
        return ActionResult({"Associations": associations})

    def list_command_invocations(self) -> ActionResult:
        invocations = self.ssm_backend.list_command_invocations()
        return ActionResult({"CommandInvocations": invocations})

    def list_compliance_items(self) -> ActionResult:
        items = self.ssm_backend.list_compliance_items()
        return ActionResult({"ComplianceItems": items})

    def list_compliance_summaries(self) -> ActionResult:
        summaries = self.ssm_backend.list_compliance_summaries()
        return ActionResult({"ComplianceSummaryItems": summaries})

    def list_nodes(self) -> ActionResult:
        nodes = self.ssm_backend.list_nodes()
        return ActionResult({"Nodes": nodes})

    def list_ops_item_events(self) -> ActionResult:
        events = self.ssm_backend.list_ops_item_events()
        return ActionResult({"Summaries": events})

    def list_ops_item_related_items(self) -> ActionResult:
        filters = self._get_param("Filters")
        ops_item_id = None
        if filters:
            for f in filters:
                if f.get("Key") == "OpsItemId":
                    vals = f.get("Values", [])
                    if vals:
                        ops_item_id = vals[0]
        if not ops_item_id:
            ops_item_id = self._get_param("OpsItemId")
        items = self.ssm_backend.list_ops_item_related_items(ops_item_id=ops_item_id)
        return ActionResult({"Summaries": items})

    def list_ops_metadata(self) -> ActionResult:
        metadata = self.ssm_backend.list_ops_metadata()
        return ActionResult({"OpsMetadataList": metadata})

    def list_resource_compliance_summaries(self) -> ActionResult:
        summaries = self.ssm_backend.list_resource_compliance_summaries()
        return ActionResult({"ResourceComplianceSummaryItems": summaries})

    def list_resource_data_sync(self) -> ActionResult:
        syncs = self.ssm_backend.list_resource_data_sync()
        return ActionResult({"ResourceDataSyncItems": syncs})

    def create_ops_item(self) -> ActionResult:
        title = self._get_param("Title")
        source = self._get_param("Source")
        description = self._get_param("Description")
        priority = self._get_param("Priority")
        category = self._get_param("Category")
        severity = self._get_param("Severity")
        operational_data = self._get_param("OperationalData")
        notifications = self._get_param("Notifications")
        tags = self._get_param("Tags")
        ops_item = self.ssm_backend.create_ops_item(
            title=title,
            source=source,
            description=description,
            priority=priority,
            category=category,
            severity=severity,
            operational_data=operational_data,
            notifications=notifications,
            tags=tags,
        )
        return ActionResult({"OpsItemId": ops_item.ops_item_id, "OpsItemArn": ops_item.arn})

    def get_ops_item(self) -> ActionResult:
        ops_item_id = self._get_param("OpsItemId")
        ops_item = self.ssm_backend.get_ops_item(ops_item_id)
        return ActionResult({"OpsItem": ops_item.to_json()})

    def update_ops_item(self) -> ActionResult:
        ops_item_id = self._get_param("OpsItemId")
        title = self._get_param("Title")
        description = self._get_param("Description")
        status = self._get_param("Status")
        priority = self._get_param("Priority")
        category = self._get_param("Category")
        severity = self._get_param("Severity")
        operational_data = self._get_param("OperationalData")
        notifications = self._get_param("Notifications")
        self.ssm_backend.update_ops_item(
            ops_item_id=ops_item_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            category=category,
            severity=severity,
            operational_data=operational_data,
            notifications=notifications,
        )
        return EmptyResult()

    def create_activation(self) -> ActionResult:
        iam_role = self._get_param("IamRole")
        description = self._get_param("Description")
        default_instance_name = self._get_param("DefaultInstanceName")
        registration_limit = self._get_param("RegistrationLimit", 1)
        expiration_date = self._get_param("ExpirationDate")
        tags = self._get_param("Tags")
        activation = self.ssm_backend.create_activation(
            iam_role=iam_role,
            description=description,
            default_instance_name=default_instance_name,
            registration_limit=registration_limit,
            expiration_date=expiration_date,
            tags=tags,
        )
        return ActionResult({"ActivationId": activation.activation_id, "ActivationCode": str(activation.activation_id)})

    def delete_activation(self) -> ActionResult:
        activation_id = self._get_param("ActivationId")
        self.ssm_backend.delete_activation(activation_id)
        return EmptyResult()

    def create_resource_data_sync(self) -> ActionResult:
        sync_name = self._get_param("SyncName")
        s3_destination = self._get_param("S3Destination")
        sync_type = self._get_param("SyncType")
        sync_source = self._get_param("SyncSource")
        self.ssm_backend.create_resource_data_sync(
            sync_name=sync_name,
            s3_destination=s3_destination,
            sync_type=sync_type,
            sync_source=sync_source,
        )
        return EmptyResult()

    def delete_resource_data_sync(self) -> ActionResult:
        sync_name = self._get_param("SyncName")
        self.ssm_backend.delete_resource_data_sync(sync_name)
        return EmptyResult()

    def start_automation_execution(self) -> ActionResult:
        document_name = self._get_param("DocumentName")
        document_version = self._get_param("DocumentVersion")
        parameters = self._get_param("Parameters")
        target_parameter_name = self._get_param("TargetParameterName")
        targets = self._get_param("Targets")
        mode = self._get_param("Mode")
        max_concurrency = self._get_param("MaxConcurrency")
        max_errors = self._get_param("MaxErrors")
        execution = self.ssm_backend.start_automation_execution(
            document_name=document_name,
            document_version=document_version,
            parameters=parameters,
            target_parameter_name=target_parameter_name,
            targets=targets,
            mode=mode,
            max_concurrency=max_concurrency,
            max_errors=max_errors,
        )
        return ActionResult({"AutomationExecutionId": execution.automation_execution_id})

    def get_automation_execution(self) -> ActionResult:
        automation_execution_id = self._get_param("AutomationExecutionId")
        execution = self.ssm_backend.get_automation_execution(automation_execution_id)
        return ActionResult({"AutomationExecution": execution.get_execution()})

    def stop_automation_execution(self) -> ActionResult:
        automation_execution_id = self._get_param("AutomationExecutionId")
        type_ = self._get_param("Type")
        self.ssm_backend.stop_automation_execution(automation_execution_id, type_)
        return EmptyResult()

    def register_patch_baseline_for_patch_group(self) -> ActionResult:
        baseline_id = self._get_param("BaselineId")
        patch_group = self._get_param("PatchGroup")
        baseline_id, patch_group = (
            self.ssm_backend.register_patch_baseline_for_patch_group(
                baseline_id=baseline_id,
                patch_group=patch_group,
            )
        )
        return ActionResult({"BaselineId": baseline_id, "PatchGroup": patch_group})

    def describe_association_execution_targets(self) -> ActionResult:
        association_id = self._get_param("AssociationId")
        execution_id = self._get_param("ExecutionId")
        targets = self.ssm_backend.describe_association_execution_targets(
            association_id, execution_id
        )
        return ActionResult({"AssociationExecutionTargets": targets})

    def describe_association_executions(self) -> ActionResult:
        association_id = self._get_param("AssociationId")
        executions = self.ssm_backend.describe_association_executions(association_id)
        return ActionResult({"AssociationExecutions": executions})

    def describe_effective_instance_associations(self) -> ActionResult:
        instance_id = self._get_param("InstanceId")
        associations = self.ssm_backend.describe_effective_instance_associations(
            instance_id
        )
        return ActionResult({"Associations": associations})

    def describe_instance_associations_status(self) -> ActionResult:
        instance_id = self._get_param("InstanceId")
        statuses = self.ssm_backend.describe_instance_associations_status(instance_id)
        return ActionResult({"InstanceAssociationStatusInfos": statuses})

    def describe_instance_patch_states(self) -> ActionResult:
        instance_ids = self._get_param("InstanceIds")
        states = self.ssm_backend.describe_instance_patch_states(instance_ids)
        return ActionResult({"InstancePatchStates": states})

    def describe_instance_patch_states_for_patch_group(self) -> ActionResult:
        patch_group = self._get_param("PatchGroup")
        states = self.ssm_backend.describe_instance_patch_states_for_patch_group(
            patch_group
        )
        return ActionResult({"InstancePatchStates": states})

    def describe_patch_group_state(self) -> ActionResult:
        patch_group = self._get_param("PatchGroup")
        result = self.ssm_backend.describe_patch_group_state(patch_group)
        return ActionResult(result)

    def describe_patch_properties(self) -> ActionResult:
        operating_system = self._get_param("OperatingSystem")
        property_ = self._get_param("Property")
        patch_set = self._get_param("PatchSet")
        properties = self.ssm_backend.describe_patch_properties(
            operating_system, property_, patch_set
        )
        return ActionResult({"Properties": properties})

    def describe_sessions(self) -> ActionResult:
        state = self._get_param("State")
        sessions = self.ssm_backend.describe_sessions(state)
        return ActionResult({"Sessions": sessions})

    def get_calendar_state(self) -> ActionResult:
        calendar_names = self._get_param("CalendarNames")
        result = self.ssm_backend.get_calendar_state(calendar_names)
        return ActionResult(result)

    def get_connection_status(self) -> ActionResult:
        target = self._get_param("Target")
        result = self.ssm_backend.get_connection_status(target)
        return ActionResult(result)

    def get_ops_metadata(self) -> ActionResult:
        ops_metadata_arn = self._get_param("OpsMetadataArn")
        result = self.ssm_backend.get_ops_metadata(ops_metadata_arn)
        return ActionResult(result)

    def create_ops_metadata(self) -> ActionResult:
        resource_id = self._get_param("ResourceId")
        metadata = self._get_param("Metadata")
        tags = self._get_param("Tags")
        ops_meta = self.ssm_backend.create_ops_metadata(
            resource_id=resource_id,
            metadata=metadata,
            tags=tags,
        )
        return ActionResult({"OpsMetadataArn": ops_meta.ops_metadata_arn})

    def update_ops_metadata(self) -> ActionResult:
        ops_metadata_arn = self._get_param("OpsMetadataArn")
        metadata_to_update = self._get_param("MetadataToUpdate")
        keys_to_delete = self._get_param("KeysToDelete")
        result_arn = self.ssm_backend.update_ops_metadata(
            ops_metadata_arn=ops_metadata_arn,
            metadata_to_update=metadata_to_update,
            keys_to_delete=keys_to_delete,
        )
        return ActionResult({"OpsMetadataArn": result_arn})

    def delete_ops_metadata(self) -> ActionResult:
        ops_metadata_arn = self._get_param("OpsMetadataArn")
        self.ssm_backend.delete_ops_metadata(ops_metadata_arn)
        return EmptyResult()

    def delete_ops_item(self) -> ActionResult:
        ops_item_id = self._get_param("OpsItemId")
        self.ssm_backend.delete_ops_item(ops_item_id)
        return EmptyResult()

    def associate_ops_item_related_item(self) -> ActionResult:
        ops_item_id = self._get_param("OpsItemId")
        association_type = self._get_param("AssociationType")
        resource_type = self._get_param("ResourceType")
        resource_uri = self._get_param("ResourceUri")
        association_id = self.ssm_backend.associate_ops_item_related_item(
            ops_item_id=ops_item_id,
            association_type=association_type,
            resource_type=resource_type,
            resource_uri=resource_uri,
        )
        return ActionResult({"AssociationId": association_id})

    def disassociate_ops_item_related_item(self) -> ActionResult:
        ops_item_id = self._get_param("OpsItemId")
        association_id = self._get_param("AssociationId")
        self.ssm_backend.disassociate_ops_item_related_item(
            ops_item_id=ops_item_id,
            association_id=association_id,
        )
        return EmptyResult()

    def delete_inventory(self) -> ActionResult:
        type_name = self._get_param("TypeName")
        schema_delete_option = self._get_param("SchemaDeleteOption")
        result = self.ssm_backend.delete_inventory(
            type_name=type_name,
            schema_delete_option=schema_delete_option,
        )
        return ActionResult(result)

    def list_inventory_entries(self) -> ActionResult:
        instance_id = self._get_param("InstanceId")
        type_name = self._get_param("TypeName")
        result = self.ssm_backend.list_inventory_entries(
            instance_id=instance_id,
            type_name=type_name,
        )
        return ActionResult(result)

    def describe_instance_patches(self) -> ActionResult:
        instance_id = self._get_param("InstanceId")
        patches = self.ssm_backend.describe_instance_patches(instance_id)
        return ActionResult({"Patches": patches})

    def describe_maintenance_windows_for_target(self) -> ActionResult:
        targets = self._get_param("Targets")
        resource_type = self._get_param("ResourceType")
        windows = self.ssm_backend.describe_maintenance_windows_for_target(
            targets=targets,
            resource_type=resource_type,
        )
        return ActionResult({"WindowIdentities": windows})

    def list_association_versions(self) -> ActionResult:
        association_id = self._get_param("AssociationId")
        versions = self.ssm_backend.list_association_versions(association_id)
        return ActionResult({"AssociationVersions": versions})

    def list_document_versions(self) -> ActionResult:
        name = self._get_param("Name")
        versions = self.ssm_backend.list_document_versions(name)
        return ActionResult({"DocumentVersions": versions})

    def list_document_metadata_history(self) -> ActionResult:
        name = self._get_param("Name")
        document_version = self._get_param("DocumentVersion")
        result = self.ssm_backend.list_document_metadata_history(
            name=name,
            document_version=document_version,
        )
        return ActionResult(result)

    def update_association_status(self) -> ActionResult:
        name = self._get_param("Name")
        instance_id = self._get_param("InstanceId")
        association_status = self._get_param("AssociationStatus")
        result = self.ssm_backend.update_association_status(
            name=name,
            instance_id=instance_id,
            association_status=association_status,
        )
        return ActionResult({"AssociationDescription": result})

    def update_maintenance_window_target(self) -> ActionResult:
        window_id = self._get_param("WindowId")
        window_target_id = self._get_param("WindowTargetId")
        targets = self._get_param("Targets")
        owner_information = self._get_param("OwnerInformation")
        name = self._get_param("Name")
        description = self._get_param("Description")
        replace = self._get_param("Replace", False)
        result = self.ssm_backend.update_maintenance_window_target(
            window_id=window_id,
            window_target_id=window_target_id,
            targets=targets,
            owner_information=owner_information,
            name=name,
            description=description,
            replace=replace,
        )
        return ActionResult(result)

    def update_maintenance_window_task(self) -> ActionResult:
        window_id = self._get_param("WindowId")
        window_task_id = self._get_param("WindowTaskId")
        targets = self._get_param("Targets")
        task_arn = self._get_param("TaskArn")
        service_role_arn = self._get_param("ServiceRoleArn")
        task_parameters = self._get_param("TaskParameters")
        task_invocation_parameters = self._get_param("TaskInvocationParameters")
        priority = self._get_param("Priority")
        max_concurrency = self._get_param("MaxConcurrency")
        max_errors = self._get_param("MaxErrors")
        logging_info = self._get_param("LoggingInfo")
        name = self._get_param("Name")
        description = self._get_param("Description")
        replace = self._get_param("Replace", False)
        cutoff_behavior = self._get_param("CutoffBehavior")
        alarm_configurations = self._get_param("AlarmConfigurations")
        result = self.ssm_backend.update_maintenance_window_task(
            window_id=window_id,
            window_task_id=window_task_id,
            targets=targets,
            task_arn=task_arn,
            service_role_arn=service_role_arn,
            task_parameters=task_parameters,
            task_invocation_parameters=task_invocation_parameters,
            priority=priority,
            max_concurrency=max_concurrency,
            max_errors=max_errors,
            logging_info=logging_info,
            name=name,
            description=description,
            replace=replace,
            cutoff_behavior=cutoff_behavior,
            alarm_configurations=alarm_configurations,
        )
        return ActionResult(result)

    def update_managed_instance_role(self) -> ActionResult:
        instance_id = self._get_param("InstanceId")
        iam_role = self._get_param("IamRole")
        self.ssm_backend.update_managed_instance_role(
            instance_id=instance_id,
            iam_role=iam_role,
        )
        return EmptyResult()

    def delete_resource_policy(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        policy_id = self._get_param("PolicyId")
        policy_hash = self._get_param("PolicyHash")
        self.ssm_backend.delete_resource_policy(
            resource_arn=resource_arn,
            policy_id=policy_id,
            policy_hash=policy_hash,
        )
        return EmptyResult()

    def get_resource_policies(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        policies = self.ssm_backend.get_resource_policies(resource_arn)
        return ActionResult({"Policies": policies})

    def put_resource_policy(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        policy = self._get_param("Policy")
        policy_id = self._get_param("PolicyId")
        policy_hash = self._get_param("PolicyHash")
        result = self.ssm_backend.put_resource_policy(
            resource_arn=resource_arn,
            policy=policy,
            policy_id=policy_id,
            policy_hash=policy_hash,
        )
        return ActionResult(result)

    def start_change_request_execution(self) -> ActionResult:
        document_name = self._get_param("DocumentName")
        document_version = self._get_param("DocumentVersion")
        parameters = self._get_param("Parameters")
        change_request_name = self._get_param("ChangeRequestName")
        runbooks = self._get_param("Runbooks")
        execution_id = self.ssm_backend.start_change_request_execution(
            document_name=document_name,
            document_version=document_version,
            parameters=parameters,
            change_request_name=change_request_name,
            runbooks=runbooks,
        )
        return ActionResult({"AutomationExecutionId": execution_id})

    def get_patch_baseline(self) -> ActionResult:
        baseline_id = self._get_param("BaselineId")
        result = self.ssm_backend.get_patch_baseline(baseline_id)
        return ActionResult(result)

    def put_compliance_items(self) -> ActionResult:
        resource_id = self._get_param("ResourceId")
        resource_type = self._get_param("ResourceType")
        compliance_type = self._get_param("ComplianceType")
        execution_summary = self._get_param("ExecutionSummary")
        items = self._get_param("Items")
        item_content_hash = self._get_param("ItemContentHash")
        upload_type = self._get_param("UploadType")
        result = self.ssm_backend.put_compliance_items(
            resource_id=resource_id,
            resource_type=resource_type,
            compliance_type=compliance_type,
            execution_summary=execution_summary,
            items=items,
            item_content_hash=item_content_hash,
            upload_type=upload_type,
        )
        return ActionResult(result)

    def reset_service_setting(self) -> ActionResult:
        setting_id = self._get_param("SettingId")
        result = self.ssm_backend.reset_service_setting(setting_id=setting_id)
        return ActionResult(result)

    def update_service_setting(self) -> ActionResult:
        setting_id = self._get_param("SettingId")
        setting_value = self._get_param("SettingValue")
        result = self.ssm_backend.update_service_setting(
            setting_id=setting_id, setting_value=setting_value
        )
        return ActionResult(result)

    def update_resource_data_sync(self) -> ActionResult:
        sync_name = self._get_param("SyncName")
        sync_type = self._get_param("SyncType")
        sync_source = self._get_param("SyncSource")
        self.ssm_backend.update_resource_data_sync(
            sync_name=sync_name,
            sync_type=sync_type,
            sync_source=sync_source,
        )
        return EmptyResult()

    def update_document_metadata(self) -> ActionResult:
        name = self._get_param("Name")
        document_version = self._get_param("DocumentVersion")
        document_reviews = self._get_param("DocumentReviews")
        self.ssm_backend.update_document_metadata(
            name=name,
            document_version=document_version,
            document_reviews=document_reviews,
        )
        return EmptyResult()

    def start_session(self) -> ActionResult:
        target = self._get_param("Target")
        document_name = self._get_param("DocumentName")
        parameters = self._get_param("Parameters")
        reason = self._get_param("Reason")
        result = self.ssm_backend.start_session(
            target=target,
            document_name=document_name,
            parameters=parameters,
            reason=reason,
        )
        return ActionResult(result)

    def resume_session(self) -> ActionResult:
        session_id = self._get_param("SessionId")
        result = self.ssm_backend.resume_session(session_id=session_id)
        return ActionResult(result)

    def terminate_session(self) -> ActionResult:
        session_id = self._get_param("SessionId")
        result = self.ssm_backend.terminate_session(session_id=session_id)
        return ActionResult(result)

    def start_execution_preview(self) -> ActionResult:
        document_name = self._get_param("DocumentName")
        document_version = self._get_param("DocumentVersion")
        execution_inputs = self._get_param("ExecutionInputs")
        result = self.ssm_backend.start_execution_preview(
            document_name=document_name,
            document_version=document_version,
            execution_inputs=execution_inputs,
        )
        return ActionResult(result)

    def get_access_token(self) -> ActionResult:
        access_request_id = self._get_param("AccessRequestId")
        result = self.ssm_backend.get_access_token(
            access_request_id=access_request_id,
        )
        return ActionResult(result)

    def start_access_request(self) -> ActionResult:
        targets = self._get_param("Targets")
        tags = self._get_param("Tags")
        result = self.ssm_backend.start_access_request(
            targets=targets,
            tags=tags,
        )
        return ActionResult(result)
