"""Exceptions raised by the appconfig service."""

from moto.core.exceptions import JsonRESTError


class AppNotFoundException(JsonRESTError):
    def __init__(self) -> None:
        super().__init__("ResourceNotFoundException", "Application not found")


class ConfigurationProfileNotFound(JsonRESTError):
    def __init__(self) -> None:
        super().__init__("ResourceNotFoundException", "ConfigurationProfile not found")


class ConfigurationVersionNotFound(JsonRESTError):
    def __init__(self) -> None:
        super().__init__(
            "ResourceNotFoundException", "HostedConfigurationVersion not found"
        )


class DeploymentStrategyNotFound(JsonRESTError):
    def __init__(self) -> None:
        super().__init__(
            "ResourceNotFoundException", "DeploymentStrategy not found"
        )


class EnvironmentNotFound(JsonRESTError):
    def __init__(self) -> None:
        super().__init__(
            "ResourceNotFoundException", "Environment not found"
        )


class ExtensionNotFound(JsonRESTError):
    def __init__(self) -> None:
        super().__init__(
            "ResourceNotFoundException", "Extension not found"
        )


class ExtensionAssociationNotFound(JsonRESTError):
    def __init__(self) -> None:
        super().__init__(
            "ResourceNotFoundException", "ExtensionAssociation not found"
        )


class DeploymentNotFound(JsonRESTError):
    def __init__(self) -> None:
        super().__init__(
            "ResourceNotFoundException", "Deployment not found"
        )
