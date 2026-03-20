from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.utils import utcnow
from moto.moto_api._internal import mock_random as random
from moto.utilities.utils import get_partition

from .exceptions import (
    InvalidParameterException,
    InvalidRequestException,
    ResourceInUseException,
    ResourceNotFoundException,
)
from .utils import validate_role_arn

# String Templates
CLUSTER_ARN_TEMPLATE = "arn:{partition}:eks:{region}:{account_id}:cluster/{name}"
FARGATE_PROFILE_ARN_TEMPLATE = "arn:{partition}:eks:{region}:{account_id}:fargateprofile/{cluster_name}/{fargate_profile_name}/{uuid}"
NODEGROUP_ARN_TEMPLATE = "arn:{partition}:eks:{region}:{account_id}:nodegroup/{cluster_name}/{nodegroup_name}/{uuid}"
ADDON_ARN_TEMPLATE = (
    "arn:{partition}:eks:{region}:{account_id}:addon/{cluster_name}/{addon_name}/{uuid}"
)
ACCESS_ENTRY_ARN_TEMPLATE = "arn:{partition}:eks:{region}:{account_id}:access-entry/{cluster_name}/{principal_arn_suffix}/{uuid}"
POD_IDENTITY_ASSOCIATION_ARN_TEMPLATE = "arn:{partition}:eks:{region}:{account_id}:podidentityassociation/{cluster_name}/{uuid}"
IDENTITY_PROVIDER_CONFIG_ARN_TEMPLATE = "arn:{partition}:eks:{region}:{account_id}:identityproviderconfig/{cluster_name}/oidc/{config_name}/{uuid}"
INSIGHT_ARN_TEMPLATE = (
    "arn:{partition}:eks:{region}:{account_id}:insight/{cluster_name}/{insight_id}"
)
EKS_ANYWHERE_SUBSCRIPTION_ARN_TEMPLATE = (
    "arn:{partition}:eks:{region}:{account_id}:eks-anywhere-subscription/{uuid}"
)
CAPABILITY_ARN_TEMPLATE = "arn:{partition}:eks:{region}:{account_id}:capability/{cluster_name}/{capability_name}/{uuid}"
ISSUER_TEMPLATE = (
    "https://oidc.eks.{region}.amazonaws.com/id/" + random.get_random_string(length=10)
)
ENDPOINT_TEMPLATE = (
    "https://"
    + random.get_random_string()
    + "."
    + random.get_random_string(3)
    + ".{region}.eks.amazonaws.com/"
)

# Defaults used for creating a Cluster
DEFAULT_KUBERNETES_NETWORK_CONFIG = {"serviceIpv4Cidr": "172.20.0.0/16"}
DEFAULT_KUBERNETES_VERSION = "1.19"
DEFAULT_LOGGING = {
    "clusterLogging": [
        {
            "types": [
                "api",
                "audit",
                "authenticator",
                "controllerManager",
                "scheduler",
            ],
            "enabled": False,
        }
    ]
}
DEFAULT_PLATFORM_VERSION = "eks.4"
ACTIVE_STATUS = "ACTIVE"

# Defaults used for creating a Managed Nodegroup
DEFAULT_AMI_TYPE = "AL2_x86_64"
DEFAULT_CAPACITY_TYPE = "ON_DEMAND"
DEFAULT_DISK_SIZE = "20"
DEFAULT_INSTANCE_TYPES = ["t3.medium"]
DEFAULT_NODEGROUP_HEALTH: dict[str, Any] = {"issues": []}
DEFAULT_RELEASE_VERSION = "1.19.8-20210414"
DEFAULT_REMOTE_ACCESS = {"ec2SshKey": "eksKeypair"}
DEFAULT_SCALING_CONFIG = {"minSize": 2, "maxSize": 2, "desiredSize": 2}

# Exception messages, also imported into testing.
# Obtained through cURL responses from the actual APIs.
CLUSTER_IN_USE_MSG = "Cluster has nodegroups attached"
CLUSTER_EXISTS_MSG = "Cluster already exists with name: {clusterName}"
CLUSTER_NOT_FOUND_MSG = "No cluster found for name: {clusterName}."
CLUSTER_NOT_READY_MSG = "Cluster '{clusterName}' is not in ACTIVE status"
FARGATE_PROFILE_EXISTS_MSG = (
    "A Fargate Profile already exists with this name in this cluster."
)
FARGATE_PROFILE_NEEDS_SELECTOR_MSG = "Fargate Profile requires at least one selector."
FARGATE_PROFILE_NOT_FOUND_MSG = (
    "No Fargate Profile found with name: {fargateProfileName}."
)
FARGATE_PROFILE_SELECTOR_NEEDS_NAMESPACE = (
    "Fargate Profile must have at least one selector with at least one namespace value."
)
FARGATE_PROFILE_TOO_MANY_LABELS = (
    "Request contains Selector with more than 5 Label pairs"
)
LAUNCH_TEMPLATE_WITH_DISK_SIZE_MSG = (
    "Disk size must be specified within the launch template."
)
LAUNCH_TEMPLATE_WITH_REMOTE_ACCESS_MSG = (
    "Remote access configuration cannot be specified with a launch template."
)
NODEGROUP_EXISTS_MSG = (
    "NodeGroup already exists with name {nodegroupName} and cluster name {clusterName}"
)
NODEGROUP_NOT_FOUND_MSG = "No node group found for name: {nodegroupName}."
ADDON_EXISTS_MSG = (
    "Addon already exists with name {addonName} and cluster name {clusterName}"
)
ADDON_NOT_FOUND_MSG = "No addon found for name: {addonName}."
ACCESS_ENTRY_EXISTS_MSG = (
    "Access entry already exists for principal {principalArn} in cluster {clusterName}"
)
ACCESS_ENTRY_NOT_FOUND_MSG = "No access entry found for principal: {principalArn}."
POD_IDENTITY_ASSOCIATION_NOT_FOUND_MSG = (
    "No pod identity association found for id: {associationId}."
)
IDENTITY_PROVIDER_CONFIG_NOT_FOUND_MSG = (
    "No identity provider config found for name: {configName}."
)
IDENTITY_PROVIDER_CONFIG_EXISTS_MSG = "Identity provider config already exists with name {configName} and cluster name {clusterName}"
INSIGHT_NOT_FOUND_MSG = "No insight found for id: {insightId}."
INSIGHTS_REFRESH_NOT_FOUND_MSG = (
    "No insights refresh operation found for cluster: {clusterName}."
)
EKS_ANYWHERE_SUBSCRIPTION_NOT_FOUND_MSG = (
    "No EKS Anywhere subscription found for id: {subscriptionId}."
)
CAPABILITY_NOT_FOUND_MSG = "No capability found for name: {capabilityName}."
CAPABILITY_EXISTS_MSG = "Capability already exists with name {capabilityName} and cluster name {clusterName}"


class Cluster:
    def __init__(
        self,
        name: str,
        role_arn: str,
        resources_vpc_config: dict[str, Any],
        account_id: str,
        region_name: str,
        aws_partition: str,
        version: Optional[str] = None,
        kubernetes_network_config: Optional[dict[str, str]] = None,
        logging: Optional[dict[str, Any]] = None,
        client_request_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        encryption_config: Optional[list[dict[str, Any]]] = None,
        remote_network_config: Optional[dict[str, list[dict[str, list[str]]]]] = None,
    ):
        if encryption_config is None:
            encryption_config = []
        if tags is None:
            tags = {}

        self.nodegroups: dict[str, Nodegroup] = {}
        self.nodegroup_count = 0

        self.fargate_profiles: dict[str, FargateProfile] = {}
        self.fargate_profile_count = 0

        self.addons: dict[str, Addon] = {}
        self.access_entries: dict[str, AccessEntry] = {}
        self.pod_identity_associations: dict[str, PodIdentityAssociation] = {}
        self.identity_provider_configs: dict[str, IdentityProviderConfig] = {}
        self.capabilities: dict[str, Capability] = {}

        self.arn = CLUSTER_ARN_TEMPLATE.format(
            partition=aws_partition,
            account_id=account_id,
            region=region_name,
            name=name,
        )
        self.certificate_authority = {"data": random.get_random_string(1400)}
        self.created_at = utcnow()
        self.identity = {"oidc": {"issuer": ISSUER_TEMPLATE.format(region=region_name)}}
        self.endpoint = ENDPOINT_TEMPLATE.format(region=region_name)

        self.kubernetes_network_config = (
            kubernetes_network_config or DEFAULT_KUBERNETES_NETWORK_CONFIG
        )
        self.logging = logging or DEFAULT_LOGGING
        self.platformVersion = DEFAULT_PLATFORM_VERSION
        self.status = ACTIVE_STATUS
        self.version = version or DEFAULT_KUBERNETES_VERSION

        self.client_request_token = client_request_token
        self.encryption_config = encryption_config
        self.name = name
        self.resources_vpc_config = resources_vpc_config
        self.role_arn = role_arn
        self.tags = tags
        self.remote_network_config = remote_network_config

    @property
    def is_active(self) -> bool:
        return self.status == "ACTIVE"


class FargateProfile:
    def __init__(
        self,
        cluster_name: str,
        fargate_profile_name: str,
        pod_execution_role_arn: str,
        selectors: list[dict[str, Any]],
        account_id: str,
        region_name: str,
        aws_partition: str,
        client_request_token: Optional[str] = None,
        subnets: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        if subnets is None:
            subnets = []
        if tags is None:
            tags = {}

        self.created_at = utcnow()
        self.uuid = str(random.uuid4())
        self.fargate_profile_arn = FARGATE_PROFILE_ARN_TEMPLATE.format(
            partition=aws_partition,
            account_id=account_id,
            region=region_name,
            cluster_name=cluster_name,
            fargate_profile_name=fargate_profile_name,
            uuid=self.uuid,
        )

        self.status = ACTIVE_STATUS
        self.cluster_name = cluster_name
        self.fargate_profile_name = fargate_profile_name
        self.pod_execution_role_arn = pod_execution_role_arn
        self.client_request_token = client_request_token
        self.selectors = selectors
        self.subnets = subnets
        self.tags = tags


class Nodegroup:
    def __init__(
        self,
        cluster_name: str,
        node_role: str,
        nodegroup_name: str,
        subnets: list[str],
        account_id: str,
        region_name: str,
        aws_partition: str,
        scaling_config: Optional[dict[str, int]] = None,
        disk_size: Optional[int] = None,
        instance_types: Optional[list[str]] = None,
        ami_type: Optional[str] = None,
        remote_access: Optional[dict[str, Any]] = None,
        labels: Optional[dict[str, str]] = None,
        taints: Optional[list[dict[str, str]]] = None,
        tags: Optional[dict[str, str]] = None,
        client_request_token: Optional[str] = None,
        launch_template: Optional[dict[str, str]] = None,
        capacity_type: Optional[str] = None,
        version: Optional[str] = None,
        release_version: Optional[str] = None,
        update_config: Optional[dict[str, Any]] = None,
        node_repair_config: Optional[dict[str, Any]] = None,
    ):
        if tags is None:
            tags = {}
        if labels is None:
            labels = {}
        if taints is None:
            taints = []

        self.uuid = str(random.uuid4())
        self.arn = NODEGROUP_ARN_TEMPLATE.format(
            partition=aws_partition,
            account_id=account_id,
            region=region_name,
            cluster_name=cluster_name,
            nodegroup_name=nodegroup_name,
            uuid=self.uuid,
        )
        self.created_at = utcnow()
        self.modified_at = utcnow()
        self.health = DEFAULT_NODEGROUP_HEALTH
        self.resources = {
            "autoScalingGroups": [{"name": "eks-" + self.uuid}],
            "remoteAccessSecurityGroup": "sg-" + random.get_random_string(17).lower(),
        }

        self.ami_type = ami_type or DEFAULT_AMI_TYPE
        self.capacity_type = capacity_type or DEFAULT_CAPACITY_TYPE
        self.disk_size = disk_size or DEFAULT_DISK_SIZE
        self.instance_types = instance_types or DEFAULT_INSTANCE_TYPES
        self.release_version = release_version or DEFAULT_RELEASE_VERSION
        self.remote_access = remote_access or DEFAULT_REMOTE_ACCESS
        self.scaling_config = scaling_config or DEFAULT_SCALING_CONFIG
        self.status = ACTIVE_STATUS
        self.version = version or DEFAULT_KUBERNETES_VERSION

        self.client_request_token = client_request_token
        self.cluster_name = cluster_name
        self.labels = labels
        self.launch_template = launch_template
        self.node_role = node_role
        self.nodegroup_name = nodegroup_name
        self.partition = aws_partition
        self.region = region_name
        self.subnets = subnets
        self.tags = tags
        self.taints = taints
        self.update_config = update_config
        self.node_repair_config = node_repair_config

        # Determine LaunchTemplateId from Name (and vice versa)
        try:
            from moto.ec2.models import ec2_backends

            ec2 = ec2_backends[account_id][region_name]

            template = None
            if "name" in self.launch_template:  # type: ignore
                name = self.launch_template["name"]  # type: ignore
                template = ec2.describe_launch_templates(template_names=[name])[0]
            elif "id" in self.launch_template:  # type: ignore
                _id = self.launch_template["id"]  # type: ignore
                template = ec2.describe_launch_templates(template_ids=[_id])[0]

            self.launch_template["id"] = template.id  # type: ignore
            self.launch_template["name"] = template.name  # type: ignore
        except:  # noqa: E722 Do not use bare except
            pass


class Addon:
    def __init__(
        self,
        cluster_name: str,
        addon_name: str,
        account_id: str,
        region_name: str,
        aws_partition: str,
        addon_version: Optional[str] = None,
        service_account_role_arn: Optional[str] = None,
        resolve_conflicts: Optional[str] = None,
        client_request_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        configuration_values: Optional[str] = None,
    ):
        if tags is None:
            tags = {}

        self.uuid = str(random.uuid4())
        self.addon_arn = ADDON_ARN_TEMPLATE.format(
            partition=aws_partition,
            account_id=account_id,
            region=region_name,
            cluster_name=cluster_name,
            addon_name=addon_name,
            uuid=self.uuid,
        )
        self.created_at = utcnow()
        self.modified_at = utcnow()
        self.status = ACTIVE_STATUS
        self.health = {"issues": []}

        self.addon_name = addon_name
        self.cluster_name = cluster_name
        self.addon_version = addon_version or "v1.0.0-eksbuild.1"
        self.service_account_role_arn = service_account_role_arn
        self.resolve_conflicts = resolve_conflicts
        self.client_request_token = client_request_token
        self.tags = tags
        self.configuration_values = configuration_values


class AccessEntry:
    def __init__(
        self,
        cluster_name: str,
        principal_arn: str,
        account_id: str,
        region_name: str,
        aws_partition: str,
        kubernetes_groups: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
        client_request_token: Optional[str] = None,
        username: Optional[str] = None,
        entry_type: Optional[str] = None,
    ):
        if tags is None:
            tags = {}
        if kubernetes_groups is None:
            kubernetes_groups = []

        self.uuid = str(random.uuid4())
        # Extract the suffix from the principal ARN for the access entry ARN
        principal_suffix = (
            principal_arn.rsplit("/", 1)[-1] if "/" in principal_arn else principal_arn
        )
        self.access_entry_arn = ACCESS_ENTRY_ARN_TEMPLATE.format(
            partition=aws_partition,
            account_id=account_id,
            region=region_name,
            cluster_name=cluster_name,
            principal_arn_suffix=principal_suffix,
            uuid=self.uuid,
        )
        self.created_at = utcnow()
        self.modified_at = utcnow()

        self.cluster_name = cluster_name
        self.principal_arn = principal_arn
        self.kubernetes_groups = kubernetes_groups
        self.tags = tags
        self.username = username or ""
        self.type = entry_type or "STANDARD"
        self.access_policies: dict[str, dict[str, Any]] = {}


class PodIdentityAssociation:
    def __init__(
        self,
        cluster_name: str,
        namespace: str,
        service_account: str,
        role_arn: str,
        account_id: str,
        region_name: str,
        aws_partition: str,
        client_request_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        if tags is None:
            tags = {}

        self.uuid = str(random.uuid4())
        self.association_id = "a-" + random.get_random_string(length=12).lower()
        self.association_arn = POD_IDENTITY_ASSOCIATION_ARN_TEMPLATE.format(
            partition=aws_partition,
            account_id=account_id,
            region=region_name,
            cluster_name=cluster_name,
            uuid=self.uuid,
        )
        self.created_at = utcnow()
        self.modified_at = utcnow()

        self.cluster_name = cluster_name
        self.namespace = namespace
        self.service_account = service_account
        self.role_arn = role_arn
        self.tags = tags
        self.owner_arn = None


class IdentityProviderConfig:
    def __init__(
        self,
        cluster_name: str,
        config_name: str,
        issuer_url: str,
        client_id: str,
        account_id: str,
        region_name: str,
        aws_partition: str,
        groups_claim: Optional[str] = None,
        groups_prefix: Optional[str] = None,
        required_claims: Optional[dict[str, str]] = None,
        username_claim: Optional[str] = None,
        username_prefix: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        if tags is None:
            tags = {}

        self.uuid = str(random.uuid4())
        self.identity_provider_config_arn = (
            IDENTITY_PROVIDER_CONFIG_ARN_TEMPLATE.format(
                partition=aws_partition,
                account_id=account_id,
                region=region_name,
                cluster_name=cluster_name,
                config_name=config_name,
                uuid=self.uuid,
            )
        )
        self.created_at = utcnow()

        self.cluster_name = cluster_name
        self.config_name = config_name
        self.issuer_url = issuer_url
        self.client_id = client_id
        self.groups_claim = groups_claim
        self.groups_prefix = groups_prefix
        self.required_claims = required_claims or {}
        self.username_claim = username_claim
        self.username_prefix = username_prefix
        self.tags = tags
        self.status = ACTIVE_STATUS
        self.config_type = "oidc"


class EksAnywhereSubscription:
    def __init__(
        self,
        account_id: str,
        region_name: str,
        aws_partition: str,
        name: Optional[str] = None,
        term: Optional[dict[str, Any]] = None,
        auto_renew: bool = True,
        license_quantity: Optional[int] = None,
        license_type: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        if tags is None:
            tags = {}

        self.uuid = str(random.uuid4())
        self.id = self.uuid
        self.arn = EKS_ANYWHERE_SUBSCRIPTION_ARN_TEMPLATE.format(
            partition=aws_partition,
            account_id=account_id,
            region=region_name,
            uuid=self.uuid,
        )
        self.created_at = utcnow()

        self.name = name or f"subscription-{self.uuid[:8]}"
        self.term = term or {"duration": 12, "unit": "MONTHS"}
        self.auto_renew = auto_renew
        self.license_quantity = license_quantity or 1
        self.license_type = license_type or "Cluster"
        self.tags = tags
        self.status = ACTIVE_STATUS
        self.effective_date = self.created_at
        self.expiration_date = None


class Capability:
    def __init__(
        self,
        cluster_name: str,
        capability_name: str,
        account_id: str,
        region_name: str,
        aws_partition: str,
        capability_type: Optional[str] = None,
        role_arn: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
        delete_propagation_policy: Optional[str] = None,
    ):
        if tags is None:
            tags = {}

        self.uuid = str(random.uuid4())
        self.arn = CAPABILITY_ARN_TEMPLATE.format(
            partition=aws_partition,
            account_id=account_id,
            region=region_name,
            cluster_name=cluster_name,
            capability_name=capability_name,
            uuid=self.uuid,
        )
        self.created_at = utcnow()
        self.modified_at = utcnow()

        self.cluster_name = cluster_name
        self.capability_name = capability_name
        self.type = capability_type or "STANDARD"
        self.role_arn = role_arn or ""
        self.configuration = configuration or {}
        self.tags = tags
        self.status = ACTIVE_STATUS
        self.delete_propagation_policy = delete_propagation_policy or "DELETE"


class EKSBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.clusters: dict[str, Cluster] = {}
        self.cluster_count = 0
        self.partition = get_partition(region_name)
        self.eks_anywhere_subscriptions: dict[str, EksAnywhereSubscription] = {}
        # insights_refreshes: cluster_name -> list of refresh records (newest first)
        self.insights_refreshes: dict[str, list[dict[str, Any]]] = {}

    def create_cluster(
        self,
        name: str,
        role_arn: str,
        resources_vpc_config: dict[str, Any],
        version: Optional[str] = None,
        kubernetes_network_config: Optional[dict[str, str]] = None,
        logging: Optional[dict[str, Any]] = None,
        client_request_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        encryption_config: Optional[list[dict[str, Any]]] = None,
        remote_network_config: Optional[dict[str, list[dict[str, list[str]]]]] = None,
    ) -> Cluster:
        if name in self.clusters:
            # Cluster exists.
            raise ResourceInUseException(
                clusterName=name,
                nodegroupName=None,
                addonName=None,
                message=CLUSTER_EXISTS_MSG.format(clusterName=name),
            )
        validate_role_arn(role_arn)

        cluster = Cluster(
            name=name,
            role_arn=role_arn,
            resources_vpc_config=resources_vpc_config,
            version=version,
            kubernetes_network_config=kubernetes_network_config,
            logging=logging,
            client_request_token=client_request_token,
            tags=tags,
            encryption_config=encryption_config,
            remote_network_config=remote_network_config,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )
        self.clusters[name] = cluster
        self.cluster_count += 1
        return cluster

    def create_fargate_profile(
        self,
        fargate_profile_name: str,
        cluster_name: str,
        selectors: list[dict[str, Any]],
        pod_execution_role_arn: str,
        subnets: Optional[list[str]] = None,
        client_request_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> FargateProfile:
        try:
            # Cluster exists.
            cluster = self.clusters[cluster_name]
        except KeyError:
            # Cluster does not exist.
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        if fargate_profile_name in cluster.fargate_profiles:
            # Fargate Profile already exists.
            raise ResourceInUseException(
                clusterName=None,
                nodegroupName=None,
                addonName=None,
                message=FARGATE_PROFILE_EXISTS_MSG,
            )
        if not cluster.is_active:
            raise InvalidRequestException(
                message=CLUSTER_NOT_READY_MSG.format(clusterName=cluster_name)
            )

        _validate_fargate_profile_selectors(selectors)

        fargate_profile = FargateProfile(
            cluster_name=cluster_name,
            fargate_profile_name=fargate_profile_name,
            pod_execution_role_arn=pod_execution_role_arn,
            client_request_token=client_request_token,
            selectors=selectors,
            subnets=subnets,
            tags=tags,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )

        cluster.fargate_profiles[fargate_profile_name] = fargate_profile
        cluster.fargate_profile_count += 1
        return fargate_profile

    def create_nodegroup(
        self,
        cluster_name: str,
        node_role: str,
        nodegroup_name: str,
        subnets: list[str],
        scaling_config: Optional[dict[str, int]] = None,
        disk_size: Optional[int] = None,
        instance_types: Optional[list[str]] = None,
        ami_type: Optional[str] = None,
        remote_access: Optional[dict[str, Any]] = None,
        labels: Optional[dict[str, str]] = None,
        taints: Optional[list[dict[str, str]]] = None,
        tags: Optional[dict[str, str]] = None,
        client_request_token: Optional[str] = None,
        launch_template: Optional[dict[str, str]] = None,
        capacity_type: Optional[str] = None,
        version: Optional[str] = None,
        release_version: Optional[str] = None,
    ) -> Nodegroup:
        try:
            # Cluster exists.
            cluster = self.clusters[cluster_name]
        except KeyError:
            # Cluster does not exist.
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        if nodegroup_name in cluster.nodegroups:
            # Nodegroup already exists.
            raise ResourceInUseException(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                addonName=None,
                message=NODEGROUP_EXISTS_MSG.format(
                    nodegroupName=nodegroup_name, clusterName=cluster_name
                ),
            )
        if not cluster.is_active:
            raise InvalidRequestException(
                message=CLUSTER_NOT_READY_MSG.format(clusterName=cluster_name)
            )
        if launch_template:
            validate_launch_template_combination(disk_size, remote_access)
        validate_role_arn(node_role)

        nodegroup = Nodegroup(
            cluster_name=cluster_name,
            node_role=node_role,
            nodegroup_name=nodegroup_name,
            subnets=subnets,
            scaling_config=scaling_config,
            disk_size=disk_size,
            instance_types=instance_types,
            ami_type=ami_type,
            remote_access=remote_access,
            labels=labels,
            taints=taints,
            tags=tags,
            client_request_token=client_request_token,
            launch_template=launch_template,
            capacity_type=capacity_type,
            version=version,
            release_version=release_version,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )

        cluster.nodegroups[nodegroup_name] = nodegroup
        cluster.nodegroup_count += 1
        return nodegroup

    def describe_cluster(self, name: str) -> Cluster:
        try:
            # Cluster exists.
            return self.clusters[name]
        except KeyError:
            # Cluster does not exist.
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=name),
            )

    def describe_fargate_profile(
        self, cluster_name: str, fargate_profile_name: str
    ) -> FargateProfile:
        try:
            # Cluster exists.
            cluster = self.clusters[cluster_name]
        except KeyError:
            # Cluster does not exist.
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            # Fargate Profile exists.
            return cluster.fargate_profiles[fargate_profile_name]
        except KeyError:
            # Fargate Profile does not exist.
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=FARGATE_PROFILE_NOT_FOUND_MSG.format(
                    fargateProfileName=fargate_profile_name
                ),
            )

    def describe_nodegroup(self, cluster_name: str, nodegroup_name: str) -> Nodegroup:
        try:
            # Cluster exists.
            cluster = self.clusters[cluster_name]
        except KeyError:
            # Cluster does not exist.
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            # Nodegroup exists.
            return cluster.nodegroups[nodegroup_name]
        except KeyError:
            # Nodegroup does not exist.
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                fargateProfileName=None,
                addonName=None,
                message=NODEGROUP_NOT_FOUND_MSG.format(nodegroupName=nodegroup_name),
            )

    def delete_cluster(self, name: str) -> Cluster:
        try:
            # Cluster exists.
            validate_safe_to_delete(self.clusters[name])
        except KeyError:
            # Cluster does not exist.
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=name),
            )

        result = self.clusters.pop(name)
        self.cluster_count -= 1
        return result

    def delete_fargate_profile(
        self, cluster_name: str, fargate_profile_name: str
    ) -> FargateProfile:
        try:
            # Cluster exists.
            cluster = self.clusters[cluster_name]
        except KeyError:
            # Cluster does not exist.
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            # Fargate Profile exists.
            deleted_fargate_profile = cluster.fargate_profiles.pop(fargate_profile_name)
        except KeyError:
            # Fargate Profile does not exist.
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=fargate_profile_name,
                addonName=None,
                message=FARGATE_PROFILE_NOT_FOUND_MSG.format(
                    fargateProfileName=fargate_profile_name
                ),
            )

        cluster.fargate_profile_count -= 1
        return deleted_fargate_profile

    def delete_nodegroup(self, cluster_name: str, nodegroup_name: str) -> Nodegroup:
        try:
            # Cluster exists.
            cluster = self.clusters[cluster_name]
        except KeyError:
            # Cluster does not exist.
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            # Nodegroup exists.
            result = cluster.nodegroups.pop(nodegroup_name)
        except KeyError:
            # Nodegroup does not exist.
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                fargateProfileName=None,
                addonName=None,
                message=NODEGROUP_NOT_FOUND_MSG.format(nodegroupName=nodegroup_name),
            )

        cluster.nodegroup_count -= 1
        return result

    # --- Addon CRUD ---

    def create_addon(
        self,
        cluster_name: str,
        addon_name: str,
        addon_version: Optional[str] = None,
        service_account_role_arn: Optional[str] = None,
        resolve_conflicts: Optional[str] = None,
        client_request_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        configuration_values: Optional[str] = None,
    ) -> Addon:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        if addon_name in cluster.addons:
            raise ResourceInUseException(
                clusterName=cluster_name,
                nodegroupName=None,
                addonName=addon_name,
                message=ADDON_EXISTS_MSG.format(
                    addonName=addon_name, clusterName=cluster_name
                ),
            )

        addon = Addon(
            cluster_name=cluster_name,
            addon_name=addon_name,
            addon_version=addon_version,
            service_account_role_arn=service_account_role_arn,
            resolve_conflicts=resolve_conflicts,
            client_request_token=client_request_token,
            tags=tags,
            configuration_values=configuration_values,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )

        cluster.addons[addon_name] = addon
        return addon

    def describe_addon(self, cluster_name: str, addon_name: str) -> Addon:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            return cluster.addons[addon_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=addon_name,
                message=ADDON_NOT_FOUND_MSG.format(addonName=addon_name),
            )

    def delete_addon(self, cluster_name: str, addon_name: str) -> Addon:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            addon = cluster.addons.pop(addon_name)
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=addon_name,
                message=ADDON_NOT_FOUND_MSG.format(addonName=addon_name),
            )
        addon.status = "DELETING"
        return addon

    def list_addons(
        self, cluster_name: str, max_results: int, next_token: Optional[str]
    ) -> tuple[list[str], Optional[str]]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        return paginated_list(list(cluster.addons.keys()), max_results, next_token)

    def describe_addon_versions(
        self,
        kubernetes_version: Optional[str] = None,
        addon_name: Optional[str] = None,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        # Return a static list of well-known addon versions
        all_addons = [
            {
                "addonName": "vpc-cni",
                "type": "networking",
                "addonVersions": [
                    {
                        "addonVersion": "v1.12.0-eksbuild.1",
                        "architecture": ["amd64", "arm64"],
                        "compatibilities": [
                            {
                                "clusterVersion": "1.27",
                                "platformVersions": ["*"],
                                "defaultVersion": True,
                            }
                        ],
                    }
                ],
                "publisher": "eks",
                "owner": "aws",
            },
            {
                "addonName": "coredns",
                "type": "networking",
                "addonVersions": [
                    {
                        "addonVersion": "v1.9.3-eksbuild.2",
                        "architecture": ["amd64", "arm64"],
                        "compatibilities": [
                            {
                                "clusterVersion": "1.27",
                                "platformVersions": ["*"],
                                "defaultVersion": True,
                            }
                        ],
                    }
                ],
                "publisher": "eks",
                "owner": "aws",
            },
            {
                "addonName": "kube-proxy",
                "type": "networking",
                "addonVersions": [
                    {
                        "addonVersion": "v1.27.1-eksbuild.1",
                        "architecture": ["amd64", "arm64"],
                        "compatibilities": [
                            {
                                "clusterVersion": "1.27",
                                "platformVersions": ["*"],
                                "defaultVersion": True,
                            }
                        ],
                    }
                ],
                "publisher": "eks",
                "owner": "aws",
            },
            {
                "addonName": "aws-ebs-csi-driver",
                "type": "storage",
                "addonVersions": [
                    {
                        "addonVersion": "v1.19.0-eksbuild.1",
                        "architecture": ["amd64", "arm64"],
                        "compatibilities": [
                            {
                                "clusterVersion": "1.27",
                                "platformVersions": ["*"],
                                "defaultVersion": True,
                            }
                        ],
                    }
                ],
                "publisher": "eks",
                "owner": "aws",
            },
        ]

        # Filter by addon_name if provided
        if addon_name:
            all_addons = [a for a in all_addons if a["addonName"] == addon_name]

        return {"addons": all_addons, "nextToken": None}

    # --- Access Entry CRUD ---

    def create_access_entry(
        self,
        cluster_name: str,
        principal_arn: str,
        kubernetes_groups: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
        client_request_token: Optional[str] = None,
        username: Optional[str] = None,
        entry_type: Optional[str] = None,
    ) -> AccessEntry:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        if principal_arn in cluster.access_entries:
            raise ResourceInUseException(
                clusterName=cluster_name,
                nodegroupName=None,
                addonName=None,
                message=ACCESS_ENTRY_EXISTS_MSG.format(
                    principalArn=principal_arn, clusterName=cluster_name
                ),
            )

        access_entry = AccessEntry(
            cluster_name=cluster_name,
            principal_arn=principal_arn,
            kubernetes_groups=kubernetes_groups,
            tags=tags,
            client_request_token=client_request_token,
            username=username,
            entry_type=entry_type,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )

        cluster.access_entries[principal_arn] = access_entry
        return access_entry

    def describe_access_entry(
        self, cluster_name: str, principal_arn: str
    ) -> AccessEntry:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            return cluster.access_entries[principal_arn]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=ACCESS_ENTRY_NOT_FOUND_MSG.format(principalArn=principal_arn),
            )

    def delete_access_entry(self, cluster_name: str, principal_arn: str) -> AccessEntry:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            return cluster.access_entries.pop(principal_arn)
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=ACCESS_ENTRY_NOT_FOUND_MSG.format(principalArn=principal_arn),
            )

    def list_access_entries(
        self, cluster_name: str, max_results: int, next_token: Optional[str]
    ) -> tuple[list[str], Optional[str]]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        return paginated_list(
            list(cluster.access_entries.keys()), max_results, next_token
        )

    # --- Access Policy ---

    def associate_access_policy(
        self,
        cluster_name: str,
        principal_arn: str,
        policy_arn: str,
        access_scope: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            access_entry = cluster.access_entries[principal_arn]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=ACCESS_ENTRY_NOT_FOUND_MSG.format(principalArn=principal_arn),
            )

        now = utcnow()
        associated_policy = {
            "policyArn": policy_arn,
            "accessScope": access_scope,
            "associatedAt": now,
            "modifiedAt": now,
        }
        access_entry.access_policies[policy_arn] = associated_policy
        return {
            "clusterName": cluster_name,
            "principalArn": principal_arn,
            "associatedAccessPolicy": associated_policy,
        }

    def disassociate_access_policy(
        self,
        cluster_name: str,
        principal_arn: str,
        policy_arn: str,
    ) -> None:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            access_entry = cluster.access_entries[principal_arn]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=ACCESS_ENTRY_NOT_FOUND_MSG.format(principalArn=principal_arn),
            )

        if policy_arn not in access_entry.access_policies:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=f"No associated access policy found for ARN: {policy_arn}.",
            )
        del access_entry.access_policies[policy_arn]

    # --- Pod Identity Association CRUD ---

    def create_pod_identity_association(
        self,
        cluster_name: str,
        namespace: str,
        service_account: str,
        role_arn: str,
        client_request_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> PodIdentityAssociation:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        association = PodIdentityAssociation(
            cluster_name=cluster_name,
            namespace=namespace,
            service_account=service_account,
            role_arn=role_arn,
            client_request_token=client_request_token,
            tags=tags,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )

        cluster.pod_identity_associations[association.association_id] = association
        return association

    def describe_pod_identity_association(
        self, cluster_name: str, association_id: str
    ) -> PodIdentityAssociation:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            return cluster.pod_identity_associations[association_id]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=POD_IDENTITY_ASSOCIATION_NOT_FOUND_MSG.format(
                    associationId=association_id
                ),
            )

    def delete_pod_identity_association(
        self, cluster_name: str, association_id: str
    ) -> PodIdentityAssociation:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            return cluster.pod_identity_associations.pop(association_id)
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=POD_IDENTITY_ASSOCIATION_NOT_FOUND_MSG.format(
                    associationId=association_id
                ),
            )

    def list_pod_identity_associations(
        self,
        cluster_name: str,
        namespace: Optional[str] = None,
        service_account: Optional[str] = None,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        associations = list(cluster.pod_identity_associations.values())

        # Filter by namespace/service_account if provided
        if namespace:
            associations = [a for a in associations if a.namespace == namespace]
        if service_account:
            associations = [
                a for a in associations if a.service_account == service_account
            ]

        # Return summary list
        summary = [
            {
                "clusterName": a.cluster_name,
                "namespace": a.namespace,
                "serviceAccount": a.service_account,
                "associationArn": a.association_arn,
                "associationId": a.association_id,
                "ownerArn": a.owner_arn,
            }
            for a in associations
        ]

        return {"associations": summary, "nextToken": None}

    # --- Update Access Entry ---

    def update_access_entry(
        self,
        cluster_name: str,
        principal_arn: str,
        kubernetes_groups: Optional[list[str]] = None,
        username: Optional[str] = None,
    ) -> "AccessEntry":
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            access_entry = cluster.access_entries[principal_arn]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=ACCESS_ENTRY_NOT_FOUND_MSG.format(principalArn=principal_arn),
            )

        if kubernetes_groups is not None:
            access_entry.kubernetes_groups = kubernetes_groups
        if username is not None:
            access_entry.username = username
        access_entry.modified_at = utcnow()
        return access_entry

    def list_associated_access_policies(
        self,
        cluster_name: str,
        principal_arn: str,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            access_entry = cluster.access_entries[principal_arn]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=ACCESS_ENTRY_NOT_FOUND_MSG.format(principalArn=principal_arn),
            )

        policies = list(access_entry.access_policies.values())
        return {
            "clusterName": cluster_name,
            "principalArn": principal_arn,
            "associatedAccessPolicies": policies,
            "nextToken": None,
        }

    # --- Update Addon ---

    def update_addon(
        self,
        cluster_name: str,
        addon_name: str,
        addon_version: Optional[str] = None,
        service_account_role_arn: Optional[str] = None,
        resolve_conflicts: Optional[str] = None,
        client_request_token: Optional[str] = None,
        configuration_values: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            addon = cluster.addons[addon_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=addon_name,
                message=ADDON_NOT_FOUND_MSG.format(addonName=addon_name),
            )

        if addon_version is not None:
            addon.addon_version = addon_version
        if service_account_role_arn is not None:
            addon.service_account_role_arn = service_account_role_arn
        if resolve_conflicts is not None:
            addon.resolve_conflicts = resolve_conflicts
        if configuration_values is not None:
            addon.configuration_values = configuration_values
        addon.modified_at = utcnow()

        params = []
        if addon_version:
            params.append({"type": "AddonVersion", "value": addon_version})
        if service_account_role_arn:
            params.append(
                {
                    "type": "ServiceAccountRoleArn",
                    "value": service_account_role_arn,
                }
            )
        if configuration_values:
            params.append(
                {"type": "ConfigurationValues", "value": configuration_values}
            )

        return {
            "id": str(random.uuid4()),
            "status": "Successful",
            "type": "AddonUpdate",
            "params": params,
            "createdAt": utcnow(),
            "errors": [],
        }

    # --- Update Cluster Version ---

    def update_cluster_version(
        self,
        name: str,
        version: str,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=name),
            )

        cluster.version = version

        return {
            "id": str(random.uuid4()),
            "status": "Successful",
            "type": "VersionUpdate",
            "params": [
                {"type": "Version", "value": version},
                {"type": "PlatformVersion", "value": cluster.platformVersion},
            ],
            "createdAt": utcnow(),
            "errors": [],
        }

    # --- Associate Encryption Config ---

    def associate_encryption_config(
        self,
        cluster_name: str,
        encryption_config: list[dict[str, Any]],
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        cluster.encryption_config.extend(encryption_config)

        return {
            "id": str(random.uuid4()),
            "status": "Successful",
            "type": "AssociateEncryptionConfig",
            "params": [{"type": "EncryptionConfig", "value": str(encryption_config)}],
            "createdAt": utcnow(),
            "errors": [],
        }

    # --- Identity Provider Config CRUD ---

    def associate_identity_provider_config(
        self,
        cluster_name: str,
        oidc: dict[str, Any],
        tags: Optional[dict[str, str]] = None,
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        config_name = oidc.get("identityProviderConfigName", "")
        if config_name in cluster.identity_provider_configs:
            raise ResourceInUseException(
                clusterName=cluster_name,
                nodegroupName=None,
                addonName=None,
                message=IDENTITY_PROVIDER_CONFIG_EXISTS_MSG.format(
                    configName=config_name, clusterName=cluster_name
                ),
            )

        config = IdentityProviderConfig(
            cluster_name=cluster_name,
            config_name=config_name,
            issuer_url=oidc.get("issuerUrl", ""),
            client_id=oidc.get("clientId", ""),
            groups_claim=oidc.get("groupsClaim"),
            groups_prefix=oidc.get("groupsPrefix"),
            required_claims=oidc.get("requiredClaims"),
            username_claim=oidc.get("usernameClaim"),
            username_prefix=oidc.get("usernamePrefix"),
            tags=tags,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )
        cluster.identity_provider_configs[config_name] = config

        return {
            "id": str(random.uuid4()),
            "status": "Successful",
            "type": "AssociateIdentityProviderConfig",
            "params": [{"type": "IdentityProviderConfig", "value": str(oidc)}],
            "createdAt": utcnow(),
            "errors": [],
        }

    def describe_identity_provider_config(
        self,
        cluster_name: str,
        identity_provider_config: dict[str, str],
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        config_name = identity_provider_config.get("name", "")
        try:
            config = cluster.identity_provider_configs[config_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=IDENTITY_PROVIDER_CONFIG_NOT_FOUND_MSG.format(
                    configName=config_name
                ),
            )

        return {
            "identityProviderConfig": {
                "oidc": {
                    "identityProviderConfigName": config.config_name,
                    "identityProviderConfigArn": config.identity_provider_config_arn,
                    "clusterName": config.cluster_name,
                    "issuerUrl": config.issuer_url,
                    "clientId": config.client_id,
                    "usernameClaim": config.username_claim,
                    "usernamePrefix": config.username_prefix,
                    "groupsClaim": config.groups_claim,
                    "groupsPrefix": config.groups_prefix,
                    "requiredClaims": config.required_claims,
                    "tags": config.tags,
                    "status": {"status": config.status},
                },
            },
        }

    def disassociate_identity_provider_config(
        self,
        cluster_name: str,
        identity_provider_config: dict[str, str],
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        config_name = identity_provider_config.get("name", "")
        try:
            cluster.identity_provider_configs.pop(config_name)
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=IDENTITY_PROVIDER_CONFIG_NOT_FOUND_MSG.format(
                    configName=config_name
                ),
            )

        return {
            "id": str(random.uuid4()),
            "status": "Successful",
            "type": "DisassociateIdentityProviderConfig",
            "params": [],
            "createdAt": utcnow(),
            "errors": [],
        }

    def list_identity_provider_configs(
        self,
        cluster_name: str,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        configs = [
            {
                "type": "oidc",
                "name": config.config_name,
            }
            for config in cluster.identity_provider_configs.values()
        ]
        return {"identityProviderConfigs": configs, "nextToken": None}

    # --- Insights ---

    def describe_insight(
        self,
        cluster_name: str,
        insight_id: str,
    ) -> dict[str, Any]:
        try:
            self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        # Insights are read-only AWS-generated items; return a mock insight
        raise ResourceNotFoundException(
            clusterName=cluster_name,
            nodegroupName=None,
            fargateProfileName=None,
            addonName=None,
            message=INSIGHT_NOT_FOUND_MSG.format(insightId=insight_id),
        )

    def list_insights(
        self,
        cluster_name: str,
        filter_param: Optional[dict[str, Any]] = None,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        # Insights are AWS-generated; return empty list
        return {"insights": [], "nextToken": None}

    def start_insights_refresh(
        self,
        cluster_name: str,
        insight_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        try:
            self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        refresh_id = str(random.uuid4())
        now = utcnow()
        record = {
            "id": refresh_id,
            "status": "COMPLETED",
            "message": "Insights refresh completed successfully.",
            "startedAt": now,
            "endedAt": now,
        }
        if cluster_name not in self.insights_refreshes:
            self.insights_refreshes[cluster_name] = []
        self.insights_refreshes[cluster_name].insert(0, record)
        return {
            "status": record["status"],
            "message": record["message"],
        }

    def describe_insights_refresh(self, cluster_name: str) -> dict[str, Any]:
        try:
            self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        refreshes = self.insights_refreshes.get(cluster_name, [])
        if not refreshes:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=INSIGHTS_REFRESH_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        record = refreshes[0]
        return {
            "status": record["status"],
            "message": record["message"],
            "startedAt": record["startedAt"],
            "endedAt": record["endedAt"],
        }

    # --- Access Policies (global) ---

    def list_access_policies(
        self,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        # Return a static list of well-known EKS access policies
        policies = [
            {
                "name": "AmazonEKSClusterAdminPolicy",
                "arn": "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy",
            },
            {
                "name": "AmazonEKSAdminPolicy",
                "arn": "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy",
            },
            {
                "name": "AmazonEKSEditPolicy",
                "arn": "arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy",
            },
            {
                "name": "AmazonEKSViewPolicy",
                "arn": "arn:aws:eks::aws:cluster-access-policy/AmazonEKSViewPolicy",
            },
            {
                "name": "AmazonEKSAdminViewPolicy",
                "arn": "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminViewPolicy",
            },
        ]
        return {"accessPolicies": policies, "nextToken": None}

    # --- Describe Addon Configuration ---

    def describe_addon_configuration(
        self,
        addon_name: str,
        addon_version: str,
    ) -> dict[str, Any]:
        return {
            "addonName": addon_name,
            "addonVersion": addon_version,
            "configurationSchema": "{}",
            "podIdentityConfiguration": [],
        }

    # --- Describe Cluster Versions ---

    def describe_cluster_versions(
        self,
        cluster_type: Optional[str] = None,
        max_results: int = 100,
        next_token: Optional[str] = None,
        default_only: bool = False,
        include_all: bool = False,
        cluster_versions_only: Optional[list[str]] = None,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        versions = [
            {
                "clusterVersion": "1.31",
                "clusterType": "eks",
                "defaultPlatformVersion": "eks.14",
                "defaultVersion": True,
                "releaseDate": utcnow(),
                "endOfStandardSupportDate": None,
                "endOfExtendedSupportDate": None,
                "status": "standard-support",
            },
            {
                "clusterVersion": "1.30",
                "clusterType": "eks",
                "defaultPlatformVersion": "eks.18",
                "defaultVersion": False,
                "releaseDate": utcnow(),
                "endOfStandardSupportDate": None,
                "endOfExtendedSupportDate": None,
                "status": "standard-support",
            },
            {
                "clusterVersion": "1.29",
                "clusterType": "eks",
                "defaultPlatformVersion": "eks.19",
                "defaultVersion": False,
                "releaseDate": utcnow(),
                "endOfStandardSupportDate": None,
                "endOfExtendedSupportDate": None,
                "status": "standard-support",
            },
            {
                "clusterVersion": "1.28",
                "clusterType": "eks",
                "defaultPlatformVersion": "eks.22",
                "defaultVersion": False,
                "releaseDate": utcnow(),
                "endOfStandardSupportDate": None,
                "endOfExtendedSupportDate": None,
                "status": "extended-support",
            },
            {
                "clusterVersion": "1.27",
                "clusterType": "eks",
                "defaultPlatformVersion": "eks.24",
                "defaultVersion": False,
                "releaseDate": utcnow(),
                "endOfStandardSupportDate": None,
                "endOfExtendedSupportDate": None,
                "status": "extended-support",
            },
        ]

        if cluster_versions_only:
            versions = [
                v for v in versions if v["clusterVersion"] in cluster_versions_only
            ]
        if default_only:
            versions = [v for v in versions if v["defaultVersion"]]
        if status:
            versions = [v for v in versions if v["status"] == status]

        return {"clusterVersions": versions, "nextToken": None}

    # --- Deregister Cluster ---

    def deregister_cluster(self, name: str) -> "Cluster":
        try:
            self.clusters[name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=name),
            )

        result = self.clusters.pop(name)
        self.cluster_count -= 1
        result.status = "DELETING"
        return result

    # --- EKS Anywhere Subscriptions CRUD ---

    def create_eks_anywhere_subscription(
        self,
        name: Optional[str] = None,
        term: Optional[dict[str, Any]] = None,
        auto_renew: bool = True,
        license_quantity: Optional[int] = None,
        license_type: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        client_request_token: Optional[str] = None,
    ) -> "EksAnywhereSubscription":
        subscription = EksAnywhereSubscription(
            name=name,
            term=term,
            auto_renew=auto_renew,
            license_quantity=license_quantity,
            license_type=license_type,
            tags=tags,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )
        self.eks_anywhere_subscriptions[subscription.id] = subscription
        return subscription

    def describe_eks_anywhere_subscription(
        self, subscription_id: str
    ) -> "EksAnywhereSubscription":
        try:
            return self.eks_anywhere_subscriptions[subscription_id]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=EKS_ANYWHERE_SUBSCRIPTION_NOT_FOUND_MSG.format(
                    subscriptionId=subscription_id
                ),
            )

    def delete_eks_anywhere_subscription(
        self, subscription_id: str
    ) -> "EksAnywhereSubscription":
        try:
            subscription = self.eks_anywhere_subscriptions.pop(subscription_id)
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=EKS_ANYWHERE_SUBSCRIPTION_NOT_FOUND_MSG.format(
                    subscriptionId=subscription_id
                ),
            )
        subscription.status = "DELETING"
        return subscription

    def list_eks_anywhere_subscriptions(
        self,
        max_results: int = 100,
        next_token: Optional[str] = None,
        include_status: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        subscriptions = list(self.eks_anywhere_subscriptions.values())
        if include_status:
            subscriptions = [s for s in subscriptions if s.status in include_status]

        results = [
            {
                "id": s.id,
                "arn": s.arn,
                "createdAt": s.created_at,
                "effectiveDate": s.effective_date,
                "expirationDate": s.expiration_date,
                "licenseQuantity": s.license_quantity,
                "licenseType": s.license_type,
                "term": s.term,
                "status": s.status,
                "autoRenew": s.auto_renew,
                "tags": s.tags,
            }
            for s in subscriptions
        ]
        return {"subscriptions": results, "nextToken": None}

    def update_eks_anywhere_subscription(
        self,
        subscription_id: str,
        auto_renew: bool = True,
        client_request_token: Optional[str] = None,
    ) -> "EksAnywhereSubscription":
        try:
            subscription = self.eks_anywhere_subscriptions[subscription_id]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=EKS_ANYWHERE_SUBSCRIPTION_NOT_FOUND_MSG.format(
                    subscriptionId=subscription_id
                ),
            )

        subscription.auto_renew = auto_renew
        return subscription

    # --- Capability CRUD ---

    def create_capability(
        self,
        cluster_name: str,
        capability_name: str,
        capability_type: Optional[str] = None,
        role_arn: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
        client_request_token: Optional[str] = None,
        delete_propagation_policy: Optional[str] = None,
    ) -> "Capability":
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        if capability_name in cluster.capabilities:
            raise ResourceInUseException(
                clusterName=cluster_name,
                nodegroupName=None,
                addonName=None,
                message=CAPABILITY_EXISTS_MSG.format(
                    capabilityName=capability_name, clusterName=cluster_name
                ),
            )

        capability = Capability(
            cluster_name=cluster_name,
            capability_name=capability_name,
            capability_type=capability_type,
            role_arn=role_arn,
            configuration=configuration,
            tags=tags,
            delete_propagation_policy=delete_propagation_policy,
            account_id=self.account_id,
            region_name=self.region_name,
            aws_partition=self.partition,
        )
        cluster.capabilities[capability_name] = capability
        return capability

    def describe_capability(
        self, cluster_name: str, capability_name: str
    ) -> "Capability":
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            return cluster.capabilities[capability_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CAPABILITY_NOT_FOUND_MSG.format(capabilityName=capability_name),
            )

    def delete_capability(
        self, cluster_name: str, capability_name: str
    ) -> "Capability":
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            capability = cluster.capabilities.pop(capability_name)
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CAPABILITY_NOT_FOUND_MSG.format(capabilityName=capability_name),
            )
        capability.status = "DELETING"
        return capability

    def list_capabilities(
        self,
        cluster_name: str,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        capabilities = [
            {
                "capabilityName": cap.capability_name,
                "capabilityArn": cap.arn,
                "status": cap.status,
                "type": cap.type,
            }
            for cap in cluster.capabilities.values()
        ]
        return {"capabilities": capabilities, "nextToken": None}

    def update_capability(
        self,
        cluster_name: str,
        capability_name: str,
        role_arn: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        client_request_token: Optional[str] = None,
        delete_propagation_policy: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            capability = cluster.capabilities[capability_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CAPABILITY_NOT_FOUND_MSG.format(capabilityName=capability_name),
            )

        if role_arn is not None:
            capability.role_arn = role_arn
        if configuration is not None:
            capability.configuration = configuration
        if delete_propagation_policy is not None:
            capability.delete_propagation_policy = delete_propagation_policy
        capability.modified_at = utcnow()

        params = []
        if role_arn:
            params.append({"type": "RoleArn", "value": role_arn})
        if configuration:
            params.append({"type": "Configuration", "value": str(configuration)})

        return {
            "id": str(random.uuid4()),
            "status": "Successful",
            "type": "CapabilityUpdate",
            "params": params,
            "createdAt": utcnow(),
            "errors": [],
        }

    # --- Tagging ---

    def _find_resource_by_arn(self, resource_arn: str) -> Any:
        """Find any EKS resource by ARN (cluster, nodegroup, addon, etc)."""
        # Check clusters
        for cluster in self.clusters.values():
            if cluster.arn == resource_arn:
                return cluster
            # Check nodegroups
            for ng in cluster.nodegroups.values():
                if ng.arn == resource_arn:
                    return ng
            # Check fargate profiles
            for fp in cluster.fargate_profiles.values():
                if fp.fargate_profile_arn == resource_arn:
                    return fp
            # Check addons
            for addon in cluster.addons.values():
                if addon.addon_arn == resource_arn:
                    return addon
            # Check access entries
            for ae in cluster.access_entries.values():
                if ae.access_entry_arn == resource_arn:
                    return ae
            # Check pod identity associations
            for pia in cluster.pod_identity_associations.values():
                if pia.association_arn == resource_arn:
                    return pia
            # Check identity provider configs
            for ipc in cluster.identity_provider_configs.values():
                if ipc.identity_provider_config_arn == resource_arn:
                    return ipc
            # Check capabilities
            for cap in cluster.capabilities.values():
                if cap.arn == resource_arn:
                    return cap
        # Check EKS Anywhere subscriptions
        for sub in self.eks_anywhere_subscriptions.values():
            if sub.arn == resource_arn:
                return sub
        return None

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        resource = self._find_resource_by_arn(resource_arn)
        if resource is None:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message="An error occurred (NotFoundException) when calling the TagResource operation: Resource was not found",
            )
        resource.tags.update(tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        if not isinstance(tag_keys, list):
            tag_keys = [tag_keys]

        resource = self._find_resource_by_arn(resource_arn)
        if resource is None:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message="An error occurred (NotFoundException) when calling the UntagResource operation: Resource was not found",
            )
        for name in tag_keys:
            if name in resource.tags:
                del resource.tags[name]

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        resource = self._find_resource_by_arn(resource_arn)
        if resource is None:
            raise ResourceNotFoundException(
                clusterName=None,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message="An error occurred (NotFoundException) when calling the ListTagsForResource operation: Resource was not found",
            )
        return resource.tags

    def list_clusters(
        self, max_results: int, next_token: Optional[str]
    ) -> tuple[list[Cluster], Optional[Cluster]]:
        return paginated_list(list(self.clusters.keys()), max_results, next_token)

    def list_fargate_profiles(
        self, cluster_name: str, max_results: int, next_token: Optional[str]
    ) -> tuple[list[FargateProfile], Optional[FargateProfile]]:
        cluster = self.clusters[cluster_name]
        return paginated_list(
            list(cluster.fargate_profiles.keys()), max_results, next_token
        )

    def list_nodegroups(
        self, cluster_name: str, max_results: int, next_token: Optional[str]
    ) -> tuple[list[Nodegroup], Optional[Nodegroup]]:
        cluster = self.clusters[cluster_name]
        return paginated_list(list(cluster.nodegroups.keys()), max_results, next_token)

    def update_cluster_config(
        self,
        name: str,
        resources_vpc_config: dict[str, Any],
        logging: Optional[dict[str, Any]] = None,
        client_request_token: Optional[str] = None,
        kubernetes_network_config: Optional[dict[str, str]] = None,
        remote_network_config: Optional[dict[str, list[dict[str, list[str]]]]] = None,
    ) -> Cluster:
        cluster = self.clusters.get(name)
        if cluster:
            if resources_vpc_config:
                self.clusters[name].resources_vpc_config = resources_vpc_config
            if logging:
                self.clusters[name].logging = logging
            if client_request_token:
                self.clusters[name].client_request_token = client_request_token
            if kubernetes_network_config:
                self.clusters[
                    name
                ].kubernetes_network_config = kubernetes_network_config
            if remote_network_config:
                self.clusters[name].remote_network_config = remote_network_config
            return cluster
        raise ResourceNotFoundException(
            clusterName=name,
            nodegroupName=None,
            fargateProfileName=None,
            addonName=None,
            message=CLUSTER_NOT_FOUND_MSG.format(clusterName=name),
        )

    def update_nodegroup_config(
        self,
        cluster_name: str,
        nodegroup_name: str,
        labels: Optional[dict[str, Any]] = None,
        taints: Optional[dict[str, Any]] = None,
        scaling_config: Optional[dict[str, int]] = None,
        update_config: Optional[dict[str, Any]] = None,
        node_repair_config: Optional[dict[str, Any]] = None,
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        # Validate cluster exists
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )

        # Validate nodegroup exists
        try:
            nodegroup = cluster.nodegroups[nodegroup_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                fargateProfileName=None,
                addonName=None,
                message=NODEGROUP_NOT_FOUND_MSG.format(nodegroupName=nodegroup_name),
            )

        # Update labels
        if labels:
            if "addOrUpdateLabels" in labels:
                nodegroup.labels.update(labels["addOrUpdateLabels"])
            if "removeLabels" in labels:
                for key in labels["removeLabels"]:
                    nodegroup.labels.pop(key, None)

        # Update taints
        if taints:
            if "addOrUpdateTaints" in taints:
                for new_taint in taints["addOrUpdateTaints"]:
                    # Remove existing taint with same key+effect, then add new one
                    nodegroup.taints = [
                        t
                        for t in nodegroup.taints
                        if not (
                            t["key"] == new_taint["key"]
                            and t.get("effect") == new_taint.get("effect")
                        )
                    ]
                    nodegroup.taints.append(new_taint)
            if "removeTaints" in taints:
                for taint_to_remove in taints["removeTaints"]:
                    nodegroup.taints = [
                        t
                        for t in nodegroup.taints
                        if not (
                            t["key"] == taint_to_remove["key"]
                            and t.get("effect") == taint_to_remove.get("effect")
                        )
                    ]

        # Update scaling config
        if scaling_config:
            nodegroup.scaling_config.update(scaling_config)

        # Update update_config
        if update_config:
            nodegroup.update_config = update_config

        # Update node_repair_config
        if node_repair_config:
            nodegroup.node_repair_config = node_repair_config

        # Update modified timestamp
        nodegroup.modified_at = utcnow()

        # Build params list for response
        params = []
        if labels:
            params.append({"type": "Labels", "value": str(labels)})
        if taints:
            params.append({"type": "Taints", "value": str(taints)})
        if scaling_config:
            params.append({"type": "ScalingConfig", "value": str(scaling_config)})
        if update_config:
            params.append({"type": "UpdateConfig", "value": str(update_config)})
        if node_repair_config:
            params.append(
                {"type": "NodeRepairConfig", "value": str(node_repair_config)}
            )

        # Return update object (not nodegroup)
        return {
            "id": str(random.uuid4()),
            "status": "Successful",
            "type": "ConfigUpdate",
            "params": params,
            "createdAt": utcnow(),
            "errors": [],
        }


    def update_nodegroup_version(
        self,
        cluster_name: str,
        nodegroup_name: str,
        version: Optional[str] = None,
        release_version: Optional[str] = None,
        launch_template: Optional[dict[str, Any]] = None,
        force: bool = False,
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        import uuid as _uuid
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        try:
            nodegroup = cluster.nodegroups[nodegroup_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                fargateProfileName=None,
                addonName=None,
                message=NODEGROUP_NOT_FOUND_MSG.format(nodegroupName=nodegroup_name),
            )
        if version:
            nodegroup.version = version
        return {
            "id": str(_uuid.uuid4()),
            "status": "Successful",
            "type": "VersionUpdate",
            "params": [{"type": "Version", "value": version or ""}],
            "createdAt": utcnow(),
            "errors": [],
        }

    def update_pod_identity_association(
        self,
        cluster_name: str,
        association_id: str,
        role_arn: Optional[str] = None,
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        try:
            cluster = self.clusters[cluster_name]
        except KeyError:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=CLUSTER_NOT_FOUND_MSG.format(clusterName=cluster_name),
            )
        if association_id not in cluster.pod_identity_associations:
            raise ResourceNotFoundException(
                clusterName=cluster_name,
                nodegroupName=None,
                fargateProfileName=None,
                addonName=None,
                message=f"No pod identity association found for associationId: {association_id}",
            )
        assoc = cluster.pod_identity_associations[association_id]
        if role_arn:
            assoc.role_arn = role_arn
        assoc.modified_at = utcnow()
        return {"association": assoc}

    def register_cluster(
        self,
        name: str,
        connector_config: dict[str, Any],
        client_request_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        import uuid as _uuid
        cluster_arn = (
            f"arn:aws:eks:{self.region_name}:{self.account_id}:cluster/{name}"
        )
        cluster_data = {
            "name": name,
            "arn": cluster_arn,
            "status": "ACTIVE",
            "connectorConfig": connector_config,
            "tags": tags or {},
        }
        return {"cluster": cluster_data}

    def list_updates(
        self,
        cluster_name: str,
        nodegroup_name: Optional[str] = None,
        addon_name: Optional[str] = None,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        return {"updateIds": [], "nextToken": None}

    def describe_update(
        self,
        cluster_name: str,
        update_id: str,
        nodegroup_name: Optional[str] = None,
        addon_name: Optional[str] = None,
    ) -> dict[str, Any]:
        import uuid as _uuid
        return {
            "update": {
                "id": update_id,
                "status": "Successful",
                "type": "ConfigUpdate",
                "params": [],
                "createdAt": utcnow(),
                "errors": [],
            }
        }


def paginated_list(
    full_list: list[Any], max_results: int, next_token: Optional[str]
) -> tuple[list[Any], Optional[Any]]:
    """
    Returns a tuple containing a slice of the full list
    starting at next_token and ending with at most the
    max_results number of elements, and the new
    next_token which can be passed back in for the next
    segment of the full list.
    """
    sorted_list = sorted(full_list)
    list_len = len(sorted_list)

    start = sorted_list.index(next_token) if next_token else 0
    end = min(start + max_results, list_len)
    new_next = None if end == list_len else sorted_list[end]

    return sorted_list[start:end], new_next


def validate_safe_to_delete(cluster: Cluster) -> None:
    # A cluster which has nodegroups attached can not be deleted.
    if cluster.nodegroup_count:
        nodegroup_names = ",".join(list(cluster.nodegroups.keys()))
        raise ResourceInUseException(
            clusterName=cluster.name,
            nodegroupName=nodegroup_names,
            addonName=None,
            message=CLUSTER_IN_USE_MSG,
        )


def validate_launch_template_combination(
    disk_size: Optional[int], remote_access: Optional[dict[str, Any]]
) -> None:
    if not (disk_size or remote_access):
        return

    raise InvalidParameterException(
        message=LAUNCH_TEMPLATE_WITH_DISK_SIZE_MSG
        if disk_size
        else LAUNCH_TEMPLATE_WITH_REMOTE_ACCESS_MSG
    )


def _validate_fargate_profile_selectors(selectors: list[dict[str, Any]]) -> None:
    def raise_exception(message: str) -> None:
        raise InvalidParameterException(
            clusterName=None,
            nodegroupName=None,
            fargateProfileName=None,
            addonName=None,
            message=message,
        )

    # At least one Selector must exist
    if not selectors:
        raise_exception(message=FARGATE_PROFILE_NEEDS_SELECTOR_MSG)

    for selector in selectors:
        # Every existing Selector must have a namespace
        if "namespace" not in selector:
            raise_exception(message=FARGATE_PROFILE_SELECTOR_NEEDS_NAMESPACE)
        # If a selector has labels, it can not have more than 5
        if len(selector.get("labels", {})) > 5:
            raise_exception(message=FARGATE_PROFILE_TOO_MANY_LABELS)


eks_backends = BackendDict(EKSBackend, "eks")
