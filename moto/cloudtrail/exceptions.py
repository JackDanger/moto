"""Exceptions raised by the cloudtrail service."""

from moto.core.exceptions import JsonRESTError


class InvalidParameterCombinationException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("InvalidParameterCombinationException", message)


class S3BucketDoesNotExistException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("S3BucketDoesNotExistException", message)


class InsufficientSnsTopicPolicyException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("InsufficientSnsTopicPolicyException", message)


class TrailNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, account_id: str, name: str):
        super().__init__(
            "TrailNotFoundException",
            f"Unknown trail: {name} for the user: {account_id}",
        )


class InvalidTrailNameException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("InvalidTrailNameException", message)


class TrailNameTooShort(InvalidTrailNameException):
    def __init__(self, actual_length: int):
        super().__init__(
            f"Trail name too short. Minimum allowed length: 3 characters. Specified name length: {actual_length} characters."
        )


class TrailNameTooLong(InvalidTrailNameException):
    def __init__(self, actual_length: int):
        super().__init__(
            f"Trail name too long. Maximum allowed length: 128 characters. Specified name length: {actual_length} characters."
        )


class TrailNameNotStartingCorrectly(InvalidTrailNameException):
    def __init__(self) -> None:
        super().__init__("Trail name must starts with a letter or number.")


class TrailNameNotEndingCorrectly(InvalidTrailNameException):
    def __init__(self) -> None:
        super().__init__("Trail name must ends with a letter or number.")


class TrailNameInvalidChars(InvalidTrailNameException):
    def __init__(self) -> None:
        super().__init__(
            "Trail name or ARN can only contain uppercase letters, lowercase letters, numbers, periods (.), hyphens (-), and underscores (_)."
        )


class EventDataStoreNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, arn: str):
        super().__init__(
            "EventDataStoreNotFoundException",
            f"The event data store {arn} was not found.",
        )


class ChannelNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, arn: str):
        super().__init__(
            "ChannelNotFoundException",
            f"The channel {arn} was not found.",
        )


class ResourceNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, resource_arn: str):
        super().__init__(
            "ResourceNotFoundException",
            f"The resource with ARN {resource_arn} was not found.",
        )


class QueryIdNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, query_id: str):
        super().__init__(
            "QueryIdNotFoundException",
            f"The query ID {query_id} was not found.",
        )
