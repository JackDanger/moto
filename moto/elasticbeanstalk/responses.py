from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .exceptions import InvalidParameterValueError
from .models import EBBackend, eb_backends

# AWS Solution Stack Details as of 2025-07-13
SOLUTION_STACK_DETAILS = [
    {
        "SolutionStackName": "64bit Windows Server 2019 v2.19.2 running IIS 10.0",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Windows Server Core 2019 v2.19.2 running IIS 10.0",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Windows Server 2025 v2.19.2 running IIS 10.0",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Windows Server Core 2016 v2.19.2 running IIS 10.0",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Windows Server Core 2025 v2.19.2 running IIS 10.0",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Windows Server 2022 v2.19.2 running IIS 10.0",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Windows Server 2016 v2.19.2 running IIS 10.0",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Windows Server Core 2022 v2.19.2 running IIS 10.0",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2017.03 v2.5.4 running Java 8",
        "PermittedFileTypes": ["jar", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v5.7.0 running Tomcat 9 Corretto 17",
        "PermittedFileTypes": ["war", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v5.7.0 running Tomcat 11 Corretto 17",
        "PermittedFileTypes": ["war", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v5.7.0 running Tomcat 10 Corretto 21",
        "PermittedFileTypes": ["war", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v5.7.0 running Tomcat 11 Corretto 21",
        "PermittedFileTypes": ["war", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v5.7.0 running Tomcat 10 Corretto 17",
        "PermittedFileTypes": ["war", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v5.7.0 running Tomcat 9 Corretto 11",
        "PermittedFileTypes": ["war", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Python 3.11",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.7.0 running PHP 8.2",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.7.0 running PHP 8.4",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Python 3.9",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Python 3.12",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Ruby 3.3",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Ruby 3.4",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Python 3.13",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.7.0 running PHP 8.3",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Ruby 3.2",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v6.6.0 running Node.js 22",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.7.0 running PHP 8.1",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v6.6.0 running Node.js 20",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Corretto 17",
        "PermittedFileTypes": ["jar", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v3.5.0 running .NET 9",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v6.6.0 running Node.js 18",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Corretto 8",
        "PermittedFileTypes": ["jar", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v3.5.0 running .NET 8",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Corretto 11",
        "PermittedFileTypes": ["jar", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Docker",
        "PermittedFileTypes": [],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.2.0 running ECS",
        "PermittedFileTypes": [],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.4.0 running Go 1",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2023 v4.6.0 running Corretto 21",
        "PermittedFileTypes": ["jar", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v4.9.0 running Tomcat 9 Corretto 11",
        "PermittedFileTypes": ["war", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v2.11.0 running .NET Core",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v3.9.0 running Corretto 11",
        "PermittedFileTypes": ["jar", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v3.9.0 running Corretto 8",
        "PermittedFileTypes": ["jar", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v3.13.0 running Go 1",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v5.11.0 running Node.js 18",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v3.5.0 running ECS",
        "PermittedFileTypes": [],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v3.9.0 running Corretto 17",
        "PermittedFileTypes": ["jar", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v3.10.0 running PHP 8.1",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v4.9.0 running Tomcat 9 Corretto 8",
        "PermittedFileTypes": ["war", "zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v4.2.0 running Docker",
        "PermittedFileTypes": [],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v3.3.14 running Python 3.8",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v5.0.2 running Node.js 12",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v5.0.2 running Node.js 10",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2 v0.1.0 running Node.js 12 (BETA)",
        "PermittedFileTypes": ["zip"],
    },
    {
        "SolutionStackName": "64bit Amazon Linux 2018.03 v2.6.33 running Packer 1.0.3",
        "PermittedFileTypes": [],
    },
]


class EBResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="elasticbeanstalk")
        self.automated_parameter_parsing = True

    @property
    def elasticbeanstalk_backend(self) -> EBBackend:
        """
        :rtype: EBBackend
        """
        return eb_backends[self.current_account][self.region]

    def create_application(self) -> ActionResult:
        app = self.elasticbeanstalk_backend.create_application(
            application_name=self._get_param("ApplicationName")
        )

        result = {"Application": app}
        return ActionResult(result)

    def describe_applications(self) -> ActionResult:
        applications = self.elasticbeanstalk_backend.applications.values()
        result = {"Applications": applications}
        return ActionResult(result)

    def create_environment(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        try:
            app = self.elasticbeanstalk_backend.applications[application_name]
        except KeyError:
            raise InvalidParameterValueError(
                f"No Application named '{application_name}' found."
            )

        tags = {tag["Key"]: tag["Value"] for tag in self._get_param("Tags", [])}
        env = self.elasticbeanstalk_backend.create_environment(
            app,
            environment_name=self._get_param("EnvironmentName"),
            stack_name=self._get_param("SolutionStackName"),
            tags=tags,
        )

        result = env
        return ActionResult(result)

    def describe_environments(self) -> ActionResult:
        envs = self.elasticbeanstalk_backend.describe_environments()

        result = {"Environments": envs}
        return ActionResult(result)

    def list_available_solution_stacks(self) -> ActionResult:
        solution_stacks = {
            "SolutionStacks": [
                stack["SolutionStackName"] for stack in SOLUTION_STACK_DETAILS
            ],
            "SolutionStackDetails": SOLUTION_STACK_DETAILS,
        }
        return ActionResult(solution_stacks)

    def update_tags_for_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        tags_to_add = {
            tag["Key"]: tag["Value"] for tag in self._get_param("TagsToAdd", [])
        }
        tags_to_remove = self._get_param("TagsToRemove", [])
        self.elasticbeanstalk_backend.update_tags_for_resource(
            resource_arn, tags_to_add, tags_to_remove
        )
        return EmptyResult()

    def list_tags_for_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        tags = self.elasticbeanstalk_backend.list_tags_for_resource(resource_arn)
        result = {
            "ResourceArn": resource_arn,
            "ResourceTags": [{"Key": k, "Value": v} for k, v in tags.items()],
        }
        return ActionResult(result)

    def create_application_version(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        version_label = self._get_param("VersionLabel")
        description = self._get_param("Description", "")
        source_bundle = self._get_param("SourceBundle")
        version = self.elasticbeanstalk_backend.create_application_version(
            application_name=application_name,
            version_label=version_label,
            description=description,
            source_bundle=source_bundle,
        )
        result = {"ApplicationVersion": version}
        return ActionResult(result)

    def describe_application_versions(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        version_labels = self._get_param("VersionLabels", [])
        versions = self.elasticbeanstalk_backend.describe_application_versions(
            application_name=application_name,
            version_labels=version_labels or None,
        )
        result = {"ApplicationVersions": versions}
        return ActionResult(result)

    def describe_account_attributes(self) -> ActionResult:
        result = {
            "ResourceQuotas": {
                "ApplicationQuota": {"Maximum": 75},
                "ApplicationVersionQuota": {"Maximum": 1000},
                "EnvironmentQuota": {"Maximum": 200},
                "ConfigurationTemplateQuota": {"Maximum": 2000},
                "CustomPlatformQuota": {"Maximum": 50},
            }
        }
        return ActionResult(result)

    def describe_configuration_options(self) -> ActionResult:
        result = {"Options": [], "SolutionStackName": self._get_param("SolutionStackName", "")}
        return ActionResult(result)

    def describe_configuration_settings(self) -> ActionResult:
        result = {"ConfigurationSettings": []}
        return ActionResult(result)

    def describe_environment_health(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        result = {
            "EnvironmentName": environment_name or "",
            "HealthStatus": "Ok",
            "Status": "Ready",
            "Color": "Green",
        }
        return ActionResult(result)

    def describe_environment_managed_action_history(self) -> ActionResult:
        result = {"ManagedActionHistoryItems": []}
        return ActionResult(result)

    def describe_environment_managed_actions(self) -> ActionResult:
        result = {"ManagedActions": []}
        return ActionResult(result)

    def describe_environment_resources(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        result = {
            "EnvironmentResources": {
                "EnvironmentName": environment_name or "",
                "AutoScalingGroups": [],
                "Instances": [],
                "LaunchConfigurations": [],
                "LaunchTemplates": [],
                "LoadBalancers": [],
                "Triggers": [],
                "Queues": [],
            }
        }
        return ActionResult(result)

    def describe_events(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        environment_name = self._get_param("EnvironmentName")
        events = self.elasticbeanstalk_backend.describe_events(
            application_name=application_name,
            environment_name=environment_name,
        )
        result = {"Events": events}
        return ActionResult(result)

    def describe_instances_health(self) -> ActionResult:
        result = {"InstanceHealthList": []}
        return ActionResult(result)

    def describe_platform_version(self) -> ActionResult:
        result = {
            "PlatformDescription": {
                "PlatformArn": self._get_param("PlatformArn", ""),
                "PlatformStatus": "Ready",
                "PlatformCategory": "Custom",
                "OperatingSystemName": "Amazon Linux 2023",
                "OperatingSystemVersion": "2023",
                "ProgrammingLanguages": [],
                "Frameworks": [],
                "CustomAmiList": [],
            }
        }
        return ActionResult(result)

    def list_platform_branches(self) -> ActionResult:
        result = {"PlatformBranchSummaryList": []}
        return ActionResult(result)

    def list_platform_versions(self) -> ActionResult:
        result = {"PlatformSummaryList": []}
        return ActionResult(result)

    def delete_application(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        self.elasticbeanstalk_backend.delete_application(
            application_name=application_name,
        )
        return EmptyResult()

    def create_configuration_template(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        template_name = self._get_param("TemplateName")
        solution_stack_name = self._get_param("SolutionStackName", "")
        description = self._get_param("Description", "")
        option_settings = self._get_param("OptionSettings", [])
        template = self.elasticbeanstalk_backend.create_configuration_template(
            application_name=application_name,
            template_name=template_name,
            solution_stack_name=solution_stack_name,
            description=description,
            option_settings=option_settings,
        )
        result = {
            "ApplicationName": template.application_name,
            "TemplateName": template.template_name,
            "SolutionStackName": template.solution_stack_name,
            "Description": template.description,
            "DateCreated": template.date_created.isoformat(),
            "DateUpdated": template.date_updated.isoformat(),
            "DeploymentStatus": template.deployment_status,
        }
        return ActionResult(result)

    def update_configuration_template(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        template_name = self._get_param("TemplateName")
        description = self._get_param("Description")
        option_settings = self._get_param("OptionSettings")
        template = self.elasticbeanstalk_backend.update_configuration_template(
            application_name=application_name,
            template_name=template_name,
            description=description,
            option_settings=option_settings,
        )
        result = {
            "ApplicationName": template.application_name,
            "TemplateName": template.template_name,
            "SolutionStackName": template.solution_stack_name,
            "Description": template.description,
            "DateCreated": template.date_created.isoformat(),
            "DateUpdated": template.date_updated.isoformat(),
            "DeploymentStatus": template.deployment_status,
        }
        return ActionResult(result)

    def delete_configuration_template(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        template_name = self._get_param("TemplateName")
        self.elasticbeanstalk_backend.delete_configuration_template(
            application_name=application_name,
            template_name=template_name,
        )
        return EmptyResult()

    def update_environment(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        environment_id = self._get_param("EnvironmentId")
        description = self._get_param("Description")
        option_settings = self._get_param("OptionSettings")
        version_label = self._get_param("VersionLabel")
        env = self.elasticbeanstalk_backend.update_environment(
            environment_name=environment_name,
            environment_id=environment_id,
            description=description,
            option_settings=option_settings,
            version_label=version_label,
        )
        return ActionResult(env)

    def terminate_environment(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        environment_id = self._get_param("EnvironmentId")
        env = self.elasticbeanstalk_backend.terminate_environment(
            environment_name=environment_name,
            environment_id=environment_id,
        )
        return ActionResult(env)

    def rebuild_environment(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        environment_id = self._get_param("EnvironmentId")
        self.elasticbeanstalk_backend.rebuild_environment(
            environment_name=environment_name,
            environment_id=environment_id,
        )
        return EmptyResult()

    def abort_environment_update(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        environment_id = self._get_param("EnvironmentId")
        self.elasticbeanstalk_backend.abort_environment_update(
            environment_name=environment_name,
            environment_id=environment_id,
        )
        return EmptyResult()

    def swap_environment_cnam_es(self) -> ActionResult:
        # Method name matches camelcase_to_underscores("SwapEnvironmentCNAMEs")
        source_environment_name = self._get_param("SourceEnvironmentName")
        source_environment_id = self._get_param("SourceEnvironmentId")
        destination_environment_name = self._get_param("DestinationEnvironmentName")
        destination_environment_id = self._get_param("DestinationEnvironmentId")
        self.elasticbeanstalk_backend.swap_environment_cnames(
            source_environment_name=source_environment_name,
            source_environment_id=source_environment_id,
            destination_environment_name=destination_environment_name,
            destination_environment_id=destination_environment_id,
        )
        return EmptyResult()

    def compose_environments(self) -> ActionResult:
        application_name = self._get_param("ApplicationName")
        group_name = self._get_param("GroupName")
        version_labels = self._get_param("VersionLabels", [])
        envs = self.elasticbeanstalk_backend.compose_environments(
            application_name=application_name,
            group_name=group_name,
            version_labels=version_labels or None,
        )
        result = {"Environments": envs}
        return ActionResult(result)

    def create_platform_version(self) -> ActionResult:
        platform_name = self._get_param("PlatformName", "custom-platform")
        platform_version = self._get_param("PlatformVersion", "1.0.0")
        pv = self.elasticbeanstalk_backend.create_platform_version(
            platform_name=platform_name,
            platform_version=platform_version,
        )
        result = {
            "PlatformSummary": {
                "PlatformArn": pv.platform_arn,
                "PlatformStatus": pv.platform_status,
            },
            "Builder": {"ARN": ""},
        }
        return ActionResult(result)

    def delete_platform_version(self) -> ActionResult:
        platform_arn = self._get_param("PlatformArn", "")
        self.elasticbeanstalk_backend.delete_platform_version(
            platform_arn=platform_arn,
        )
        return EmptyResult()

    def request_environment_info(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        environment_id = self._get_param("EnvironmentId")
        info_type = self._get_param("InfoType", "tail")
        self.elasticbeanstalk_backend.request_environment_info(
            environment_name=environment_name,
            environment_id=environment_id,
            info_type=info_type,
        )
        return EmptyResult()

    def retrieve_environment_info(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        environment_id = self._get_param("EnvironmentId")
        info_type = self._get_param("InfoType", "tail")
        info = self.elasticbeanstalk_backend.retrieve_environment_info(
            environment_name=environment_name,
            environment_id=environment_id,
            info_type=info_type,
        )
        result = {"EnvironmentInfo": info}
        return ActionResult(result)

    def apply_environment_managed_action(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        environment_id = self._get_param("EnvironmentId")
        action_id = self._get_param("ActionId")
        result = self.elasticbeanstalk_backend.apply_environment_managed_action(
            environment_name=environment_name,
            environment_id=environment_id,
            action_id=action_id,
        )
        return ActionResult(result)

    def check_dns_availability(self) -> ActionResult:
        cname_prefix = self._get_param("CNAMEPrefix", "")
        result = self.elasticbeanstalk_backend.check_dns_availability(
            cname_prefix=cname_prefix,
        )
        return ActionResult(result)

    def create_storage_location(self) -> ActionResult:
        bucket = self.elasticbeanstalk_backend.create_storage_location()
        return ActionResult({"S3Bucket": bucket})

    def associate_environment_operations_role(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName", "")
        operations_role = self._get_param("OperationsRole", "")
        self.elasticbeanstalk_backend.associate_environment_operations_role(
            environment_name=environment_name,
            operations_role=operations_role,
        )
        return EmptyResult()

    def disassociate_environment_operations_role(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName", "")
        self.elasticbeanstalk_backend.disassociate_environment_operations_role(
            environment_name=environment_name,
        )
        return EmptyResult()

    def restart_app_server(self) -> ActionResult:
        environment_name = self._get_param("EnvironmentName")
        environment_id = self._get_param("EnvironmentId")
        self.elasticbeanstalk_backend.restart_app_server(
            environment_name=environment_name,
            environment_id=environment_id,
        )
        return EmptyResult()

    def update_application(self) -> ActionResult:
        application_name = self._get_param("ApplicationName", "")
        description = self._get_param("Description")
        app = self.elasticbeanstalk_backend.update_application(
            application_name=application_name,
            description=description,
        )
        result = {
            "Application": {
                "ApplicationName": app.application_name,
                "Description": app.description,
                "ApplicationArn": app.arn,
            }
        }
        return ActionResult(result)

    def delete_application_version(self) -> ActionResult:
        application_name = self._get_param("ApplicationName", "")
        version_label = self._get_param("VersionLabel", "")
        delete_source_bundle = self._get_param("DeleteSourceBundle", False)
        self.elasticbeanstalk_backend.delete_application_version(
            application_name=application_name,
            version_label=version_label,
            delete_source_bundle=delete_source_bundle,
        )
        return EmptyResult()

    def delete_environment_configuration(self) -> ActionResult:
        application_name = self._get_param("ApplicationName", "")
        environment_name = self._get_param("EnvironmentName", "")
        self.elasticbeanstalk_backend.delete_environment_configuration(
            application_name=application_name,
            environment_name=environment_name,
        )
        return EmptyResult()

    def update_application_resource_lifecycle(self) -> ActionResult:
        application_name = self._get_param("ApplicationName", "")
        resource_lifecycle_config = self._get_param("ResourceLifecycleConfig", {})
        result = self.elasticbeanstalk_backend.update_application_resource_lifecycle(
            application_name=application_name,
            resource_lifecycle_config=resource_lifecycle_config,
        )
        return ActionResult(result)

    def update_application_version(self) -> ActionResult:
        application_name = self._get_param("ApplicationName", "")
        version_label = self._get_param("VersionLabel", "")
        description = self._get_param("Description")
        version = self.elasticbeanstalk_backend.update_application_version(
            application_name=application_name,
            version_label=version_label,
            description=description,
        )
        result = {
            "ApplicationVersion": {
                "ApplicationName": version.application_name,
                "VersionLabel": version.version_label,
                "Description": version.description,
                "Status": version.status,
            }
        }
        return ActionResult(result)

    def validate_configuration_settings(self) -> ActionResult:
        application_name = self._get_param("ApplicationName", "")
        template_name = self._get_param("TemplateName")
        environment_name = self._get_param("EnvironmentName")
        option_settings = self._get_param("OptionSettings", [])
        messages = self.elasticbeanstalk_backend.validate_configuration_settings(
            application_name=application_name,
            template_name=template_name,
            environment_name=environment_name,
            option_settings=option_settings,
        )
        return ActionResult({"Messages": messages})
