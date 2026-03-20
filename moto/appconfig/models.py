from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_with_milliseconds
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    AppNotFoundException,
    ConfigurationProfileNotFound,
    ConfigurationVersionNotFound,
    DeploymentNotFound,
    DeploymentStrategyNotFound,
    EnvironmentNotFound,
    ExtensionAssociationNotFound,
    ExtensionNotFound,
)


class HostedConfigurationVersion(BaseModel):
    def __init__(
        self,
        app_id: str,
        config_id: str,
        version: int,
        description: str,
        content: str,
        content_type: str,
        version_label: str,
    ):
        self.app_id = app_id
        self.config_id = config_id
        self.version = version
        self.description = description
        self.content = content
        self.content_type = content_type
        self.version_label = version_label

    def get_headers(self) -> dict[str, Any]:
        headers: dict[str, Any] = {
            "application-id": self.app_id,
            "configuration-profile-id": self.config_id,
            "version-number": str(self.version),
            "content-type": self.content_type,
        }
        if self.description is not None:
            headers["description"] = self.description
        if self.version_label is not None:
            headers["VersionLabel"] = self.version_label
        return headers

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ApplicationId": self.app_id,
            "ConfigurationProfileId": self.config_id,
            "VersionNumber": self.version,
            "ContentType": self.content_type,
        }
        if self.description is not None:
            result["Description"] = self.description
        if self.version_label is not None:
            result["VersionLabel"] = self.version_label
        return result


class ConfigurationProfile(BaseModel):
    def __init__(
        self,
        application_id: str,
        name: str,
        region: str,
        account_id: str,
        description: str,
        location_uri: str,
        retrieval_role_arn: str,
        validators: list[dict[str, str]],
        _type: str,
    ):
        self.id = mock_random.get_random_hex(7)
        self.arn = f"arn:{get_partition(region)}:appconfig:{region}:{account_id}:application/{application_id}/configurationprofile/{self.id}"
        self.application_id = application_id
        self.name = name
        self.description = description
        self.location_uri = location_uri
        self.retrieval_role_arn = retrieval_role_arn
        self.validators = validators
        self._type = _type
        self.config_versions: dict[int, HostedConfigurationVersion] = {}

    def create_version(
        self,
        app_id: str,
        config_id: str,
        description: str,
        content: str,
        content_type: str,
        version_label: str,
    ) -> HostedConfigurationVersion:
        if self.config_versions:
            version = sorted(self.config_versions.keys())[-1] + 1
        else:
            version = 1
        self.config_versions[version] = HostedConfigurationVersion(
            app_id=app_id,
            config_id=config_id,
            version=version,
            description=description,
            content=content,
            content_type=content_type,
            version_label=version_label,
        )
        return self.config_versions[version]

    def get_version(self, version: int) -> HostedConfigurationVersion:
        if version not in self.config_versions:
            raise ConfigurationVersionNotFound
        return self.config_versions[version]

    def delete_version(self, version: int) -> None:
        self.config_versions.pop(version)

    def to_json(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "Name": self.name,
            "ApplicationId": self.application_id,
            "Description": self.description,
            "LocationUri": self.location_uri,
            "RetrievalRoleArn": self.retrieval_role_arn,
            "Validators": self.validators,
            "Type": self._type,
        }


class Environment(BaseModel):
    def __init__(
        self,
        application_id: str,
        name: str,
        description: Optional[str],
        monitors: Optional[list[dict[str, str]]],
        region: str,
        account_id: str,
    ):
        self.id = mock_random.get_random_hex(7)
        self.arn = f"arn:{get_partition(region)}:appconfig:{region}:{account_id}:application/{application_id}/environment/{self.id}"
        self.application_id = application_id
        self.name = name
        self.description = description
        self.monitors = monitors or []
        self.state = "READY_FOR_DEPLOYMENT"
        self.deployments: dict[int, Deployment] = {}

    def to_json(self) -> dict[str, Any]:
        return {
            "ApplicationId": self.application_id,
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
            "State": self.state,
            "Monitors": self.monitors,
        }


class DeploymentStrategy(BaseModel):
    def __init__(
        self,
        name: str,
        description: Optional[str],
        deployment_duration_in_minutes: int,
        final_bake_time_in_minutes: int,
        growth_factor: float,
        growth_type: Optional[str],
        replicate_to: Optional[str],
        region: str,
        account_id: str,
    ):
        self.id = mock_random.get_random_hex(7)
        self.arn = f"arn:{get_partition(region)}:appconfig:{region}:{account_id}:deploymentstrategy/{self.id}"
        self.name = name
        self.description = description
        self.deployment_duration_in_minutes = deployment_duration_in_minutes
        self.final_bake_time_in_minutes = final_bake_time_in_minutes or 0
        self.growth_factor = growth_factor
        self.growth_type = growth_type or "LINEAR"
        self.replicate_to = replicate_to or "NONE"

    def to_json(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
            "DeploymentDurationInMinutes": self.deployment_duration_in_minutes,
            "GrowthType": self.growth_type,
            "GrowthFactor": self.growth_factor,
            "FinalBakeTimeInMinutes": self.final_bake_time_in_minutes,
            "ReplicateTo": self.replicate_to,
        }


class Deployment(BaseModel):
    def __init__(
        self,
        application_id: str,
        environment_id: str,
        deployment_strategy_id: str,
        configuration_profile_id: str,
        configuration_version: str,
        description: Optional[str],
        kms_key_identifier: Optional[str],
        deployment_number: int,
        strategy: DeploymentStrategy,
        config_profile: ConfigurationProfile,
    ):
        self.application_id = application_id
        self.environment_id = environment_id
        self.deployment_strategy_id = deployment_strategy_id
        self.configuration_profile_id = configuration_profile_id
        self.configuration_version = configuration_version
        self.description = description
        self.kms_key_identifier = kms_key_identifier
        self.kms_key_arn = kms_key_identifier
        self.deployment_number = deployment_number
        self.configuration_name = config_profile.name
        self.configuration_location_uri = config_profile.location_uri
        self.deployment_duration_in_minutes = strategy.deployment_duration_in_minutes
        self.growth_type = strategy.growth_type
        self.growth_factor = strategy.growth_factor
        self.final_bake_time_in_minutes = strategy.final_bake_time_in_minutes
        self.state = "COMPLETE"
        self.percentage_complete = 100.0
        now = datetime.now(timezone.utc)
        self.started_at = iso_8601_datetime_with_milliseconds(now)
        self.completed_at = iso_8601_datetime_with_milliseconds(now)
        self.event_log: list[dict[str, Any]] = []
        self.applied_extensions: list[dict[str, Any]] = []
        self.version_label: Optional[str] = None

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ApplicationId": self.application_id,
            "EnvironmentId": self.environment_id,
            "DeploymentStrategyId": self.deployment_strategy_id,
            "ConfigurationProfileId": self.configuration_profile_id,
            "DeploymentNumber": self.deployment_number,
            "ConfigurationName": self.configuration_name,
            "ConfigurationLocationUri": self.configuration_location_uri,
            "ConfigurationVersion": self.configuration_version,
            "Description": self.description,
            "DeploymentDurationInMinutes": self.deployment_duration_in_minutes,
            "GrowthType": self.growth_type,
            "GrowthFactor": self.growth_factor,
            "FinalBakeTimeInMinutes": self.final_bake_time_in_minutes,
            "State": self.state,
            "EventLog": self.event_log,
            "PercentageComplete": self.percentage_complete,
            "StartedAt": self.started_at,
            "CompletedAt": self.completed_at,
            "AppliedExtensions": self.applied_extensions,
            "KmsKeyArn": self.kms_key_arn,
            "KmsKeyIdentifier": self.kms_key_identifier,
            "VersionLabel": self.version_label,
        }
        return result

    def to_summary(self) -> dict[str, Any]:
        return {
            "DeploymentNumber": self.deployment_number,
            "ConfigurationName": self.configuration_name,
            "ConfigurationVersion": self.configuration_version,
            "DeploymentDurationInMinutes": self.deployment_duration_in_minutes,
            "GrowthType": self.growth_type,
            "GrowthFactor": self.growth_factor,
            "FinalBakeTimeInMinutes": self.final_bake_time_in_minutes,
            "State": self.state,
            "PercentageComplete": self.percentage_complete,
            "StartedAt": self.started_at,
            "CompletedAt": self.completed_at,
            "VersionLabel": self.version_label,
        }


class Extension(BaseModel):
    def __init__(
        self,
        name: str,
        description: Optional[str],
        actions: Optional[dict[str, Any]],
        parameters: Optional[dict[str, Any]],
        region: str,
        account_id: str,
    ):
        self.id = mock_random.get_random_hex(7)
        self.arn = f"arn:{get_partition(region)}:appconfig:{region}:{account_id}:extension/{self.id}"
        self.name = name
        self.description = description
        self.actions = actions or {}
        self.parameters = parameters or {}
        self.version_number = 1

    def to_json(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "Name": self.name,
            "VersionNumber": self.version_number,
            "Arn": self.arn,
            "Description": self.description,
            "Actions": self.actions,
            "Parameters": self.parameters,
        }


class ExtensionAssociation(BaseModel):
    def __init__(
        self,
        extension_identifier: str,
        extension_version_number: Optional[int],
        resource_identifier: str,
        parameters: Optional[dict[str, str]],
        extension_arn: str,
        region: str,
        account_id: str,
    ):
        self.id = mock_random.get_random_hex(7)
        self.arn = f"arn:{get_partition(region)}:appconfig:{region}:{account_id}:extensionassociation/{self.id}"
        self.extension_arn = extension_arn
        self.resource_arn = resource_identifier
        self.parameters = parameters or {}
        self.extension_version_number = extension_version_number or 1

    def to_json(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "ExtensionArn": self.extension_arn,
            "ResourceArn": self.resource_arn,
            "Arn": self.arn,
            "Parameters": self.parameters,
            "ExtensionVersionNumber": self.extension_version_number,
        }


class Application(BaseModel):
    def __init__(
        self, name: str, description: Optional[str], region: str, account_id: str
    ):
        self.id = mock_random.get_random_hex(7)
        self.arn = f"arn:{get_partition(region)}:appconfig:{region}:{account_id}:application/{self.id}"
        self.name = name
        self.description = description

        self.config_profiles: dict[str, ConfigurationProfile] = {}
        self.environments: dict[str, Environment] = {}

    def to_json(self) -> dict[str, Any]:
        return {
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
        }


class AppConfigBackend(BaseBackend):
    """Implementation of AppConfig APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.applications: dict[str, Application] = {}
        self.deployment_strategies: dict[str, DeploymentStrategy] = {}
        self.extensions: dict[str, Extension] = {}
        self.extension_associations: dict[str, ExtensionAssociation] = {}
        self.tagger = TaggingService()
        self.deletion_protection: Optional[dict[str, Any]] = None

    # --- Applications ---

    def create_application(
        self, name: str, description: Optional[str], tags: dict[str, str]
    ) -> Application:
        app = Application(
            name, description, region=self.region_name, account_id=self.account_id
        )
        self.applications[app.id] = app
        self.tag_resource(app.arn, tags)
        return app

    def delete_application(self, app_id: str) -> None:
        self.applications.pop(app_id, None)

    def get_application(self, app_id: str) -> Application:
        if app_id not in self.applications:
            raise AppNotFoundException
        return self.applications[app_id]

    def update_application(
        self, application_id: str, name: str, description: str
    ) -> Application:
        app = self.get_application(application_id)
        if name is not None:
            app.name = name
        if description is not None:
            app.description = description
        return app

    def list_applications(self) -> Iterable[Application]:
        return self.applications.values()

    # --- Configuration Profiles ---

    def create_configuration_profile(
        self,
        application_id: str,
        name: str,
        description: str,
        location_uri: str,
        retrieval_role_arn: str,
        validators: list[dict[str, str]],
        _type: str,
        tags: dict[str, str],
    ) -> ConfigurationProfile:
        config_profile = ConfigurationProfile(
            application_id=application_id,
            name=name,
            region=self.region_name,
            account_id=self.account_id,
            description=description,
            location_uri=location_uri,
            retrieval_role_arn=retrieval_role_arn,
            validators=validators,
            _type=_type,
        )
        self.tag_resource(config_profile.arn, tags)
        self.get_application(application_id).config_profiles[config_profile.id] = (
            config_profile
        )
        return config_profile

    def delete_configuration_profile(self, app_id: str, config_profile_id: str) -> None:
        self.get_application(app_id).config_profiles.pop(config_profile_id)

    def get_configuration_profile(
        self, app_id: str, config_profile_id: str
    ) -> ConfigurationProfile:
        app = self.get_application(app_id)
        if config_profile_id not in app.config_profiles:
            raise ConfigurationProfileNotFound
        return app.config_profiles[config_profile_id]

    def update_configuration_profile(
        self,
        application_id: str,
        config_profile_id: str,
        name: str,
        description: str,
        retrieval_role_arn: str,
        validators: list[dict[str, str]],
    ) -> ConfigurationProfile:
        config_profile = self.get_configuration_profile(
            application_id, config_profile_id
        )
        if name is not None:
            config_profile.name = name
        if description is not None:
            config_profile.description = description
        if retrieval_role_arn is not None:
            config_profile.retrieval_role_arn = retrieval_role_arn
        if validators is not None:
            config_profile.validators = validators
        return config_profile

    def list_configuration_profiles(
        self, app_id: str
    ) -> Iterable[ConfigurationProfile]:
        app = self.get_application(app_id)
        return app.config_profiles.values()

    # --- Hosted Configuration Versions ---

    def create_hosted_configuration_version(
        self,
        app_id: str,
        config_profile_id: str,
        description: str,
        content: str,
        content_type: str,
        version_label: str,
    ) -> HostedConfigurationVersion:
        """
        The LatestVersionNumber-parameter is not yet implemented
        """
        profile = self.get_configuration_profile(app_id, config_profile_id)
        return profile.create_version(
            app_id=app_id,
            config_id=config_profile_id,
            description=description,
            content=content,
            content_type=content_type,
            version_label=version_label,
        )

    def get_hosted_configuration_version(
        self, app_id: str, config_profile_id: str, version: int
    ) -> HostedConfigurationVersion:
        profile = self.get_configuration_profile(
            app_id=app_id, config_profile_id=config_profile_id
        )
        return profile.get_version(version)

    def delete_hosted_configuration_version(
        self, app_id: str, config_profile_id: str, version: int
    ) -> None:
        profile = self.get_configuration_profile(
            app_id=app_id, config_profile_id=config_profile_id
        )
        profile.delete_version(version=version)

    def list_hosted_configuration_versions(
        self, app_id: str, config_profile_id: str
    ) -> list[HostedConfigurationVersion]:
        profile = self.get_configuration_profile(app_id, config_profile_id)
        return list(profile.config_versions.values())

    # --- Environments ---

    def create_environment(
        self,
        application_id: str,
        name: str,
        description: Optional[str],
        monitors: Optional[list[dict[str, str]]],
        tags: Optional[dict[str, str]],
    ) -> Environment:
        app = self.get_application(application_id)
        env = Environment(
            application_id=application_id,
            name=name,
            description=description,
            monitors=monitors,
            region=self.region_name,
            account_id=self.account_id,
        )
        app.environments[env.id] = env
        if tags:
            self.tag_resource(env.arn, tags)
        return env

    def get_environment(self, app_id: str, env_id: str) -> Environment:
        app = self.get_application(app_id)
        if env_id not in app.environments:
            raise EnvironmentNotFound
        return app.environments[env_id]

    def update_environment(
        self,
        application_id: str,
        environment_id: str,
        name: Optional[str],
        description: Optional[str],
        monitors: Optional[list[dict[str, str]]],
    ) -> Environment:
        env = self.get_environment(application_id, environment_id)
        if name is not None:
            env.name = name
        if description is not None:
            env.description = description
        if monitors is not None:
            env.monitors = monitors
        return env

    def delete_environment(self, app_id: str, env_id: str) -> None:
        app = self.get_application(app_id)
        app.environments.pop(env_id, None)

    def list_environments(self, app_id: str) -> Iterable[Environment]:
        app = self.get_application(app_id)
        return app.environments.values()

    # --- Deployment Strategies ---

    def create_deployment_strategy(
        self,
        name: str,
        description: Optional[str],
        deployment_duration_in_minutes: int,
        final_bake_time_in_minutes: int,
        growth_factor: float,
        growth_type: Optional[str],
        replicate_to: Optional[str],
        tags: Optional[dict[str, str]],
    ) -> DeploymentStrategy:
        strategy = DeploymentStrategy(
            name=name,
            description=description,
            deployment_duration_in_minutes=deployment_duration_in_minutes,
            final_bake_time_in_minutes=final_bake_time_in_minutes,
            growth_factor=growth_factor,
            growth_type=growth_type,
            replicate_to=replicate_to,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.deployment_strategies[strategy.id] = strategy
        if tags:
            self.tag_resource(strategy.arn, tags)
        return strategy

    def get_deployment_strategy(self, strategy_id: str) -> DeploymentStrategy:
        if strategy_id not in self.deployment_strategies:
            raise DeploymentStrategyNotFound
        return self.deployment_strategies[strategy_id]

    def update_deployment_strategy(
        self,
        strategy_id: str,
        description: Optional[str],
        deployment_duration_in_minutes: Optional[int],
        final_bake_time_in_minutes: Optional[int],
        growth_factor: Optional[float],
        growth_type: Optional[str],
    ) -> DeploymentStrategy:
        strategy = self.get_deployment_strategy(strategy_id)
        if description is not None:
            strategy.description = description
        if deployment_duration_in_minutes is not None:
            strategy.deployment_duration_in_minutes = deployment_duration_in_minutes
        if final_bake_time_in_minutes is not None:
            strategy.final_bake_time_in_minutes = final_bake_time_in_minutes
        if growth_factor is not None:
            strategy.growth_factor = growth_factor
        if growth_type is not None:
            strategy.growth_type = growth_type
        return strategy

    def delete_deployment_strategy(self, strategy_id: str) -> None:
        self.deployment_strategies.pop(strategy_id, None)

    def list_deployment_strategies(self) -> Iterable[DeploymentStrategy]:
        return self.deployment_strategies.values()

    # --- Deployments ---

    def start_deployment(
        self,
        application_id: str,
        environment_id: str,
        deployment_strategy_id: str,
        configuration_profile_id: str,
        configuration_version: str,
        description: Optional[str],
        kms_key_identifier: Optional[str],
        tags: Optional[dict[str, str]],
    ) -> Deployment:
        env = self.get_environment(application_id, environment_id)
        strategy = self.get_deployment_strategy(deployment_strategy_id)
        config_profile = self.get_configuration_profile(
            application_id, configuration_profile_id
        )
        deployment_number = len(env.deployments) + 1
        deployment = Deployment(
            application_id=application_id,
            environment_id=environment_id,
            deployment_strategy_id=deployment_strategy_id,
            configuration_profile_id=configuration_profile_id,
            configuration_version=configuration_version,
            description=description,
            kms_key_identifier=kms_key_identifier,
            deployment_number=deployment_number,
            strategy=strategy,
            config_profile=config_profile,
        )
        env.deployments[deployment_number] = deployment
        return deployment

    def get_deployment(
        self, app_id: str, env_id: str, deployment_number: int
    ) -> Deployment:
        env = self.get_environment(app_id, env_id)
        if deployment_number not in env.deployments:
            raise DeploymentNotFound
        return env.deployments[deployment_number]

    def stop_deployment(
        self, app_id: str, env_id: str, deployment_number: int
    ) -> Deployment:
        deployment = self.get_deployment(app_id, env_id, deployment_number)
        deployment.state = "ROLLED_BACK"
        return deployment

    def list_deployments(
        self, app_id: str, env_id: str
    ) -> list[Deployment]:
        env = self.get_environment(app_id, env_id)
        return list(env.deployments.values())

    # --- Extensions ---

    def create_extension(
        self,
        name: str,
        description: Optional[str],
        actions: Optional[dict[str, Any]],
        parameters: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> Extension:
        ext = Extension(
            name=name,
            description=description,
            actions=actions,
            parameters=parameters,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.extensions[ext.id] = ext
        if tags:
            self.tag_resource(ext.arn, tags)
        return ext

    def get_extension(self, ext_id: str) -> Extension:
        if ext_id not in self.extensions:
            raise ExtensionNotFound
        return self.extensions[ext_id]

    def update_extension(
        self,
        ext_id: str,
        description: Optional[str],
        actions: Optional[dict[str, Any]],
        parameters: Optional[dict[str, Any]],
    ) -> Extension:
        ext = self.get_extension(ext_id)
        if description is not None:
            ext.description = description
        if actions is not None:
            ext.actions = actions
        if parameters is not None:
            ext.parameters = parameters
        ext.version_number += 1
        return ext

    def delete_extension(self, ext_id: str) -> None:
        self.extensions.pop(ext_id, None)

    def list_extensions(self) -> Iterable[Extension]:
        return self.extensions.values()

    # --- Extension Associations ---

    def create_extension_association(
        self,
        extension_identifier: str,
        extension_version_number: Optional[int],
        resource_identifier: str,
        parameters: Optional[dict[str, str]],
        tags: Optional[dict[str, str]],
    ) -> ExtensionAssociation:
        ext = self.get_extension(extension_identifier)
        assoc = ExtensionAssociation(
            extension_identifier=extension_identifier,
            extension_version_number=extension_version_number,
            resource_identifier=resource_identifier,
            parameters=parameters,
            extension_arn=ext.arn,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.extension_associations[assoc.id] = assoc
        if tags:
            self.tag_resource(assoc.arn, tags)
        return assoc

    def get_extension_association(self, assoc_id: str) -> ExtensionAssociation:
        if assoc_id not in self.extension_associations:
            raise ExtensionAssociationNotFound
        return self.extension_associations[assoc_id]

    def update_extension_association(
        self, assoc_id: str, parameters: Optional[dict[str, str]]
    ) -> ExtensionAssociation:
        assoc = self.get_extension_association(assoc_id)
        if parameters is not None:
            assoc.parameters = parameters
        return assoc

    def delete_extension_association(self, assoc_id: str) -> None:
        self.extension_associations.pop(assoc_id, None)

    def list_extension_associations(self) -> Iterable[ExtensionAssociation]:
        return self.extension_associations.values()

    # --- Configuration (deprecated but still in API) ---

    def get_configuration(
        self, app_id: str, env_id: str, config_profile_id: str
    ) -> tuple[str, str]:
        """Return content and content_type for the latest hosted config version."""
        profile = self.get_configuration_profile(app_id, config_profile_id)
        if profile.config_versions:
            latest = sorted(profile.config_versions.keys())[-1]
            version = profile.config_versions[latest]
            return version.content, version.content_type
        return "", "application/octet-stream"

    # --- Account Settings ---

    def get_account_settings(self) -> dict[str, Any]:
        return {"DeletionProtection": self.deletion_protection}

    def update_account_settings(
        self, deletion_protection: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        if deletion_protection is not None:
            self.deletion_protection = deletion_protection
        return {"DeletionProtection": self.deletion_protection}

    # --- Validate Configuration ---

    def validate_configuration(
        self, app_id: str, config_profile_id: str, configuration_version: str
    ) -> None:
        # Just validate that the app and profile exist
        self.get_configuration_profile(app_id, config_profile_id)

    # --- Tags ---

    def list_tags_for_resource(self, arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(arn)

    def tag_resource(self, arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(arn, TaggingService.convert_dict_to_tags_input(tags))

    def untag_resource(self, arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(arn, tag_keys)


appconfig_backends = BackendDict(AppConfigBackend, "appconfig")
