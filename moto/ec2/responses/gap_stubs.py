"""Stub responses for EC2 operations not yet fully implemented in Moto."""

from moto.core.responses import ActionResult, EmptyResult

from ._base_response import EC2BaseResponse


class GapStubs(EC2BaseResponse):
    """Minimal stubs returning empty results for unimplemented EC2 operations."""

    def accept_transit_gateway_multicast_domain_associations(self) -> str:
        return EmptyResult()

    def cancel_import_task(self) -> str:
        return EmptyResult()

    def create_instance_event_window(self) -> str:
        return EmptyResult()

    def create_ipam_resource_discovery(self) -> str:
        return EmptyResult()

    def create_network_insights_access_scope(self) -> str:
        return EmptyResult()

    def create_public_ipv4_pool(self) -> str:
        return EmptyResult()

    def create_verified_access_instance(self) -> str:
        return EmptyResult()

    def deregister_transit_gateway_multicast_group_members(self) -> str:
        return EmptyResult()

    def deregister_transit_gateway_multicast_group_sources(self) -> str:
        return EmptyResult()

    def describe_address_transfers(self) -> str:
        return EmptyResult()

    def describe_aggregate_id_format(self) -> str:
        return EmptyResult()

    def describe_aws_network_performance_metric_subscriptions(self) -> str:
        return EmptyResult()

    def describe_byoip_cidrs(self) -> str:
        return EmptyResult()

    def describe_capacity_block_extension_history(self) -> str:
        return EmptyResult()

    def describe_capacity_block_status(self) -> str:
        return EmptyResult()

    def describe_capacity_blocks(self) -> str:
        return EmptyResult()

    def describe_capacity_manager_data_exports(self) -> str:
        return EmptyResult()

    def describe_capacity_reservation_fleets(self) -> str:
        return EmptyResult()

    def describe_capacity_reservation_topology(self) -> str:
        return EmptyResult()

    def describe_capacity_reservations(self) -> str:
        return EmptyResult()

    def describe_classic_link_instances(self) -> str:
        return EmptyResult()

    def describe_client_vpn_authorization_rules(self) -> str:
        return EmptyResult()

    def describe_client_vpn_connections(self) -> str:
        return EmptyResult()

    def describe_client_vpn_routes(self) -> str:
        return EmptyResult()

    def describe_client_vpn_target_networks(self) -> str:
        return EmptyResult()

    def describe_coip_pools(self) -> str:
        return EmptyResult()

    def describe_conversion_tasks(self) -> str:
        return EmptyResult()

    def describe_declarative_policies_reports(self) -> str:
        return EmptyResult()

    def describe_elastic_gpus(self) -> str:
        return EmptyResult()

    def describe_export_image_tasks(self) -> str:
        return EmptyResult()

    def describe_export_tasks(self) -> str:
        return EmptyResult()

    def describe_fast_launch_images(self) -> str:
        return EmptyResult()

    def describe_fast_snapshot_restores(self) -> str:
        return EmptyResult()

    def describe_fpga_image_attribute(self) -> str:
        return EmptyResult()

    def describe_fpga_images(self) -> str:
        return EmptyResult()

    def describe_host_reservation_offerings(self) -> str:
        return EmptyResult()

    def describe_host_reservations(self) -> str:
        return EmptyResult()

    def describe_id_format(self) -> str:
        return EmptyResult()

    def describe_identity_id_format(self) -> str:
        return EmptyResult()

    def describe_image_usage_report_entries(self) -> str:
        return EmptyResult()

    def describe_image_usage_reports(self) -> str:
        return EmptyResult()

    def describe_import_image_tasks(self) -> str:
        return EmptyResult()

    def describe_import_snapshot_tasks(self) -> str:
        return EmptyResult()

    def describe_instance_connect_endpoints(self) -> str:
        return EmptyResult()

    def describe_instance_event_notification_attributes(self) -> str:
        return EmptyResult()

    def describe_instance_event_windows(self) -> str:
        return EmptyResult()

    def describe_instance_image_metadata(self) -> str:
        return EmptyResult()

    def describe_instance_sql_ha_history_states(self) -> str:
        return EmptyResult()

    def describe_instance_sql_ha_states(self) -> str:
        return EmptyResult()

    def describe_instance_topology(self) -> str:
        return EmptyResult()

    def describe_ipam_byoasn(self) -> str:
        return EmptyResult()

    def describe_ipam_external_resource_verification_tokens(self) -> str:
        return EmptyResult()

    def describe_ipam_policies(self) -> str:
        return EmptyResult()

    def describe_ipam_prefix_list_resolver_targets(self) -> str:
        return EmptyResult()

    def describe_ipam_prefix_list_resolvers(self) -> str:
        return EmptyResult()

    def describe_ipam_resource_discoveries(self) -> str:
        return EmptyResult()

    def describe_ipam_resource_discovery_associations(self) -> str:
        return EmptyResult()

    def describe_ipam_scopes(self) -> str:
        return EmptyResult()

    def describe_ipv6_pools(self) -> str:
        return EmptyResult()

    def describe_local_gateway_route_table_virtual_interface_group_associations(
        self,
    ) -> str:
        return EmptyResult()

    def describe_local_gateway_route_table_vpc_associations(self) -> str:
        return EmptyResult()

    def describe_local_gateway_route_tables(self) -> str:
        return EmptyResult()

    def describe_local_gateway_virtual_interface_groups(self) -> str:
        return EmptyResult()

    def describe_local_gateway_virtual_interfaces(self) -> str:
        return EmptyResult()

    def describe_local_gateways(self) -> str:
        return EmptyResult()

    def describe_locked_snapshots(self) -> str:
        return EmptyResult()

    def describe_mac_hosts(self) -> str:
        return EmptyResult()

    def describe_mac_modification_tasks(self) -> str:
        return EmptyResult()

    def describe_moving_addresses(self) -> str:
        return EmptyResult()

    def describe_network_insights_access_scope_analyses(self) -> str:
        return EmptyResult()

    def describe_network_insights_access_scopes(self) -> str:
        return EmptyResult()

    def describe_network_insights_analyses(self) -> str:
        return EmptyResult()

    def describe_network_insights_paths(self) -> str:
        return EmptyResult()

    def describe_network_interface_permissions(self) -> str:
        return EmptyResult()

    def describe_outpost_lags(self) -> str:
        return EmptyResult()

    def describe_principal_id_format(self) -> str:
        return EmptyResult()

    def describe_public_ipv4_pools(self) -> str:
        return EmptyResult()

    def describe_replace_root_volume_tasks(self) -> str:
        return EmptyResult()

    def describe_reserved_instances_modifications(self) -> str:
        return EmptyResult()

    def describe_route_server_endpoints(self) -> str:
        return EmptyResult()

    def describe_route_server_peers(self) -> str:
        return EmptyResult()

    def describe_route_servers(self) -> str:
        return EmptyResult()

    def describe_scheduled_instance_availability(self) -> str:
        return EmptyResult()

    def describe_scheduled_instances(self) -> str:
        return EmptyResult()

    def describe_secondary_interfaces(self) -> str:
        return EmptyResult()

    def describe_secondary_networks(self) -> str:
        return EmptyResult()

    def describe_secondary_subnets(self) -> str:
        return EmptyResult()

    def describe_security_group_vpc_associations(self) -> str:
        return EmptyResult()

    def describe_security_group_references(self) -> str:
        return EmptyResult()

    def describe_service_link_virtual_interfaces(self) -> str:
        return EmptyResult()

    def describe_stale_security_groups(self) -> str:
        return EmptyResult()

    def describe_store_image_tasks(self) -> str:
        return EmptyResult()

    def describe_traffic_mirror_filter_rules(self) -> str:
        return EmptyResult()

    def describe_traffic_mirror_sessions(self) -> str:
        return EmptyResult()

    def describe_transit_gateway_connect_peers(self) -> str:
        return EmptyResult()

    def describe_transit_gateway_connects(self) -> str:
        return EmptyResult()

    def describe_transit_gateway_metering_policies(self) -> str:
        return EmptyResult()

    def describe_transit_gateway_multicast_domains(self) -> str:
        return EmptyResult()

    def describe_transit_gateway_policy_tables(self) -> str:
        return EmptyResult()

    def describe_transit_gateway_route_table_announcements(self) -> str:
        return EmptyResult()

    def describe_trunk_interface_associations(self) -> str:
        return EmptyResult()

    def describe_verified_access_endpoints(self) -> str:
        return EmptyResult()

    def describe_verified_access_groups(self) -> str:
        return EmptyResult()

    def describe_verified_access_instance_logging_configurations(self) -> str:
        return EmptyResult()

    def describe_verified_access_instances(self) -> str:
        return EmptyResult()

    def describe_verified_access_trust_providers(self) -> str:
        return EmptyResult()

    def describe_vpc_block_public_access_exclusions(self) -> str:
        return EmptyResult()

    def describe_vpc_block_public_access_options(self) -> str:
        return EmptyResult()

    def describe_vpc_encryption_controls(self) -> str:
        return EmptyResult()

    def describe_vpc_endpoint_associations(self) -> str:
        return EmptyResult()

    def describe_vpc_endpoint_connection_notifications(self) -> str:
        return EmptyResult()

    def describe_vpc_endpoint_connections(self) -> str:
        return EmptyResult()

    def describe_vpn_concentrators(self) -> str:
        return EmptyResult()

    def disable_allowed_images_settings(self) -> str:
        return EmptyResult()

    def disable_aws_network_performance_metric_subscription(self) -> str:
        return EmptyResult()

    def disable_capacity_manager(self) -> str:
        return EmptyResult()

    def disable_image_block_public_access(self) -> str:
        return EmptyResult()

    def disable_serial_console_access(self) -> str:
        return EmptyResult()

    def disable_snapshot_block_public_access(self) -> str:
        return EmptyResult()

    def enable_aws_network_performance_metric_subscription(self) -> str:
        return EmptyResult()

    def enable_capacity_manager(self) -> str:
        return EmptyResult()

    def enable_reachability_analyzer_organization_sharing(self) -> str:
        return EmptyResult()

    def enable_serial_console_access(self) -> str:
        return EmptyResult()

    def get_allowed_images_settings(self) -> str:
        return EmptyResult()

    def get_aws_network_performance_data(self) -> str:
        return EmptyResult()

    def get_capacity_manager_attributes(self) -> str:
        return EmptyResult()

    def get_ebs_default_kms_key_id(self) -> str:
        return EmptyResult()

    def get_enabled_ipam_policy(self) -> str:
        return EmptyResult()

    def get_image_block_public_access_state(self) -> str:
        return EmptyResult()

    def get_instance_metadata_defaults(self) -> str:
        return EmptyResult()

    def get_serial_console_access_status(self) -> str:
        return EmptyResult()

    def get_snapshot_block_public_access_state(self) -> str:
        return EmptyResult()

    def get_vpn_connection_device_types(self) -> str:
        return EmptyResult()

    def get_active_vpn_tunnel_status(self) -> str:
        return EmptyResult()

    def get_associated_enclave_certificate_iam_roles(self) -> str:
        return EmptyResult()

    def get_associated_ipv6_pool_cidrs(self) -> str:
        return EmptyResult()

    def get_capacity_manager_metric_dimensions(self) -> str:
        return EmptyResult()

    def get_capacity_reservation_usage(self) -> str:
        return EmptyResult()

    def get_console_screenshot(self) -> str:
        return EmptyResult()

    def get_default_credit_specification(self) -> str:
        return EmptyResult()

    def get_flow_logs_integration_template(self) -> str:
        return EmptyResult()

    def get_groups_for_capacity_reservation(self) -> str:
        return EmptyResult()

    def get_image_ancestry(self) -> str:
        return EmptyResult()

    def get_instance_tpm_ek_pub(self) -> str:
        return EmptyResult()

    def get_instance_types_from_instance_requirements(self) -> str:
        return EmptyResult()

    def get_ipam_address_history(self) -> str:
        return EmptyResult()

    def get_ipam_discovered_accounts(self) -> str:
        return EmptyResult()

    def get_ipam_discovered_public_addresses(self) -> str:
        return EmptyResult()

    def get_ipam_discovered_resource_cidrs(self) -> str:
        return EmptyResult()

    def get_ipam_policy_allocation_rules(self) -> str:
        return EmptyResult()

    def get_ipam_policy_organization_targets(self) -> str:
        return EmptyResult()

    def get_ipam_prefix_list_resolver_rules(self) -> str:
        return EmptyResult()

    def get_ipam_prefix_list_resolver_version_entries(self) -> str:
        return EmptyResult()

    def get_ipam_prefix_list_resolver_versions(self) -> str:
        return EmptyResult()

    def get_reserved_instances_exchange_quote(self) -> str:
        return EmptyResult()

    def get_route_server_associations(self) -> str:
        return EmptyResult()

    def get_route_server_propagations(self) -> str:
        return EmptyResult()

    def get_route_server_routing_database(self) -> str:
        return EmptyResult()

    def get_spot_placement_scores(self) -> str:
        return EmptyResult()

    def get_transit_gateway_metering_policy_entries(self) -> str:
        return EmptyResult()

    def get_transit_gateway_multicast_domain_associations(self) -> str:
        return EmptyResult()

    def get_transit_gateway_policy_table_associations(self) -> str:
        return EmptyResult()

    def get_transit_gateway_policy_table_entries(self) -> str:
        return EmptyResult()

    def get_verified_access_endpoint_policy(self) -> str:
        return EmptyResult()

    def get_verified_access_endpoint_targets(self) -> str:
        return EmptyResult()

    def get_verified_access_group_policy(self) -> str:
        return EmptyResult()

    def get_vpc_resources_blocking_encryption_enforcement(self) -> str:
        return EmptyResult()

    def get_vpn_connection_device_sample_configuration(self) -> str:
        return EmptyResult()

    def get_vpn_tunnel_replacement_status(self) -> str:
        return EmptyResult()

    def describe_capacity_block_extension_offerings(self) -> str:
        return EmptyResult()

    def describe_capacity_reservation_billing_requests(self) -> str:
        return EmptyResult()

    def import_image(self) -> str:
        return EmptyResult()

    def import_snapshot(self) -> str:
        return EmptyResult()

    def list_images_in_recycle_bin(self) -> str:
        return EmptyResult()

    def list_snapshots_in_recycle_bin(self) -> str:
        return EmptyResult()

    def list_volumes_in_recycle_bin(self) -> str:
        return EmptyResult()

    def modify_instance_metadata_defaults(self) -> str:
        return EmptyResult()

    def reject_transit_gateway_multicast_domain_associations(self) -> str:
        return EmptyResult()

    def replace_image_criteria_in_allowed_images_settings(self) -> str:
        return EmptyResult()

    def reset_ebs_default_kms_key_id(self) -> str:
        return EmptyResult()

    def accept_address_transfer(self) -> str:
        return EmptyResult()

    def modify_id_format(self) -> str:
        return EmptyResult()

    def modify_identity_id_format(self) -> str:
        return EmptyResult()

    def modify_address_attribute(self) -> str:
        allocation_id = self._get_param("AllocationId", "")
        return EmptyResult()

    def reset_address_attribute(self) -> str:
        allocation_id = self._get_param("AllocationId", "")
        return EmptyResult()

    def modify_availability_zone_group(self) -> str:
        return EmptyResult()

    def modify_default_credit_specification(self) -> str:
        instance_family = self._get_param("InstanceFamily", "")
        cpu_credits = self._get_param("CpuCredits", "standard")
        return EmptyResult()

    def modify_fpga_image_attribute(self) -> str:
        return EmptyResult()

    def reset_fpga_image_attribute(self) -> str:
        return EmptyResult()

    def modify_instance_capacity_reservation_attributes(self) -> str:
        return EmptyResult()

    def modify_instance_credit_specification(self) -> str:
        return EmptyResult()

    def modify_instance_event_start_time(self) -> str:
        instance_event_id = self._get_param("InstanceEventId", "")
        return EmptyResult()

    def modify_instance_maintenance_options(self) -> str:
        instance_id = self._get_param("InstanceId", "")
        auto_recovery = self._get_param("AutoRecovery", "default")
        return EmptyResult()

    def modify_instance_network_performance_options(self) -> str:
        instance_id = self._get_param("InstanceId", "")
        bandwidth_weighting = self._get_param("BandwidthWeighting", "default")
        return EmptyResult()

    def modify_instance_placement(self) -> str:
        return EmptyResult()

    def modify_ipam_resource_cidr(self) -> str:
        resource_cidr = self._get_param("ResourceCidr", "")
        return EmptyResult()

    def modify_ipam_resource_discovery(self) -> str:
        resource_discovery_id = self._get_param("IpamResourceDiscoveryId", "")
        return EmptyResult()

    def modify_ipam_scope(self) -> str:
        scope_id = self._get_param("IpamScopeId", "")
        return EmptyResult()

    def modify_local_gateway_route(self) -> str:
        route_table_id = self._get_param("LocalGatewayRouteTableId", "")
        return EmptyResult()

    def modify_private_dns_name_options(self) -> str:
        return EmptyResult()

    def modify_reserved_instances(self) -> str:
        return EmptyResult()

    def modify_transit_gateway_prefix_list_reference(self) -> str:
        route_table_id = self._get_param("TransitGatewayRouteTableId", "")
        prefix_list_id = self._get_param("PrefixListId", "")
        return EmptyResult()

    def modify_vpc_endpoint_connection_notification(self) -> str:
        return EmptyResult()

    def modify_vpc_endpoint_service_payer_responsibility(self) -> str:
        return EmptyResult()

    def modify_vpn_connection(self) -> str:
        vpn_connection_id = self._get_param("VpnConnectionId", "")
        return EmptyResult()

    def modify_vpn_connection_options(self) -> str:
        vpn_connection_id = self._get_param("VpnConnectionId", "")
        return EmptyResult()

    def modify_vpn_tunnel_certificate(self) -> str:
        vpn_connection_id = self._get_param("VpnConnectionId", "")
        return EmptyResult()

    def modify_vpn_tunnel_options(self) -> str:
        vpn_connection_id = self._get_param("VpnConnectionId", "")
        return EmptyResult()

    def move_address_to_vpc(self) -> str:
        return EmptyResult()

    def move_byoip_cidr_to_ipam(self) -> str:
        cidr = self._get_param("Cidr", "")
        return EmptyResult()

    def purchase_scheduled_instances(self) -> str:
        return EmptyResult()

    def register_instance_event_notification_attributes(self) -> str:
        return EmptyResult()

    def register_transit_gateway_multicast_group_members(self) -> str:
        domain_id = self._get_param("TransitGatewayMulticastDomainId", "")
        return EmptyResult()

    def register_transit_gateway_multicast_group_sources(self) -> str:
        domain_id = self._get_param("TransitGatewayMulticastDomainId", "")
        return EmptyResult()

    def replace_vpn_tunnel(self) -> str:
        return EmptyResult()

    def restore_address_to_classic(self) -> str:
        public_ip = self._get_param("PublicIp", "")
        return EmptyResult()

    def revoke_client_vpn_ingress(self) -> str:
        return EmptyResult()

    def run_scheduled_instances(self) -> str:
        return EmptyResult()

    def search_transit_gateway_multicast_groups(self) -> str:
        return EmptyResult()

    def send_diagnostic_interrupt(self) -> str:
        return EmptyResult()

    def start_vpc_endpoint_service_private_dns_verification(self) -> str:
        return EmptyResult()

    def lock_snapshot(self) -> str:
        snapshot_id = self._get_param("SnapshotId", "")
        lock_mode = self._get_param("LockMode", "governance")
        return EmptyResult()

    def unlock_snapshot(self) -> str:
        snapshot_id = self._get_param("SnapshotId", "")
        return EmptyResult()

    def unassign_private_nat_gateway_address(self) -> str:
        nat_gateway_id = self._get_param("NatGatewayId", "")
        return EmptyResult()

    def withdraw_byoip_cidr(self) -> str:
        cidr = self._get_param("Cidr", "")
        return EmptyResult()

    def restore_image_from_recycle_bin(self) -> str:
        image_id = self._get_param("ImageId", "")
        return EmptyResult()

    def restore_snapshot_from_recycle_bin(self) -> str:
        snapshot_id = self._get_param("SnapshotId", "")
        return EmptyResult()

    def import_client_vpn_client_certificate_revocation_list(self) -> str:
        return EmptyResult()

    def accept_capacity_reservation_billing_ownership(self) -> str:
        return EmptyResult()

    def accept_reserved_instances_exchange_quote(self) -> str:
        return EmptyResult()

    def accept_transit_gateway_vpc_attachment(self) -> str:
        return EmptyResult()

    def advertise_byoip_cidr(self) -> str:
        return EmptyResult()

    def apply_security_groups_to_client_vpn_target_network(self) -> str:
        return EmptyResult()

    def assign_private_nat_gateway_address(self) -> str:
        return EmptyResult()

    def associate_client_vpn_target_network(self) -> str:
        return EmptyResult()

    def associate_enclave_certificate_iam_role(self) -> str:
        return EmptyResult()

    def disassociate_enclave_certificate_iam_role(self) -> ActionResult:
        # Both params accepted but not persisted - EC2-Classic enclave feature stub
        return ActionResult({"Return": True})

    def associate_ipam_byoasn(self) -> str:
        return EmptyResult()

    def associate_ipam_resource_discovery(self) -> str:
        return EmptyResult()

    def associate_nat_gateway_address(self) -> str:
        return EmptyResult()

    def associate_transit_gateway_multicast_domain(self) -> str:
        return EmptyResult()

    def associate_transit_gateway_policy_table(self) -> str:
        return EmptyResult()

    def attach_verified_access_trust_provider(self) -> str:
        return EmptyResult()

    def cancel_conversion_task(self) -> str:
        return EmptyResult()

    def cancel_declarative_policies_report(self) -> str:
        return EmptyResult()

    def cancel_export_task(self) -> str:
        return EmptyResult()

    def cancel_image_launch_permission(self) -> str:
        return EmptyResult()

    def copy_fpga_image(self) -> str:
        return EmptyResult()

    def create_capacity_reservation_by_splitting(self) -> str:
        return EmptyResult()

    def create_client_vpn_route(self) -> str:
        return EmptyResult()

    def create_fpga_image(self) -> str:
        return EmptyResult()

    def create_instance_export_task(self) -> str:
        return EmptyResult()

    def create_ipam_external_resource_verification_token(self) -> str:
        return EmptyResult()

    def create_local_gateway_route_table_virtual_interface_group_association(
        self,
    ) -> str:
        return EmptyResult()

    def create_local_gateway_route_table_vpc_association(self) -> str:
        return EmptyResult()

    def create_network_interface_permission(self) -> str:
        return EmptyResult()

    def create_restore_image_task(self) -> str:
        return EmptyResult()

    def create_transit_gateway_multicast_domain(self) -> str:
        return EmptyResult()

    def create_transit_gateway_policy_table(self) -> str:
        return EmptyResult()

    def bundle_instance(self) -> ActionResult:
        return EmptyResult()

    def cancel_bundle_task(self) -> ActionResult:
        return EmptyResult()

    def cancel_reserved_instances_listing(self) -> ActionResult:
        return EmptyResult()

    def create_reserved_instances_listing(self) -> ActionResult:
        return EmptyResult()

    def purchase_reserved_instances_offering(self) -> ActionResult:
        return EmptyResult()
