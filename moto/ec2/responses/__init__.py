from .account_attributes import AccountAttributes
from .amis import AmisResponse
from .availability_zones_and_regions import AvailabilityZonesAndRegions
from .capacity_block import CapacityBlockResponse
from .capacity_reservations import CapacityReservations
from .carrier_gateways import CarrierGateway
from .client_vpn_endpoints import ClientVpnEndpoints
from .coip import CoipResponse
from .customer_gateways import CustomerGateways
from .declarative_policies import DeclarativePoliciesResponse
from .dhcp_options import DHCPOptions
from .egress_only_internet_gateways import EgressOnlyInternetGateway
from .elastic_block_store import ElasticBlockStore
from .elastic_ip_addresses import ElasticIPAddresses
from .elastic_network_interfaces import ElasticNetworkInterfaces
from .fast_launch import FastLaunchResponse
from .fleets import Fleets
from .flow_logs import FlowLogs
from .gap_stubs import GapStubs
from .general import General
from .host_reservation import HostReservationResponse
from .hosts import HostsResponse
from .iam_instance_profiles import IamInstanceProfiles
from .instance_connect_endpoint import InstanceConnectEndpointResponse
from .instance_event_window import InstanceEventWindowResponse
from .instance_metadata_defaults import InstanceMetadataDefaultsResponse
from .instances import InstanceResponse
from .internet_gateways import InternetGateways
from .ipam import IpamResponse
from .key_pairs import KeyPairs
from .launch_templates import LaunchTemplates
from .local_gateways import LocalGatewayResponse
from .monitoring import Monitoring
from .nat_gateways import NatGateways
from .network_acls import NetworkACLs
from .network_insights import NetworkInsightsResponse
from .network_insights_access_scope import NetworkInsightsAccessScopeResponse
from .public_ipv4_pool import PublicIpv4PoolResponse
from .replace_root_volume_task import ReplaceRootVolumeTaskResponse
from .reserved_instances import ReservedInstances
from .route_tables import RouteTables
from .security_group_vpc_association import SecurityGroupVpcAssociationResponse
from .security_groups import SecurityGroups
from .settings import Settings
from .snapshot_block_public_access import SnapshotBlockPublicAccessResponse
from .spot_datafeed import SpotDatafeedResponse
from .spot_fleets import SpotFleets
from .spot_instances import SpotInstances
from .store_image_task import StoreImageTaskResponse
from .subnets import Subnets
from .tags import TagResponse
from .traffic_mirror import TrafficMirrorResponse
from .transit_gateway_attachments import TransitGatewayAttachment
from .transit_gateway_connect import TransitGatewayConnectResponse
from .transit_gateway_route_tables import TransitGatewayRouteTable
from .transit_gateways import TransitGateways
from .verified_access import VerifiedAccessResponse
from .virtual_private_gateways import VirtualPrivateGateways
from .volume_attribute import VolumeAttributeResponse
from .vpc_peering_connections import VPCPeeringConnections
from .vpc_service_configuration import VPCEndpointServiceConfiguration
from .vpcs import VPCs
from .vpn_connections import VPNConnections
from .windows import Windows


class EC2Response(
    ClientVpnEndpoints,
    IpamResponse,
    TransitGatewayConnectResponse,
    NetworkInsightsResponse,
    VerifiedAccessResponse,
    InstanceConnectEndpointResponse,
    CapacityReservations,
    TrafficMirrorResponse,
    FastLaunchResponse,
    LocalGatewayResponse,
    CoipResponse,
    HostReservationResponse,
    PublicIpv4PoolResponse,
    InstanceEventWindowResponse,
    NetworkInsightsAccessScopeResponse,
    SnapshotBlockPublicAccessResponse,
    SecurityGroupVpcAssociationResponse,
    SpotDatafeedResponse,
    InstanceMetadataDefaultsResponse,
    VolumeAttributeResponse,
    ReplaceRootVolumeTaskResponse,
    StoreImageTaskResponse,
    DeclarativePoliciesResponse,
    CapacityBlockResponse,
    GapStubs,
    AccountAttributes,
    AmisResponse,
    AvailabilityZonesAndRegions,
    CustomerGateways,
    DHCPOptions,
    ElasticBlockStore,
    ElasticIPAddresses,
    ElasticNetworkInterfaces,
    Fleets,
    General,
    HostsResponse,
    InstanceResponse,
    InternetGateways,
    EgressOnlyInternetGateway,
    KeyPairs,
    LaunchTemplates,
    Monitoring,
    NetworkACLs,
    ReservedInstances,
    RouteTables,
    SecurityGroups,
    Settings,
    SpotFleets,
    SpotInstances,
    Subnets,
    FlowLogs,
    TagResponse,
    VirtualPrivateGateways,
    VPCs,
    VPCEndpointServiceConfiguration,
    VPCPeeringConnections,
    VPNConnections,
    Windows,
    NatGateways,
    TransitGateways,
    TransitGatewayRouteTable,
    TransitGatewayAttachment,
    IamInstanceProfiles,
    CarrierGateway,
):
    def __init__(self) -> None:
        super().__init__(service_name="ec2")
        self.automated_parameter_parsing = True

    @property
    def should_autoescape(self) -> bool:
        return True
