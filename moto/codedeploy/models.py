"""CodeDeployBackend class with methods for supported APIs."""

import uuid
from enum import Enum
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_with_milliseconds
from moto.utilities.tagging_service import TaggingService

from .exceptions import (
    ApplicationAlreadyExistsException,
    ApplicationDoesNotExistException,
    ApplicationNameRequiredException,
    DeploymentConfigAlreadyExistsException,
    DeploymentConfigDoesNotExistException,
    DeploymentConfigInUseException,
    DeploymentDoesNotExistException,
    DeploymentGroupAlreadyExistsException,
    DeploymentGroupDoesNotExistException,
    DeploymentGroupNameRequiredException,
    InstanceNameRequiredException,
    InstanceNotRegisteredException,
)


class Application(BaseModel):
    def __init__(
        self, application_name: str, compute_platform: str, tags: list[dict[str, str]]
    ):
        self.id = str(uuid.uuid4())
        self.application_name = application_name
        self.compute_platform = compute_platform
        self.tags = tags.copy() if tags else []

        # Boto docs mention that the field should be datetime, but AWS API says number
        self.create_time = iso_8601_datetime_with_milliseconds()

        # Revisions registered for this application
        self.revisions: dict[str, dict[str, Any]] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "applicationId": self.id,
            "applicationName": self.application_name,
            "createTime": self.create_time,
            "computePlatform": self.compute_platform,
        }


class CodeDeployDefault(str, Enum):
    # https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html
    AllAtOnce = "AllAtOnce"
    HalfAtATime = "HalfAtATime"
    OneAtATime = "OneAtATime"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}.{self.value}"


class AlarmConfiguration(BaseModel):
    def __init__(
        self,
        alarms: Optional[list[dict[str, Any]]] = None,
        enabled: Optional[bool] = False,
        ignore_poll_alarm_failure: bool = False,
    ):
        self.alarms = alarms or []
        self.enabled = enabled
        self.ignore_poll_alarm_failure = ignore_poll_alarm_failure


class DeploymentConfig(BaseModel):
    def __init__(
        self,
        deployment_config_name: str,
        minimum_healthy_hosts: Optional[dict[str, Any]],
        traffic_routing_config: Optional[dict[str, Any]],
        compute_platform: Optional[str],
        zonal_config: Optional[dict[str, Any]],
    ):
        self.deployment_config_id = str(uuid.uuid4())
        self.deployment_config_name = deployment_config_name
        self.minimum_healthy_hosts = minimum_healthy_hosts or {}
        self.traffic_routing_config = traffic_routing_config or {}
        self.compute_platform = compute_platform or "Server"
        self.zonal_config = zonal_config or {}
        self.create_time = iso_8601_datetime_with_milliseconds()

    def to_dict(self) -> dict[str, Any]:
        return {
            "deploymentConfigId": self.deployment_config_id,
            "deploymentConfigName": self.deployment_config_name,
            "minimumHealthyHosts": self.minimum_healthy_hosts,
            "trafficRoutingConfig": self.traffic_routing_config,
            "computePlatform": self.compute_platform,
            "zonalConfig": self.zonal_config,
            "createTime": self.create_time,
        }


class OnPremisesInstance(BaseModel):
    def __init__(
        self,
        instance_name: str,
        iam_session_arn: Optional[str] = None,
        iam_user_arn: Optional[str] = None,
    ):
        self.instance_name = instance_name
        self.iam_session_arn = iam_session_arn or ""
        self.iam_user_arn = iam_user_arn or ""
        self.register_time = iso_8601_datetime_with_milliseconds()
        self.deregister_time: Optional[str] = None
        self.tags: list[dict[str, str]] = []

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "instanceName": self.instance_name,
            "iamSessionArn": self.iam_session_arn,
            "iamUserArn": self.iam_user_arn,
            "registerTime": self.register_time,
            "tags": self.tags,
        }
        if self.deregister_time:
            result["deregisterTime"] = self.deregister_time
        return result


class DeploymentGroup(BaseModel):
    def __init__(
        self,
        application: Application,
        deployment_group_name: str,
        deployment_config_name: Optional[str],
        ec2_tag_filters: Optional[list[Any]],
        on_premises_instance_tag_filters: Optional[list[Any]],
        auto_scaling_groups: Optional[list[str]],
        service_role_arn: str,
        trigger_configurations: Optional[list[Any]],
        alarm_configuration: Optional[AlarmConfiguration],
        auto_rollback_configuration: Optional[dict[str, Any]],
        outdated_instances_strategy: Optional[str],
        deployment_style: Optional[Any],
        blue_green_deployment_configuration: Optional[Any],
        load_balancer_info: Optional[Any],
        ec2_tag_set: Optional[Any],
        ecs_services: Optional[list[Any]],
        on_premises_tag_set: Optional[Any],
        tags: Optional[list[dict[str, str]]],
        termination_hook_enabled: Optional[bool],
    ):
        self.application = application
        self.deployment_group_name = deployment_group_name
        self.deployment_config_name = deployment_config_name
        self.ec2_tag_filters = ec2_tag_filters or []
        self.on_premises_instance_tag_filters = on_premises_instance_tag_filters or []
        self.auto_scaling_groups = auto_scaling_groups or []
        self.service_role_arn = service_role_arn
        self.trigger_configurations = trigger_configurations or []
        self.alarm_configuration = alarm_configuration
        self.auto_rollback_configuration = auto_rollback_configuration or {}
        self.outdated_instances_strategy = outdated_instances_strategy
        self.deployment_style = deployment_style or {}
        self.blue_green_deployment_configuration = (
            blue_green_deployment_configuration or {}
        )
        self.load_balancer_info = load_balancer_info or {}
        self.ec2_tag_set = ec2_tag_set or {}
        self.ecs_services = ecs_services or []
        self.on_premises_tag_set = on_premises_tag_set or {}
        self.tags = tags or []
        self.termination_hook_enabled = termination_hook_enabled
        self.deployment_group_id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        return {
            "applicationName": self.application.application_name,
            "deploymentGroupId": self.deployment_group_id,
            "deploymentGroupName": self.deployment_group_name,
            "deploymentConfigName": str(self.deployment_config_name),
            "ec2TagFilters": self.ec2_tag_filters,
            "onPremisesInstanceTagFilters": self.on_premises_instance_tag_filters,
            "autoScalingGroups": self.auto_scaling_groups,
            "serviceRoleArn": self.service_role_arn,
            "targetRevision": {},  # TODO
            "triggerConfigurations": self.trigger_configurations,
            "alarmConfiguration": {},  # TODO
            "autoRollbackConfiguration": self.auto_rollback_configuration,
            "deploymentStyle": self.deployment_style,
            "outdatedInstancesStrategy": self.outdated_instances_strategy,
            "blueGreenDeploymentConfiguration": self.blue_green_deployment_configuration,
            "loadBalancerInfo": self.load_balancer_info,
            "lastSuccessfulDeployment": {},  # TODO
            "lastAttemptedDeployment": {},  # TODO
            "ec2TagSet": self.ec2_tag_set,
            "onPremisesTagSet": self.on_premises_tag_set,
            "computePlatform": self.application.compute_platform,
            "ecsServices": self.ecs_services,
            "terminationHookEnabled": self.termination_hook_enabled,
        }


class DeploymentInfo(BaseModel):
    def __init__(
        self,
        application: Application,
        deployment_group: DeploymentGroup,
        revision: str,
        deployment_config_name: Optional[str],
        description: Optional[str],
        ignore_application_stop_failures: Optional[bool],
        targetInstances: Optional[dict[str, Any]],
        auto_rollback_configuration: Optional[dict[str, Any]],
        update_outdated_instances_only: Optional[bool],
        file_exists_behavior: Optional[str],
        override_alarm_configuration: Optional[AlarmConfiguration],
        creator: Optional[str],
    ):
        self.application = application
        self.deployment_group = deployment_group
        self.deployment_id = str(uuid.uuid4())
        self.application_name = application.application_name
        self.deployment_group_name = deployment_group.deployment_group_name
        self.revision = revision
        self.status = "Created"

        # Boto docs mention that the time fields should be datetime, but AWS API says number
        self.create_time = iso_8601_datetime_with_milliseconds()
        self.start_time = None  # iso_8601_datetime_with_milliseconds()
        self.complete_time = None  # iso_8601_datetime_with_milliseconds()

        # summary of deployment status of the instances in the deployment
        self.deployment_overview = {
            "Pending": 0,
            "InProgress": 0,
            "Succeeded": 0,
            "Failed": 0,
            "Skipped": 0,
            "Ready": 0,
        }
        self.description = description

        # the means by which the deployment was created: {user, autoscaling, codeDeployRollback, CodeDeployAutoUpdate}
        self.creator = "user" if not creator else creator

        self.deployment_config_name = deployment_config_name

        self.ignore_application_stop_failures = ignore_application_stop_failures
        self.target_instances = targetInstances
        self.auto_rollback_configuration = auto_rollback_configuration
        self.update_outdated_instances_only = update_outdated_instances_only
        self.instance_termination_wait_time_started = False

        self.additional_deployment_status_info = ""

        self.file_exists_behavior = file_exists_behavior
        self.deployment_status_messages: list[str] = []
        self.external_id = ""
        self.related_deployments: dict[str, Any] = {}
        self.override_alarm_configuration = override_alarm_configuration

    def to_dict(self) -> dict[str, Any]:
        return {
            "applicationName": self.application_name,
            "deploymentGroupName": self.deployment_group_name,
            "deploymentConfigName": str(self.deployment_config_name),
            "deploymentId": self.deployment_id,
            "previousRevision": {},  # TODO
            "revision": self.revision,
            "status": self.status,
            "errorInformation": {},  # TODO
            "createTime": self.create_time,
            "startTime": self.start_time,
            "completeTime": self.complete_time,
            "deploymentOverview": self.deployment_overview,
            "description": self.description,
            "creator": self.creator,
            "ignoreApplicationStopFailures": self.ignore_application_stop_failures,
            "autoRollbackConfiguration": self.auto_rollback_configuration,
            "updateOutdatedInstancesOnly": self.update_outdated_instances_only,
            "rollbackInfo": {},  # TODO information about a deployment rollback
            "deploymentStyle": self.deployment_group.deployment_style,
            "targetInstances": self.target_instances,
            "instanceTerminationWaitTimeStarted": self.instance_termination_wait_time_started,  # TODO
            "blueGreenDeploymentConfiguration": self.deployment_group.blue_green_deployment_configuration,
            "loadBalancerInfo": self.deployment_group.load_balancer_info,
            "additionalDeploymentStatusInfo": self.additional_deployment_status_info,  # TODO
            "fileExistsBehavior": self.file_exists_behavior,
            "deploymentStatusMessages": self.deployment_status_messages,  # TODO
            "computePlatform": self.application.compute_platform,
            "externalId": self.external_id,
            "relatedDeployments": self.related_deployments,  # TODO
            "overrideAlarmConfiguration": self.override_alarm_configuration,
        }


# Default deployment configs that always exist
DEFAULT_DEPLOYMENT_CONFIGS = [
    "CodeDeployDefault.AllAtOnce",
    "CodeDeployDefault.HalfAtATime",
    "CodeDeployDefault.OneAtATime",
    "CodeDeployDefault.ECSLinear10PercentEvery1Minutes",
    "CodeDeployDefault.ECSLinear10PercentEvery3Minutes",
    "CodeDeployDefault.ECSCanary10Percent5Minutes",
    "CodeDeployDefault.ECSCanary10Percent15Minutes",
    "CodeDeployDefault.ECSAllAtOnce",
    "CodeDeployDefault.LambdaLinear10PercentEvery1Minute",
    "CodeDeployDefault.LambdaLinear10PercentEvery2Minutes",
    "CodeDeployDefault.LambdaLinear10PercentEvery3Minutes",
    "CodeDeployDefault.LambdaLinear10PercentEvery10Minutes",
    "CodeDeployDefault.LambdaCanary10Percent5Minutes",
    "CodeDeployDefault.LambdaCanary10Percent10Minutes",
    "CodeDeployDefault.LambdaCanary10Percent15Minutes",
    "CodeDeployDefault.LambdaCanary10Percent30Minutes",
    "CodeDeployDefault.LambdaAllAtOnce",
]


class CodeDeployBackend(BaseBackend):
    """Implementation of CodeDeploy APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.applications: dict[str, Application] = {}
        self.deployments: dict[str, DeploymentInfo] = {}
        self.deployment_groups: dict[str, dict[str, DeploymentGroup]] = {}
        self.deployment_configs: dict[str, DeploymentConfig] = {}
        self.on_premises_instances: dict[str, OnPremisesInstance] = {}
        self.tagger = TaggingService()

    def _arn_for_app(self, app_name: str) -> str:
        return f"arn:aws:codedeploy:{self.region_name}:{self.account_id}:application:{app_name}"

    def _arn_for_dg(self, app_name: str, dg_name: str) -> str:
        return f"arn:aws:codedeploy:{self.region_name}:{self.account_id}:deploymentgroup:{app_name}/{dg_name}"

    def _arn_for_deployment(self, deployment_id: str) -> str:
        return f"arn:aws:codedeploy:{self.region_name}:{self.account_id}:deployment:{deployment_id}"

    def get_application(self, application_name: str) -> Application:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )
        return self.applications[application_name]

    def batch_get_applications(self, application_names: list[str]) -> list[Application]:
        applications_info = []
        for app_name in application_names:
            app_info = self.get_application(app_name)
            applications_info.append(app_info)

        return applications_info

    def get_deployment(self, deployment_id: str) -> DeploymentInfo:
        if deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        return self.deployments[deployment_id]

    def get_deployment_group(
        self, application_name: str, deployment_group_name: str
    ) -> DeploymentGroup:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )

        # application can also exist but just not associated with a deployment group
        if (
            application_name not in self.deployment_groups
            or deployment_group_name not in self.deployment_groups[application_name]
        ):
            raise DeploymentGroupDoesNotExistException(
                f"The deployment group {deployment_group_name} does not exist with the user or AWS account."
            )
        return self.deployment_groups[application_name][deployment_group_name]

    def batch_get_deployment_groups(
        self, application_name: str, deployment_group_names: list[str]
    ) -> list[DeploymentGroup]:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )
        groups = []
        for name in deployment_group_names:
            if application_name in self.deployment_groups and name in self.deployment_groups[application_name]:
                groups.append(self.deployment_groups[application_name][name])
        return groups

    def batch_get_deployments(self, deployment_ids: list[str]) -> list[DeploymentInfo]:
        deployments = []
        for dep_id in deployment_ids:
            if dep_id in self.deployments:
                deployment_info = self.deployments[dep_id]
                deployments.append(deployment_info)

        return deployments

    def batch_get_deployment_instances(
        self, deployment_id: str, instance_ids: list[str]
    ) -> list[dict[str, Any]]:
        if deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        # Return empty summaries - instances are not tracked in detail
        return []

    def batch_get_deployment_targets(
        self, deployment_id: str, target_ids: list[str]
    ) -> list[dict[str, Any]]:
        if deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        return []

    def batch_get_on_premises_instances(
        self, instance_names: list[str]
    ) -> list[OnPremisesInstance]:
        result = []
        for name in instance_names:
            if name in self.on_premises_instances:
                result.append(self.on_premises_instances[name])
        return result

    def batch_get_application_revisions(
        self, application_name: str, revisions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )
        app = self.applications[application_name]
        result = []
        for rev in revisions:
            rev_key = str(rev)
            info = app.revisions.get(rev_key, {})
            result.append({
                "revisionLocation": rev,
                "genericRevisionInfo": info,
            })
        return result

    def create_application(
        self, application_name: str, compute_platform: str, tags: list[dict[str, str]]
    ) -> str:
        if application_name in self.applications:
            raise ApplicationAlreadyExistsException(
                f"The application {application_name} already exists with the user or AWS account."
            )

        app = Application(application_name, compute_platform, tags)
        self.applications[app.application_name] = app

        if tags:
            app_arn = self._arn_for_app(application_name)
            self.tagger.tag_resource(app_arn, tags)

        return app.id

    def create_deployment(
        self,
        application_name: str,
        deployment_group_name: str,
        revision: str,
        deployment_config_name: Optional[str] = None,
        description: Optional[str] = None,
        ignore_application_stop_failures: Optional[bool] = None,
        target_instances: Optional[Any] = None,
        auto_rollback_configuration: Optional[Any] = None,
        update_outdated_instances_only: Optional[bool] = None,
        file_exists_behavior: Optional[str] = None,
        override_alarm_configuration: Optional[Any] = None,
    ) -> str:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )

        if deployment_group_name:
            if deployment_group_name not in self.deployment_groups.get(
                application_name, {}
            ):
                raise DeploymentGroupDoesNotExistException(
                    "Deployment group name does not exist."
                )
        else:
            raise DeploymentGroupNameRequiredException(
                "Deployment group name is required."
            )

        if not deployment_config_name:
            deployment_config_name = self.deployment_groups[application_name][
                deployment_group_name
            ].deployment_config_name

        deployment = DeploymentInfo(
            self.applications[application_name],
            self.deployment_groups[application_name][deployment_group_name],
            revision,
            deployment_config_name,
            description,
            ignore_application_stop_failures,
            target_instances,
            auto_rollback_configuration,
            update_outdated_instances_only,
            file_exists_behavior,
            override_alarm_configuration,
            "user",
        )

        self.deployments[deployment.deployment_id] = deployment

        deployment_arn = self._arn_for_deployment(deployment.deployment_id)
        if self.deployment_groups[application_name][deployment_group_name].tags:
            self.tagger.tag_resource(
                deployment_arn,
                self.deployment_groups[application_name][deployment_group_name].tags,
            )

        return deployment.deployment_id

    # TODO support all optional fields
    def create_deployment_group(
        self,
        application_name: str,
        deployment_group_name: str,
        deployment_config_name: Optional[str],
        ec2_tag_filters: Optional[list[dict[str, str]]],
        on_premises_instance_tag_filters: Optional[list[dict[str, str]]],
        auto_scaling_groups: Optional[list[str]],
        service_role_arn: str,
        trigger_configurations: Optional[list[dict[str, Any]]] = None,
        alarm_configuration: Optional[AlarmConfiguration] = None,
        auto_rollback_configuration: Optional[dict[str, Any]] = None,
        outdated_instances_strategy: Optional[str] = None,
        deployment_style: Optional[dict[str, str]] = None,
        blue_green_deployment_configuration: Optional[dict[str, Any]] = None,
        load_balancer_info: Optional[dict[str, Any]] = None,
        ec2_tag_set: Optional[dict[str, Any]] = None,
        ecs_services: Optional[list[dict[str, str]]] = None,
        on_premises_tag_set: Optional[dict[str, Any]] = None,
        tags: Optional[list[dict[str, str]]] = None,
        termination_hook_enabled: Optional[bool] = None,
    ) -> str:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )

        if deployment_group_name in self.deployment_groups.get(application_name, {}):
            raise DeploymentGroupAlreadyExistsException(
                f"Deployment group {deployment_group_name} already exists."
            )

        # if deployment_config_name is not specified, use the default
        if not deployment_config_name:
            deployment_config_name = CodeDeployDefault.OneAtATime

        dg = DeploymentGroup(
            self.applications[application_name],
            deployment_group_name,
            deployment_config_name,
            ec2_tag_filters,
            on_premises_instance_tag_filters,
            auto_scaling_groups,
            service_role_arn,
            trigger_configurations,
            alarm_configuration,
            auto_rollback_configuration,
            outdated_instances_strategy,
            deployment_style,
            blue_green_deployment_configuration,
            load_balancer_info,
            ec2_tag_set,
            ecs_services,
            on_premises_tag_set,
            tags,
            termination_hook_enabled,
        )

        if application_name not in self.deployment_groups:
            self.deployment_groups[application_name] = {}
        self.deployment_groups[application_name][dg.deployment_group_name] = dg

        if tags:
            dg_arn = self._arn_for_dg(application_name, deployment_group_name)
            self.tagger.tag_resource(dg_arn, tags)

        return dg.deployment_group_id

    def create_deployment_config(
        self,
        deployment_config_name: str,
        minimum_healthy_hosts: Optional[dict[str, Any]],
        traffic_routing_config: Optional[dict[str, Any]],
        compute_platform: Optional[str],
        zonal_config: Optional[dict[str, Any]],
    ) -> str:
        if deployment_config_name in self.deployment_configs or deployment_config_name in DEFAULT_DEPLOYMENT_CONFIGS:
            raise DeploymentConfigAlreadyExistsException(
                f"A deployment configuration with the name {deployment_config_name} already exists."
            )
        config = DeploymentConfig(
            deployment_config_name,
            minimum_healthy_hosts,
            traffic_routing_config,
            compute_platform,
            zonal_config,
        )
        self.deployment_configs[deployment_config_name] = config
        return config.deployment_config_id

    def get_deployment_config(self, deployment_config_name: str) -> dict[str, Any]:
        if deployment_config_name in DEFAULT_DEPLOYMENT_CONFIGS:
            return {
                "deploymentConfigId": str(uuid.uuid4()),
                "deploymentConfigName": deployment_config_name,
                "minimumHealthyHosts": {"type": "HOST_COUNT", "value": 0},
                "createTime": iso_8601_datetime_with_milliseconds(),
                "computePlatform": "Server",
            }
        if deployment_config_name not in self.deployment_configs:
            raise DeploymentConfigDoesNotExistException(
                f"The deployment config {deployment_config_name} does not exist."
            )
        return self.deployment_configs[deployment_config_name].to_dict()

    def delete_deployment_config(self, deployment_config_name: str) -> None:
        if deployment_config_name in DEFAULT_DEPLOYMENT_CONFIGS:
            raise DeploymentConfigInUseException(
                f"The deployment configuration {deployment_config_name} is a predefined configuration and cannot be deleted."
            )
        if deployment_config_name not in self.deployment_configs:
            raise DeploymentConfigDoesNotExistException(
                f"The deployment config {deployment_config_name} does not exist."
            )
        # Check if any deployment group uses this config
        for app_groups in self.deployment_groups.values():
            for dg in app_groups.values():
                if str(dg.deployment_config_name) == deployment_config_name:
                    raise DeploymentConfigInUseException(
                        f"The deployment configuration {deployment_config_name} is in use."
                    )
        del self.deployment_configs[deployment_config_name]

    def delete_application(self, application_name: str) -> None:
        if application_name not in self.applications:
            return  # AWS does not raise error for deleting non-existent app
        del self.applications[application_name]
        # Clean up associated deployment groups
        self.deployment_groups.pop(application_name, None)
        # Clean up associated deployments
        to_remove = [
            dep_id
            for dep_id, dep in self.deployments.items()
            if dep.application_name == application_name
        ]
        for dep_id in to_remove:
            del self.deployments[dep_id]

    def delete_deployment_group(
        self, application_name: str, deployment_group_name: str
    ) -> list[dict[str, Any]]:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )
        if application_name in self.deployment_groups:
            self.deployment_groups[application_name].pop(deployment_group_name, None)
        return []  # hooksNotCleanedUp

    def delete_git_hub_account_token(self, token_name: Optional[str]) -> str:
        return token_name or ""

    def delete_resources_by_external_id(self, external_id: Optional[str]) -> None:
        pass

    def update_application(
        self,
        application_name: Optional[str],
        new_application_name: Optional[str],
    ) -> None:
        if not application_name:
            return
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )
        if new_application_name and new_application_name != application_name:
            if new_application_name in self.applications:
                raise ApplicationAlreadyExistsException(
                    f"The application {new_application_name} already exists with the user or AWS account."
                )
            app = self.applications.pop(application_name)
            app.application_name = new_application_name
            self.applications[new_application_name] = app
            # Update deployment groups key
            if application_name in self.deployment_groups:
                self.deployment_groups[new_application_name] = self.deployment_groups.pop(application_name)

    def update_deployment_group(
        self,
        application_name: str,
        current_deployment_group_name: str,
        new_deployment_group_name: Optional[str] = None,
        deployment_config_name: Optional[str] = None,
        ec2_tag_filters: Optional[list[dict[str, str]]] = None,
        on_premises_instance_tag_filters: Optional[list[dict[str, str]]] = None,
        auto_scaling_groups: Optional[list[str]] = None,
        service_role_arn: Optional[str] = None,
        trigger_configurations: Optional[list[dict[str, Any]]] = None,
        alarm_configuration: Optional[dict[str, Any]] = None,
        auto_rollback_configuration: Optional[dict[str, Any]] = None,
        outdated_instances_strategy: Optional[str] = None,
        deployment_style: Optional[dict[str, str]] = None,
        blue_green_deployment_configuration: Optional[dict[str, Any]] = None,
        load_balancer_info: Optional[dict[str, Any]] = None,
        ec2_tag_set: Optional[dict[str, Any]] = None,
        ecs_services: Optional[list[dict[str, str]]] = None,
        on_premises_tag_set: Optional[dict[str, Any]] = None,
        termination_hook_enabled: Optional[bool] = None,
    ) -> list[dict[str, Any]]:
        dg = self.get_deployment_group(application_name, current_deployment_group_name)

        if new_deployment_group_name and new_deployment_group_name != current_deployment_group_name:
            if new_deployment_group_name in self.deployment_groups.get(application_name, {}):
                raise DeploymentGroupAlreadyExistsException(
                    f"Deployment group {new_deployment_group_name} already exists."
                )
            del self.deployment_groups[application_name][current_deployment_group_name]
            dg.deployment_group_name = new_deployment_group_name
            self.deployment_groups[application_name][new_deployment_group_name] = dg

        if deployment_config_name is not None:
            dg.deployment_config_name = deployment_config_name
        if ec2_tag_filters is not None:
            dg.ec2_tag_filters = ec2_tag_filters
        if on_premises_instance_tag_filters is not None:
            dg.on_premises_instance_tag_filters = on_premises_instance_tag_filters
        if auto_scaling_groups is not None:
            dg.auto_scaling_groups = auto_scaling_groups
        if service_role_arn is not None:
            dg.service_role_arn = service_role_arn
        if trigger_configurations is not None:
            dg.trigger_configurations = trigger_configurations
        if auto_rollback_configuration is not None:
            dg.auto_rollback_configuration = auto_rollback_configuration
        if outdated_instances_strategy is not None:
            dg.outdated_instances_strategy = outdated_instances_strategy
        if deployment_style is not None:
            dg.deployment_style = deployment_style
        if blue_green_deployment_configuration is not None:
            dg.blue_green_deployment_configuration = blue_green_deployment_configuration
        if load_balancer_info is not None:
            dg.load_balancer_info = load_balancer_info
        if ec2_tag_set is not None:
            dg.ec2_tag_set = ec2_tag_set
        if ecs_services is not None:
            dg.ecs_services = ecs_services
        if on_premises_tag_set is not None:
            dg.on_premises_tag_set = on_premises_tag_set
        if termination_hook_enabled is not None:
            dg.termination_hook_enabled = termination_hook_enabled

        return []  # hooksNotCleanedUp

    # TODO: implement pagination
    def list_applications(self) -> list[str]:
        return list(self.applications.keys())

    # TODO: implement pagination and complete filtering
    def list_deployments(
        self,
        application_name: str,
        deployment_group_name: str,
        external_id: str,
        include_only_statuses: list[str],
        create_time_range: dict[str, Any],
    ) -> list[str]:
        # Ensure if applicationName is specified, then deploymentGroupName must be specified.
        # If deploymentGroupName is specified, application must be specified else error.
        if application_name and not deployment_group_name:
            raise DeploymentGroupNameRequiredException(
                "If applicationName is specified, then deploymentGroupName must be specified."
            )

        if deployment_group_name and not application_name:
            raise ApplicationNameRequiredException(
                "If deploymentGroupName is specified, applicationName must be specified."
            )

        def matches_filters(deployment: DeploymentInfo) -> bool:
            if application_name and deployment.application_name != application_name:
                return False
            if deployment_group_name:
                if application_name not in self.deployment_groups:
                    return False
                if (
                    deployment_group_name
                    not in self.deployment_groups[application_name]
                ):
                    return False
                if deployment.deployment_group_name != deployment_group_name:
                    return False
                if (
                    include_only_statuses
                    and deployment.status not in include_only_statuses
                ):
                    return False
            return True

        return [
            deployment.deployment_id
            for deployment in self.deployments.values()
            if matches_filters(deployment)
        ]

    # TODO: implement pagination
    def list_deployment_groups(
        self, application_name: str, next_token: str
    ) -> list[str]:
        if application_name not in self.deployment_groups:
            return []

        return [
            deployment_group.deployment_group_name
            for deployment_group in self.deployment_groups[application_name].values()
        ]

    def list_deployment_configs(self) -> list[str]:
        configs = list(DEFAULT_DEPLOYMENT_CONFIGS)
        configs.extend(self.deployment_configs.keys())
        return configs

    def list_deployment_instances(
        self,
        deployment_id: str,
        instance_status_filter: Optional[list[str]] = None,
        instance_type_filter: Optional[list[str]] = None,
    ) -> list[str]:
        if deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        return []

    def list_deployment_targets(
        self,
        deployment_id: str,
        target_filters: Optional[dict[str, Any]] = None,
    ) -> list[str]:
        if deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        return []

    def list_git_hub_account_token_names(self) -> list[str]:
        return []

    def list_on_premises_instances(
        self,
        registration_status: Optional[str] = None,
        tag_filters: Optional[list[dict[str, str]]] = None,
    ) -> list[str]:
        return list(self.on_premises_instances.keys())

    def list_application_revisions(
        self,
        application_name: str,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        s3_key_prefix: Optional[str] = None,
        deployed: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )
        app = self.applications[application_name]
        return [
            {"revisionType": "S3", "s3Location": {}}
            for _ in app.revisions
        ]

    def register_application_revision(
        self,
        application_name: str,
        description: Optional[str],
        revision: dict[str, Any],
    ) -> None:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )
        app = self.applications[application_name]
        rev_key = str(revision)
        app.revisions[rev_key] = {
            "description": description or "",
            "registerTime": iso_8601_datetime_with_milliseconds(),
            "firstUsedTime": None,
            "lastUsedTime": None,
        }

    def get_application_revision(
        self, application_name: str, revision: dict[str, Any]
    ) -> dict[str, Any]:
        if application_name not in self.applications:
            raise ApplicationDoesNotExistException(
                f"The application {application_name} does not exist with the user or AWS account."
            )
        app = self.applications[application_name]
        rev_key = str(revision)
        info = app.revisions.get(rev_key, {})
        return {
            "applicationName": application_name,
            "revision": revision,
            "revisionInfo": info,
        }

    def get_deployment_instance(
        self, deployment_id: str, instance_id: str
    ) -> dict[str, Any]:
        if deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        return {
            "deploymentId": deployment_id,
            "instanceId": instance_id,
            "status": "Succeeded",
            "lastUpdatedAt": iso_8601_datetime_with_milliseconds(),
            "lifecycleEvents": [],
        }

    def get_deployment_target(
        self, deployment_id: str, target_id: str
    ) -> dict[str, Any]:
        if deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        return {
            "deploymentTargetType": "InstanceTarget",
            "instanceTarget": {
                "deploymentId": deployment_id,
                "targetId": target_id,
                "targetArn": target_id,
                "status": "Succeeded",
                "lastUpdatedAt": iso_8601_datetime_with_milliseconds(),
                "lifecycleEvents": [],
            },
        }

    def get_on_premises_instance(self, instance_name: str) -> OnPremisesInstance:
        if not instance_name:
            raise InstanceNameRequiredException("Instance name is required.")
        if instance_name not in self.on_premises_instances:
            raise InstanceNotRegisteredException(
                f"The on-premises instance {instance_name} is not registered."
            )
        return self.on_premises_instances[instance_name]

    def register_on_premises_instance(
        self,
        instance_name: str,
        iam_session_arn: Optional[str] = None,
        iam_user_arn: Optional[str] = None,
    ) -> None:
        if not instance_name:
            raise InstanceNameRequiredException("Instance name is required.")
        instance = OnPremisesInstance(instance_name, iam_session_arn, iam_user_arn)
        self.on_premises_instances[instance_name] = instance

    def deregister_on_premises_instance(self, instance_name: str) -> None:
        if not instance_name:
            raise InstanceNameRequiredException("Instance name is required.")
        if instance_name in self.on_premises_instances:
            inst = self.on_premises_instances[instance_name]
            inst.deregister_time = iso_8601_datetime_with_milliseconds()
            del self.on_premises_instances[instance_name]

    def add_tags_to_on_premises_instances(
        self, tags: list[dict[str, str]], instance_names: list[str]
    ) -> None:
        for name in instance_names:
            if name in self.on_premises_instances:
                inst = self.on_premises_instances[name]
                for tag in tags:
                    # Update or add tag
                    existing = [t for t in inst.tags if t.get("Key") == tag.get("Key")]
                    if existing:
                        existing[0]["Value"] = tag.get("Value", "")
                    else:
                        inst.tags.append(tag)

    def remove_tags_from_on_premises_instances(
        self, tags: list[dict[str, str]], instance_names: list[str]
    ) -> None:
        tag_keys = [t.get("Key") for t in tags]
        for name in instance_names:
            if name in self.on_premises_instances:
                inst = self.on_premises_instances[name]
                inst.tags = [t for t in inst.tags if t.get("Key") not in tag_keys]

    def continue_deployment(self, deployment_id: Optional[str]) -> None:
        if deployment_id and deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )

    def stop_deployment(
        self, deployment_id: str, auto_rollback_enabled: Optional[bool] = None
    ) -> dict[str, Any]:
        if deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        deployment = self.deployments[deployment_id]
        deployment.status = "Stopped"
        return {
            "status": "Succeeded",
            "statusMessage": "The deployment was stopped successfully.",
        }

    def skip_wait_time_for_instance_termination(
        self, deployment_id: Optional[str] = None
    ) -> None:
        if deployment_id and deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )

    def put_lifecycle_event_hook_execution_status(
        self,
        deployment_id: Optional[str] = None,
        lifecycle_event_hook_execution_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        if deployment_id and deployment_id not in self.deployments:
            raise DeploymentDoesNotExistException(
                f"The deployment {deployment_id} does not exist with the user or AWS account."
            )
        return lifecycle_event_hook_execution_id or str(uuid.uuid4())

    def list_tags_for_resource(
        self, resource_arn: str
    ) -> dict[str, list[dict[str, str]]]:
        return self.tagger.list_tags_for_resource(resource_arn)

    def tag_resource(
        self, resource_arn: str, tags: list[dict[str, str]]
    ) -> dict[str, Any]:
        self.tagger.tag_resource(resource_arn, tags)
        return {}

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> dict[str, Any]:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)
        return {}


codedeploy_backends = BackendDict(CodeDeployBackend, "codedeploy")
