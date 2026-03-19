import datetime
import string
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.moto_api._internal import mock_random as random
from moto.moto_api._internal.managed_state_model import ManagedState
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import PARTITION_NAMES, get_partition

from .exceptions import (
    DistributionAlreadyExists,
    DomainNameNotAnS3Bucket,
    FunctionAlreadyExists,
    InvalidIfMatchVersion,
    NoSuchCachePolicy,
    NoSuchCloudFrontOriginAccessIdentity,
    NoSuchContinuousDeploymentPolicy,
    NoSuchDistribution,
    NoSuchFieldLevelEncryptionConfig,
    NoSuchFieldLevelEncryptionProfile,
    NoSuchFunctionExists,
    NoSuchInvalidation,
    NoSuchKeyGroup,
    NoSuchMonitoringSubscription,
    NoSuchOriginAccessControl,
    NoSuchOriginRequestPolicy,
    NoSuchPublicKey,
    NoSuchRealtimeLogConfig,
    NoSuchResource,
    NoSuchResponseHeadersPolicy,
    NoSuchStreamingDistribution,
    OriginDoesNotExist,
)


def random_id(uppercase: bool = True, length: int = 13) -> str:
    ascii_set = string.ascii_uppercase if uppercase else string.ascii_lowercase
    chars = list(range(10)) + list(ascii_set)
    resource_id = random.choice(ascii_set) + "".join(
        str(random.choice(chars)) for _ in range(length - 1)
    )
    return resource_id


class AnycastIpList:
    def __init__(self, name: str, account_id: str) -> None:
        self.id = random_id(length=14)
        self.name = name
        self.status = "Deployed"
        self.arn = f"arn:aws:cloudfront::{account_id}:anycast-ip-list/{self.id}"
        self.anycast_ips: list[str] = []
        self.ip_count = 0
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class VpcOrigin:
    def __init__(self, config: dict[str, Any], account_id: str) -> None:
        self.id = random_id(length=14)
        self.arn = f"arn:aws:cloudfront::{account_id}:vpcorigin/{self.id}"
        self.status = "Deployed"
        self.created_time = iso_8601_datetime_with_milliseconds()
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.vpc_origin_endpoint_config = config
        self.etag = random_id(length=14)

    def update(self, config: dict[str, Any]) -> None:
        self.vpc_origin_endpoint_config = config
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class KeyValueStore:
    def __init__(self, name: str, comment: str, account_id: str) -> None:
        self.id = random_id(length=14)
        self.name = name
        self.comment = comment
        self.arn = f"arn:aws:cloudfront::{account_id}:key-value-store/{name}"
        self.status = "READY"
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)

    def update(self, comment: str) -> None:
        self.comment = comment
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class ActiveTrustedSigners:
    def __init__(self) -> None:
        self.enabled = False
        self.quantity = 0
        self.items: list[Any] = []


class ActiveTrustedKeyGroups:
    def __init__(self) -> None:
        self.enabled = False
        self.quantity = 0
        self.items: list[Any] = []


class LambdaFunctionAssociation:
    def __init__(self) -> None:
        self.arn = ""
        self.event_type = ""
        self.include_body = False


class ForwardedValues:
    def __init__(self, config: dict[str, Any]):
        if "QueryString" not in config:
            config["QueryString"] = False
        if "Cookies" not in config:
            config["Cookies"] = {"Forward": "none"}
        self.__dict__.update(config)


class TrustedSigners:
    def __init__(self, config: dict[str, Any]):
        self.items = config.get("Items", [])
        self.quantity = len(self.items)
        self.enabled = True if self.quantity else False


class TrustedKeyGroups:
    def __init__(self, config: dict[str, Any]):
        self.items = config.get("Items", [])
        self.quantity = len(self.items)
        self.enabled = True if self.quantity > 0 else False


class AllowedMethods:
    def __init__(self, config: dict[str, Any]):
        self.items = config.get("Items", ["HEAD", "GET"])
        self.quantity = len(self.items)
        cached_methods = config.get("CachedMethods", {})
        cached_methods_items = cached_methods.get("Items", ["GET", "HEAD"])
        self.cached_methods = {
            "Items": cached_methods_items,
            "Quantity": len(cached_methods_items),
        }


class DefaultCacheBehaviour:
    def __init__(self, config: dict[str, Any]):
        self.target_origin_id = config["TargetOriginId"]
        self.trusted_signers_enabled = False
        self.trusted_signers = TrustedSigners(config.get("TrustedSigners") or {})
        self.trusted_key_groups = TrustedKeyGroups(config.get("TrustedKeyGroups") or {})
        self.viewer_protocol_policy = config["ViewerProtocolPolicy"]
        methods = config.get("AllowedMethods", {})
        self.allowed_methods = AllowedMethods(methods)
        self.smooth_streaming = config.get("SmoothStreaming", False)
        self.compress = config.get("Compress", True)
        self.lambda_function_associations = {"Quantity": 0}
        self.function_associations = {"Quantity": 0}
        self.field_level_encryption_id = config.get("FieldLevelEncryptionId") or ""
        self.forwarded_values = ForwardedValues(config.get("ForwardedValues", {}))
        self.min_ttl = config.get("MinTTL") or 0
        self.default_ttl = config.get("DefaultTTL") or 0
        self.max_ttl = config.get("MaxTTL") or 0
        self.realtime_log_config_arn = config.get("RealtimeLogConfigArn") or ""
        self.cache_policy_id = config.get("CachePolicyId", "")
        self.origin_request_policy_id = config.get("OriginRequestPolicyId")
        self.response_headers_policy_id = config.get("ResponseHeadersPolicyId")


class CacheBehaviour(DefaultCacheBehaviour):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.path_pattern: str = config.get("PathPattern", "")
        methods = config.get("AllowedMethods", {})
        self.allowed_methods = AllowedMethods(methods)
        self.cache_policy_id = config.get("CachePolicyId", "")
        self.origin_request_policy_id = config.get("OriginRequestPolicyId", "")


class Logging:
    def __init__(self, config: dict[str, Any]) -> None:
        self.enabled = config.get("Enabled") or False
        self.include_cookies = config.get("IncludeCookies") or False
        self.bucket = config.get("Bucket") or ""
        self.prefix = config.get("Prefix") or ""


class ViewerCertificate:
    def __init__(self, config: dict[str, Any]) -> None:
        self.cloud_front_default_certificate = config.get(
            "CloudFrontDefaultCertificate", True
        )
        self.iam_certificate_id = config.get("IAMCertificateId") or ""
        self.acm_certificate_arn = config.get("ACMCertificateArn") or ""
        self.ssl_support_method = config.get("SSLSupportMethod") or "sni-only"
        self.minimum_protocol_version = config.get("MinimumProtocolVersion") or "TLSv1"
        self.certificate_source = "cloudfront"
        self.certificate = config.get("Certificate", "")


class CustomOriginConfig:
    def __init__(self, config: dict[str, Any]):
        self.http_port = config.get("HTTPPort")
        self.https_port = config.get("HTTPSPort")
        self.origin_keepalive_timeout = config.get("OriginKeepaliveTimeout") or 5
        self.origin_protocol_policy = config.get("OriginProtocolPolicy")
        self.origin_read_timeout = config.get("OriginReadTimeout") or 30
        protocols = config.get("OriginSslProtocols", {}).get("Items", [])
        self.origin_ssl_protocols = {
            "Quantity": len(protocols),
            "Items": protocols,
        }


class Origin:
    def __init__(self, origin: dict[str, Any]):
        self.id = origin["Id"]
        self.domain_name = origin["DomainName"]
        self.origin_path = origin.get("OriginPath") or ""
        self.s3_access_identity = ""
        self.custom_origin = None
        if "OriginShield" not in origin:
            origin["OriginShield"] = {"Enabled": False}
        self.origin_shield = origin["OriginShield"]
        self.connection_attempts = origin.get("ConnectionAttempts") or 3
        self.connection_timeout = origin.get("ConnectionTimeout") or 10

        if "S3OriginConfig" in origin:
            # Very rough validation
            if not self.domain_name.endswith("amazonaws.com"):
                raise DomainNameNotAnS3Bucket
            self.s3_access_identity = origin["S3OriginConfig"]["OriginAccessIdentity"]

        if "CustomOriginConfig" in origin:
            self.custom_origin_config = CustomOriginConfig(origin["CustomOriginConfig"])

        if "CustomHeaders" not in origin:
            origin["CustomHeaders"] = {"Quantity": 0, "Items": []}
        self.custom_headers = origin["CustomHeaders"]


class GeoRestriction:
    def __init__(self, config: dict[str, Any]):
        self.restriction_type = config.get("RestrictionType", "none")
        self.items = config.get("Items", [])
        self.quantity = len(self.items)
        if not self.quantity:
            self.items = None


class DistributionConfig:
    def __init__(self, config: dict[str, Any]):
        if "Aliases" not in config:
            config["Aliases"] = {"Quantity": 0}
        else:
            config["Aliases"]["Quantity"] = len(config["Aliases"].get("Items", []))
        if "OriginGroups" not in config:
            config["OriginGroups"] = {"Quantity": 0}
        if "CustomErrorResponses" not in config:
            config["CustomErrorResponses"] = {"Quantity": 0}
        if "ViewerCertificate" not in config:
            config["ViewerCertificate"] = ViewerCertificate({})
        else:
            config["ViewerCertificate"] = ViewerCertificate(config["ViewerCertificate"])
        config["Origins"]["Items"] = [Origin(o) for o in config["Origins"]["Items"]]
        if "CacheBehaviors" not in config:
            config["CacheBehaviors"] = {"Quantity": 0}
        elif config["CacheBehaviors"].get("Quantity"):
            config["CacheBehaviors"]["Items"] = [
                CacheBehaviour(cb) for cb in config["CacheBehaviors"]["Items"]
            ]
        if "Restrictions" not in config:
            config["Restrictions"] = {"GeoRestriction": GeoRestriction({})}
        elif config.get("Restrictions", {}).get("GeoRestriction"):
            config["Restrictions"]["GeoRestriction"] = GeoRestriction(
                config["Restrictions"]["GeoRestriction"]
            )
        config["Logging"] = Logging(config.get("Logging", {}))
        config["DefaultCacheBehavior"] = DefaultCacheBehaviour(
            config.get("DefaultCacheBehavior", {})
        )
        config["PriceClass"] = config.get("PriceClass", "PriceClass_All")
        config["HttpVersion"] = config.get("HttpVersion", "http2")
        config["IsIPV6Enabled"] = config.get("IsIPV6Enabled", True)
        config["DefaultRootObject"] = config.get("DefaultRootObject", "")
        config["WebACLId"] = config.get("WebACLId", "")
        if config["DefaultCacheBehavior"].target_origin_id not in [
            o.id for o in config["Origins"]["Items"]
        ]:
            raise OriginDoesNotExist
        self.__dict__.update(config)
        # HACK: this attribute is referenced in backend methods.
        self.caller_reference = config["CallerReference"]


class Distribution(BaseModel, ManagedState):
    def __init__(self, account_id: str, region_name: str, config: dict[str, Any]):
        # Configured ManagedState
        super().__init__(
            "cloudfront::distribution", transitions=[("InProgress", "Deployed")]
        )
        # Configure internal properties
        self.distribution_id = random_id()
        self.id = self.distribution_id
        self.arn = f"arn:{get_partition(region_name)}:cloudfront:{account_id}:distribution/{self.distribution_id}"
        self.distribution_config = DistributionConfig(config)
        self.active_trusted_signers = ActiveTrustedSigners()
        self.active_trusted_key_groups = ActiveTrustedKeyGroups()
        self.origin_groups: list[Any] = []
        self.alias_icp_recordals: list[Any] = []
        self.last_modified_time = "2021-11-27T10:34:26.802Z"
        self.in_progress_invalidation_batches = 0
        self.has_active_trusted_key_groups = False
        self.domain_name = f"{random_id(uppercase=False)}.cloudfront.net"
        self.etag = random_id()

    @property
    def location(self) -> str:
        return f"https://cloudfront.amazonaws.com/2020-05-31/distribution/{self.distribution_id}"


class OriginAccessControl(BaseModel):
    def __init__(self, config_dict: dict[str, str]):
        self.id = random_id()
        self.name = config_dict.get("Name")
        self.description = config_dict.get("Description")
        self.signing_protocol = config_dict.get("SigningProtocol")
        self.signing_behavior = config_dict.get("SigningBehavior")
        self.origin_type = config_dict.get("OriginAccessControlOriginType")
        self.etag = random_id()

    def update(self, config: dict[str, str]) -> None:
        if "Name" in config:
            self.name = config["Name"]
        if "Description" in config:
            self.description = config["Description"]
        if "SigningProtocol" in config:
            self.signing_protocol = config["SigningProtocol"]
        if "SigningBehavior" in config:
            self.signing_behavior = config["SigningBehavior"]
        if "OriginAccessControlOriginType" in config:
            self.origin_type = config["OriginAccessControlOriginType"]


class Invalidation(BaseModel):
    def __init__(self, distribution: Distribution, paths: list[str], caller_ref: str):
        self.id = random_id()
        self.create_time = utcnow()
        self.distribution = distribution
        self.status = "COMPLETED"
        self.paths = paths
        self.caller_ref = caller_ref

    @property
    def location(self) -> str:
        return self.distribution.location + f"/invalidation/{self.id}"

    @property
    def invalidation_batch(self) -> dict[str, Any]:
        return {
            "Paths": {"Quantity": len(self.paths), "Items": self.paths},
            "CallerReference": self.caller_ref,
        }


class PublicKey(BaseModel):
    def __init__(self, caller_ref: str, name: str, encoded_key: str):
        self.id = random_id(length=14)
        self.caller_ref = caller_ref
        self.name = name
        self.encoded_key = encoded_key
        self.created_time = utcnow()
        self.comment = ""
        self.etag = random_id(length=14)
        self.location = (
            f"https://cloudfront.amazonaws.com/2020-05-31/public-key/{self.id}"
        )

        # Last newline-separator is lost in the XML->Python transformation, but should exist
        if not self.encoded_key.endswith("\n"):
            self.encoded_key += "\n"

    @property
    def public_key_config(self) -> dict[str, str]:
        return {
            "CallerReference": self.caller_ref,
            "Name": self.name,
            "EncodedKey": self.encoded_key,
            "Comment": self.comment,
        }


class KeyGroup(BaseModel):
    def __init__(self, name: str, items: list[str]):
        self.id = random_id(length=14)
        self.name = name
        self.items = items
        self.etag = random_id(length=14)
        self.last_modified_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        self.location = (
            f"https://cloudfront.amazonaws.com/2020-05-31/key-group/{self.id}"
        )

    @property
    def key_group_config(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Items": self.items,
            "Comment": "",
        }

    def update(self, name: str, items: list[str]) -> None:
        self.name = name
        self.items = items
        self.etag = random_id(length=14)
        self.last_modified_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )


class CloudFrontFunction(BaseModel):
    def __init__(
        self,
        name: str,
        function_code: str,
        function_config: dict[str, Any],
        account_id: str,
        region_name: str,
    ):
        self.name = name
        self.function_code = function_code
        self.function_config = function_config
        self.status = "UNPUBLISHED"
        self.stage = "DEVELOPMENT"
        self.created_time = iso_8601_datetime_with_milliseconds()
        self.last_modified_time = self.created_time
        self.etag = random_id(length=14)
        partition = get_partition(region_name)
        self.function_arn = (
            f"arn:{partition}:cloudfront::{account_id}:function/{self.name}"
        )

    def update(self, function_code: str, function_config: dict[str, Any]) -> None:
        self.function_code = function_code
        self.function_config = function_config
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)

    def publish(self) -> None:
        self.status = "UNASSOCIATED"
        self.stage = "LIVE"
        self.etag = random_id(length=14)


class CachePolicy(BaseModel):
    def __init__(self, config: dict[str, Any]):
        self.id = random_id(length=14)
        self.name = config.get("Name", "")
        self.comment = config.get("Comment", "")
        self.default_ttl = int(config.get("DefaultTTL", 86400))
        self.max_ttl = int(config.get("MaxTTL", 31536000))
        self.min_ttl = int(config.get("MinTTL", 0))
        self.parameters_in_cache_key = config.get(
            "ParametersInCacheKeyAndForwardedToOrigin", {}
        )
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)

    def update(self, config: dict[str, Any]) -> None:
        self.name = config.get("Name", self.name)
        self.comment = config.get("Comment", self.comment)
        self.default_ttl = int(config.get("DefaultTTL", self.default_ttl))
        self.max_ttl = int(config.get("MaxTTL", self.max_ttl))
        self.min_ttl = int(config.get("MinTTL", self.min_ttl))
        if "ParametersInCacheKeyAndForwardedToOrigin" in config:
            self.parameters_in_cache_key = config[
                "ParametersInCacheKeyAndForwardedToOrigin"
            ]
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class ResponseHeadersPolicy(BaseModel):
    def __init__(self, config: dict[str, Any]):
        self.id = random_id(length=14)
        self.name = config.get("Name", "")
        self.comment = config.get("Comment", "")
        self.cors_config = config.get("CorsConfig")
        self.security_headers_config = config.get("SecurityHeadersConfig")
        self.custom_headers_config = config.get("CustomHeadersConfig")
        self.server_timing_headers_config = config.get("ServerTimingHeadersConfig")
        self.remove_headers_config = config.get("RemoveHeadersConfig")
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)

    def update(self, config: dict[str, Any]) -> None:
        self.name = config.get("Name", self.name)
        self.comment = config.get("Comment", self.comment)
        if "CorsConfig" in config:
            self.cors_config = config["CorsConfig"]
        if "SecurityHeadersConfig" in config:
            self.security_headers_config = config["SecurityHeadersConfig"]
        if "CustomHeadersConfig" in config:
            self.custom_headers_config = config["CustomHeadersConfig"]
        if "ServerTimingHeadersConfig" in config:
            self.server_timing_headers_config = config["ServerTimingHeadersConfig"]
        if "RemoveHeadersConfig" in config:
            self.remove_headers_config = config["RemoveHeadersConfig"]
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class OriginAccessIdentity(BaseModel):
    def __init__(self, caller_reference: str, comment: str):
        self.id = random_id()
        self.s3_canonical_user_id = "".join(
            str(random.choice(list(string.ascii_lowercase + string.digits)))
            for _ in range(64)
        )
        self.caller_reference = caller_reference
        self.comment = comment
        self.etag = random_id()

    def update(self, caller_reference: str, comment: str) -> None:
        self.caller_reference = caller_reference
        self.comment = comment
        self.etag = random_id()


class StreamingDistributionConfig:
    def __init__(self, config: dict[str, Any]):
        self.caller_reference = config.get("CallerReference", str(random.uuid4()))
        self.comment = config.get("Comment", "")
        self.enabled = config.get("Enabled", "false")
        self.price_class = config.get("PriceClass", "PriceClass_All")
        s3_origin = config.get("S3Origin", {})
        self.s3_origin_dns_name = s3_origin.get("DomainName", "")
        self.s3_origin_access_identity = s3_origin.get("OriginAccessIdentity", "")
        self.aliases = ((config.get("Aliases") or {}).get("Items") or {}).get(
            "CNAME"
        ) or []
        if isinstance(self.aliases, str):
            self.aliases = [self.aliases]
        self.logging = Logging(config.get("Logging") or {})
        trusted = config.get("TrustedSigners", {})
        self.trusted_signers_enabled = (
            trusted.get("Enabled", "false").lower() == "true"
            if isinstance(trusted.get("Enabled"), str)
            else bool(trusted.get("Enabled", False))
        )
        items = trusted.get("Items") or {}
        self.trusted_signers = items.get("AwsAccountNumber") or []
        if isinstance(self.trusted_signers, str):
            self.trusted_signers = [self.trusted_signers]


class StreamingDistribution(BaseModel, ManagedState):
    def __init__(self, account_id: str, region_name: str, config: dict[str, Any]):
        super().__init__(
            "cloudfront::streaming-distribution",
            transitions=[("InProgress", "Deployed")],
        )
        self.streaming_distribution_id = random_id()
        self.arn = f"arn:{get_partition(region_name)}:cloudfront:{account_id}:streaming-distribution/{self.streaming_distribution_id}"
        self.streaming_distribution_config = StreamingDistributionConfig(config)
        self.domain_name = f"{random_id(uppercase=False)}.cloudfront.net"
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id()

    @property
    def location(self) -> str:
        return f"https://cloudfront.amazonaws.com/2020-05-31/streaming-distribution/{self.streaming_distribution_id}"


class OriginRequestPolicy(BaseModel):
    def __init__(self, config: dict[str, Any]):
        self.id = random_id(length=14)
        self.name = config.get("Name", "")
        self.comment = config.get("Comment", "")
        self.headers_config = config.get("HeadersConfig", {})
        self.cookies_config = config.get("CookiesConfig", {})
        self.query_strings_config = config.get("QueryStringsConfig", {})
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)

    def update(self, config: dict[str, Any]) -> None:
        self.name = config.get("Name", self.name)
        self.comment = config.get("Comment", self.comment)
        if "HeadersConfig" in config:
            self.headers_config = config["HeadersConfig"]
        if "CookiesConfig" in config:
            self.cookies_config = config["CookiesConfig"]
        if "QueryStringsConfig" in config:
            self.query_strings_config = config["QueryStringsConfig"]
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class FieldLevelEncryptionConfig(BaseModel):
    def __init__(self, config: dict[str, Any]):
        self.id = random_id(length=14)
        self.caller_reference = config.get("CallerReference", str(random.uuid4()))
        self.comment = config.get("Comment", "")
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)

    def update(self, config: dict[str, Any]) -> None:
        self.caller_reference = config.get("CallerReference", self.caller_reference)
        self.comment = config.get("Comment", self.comment)
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class FieldLevelEncryptionProfile(BaseModel):
    def __init__(self, config: dict[str, Any]):
        self.id = random_id(length=14)
        self.name = config.get("Name", "")
        self.caller_reference = config.get("CallerReference", str(random.uuid4()))
        self.comment = config.get("Comment", "")
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)

    def update(self, config: dict[str, Any]) -> None:
        self.name = config.get("Name", self.name)
        self.caller_reference = config.get("CallerReference", self.caller_reference)
        self.comment = config.get("Comment", self.comment)
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class ContinuousDeploymentPolicy(BaseModel):
    def __init__(self, config: dict[str, Any]):
        self.id = random_id(length=14)
        self.enabled = config.get("Enabled", "false")
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)

    def update(self, config: dict[str, Any]) -> None:
        if "Enabled" in config:
            self.enabled = config["Enabled"]
        self.last_modified_time = iso_8601_datetime_with_milliseconds()
        self.etag = random_id(length=14)


class MonitoringSubscription(BaseModel):
    def __init__(self, distribution_id: str, realtime_metrics_config: dict[str, Any]):
        self.distribution_id = distribution_id
        self.realtime_metrics_subscription_status = realtime_metrics_config.get(
            "RealtimeMetricsSubscriptionStatus", "Disabled"
        )


class RealtimeLogConfig(BaseModel):
    def __init__(
        self,
        name: str,
        sampling_rate: int,
        end_points: list[dict[str, Any]],
        fields: list[str],
        account_id: str,
        region_name: str,
    ):
        self.name = name
        self.arn = f"arn:{get_partition(region_name)}:cloudfront::{account_id}:realtime-log-config/{self.name}"
        self.sampling_rate = sampling_rate
        self.end_points = end_points
        self.fields = fields

    def update(
        self,
        sampling_rate: int | None,
        end_points: list[dict[str, Any]] | None,
        fields: list[str] | None,
    ) -> None:
        if sampling_rate is not None:
            self.sampling_rate = sampling_rate
        if end_points is not None:
            self.end_points = end_points
        if fields is not None:
            self.fields = fields

    @property
    def key_group_config(self) -> dict[str, Any]:
        return {
            "Items": self.items,
            "Name": self.name,
        }



class CloudFrontBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.distributions: dict[str, Distribution] = {}
        self.invalidations: dict[str, list[Invalidation]] = {}
        self.origin_access_controls: dict[str, OriginAccessControl] = {}
        self.origin_access_identities: dict[str, OriginAccessIdentity] = {}
        self.public_keys: dict[str, PublicKey] = {}
        self.key_groups: dict[str, KeyGroup] = {}
        self.functions: dict[str, CloudFrontFunction] = {}
        self.cache_policies: dict[str, CachePolicy] = {}
        self.response_headers_policies: dict[str, ResponseHeadersPolicy] = {}
        self.origin_request_policies: dict[str, OriginRequestPolicy] = {}
        self.streaming_distributions: dict[str, StreamingDistribution] = {}
        self.field_level_encryption_configs: dict[str, FieldLevelEncryptionConfig] = {}
        self.field_level_encryption_profiles: dict[
            str, FieldLevelEncryptionProfile
        ] = {}
        self.continuous_deployment_policies: dict[str, ContinuousDeploymentPolicy] = {}
        self.monitoring_subscriptions: dict[str, MonitoringSubscription] = {}
        self.realtime_log_configs: dict[str, RealtimeLogConfig] = {}
        self.anycast_ip_lists: dict[str, AnycastIpList] = {}
        self.vpc_origins: dict[str, VpcOrigin] = {}
        self.key_value_stores: dict[str, KeyValueStore] = {}
        self.tagger = TaggingService()

    def create_distribution(
        self, distribution_config: dict[str, Any], tags: list[dict[str, str]]
    ) -> tuple[Distribution, str, str]:
        """
        Not all configuration options are supported yet.  Please raise an issue if
        we're not persisting/returning the correct attributes for your
        use-case.
        """
        # We'll always call dist_with_tags, as the incoming request is the same
        return self.create_distribution_with_tags(distribution_config, tags)

    def create_distribution_with_tags(
        self, distribution_config: dict[str, Any], tags: list[dict[str, str]]
    ) -> tuple[Distribution, str, str]:
        dist = Distribution(self.account_id, self.region_name, distribution_config)
        caller_reference = dist.distribution_config.caller_reference
        existing_dist = self._distribution_with_caller_reference(caller_reference)
        if existing_dist is not None:
            raise DistributionAlreadyExists(existing_dist.distribution_id)
        self.distributions[dist.distribution_id] = dist
        self.tagger.tag_resource(dist.arn, tags)
        return dist, dist.location, dist.etag

    def get_distribution(self, distribution_id: str) -> tuple[Distribution, str]:
        if distribution_id not in self.distributions:
            raise NoSuchDistribution
        dist = self.distributions[distribution_id]
        dist.advance()
        return dist, dist.etag

    def get_distribution_config(
        self, distribution_id: str
    ) -> tuple[DistributionConfig, str]:
        if distribution_id not in self.distributions:
            raise NoSuchDistribution
        dist = self.distributions[distribution_id]
        dist.advance()
        return dist.distribution_config, dist.etag

    def delete_distribution(self, distribution_id: str, if_match: bool) -> None:
        """
        The IfMatch-value is ignored - any value is considered valid.
        Calling this function without a value is invalid, per AWS' behaviour
        """
        if not if_match:
            raise InvalidIfMatchVersion
        if distribution_id not in self.distributions:
            raise NoSuchDistribution
        del self.distributions[distribution_id]

    def list_distributions(self) -> list[Distribution]:
        """
        Pagination is not supported yet.
        """
        for dist in self.distributions.values():
            dist.advance()
        return list(self.distributions.values())

    def _distribution_with_caller_reference(
        self, reference: str
    ) -> Optional[Distribution]:
        for dist in self.distributions.values():
            config = dist.distribution_config
            if config.caller_reference == reference:
                return dist
        return None

    def update_distribution(
        self, dist_config: dict[str, Any], _id: str, if_match: bool
    ) -> tuple[Distribution, str, str]:
        """
        The IfMatch-value is ignored - any value is considered valid.
        Calling this function without a value is invalid, per AWS' behaviour
        """
        if _id not in self.distributions or _id is None:
            raise NoSuchDistribution
        if not if_match:
            raise InvalidIfMatchVersion
        if not dist_config:
            raise NoSuchDistribution
        dist = self.distributions[_id]

        dist.distribution_config = DistributionConfig(dist_config)
        self.distributions[_id] = dist
        dist.advance()
        return dist, dist.location, dist.etag

    def create_invalidation(
        self, dist_id: str, paths: list[str], caller_ref: str
    ) -> Invalidation:
        dist, _ = self.get_distribution(dist_id)
        invalidation = Invalidation(dist, paths, caller_ref)
        try:
            self.invalidations[dist_id].append(invalidation)
        except KeyError:
            self.invalidations[dist_id] = [invalidation]

        return invalidation

    def list_invalidations(self, dist_id: str) -> list[Invalidation]:
        """
        Pagination is not yet implemented
        """
        return self.invalidations.get(dist_id) or []

    def get_invalidation(self, dist_id: str, id: str) -> Invalidation:
        if dist_id not in self.distributions:
            raise NoSuchDistribution
        try:
            invalidations = self.invalidations[dist_id]
            if invalidations:
                for invalidation in invalidations:
                    if invalidation.id == id:
                        return invalidation
        except KeyError:
            pass
        raise NoSuchInvalidation

    def list_tags_for_resource(self, resource: str) -> dict[str, list[dict[str, str]]]:
        return self.tagger.list_tags_for_resource(resource)

    def tag_resource(self, resource: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(resource, tags)

    def untag_resource(self, resource: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource, tag_keys)

    def create_origin_access_control(
        self, config_dict: dict[str, str]
    ) -> OriginAccessControl:
        control = OriginAccessControl(config_dict)
        self.origin_access_controls[control.id] = control
        return control

    def get_origin_access_control(self, control_id: str) -> OriginAccessControl:
        if control_id not in self.origin_access_controls:
            raise NoSuchOriginAccessControl
        return self.origin_access_controls[control_id]

    def update_origin_access_control(
        self, control_id: str, config: dict[str, str]
    ) -> OriginAccessControl:
        """
        The IfMatch-parameter is not yet implemented
        """
        control = self.get_origin_access_control(control_id)
        control.update(config)
        return control

    def list_origin_access_controls(self) -> list[OriginAccessControl]:
        """
        Pagination is not yet implemented
        """
        return list(self.origin_access_controls.values())

    def delete_origin_access_control(self, control_id: str) -> None:
        """
        The IfMatch-parameter is not yet implemented
        """
        if control_id not in self.origin_access_controls:
            raise NoSuchOriginAccessControl
        self.origin_access_controls.pop(control_id)

    def create_public_key(
        self, caller_ref: str, name: str, encoded_key: str
    ) -> PublicKey:
        key = PublicKey(name=name, caller_ref=caller_ref, encoded_key=encoded_key)
        self.public_keys[key.id] = key
        return key

    def get_public_key(self, key_id: str) -> PublicKey:
        if key_id not in self.public_keys:
            raise NoSuchPublicKey
        return self.public_keys[key_id]

    def delete_public_key(self, key_id: str) -> None:
        """
        IfMatch is not yet implemented - deletion always succeeds
        """
        self.public_keys.pop(key_id, None)

    def list_public_keys(self) -> list[PublicKey]:
        """
        Pagination is not yet implemented
        """
        return list(self.public_keys.values())

    def create_key_group(self, name: str, items: list[str]) -> KeyGroup:
        key_group = KeyGroup(name=name, items=items)
        self.key_groups[key_group.id] = key_group
        return key_group

    def get_key_group(self, group_id: str) -> KeyGroup:
        if group_id not in self.key_groups:
            raise NoSuchKeyGroup
        return self.key_groups[group_id]

    def list_key_groups(self) -> list[KeyGroup]:
        """
        Pagination is not yet implemented
        """
        return list(self.key_groups.values())

    def update_key_group(self, group_id: str, name: str, items: list[str]) -> KeyGroup:
        if group_id not in self.key_groups:
            raise NoSuchKeyGroup
        group = self.key_groups[group_id]
        group.update(name, items)
        return group

    def delete_key_group(self, group_id: str) -> None:
        if group_id not in self.key_groups:
            raise NoSuchKeyGroup
        del self.key_groups[group_id]

    # CloudFront Functions
    def create_function(
        self,
        name: str,
        function_code: str,
        function_config: dict[str, Any],
    ) -> CloudFrontFunction:
        for func in self.functions.values():
            if func.name == name:
                raise FunctionAlreadyExists
        func = CloudFrontFunction(
            name=name,
            function_code=function_code,
            function_config=function_config,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.functions[func.name] = func
        return func

    def get_function(self, name: str) -> CloudFrontFunction:
        if name not in self.functions:
            raise NoSuchFunctionExists
        return self.functions[name]

    def describe_function(self, name: str) -> CloudFrontFunction:
        return self.get_function(name)

    def update_function(
        self,
        name: str,
        function_code: str,
        function_config: dict[str, Any],
        if_match: str,
    ) -> CloudFrontFunction:
        func = self.get_function(name)
        func.update(function_code, function_config)
        return func

    def delete_function(self, name: str, if_match: str) -> None:
        if name not in self.functions:
            raise NoSuchFunctionExists
        del self.functions[name]

    def publish_function(self, name: str, if_match: str) -> CloudFrontFunction:
        func = self.get_function(name)
        func.publish()
        return func

    def list_functions(self) -> list[CloudFrontFunction]:
        """
        Pagination is not yet implemented
        """
        return list(self.functions.values())

    # Cache Policies
    def create_cache_policy(self, config: dict[str, Any]) -> CachePolicy:
        policy = CachePolicy(config)
        self.cache_policies[policy.id] = policy
        return policy

    def get_cache_policy(self, policy_id: str) -> CachePolicy:
        if policy_id not in self.cache_policies:
            raise NoSuchCachePolicy
        return self.cache_policies[policy_id]

    def update_cache_policy(
        self, policy_id: str, config: dict[str, Any]
    ) -> CachePolicy:
        policy = self.get_cache_policy(policy_id)
        policy.update(config)
        return policy

    def delete_cache_policy(self, policy_id: str) -> None:
        if policy_id not in self.cache_policies:
            raise NoSuchCachePolicy
        del self.cache_policies[policy_id]

    def list_cache_policies(self) -> list[CachePolicy]:
        """
        Pagination is not yet implemented
        """
        return list(self.cache_policies.values())

    # Response Headers Policies
    def create_response_headers_policy(
        self, config: dict[str, Any]
    ) -> ResponseHeadersPolicy:
        policy = ResponseHeadersPolicy(config)
        self.response_headers_policies[policy.id] = policy
        return policy

    def get_response_headers_policy(self, policy_id: str) -> ResponseHeadersPolicy:
        if policy_id not in self.response_headers_policies:
            raise NoSuchResponseHeadersPolicy
        return self.response_headers_policies[policy_id]

    def update_response_headers_policy(
        self, policy_id: str, config: dict[str, Any]
    ) -> ResponseHeadersPolicy:
        policy = self.get_response_headers_policy(policy_id)
        policy.update(config)
        return policy

    def delete_response_headers_policy(self, policy_id: str) -> None:
        if policy_id not in self.response_headers_policies:
            raise NoSuchResponseHeadersPolicy
        del self.response_headers_policies[policy_id]

    def list_response_headers_policies(self) -> list[ResponseHeadersPolicy]:
        """
        Pagination is not yet implemented
        """
        return list(self.response_headers_policies.values())

    # OAI
    def create_cloud_front_origin_access_identity(
        self, caller_reference: str, comment: str
    ) -> "OriginAccessIdentity":
        oai = OriginAccessIdentity(caller_reference=caller_reference, comment=comment)
        self.origin_access_identities[oai.id] = oai
        return oai

    def get_cloud_front_origin_access_identity(
        self, identity_id: str
    ) -> "OriginAccessIdentity":
        if identity_id not in self.origin_access_identities:
            raise NoSuchCloudFrontOriginAccessIdentity
        return self.origin_access_identities[identity_id]

    def get_cloud_front_origin_access_identity_config(
        self, identity_id: str
    ) -> "OriginAccessIdentity":
        return self.get_cloud_front_origin_access_identity(identity_id)

    def update_cloud_front_origin_access_identity(
        self, identity_id: str, caller_reference: str, comment: str
    ) -> "OriginAccessIdentity":
        oai = self.get_cloud_front_origin_access_identity(identity_id)
        oai.update(caller_reference, comment)
        return oai

    def delete_cloud_front_origin_access_identity(self, identity_id: str) -> None:
        if identity_id not in self.origin_access_identities:
            raise NoSuchCloudFrontOriginAccessIdentity
        del self.origin_access_identities[identity_id]

    def list_cloud_front_origin_access_identities(self) -> list["OriginAccessIdentity"]:
        return list(self.origin_access_identities.values())

    # Streaming
    def create_streaming_distribution(
        self, config: dict[str, Any], tags: list[dict[str, str]] | None = None
    ) -> "StreamingDistribution":
        dist = StreamingDistribution(self.account_id, self.region_name, config)
        self.streaming_distributions[dist.streaming_distribution_id] = dist
        if tags:
            self.tagger.tag_resource(dist.arn, tags)
        return dist

    def get_streaming_distribution(self, dist_id: str) -> "StreamingDistribution":
        if dist_id not in self.streaming_distributions:
            raise NoSuchStreamingDistribution
        d = self.streaming_distributions[dist_id]
        d.advance()
        return d

    def get_streaming_distribution_config(
        self, dist_id: str
    ) -> "StreamingDistribution":
        return self.get_streaming_distribution(dist_id)

    def update_streaming_distribution(
        self, dist_id: str, config: dict[str, Any]
    ) -> "StreamingDistribution":
        d = self.get_streaming_distribution(dist_id)
        d.streaming_distribution_config = StreamingDistributionConfig(config)
        d.advance()
        return d

    def delete_streaming_distribution(self, dist_id: str) -> None:
        if dist_id not in self.streaming_distributions:
            raise NoSuchStreamingDistribution
        del self.streaming_distributions[dist_id]

    def list_streaming_distributions(self) -> list["StreamingDistribution"]:
        for d in self.streaming_distributions.values():
            d.advance()
        return list(self.streaming_distributions.values())

    # Origin Request Policies
    def create_origin_request_policy(
        self, config: dict[str, Any]
    ) -> "OriginRequestPolicy":
        p = OriginRequestPolicy(config)
        self.origin_request_policies[p.id] = p
        return p

    def get_origin_request_policy(self, policy_id: str) -> "OriginRequestPolicy":
        if policy_id not in self.origin_request_policies:
            raise NoSuchOriginRequestPolicy
        return self.origin_request_policies[policy_id]

    def get_origin_request_policy_config(self, policy_id: str) -> "OriginRequestPolicy":
        return self.get_origin_request_policy(policy_id)

    def update_origin_request_policy(
        self, policy_id: str, config: dict[str, Any]
    ) -> "OriginRequestPolicy":
        p = self.get_origin_request_policy(policy_id)
        p.update(config)
        return p

    def delete_origin_request_policy(self, policy_id: str) -> None:
        if policy_id not in self.origin_request_policies:
            raise NoSuchOriginRequestPolicy
        del self.origin_request_policies[policy_id]

    def list_origin_request_policies(self) -> list["OriginRequestPolicy"]:
        return list(self.origin_request_policies.values())

    # FLE Config
    def create_field_level_encryption_config(
        self, config: dict[str, Any]
    ) -> "FieldLevelEncryptionConfig":
        f = FieldLevelEncryptionConfig(config)
        self.field_level_encryption_configs[f.id] = f
        return f

    def get_field_level_encryption(
        self, config_id: str
    ) -> "FieldLevelEncryptionConfig":
        if config_id not in self.field_level_encryption_configs:
            raise NoSuchFieldLevelEncryptionConfig
        return self.field_level_encryption_configs[config_id]

    def get_field_level_encryption_config(
        self, config_id: str
    ) -> "FieldLevelEncryptionConfig":
        return self.get_field_level_encryption(config_id)

    def update_field_level_encryption_config(
        self, config_id: str, config: dict[str, Any]
    ) -> "FieldLevelEncryptionConfig":
        f = self.get_field_level_encryption(config_id)
        f.update(config)
        return f

    def delete_field_level_encryption_config(self, config_id: str) -> None:
        if config_id not in self.field_level_encryption_configs:
            raise NoSuchFieldLevelEncryptionConfig
        del self.field_level_encryption_configs[config_id]

    def list_field_level_encryption_configs(self) -> list["FieldLevelEncryptionConfig"]:
        return list(self.field_level_encryption_configs.values())

    # FLE Profiles
    def create_field_level_encryption_profile(
        self, config: dict[str, Any]
    ) -> "FieldLevelEncryptionProfile":
        p = FieldLevelEncryptionProfile(config)
        self.field_level_encryption_profiles[p.id] = p
        return p

    def get_field_level_encryption_profile(
        self, profile_id: str
    ) -> "FieldLevelEncryptionProfile":
        if profile_id not in self.field_level_encryption_profiles:
            raise NoSuchFieldLevelEncryptionProfile
        return self.field_level_encryption_profiles[profile_id]

    def get_field_level_encryption_profile_config(
        self, profile_id: str
    ) -> "FieldLevelEncryptionProfile":
        return self.get_field_level_encryption_profile(profile_id)

    def update_field_level_encryption_profile(
        self, profile_id: str, config: dict[str, Any]
    ) -> "FieldLevelEncryptionProfile":
        p = self.get_field_level_encryption_profile(profile_id)
        p.update(config)
        return p

    def delete_field_level_encryption_profile(self, profile_id: str) -> None:
        if profile_id not in self.field_level_encryption_profiles:
            raise NoSuchFieldLevelEncryptionProfile
        del self.field_level_encryption_profiles[profile_id]

    def list_field_level_encryption_profiles(
        self,
    ) -> list["FieldLevelEncryptionProfile"]:
        return list(self.field_level_encryption_profiles.values())

    # CDP
    def create_continuous_deployment_policy(
        self, config: dict[str, Any]
    ) -> "ContinuousDeploymentPolicy":
        p = ContinuousDeploymentPolicy(config)
        self.continuous_deployment_policies[p.id] = p
        return p

    def get_continuous_deployment_policy(
        self, policy_id: str
    ) -> "ContinuousDeploymentPolicy":
        if policy_id not in self.continuous_deployment_policies:
            raise NoSuchContinuousDeploymentPolicy
        return self.continuous_deployment_policies[policy_id]

    def get_continuous_deployment_policy_config(
        self, policy_id: str
    ) -> "ContinuousDeploymentPolicy":
        return self.get_continuous_deployment_policy(policy_id)

    def update_continuous_deployment_policy(
        self, policy_id: str, config: dict[str, Any]
    ) -> "ContinuousDeploymentPolicy":
        p = self.get_continuous_deployment_policy(policy_id)
        p.update(config)
        return p

    def delete_continuous_deployment_policy(self, policy_id: str) -> None:
        if policy_id not in self.continuous_deployment_policies:
            raise NoSuchContinuousDeploymentPolicy
        del self.continuous_deployment_policies[policy_id]

    def list_continuous_deployment_policies(self) -> list["ContinuousDeploymentPolicy"]:
        return list(self.continuous_deployment_policies.values())

    # Monitoring
    def create_monitoring_subscription(
        self, distribution_id: str, realtime_metrics_config: dict[str, Any]
    ) -> "MonitoringSubscription":
        if distribution_id not in self.distributions:
            raise NoSuchDistribution
        sub = MonitoringSubscription(distribution_id, realtime_metrics_config)
        self.monitoring_subscriptions[distribution_id] = sub
        return sub

    def get_monitoring_subscription(
        self, distribution_id: str
    ) -> "MonitoringSubscription":
        if distribution_id not in self.monitoring_subscriptions:
            raise NoSuchMonitoringSubscription
        return self.monitoring_subscriptions[distribution_id]

    def delete_monitoring_subscription(self, distribution_id: str) -> None:
        if distribution_id not in self.monitoring_subscriptions:
            raise NoSuchMonitoringSubscription
        del self.monitoring_subscriptions[distribution_id]

    # Realtime Log
    def create_realtime_log_config(
        self,
        name: str,
        sampling_rate: int,
        end_points: list[dict[str, Any]],
        fields: list[str],
    ) -> "RealtimeLogConfig":
        c = RealtimeLogConfig(
            name=name,
            sampling_rate=sampling_rate,
            end_points=end_points,
            fields=fields,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.realtime_log_configs[name] = c
        return c

    def get_realtime_log_config(
        self, name: str | None = None, arn: str | None = None
    ) -> "RealtimeLogConfig":
        if name and name in self.realtime_log_configs:
            return self.realtime_log_configs[name]
        if arn:
            for c in self.realtime_log_configs.values():
                if c.arn == arn:
                    return c
        raise NoSuchRealtimeLogConfig

    def update_realtime_log_config(
        self,
        name: str | None = None,
        arn: str | None = None,
        sampling_rate: int | None = None,
        end_points: list[dict[str, Any]] | None = None,
        fields: list[str] | None = None,
    ) -> "RealtimeLogConfig":
        c = self.get_realtime_log_config(name=name, arn=arn)
        c.update(sampling_rate, end_points, fields)
        return c

    def delete_realtime_log_config(
        self, name: str | None = None, arn: str | None = None
    ) -> None:
        c = self.get_realtime_log_config(name=name, arn=arn)
        del self.realtime_log_configs[c.name]

    def list_realtime_log_configs(self) -> list["RealtimeLogConfig"]:
        return list(self.realtime_log_configs.values())

    # Query ops
    def list_distributions_by_web_acl_id(self, web_acl_id: str) -> list[Distribution]:
        r = []
        [
            r.append(d) or d.advance()
            for d in self.distributions.values()
            if d.distribution_config.web_acl_id == web_acl_id
        ]
        return r

    def list_distributions_by_cache_policy_id(self, cache_policy_id: str) -> list[str]:
        r = []
        for d in self.distributions.values():
            if (
                d.distribution_config.default_cache_behavior.cache_policy_id
                == cache_policy_id
            ):
                r.append(d.distribution_id)
                continue
            for cb in d.distribution_config.cache_behaviors:
                if cb.cache_policy_id == cache_policy_id:
                    r.append(d.distribution_id)
                    break
        return r

    def list_distributions_by_origin_request_policy_id(
        self, policy_id: str
    ) -> list[str]:
        r = []
        for d in self.distributions.values():
            if (
                d.distribution_config.default_cache_behavior.origin_request_policy_id
                == policy_id
            ):
                r.append(d.distribution_id)
                continue
            for cb in d.distribution_config.cache_behaviors:
                if cb.origin_request_policy_id == policy_id:
                    r.append(d.distribution_id)
                    break
        return r

    def list_distributions_by_response_headers_policy_id(
        self, policy_id: str
    ) -> list[str]:
        r = []
        for d in self.distributions.values():
            if (
                d.distribution_config.default_cache_behavior.response_headers_policy_id
                == policy_id
            ):
                r.append(d.distribution_id)
                continue
            for cb in d.distribution_config.cache_behaviors:
                if cb.response_headers_policy_id == policy_id:
                    r.append(d.distribution_id)
                    break
        return r

    def list_distributions_by_key_group(self, key_group_id: str) -> list[str]:
        r = []
        for d in self.distributions.values():
            if (
                key_group_id
                in d.distribution_config.default_cache_behavior.trusted_key_groups.group_ids
            ):
                r.append(d.distribution_id)
                continue
            for cb in d.distribution_config.cache_behaviors:
                if key_group_id in cb.trusted_key_groups.group_ids:
                    r.append(d.distribution_id)
                    break
        return r

    def list_distributions_by_realtime_log_config(self, arn: str) -> list[Distribution]:
        r = []
        for d in self.distributions.values():
            if (
                d.distribution_config.default_cache_behavior.realtime_log_config_arn
                == arn
            ):
                d.advance()
                r.append(d)
                continue
            for cb in d.distribution_config.cache_behaviors:
                if cb.realtime_log_config_arn == arn:
                    d.advance()
                    r.append(d)
                    break
        return r

    # Config-only getters
    def get_cache_policy_config(self, policy_id: str) -> CachePolicy:
        return self.get_cache_policy(policy_id)

    def get_key_group_config(self, group_id: str) -> KeyGroup:
        if group_id not in self.key_groups:
            raise NoSuchKeyGroup
        return self.key_groups[group_id]

    def get_origin_access_control_config(self, control_id: str) -> OriginAccessControl:
        return self.get_origin_access_control(control_id)

    def get_public_key_config(self, key_id: str) -> PublicKey:
        if key_id not in self.public_keys:
            raise NoSuchPublicKey
        return self.public_keys[key_id]

    def get_response_headers_policy_config(
        self, policy_id: str
    ) -> ResponseHeadersPolicy:
        return self.get_response_headers_policy(policy_id)

    def update_public_key(self, key_id: str) -> PublicKey:
        if key_id not in self.public_keys:
            raise NoSuchPublicKey
        k = self.public_keys[key_id]
        k.etag = random_id(length=14)
        return k

    def associate_alias(self, distribution_id: str, alias: str) -> None:
        d, _ = self.get_distribution(distribution_id)
        if alias not in d.distribution_config.aliases:
            d.distribution_config.aliases.append(alias)

    def test_function(
        self, name: str, event_object: str, stage: str | None = None
    ) -> dict[str, Any]:
        self.get_function(name)
        return {
            "FunctionSummary": {"Name": name, "Status": "UNASSOCIATED"},
            "FunctionExecutionLogs": [],
            "FunctionErrorMessage": "",
            "FunctionOutput": '{"response":{"statusCode":200}}',
            "ComputeUtilization": "12",
        }

    def list_conflicting_aliases(
        self, distribution_id: str, alias: str
    ) -> list[dict[str, str]]:
        r: list[dict[str, str]] = []
        for d in self.distributions.values():
            if d.distribution_id == distribution_id:
                continue
            for a in d.distribution_config.aliases:
                if alias in a or a in alias:
                    r.append(
                        {
                            "Alias": a,
                            "DistributionId": d.distribution_id,
                            "AccountId": self.account_id,
                        }
                    )
        return r

    # Anycast IP Lists
    def create_anycast_ip_list(self, name: str) -> AnycastIpList:
        aip = AnycastIpList(name=name, account_id=self.account_id)
        self.anycast_ip_lists[aip.id] = aip
        return aip

    def get_anycast_ip_list(self, list_id: str) -> AnycastIpList:
        if list_id not in self.anycast_ip_lists:
            raise NoSuchResource(f"The anycast IP list {list_id} does not exist.")
        return self.anycast_ip_lists[list_id]

    def delete_anycast_ip_list(self, list_id: str) -> None:
        self.anycast_ip_lists.pop(list_id, None)

    def list_anycast_ip_lists(self) -> list[AnycastIpList]:
        return list(self.anycast_ip_lists.values())

    # VPC Origins
    def create_vpc_origin(self, config: dict[str, Any]) -> VpcOrigin:
        vo = VpcOrigin(config=config, account_id=self.account_id)
        self.vpc_origins[vo.id] = vo
        return vo

    def get_vpc_origin(self, vpc_origin_id: str) -> VpcOrigin:
        if vpc_origin_id not in self.vpc_origins:
            raise NoSuchResource(f"The VPC origin {vpc_origin_id} does not exist.")
        return self.vpc_origins[vpc_origin_id]

    def update_vpc_origin(
        self, vpc_origin_id: str, config: dict[str, Any]
    ) -> VpcOrigin:
        vo = self.get_vpc_origin(vpc_origin_id)
        vo.update(config)
        return vo

    def delete_vpc_origin(self, vpc_origin_id: str) -> None:
        self.vpc_origins.pop(vpc_origin_id, None)

    def list_vpc_origins(self) -> list[VpcOrigin]:
        return list(self.vpc_origins.values())

    # Key Value Stores
    def create_key_value_store(self, name: str, comment: str = "") -> KeyValueStore:
        kvs = KeyValueStore(name=name, comment=comment, account_id=self.account_id)
        self.key_value_stores[name] = kvs
        return kvs

    def describe_key_value_store(self, name: str) -> KeyValueStore:
        if name not in self.key_value_stores:
            raise NoSuchResource(f"The key value store {name} does not exist.")
        return self.key_value_stores[name]

    def update_key_value_store(self, name: str, comment: str = "") -> KeyValueStore:
        kvs = self.describe_key_value_store(name)
        kvs.update(comment)
        return kvs

    def delete_key_value_store(self, name: str) -> None:
        self.key_value_stores.pop(name, None)

    def list_key_value_stores(self) -> list[KeyValueStore]:
        return list(self.key_value_stores.values())


cloudfront_backends = BackendDict(
    CloudFrontBackend,
    "cloudfront",
    use_boto3_regions=False,
    additional_regions=PARTITION_NAMES,
)
