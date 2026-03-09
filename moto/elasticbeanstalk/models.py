import weakref
from typing import Optional

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


eb_backends = BackendDict(EBBackend, "elasticbeanstalk")
