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
