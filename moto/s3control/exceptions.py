from moto.core.exceptions import ServiceException


class S3ControlError(ServiceException):
    pass


class AccessPointNotFound(S3ControlError):
    code = "NoSuchAccessPoint"

    def __init__(self, name: str):
        super().__init__("The specified accesspoint does not exist")
        self.access_point_name = name


class AccessPointPolicyNotFound(S3ControlError):
    code = "NoSuchAccessPointPolicy"

    def __init__(self, name: str):
        super().__init__("The specified accesspoint policy does not exist")
        self.access_point_name = name


class MultiRegionAccessPointNotFound(S3ControlError):
    code = "NoSuchMultiRegionAccessPoint"

    def __init__(self, name: str):
        super().__init__("The specified multi-region access point does not exist")
        self.name = name


class MultiRegionAccessPointPolicyNotFound(S3ControlError):
    code = "NoSuchMultiRegionAccessPointPolicy"

    def __init__(self, name: str):
        super().__init__(
            "The specified multi-region access point policy does not exist"
        )
        self.name = name


class MultiRegionAccessPointOperationNotFound(S3ControlError):
    code = "NoSuchAsyncRequest"

    def __init__(self, request_token: str):
        super().__init__("The specified async request does not exist")
        self.request_token_arn = request_token


class NoSuchPublicAccessBlockConfiguration(S3ControlError):
    # Note that this exception is in the different format then the S3 exception with the same name
    # This exception should return a nested response `<ErrorResponse><Error>..`
    # The S3 variant uses a flat `<Error>`-response
    code = "NoSuchPublicAccessBlockConfiguration"

    def __init__(self) -> None:
        super().__init__("The public access block configuration was not found")


class InvalidRequestException(S3ControlError):
    code = "InvalidRequest"

    def __init__(self, message: str):
        super().__init__(message)


class StorageLensConfigurationNotFound(S3ControlError):
    code = "NoSuchConfiguration"

    def __init__(self, config_id: str, **kwargs: Any):
        super().__init__(
            "NoSuchConfiguration",
            f"The specified configuration does not exist: {config_id}",
            **kwargs,
        )


class AccessGrantNotFound(S3ControlError):
    code = 404

    def __init__(self, grant_id: str, **kwargs: Any):
        super().__init__(
            "NoSuchAccessGrant",
            f"The specified access grant does not exist: {grant_id}",
            **kwargs,
        )


class AccessGrantsInstanceNotFound(S3ControlError):
    code = 404

    def __init__(self, **kwargs: Any):
        super().__init__(
            "NoSuchAccessGrantsInstance",
            "The Access Grants instance does not exist",
            **kwargs,
        )


class AccessGrantsLocationNotFound(S3ControlError):
    code = 404

    def __init__(self, location_id: str, **kwargs: Any):
        super().__init__(
            "NoSuchAccessGrantsLocation",
            f"The specified access grants location does not exist: {location_id}",
            **kwargs,
        )


class JobNotFound(S3ControlError):
    code = 404

    def __init__(self, job_id: str, **kwargs: Any):
        super().__init__(
            "NoSuchJob",
            f"The specified job does not exist: {job_id}",
            **kwargs,
        )


class StorageLensGroupNotFound(S3ControlError):
    code = 404

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(
            "NoSuchStorageLensGroup",
            f"The specified Storage Lens group does not exist: {name}",
            **kwargs,
        )
