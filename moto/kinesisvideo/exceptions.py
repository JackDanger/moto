from moto.core.exceptions import ServiceException


class KinesisvideoClientError(ServiceException):
    pass


class ResourceNotFoundException(KinesisvideoClientError):
    def __init__(self, message: str = "The requested stream is not found or not active.") -> None:
        self.code = 404
        super().__init__(
            "ResourceNotFoundException",
            message,
        )


class ResourceInUseException(KinesisvideoClientError):
    def __init__(self, message: str):
        super().__init__("ResourceInUseException", message)


class AccessDeniedException(KinesisvideoClientError):
    def __init__(self, message: str):
        self.code = 401
        super().__init__("ClientLimitExceededException", message)
