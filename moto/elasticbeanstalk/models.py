import uuid
import weakref
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel

from ..core.utils import utcnow
from .exceptions import (
    InvalidParameterValueError,
    ResourceNotFoundException,
)
from .utils import make_arn


class Environment(BaseModel):
    def __init__(
        self,
        application: "Application",
        environment_name: str,
        solution_stack_name: str,
        tags: dict[str, str],
    ):
        self.application = weakref.proxy(
            application
        )  # weakref to break circular dependencies
        self.environment_name = environment_name
        self.solution_stack_name = solution_stack_name
        self.tags = tags
        self.date_created = utcnow()
        self.date_updated = utcnow()
        # TODO: These attributes were all hardcoded in the original XML templates and need to be properly implemented.
        self.environment_id = ""
        self.version_label = 1
        self.solution_stack_name = "None"
        self.endpoint_url = ""
        self.cname = ""
        self.status = "Ready"
        self.abortable_operation_in_progress = False
        self.health = "Grey"
        self.health_status = "No Data"
        self.tier = {
            "Name": "WebServer",
            "Type": "Standard",
            "Version": "1.0",
        }
        self.environment_links: list[dict[str, str]] = []

    @property
    def application_name(self) -> str:
        return self.application.application_name

    @property
    def environment_arn(self) -> str:
        resource_path = f"{self.application_name}/{self.environment_name}"
        return make_arn(
            self.region, self.application.account_id, "environment", resource_path
        )

    @property
    def platform_arn(self) -> str:
        return "TODO"  # TODO

    @property
    def region(self) -> str:
        return self.application.region


class ConfigurationTemplate(BaseModel):
    def __init__(
        self,
        application_name: str,
        template_name: str,
        solution_stack_name: str,
        description: str,
        option_settings: list[dict[str, str]],
        region: str,
        account_id: str,
    ):
        self.application_name = application_name
        self.template_name = template_name
        self.solution_stack_name = solution_stack_name
        self.description = description
        self.option_settings = option_settings
        self.date_created = utcnow()
        self.date_updated = utcnow()
        self.deployment_status = "deployed"


class PlatformVersion(BaseModel):
    def __init__(
        self,
        platform_name: str,
        platform_version: str,
        region: str,
        account_id: str,
    ):
        self.platform_name = platform_name
        self.platform_version = platform_version
        self.platform_arn = make_arn(
            region, account_id, "platform", f"{platform_name}/{platform_version}"
        )
        self.platform_status = "Ready"
        self.created_at = utcnow()


class ApplicationVersion(BaseModel):
    def __init__(
        self,
        application_name: str,
        version_label: str,
        description: str,
        source_bundle: Optional[dict[str, str]],
        region: str,
        account_id: str,
    ):
        self.application_name = application_name
        self.version_label = version_label
        self.description = description
        self.source_bundle = source_bundle or {}
        self.date_created = utcnow()
        self.date_updated = utcnow()
        self.status = "UNPROCESSED"
        self.arn = make_arn(
            region, account_id, "applicationversion", f"{application_name}/{version_label}"
        )


class Application(BaseModel):
    def __init__(
        self,
        backend: "EBBackend",
        application_name: str,
    ):
        self.backend = weakref.proxy(backend)  # weakref to break cycles
        self.application_name = application_name
        self.environments: dict[str, Environment] = {}
        self.versions: dict[str, ApplicationVersion] = {}
        self.configuration_templates: dict[str, ConfigurationTemplate] = {}
        self.account_id = self.backend.account_id
        self.region = self.backend.region_name
        self.arn = make_arn(
            self.region, self.account_id, "application", self.application_name
        )

    def create_environment(
        self, environment_name: str, solution_stack_name: str, tags: dict[str, str]
    ) -> Environment:
        if environment_name in self.environments:
            raise InvalidParameterValueError(message="")

        env = Environment(
            application=self,
            environment_name=environment_name,
            solution_stack_name=solution_stack_name,
            tags=tags,
        )
        self.environments[environment_name] = env

        return env


class EBBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.applications: dict[str, Application] = {}
        self.platform_versions: dict[str, PlatformVersion] = {}
        self.environment_info: dict[str, list[dict[str, Any]]] = {}
        self.cname_swaps: list[dict[str, str]] = []

    def create_application(self, application_name: str) -> Application:
        if application_name in self.applications:
            raise InvalidParameterValueError(
                f"Application {application_name} already exists."
            )
        new_app = Application(backend=self, application_name=application_name)
        self.applications[application_name] = new_app
        return new_app

    def create_environment(
        self,
        app: Application,
        environment_name: str,
        stack_name: str,
        tags: dict[str, str],
    ) -> Environment:
        return app.create_environment(
            environment_name=environment_name, solution_stack_name=stack_name, tags=tags
        )

    def describe_environments(self) -> list[Environment]:
        envs = []
        for app in self.applications.values():
            for env in app.environments.values():
                envs.append(env)
        return envs

    def list_available_solution_stacks(self) -> None:
        # Implemented in response.py
        pass

    def update_tags_for_resource(
        self, resource_arn: str, tags_to_add: dict[str, str], tags_to_remove: list[str]
    ) -> None:
        try:
            res = self._find_environment_by_arn(resource_arn)
        except KeyError:
            raise ResourceNotFoundException(
                f"Resource not found for ARN '{resource_arn}'."
            )

        for key, value in tags_to_add.items():
            res.tags[key] = value

        for key in tags_to_remove:
            del res.tags[key]

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        try:
            res = self._find_environment_by_arn(resource_arn)
        except KeyError:
            raise ResourceNotFoundException(
                f"Resource not found for ARN '{resource_arn}'."
            )
        return res.tags

    def _find_environment_by_arn(self, arn: str) -> Environment:
        for app in self.applications.keys():
            for env in self.applications[app].environments.values():
                if env.environment_arn == arn:
                    return env
        raise KeyError()

    def create_application_version(
        self,
        application_name: str,
        version_label: str,
        description: str = "",
        source_bundle: Optional[dict[str, str]] = None,
    ) -> ApplicationVersion:
        if application_name not in self.applications:
            raise InvalidParameterValueError(
                f"No Application named '{application_name}' found."
            )
        app = self.applications[application_name]
        version = ApplicationVersion(
            application_name=application_name,
            version_label=version_label,
            description=description,
            source_bundle=source_bundle,
            region=self.region_name,
            account_id=self.account_id,
        )
        app.versions[version_label] = version
        return version

    def describe_application_versions(
        self,
        application_name: Optional[str] = None,
        version_labels: Optional[list[str]] = None,
    ) -> list[ApplicationVersion]:
        versions: list[ApplicationVersion] = []
        for app in self.applications.values():
            if application_name and app.application_name != application_name:
                continue
            for v in app.versions.values():
                if version_labels and v.version_label not in version_labels:
                    continue
                versions.append(v)
        return versions

    def describe_events(
        self,
        application_name: Optional[str] = None,
        environment_name: Optional[str] = None,
    ) -> list[dict[str, str]]:
        # Return empty events list - no event tracking yet
        return []

    def delete_application(
        self,
        application_name: str,
    ) -> None:
        if application_name in self.applications:
            self.applications.pop(application_name)

    # Configuration Template operations

    def create_configuration_template(
        self,
        application_name: str,
        template_name: str,
        solution_stack_name: str = "",
        description: str = "",
        option_settings: Optional[list[dict[str, str]]] = None,
    ) -> ConfigurationTemplate:
        if application_name not in self.applications:
            raise InvalidParameterValueError(
                f"No Application named '{application_name}' found."
            )
        app = self.applications[application_name]
        template = ConfigurationTemplate(
            application_name=application_name,
            template_name=template_name,
            solution_stack_name=solution_stack_name,
            description=description,
            option_settings=option_settings or [],
            region=self.region_name,
            account_id=self.account_id,
        )
        app.configuration_templates[template_name] = template
        return template

    def describe_configuration_settings(
        self,
        application_name: str,
        template_name: Optional[str] = None,
        environment_name: Optional[str] = None,
    ) -> list[ConfigurationTemplate]:
        if application_name not in self.applications:
            raise InvalidParameterValueError(
                f"No Application named '{application_name}' found."
            )
        app = self.applications[application_name]
        templates: list[ConfigurationTemplate] = []
        if template_name:
            if template_name in app.configuration_templates:
                templates.append(app.configuration_templates[template_name])
        else:
            templates = list(app.configuration_templates.values())
        return templates

    def update_configuration_template(
        self,
        application_name: str,
        template_name: str,
        description: Optional[str] = None,
        option_settings: Optional[list[dict[str, str]]] = None,
    ) -> ConfigurationTemplate:
        if application_name not in self.applications:
            raise InvalidParameterValueError(
                f"No Application named '{application_name}' found."
            )
        app = self.applications[application_name]
        if template_name not in app.configuration_templates:
            raise InvalidParameterValueError(
                f"No Configuration Template named '{template_name}' found."
            )
        template = app.configuration_templates[template_name]
        if description is not None:
            template.description = description
        if option_settings is not None:
            template.option_settings = option_settings
        template.date_updated = utcnow()
        return template

    def delete_configuration_template(
        self,
        application_name: str,
        template_name: str,
    ) -> None:
        if application_name not in self.applications:
            raise InvalidParameterValueError(
                f"No Application named '{application_name}' found."
            )
        app = self.applications[application_name]
        app.configuration_templates.pop(template_name, None)

    # Environment operations

    def update_environment(
        self,
        environment_name: Optional[str] = None,
        environment_id: Optional[str] = None,
        description: Optional[str] = None,
        option_settings: Optional[list[dict[str, str]]] = None,
        version_label: Optional[str] = None,
    ) -> Optional[Environment]:
        for app in self.applications.values():
            for env in app.environments.values():
                if (
                    (environment_name and env.environment_name == environment_name)
                    or (environment_id and env.environment_id == environment_id)
                ):
                    env.date_updated = utcnow()
                    if version_label is not None:
                        env.version_label = version_label
                    return env
        raise InvalidParameterValueError(
            f"No Environment named '{environment_name or environment_id}' found."
        )

    def terminate_environment(
        self,
        environment_name: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> Optional[Environment]:
        for app in self.applications.values():
            for env_name, env in list(app.environments.items()):
                if (
                    (environment_name and env.environment_name == environment_name)
                    or (environment_id and env.environment_id == environment_id)
                ):
                    env.status = "Terminated"
                    env.date_updated = utcnow()
                    del app.environments[env_name]
                    return env
        raise InvalidParameterValueError(
            f"No Environment named '{environment_name or environment_id}' found."
        )

    def rebuild_environment(
        self,
        environment_name: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> None:
        for app in self.applications.values():
            for env in app.environments.values():
                if (
                    (environment_name and env.environment_name == environment_name)
                    or (environment_id and env.environment_id == environment_id)
                ):
                    env.status = "Launching"
                    env.date_updated = utcnow()
                    return
        raise InvalidParameterValueError(
            f"No Environment named '{environment_name or environment_id}' found."
        )

    def abort_environment_update(
        self,
        environment_name: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> None:
        # In real AWS, this aborts an in-progress environment update.
        # In the mock, we just acknowledge the call.
        pass

    def _find_environment(
        self,
        environment_name: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> Optional[Environment]:
        for app in self.applications.values():
            for env in app.environments.values():
                if environment_name and env.environment_name == environment_name:
                    return env
                if environment_id and env.environment_id == environment_id:
                    return env
        return None

    def swap_environment_cnames(
        self,
        source_environment_name: Optional[str] = None,
        source_environment_id: Optional[str] = None,
        destination_environment_name: Optional[str] = None,
        destination_environment_id: Optional[str] = None,
    ) -> None:
        source_env = self._find_environment(
            source_environment_name, source_environment_id
        )
        dest_env = self._find_environment(
            destination_environment_name, destination_environment_id
        )

        if not source_env:
            name = source_environment_name or source_environment_id or ""
            raise InvalidParameterValueError(
                f"No Environment named '{name}' found."
            )
        if not dest_env:
            name = destination_environment_name or destination_environment_id or ""
            raise InvalidParameterValueError(
                f"No Environment named '{name}' found."
            )

        source_env.cname, dest_env.cname = dest_env.cname, source_env.cname

    def compose_environments(
        self,
        application_name: Optional[str] = None,
        group_name: Optional[str] = None,
        version_labels: Optional[list[str]] = None,
    ) -> list[Environment]:
        # Returns matching environments (stub behavior)
        envs: list[Environment] = []
        if application_name and application_name in self.applications:
            app = self.applications[application_name]
            envs = list(app.environments.values())
        return envs

    # Platform Version operations

    def create_platform_version(
        self,
        platform_name: str,
        platform_version: str,
    ) -> PlatformVersion:
        pv = PlatformVersion(
            platform_name=platform_name,
            platform_version=platform_version,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.platform_versions[pv.platform_arn] = pv
        return pv

    def delete_platform_version(
        self,
        platform_arn: str,
    ) -> None:
        self.platform_versions.pop(platform_arn, None)

    # Environment Info operations

    def request_environment_info(
        self,
        environment_name: Optional[str] = None,
        environment_id: Optional[str] = None,
        info_type: str = "tail",
    ) -> None:
        key = environment_name or environment_id or ""
        self.environment_info[key] = [
            {
                "InfoType": info_type,
                "Ec2InstanceId": "i-mock12345",
                "SampleTimestamp": utcnow().isoformat(),
                "Message": f"Mock {info_type} log for {key}",
            }
        ]

    def retrieve_environment_info(
        self,
        environment_name: Optional[str] = None,
        environment_id: Optional[str] = None,
        info_type: str = "tail",
    ) -> list[dict[str, Any]]:
        key = environment_name or environment_id or ""
        return self.environment_info.get(key, [])

    def apply_environment_managed_action(
        self,
        environment_name: Optional[str] = None,
        environment_id: Optional[str] = None,
        action_id: Optional[str] = None,
    ) -> dict[str, str]:
        return {
            "ActionId": action_id or str(uuid.uuid4()),
            "ActionType": "Unknown",
            "ActionDescription": "Mock managed action",
            "Status": "Applied",
        }


eb_backends = BackendDict(EBBackend, "elasticbeanstalk")
