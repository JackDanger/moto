import json
from typing import Any
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import AppConfigBackend, appconfig_backends


class AppConfigResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="appconfig")

    @property
    def appconfig_backend(self) -> AppConfigBackend:
        return appconfig_backends[self.current_account][self.region]

    # --- Applications ---

    def create_application(self) -> str:
        name = self._get_param("Name")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        app = self.appconfig_backend.create_application(
            name=name,
            description=description,
            tags=tags,
        )
        return json.dumps(app.to_json())

    def delete_application(self) -> str:
        app_id = self._get_param("ApplicationId")
        self.appconfig_backend.delete_application(app_id)
        return "{}"

    def get_application(self) -> str:
        app_id = self._get_param("ApplicationId")
        app = self.appconfig_backend.get_application(app_id)
        return json.dumps(app.to_json())

    def update_application(self) -> str:
        app_id = self._get_param("ApplicationId")
        name = self._get_param("Name")
        description = self._get_param("Description")
        app = self.appconfig_backend.update_application(
            application_id=app_id,
            name=name,
            description=description,
        )
        return json.dumps(app.to_json())

    def list_applications(self) -> str:
        apps = self.appconfig_backend.list_applications()
        return json.dumps({"Items": [a.to_json() for a in apps]})

    # --- Configuration Profiles ---

    def create_configuration_profile(self) -> str:
        app_id = self._get_param("ApplicationId")
        name = self._get_param("Name")
        description = self._get_param("Description")
        location_uri = self._get_param("LocationUri")
        retrieval_role_arn = self._get_param("RetrievalRoleArn")
        validators = self._get_param("Validators")
        _type = self._get_param("Type")
        tags = self._get_param("Tags")
        config_profile = self.appconfig_backend.create_configuration_profile(
            application_id=app_id,
            name=name,
            description=description,
            location_uri=location_uri,
            retrieval_role_arn=retrieval_role_arn,
            validators=validators,
            _type=_type,
            tags=tags,
        )
        return json.dumps(config_profile.to_json())

    def delete_configuration_profile(self) -> str:
        app_id = self._get_param("ApplicationId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        self.appconfig_backend.delete_configuration_profile(app_id, config_profile_id)
        return "{}"

    def get_configuration_profile(self) -> str:
        app_id = self._get_param("ApplicationId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        config_profile = self.appconfig_backend.get_configuration_profile(
            app_id, config_profile_id
        )
        return json.dumps(config_profile.to_json())

    def update_configuration_profile(self) -> str:
        app_id = self._get_param("ApplicationId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        name = self._get_param("Name")
        description = self._get_param("Description")
        retrieval_role_arn = self._get_param("RetrievalRoleArn")
        validators = self._get_param("Validators")
        config_profile = self.appconfig_backend.update_configuration_profile(
            application_id=app_id,
            config_profile_id=config_profile_id,
            name=name,
            description=description,
            retrieval_role_arn=retrieval_role_arn,
            validators=validators,
        )
        return json.dumps(config_profile.to_json())

    def list_configuration_profiles(self) -> str:
        app_id = self._get_param("ApplicationId")
        profiles = self.appconfig_backend.list_configuration_profiles(app_id)
        return json.dumps({"Items": [p.to_json() for p in profiles]})

    # --- Hosted Configuration Versions ---

    def create_hosted_configuration_version(self) -> tuple[str, dict[str, Any]]:
        app_id = self._get_param("ApplicationId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        description = self.headers.get("Description")
        content = self.body
        content_type = self.headers.get("Content-Type")
        version_label = self.headers.get("VersionLabel")
        version = self.appconfig_backend.create_hosted_configuration_version(
            app_id=app_id,
            config_profile_id=config_profile_id,
            description=description,
            content=content,
            content_type=content_type,
            version_label=version_label,
        )
        return version.content, version.get_headers()

    def get_hosted_configuration_version(self) -> tuple[str, dict[str, Any]]:
        app_id = self._get_param("ApplicationId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        version_number = self._get_int_param("VersionNumber")
        version = self.appconfig_backend.get_hosted_configuration_version(
            app_id=app_id,
            config_profile_id=config_profile_id,
            version=version_number,
        )
        return version.content, version.get_headers()

    def delete_hosted_configuration_version(self) -> str:
        app_id = self._get_param("ApplicationId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        version_number = self._get_int_param("VersionNumber")
        self.appconfig_backend.delete_hosted_configuration_version(
            app_id=app_id,
            config_profile_id=config_profile_id,
            version=version_number,
        )
        return "{}"

    def list_hosted_configuration_versions(self) -> str:
        app_id = self._get_param("ApplicationId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        versions = self.appconfig_backend.list_hosted_configuration_versions(
            app_id=app_id,
            config_profile_id=config_profile_id,
        )
        return json.dumps({"Items": [v.to_json() for v in versions]})

    # --- Environments ---

    def create_environment(self) -> str:
        app_id = self._get_param("ApplicationId")
        name = self._get_param("Name")
        description = self._get_param("Description")
        monitors = self._get_param("Monitors")
        tags = self._get_param("Tags")
        env = self.appconfig_backend.create_environment(
            application_id=app_id,
            name=name,
            description=description,
            monitors=monitors,
            tags=tags,
        )
        return json.dumps(env.to_json())

    def get_environment(self) -> str:
        app_id = self._get_param("ApplicationId")
        env_id = self._get_param("EnvironmentId")
        env = self.appconfig_backend.get_environment(app_id, env_id)
        return json.dumps(env.to_json())

    def update_environment(self) -> str:
        app_id = self._get_param("ApplicationId")
        env_id = self._get_param("EnvironmentId")
        name = self._get_param("Name")
        description = self._get_param("Description")
        monitors = self._get_param("Monitors")
        env = self.appconfig_backend.update_environment(
            application_id=app_id,
            environment_id=env_id,
            name=name,
            description=description,
            monitors=monitors,
        )
        return json.dumps(env.to_json())

    def delete_environment(self) -> str:
        app_id = self._get_param("ApplicationId")
        env_id = self._get_param("EnvironmentId")
        self.appconfig_backend.delete_environment(app_id, env_id)
        return "{}"

    def list_environments(self) -> str:
        app_id = self._get_param("ApplicationId")
        envs = self.appconfig_backend.list_environments(app_id)
        return json.dumps({"Items": [e.to_json() for e in envs]})

    # --- Deployment Strategies ---

    def create_deployment_strategy(self) -> str:
        name = self._get_param("Name")
        description = self._get_param("Description")
        deployment_duration = self._get_param("DeploymentDurationInMinutes")
        final_bake_time = self._get_param("FinalBakeTimeInMinutes")
        growth_factor = self._get_param("GrowthFactor")
        growth_type = self._get_param("GrowthType")
        replicate_to = self._get_param("ReplicateTo")
        tags = self._get_param("Tags")
        strategy = self.appconfig_backend.create_deployment_strategy(
            name=name,
            description=description,
            deployment_duration_in_minutes=deployment_duration,
            final_bake_time_in_minutes=final_bake_time,
            growth_factor=growth_factor,
            growth_type=growth_type,
            replicate_to=replicate_to,
            tags=tags,
        )
        return json.dumps(strategy.to_json())

    def get_deployment_strategy(self) -> str:
        strategy_id = self._get_param("DeploymentStrategyId")
        strategy = self.appconfig_backend.get_deployment_strategy(strategy_id)
        return json.dumps(strategy.to_json())

    def update_deployment_strategy(self) -> str:
        strategy_id = self._get_param("DeploymentStrategyId")
        description = self._get_param("Description")
        deployment_duration = self._get_param("DeploymentDurationInMinutes")
        final_bake_time = self._get_param("FinalBakeTimeInMinutes")
        growth_factor = self._get_param("GrowthFactor")
        growth_type = self._get_param("GrowthType")
        strategy = self.appconfig_backend.update_deployment_strategy(
            strategy_id=strategy_id,
            description=description,
            deployment_duration_in_minutes=deployment_duration,
            final_bake_time_in_minutes=final_bake_time,
            growth_factor=growth_factor,
            growth_type=growth_type,
        )
        return json.dumps(strategy.to_json())

    def delete_deployment_strategy(self) -> str:
        strategy_id = self._get_param("DeploymentStrategyId")
        self.appconfig_backend.delete_deployment_strategy(strategy_id)
        return "{}"

    def list_deployment_strategies(self) -> str:
        strategies = self.appconfig_backend.list_deployment_strategies()
        return json.dumps({"Items": [s.to_json() for s in strategies]})

    # --- Deployments ---

    def start_deployment(self) -> str:
        app_id = self._get_param("ApplicationId")
        env_id = self._get_param("EnvironmentId")
        strategy_id = self._get_param("DeploymentStrategyId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        config_version = self._get_param("ConfigurationVersion")
        description = self._get_param("Description")
        kms_key_identifier = self._get_param("KmsKeyIdentifier")
        tags = self._get_param("Tags")
        deployment = self.appconfig_backend.start_deployment(
            application_id=app_id,
            environment_id=env_id,
            deployment_strategy_id=strategy_id,
            configuration_profile_id=config_profile_id,
            configuration_version=config_version,
            description=description,
            kms_key_identifier=kms_key_identifier,
            tags=tags,
        )
        return json.dumps(deployment.to_json())

    def get_deployment(self) -> str:
        app_id = self._get_param("ApplicationId")
        env_id = self._get_param("EnvironmentId")
        deployment_number = self._get_int_param("DeploymentNumber")
        deployment = self.appconfig_backend.get_deployment(
            app_id, env_id, deployment_number
        )
        return json.dumps(deployment.to_json())

    def stop_deployment(self) -> str:
        app_id = self._get_param("ApplicationId")
        env_id = self._get_param("EnvironmentId")
        deployment_number = self._get_int_param("DeploymentNumber")
        deployment = self.appconfig_backend.stop_deployment(
            app_id, env_id, deployment_number
        )
        return json.dumps(deployment.to_json())

    def list_deployments(self) -> str:
        app_id = self._get_param("ApplicationId")
        env_id = self._get_param("EnvironmentId")
        deployments = self.appconfig_backend.list_deployments(app_id, env_id)
        return json.dumps({"Items": [d.to_summary() for d in deployments]})

    # --- Extensions ---

    def create_extension(self) -> str:
        name = self._get_param("Name")
        description = self._get_param("Description")
        actions = self._get_param("Actions")
        parameters = self._get_param("Parameters")
        tags = self._get_param("Tags")
        ext = self.appconfig_backend.create_extension(
            name=name,
            description=description,
            actions=actions,
            parameters=parameters,
            tags=tags,
        )
        return json.dumps(ext.to_json())

    def get_extension(self) -> str:
        ext_id = self._get_param("ExtensionIdentifier")
        ext = self.appconfig_backend.get_extension(ext_id)
        return json.dumps(ext.to_json())

    def update_extension(self) -> str:
        ext_id = self._get_param("ExtensionIdentifier")
        description = self._get_param("Description")
        actions = self._get_param("Actions")
        parameters = self._get_param("Parameters")
        ext = self.appconfig_backend.update_extension(
            ext_id=ext_id,
            description=description,
            actions=actions,
            parameters=parameters,
        )
        return json.dumps(ext.to_json())

    def delete_extension(self) -> str:
        ext_id = self._get_param("ExtensionIdentifier")
        self.appconfig_backend.delete_extension(ext_id)
        return "{}"

    def list_extensions(self) -> str:
        extensions = self.appconfig_backend.list_extensions()
        return json.dumps({"Items": [e.to_json() for e in extensions]})

    # --- Extension Associations ---

    def create_extension_association(self) -> str:
        ext_id = self._get_param("ExtensionIdentifier")
        ext_version = self._get_param("ExtensionVersionNumber")
        resource_id = self._get_param("ResourceIdentifier")
        parameters = self._get_param("Parameters")
        tags = self._get_param("Tags")
        assoc = self.appconfig_backend.create_extension_association(
            extension_identifier=ext_id,
            extension_version_number=ext_version,
            resource_identifier=resource_id,
            parameters=parameters,
            tags=tags,
        )
        return json.dumps(assoc.to_json())

    def get_extension_association(self) -> str:
        assoc_id = self._get_param("ExtensionAssociationId")
        assoc = self.appconfig_backend.get_extension_association(assoc_id)
        return json.dumps(assoc.to_json())

    def update_extension_association(self) -> str:
        assoc_id = self._get_param("ExtensionAssociationId")
        parameters = self._get_param("Parameters")
        assoc = self.appconfig_backend.update_extension_association(
            assoc_id=assoc_id,
            parameters=parameters,
        )
        return json.dumps(assoc.to_json())

    def delete_extension_association(self) -> str:
        assoc_id = self._get_param("ExtensionAssociationId")
        self.appconfig_backend.delete_extension_association(assoc_id)
        return "{}"

    def list_extension_associations(self) -> str:
        assocs = self.appconfig_backend.list_extension_associations()
        return json.dumps({"Items": [a.to_json() for a in assocs]})

    # --- Configuration (deprecated) ---

    def get_configuration(self) -> tuple[str, dict[str, Any]]:
        app_id = self._get_param("Application")
        env_id = self._get_param("Environment")
        config_id = self._get_param("Configuration")
        content, content_type = self.appconfig_backend.get_configuration(
            app_id, env_id, config_id
        )
        headers = {
            "Content-Type": content_type,
            "Configuration-Version": "1",
        }
        return content, headers

    # --- Account Settings ---

    def get_account_settings(self) -> str:
        result = self.appconfig_backend.get_account_settings()
        return json.dumps(result)

    def update_account_settings(self) -> str:
        deletion_protection = self._get_param("DeletionProtection")
        result = self.appconfig_backend.update_account_settings(deletion_protection)
        return json.dumps(result)

    # --- Validate Configuration ---

    def validate_configuration(self) -> str:
        app_id = self._get_param("ApplicationId")
        config_profile_id = self._get_param("ConfigurationProfileId")
        config_version = self._get_param("ConfigurationVersion")
        self.appconfig_backend.validate_configuration(
            app_id, config_profile_id, config_version
        )
        return "{}"

    # --- Tags ---

    def list_tags_for_resource(self) -> str:
        arn = unquote(self.path.split("/tags/")[-1])
        tags = self.appconfig_backend.list_tags_for_resource(arn)
        return json.dumps({"Tags": tags})

    def tag_resource(self) -> str:
        arn = unquote(self.path.split("/tags/")[-1])
        tags = self._get_param("Tags")
        self.appconfig_backend.tag_resource(arn, tags)
        return "{}"

    def untag_resource(self) -> str:
        arn = unquote(self.path.split("/tags/")[-1])
        tag_keys = self.querystring.get("tagKeys")
        self.appconfig_backend.untag_resource(arn, tag_keys)  # type: ignore[arg-type]
        return "{}"
