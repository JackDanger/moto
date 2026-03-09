"""Handles incoming codedeploy requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import CodeDeployBackend, codedeploy_backends


class CodeDeployResponse(BaseResponse):
    """Handler for CodeDeploy requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="codedeploy")
        self.default_response_headers = {"Content-Type": "application/json"}

    @property
    def codedeploy_backend(self) -> CodeDeployBackend:
        """Return backend instance specific for this region."""
        return codedeploy_backends[self.current_account][self.region]

    def batch_get_applications(self) -> str:
        application_names = self._get_param("applicationNames")
        applications = self.codedeploy_backend.batch_get_applications(
            application_names=application_names,
        )

        applications_info = {
            "applicationsInfo": [app.to_dict() for app in applications]
        }
        return json.dumps(applications_info)

    def get_application(self) -> str:
        application_name = self._get_param("applicationName")
        application = self.codedeploy_backend.get_application(
            application_name=application_name,
        )

        return json.dumps({"application": application.to_dict()})

    def get_deployment(self) -> str:
        deployment_id = self._get_param("deploymentId")
        deployment = self.codedeploy_backend.get_deployment(
            deployment_id=deployment_id,
        )
        return json.dumps({"deploymentInfo": deployment.to_dict()})

    def get_deployment_group(self) -> str:
        application_name = self._get_param("applicationName")
        deployment_group_name = self._get_param("deploymentGroupName")
        deployment_group = self.codedeploy_backend.get_deployment_group(
            application_name=application_name,
            deployment_group_name=deployment_group_name,
        )
        return json.dumps({"deploymentGroupInfo": deployment_group.to_dict()})

    def batch_get_deployment_groups(self) -> str:
        application_name = self._get_param("applicationName")
        deployment_group_names = self._get_param("deploymentGroupNames")
        groups = self.codedeploy_backend.batch_get_deployment_groups(
            application_name=application_name,
            deployment_group_names=deployment_group_names,
        )
        return json.dumps({
            "deploymentGroupsInfo": [g.to_dict() for g in groups],
            "errorMessage": "",
        })

    def batch_get_deployments(self) -> str:
        deployment_ids = self._get_param("deploymentIds")
        deployments = self.codedeploy_backend.batch_get_deployments(
            deployment_ids=deployment_ids,
        )

        deployments_info = {
            "deploymentsInfo": [deployment.to_dict() for deployment in deployments]
        }
        return json.dumps(deployments_info)

    def batch_get_deployment_instances(self) -> str:
        deployment_id = self._get_param("deploymentId")
        instance_ids = self._get_param("instanceIds")
        instances = self.codedeploy_backend.batch_get_deployment_instances(
            deployment_id=deployment_id,
            instance_ids=instance_ids,
        )
        return json.dumps({
            "instancesSummary": instances,
            "errorMessage": "",
        })

    def batch_get_deployment_targets(self) -> str:
        deployment_id = self._get_param("deploymentId")
        target_ids = self._get_param("targetIds")
        targets = self.codedeploy_backend.batch_get_deployment_targets(
            deployment_id=deployment_id,
            target_ids=target_ids,
        )
        return json.dumps({"deploymentTargets": targets})

    def batch_get_on_premises_instances(self) -> str:
        instance_names = self._get_param("instanceNames")
        instances = self.codedeploy_backend.batch_get_on_premises_instances(
            instance_names=instance_names,
        )
        return json.dumps({
            "instanceInfos": [inst.to_dict() for inst in instances],
        })

    def batch_get_application_revisions(self) -> str:
        application_name = self._get_param("applicationName")
        revisions = self._get_param("revisions")
        result = self.codedeploy_backend.batch_get_application_revisions(
            application_name=application_name,
            revisions=revisions,
        )
        return json.dumps({
            "applicationName": application_name,
            "errorMessage": "",
            "revisions": result,
        })

    def create_application(self) -> str:
        application_name = self._get_param("applicationName")
        compute_platform = self._get_param("computePlatform")
        tags = self._get_param("tags")
        application_id = self.codedeploy_backend.create_application(
            application_name=application_name,
            compute_platform=compute_platform,
            tags=tags,
        )
        return json.dumps({"applicationId": application_id})

    def create_deployment(self) -> str:
        application_name = self._get_param("applicationName")
        deployment_group_name = self._get_param("deploymentGroupName")
        revision = self._get_param("revision")
        deployment_config_name = self._get_param("deploymentConfigName")
        description = self._get_param("description")
        ignore_application_stop_failures = self._get_bool_param(
            "ignoreApplicationStopFailures"
        )
        target_instances = self._get_param("targetInstances")
        auto_rollback_configuration = self._get_param("autoRollbackConfiguration")
        update_outdated_instances_only = self._get_param("updateOutdatedInstancesOnly")
        file_exists_behavior = self._get_param("fileExistsBehavior")
        override_alarm_configuration = self._get_param("overrideAlarmConfiguration")
        deployment_id = self.codedeploy_backend.create_deployment(
            application_name=application_name,
            deployment_group_name=deployment_group_name,
            revision=revision,
            deployment_config_name=deployment_config_name,
            description=description,
            ignore_application_stop_failures=ignore_application_stop_failures,
            target_instances=target_instances,
            auto_rollback_configuration=auto_rollback_configuration,
            update_outdated_instances_only=update_outdated_instances_only,
            file_exists_behavior=file_exists_behavior,
            override_alarm_configuration=override_alarm_configuration,
        )
        return json.dumps({"deploymentId": deployment_id})

    def create_deployment_group(self) -> str:
        application_name = self._get_param("applicationName")
        deployment_group_name = self._get_param("deploymentGroupName")
        deployment_config_name = self._get_param("deploymentConfigName")
        ec2_tag_filters = self._get_param("ec2TagFilters")
        on_premises_instance_tag_filters = self._get_param(
            "onPremisesInstanceTagFilters"
        )
        auto_scaling_groups = self._get_param("autoScalingGroups")
        service_role_arn = self._get_param("serviceRoleArn")
        trigger_configurations = self._get_param("triggerConfigurations")
        alarm_configuration = self._get_param("alarmConfiguration")
        auto_rollback_configuration = self._get_param("autoRollbackConfiguration")
        outdated_instances_strategy = self._get_param("outdatedInstancesStrategy")
        deployment_style = self._get_param("deploymentStyle")
        blue_green_deployment_configuration = self._get_param(
            "blueGreenDeploymentConfiguration"
        )
        load_balancer_info = self._get_param("loadBalancerInfo")
        ec2_tag_set = self._get_param("ec2TagSet")
        ecs_services = self._get_param("ecsServices")
        on_premises_tag_set = self._get_param("onPremisesTagSet")
        tags = self._get_param("tags")
        termination_hook_enabled = self._get_param("terminationHookEnabled")
        deployment_group_id = self.codedeploy_backend.create_deployment_group(
            application_name=application_name,
            deployment_group_name=deployment_group_name,
            deployment_config_name=deployment_config_name,
            ec2_tag_filters=ec2_tag_filters,
            on_premises_instance_tag_filters=on_premises_instance_tag_filters,
            auto_scaling_groups=auto_scaling_groups,
            service_role_arn=service_role_arn,
            trigger_configurations=trigger_configurations,
            alarm_configuration=alarm_configuration,
            auto_rollback_configuration=auto_rollback_configuration,
            outdated_instances_strategy=outdated_instances_strategy,
            deployment_style=deployment_style,
            blue_green_deployment_configuration=blue_green_deployment_configuration,
            load_balancer_info=load_balancer_info,
            ec2_tag_set=ec2_tag_set,
            ecs_services=ecs_services,
            on_premises_tag_set=on_premises_tag_set,
            tags=tags,
            termination_hook_enabled=termination_hook_enabled,
        )
        return json.dumps({"deploymentGroupId": deployment_group_id})

    def create_deployment_config(self) -> str:
        deployment_config_name = self._get_param("deploymentConfigName")
        minimum_healthy_hosts = self._get_param("minimumHealthyHosts")
        traffic_routing_config = self._get_param("trafficRoutingConfig")
        compute_platform = self._get_param("computePlatform")
        zonal_config = self._get_param("zonalConfig")
        config_id = self.codedeploy_backend.create_deployment_config(
            deployment_config_name=deployment_config_name,
            minimum_healthy_hosts=minimum_healthy_hosts,
            traffic_routing_config=traffic_routing_config,
            compute_platform=compute_platform,
            zonal_config=zonal_config,
        )
        return json.dumps({"deploymentConfigId": config_id})

    def get_deployment_config(self) -> str:
        deployment_config_name = self._get_param("deploymentConfigName")
        config_info = self.codedeploy_backend.get_deployment_config(
            deployment_config_name=deployment_config_name,
        )
        return json.dumps({"deploymentConfigInfo": config_info})

    def delete_application(self) -> str:
        application_name = self._get_param("applicationName")
        self.codedeploy_backend.delete_application(
            application_name=application_name,
        )
        return json.dumps({})

    def delete_deployment_config(self) -> str:
        deployment_config_name = self._get_param("deploymentConfigName")
        self.codedeploy_backend.delete_deployment_config(
            deployment_config_name=deployment_config_name,
        )
        return json.dumps({})

    def delete_deployment_group(self) -> str:
        application_name = self._get_param("applicationName")
        deployment_group_name = self._get_param("deploymentGroupName")
        hooks = self.codedeploy_backend.delete_deployment_group(
            application_name=application_name,
            deployment_group_name=deployment_group_name,
        )
        return json.dumps({"hooksNotCleanedUp": hooks})

    def delete_git_hub_account_token(self) -> str:
        token_name = self._get_param("tokenName")
        result = self.codedeploy_backend.delete_git_hub_account_token(
            token_name=token_name,
        )
        return json.dumps({"tokenName": result})

    def delete_resources_by_external_id(self) -> str:
        external_id = self._get_param("externalId")
        self.codedeploy_backend.delete_resources_by_external_id(
            external_id=external_id,
        )
        return json.dumps({})

    def update_application(self) -> str:
        application_name = self._get_param("applicationName")
        new_application_name = self._get_param("newApplicationName")
        self.codedeploy_backend.update_application(
            application_name=application_name,
            new_application_name=new_application_name,
        )
        return json.dumps({})

    def update_deployment_group(self) -> str:
        application_name = self._get_param("applicationName")
        current_deployment_group_name = self._get_param("currentDeploymentGroupName")
        new_deployment_group_name = self._get_param("newDeploymentGroupName")
        deployment_config_name = self._get_param("deploymentConfigName")
        ec2_tag_filters = self._get_param("ec2TagFilters")
        on_premises_instance_tag_filters = self._get_param("onPremisesInstanceTagFilters")
        auto_scaling_groups = self._get_param("autoScalingGroups")
        service_role_arn = self._get_param("serviceRoleArn")
        trigger_configurations = self._get_param("triggerConfigurations")
        alarm_configuration = self._get_param("alarmConfiguration")
        auto_rollback_configuration = self._get_param("autoRollbackConfiguration")
        outdated_instances_strategy = self._get_param("outdatedInstancesStrategy")
        deployment_style = self._get_param("deploymentStyle")
        blue_green_deployment_configuration = self._get_param("blueGreenDeploymentConfiguration")
        load_balancer_info = self._get_param("loadBalancerInfo")
        ec2_tag_set = self._get_param("ec2TagSet")
        ecs_services = self._get_param("ecsServices")
        on_premises_tag_set = self._get_param("onPremisesTagSet")
        termination_hook_enabled = self._get_param("terminationHookEnabled")
        hooks = self.codedeploy_backend.update_deployment_group(
            application_name=application_name,
            current_deployment_group_name=current_deployment_group_name,
            new_deployment_group_name=new_deployment_group_name,
            deployment_config_name=deployment_config_name,
            ec2_tag_filters=ec2_tag_filters,
            on_premises_instance_tag_filters=on_premises_instance_tag_filters,
            auto_scaling_groups=auto_scaling_groups,
            service_role_arn=service_role_arn,
            trigger_configurations=trigger_configurations,
            alarm_configuration=alarm_configuration,
            auto_rollback_configuration=auto_rollback_configuration,
            outdated_instances_strategy=outdated_instances_strategy,
            deployment_style=deployment_style,
            blue_green_deployment_configuration=blue_green_deployment_configuration,
            load_balancer_info=load_balancer_info,
            ec2_tag_set=ec2_tag_set,
            ecs_services=ecs_services,
            on_premises_tag_set=on_premises_tag_set,
            termination_hook_enabled=termination_hook_enabled,
        )
        return json.dumps({"hooksNotCleanedUp": hooks})

    def list_applications(self) -> str:
        applications = self.codedeploy_backend.list_applications()
        return json.dumps({"applications": applications})

    def list_deployments(self) -> str:
        application_name = self._get_param("applicationName")
        deployment_group_name = self._get_param("deploymentGroupName")
        external_id = self._get_param("externalId")
        include_only_statuses = self._get_param("includeOnlyStatuses")
        create_time_range = self._get_param("createTimeRange")
        deployments = self.codedeploy_backend.list_deployments(
            application_name=application_name,
            deployment_group_name=deployment_group_name,
            external_id=external_id,
            include_only_statuses=include_only_statuses,
            create_time_range=create_time_range,
        )
        return json.dumps({"deployments": deployments})

    def list_deployment_groups(self) -> str:
        application_name = self._get_param("applicationName")
        next_token = self._get_param("nextToken", "")
        deployment_groups = self.codedeploy_backend.list_deployment_groups(
            application_name=application_name,
            next_token=next_token,
        )
        return json.dumps(
            {
                "applicationName": application_name,
                "deploymentGroups": deployment_groups,
                "nextToken": next_token,
            }
        )

    def list_deployment_configs(self) -> str:
        configs = self.codedeploy_backend.list_deployment_configs()
        return json.dumps({
            "deploymentConfigsList": configs,
            "nextToken": "",
        })

    def list_deployment_instances(self) -> str:
        deployment_id = self._get_param("deploymentId")
        instance_status_filter = self._get_param("instanceStatusFilter")
        instance_type_filter = self._get_param("instanceTypeFilter")
        instances = self.codedeploy_backend.list_deployment_instances(
            deployment_id=deployment_id,
            instance_status_filter=instance_status_filter,
            instance_type_filter=instance_type_filter,
        )
        return json.dumps({
            "instancesList": instances,
            "nextToken": "",
        })

    def list_deployment_targets(self) -> str:
        deployment_id = self._get_param("deploymentId")
        target_filters = self._get_param("targetFilters")
        targets = self.codedeploy_backend.list_deployment_targets(
            deployment_id=deployment_id,
            target_filters=target_filters,
        )
        return json.dumps({
            "targetIds": targets,
            "nextToken": "",
        })

    def list_git_hub_account_token_names(self) -> str:
        tokens = self.codedeploy_backend.list_git_hub_account_token_names()
        return json.dumps({
            "tokenNameList": tokens,
            "nextToken": "",
        })

    def list_on_premises_instances(self) -> str:
        registration_status = self._get_param("registrationStatus")
        tag_filters = self._get_param("tagFilters")
        instances = self.codedeploy_backend.list_on_premises_instances(
            registration_status=registration_status,
            tag_filters=tag_filters,
        )
        return json.dumps({
            "instanceNames": instances,
            "nextToken": "",
        })

    def list_application_revisions(self) -> str:
        application_name = self._get_param("applicationName")
        sort_by = self._get_param("sortBy")
        sort_order = self._get_param("sortOrder")
        s3_bucket = self._get_param("s3Bucket")
        s3_key_prefix = self._get_param("s3KeyPrefix")
        deployed = self._get_param("deployed")
        revisions = self.codedeploy_backend.list_application_revisions(
            application_name=application_name,
            sort_by=sort_by,
            sort_order=sort_order,
            s3_bucket=s3_bucket,
            s3_key_prefix=s3_key_prefix,
            deployed=deployed,
        )
        return json.dumps({
            "revisions": revisions,
            "nextToken": "",
        })

    def register_application_revision(self) -> str:
        application_name = self._get_param("applicationName")
        description = self._get_param("description")
        revision = self._get_param("revision")
        self.codedeploy_backend.register_application_revision(
            application_name=application_name,
            description=description,
            revision=revision,
        )
        return json.dumps({})

    def get_application_revision(self) -> str:
        application_name = self._get_param("applicationName")
        revision = self._get_param("revision")
        result = self.codedeploy_backend.get_application_revision(
            application_name=application_name,
            revision=revision,
        )
        return json.dumps(result)

    def get_deployment_instance(self) -> str:
        deployment_id = self._get_param("deploymentId")
        instance_id = self._get_param("instanceId")
        result = self.codedeploy_backend.get_deployment_instance(
            deployment_id=deployment_id,
            instance_id=instance_id,
        )
        return json.dumps({"instanceSummary": result})

    def get_deployment_target(self) -> str:
        deployment_id = self._get_param("deploymentId")
        target_id = self._get_param("targetId")
        result = self.codedeploy_backend.get_deployment_target(
            deployment_id=deployment_id,
            target_id=target_id,
        )
        return json.dumps({"deploymentTarget": result})

    def get_on_premises_instance(self) -> str:
        instance_name = self._get_param("instanceName")
        instance = self.codedeploy_backend.get_on_premises_instance(
            instance_name=instance_name,
        )
        return json.dumps({"instanceInfo": instance.to_dict()})

    def register_on_premises_instance(self) -> str:
        instance_name = self._get_param("instanceName")
        iam_session_arn = self._get_param("iamSessionArn")
        iam_user_arn = self._get_param("iamUserArn")
        self.codedeploy_backend.register_on_premises_instance(
            instance_name=instance_name,
            iam_session_arn=iam_session_arn,
            iam_user_arn=iam_user_arn,
        )
        return json.dumps({})

    def deregister_on_premises_instance(self) -> str:
        instance_name = self._get_param("instanceName")
        self.codedeploy_backend.deregister_on_premises_instance(
            instance_name=instance_name,
        )
        return json.dumps({})

    def add_tags_to_on_premises_instances(self) -> str:
        tags = self._get_param("tags")
        instance_names = self._get_param("instanceNames")
        self.codedeploy_backend.add_tags_to_on_premises_instances(
            tags=tags,
            instance_names=instance_names,
        )
        return json.dumps({})

    def remove_tags_from_on_premises_instances(self) -> str:
        tags = self._get_param("tags")
        instance_names = self._get_param("instanceNames")
        self.codedeploy_backend.remove_tags_from_on_premises_instances(
            tags=tags,
            instance_names=instance_names,
        )
        return json.dumps({})

    def continue_deployment(self) -> str:
        deployment_id = self._get_param("deploymentId")
        self.codedeploy_backend.continue_deployment(
            deployment_id=deployment_id,
        )
        return json.dumps({})

    def stop_deployment(self) -> str:
        deployment_id = self._get_param("deploymentId")
        auto_rollback_enabled = self._get_param("autoRollbackEnabled")
        result = self.codedeploy_backend.stop_deployment(
            deployment_id=deployment_id,
            auto_rollback_enabled=auto_rollback_enabled,
        )
        return json.dumps(result)

    def skip_wait_time_for_instance_termination(self) -> str:
        deployment_id = self._get_param("deploymentId")
        self.codedeploy_backend.skip_wait_time_for_instance_termination(
            deployment_id=deployment_id,
        )
        return json.dumps({})

    def put_lifecycle_event_hook_execution_status(self) -> str:
        deployment_id = self._get_param("deploymentId")
        lifecycle_event_hook_execution_id = self._get_param("lifecycleEventHookExecutionId")
        status = self._get_param("status")
        result = self.codedeploy_backend.put_lifecycle_event_hook_execution_status(
            deployment_id=deployment_id,
            lifecycle_event_hook_execution_id=lifecycle_event_hook_execution_id,
            status=status,
        )
        return json.dumps({"lifecycleEventHookExecutionId": result})

    def list_tags_for_resource(self) -> str:
        """Handler for list_tags_for_resource API call."""
        resource_arn = self._get_param("ResourceArn")
        tags_response = self.codedeploy_backend.list_tags_for_resource(resource_arn)
        return json.dumps(tags_response)

    def tag_resource(self) -> str:
        """Handler for tag_resource API call."""
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags")
        response = self.codedeploy_backend.tag_resource(resource_arn, tags)
        return json.dumps(response)

    def untag_resource(self) -> str:
        """Handler for untag_resource API call."""
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys")
        response = self.codedeploy_backend.untag_resource(resource_arn, tag_keys)
        return json.dumps(response)
