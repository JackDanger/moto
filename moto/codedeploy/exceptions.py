"""Exceptions raised by the codedeploy service."""

from moto.core.exceptions import JsonRESTError


class CodeDeployException(JsonRESTError):
    pass


class ApplicationDoesNotExistException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("ApplicationDoesNotExistException", message)


class DeploymentDoesNotExistException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("DeploymentDoesNotExistException", message)


class ApplicationAlreadyExistsException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("ApplicationAlreadyExistsException", message)


class ApplicationNameRequiredException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("ApplicationNameRequiredException", message)


class DeploymentGroupAlreadyExistsException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("DeploymentGroupAlreadyExistsException", message)


class DeploymentGroupNameRequiredException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("DeploymentGroupNameRequiredException", message)


class DeploymentGroupDoesNotExistException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("DeploymentGroupDoesNotExistException", message)


class DeploymentConfigAlreadyExistsException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("DeploymentConfigAlreadyExistsException", message)


class DeploymentConfigDoesNotExistException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("DeploymentConfigDoesNotExistException", message)


class DeploymentConfigInUseException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("DeploymentConfigInUseException", message)


class InstanceNameRequiredException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("InstanceNameRequiredException", message)


class InstanceNotRegisteredException(CodeDeployException):
    code = 400

    def __init__(self, message: str):
        super().__init__("InstanceNotRegisteredException", message)
