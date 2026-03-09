from moto.core.exceptions import ServiceException


class LifecyclePolicyNotFoundException(ServiceException):
    code = "LifecyclePolicyNotFoundException"

    def __init__(self, repository_name: str, registry_id: str):
        message = (
            f"Lifecycle policy does not exist "
            f"for the repository with name '{repository_name}' "
            f"in the registry with id '{registry_id}'"
        )
        super().__init__(message)


class LimitExceededException(ServiceException):
    code = "LimitExceededException"
    message = "The scan quota per image has been exceeded. Wait and try again."


class RegistryPolicyNotFoundException(ServiceException):
    code = "RegistryPolicyNotFoundException"

    def __init__(self, registry_id: str):
        message = (
            f"Registry policy does not exist in the registry with id '{registry_id}'"
        )
        super().__init__(message)


class RepositoryAlreadyExistsException(ServiceException):
    code = "RepositoryAlreadyExistsException"

    def __init__(self, repository_name: str, registry_id: str):
        message = (
            f"The repository with name '{repository_name}' already exists "
            f"in the registry with id '{registry_id}'"
        )
        super().__init__(message)


class RepositoryNotEmptyException(ServiceException):
    code = "RepositoryNotEmptyException"

    def __init__(self, repository_name: str, registry_id: str):
        message = (
            f"The repository with name '{repository_name}' "
            f"in registry with id '{registry_id}' "
            f"cannot be deleted because it still contains images"
        )
        super().__init__(message)


class RepositoryNotFoundException(ServiceException):
    code = "RepositoryNotFoundException"

    def __init__(self, repository_name: str, registry_id: str):
        message = (
            f"The repository with name '{repository_name}' does not exist "
            f"in the registry with id '{registry_id}'"
        )
        super().__init__(message)


class RepositoryPolicyNotFoundException(ServiceException):
    code = "RepositoryPolicyNotFoundException"

    def __init__(self, repository_name: str, registry_id: str):
        message = (
            f"Repository policy does not exist "
            f"for the repository with name '{repository_name}' "
            f"in the registry with id '{registry_id}'"
        )
        super().__init__(message)


class ImageNotFoundException(ServiceException):
    code = "ImageNotFoundException"

    def __init__(self, image_id: str, repository_name: str, registry_id: str):
        message = (
            f"The image with imageId {image_id} does not exist "
            f"within the repository with name '{repository_name}' "
            f"in the registry with id '{registry_id}'"
        )
        super().__init__(message)


class ImageAlreadyExistsException(ServiceException):
    code = "ImageAlreadyExistsException"

    def __init__(
        self,
        repository_name: str,
        registry_id: str,
        digest: str,
        image_tag: str,
    ):
        message = (
            f"Image with digest '{digest}' and tag '{image_tag}' already exists "
            f"in the repository with name '{repository_name}' "
            f"in registry with id '{registry_id}'"
        )
        super().__init__(message)


class InvalidParameterException(ServiceException):
    code = "InvalidParameterException"


class ScanNotFoundException(ServiceException):
    code = "ScanNotFoundException"

    def __init__(self, image_id: str, repository_name: str, registry_id: str):
        message = (
            f"Image scan does not exist for the image with '{image_id}' "
            f"in the repository with name '{repository_name}' "
            f"in the registry with id '{registry_id}'"
        )
        super().__init__(message)


class ValidationException(ServiceException):
    code = "ValidationException"


class PullThroughCacheRuleNotFoundException(ServiceException):
    code = "PullThroughCacheRuleNotFoundException"

    def __init__(self, ecr_repository_prefix: str, registry_id: str):
        message = (
            "The pull through cache rule with Amazon ECR repository "
            f"prefix '{ecr_repository_prefix}' does not exist in the "
            f"registry with id '{registry_id}'"
        )
        super().__init__(message)


class PullThroughCacheRuleAlreadyExistsException(ServiceException):
    code = "PullThroughCacheRuleAlreadyExistsException"

    def __init__(self, ecr_repository_prefix: str, registry_id: str):
        message = (
            "The pull through cache rule with Amazon ECR repository "
            f"prefix '{ecr_repository_prefix}' already exists in the "
            f"registry with id '{registry_id}'"
        )
        super().__init__(message)


class TemplateNotFoundException(ServiceException):
    code = "TemplateNotFoundException"

    def __init__(self, prefix: str, registry_id: str):
        message = (
            f"The repository creation template with the prefix "
            f"'{prefix}' does not exist in the registry with id "
            f"'{registry_id}'"
        )
        super().__init__(message)


class TemplateAlreadyExistsException(ServiceException):
    code = "TemplateAlreadyExistsException"

    def __init__(self, prefix: str, registry_id: str):
        message = (
            f"The repository creation template with the prefix "
            f"'{prefix}' already exists in the registry with id "
            f"'{registry_id}'"
        )
        super().__init__(message)
