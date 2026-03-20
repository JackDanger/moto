"""Exceptions for Rekognition."""

from moto.core.exceptions import AWSError


class ResourceNotFoundException(AWSError):
    TYPE = "ResourceNotFoundException"
    STATUS = 400


class ResourceAlreadyExistsException(AWSError):
    TYPE = "ResourceAlreadyExistsException"
    STATUS = 400


class InvalidParameterException(AWSError):
    TYPE = "InvalidParameterException"
    STATUS = 400


class ResourceInUseException(AWSError):
    TYPE = "ResourceInUseException"
    STATUS = 400
