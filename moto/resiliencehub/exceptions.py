"""Exceptions raised by the resiliencehub service."""

from moto.core.exceptions import JsonRESTError


class ResourceNotFound(JsonRESTError):
    def __init__(self, msg: str):
        super().__init__("ResourceNotFoundException", msg)


class AppNotFound(ResourceNotFound):
    def __init__(self, arn: str):
        super().__init__(f"App not found for appArn {arn}")


class AppVersionNotFound(ResourceNotFound):
    def __init__(self) -> None:
        super().__init__("App Version not found")


class ResiliencyPolicyNotFound(ResourceNotFound):
    def __init__(self, arn: str):
        super().__init__(f"ResiliencyPolicy {arn} not found")


class AppAssessmentNotFound(ResourceNotFound):
    def __init__(self, arn: str):
        super().__init__(f"AppAssessment {arn} not found")


class AppComponentNotFound(ResourceNotFound):
    def __init__(self, component_id: str):
        super().__init__(f"AppComponent {component_id} not found")


class AppVersionResourceNotFound(ResourceNotFound):
    def __init__(self, resource_name: str):
        super().__init__(f"Resource {resource_name} not found")


class RecommendationTemplateNotFound(ResourceNotFound):
    def __init__(self, arn: str):
        super().__init__(f"RecommendationTemplate {arn} not found")


class ValidationException(JsonRESTError):
    def __init__(self, msg: str):
        super().__init__("ValidationException", msg)


class ConflictException(JsonRESTError):
    def __init__(self, msg: str):
        super().__init__("ConflictException", msg)
