"""Stub responses for EC2 operations not yet fully implemented in Moto."""

from moto.core.responses import ActionResult, EmptyResult

from ._base_response import EC2BaseResponse


class GapStubs(EC2BaseResponse):
    """Minimal stubs returning empty results for unimplemented EC2 operations."""

    def accept_transit_gateway_multicast_domain_associations(self) -> str:
        return ActionResult(
            {
                "Associations": {},
            }
        )

    def cancel_import_task(self) -> str:
        return ActionResult(
            {
                "ImportTaskId": "",
                "PreviousState": "",
                "State": "",
            }
        )

    def create_instance_event_window(self) -> str:
        return ActionResult(
            {
                "InstanceEventWindow": {},
            }
        )

    def create_ipam_resource_discovery(self) -> str:
        return ActionResult(
            {
                "IpamResourceDiscovery": {},
            }
        )

    def create_network_insights_access_scope(self) -> str:
        return ActionResult(
            {
                "NetworkInsightsAccessScope": {},
                "NetworkInsightsAccessScopeContent": {},
            }
        )

    def create_public_ipv4_pool(self) -> str:
        return ActionResult(
            {
                "PoolId": "",
            }
        )

    def create_verified_access_instance(self) -> str:
        return ActionResult(
            {
                "VerifiedAccessInstance": {},
            }
        )

    def deregister_transit_gateway_multicast_group_members(self) -> str:
        return ActionResult(
            {
                "DeregisteredMulticastGroupMembers": {},
            }
        )

    def deregister_transit_gateway_multicast_group_sources(self) -> str:
        return ActionResult(
            {
                "DeregisteredMulticastGroupSources": {},
            }
        )

    def describe_address_transfers(self) -> str:
        return ActionResult(
            {
                "AddressTransfers": [],
                "NextToken": "",
            }
        )

    def describe_aggregate_id_format(self) -> str:
        return ActionResult(
            {
                "UseLongIdsAggregated": True,
                "Statuses": [],
            }
        )

    def describe_aws_network_performance_metric_subscriptions(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "Subscriptions": [],
            }
        )

    def describe_byoip_cidrs(self) -> str:
        return ActionResult(
            {
                "ByoipCidrs": [],
                "NextToken": "",
            }
        )

    def describe_capacity_block_extension_history(self) -> str:
        return ActionResult(
            {
                "CapacityBlockExtensions": [],
                "NextToken": "",
            }
        )

    def describe_capacity_block_status(self) -> str:
        return ActionResult(
            {
                "CapacityBlockStatuses": [],
                "NextToken": "",
            }
        )

    def describe_capacity_blocks(self) -> str:
        return ActionResult(
            {
                "CapacityBlocks": [],
                "NextToken": "",
            }
        )

    def describe_capacity_manager_data_exports(self) -> str:
        return ActionResult(
            {
                "CapacityManagerDataExports": [],
                "NextToken": "",
            }
        )

    def describe_capacity_reservation_fleets(self) -> str:
        return ActionResult(
            {
                "CapacityReservationFleets": [],
                "NextToken": "",
            }
        )

    def describe_capacity_reservation_topology(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "CapacityReservations": [],
            }
        )

    def describe_capacity_reservations(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "CapacityReservations": [],
            }
        )

    def describe_classic_link_instances(self) -> str:
        return ActionResult(
            {
                "Instances": [],
                "NextToken": "",
            }
        )

    def describe_client_vpn_authorization_rules(self) -> str:
        return ActionResult(
            {
                "AuthorizationRules": [],
                "NextToken": "",
            }
        )

    def describe_client_vpn_connections(self) -> str:
        return ActionResult(
            {
                "Connections": [],
                "NextToken": "",
            }
        )

    def describe_client_vpn_routes(self) -> str:
        return ActionResult(
            {
                "Routes": [],
                "NextToken": "",
            }
        )

    def describe_client_vpn_target_networks(self) -> str:
        return ActionResult(
            {
                "ClientVpnTargetNetworks": [],
                "NextToken": "",
            }
        )

    def describe_coip_pools(self) -> str:
        return ActionResult(
            {
                "CoipPools": [],
                "NextToken": "",
            }
        )

    def describe_conversion_tasks(self) -> str:
        return ActionResult(
            {
                "ConversionTasks": [],
            }
        )

    def describe_declarative_policies_reports(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "Reports": [],
            }
        )

    def describe_elastic_gpus(self) -> str:
        return ActionResult(
            {
                "ElasticGpuSet": [],
                "MaxResults": 0,
                "NextToken": "",
            }
        )

    def describe_export_image_tasks(self) -> str:
        return ActionResult(
            {
                "ExportImageTasks": [],
                "NextToken": "",
            }
        )

    def describe_export_tasks(self) -> str:
        return ActionResult(
            {
                "ExportTasks": [],
            }
        )

    def describe_fast_launch_images(self) -> str:
        return ActionResult(
            {
                "FastLaunchImages": [],
                "NextToken": "",
            }
        )

    def describe_fast_snapshot_restores(self) -> str:
        return ActionResult(
            {
                "FastSnapshotRestores": [],
                "NextToken": "",
            }
        )

    def describe_fpga_image_attribute(self) -> str:
        return ActionResult(
            {
                "FpgaImageAttribute": {},
            }
        )

    def describe_fpga_images(self) -> str:
        return ActionResult(
            {
                "FpgaImages": [],
                "NextToken": "",
            }
        )

    def describe_host_reservation_offerings(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "OfferingSet": [],
            }
        )

    def describe_host_reservations(self) -> str:
        return ActionResult(
            {
                "HostReservationSet": [],
                "NextToken": "",
            }
        )

    def describe_id_format(self) -> str:
        return ActionResult(
            {
                "Statuses": [],
            }
        )

    def describe_identity_id_format(self) -> str:
        return ActionResult(
            {
                "Statuses": [],
            }
        )

    def describe_image_usage_report_entries(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "ImageUsageReportEntries": [],
            }
        )

    def describe_image_usage_reports(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "ImageUsageReports": [],
            }
        )

    def describe_import_image_tasks(self) -> str:
        return ActionResult(
            {
                "ImportImageTasks": [],
                "NextToken": "",
            }
        )

    def describe_import_snapshot_tasks(self) -> str:
        return ActionResult(
            {
                "ImportSnapshotTasks": [],
                "NextToken": "",
            }
        )

    def describe_instance_connect_endpoints(self) -> str:
        return ActionResult(
            {
                "InstanceConnectEndpoints": [],
                "NextToken": "",
            }
        )

    def describe_instance_event_notification_attributes(self) -> str:
        return ActionResult(
            {
                "InstanceTagAttribute": {},
            }
        )

    def describe_instance_event_windows(self) -> str:
        return ActionResult(
            {
                "InstanceEventWindows": [],
                "NextToken": "",
            }
        )

    def describe_instance_image_metadata(self) -> str:
        return ActionResult(
            {
                "InstanceImageMetadata": [],
                "NextToken": "",
            }
        )

    def describe_instance_sql_ha_history_states(self) -> str:
        return ActionResult(
            {
                "Instances": [],
                "NextToken": "",
            }
        )

    def describe_instance_sql_ha_states(self) -> str:
        return ActionResult(
            {
                "Instances": [],
                "NextToken": "",
            }
        )

    def describe_instance_topology(self) -> str:
        return ActionResult(
            {
                "Instances": [],
                "NextToken": "",
            }
        )

    def describe_ipam_byoasn(self) -> str:
        return ActionResult(
            {
                "Byoasns": [],
                "NextToken": "",
            }
        )

    def describe_ipam_external_resource_verification_tokens(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "IpamExternalResourceVerificationTokens": [],
            }
        )

    def describe_ipam_policies(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "IpamPolicies": [],
            }
        )

    def describe_ipam_prefix_list_resolver_targets(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "IpamPrefixListResolverTargets": [],
            }
        )

    def describe_ipam_prefix_list_resolvers(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "IpamPrefixListResolvers": [],
            }
        )

    def describe_ipam_resource_discoveries(self) -> str:
        return ActionResult(
            {
                "IpamResourceDiscoveries": [],
                "NextToken": "",
            }
        )

    def describe_ipam_resource_discovery_associations(self) -> str:
        return ActionResult(
            {
                "IpamResourceDiscoveryAssociations": [],
                "NextToken": "",
            }
        )

    def describe_ipam_scopes(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "IpamScopes": [],
            }
        )

    def describe_ipv6_pools(self) -> str:
        return ActionResult(
            {
                "Ipv6Pools": [],
                "NextToken": "",
            }
        )

    def describe_local_gateway_route_table_virtual_interface_group_associations(
        self,
    ) -> str:
        return ActionResult(
            {
                "LocalGatewayRouteTableVirtualInterfaceGroupAssociations": [],
                "NextToken": "",
            }
        )

    def describe_local_gateway_route_table_vpc_associations(self) -> str:
        return ActionResult(
            {
                "LocalGatewayRouteTableVpcAssociations": [],
                "NextToken": "",
            }
        )

    def describe_local_gateway_route_tables(self) -> str:
        return ActionResult(
            {
                "LocalGatewayRouteTables": [],
                "NextToken": "",
            }
        )

    def describe_local_gateway_virtual_interface_groups(self) -> str:
        return ActionResult(
            {
                "LocalGatewayVirtualInterfaceGroups": [],
                "NextToken": "",
            }
        )

    def describe_local_gateway_virtual_interfaces(self) -> str:
        return ActionResult(
            {
                "LocalGatewayVirtualInterfaces": [],
                "NextToken": "",
            }
        )

    def describe_local_gateways(self) -> str:
        return ActionResult(
            {
                "LocalGateways": [],
                "NextToken": "",
            }
        )

    def describe_locked_snapshots(self) -> str:
        return ActionResult(
            {
                "Snapshots": [],
                "NextToken": "",
            }
        )

    def describe_mac_hosts(self) -> str:
        return ActionResult(
            {
                "MacHosts": [],
                "NextToken": "",
            }
        )

    def describe_mac_modification_tasks(self) -> str:
        return ActionResult(
            {
                "MacModificationTasks": [],
                "NextToken": "",
            }
        )

    def describe_moving_addresses(self) -> str:
        return ActionResult(
            {
                "MovingAddressStatuses": [],
                "NextToken": "",
            }
        )

    def describe_network_insights_access_scope_analyses(self) -> str:
        return ActionResult(
            {
                "NetworkInsightsAccessScopeAnalyses": [],
                "NextToken": "",
            }
        )

    def describe_network_insights_access_scopes(self) -> str:
        return ActionResult(
            {
                "NetworkInsightsAccessScopes": [],
                "NextToken": "",
            }
        )

    def describe_network_insights_analyses(self) -> str:
        return ActionResult(
            {
                "NetworkInsightsAnalyses": [],
                "NextToken": "",
            }
        )

    def describe_network_insights_paths(self) -> str:
        return ActionResult(
            {
                "NetworkInsightsPaths": [],
                "NextToken": "",
            }
        )

    def describe_network_interface_permissions(self) -> str:
        return ActionResult(
            {
                "NetworkInterfacePermissions": [],
                "NextToken": "",
            }
        )

    def describe_outpost_lags(self) -> str:
        return ActionResult(
            {
                "OutpostLags": [],
                "NextToken": "",
            }
        )

    def describe_principal_id_format(self) -> str:
        return ActionResult(
            {
                "Principals": [],
                "NextToken": "",
            }
        )

    def describe_public_ipv4_pools(self) -> str:
        return ActionResult(
            {
                "PublicIpv4Pools": [],
                "NextToken": "",
            }
        )

    def describe_replace_root_volume_tasks(self) -> str:
        return ActionResult(
            {
                "ReplaceRootVolumeTasks": [],
                "NextToken": "",
            }
        )

    def describe_reserved_instances_modifications(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "ReservedInstancesModifications": [],
            }
        )

    def describe_route_server_endpoints(self) -> str:
        return ActionResult(
            {
                "RouteServerEndpoints": [],
                "NextToken": "",
            }
        )

    def describe_route_server_peers(self) -> str:
        return ActionResult(
            {
                "RouteServerPeers": [],
                "NextToken": "",
            }
        )

    def describe_route_servers(self) -> str:
        return ActionResult(
            {
                "RouteServers": [],
                "NextToken": "",
            }
        )

    def describe_scheduled_instance_availability(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "ScheduledInstanceAvailabilitySet": [],
            }
        )

    def describe_scheduled_instances(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "ScheduledInstanceSet": [],
            }
        )

    def describe_secondary_interfaces(self) -> str:
        return ActionResult(
            {
                "SecondaryInterfaces": [],
                "NextToken": "",
            }
        )

    def describe_secondary_networks(self) -> str:
        return ActionResult(
            {
                "SecondaryNetworks": [],
                "NextToken": "",
            }
        )

    def describe_secondary_subnets(self) -> str:
        return ActionResult(
            {
                "SecondarySubnets": [],
                "NextToken": "",
            }
        )

    def describe_security_group_vpc_associations(self) -> str:
        return ActionResult(
            {
                "SecurityGroupVpcAssociations": [],
                "NextToken": "",
            }
        )

    def describe_security_group_references(self) -> str:
        return ActionResult(
            {
                "SecurityGroupReferenceSet": [],
            }
        )

    def describe_service_link_virtual_interfaces(self) -> str:
        return ActionResult(
            {
                "ServiceLinkVirtualInterfaces": [],
                "NextToken": "",
            }
        )

    def describe_stale_security_groups(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "StaleSecurityGroupSet": [],
            }
        )

    def describe_store_image_tasks(self) -> str:
        return ActionResult(
            {
                "StoreImageTaskResults": [],
                "NextToken": "",
            }
        )

    def describe_traffic_mirror_filter_rules(self) -> str:
        return ActionResult(
            {
                "TrafficMirrorFilterRules": [],
                "NextToken": "",
            }
        )

    def describe_traffic_mirror_sessions(self) -> str:
        return ActionResult(
            {
                "TrafficMirrorSessions": [],
                "NextToken": "",
            }
        )

    def describe_transit_gateway_connect_peers(self) -> str:
        return ActionResult(
            {
                "TransitGatewayConnectPeers": [],
                "NextToken": "",
            }
        )

    def describe_transit_gateway_connects(self) -> str:
        return ActionResult(
            {
                "TransitGatewayConnects": [],
                "NextToken": "",
            }
        )

    def describe_transit_gateway_metering_policies(self) -> str:
        return ActionResult(
            {
                "TransitGatewayMeteringPolicies": [],
                "NextToken": "",
            }
        )

    def describe_transit_gateway_multicast_domains(self) -> str:
        return ActionResult(
            {
                "TransitGatewayMulticastDomains": [],
                "NextToken": "",
            }
        )

    def describe_transit_gateway_policy_tables(self) -> str:
        return ActionResult(
            {
                "TransitGatewayPolicyTables": [],
                "NextToken": "",
            }
        )

    def describe_transit_gateway_route_table_announcements(self) -> str:
        return ActionResult(
            {
                "TransitGatewayRouteTableAnnouncements": [],
                "NextToken": "",
            }
        )

    def describe_trunk_interface_associations(self) -> str:
        return ActionResult(
            {
                "InterfaceAssociations": [],
                "NextToken": "",
            }
        )

    def describe_verified_access_endpoints(self) -> str:
        return ActionResult(
            {
                "VerifiedAccessEndpoints": [],
                "NextToken": "",
            }
        )

    def describe_verified_access_groups(self) -> str:
        return ActionResult(
            {
                "VerifiedAccessGroups": [],
                "NextToken": "",
            }
        )

    def describe_verified_access_instance_logging_configurations(self) -> str:
        return ActionResult(
            {
                "LoggingConfigurations": [],
                "NextToken": "",
            }
        )

    def describe_verified_access_instances(self) -> str:
        return ActionResult(
            {
                "VerifiedAccessInstances": [],
                "NextToken": "",
            }
        )

    def describe_verified_access_trust_providers(self) -> str:
        return ActionResult(
            {
                "VerifiedAccessTrustProviders": [],
                "NextToken": "",
            }
        )

    def describe_vpc_block_public_access_exclusions(self) -> str:
        return ActionResult(
            {
                "VpcBlockPublicAccessExclusions": [],
                "NextToken": "",
            }
        )

    def describe_vpc_block_public_access_options(self) -> str:
        return ActionResult(
            {
                "VpcBlockPublicAccessOptions": {},
            }
        )

    def describe_vpc_encryption_controls(self) -> str:
        return ActionResult(
            {
                "VpcEncryptionControls": [],
                "NextToken": "",
            }
        )

    def describe_vpc_endpoint_associations(self) -> str:
        return ActionResult(
            {
                "VpcEndpointAssociations": [],
                "NextToken": "",
            }
        )

    def describe_vpc_endpoint_connection_notifications(self) -> str:
        return ActionResult(
            {
                "ConnectionNotificationSet": [],
                "NextToken": "",
            }
        )

    def describe_vpc_endpoint_connections(self) -> str:
        return ActionResult(
            {
                "VpcEndpointConnections": [],
                "NextToken": "",
            }
        )

    def describe_vpn_concentrators(self) -> str:
        return ActionResult(
            {
                "VpnConcentrators": [],
                "NextToken": "",
            }
        )

    def disable_allowed_images_settings(self) -> str:
        return ActionResult(
            {
                "AllowedImagesSettingsState": "",
            }
        )

    def disable_aws_network_performance_metric_subscription(self) -> str:
        return ActionResult(
            {
                "Output": True,
            }
        )

    def disable_capacity_manager(self) -> str:
        return ActionResult(
            {
                "CapacityManagerStatus": "",
                "OrganizationsAccess": True,
            }
        )

    def disable_image_block_public_access(self) -> str:
        return ActionResult(
            {
                "ImageBlockPublicAccessState": "",
            }
        )

    def disable_serial_console_access(self) -> str:
        return ActionResult(
            {
                "SerialConsoleAccessEnabled": True,
            }
        )

    def disable_snapshot_block_public_access(self) -> str:
        return ActionResult(
            {
                "State": "",
            }
        )

    def enable_aws_network_performance_metric_subscription(self) -> str:
        return ActionResult(
            {
                "Output": True,
            }
        )

    def enable_capacity_manager(self) -> str:
        return ActionResult(
            {
                "CapacityManagerStatus": "",
                "OrganizationsAccess": True,
            }
        )

    def enable_reachability_analyzer_organization_sharing(self) -> str:
        return ActionResult(
            {
                "ReturnValue": True,
            }
        )

    def enable_serial_console_access(self) -> str:
        return ActionResult(
            {
                "SerialConsoleAccessEnabled": True,
            }
        )

    def get_allowed_images_settings(self) -> str:
        return ActionResult(
            {
                "State": "",
                "ImageCriteria": [],
                "ManagedBy": "",
            }
        )

    def get_aws_network_performance_data(self) -> str:
        return ActionResult(
            {
                "DataResponses": [],
                "NextToken": "",
            }
        )

    def get_capacity_manager_attributes(self) -> str:
        return ActionResult(
            {
                "CapacityManagerStatus": "",
                "OrganizationsAccess": True,
                "DataExportCount": 0,
                "IngestionStatus": "",
                "IngestionStatusMessage": "",
            }
        )

    def get_ebs_default_kms_key_id(self) -> str:
        return ActionResult(
            {
                "KmsKeyId": "",
            }
        )

    def get_enabled_ipam_policy(self) -> str:
        return ActionResult(
            {
                "IpamPolicyEnabled": True,
                "IpamPolicyId": "",
                "ManagedBy": "",
            }
        )

    def get_image_block_public_access_state(self) -> str:
        return ActionResult(
            {
                "ImageBlockPublicAccessState": "",
                "ManagedBy": "",
            }
        )

    def get_instance_metadata_defaults(self) -> str:
        return ActionResult(
            {
                "AccountLevel": {},
            }
        )

    def get_serial_console_access_status(self) -> str:
        return ActionResult(
            {
                "SerialConsoleAccessEnabled": True,
                "ManagedBy": "",
            }
        )

    def get_snapshot_block_public_access_state(self) -> str:
        return ActionResult(
            {
                "State": "",
                "ManagedBy": "",
            }
        )

    def get_vpn_connection_device_types(self) -> str:
        return ActionResult(
            {
                "VpnConnectionDeviceTypes": [],
                "NextToken": "",
            }
        )

    def get_active_vpn_tunnel_status(self) -> str:
        return ActionResult(
            {
                "ActiveVpnTunnelStatus": {},
            }
        )

    def get_associated_enclave_certificate_iam_roles(self) -> str:
        return ActionResult(
            {
                "AssociatedRoles": [],
            }
        )

    def get_associated_ipv6_pool_cidrs(self) -> str:
        return ActionResult(
            {
                "Ipv6CidrAssociations": [],
                "NextToken": "",
            }
        )

    def get_capacity_manager_metric_dimensions(self) -> str:
        return ActionResult(
            {
                "MetricDimensionResults": [],
                "NextToken": "",
            }
        )

    def get_capacity_reservation_usage(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "CapacityReservationId": "",
                "InstanceType": "",
                "TotalInstanceCount": 0,
                "AvailableInstanceCount": 0,
                "State": "",
                "InstanceUsages": [],
                "Interruptible": True,
                "InterruptibleCapacityAllocation": {},
                "InterruptionInfo": {},
            }
        )

    def get_console_screenshot(self) -> str:
        return ActionResult(
            {
                "ImageData": "",
                "InstanceId": "",
            }
        )

    def get_default_credit_specification(self) -> str:
        return ActionResult(
            {
                "InstanceFamilyCreditSpecification": {},
            }
        )

    def get_flow_logs_integration_template(self) -> str:
        return ActionResult(
            {
                "Result": "",
            }
        )

    def get_groups_for_capacity_reservation(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "CapacityReservationGroups": [],
            }
        )

    def get_image_ancestry(self) -> str:
        return ActionResult(
            {
                "ImageAncestryEntries": [],
            }
        )

    def get_instance_tpm_ek_pub(self) -> str:
        return ActionResult(
            {
                "InstanceId": "",
                "KeyType": "",
                "KeyFormat": "",
                "KeyValue": "",
            }
        )

    def get_instance_types_from_instance_requirements(self) -> str:
        return ActionResult(
            {
                "InstanceTypes": [],
                "NextToken": "",
            }
        )

    def get_ipam_address_history(self) -> str:
        return ActionResult(
            {
                "HistoryRecords": [],
                "NextToken": "",
            }
        )

    def get_ipam_discovered_accounts(self) -> str:
        return ActionResult(
            {
                "IpamDiscoveredAccounts": [],
                "NextToken": "",
            }
        )

    def get_ipam_discovered_public_addresses(self) -> str:
        return ActionResult(
            {
                "IpamDiscoveredPublicAddresses": [],
                "NextToken": "",
            }
        )

    def get_ipam_discovered_resource_cidrs(self) -> str:
        return ActionResult(
            {
                "IpamDiscoveredResourceCidrs": [],
                "NextToken": "",
            }
        )

    def get_ipam_policy_allocation_rules(self) -> str:
        return ActionResult(
            {
                "IpamPolicyDocuments": [],
                "NextToken": "",
            }
        )

    def get_ipam_policy_organization_targets(self) -> str:
        return ActionResult(
            {
                "OrganizationTargets": [],
                "NextToken": "",
            }
        )

    def get_ipam_prefix_list_resolver_rules(self) -> str:
        return ActionResult(
            {
                "Rules": [],
                "NextToken": "",
            }
        )

    def get_ipam_prefix_list_resolver_version_entries(self) -> str:
        return ActionResult(
            {
                "Entries": [],
                "NextToken": "",
            }
        )

    def get_ipam_prefix_list_resolver_versions(self) -> str:
        return ActionResult(
            {
                "IpamPrefixListResolverVersions": [],
                "NextToken": "",
            }
        )

    def get_reserved_instances_exchange_quote(self) -> str:
        return ActionResult(
            {
                "CurrencyCode": "",
                "IsValidExchange": True,
                "PaymentDue": "",
                "ReservedInstanceValueRollup": {},
                "ReservedInstanceValueSet": [],
                "TargetConfigurationValueRollup": {},
                "TargetConfigurationValueSet": [],
                "ValidationFailureReason": "",
            }
        )

    def get_route_server_associations(self) -> str:
        return ActionResult(
            {
                "RouteServerAssociations": [],
            }
        )

    def get_route_server_propagations(self) -> str:
        return ActionResult(
            {
                "RouteServerPropagations": [],
            }
        )

    def get_route_server_routing_database(self) -> str:
        return ActionResult(
            {
                "AreRoutesPersisted": True,
                "Routes": [],
                "NextToken": "",
            }
        )

    def get_spot_placement_scores(self) -> str:
        return ActionResult(
            {
                "SpotPlacementScores": [],
                "NextToken": "",
            }
        )

    def get_transit_gateway_metering_policy_entries(self) -> str:
        return ActionResult(
            {
                "TransitGatewayMeteringPolicyEntries": [],
                "NextToken": "",
            }
        )

    def get_transit_gateway_multicast_domain_associations(self) -> str:
        return ActionResult(
            {
                "MulticastDomainAssociations": [],
                "NextToken": "",
            }
        )

    def get_transit_gateway_policy_table_associations(self) -> str:
        return ActionResult(
            {
                "Associations": [],
                "NextToken": "",
            }
        )

    def get_transit_gateway_policy_table_entries(self) -> str:
        return ActionResult(
            {
                "TransitGatewayPolicyTableEntries": [],
                "NextToken": "",
            }
        )

    def get_verified_access_endpoint_policy(self) -> str:
        return ActionResult(
            {
                "PolicyEnabled": True,
                "PolicyDocument": "",
            }
        )

    def get_verified_access_endpoint_targets(self) -> str:
        return ActionResult(
            {
                "VerifiedAccessEndpointTargets": [],
                "NextToken": "",
            }
        )

    def get_verified_access_group_policy(self) -> str:
        return ActionResult(
            {
                "PolicyEnabled": True,
                "PolicyDocument": "",
            }
        )

    def get_vpc_resources_blocking_encryption_enforcement(self) -> str:
        return ActionResult(
            {
                "NonCompliantResources": [],
                "NextToken": "",
            }
        )

    def get_vpn_connection_device_sample_configuration(self) -> str:
        return ActionResult(
            {
                "VpnConnectionDeviceSampleConfiguration": "",
            }
        )

    def get_vpn_tunnel_replacement_status(self) -> str:
        return ActionResult(
            {
                "VpnConnectionId": "",
                "TransitGatewayId": "",
                "CustomerGatewayId": "",
                "VpnGatewayId": "",
                "VpnTunnelOutsideIpAddress": "",
                "MaintenanceDetails": {},
            }
        )

    def describe_capacity_block_extension_offerings(self) -> str:
        return ActionResult(
            {
                "CapacityBlockExtensionOfferings": [],
                "NextToken": "",
            }
        )

    def describe_capacity_reservation_billing_requests(self) -> str:
        return ActionResult(
            {
                "NextToken": "",
                "CapacityReservationBillingRequests": [],
            }
        )

    def import_image(self) -> str:
        return ActionResult(
            {
                "Architecture": "",
                "Description": "",
                "Encrypted": True,
                "Hypervisor": "",
                "ImageId": "",
                "ImportTaskId": "",
                "KmsKeyId": "",
                "LicenseType": "",
                "Platform": "",
                "Progress": "",
                "SnapshotDetails": [],
                "Status": "",
                "StatusMessage": "",
                "LicenseSpecifications": [],
                "Tags": [],
                "UsageOperation": "",
            }
        )

    def import_snapshot(self) -> str:
        return ActionResult(
            {
                "Description": "",
                "ImportTaskId": "",
                "SnapshotTaskDetail": {},
                "Tags": [],
            }
        )

    def list_images_in_recycle_bin(self) -> str:
        return ActionResult(
            {
                "Images": [],
                "NextToken": "",
            }
        )

    def list_snapshots_in_recycle_bin(self) -> str:
        return ActionResult(
            {
                "Snapshots": [],
                "NextToken": "",
            }
        )

    def list_volumes_in_recycle_bin(self) -> str:
        return ActionResult(
            {
                "Volumes": [],
                "NextToken": "",
            }
        )

    def modify_instance_metadata_defaults(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def reject_transit_gateway_multicast_domain_associations(self) -> str:
        return ActionResult(
            {
                "Associations": {},
            }
        )

    def replace_image_criteria_in_allowed_images_settings(self) -> str:
        return ActionResult(
            {
                "ReturnValue": True,
            }
        )

    def reset_ebs_default_kms_key_id(self) -> str:
        return ActionResult(
            {
                "KmsKeyId": "",
            }
        )

    def accept_address_transfer(self) -> str:
        return ActionResult(
            {
                "AddressTransfer": {},
            }
        )

    def modify_id_format(self) -> str:
        return EmptyResult()

    def modify_identity_id_format(self) -> str:
        return EmptyResult()

    def modify_address_attribute(self) -> str:
        allocation_id = self._get_param("AllocationId", "")
        return ActionResult(
            {
                "Address": {},
            }
        )

    def reset_address_attribute(self) -> str:
        allocation_id = self._get_param("AllocationId", "")
        return ActionResult(
            {
                "Address": {},
            }
        )

    def modify_availability_zone_group(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def modify_default_credit_specification(self) -> str:
        instance_family = self._get_param("InstanceFamily", "")
        cpu_credits = self._get_param("CpuCredits", "standard")
        return ActionResult(
            {
                "InstanceFamilyCreditSpecification": {},
            }
        )

    def modify_fpga_image_attribute(self) -> str:
        return ActionResult(
            {
                "FpgaImageAttribute": {},
            }
        )

    def reset_fpga_image_attribute(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def modify_instance_capacity_reservation_attributes(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def modify_instance_credit_specification(self) -> str:
        return ActionResult(
            {
                "SuccessfulInstanceCreditSpecifications": [],
                "UnsuccessfulInstanceCreditSpecifications": [],
            }
        )

    def modify_instance_event_start_time(self) -> str:
        instance_event_id = self._get_param("InstanceEventId", "")
        return ActionResult(
            {
                "Event": {},
            }
        )

    def modify_instance_maintenance_options(self) -> str:
        instance_id = self._get_param("InstanceId", "")
        auto_recovery = self._get_param("AutoRecovery", "default")
        return ActionResult(
            {
                "InstanceId": "",
                "AutoRecovery": "",
                "RebootMigration": "",
            }
        )

    def modify_instance_network_performance_options(self) -> str:
        instance_id = self._get_param("InstanceId", "")
        bandwidth_weighting = self._get_param("BandwidthWeighting", "default")
        return ActionResult(
            {
                "InstanceId": "",
                "BandwidthWeighting": "",
            }
        )

    def modify_instance_placement(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def modify_ipam_resource_cidr(self) -> str:
        resource_cidr = self._get_param("ResourceCidr", "")
        return ActionResult(
            {
                "IpamResourceCidr": {},
            }
        )

    def modify_ipam_resource_discovery(self) -> str:
        resource_discovery_id = self._get_param("IpamResourceDiscoveryId", "")
        return ActionResult(
            {
                "IpamResourceDiscovery": {},
            }
        )

    def modify_ipam_scope(self) -> str:
        scope_id = self._get_param("IpamScopeId", "")
        return ActionResult(
            {
                "IpamScope": {},
            }
        )

    def modify_local_gateway_route(self) -> str:
        route_table_id = self._get_param("LocalGatewayRouteTableId", "")
        return ActionResult(
            {
                "Route": {},
            }
        )

    def modify_private_dns_name_options(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def modify_reserved_instances(self) -> str:
        return ActionResult(
            {
                "ReservedInstancesModificationId": "",
            }
        )

    def modify_transit_gateway_prefix_list_reference(self) -> str:
        route_table_id = self._get_param("TransitGatewayRouteTableId", "")
        prefix_list_id = self._get_param("PrefixListId", "")
        return ActionResult(
            {
                "TransitGatewayPrefixListReference": {},
            }
        )

    def modify_vpc_endpoint_connection_notification(self) -> str:
        return ActionResult(
            {
                "ReturnValue": True,
            }
        )

    def modify_vpc_endpoint_service_payer_responsibility(self) -> str:
        return ActionResult(
            {
                "ReturnValue": True,
            }
        )

    def modify_vpn_connection(self) -> str:
        vpn_connection_id = self._get_param("VpnConnectionId", "")
        return ActionResult(
            {
                "VpnConnection": {},
            }
        )

    def modify_vpn_connection_options(self) -> str:
        vpn_connection_id = self._get_param("VpnConnectionId", "")
        return ActionResult(
            {
                "VpnConnection": {},
            }
        )

    def modify_vpn_tunnel_certificate(self) -> str:
        vpn_connection_id = self._get_param("VpnConnectionId", "")
        return ActionResult(
            {
                "VpnConnection": {},
            }
        )

    def modify_vpn_tunnel_options(self) -> str:
        vpn_connection_id = self._get_param("VpnConnectionId", "")
        return ActionResult(
            {
                "VpnConnection": {},
            }
        )

    def move_address_to_vpc(self) -> str:
        return ActionResult(
            {
                "AllocationId": "",
                "Status": "",
            }
        )

    def move_byoip_cidr_to_ipam(self) -> str:
        cidr = self._get_param("Cidr", "")
        return ActionResult(
            {
                "ByoipCidr": {},
            }
        )

    def purchase_scheduled_instances(self) -> str:
        return ActionResult(
            {
                "ScheduledInstanceSet": [],
            }
        )

    def register_instance_event_notification_attributes(self) -> str:
        return ActionResult(
            {
                "InstanceTagAttribute": {},
            }
        )

    def register_transit_gateway_multicast_group_members(self) -> str:
        domain_id = self._get_param("TransitGatewayMulticastDomainId", "")
        return ActionResult(
            {
                "RegisteredMulticastGroupMembers": {},
            }
        )

    def register_transit_gateway_multicast_group_sources(self) -> str:
        domain_id = self._get_param("TransitGatewayMulticastDomainId", "")
        return ActionResult(
            {
                "RegisteredMulticastGroupSources": {},
            }
        )

    def replace_vpn_tunnel(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def restore_address_to_classic(self) -> str:
        public_ip = self._get_param("PublicIp", "")
        return ActionResult(
            {
                "PublicIp": "",
                "Status": "",
            }
        )

    def revoke_client_vpn_ingress(self) -> str:
        return ActionResult(
            {
                "Status": {},
            }
        )

    def run_scheduled_instances(self) -> str:
        return ActionResult(
            {
                "InstanceIdSet": [],
            }
        )

    def search_transit_gateway_multicast_groups(self) -> str:
        return ActionResult(
            {
                "MulticastGroups": [],
                "NextToken": "",
            }
        )

    def send_diagnostic_interrupt(self) -> str:
        return EmptyResult()

    def start_vpc_endpoint_service_private_dns_verification(self) -> str:
        return ActionResult(
            {
                "ReturnValue": True,
            }
        )

    def lock_snapshot(self) -> str:
        snapshot_id = self._get_param("SnapshotId", "")
        lock_mode = self._get_param("LockMode", "governance")
        return ActionResult(
            {
                "SnapshotId": "",
                "LockState": "",
                "LockDuration": 0,
                "CoolOffPeriod": 0,
            }
        )

    def unlock_snapshot(self) -> str:
        snapshot_id = self._get_param("SnapshotId", "")
        return ActionResult(
            {
                "SnapshotId": "",
            }
        )

    def unassign_private_nat_gateway_address(self) -> str:
        nat_gateway_id = self._get_param("NatGatewayId", "")
        return ActionResult(
            {
                "NatGatewayId": "",
                "NatGatewayAddresses": [],
            }
        )

    def withdraw_byoip_cidr(self) -> str:
        cidr = self._get_param("Cidr", "")
        return ActionResult(
            {
                "ByoipCidr": {},
            }
        )

    def restore_image_from_recycle_bin(self) -> str:
        image_id = self._get_param("ImageId", "")
        return ActionResult(
            {
                "Return": True,
            }
        )

    def restore_snapshot_from_recycle_bin(self) -> str:
        snapshot_id = self._get_param("SnapshotId", "")
        return ActionResult(
            {
                "SnapshotId": "",
                "OutpostArn": "",
                "Description": "",
                "Encrypted": True,
                "OwnerId": "",
                "Progress": "",
                "State": "",
                "VolumeId": "",
                "VolumeSize": 0,
                "SseType": "",
            }
        )

    def import_client_vpn_client_certificate_revocation_list(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def accept_capacity_reservation_billing_ownership(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def accept_reserved_instances_exchange_quote(self) -> str:
        return ActionResult(
            {
                "ExchangeId": "",
            }
        )

    def accept_transit_gateway_vpc_attachment(self) -> str:
        return ActionResult(
            {
                "TransitGatewayVpcAttachment": {},
            }
        )

    def advertise_byoip_cidr(self) -> str:
        return ActionResult(
            {
                "ByoipCidr": {},
            }
        )

    def apply_security_groups_to_client_vpn_target_network(self) -> str:
        return ActionResult(
            {
                "SecurityGroupIds": [],
            }
        )

    def assign_private_nat_gateway_address(self) -> str:
        return ActionResult(
            {
                "NatGatewayId": "",
                "NatGatewayAddresses": [],
            }
        )

    def associate_client_vpn_target_network(self) -> str:
        return ActionResult(
            {
                "AssociationId": "",
                "Status": {},
            }
        )

    def associate_enclave_certificate_iam_role(self) -> str:
        return ActionResult(
            {
                "CertificateS3BucketName": "",
                "CertificateS3ObjectKey": "",
                "EncryptionKmsKeyId": "",
            }
        )

    def disassociate_enclave_certificate_iam_role(self) -> ActionResult:
        # Both params accepted but not persisted - EC2-Classic enclave feature stub
        return ActionResult({"Return": True})

    def associate_ipam_byoasn(self) -> str:
        return ActionResult(
            {
                "AsnAssociation": {},
            }
        )

    def associate_ipam_resource_discovery(self) -> str:
        return ActionResult(
            {
                "IpamResourceDiscoveryAssociation": {},
            }
        )

    def associate_nat_gateway_address(self) -> str:
        return ActionResult(
            {
                "NatGatewayId": "",
                "NatGatewayAddresses": [],
            }
        )

    def associate_transit_gateway_multicast_domain(self) -> str:
        return ActionResult(
            {
                "Associations": {},
            }
        )

    def associate_transit_gateway_policy_table(self) -> str:
        return ActionResult(
            {
                "Association": {},
            }
        )

    def attach_verified_access_trust_provider(self) -> str:
        return ActionResult(
            {
                "VerifiedAccessTrustProvider": {},
                "VerifiedAccessInstance": {},
            }
        )

    def cancel_conversion_task(self) -> str:
        return EmptyResult()

    def cancel_declarative_policies_report(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def cancel_export_task(self) -> str:
        return EmptyResult()

    def cancel_image_launch_permission(self) -> str:
        return ActionResult(
            {
                "Return": True,
            }
        )

    def copy_fpga_image(self) -> str:
        return ActionResult(
            {
                "FpgaImageId": "",
            }
        )

    def create_capacity_reservation_by_splitting(self) -> str:
        return ActionResult(
            {
                "SourceCapacityReservation": {},
                "DestinationCapacityReservation": {},
                "InstanceCount": 0,
            }
        )

    def create_client_vpn_route(self) -> str:
        return ActionResult(
            {
                "Status": {},
            }
        )

    def create_fpga_image(self) -> str:
        return ActionResult(
            {
                "FpgaImageId": "",
                "FpgaImageGlobalId": "",
            }
        )

    def create_instance_export_task(self) -> str:
        return ActionResult(
            {
                "ExportTask": {},
            }
        )

    def create_ipam_external_resource_verification_token(self) -> str:
        return ActionResult(
            {
                "IpamExternalResourceVerificationToken": {},
            }
        )

    def create_local_gateway_route_table_virtual_interface_group_association(
        self,
    ) -> str:
        return ActionResult(
            {
                "LocalGatewayRouteTableVirtualInterfaceGroupAssociation": {},
            }
        )

    def create_local_gateway_route_table_vpc_association(self) -> str:
        return ActionResult(
            {
                "LocalGatewayRouteTableVpcAssociation": {},
            }
        )

    def create_network_interface_permission(self) -> str:
        return ActionResult(
            {
                "InterfacePermission": {},
            }
        )

    def create_restore_image_task(self) -> str:
        return ActionResult(
            {
                "ImageId": "",
            }
        )

    def create_transit_gateway_multicast_domain(self) -> str:
        return ActionResult(
            {
                "TransitGatewayMulticastDomain": {},
            }
        )

    def create_transit_gateway_policy_table(self) -> str:
        return ActionResult(
            {
                "TransitGatewayPolicyTable": {},
            }
        )

    def bundle_instance(self) -> ActionResult:
        return ActionResult(
            {
                "BundleTask": {},
            }
        )

    def cancel_bundle_task(self) -> ActionResult:
        return ActionResult(
            {
                "BundleTask": {},
            }
        )

    def cancel_reserved_instances_listing(self) -> ActionResult:
        return ActionResult(
            {
                "ReservedInstancesListings": [],
            }
        )

    def create_reserved_instances_listing(self) -> ActionResult:
        return ActionResult(
            {
                "ReservedInstancesListings": [],
            }
        )

    def purchase_reserved_instances_offering(self) -> ActionResult:
        return ActionResult(
            {
                "ReservedInstancesId": "",
            }
        )
