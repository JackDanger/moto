from moto.core.exceptions import JsonRESTError


class InvalidStructureException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("InvalidStructureException", message)


class PipelineNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("PipelineNotFoundException", message)


class ResourceNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("ResourceNotFoundException", message)


class InvalidTagsException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("InvalidTagsException", message)


class TooManyTagsException(JsonRESTError):
    code = 400

    def __init__(self, arn: str):
        super().__init__(
            "TooManyTagsException", f"Tag limit exceeded for resource [{arn}]."
        )


class ActionNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("ActionNotFoundException", message)


class ActionTypeNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("ActionTypeNotFoundException", message)


class PipelineExecutionNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("PipelineExecutionNotFoundException", message)


class StageNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("StageNotFoundException", message)


class WebhookNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("WebhookNotFoundException", message)


class JobNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("JobNotFoundException", message)


class InvalidNonceException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("InvalidNonceException", message)


class NotLatestPipelineExecutionException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("NotLatestPipelineExecutionException", message)


class StageNotRetryableException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("StageNotRetryableException", message)


class ConflictException(JsonRESTError):
    code = 409

    def __init__(self, message: str):
        super().__init__("ConflictException", message)


class ValidationException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("ValidationException", message)
