from moto.core.exceptions import ServiceException


class CloudFrontException(ServiceException):
    pass


class OriginDoesNotExist(CloudFrontException):
    def __init__(self) -> None:
        super().__init__(
            "NoSuchOrigin",
            "One or more of your origins or origin groups do not exist.",
        )


class DomainNameNotAnS3Bucket(CloudFrontException):
    def __init__(self) -> None:
        super().__init__(
            "InvalidArgument",
            "The parameter Origin DomainName does not refer to a valid S3 bucket.",
        )


class DistributionAlreadyExists(CloudFrontException):
    def __init__(self, dist_id: str):
        super().__init__(
            "DistributionAlreadyExists",
            f"The caller reference that you are using to create a distribution is associated with another distribution. Already exists: {dist_id}",
        )


class InvalidIfMatchVersion(CloudFrontException):
    def __init__(self) -> None:
        super().__init__(
            "InvalidIfMatchVersion",
            "The If-Match version is missing or not valid for the resource.",
        )


class NoSuchDistribution(CloudFrontException):
    def __init__(self) -> None:
        super().__init__(
            "NoSuchDistribution", "The specified distribution does not exist."
        )


class NoSuchOriginAccessControl(CloudFrontException):
    def __init__(self) -> None:
        super().__init__(
            "NoSuchOriginAccessControl",
            "The specified origin access control does not exist.",
        )


class NoSuchInvalidation(CloudFrontException):
    def __init__(self) -> None:
        super().__init__(
            "NoSuchInvalidation", "The specified invalidation does not exist."
        )


class NoSuchFunctionExists(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchFunctionExists", message="The specified function does not exist."
        )


class FunctionAlreadyExists(CloudFrontException):
    def __init__(self) -> None:
        super().__init__(
            "FunctionAlreadyExists",
            message="A function with the same name already exists.",
        )


class NoSuchCachePolicy(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchCachePolicy", message="The specified cache policy does not exist."
        )


class NoSuchResponseHeadersPolicy(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchResponseHeadersPolicy",
            message="The specified response headers policy does not exist.",
        )


class NoSuchKeyGroup(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchResource",
            message="The specified key group does not exist.",
        )


class NoSuchCloudFrontOriginAccessIdentity(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchCloudFrontOriginAccessIdentity",
            message="The specified origin access identity does not exist.",
        )


class NoSuchStreamingDistribution(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchStreamingDistribution",
            message="The specified streaming distribution does not exist.",
        )


class NoSuchOriginRequestPolicy(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchOriginRequestPolicy",
            message="The specified origin request policy does not exist.",
        )


class NoSuchFieldLevelEncryptionConfig(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchFieldLevelEncryptionConfig",
            message="The specified field-level encryption configuration does not exist.",
        )


class NoSuchFieldLevelEncryptionProfile(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchFieldLevelEncryptionProfile",
            message="The specified field-level encryption profile does not exist.",
        )


class NoSuchContinuousDeploymentPolicy(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchContinuousDeploymentPolicy",
            message="The specified continuous deployment policy does not exist.",
        )


class NoSuchRealtimeLogConfig(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchRealtimeLogConfig",
            message="The specified real-time log configuration does not exist.",
        )


class NoSuchMonitoringSubscription(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchMonitoringSubscription",
            message="The specified monitoring subscription does not exist.",
        )


class NoSuchPublicKey(CloudFrontException):
    code = 404

    def __init__(self) -> None:
        super().__init__(
            "NoSuchPublicKey", message="The specified public key does not exist."
        )


class NoSuchResource(CloudFrontException):
    code = 404

    def __init__(self, message: str = "The specified resource does not exist.") -> None:
        super().__init__("NoSuchResource", message=message)
