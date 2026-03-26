"""Stub responses for EC2 operations not yet fully implemented in Moto."""
from ._base_response import EC2BaseResponse

class GapStubs(EC2BaseResponse):
    """Minimal stubs returning empty results for unimplemented EC2 operations."""

    def accept_transit_gateway_multicast_domain_associations(self) -> str:
        template = self.response_template(EC2_ACCEPT_TRANSIT_GATEWAY_MULTICAST_DOMAIN_ASSOCIATIONS)
        return template.render()

    def cancel_import_task(self) -> str:
        template = self.response_template(EC2_CANCEL_IMPORT_TASK)
        return template.render()

    def create_instance_event_window(self) -> str:
        template = self.response_template(EC2_CREATE_INSTANCE_EVENT_WINDOW)
        return template.render()

    def create_ipam_resource_discovery(self) -> str:
        template = self.response_template(EC2_CREATE_IPAM_RESOURCE_DISCOVERY)
        return template.render()

    def create_network_insights_access_scope(self) -> str:
        template = self.response_template(EC2_CREATE_NETWORK_INSIGHTS_ACCESS_SCOPE)
        return template.render()

    def create_public_ipv4_pool(self) -> str:
        template = self.response_template(EC2_CREATE_PUBLIC_IPV4_POOL)
        return template.render()

    def create_traffic_mirror_filter(self) -> str:
        template = self.response_template(EC2_CREATE_TRAFFIC_MIRROR_FILTER)
        return template.render()

    def create_traffic_mirror_target(self) -> str:
        template = self.response_template(EC2_CREATE_TRAFFIC_MIRROR_TARGET)
        return template.render()

    def create_verified_access_instance(self) -> str:
        template = self.response_template(EC2_CREATE_VERIFIED_ACCESS_INSTANCE)
        return template.render()

    def deregister_transit_gateway_multicast_group_members(self) -> str:
        template = self.response_template(EC2_DEREGISTER_TRANSIT_GATEWAY_MULTICAST_GROUP_MEMBERS)
        return template.render()

    def deregister_transit_gateway_multicast_group_sources(self) -> str:
        template = self.response_template(EC2_DEREGISTER_TRANSIT_GATEWAY_MULTICAST_GROUP_SOURCES)
        return template.render()

    def describe_address_transfers(self) -> str:
        template = self.response_template(EC2_DESCRIBE_ADDRESS_TRANSFERS)
        return template.render()

    def describe_aggregate_id_format(self) -> str:
        template = self.response_template(EC2_DESCRIBE_AGGREGATE_ID_FORMAT)
        return template.render()

    def describe_aws_network_performance_metric_subscriptions(self) -> str:
        template = self.response_template(EC2_DESCRIBE_AWS_NETWORK_PERFORMANCE_METRIC_SUBSCRIPTIONS)
        return template.render()

    def describe_byoip_cidrs(self) -> str:
        template = self.response_template(EC2_DESCRIBE_BYOIP_CIDRS)
        return template.render()

    def describe_capacity_block_extension_history(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CAPACITY_BLOCK_EXTENSION_HISTORY)
        return template.render()

    def describe_capacity_block_status(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CAPACITY_BLOCK_STATUS)
        return template.render()

    def describe_capacity_blocks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CAPACITY_BLOCKS)
        return template.render()

    def describe_capacity_manager_data_exports(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CAPACITY_MANAGER_DATA_EXPORTS)
        return template.render()

    def describe_capacity_reservation_fleets(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CAPACITY_RESERVATION_FLEETS)
        return template.render()

    def describe_capacity_reservation_topology(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CAPACITY_RESERVATION_TOPOLOGY)
        return template.render()

    def describe_capacity_reservations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CAPACITY_RESERVATIONS)
        return template.render()

    def describe_classic_link_instances(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CLASSIC_LINK_INSTANCES)
        return template.render()

    def describe_client_vpn_authorization_rules(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CLIENT_VPN_AUTHORIZATION_RULES)
        return template.render()

    def describe_client_vpn_connections(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CLIENT_VPN_CONNECTIONS)
        return template.render()

    def describe_client_vpn_routes(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CLIENT_VPN_ROUTES)
        return template.render()

    def describe_client_vpn_target_networks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CLIENT_VPN_TARGET_NETWORKS)
        return template.render()

    def describe_coip_pools(self) -> str:
        template = self.response_template(EC2_DESCRIBE_COIP_POOLS)
        return template.render()

    def describe_conversion_tasks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_CONVERSION_TASKS)
        return template.render()

    def describe_declarative_policies_reports(self) -> str:
        template = self.response_template(EC2_DESCRIBE_DECLARATIVE_POLICIES_REPORTS)
        return template.render()

    def describe_elastic_gpus(self) -> str:
        template = self.response_template(EC2_DESCRIBE_ELASTIC_GPUS)
        return template.render()

    def describe_export_image_tasks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_EXPORT_IMAGE_TASKS)
        return template.render()

    def describe_export_tasks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_EXPORT_TASKS)
        return template.render()

    def describe_fast_launch_images(self) -> str:
        template = self.response_template(EC2_DESCRIBE_FAST_LAUNCH_IMAGES)
        return template.render()

    def describe_fast_snapshot_restores(self) -> str:
        template = self.response_template(EC2_DESCRIBE_FAST_SNAPSHOT_RESTORES)
        return template.render()

    def describe_fleet_history(self) -> str:
        template = self.response_template(EC2_DESCRIBE_FLEET_HISTORY)
        return template.render()

    def describe_fpga_image_attribute(self) -> str:
        template = self.response_template(EC2_DESCRIBE_FPGA_IMAGE_ATTRIBUTE)
        return template.render()

    def describe_fpga_images(self) -> str:
        template = self.response_template(EC2_DESCRIBE_FPGA_IMAGES)
        return template.render()

    def describe_host_reservation_offerings(self) -> str:
        template = self.response_template(EC2_DESCRIBE_HOST_RESERVATION_OFFERINGS)
        return template.render()

    def describe_host_reservations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_HOST_RESERVATIONS)
        return template.render()

    def describe_id_format(self) -> str:
        template = self.response_template(EC2_DESCRIBE_ID_FORMAT)
        return template.render()

    def describe_identity_id_format(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IDENTITY_ID_FORMAT)
        return template.render()

    def describe_image_usage_report_entries(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IMAGE_USAGE_REPORT_ENTRIES)
        return template.render()

    def describe_image_usage_reports(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IMAGE_USAGE_REPORTS)
        return template.render()

    def describe_import_image_tasks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IMPORT_IMAGE_TASKS)
        return template.render()

    def describe_import_snapshot_tasks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IMPORT_SNAPSHOT_TASKS)
        return template.render()

    def describe_instance_connect_endpoints(self) -> str:
        template = self.response_template(EC2_DESCRIBE_INSTANCE_CONNECT_ENDPOINTS)
        return template.render()

    def describe_instance_event_notification_attributes(self) -> str:
        template = self.response_template(EC2_DESCRIBE_INSTANCE_EVENT_NOTIFICATION_ATTRIBUTES)
        return template.render()

    def describe_instance_event_windows(self) -> str:
        template = self.response_template(EC2_DESCRIBE_INSTANCE_EVENT_WINDOWS)
        return template.render()

    def describe_instance_image_metadata(self) -> str:
        template = self.response_template(EC2_DESCRIBE_INSTANCE_IMAGE_METADATA)
        return template.render()

    def describe_instance_sql_ha_history_states(self) -> str:
        template = self.response_template(EC2_DESCRIBE_INSTANCE_SQL_HA_HISTORY_STATES)
        return template.render()

    def describe_instance_sql_ha_states(self) -> str:
        template = self.response_template(EC2_DESCRIBE_INSTANCE_SQL_HA_STATES)
        return template.render()

    def describe_instance_topology(self) -> str:
        template = self.response_template(EC2_DESCRIBE_INSTANCE_TOPOLOGY)
        return template.render()

    def describe_ipam_byoasn(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPAM_BYOASN)
        return template.render()

    def describe_ipam_external_resource_verification_tokens(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPAM_EXTERNAL_RESOURCE_VERIFICATION_TOKENS)
        return template.render()

    def describe_ipam_policies(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPAM_POLICIES)
        return template.render()

    def describe_ipam_prefix_list_resolver_targets(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPAM_PREFIX_LIST_RESOLVER_TARGETS)
        return template.render()

    def describe_ipam_prefix_list_resolvers(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPAM_PREFIX_LIST_RESOLVERS)
        return template.render()

    def describe_ipam_resource_discoveries(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPAM_RESOURCE_DISCOVERIES)
        return template.render()

    def describe_ipam_resource_discovery_associations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPAM_RESOURCE_DISCOVERY_ASSOCIATIONS)
        return template.render()

    def describe_ipam_scopes(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPAM_SCOPES)
        return template.render()

    def describe_ipv6_pools(self) -> str:
        template = self.response_template(EC2_DESCRIBE_IPV6_POOLS)
        return template.render()

    def describe_local_gateway_route_table_virtual_interface_group_associations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_LOCAL_GATEWAY_ROUTE_TABLE_VIRTUAL_INTERFACE_GROUP_ASSOCIATIONS)
        return template.render()

    def describe_local_gateway_route_table_vpc_associations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_LOCAL_GATEWAY_ROUTE_TABLE_VPC_ASSOCIATIONS)
        return template.render()

    def describe_local_gateway_route_tables(self) -> str:
        template = self.response_template(EC2_DESCRIBE_LOCAL_GATEWAY_ROUTE_TABLES)
        return template.render()

    def describe_local_gateway_virtual_interface_groups(self) -> str:
        template = self.response_template(EC2_DESCRIBE_LOCAL_GATEWAY_VIRTUAL_INTERFACE_GROUPS)
        return template.render()

    def describe_local_gateway_virtual_interfaces(self) -> str:
        template = self.response_template(EC2_DESCRIBE_LOCAL_GATEWAY_VIRTUAL_INTERFACES)
        return template.render()

    def describe_local_gateways(self) -> str:
        template = self.response_template(EC2_DESCRIBE_LOCAL_GATEWAYS)
        return template.render()

    def describe_locked_snapshots(self) -> str:
        template = self.response_template(EC2_DESCRIBE_LOCKED_SNAPSHOTS)
        return template.render()

    def describe_mac_hosts(self) -> str:
        template = self.response_template(EC2_DESCRIBE_MAC_HOSTS)
        return template.render()

    def describe_mac_modification_tasks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_MAC_MODIFICATION_TASKS)
        return template.render()

    def describe_moving_addresses(self) -> str:
        template = self.response_template(EC2_DESCRIBE_MOVING_ADDRESSES)
        return template.render()

    def describe_network_insights_access_scope_analyses(self) -> str:
        template = self.response_template(EC2_DESCRIBE_NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSES)
        return template.render()

    def describe_network_insights_access_scopes(self) -> str:
        template = self.response_template(EC2_DESCRIBE_NETWORK_INSIGHTS_ACCESS_SCOPES)
        return template.render()

    def describe_network_insights_analyses(self) -> str:
        template = self.response_template(EC2_DESCRIBE_NETWORK_INSIGHTS_ANALYSES)
        return template.render()

    def describe_network_insights_paths(self) -> str:
        template = self.response_template(EC2_DESCRIBE_NETWORK_INSIGHTS_PATHS)
        return template.render()

    def describe_network_interface_permissions(self) -> str:
        template = self.response_template(EC2_DESCRIBE_NETWORK_INTERFACE_PERMISSIONS)
        return template.render()

    def describe_outpost_lags(self) -> str:
        template = self.response_template(EC2_DESCRIBE_OUTPOST_LAGS)
        return template.render()

    def describe_principal_id_format(self) -> str:
        template = self.response_template(EC2_DESCRIBE_PRINCIPAL_ID_FORMAT)
        return template.render()

    def describe_public_ipv4_pools(self) -> str:
        template = self.response_template(EC2_DESCRIBE_PUBLIC_IPV4_POOLS)
        return template.render()

    def describe_replace_root_volume_tasks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_REPLACE_ROOT_VOLUME_TASKS)
        return template.render()

    def describe_reserved_instances_modifications(self) -> str:
        template = self.response_template(EC2_DESCRIBE_RESERVED_INSTANCES_MODIFICATIONS)
        return template.render()

    def describe_route_server_endpoints(self) -> str:
        template = self.response_template(EC2_DESCRIBE_ROUTE_SERVER_ENDPOINTS)
        return template.render()

    def describe_route_server_peers(self) -> str:
        template = self.response_template(EC2_DESCRIBE_ROUTE_SERVER_PEERS)
        return template.render()

    def describe_route_servers(self) -> str:
        template = self.response_template(EC2_DESCRIBE_ROUTE_SERVERS)
        return template.render()

    def describe_scheduled_instance_availability(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SCHEDULED_INSTANCE_AVAILABILITY)
        return template.render()

    def describe_scheduled_instances(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SCHEDULED_INSTANCES)
        return template.render()

    def describe_secondary_interfaces(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SECONDARY_INTERFACES)
        return template.render()

    def describe_secondary_networks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SECONDARY_NETWORKS)
        return template.render()

    def describe_secondary_subnets(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SECONDARY_SUBNETS)
        return template.render()

    def describe_security_group_vpc_associations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SECURITY_GROUP_VPC_ASSOCIATIONS)
        return template.render()

    def describe_security_group_references(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SECURITY_GROUP_REFERENCES)
        return template.render()

    def describe_service_link_virtual_interfaces(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SERVICE_LINK_VIRTUAL_INTERFACES)
        return template.render()

    def describe_stale_security_groups(self) -> str:
        template = self.response_template(EC2_DESCRIBE_STALE_SECURITY_GROUPS)
        return template.render()

    def describe_snapshot_tier_status(self) -> str:
        template = self.response_template(EC2_DESCRIBE_SNAPSHOT_TIER_STATUS)
        return template.render()

    def describe_store_image_tasks(self) -> str:
        template = self.response_template(EC2_DESCRIBE_STORE_IMAGE_TASKS)
        return template.render()

    def describe_traffic_mirror_filter_rules(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRAFFIC_MIRROR_FILTER_RULES)
        return template.render()

    def describe_traffic_mirror_filters(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRAFFIC_MIRROR_FILTERS)
        return template.render()

    def describe_traffic_mirror_sessions(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRAFFIC_MIRROR_SESSIONS)
        return template.render()

    def describe_traffic_mirror_targets(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRAFFIC_MIRROR_TARGETS)
        return template.render()

    def describe_transit_gateway_connect_peers(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRANSIT_GATEWAY_CONNECT_PEERS)
        return template.render()

    def describe_transit_gateway_connects(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRANSIT_GATEWAY_CONNECTS)
        return template.render()

    def describe_transit_gateway_metering_policies(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRANSIT_GATEWAY_METERING_POLICIES)
        return template.render()

    def describe_transit_gateway_multicast_domains(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRANSIT_GATEWAY_MULTICAST_DOMAINS)
        return template.render()

    def describe_transit_gateway_policy_tables(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRANSIT_GATEWAY_POLICY_TABLES)
        return template.render()

    def describe_transit_gateway_route_table_announcements(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRANSIT_GATEWAY_ROUTE_TABLE_ANNOUNCEMENTS)
        return template.render()

    def describe_trunk_interface_associations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_TRUNK_INTERFACE_ASSOCIATIONS)
        return template.render()

    def describe_verified_access_endpoints(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VERIFIED_ACCESS_ENDPOINTS)
        return template.render()

    def describe_verified_access_groups(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VERIFIED_ACCESS_GROUPS)
        return template.render()

    def describe_verified_access_instance_logging_configurations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VERIFIED_ACCESS_INSTANCE_LOGGING_CONFIGURATIONS)
        return template.render()

    def describe_verified_access_instances(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VERIFIED_ACCESS_INSTANCES)
        return template.render()

    def describe_verified_access_trust_providers(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VERIFIED_ACCESS_TRUST_PROVIDERS)
        return template.render()

    def describe_vpc_block_public_access_exclusions(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VPC_BLOCK_PUBLIC_ACCESS_EXCLUSIONS)
        return template.render()

    def describe_vpc_block_public_access_options(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VPC_BLOCK_PUBLIC_ACCESS_OPTIONS)
        return template.render()

    def describe_vpc_encryption_controls(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VPC_ENCRYPTION_CONTROLS)
        return template.render()

    def describe_vpc_endpoint_associations(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VPC_ENDPOINT_ASSOCIATIONS)
        return template.render()

    def describe_vpc_endpoint_connection_notifications(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VPC_ENDPOINT_CONNECTION_NOTIFICATIONS)
        return template.render()

    def describe_vpc_endpoint_connections(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VPC_ENDPOINT_CONNECTIONS)
        return template.render()

    def describe_vpn_concentrators(self) -> str:
        template = self.response_template(EC2_DESCRIBE_VPN_CONCENTRATORS)
        return template.render()

    def disable_allowed_images_settings(self) -> str:
        template = self.response_template(EC2_DISABLE_ALLOWED_IMAGES_SETTINGS)
        return template.render()

    def disable_aws_network_performance_metric_subscription(self) -> str:
        template = self.response_template(EC2_DISABLE_AWS_NETWORK_PERFORMANCE_METRIC_SUBSCRIPTION)
        return template.render()

    def disable_capacity_manager(self) -> str:
        template = self.response_template(EC2_DISABLE_CAPACITY_MANAGER)
        return template.render()

    def disable_image_block_public_access(self) -> str:
        template = self.response_template(EC2_DISABLE_IMAGE_BLOCK_PUBLIC_ACCESS)
        return template.render()

    def disable_serial_console_access(self) -> str:
        template = self.response_template(EC2_DISABLE_SERIAL_CONSOLE_ACCESS)
        return template.render()

    def disable_snapshot_block_public_access(self) -> str:
        template = self.response_template(EC2_DISABLE_SNAPSHOT_BLOCK_PUBLIC_ACCESS)
        return template.render()

    def enable_aws_network_performance_metric_subscription(self) -> str:
        template = self.response_template(EC2_ENABLE_AWS_NETWORK_PERFORMANCE_METRIC_SUBSCRIPTION)
        return template.render()

    def enable_capacity_manager(self) -> str:
        template = self.response_template(EC2_ENABLE_CAPACITY_MANAGER)
        return template.render()

    def enable_reachability_analyzer_organization_sharing(self) -> str:
        template = self.response_template(EC2_ENABLE_REACHABILITY_ANALYZER_ORGANIZATION_SHARING)
        return template.render()

    def enable_serial_console_access(self) -> str:
        template = self.response_template(EC2_ENABLE_SERIAL_CONSOLE_ACCESS)
        return template.render()

    def get_allowed_images_settings(self) -> str:
        template = self.response_template(EC2_GET_ALLOWED_IMAGES_SETTINGS)
        return template.render()

    def get_aws_network_performance_data(self) -> str:
        template = self.response_template(EC2_GET_AWS_NETWORK_PERFORMANCE_DATA)
        return template.render()

    def get_capacity_manager_attributes(self) -> str:
        template = self.response_template(EC2_GET_CAPACITY_MANAGER_ATTRIBUTES)
        return template.render()

    def get_ebs_default_kms_key_id(self) -> str:
        template = self.response_template(EC2_GET_EBS_DEFAULT_KMS_KEY_ID)
        return template.render()

    def get_enabled_ipam_policy(self) -> str:
        template = self.response_template(EC2_GET_ENABLED_IPAM_POLICY)
        return template.render()

    def get_image_block_public_access_state(self) -> str:
        template = self.response_template(EC2_GET_IMAGE_BLOCK_PUBLIC_ACCESS_STATE)
        return template.render()

    def get_instance_metadata_defaults(self) -> str:
        template = self.response_template(EC2_GET_INSTANCE_METADATA_DEFAULTS)
        return template.render()

    def get_serial_console_access_status(self) -> str:
        template = self.response_template(EC2_GET_SERIAL_CONSOLE_ACCESS_STATUS)
        return template.render()

    def get_snapshot_block_public_access_state(self) -> str:
        template = self.response_template(EC2_GET_SNAPSHOT_BLOCK_PUBLIC_ACCESS_STATE)
        return template.render()

    def get_vpn_connection_device_types(self) -> str:
        template = self.response_template(EC2_GET_VPN_CONNECTION_DEVICE_TYPES)
        return template.render()

    def import_image(self) -> str:
        template = self.response_template(EC2_IMPORT_IMAGE)
        return template.render()

    def import_snapshot(self) -> str:
        template = self.response_template(EC2_IMPORT_SNAPSHOT)
        return template.render()

    def list_images_in_recycle_bin(self) -> str:
        template = self.response_template(EC2_LIST_IMAGES_IN_RECYCLE_BIN)
        return template.render()

    def list_snapshots_in_recycle_bin(self) -> str:
        template = self.response_template(EC2_LIST_SNAPSHOTS_IN_RECYCLE_BIN)
        return template.render()

    def list_volumes_in_recycle_bin(self) -> str:
        template = self.response_template(EC2_LIST_VOLUMES_IN_RECYCLE_BIN)
        return template.render()

    def modify_instance_metadata_defaults(self) -> str:
        template = self.response_template(EC2_MODIFY_INSTANCE_METADATA_DEFAULTS)
        return template.render()

    def reject_transit_gateway_multicast_domain_associations(self) -> str:
        template = self.response_template(EC2_REJECT_TRANSIT_GATEWAY_MULTICAST_DOMAIN_ASSOCIATIONS)
        return template.render()

    def replace_image_criteria_in_allowed_images_settings(self) -> str:
        template = self.response_template(EC2_REPLACE_IMAGE_CRITERIA_IN_ALLOWED_IMAGES_SETTINGS)
        return template.render()

    def reset_ebs_default_kms_key_id(self) -> str:
        template = self.response_template(EC2_RESET_EBS_DEFAULT_KMS_KEY_ID)
        return template.render()

    def accept_capacity_reservation_billing_ownership(self) -> str:
        template = self.response_template(EC2_ACCEPT_CAPACITY_RESERVATION_BILLING_OWNERSHIP)
        return template.render()

    def accept_reserved_instances_exchange_quote(self) -> str:
        template = self.response_template(EC2_ACCEPT_RESERVED_INSTANCES_EXCHANGE_QUOTE)
        return template.render()

    def accept_transit_gateway_vpc_attachment(self) -> str:
        template = self.response_template(EC2_ACCEPT_TRANSIT_GATEWAY_VPC_ATTACHMENT)
        return template.render()

    def advertise_byoip_cidr(self) -> str:
        template = self.response_template(EC2_ADVERTISE_BYOIP_CIDR)
        return template.render()

    def apply_security_groups_to_client_vpn_target_network(self) -> str:
        template = self.response_template(EC2_APPLY_SECURITY_GROUPS_TO_CLIENT_VPN_TARGET_NETWORK)
        return template.render()

    def assign_private_nat_gateway_address(self) -> str:
        template = self.response_template(EC2_ASSIGN_PRIVATE_NAT_GATEWAY_ADDRESS)
        return template.render()

    def associate_client_vpn_target_network(self) -> str:
        template = self.response_template(EC2_ASSOCIATE_CLIENT_VPN_TARGET_NETWORK)
        return template.render()

    def associate_enclave_certificate_iam_role(self) -> str:
        template = self.response_template(EC2_ASSOCIATE_ENCLAVE_CERTIFICATE_IAM_ROLE)
        return template.render()

    def associate_ipam_byoasn(self) -> str:
        template = self.response_template(EC2_ASSOCIATE_IPAM_BYOASN)
        return template.render()

    def associate_ipam_resource_discovery(self) -> str:
        template = self.response_template(EC2_ASSOCIATE_IPAM_RESOURCE_DISCOVERY)
        return template.render()

    def associate_nat_gateway_address(self) -> str:
        template = self.response_template(EC2_ASSOCIATE_NAT_GATEWAY_ADDRESS)
        return template.render()

    def associate_transit_gateway_multicast_domain(self) -> str:
        template = self.response_template(EC2_ASSOCIATE_TRANSIT_GATEWAY_MULTICAST_DOMAIN)
        return template.render()

    def associate_transit_gateway_policy_table(self) -> str:
        template = self.response_template(EC2_ASSOCIATE_TRANSIT_GATEWAY_POLICY_TABLE)
        return template.render()

    def attach_classic_link_vpc(self) -> str:
        template = self.response_template(EC2_ATTACH_CLASSIC_LINK_VPC)
        return template.render()

    def attach_verified_access_trust_provider(self) -> str:
        template = self.response_template(EC2_ATTACH_VERIFIED_ACCESS_TRUST_PROVIDER)
        return template.render()

    def bundle_instance(self) -> str:
        template = self.response_template(EC2_BUNDLE_INSTANCE)
        return template.render()

    def cancel_bundle_task(self) -> str:
        template = self.response_template(EC2_CANCEL_BUNDLE_TASK)
        return template.render()

    def cancel_conversion_task(self) -> str:
        template = self.response_template(EC2_CANCEL_CONVERSION_TASK)
        return template.render()

    def cancel_declarative_policies_report(self) -> str:
        template = self.response_template(EC2_CANCEL_DECLARATIVE_POLICIES_REPORT)
        return template.render()

    def cancel_export_task(self) -> str:
        template = self.response_template(EC2_CANCEL_EXPORT_TASK)
        return template.render()

    def cancel_image_launch_permission(self) -> str:
        template = self.response_template(EC2_CANCEL_IMAGE_LAUNCH_PERMISSION)
        return template.render()

    def cancel_reserved_instances_listing(self) -> str:
        template = self.response_template(EC2_CANCEL_RESERVED_INSTANCES_LISTING)
        return template.render()

    def copy_fpga_image(self) -> str:
        template = self.response_template(EC2_COPY_FPGA_IMAGE)
        return template.render()

    def create_capacity_reservation_by_splitting(self) -> str:
        template = self.response_template(EC2_CREATE_CAPACITY_RESERVATION_BY_SPLITTING)
        return template.render()

    def create_client_vpn_route(self) -> str:
        template = self.response_template(EC2_CREATE_CLIENT_VPN_ROUTE)
        return template.render()

    def create_fpga_image(self) -> str:
        template = self.response_template(EC2_CREATE_FPGA_IMAGE)
        return template.render()

    def create_instance_export_task(self) -> str:
        template = self.response_template(EC2_CREATE_INSTANCE_EXPORT_TASK)
        return template.render()

    def create_ipam_external_resource_verification_token(self) -> str:
        template = self.response_template(EC2_CREATE_IPAM_EXTERNAL_RESOURCE_VERIFICATION_TOKEN)
        return template.render()

    def create_local_gateway_route_table_virtual_interface_group_association(self) -> str:
        template = self.response_template(EC2_CREATE_LOCAL_GATEWAY_ROUTE_TABLE_VIRTUAL_INTERFACE_GROUP_ASSOCIATION)
        return template.render()

    def create_local_gateway_route_table_vpc_association(self) -> str:
        template = self.response_template(EC2_CREATE_LOCAL_GATEWAY_ROUTE_TABLE_VPC_ASSOCIATION)
        return template.render()

    def create_network_interface_permission(self) -> str:
        template = self.response_template(EC2_CREATE_NETWORK_INTERFACE_PERMISSION)
        return template.render()

    def create_reserved_instances_listing(self) -> str:
        template = self.response_template(EC2_CREATE_RESERVED_INSTANCES_LISTING)
        return template.render()

    def create_restore_image_task(self) -> str:
        template = self.response_template(EC2_CREATE_RESTORE_IMAGE_TASK)
        return template.render()

    def create_transit_gateway_multicast_domain(self) -> str:
        template = self.response_template(EC2_CREATE_TRANSIT_GATEWAY_MULTICAST_DOMAIN)
        return template.render()

    def create_transit_gateway_policy_table(self) -> str:
        template = self.response_template(EC2_CREATE_TRANSIT_GATEWAY_POLICY_TABLE)
        return template.render()


# --- XML Response Templates ---

EC2_ACCEPT_TRANSIT_GATEWAY_MULTICAST_DOMAIN_ASSOCIATIONS = """<AcceptTransitGatewayMulticastDomainAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</AcceptTransitGatewayMulticastDomainAssociationsResponse>"""

EC2_CANCEL_IMPORT_TASK = """<CancelImportTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</CancelImportTaskResponse>"""

EC2_CREATE_INSTANCE_EVENT_WINDOW = """<CreateInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</CreateInstanceEventWindowResponse>"""

EC2_CREATE_IPAM_RESOURCE_DISCOVERY = """<CreateIpamResourceDiscoveryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</CreateIpamResourceDiscoveryResponse>"""

EC2_CREATE_NETWORK_INSIGHTS_ACCESS_SCOPE = """<CreateNetworkInsightsAccessScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</CreateNetworkInsightsAccessScopeResponse>"""

EC2_CREATE_PUBLIC_IPV4_POOL = """<CreatePublicIpv4PoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</CreatePublicIpv4PoolResponse>"""

EC2_CREATE_TRAFFIC_MIRROR_FILTER = """<CreateTrafficMirrorFilterResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</CreateTrafficMirrorFilterResponse>"""

EC2_CREATE_TRAFFIC_MIRROR_TARGET = """<CreateTrafficMirrorTargetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</CreateTrafficMirrorTargetResponse>"""

EC2_CREATE_VERIFIED_ACCESS_INSTANCE = """<CreateVerifiedAccessInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</CreateVerifiedAccessInstanceResponse>"""

EC2_DEREGISTER_TRANSIT_GATEWAY_MULTICAST_GROUP_MEMBERS = """<DeregisterTransitGatewayMulticastGroupMembersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</DeregisterTransitGatewayMulticastGroupMembersResponse>"""

EC2_DEREGISTER_TRANSIT_GATEWAY_MULTICAST_GROUP_SOURCES = """<DeregisterTransitGatewayMulticastGroupSourcesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</DeregisterTransitGatewayMulticastGroupSourcesResponse>"""

EC2_DESCRIBE_ADDRESS_TRANSFERS = """<DescribeAddressTransfersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <addressTransfersSet/>
</DescribeAddressTransfersResponse>"""

EC2_DESCRIBE_AGGREGATE_ID_FORMAT = """<DescribeAggregateIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <aggregateIdFormatSet/>
</DescribeAggregateIdFormatResponse>"""

EC2_DESCRIBE_AWS_NETWORK_PERFORMANCE_METRIC_SUBSCRIPTIONS = """<DescribeAwsNetworkPerformanceMetricSubscriptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <awsNetworkPerformanceMetricSubscriptionsSet/>
</DescribeAwsNetworkPerformanceMetricSubscriptionsResponse>"""

EC2_DESCRIBE_BYOIP_CIDRS = """<DescribeByoipCidrsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <byoipCidrSet/>
</DescribeByoipCidrsResponse>"""

EC2_DESCRIBE_CAPACITY_BLOCK_EXTENSION_HISTORY = """<DescribeCapacityBlockExtensionHistoryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <capacityBlockExtensionHistorySet/>
</DescribeCapacityBlockExtensionHistoryResponse>"""

EC2_DESCRIBE_CAPACITY_BLOCK_STATUS = """<DescribeCapacityBlockStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <capacityBlockStatusSet/>
</DescribeCapacityBlockStatusResponse>"""

EC2_DESCRIBE_CAPACITY_BLOCKS = """<DescribeCapacityBlocksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <capacityBlocksSet/>
</DescribeCapacityBlocksResponse>"""

EC2_DESCRIBE_CAPACITY_MANAGER_DATA_EXPORTS = """<DescribeCapacityManagerDataExportsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <capacityManagerDataExportsSet/>
</DescribeCapacityManagerDataExportsResponse>"""

EC2_DESCRIBE_CAPACITY_RESERVATION_FLEETS = """<DescribeCapacityReservationFleetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <capacityReservationFleetsSet/>
</DescribeCapacityReservationFleetsResponse>"""

EC2_DESCRIBE_CAPACITY_RESERVATION_TOPOLOGY = """<DescribeCapacityReservationTopologyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <capacityReservationTopologySet/>
</DescribeCapacityReservationTopologyResponse>"""

EC2_DESCRIBE_CAPACITY_RESERVATIONS = """<DescribeCapacityReservationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <capacityReservationsSet/>
</DescribeCapacityReservationsResponse>"""

EC2_DESCRIBE_CLASSIC_LINK_INSTANCES = """<DescribeClassicLinkInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <classicLinkInstancesSet/>
</DescribeClassicLinkInstancesResponse>"""

EC2_DESCRIBE_CLIENT_VPN_AUTHORIZATION_RULES = """<DescribeClientVpnAuthorizationRulesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <authorizationRuleSet/>
</DescribeClientVpnAuthorizationRulesResponse>"""

EC2_DESCRIBE_CLIENT_VPN_CONNECTIONS = """<DescribeClientVpnConnectionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <connectionSet/>
</DescribeClientVpnConnectionsResponse>"""

EC2_DESCRIBE_CLIENT_VPN_ROUTES = """<DescribeClientVpnRoutesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <routeSet/>
</DescribeClientVpnRoutesResponse>"""

EC2_DESCRIBE_CLIENT_VPN_TARGET_NETWORKS = """<DescribeClientVpnTargetNetworksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <targetNetworkSet/>
</DescribeClientVpnTargetNetworksResponse>"""

EC2_DESCRIBE_COIP_POOLS = """<DescribeCoipPoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <coipPoolsSet/>
</DescribeCoipPoolsResponse>"""

EC2_DESCRIBE_CONVERSION_TASKS = """<DescribeConversionTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <conversionTasksSet/>
</DescribeConversionTasksResponse>"""

EC2_DESCRIBE_DECLARATIVE_POLICIES_REPORTS = """<DescribeDeclarativePoliciesReportsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <declarativePoliciesReportsSet/>
</DescribeDeclarativePoliciesReportsResponse>"""

EC2_DESCRIBE_ELASTIC_GPUS = """<DescribeElasticGpusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <elasticGpusSet/>
</DescribeElasticGpusResponse>"""

EC2_DESCRIBE_EXPORT_IMAGE_TASKS = """<DescribeExportImageTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <exportImageTasksSet/>
</DescribeExportImageTasksResponse>"""

EC2_DESCRIBE_EXPORT_TASKS = """<DescribeExportTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <exportTasksSet/>
</DescribeExportTasksResponse>"""

EC2_DESCRIBE_FAST_LAUNCH_IMAGES = """<DescribeFastLaunchImagesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <fastLaunchImagesSet/>
</DescribeFastLaunchImagesResponse>"""

EC2_DESCRIBE_FAST_SNAPSHOT_RESTORES = """<DescribeFastSnapshotRestoresResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <fastSnapshotRestoresSet/>
</DescribeFastSnapshotRestoresResponse>"""

EC2_DESCRIBE_FLEET_HISTORY = """<DescribeFleetHistoryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <historyRecordSet/>
</DescribeFleetHistoryResponse>"""

EC2_DESCRIBE_FPGA_IMAGE_ATTRIBUTE = """<DescribeFpgaImageAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <fpgaImageAttribute/>
</DescribeFpgaImageAttributeResponse>"""

EC2_DESCRIBE_FPGA_IMAGES = """<DescribeFpgaImagesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <fpgaImagesSet/>
</DescribeFpgaImagesResponse>"""

EC2_DESCRIBE_HOST_RESERVATION_OFFERINGS = """<DescribeHostReservationOfferingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <hostReservationOfferingsSet/>
</DescribeHostReservationOfferingsResponse>"""

EC2_DESCRIBE_HOST_RESERVATIONS = """<DescribeHostReservationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <hostReservationsSet/>
</DescribeHostReservationsResponse>"""

EC2_DESCRIBE_ID_FORMAT = """<DescribeIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <idFormatSet/>
</DescribeIdFormatResponse>"""

EC2_DESCRIBE_IDENTITY_ID_FORMAT = """<DescribeIdentityIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <idFormatSet/>
</DescribeIdentityIdFormatResponse>"""

EC2_DESCRIBE_IMAGE_USAGE_REPORT_ENTRIES = """<DescribeImageUsageReportEntriesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <imageUsageReportEntriesSet/>
</DescribeImageUsageReportEntriesResponse>"""

EC2_DESCRIBE_IMAGE_USAGE_REPORTS = """<DescribeImageUsageReportsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <imageUsageReportsSet/>
</DescribeImageUsageReportsResponse>"""

EC2_DESCRIBE_IMPORT_IMAGE_TASKS = """<DescribeImportImageTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <importImageTasksSet/>
</DescribeImportImageTasksResponse>"""

EC2_DESCRIBE_IMPORT_SNAPSHOT_TASKS = """<DescribeImportSnapshotTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <importSnapshotTasksSet/>
</DescribeImportSnapshotTasksResponse>"""

EC2_DESCRIBE_INSTANCE_CONNECT_ENDPOINTS = """<DescribeInstanceConnectEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <instanceConnectEndpointsSet/>
</DescribeInstanceConnectEndpointsResponse>"""

EC2_DESCRIBE_INSTANCE_EVENT_NOTIFICATION_ATTRIBUTES = """<DescribeInstanceEventNotificationAttributesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <instanceEventNotificationAttributesSet/>
</DescribeInstanceEventNotificationAttributesResponse>"""

EC2_DESCRIBE_INSTANCE_EVENT_WINDOWS = """<DescribeInstanceEventWindowsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <instanceEventWindowsSet/>
</DescribeInstanceEventWindowsResponse>"""

EC2_DESCRIBE_INSTANCE_IMAGE_METADATA = """<DescribeInstanceImageMetadataResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <instanceImageMetadataSet/>
</DescribeInstanceImageMetadataResponse>"""

EC2_DESCRIBE_INSTANCE_SQL_HA_HISTORY_STATES = """<DescribeInstanceSqlHaHistoryStatesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <instanceSqlHaHistoryStatesSet/>
</DescribeInstanceSqlHaHistoryStatesResponse>"""

EC2_DESCRIBE_INSTANCE_SQL_HA_STATES = """<DescribeInstanceSqlHaStatesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <instanceSqlHaStatesSet/>
</DescribeInstanceSqlHaStatesResponse>"""

EC2_DESCRIBE_INSTANCE_TOPOLOGY = """<DescribeInstanceTopologyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <instanceTopologySet/>
</DescribeInstanceTopologyResponse>"""

EC2_DESCRIBE_IPAM_BYOASN = """<DescribeIpamByoasnResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamByoasnSet/>
</DescribeIpamByoasnResponse>"""

EC2_DESCRIBE_IPAM_EXTERNAL_RESOURCE_VERIFICATION_TOKENS = """<DescribeIpamExternalResourceVerificationTokensResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamExternalResourceVerificationTokensSet/>
</DescribeIpamExternalResourceVerificationTokensResponse>"""

EC2_DESCRIBE_IPAM_POLICIES = """<DescribeIpamPoliciesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamPoliciesSet/>
</DescribeIpamPoliciesResponse>"""

EC2_DESCRIBE_IPAM_PREFIX_LIST_RESOLVER_TARGETS = """<DescribeIpamPrefixListResolverTargetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamPrefixResolverTargetsSet/>
</DescribeIpamPrefixListResolverTargetsResponse>"""

EC2_DESCRIBE_IPAM_PREFIX_LIST_RESOLVERS = """<DescribeIpamPrefixListResolversResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamPrefixResolversSet/>
</DescribeIpamPrefixListResolversResponse>"""

EC2_DESCRIBE_IPAM_RESOURCE_DISCOVERIES = """<DescribeIpamResourceDiscoveriesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamResourceDiscoveriesSet/>
</DescribeIpamResourceDiscoveriesResponse>"""

EC2_DESCRIBE_IPAM_RESOURCE_DISCOVERY_ASSOCIATIONS = """<DescribeIpamResourceDiscoveryAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamResourceDiscoveryAssociationsSet/>
</DescribeIpamResourceDiscoveryAssociationsResponse>"""

EC2_DESCRIBE_IPAM_SCOPES = """<DescribeIpamScopesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamScopesSet/>
</DescribeIpamScopesResponse>"""

EC2_DESCRIBE_IPV6_POOLS = """<DescribeIpv6PoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipv6PoolsSet/>
</DescribeIpv6PoolsResponse>"""

EC2_DESCRIBE_LOCAL_GATEWAY_ROUTE_TABLE_VIRTUAL_INTERFACE_GROUP_ASSOCIATIONS = """<DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <localGatewayRouteTableVirtualInterfaceGroupAssociationsSet/>
</DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResponse>"""

EC2_DESCRIBE_LOCAL_GATEWAY_ROUTE_TABLE_VPC_ASSOCIATIONS = """<DescribeLocalGatewayRouteTableVpcAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <localGatewayRouteTableVpcAssociationsSet/>
</DescribeLocalGatewayRouteTableVpcAssociationsResponse>"""

EC2_DESCRIBE_LOCAL_GATEWAY_ROUTE_TABLES = """<DescribeLocalGatewayRouteTablesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <localGatewayRouteTablesSet/>
</DescribeLocalGatewayRouteTablesResponse>"""

EC2_DESCRIBE_LOCAL_GATEWAY_VIRTUAL_INTERFACE_GROUPS = """<DescribeLocalGatewayVirtualInterfaceGroupsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <localGatewayVirtualInterfaceGroupsSet/>
</DescribeLocalGatewayVirtualInterfaceGroupsResponse>"""

EC2_DESCRIBE_LOCAL_GATEWAY_VIRTUAL_INTERFACES = """<DescribeLocalGatewayVirtualInterfacesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <localGatewayVirtualInterfacesSet/>
</DescribeLocalGatewayVirtualInterfacesResponse>"""

EC2_DESCRIBE_LOCAL_GATEWAYS = """<DescribeLocalGatewaysResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <localGatewaysSet/>
</DescribeLocalGatewaysResponse>"""

EC2_DESCRIBE_LOCKED_SNAPSHOTS = """<DescribeLockedSnapshotsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <lockedSnapshotsSet/>
</DescribeLockedSnapshotsResponse>"""

EC2_DESCRIBE_MAC_HOSTS = """<DescribeMacHostsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <macHostsSet/>
</DescribeMacHostsResponse>"""

EC2_DESCRIBE_MAC_MODIFICATION_TASKS = """<DescribeMacModificationTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <macModificationTasksSet/>
</DescribeMacModificationTasksResponse>"""

EC2_DESCRIBE_MOVING_ADDRESSES = """<DescribeMovingAddressesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <movingAddressesSet/>
</DescribeMovingAddressesResponse>"""

EC2_DESCRIBE_NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSES = """<DescribeNetworkInsightsAccessScopeAnalysesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <networkInsightsAccessScopeAnalysesSet/>
</DescribeNetworkInsightsAccessScopeAnalysesResponse>"""

EC2_DESCRIBE_NETWORK_INSIGHTS_ACCESS_SCOPES = """<DescribeNetworkInsightsAccessScopesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <networkInsightsAccessScopesSet/>
</DescribeNetworkInsightsAccessScopesResponse>"""

EC2_DESCRIBE_NETWORK_INSIGHTS_ANALYSES = """<DescribeNetworkInsightsAnalysesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <networkInsightsAnalysesSet/>
</DescribeNetworkInsightsAnalysesResponse>"""

EC2_DESCRIBE_NETWORK_INSIGHTS_PATHS = """<DescribeNetworkInsightsPathsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <networkInsightsPathsSet/>
</DescribeNetworkInsightsPathsResponse>"""

EC2_DESCRIBE_NETWORK_INTERFACE_PERMISSIONS = """<DescribeNetworkInterfacePermissionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <networkInterfacePermissionsSet/>
</DescribeNetworkInterfacePermissionsResponse>"""

EC2_DESCRIBE_OUTPOST_LAGS = """<DescribeOutpostLagsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <outpostLagsSet/>
</DescribeOutpostLagsResponse>"""

EC2_DESCRIBE_PRINCIPAL_ID_FORMAT = """<DescribePrincipalIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <principalIdFormatSet/>
</DescribePrincipalIdFormatResponse>"""

EC2_DESCRIBE_PUBLIC_IPV4_POOLS = """<DescribePublicIpv4PoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <publicIpv4PoolSet/>
</DescribePublicIpv4PoolsResponse>"""

EC2_DESCRIBE_REPLACE_ROOT_VOLUME_TASKS = """<DescribeReplaceRootVolumeTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <replaceRootVolumeTaskSet/>
</DescribeReplaceRootVolumeTasksResponse>"""

EC2_DESCRIBE_RESERVED_INSTANCES_MODIFICATIONS = """<DescribeReservedInstancesModificationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <reservedInstancesModificationsSet/>
</DescribeReservedInstancesModificationsResponse>"""

EC2_DESCRIBE_ROUTE_SERVER_ENDPOINTS = """<DescribeRouteServerEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <routeServerEndpointsSet/>
</DescribeRouteServerEndpointsResponse>"""

EC2_DESCRIBE_ROUTE_SERVER_PEERS = """<DescribeRouteServerPeersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <routeServerPeersSet/>
</DescribeRouteServerPeersResponse>"""

EC2_DESCRIBE_ROUTE_SERVERS = """<DescribeRouteServersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <routeServersSet/>
</DescribeRouteServersResponse>"""

EC2_DESCRIBE_SCHEDULED_INSTANCE_AVAILABILITY = """<DescribeScheduledInstanceAvailabilityResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <scheduledInstanceAvailabilitySet/>
</DescribeScheduledInstanceAvailabilityResponse>"""

EC2_DESCRIBE_SCHEDULED_INSTANCES = """<DescribeScheduledInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <scheduledInstanceSet/>
</DescribeScheduledInstancesResponse>"""

EC2_DESCRIBE_SECONDARY_INTERFACES = """<DescribeSecondaryInterfacesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <secondaryInterfacesSet/>
</DescribeSecondaryInterfacesResponse>"""

EC2_DESCRIBE_SECONDARY_NETWORKS = """<DescribeSecondaryNetworksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <secondaryNetworksSet/>
</DescribeSecondaryNetworksResponse>"""

EC2_DESCRIBE_SECONDARY_SUBNETS = """<DescribeSecondarySubnetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <secondarySubnetsSet/>
</DescribeSecondarySubnetsResponse>"""

EC2_DESCRIBE_SECURITY_GROUP_REFERENCES = """<DescribeSecurityGroupReferencesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <securityGroupReferenceSet/>
</DescribeSecurityGroupReferencesResponse>"""

EC2_DESCRIBE_SECURITY_GROUP_VPC_ASSOCIATIONS = """<DescribeSecurityGroupVpcAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <securityGroupVpcAssociationsSet/>
</DescribeSecurityGroupVpcAssociationsResponse>"""

EC2_DESCRIBE_SERVICE_LINK_VIRTUAL_INTERFACES = """<DescribeServiceLinkVirtualInterfacesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <serviceLinkVirtualInterfacesSet/>
</DescribeServiceLinkVirtualInterfacesResponse>"""

EC2_DESCRIBE_STALE_SECURITY_GROUPS = """<DescribeStaleSecurityGroupsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <staleSecurityGroupSet/>
</DescribeStaleSecurityGroupsResponse>"""

EC2_DESCRIBE_SNAPSHOT_TIER_STATUS = """<DescribeSnapshotTierStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <snapshotTierStatusSet/>
</DescribeSnapshotTierStatusResponse>"""

EC2_DESCRIBE_STORE_IMAGE_TASKS = """<DescribeStoreImageTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <storeImageTaskResultSet/>
</DescribeStoreImageTasksResponse>"""

EC2_DESCRIBE_TRAFFIC_MIRROR_FILTER_RULES = """<DescribeTrafficMirrorFilterRulesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <trafficMirrorFilterRulesSet/>
</DescribeTrafficMirrorFilterRulesResponse>"""

EC2_DESCRIBE_TRAFFIC_MIRROR_FILTERS = """<DescribeTrafficMirrorFiltersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <trafficMirrorFiltersSet/>
</DescribeTrafficMirrorFiltersResponse>"""

EC2_DESCRIBE_TRAFFIC_MIRROR_SESSIONS = """<DescribeTrafficMirrorSessionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <trafficMirrorSessionsSet/>
</DescribeTrafficMirrorSessionsResponse>"""

EC2_DESCRIBE_TRAFFIC_MIRROR_TARGETS = """<DescribeTrafficMirrorTargetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <trafficMirrorTargetsSet/>
</DescribeTrafficMirrorTargetsResponse>"""

EC2_DESCRIBE_TRANSIT_GATEWAY_CONNECT_PEERS = """<DescribeTransitGatewayConnectPeersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <transitGatewayConnectPeersSet/>
</DescribeTransitGatewayConnectPeersResponse>"""

EC2_DESCRIBE_TRANSIT_GATEWAY_CONNECTS = """<DescribeTransitGatewayConnectsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <transitGatewayConnectsSet/>
</DescribeTransitGatewayConnectsResponse>"""

EC2_DESCRIBE_TRANSIT_GATEWAY_METERING_POLICIES = """<DescribeTransitGatewayMeteringPoliciesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <transitGatewayMeteringPoliciesSet/>
</DescribeTransitGatewayMeteringPoliciesResponse>"""

EC2_DESCRIBE_TRANSIT_GATEWAY_MULTICAST_DOMAINS = """<DescribeTransitGatewayMulticastDomainsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <transitGatewayMulticastDomainsSet/>
</DescribeTransitGatewayMulticastDomainsResponse>"""

EC2_DESCRIBE_TRANSIT_GATEWAY_POLICY_TABLES = """<DescribeTransitGatewayPolicyTablesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <transitGatewayPolicyTablesSet/>
</DescribeTransitGatewayPolicyTablesResponse>"""

EC2_DESCRIBE_TRANSIT_GATEWAY_ROUTE_TABLE_ANNOUNCEMENTS = """<DescribeTransitGatewayRouteTableAnnouncementsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <transitGatewayRouteTableAnnouncementsSet/>
</DescribeTransitGatewayRouteTableAnnouncementsResponse>"""

EC2_DESCRIBE_TRUNK_INTERFACE_ASSOCIATIONS = """<DescribeTrunkInterfaceAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <interfaceAssociationSet/>
</DescribeTrunkInterfaceAssociationsResponse>"""

EC2_DESCRIBE_VERIFIED_ACCESS_ENDPOINTS = """<DescribeVerifiedAccessEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <verifiedAccessEndpointSet/>
</DescribeVerifiedAccessEndpointsResponse>"""

EC2_DESCRIBE_VERIFIED_ACCESS_GROUPS = """<DescribeVerifiedAccessGroupsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <verifiedAccessGroupSet/>
</DescribeVerifiedAccessGroupsResponse>"""

EC2_DESCRIBE_VERIFIED_ACCESS_INSTANCE_LOGGING_CONFIGURATIONS = """<DescribeVerifiedAccessInstanceLoggingConfigurationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <loggingConfigurationSet/>
</DescribeVerifiedAccessInstanceLoggingConfigurationsResponse>"""

EC2_DESCRIBE_VERIFIED_ACCESS_INSTANCES = """<DescribeVerifiedAccessInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <verifiedAccessInstanceSet/>
</DescribeVerifiedAccessInstancesResponse>"""

EC2_DESCRIBE_VERIFIED_ACCESS_TRUST_PROVIDERS = """<DescribeVerifiedAccessTrustProvidersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <verifiedAccessTrustProviderSet/>
</DescribeVerifiedAccessTrustProvidersResponse>"""

EC2_DESCRIBE_VPC_BLOCK_PUBLIC_ACCESS_EXCLUSIONS = """<DescribeVpcBlockPublicAccessExclusionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <vpcBlockPublicAccessExclusionsSet/>
</DescribeVpcBlockPublicAccessExclusionsResponse>"""

EC2_DESCRIBE_VPC_BLOCK_PUBLIC_ACCESS_OPTIONS = """<DescribeVpcBlockPublicAccessOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <vpcBlockPublicAccessOptionsSet/>
</DescribeVpcBlockPublicAccessOptionsResponse>"""

EC2_DESCRIBE_VPC_ENCRYPTION_CONTROLS = """<DescribeVpcEncryptionControlsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <vpcEncryptionControlsSet/>
</DescribeVpcEncryptionControlsResponse>"""

EC2_DESCRIBE_VPC_ENDPOINT_ASSOCIATIONS = """<DescribeVpcEndpointAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <vpcEndpointAssociationsSet/>
</DescribeVpcEndpointAssociationsResponse>"""

EC2_DESCRIBE_VPC_ENDPOINT_CONNECTION_NOTIFICATIONS = """<DescribeVpcEndpointConnectionNotificationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <vpcEndpointConnectionNotificationsSet/>
</DescribeVpcEndpointConnectionNotificationsResponse>"""

EC2_DESCRIBE_VPC_ENDPOINT_CONNECTIONS = """<DescribeVpcEndpointConnectionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <vpcEndpointConnectionsSet/>
</DescribeVpcEndpointConnectionsResponse>"""

EC2_DESCRIBE_VPN_CONCENTRATORS = """<DescribeVpnConcentratorsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <vpnConcentratorsSet/>
</DescribeVpnConcentratorsResponse>"""

EC2_DISABLE_ALLOWED_IMAGES_SETTINGS = """<DisableAllowedImagesSettingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</DisableAllowedImagesSettingsResponse>"""

EC2_DISABLE_AWS_NETWORK_PERFORMANCE_METRIC_SUBSCRIPTION = """<DisableAwsNetworkPerformanceMetricSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</DisableAwsNetworkPerformanceMetricSubscriptionResponse>"""

EC2_DISABLE_CAPACITY_MANAGER = """<DisableCapacityManagerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</DisableCapacityManagerResponse>"""

EC2_DISABLE_IMAGE_BLOCK_PUBLIC_ACCESS = """<DisableImageBlockPublicAccessResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</DisableImageBlockPublicAccessResponse>"""

EC2_DISABLE_SERIAL_CONSOLE_ACCESS = """<DisableSerialConsoleAccessResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</DisableSerialConsoleAccessResponse>"""

EC2_DISABLE_SNAPSHOT_BLOCK_PUBLIC_ACCESS = """<DisableSnapshotBlockPublicAccessResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</DisableSnapshotBlockPublicAccessResponse>"""

EC2_ENABLE_AWS_NETWORK_PERFORMANCE_METRIC_SUBSCRIPTION = """<EnableAwsNetworkPerformanceMetricSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</EnableAwsNetworkPerformanceMetricSubscriptionResponse>"""

EC2_ENABLE_CAPACITY_MANAGER = """<EnableCapacityManagerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</EnableCapacityManagerResponse>"""

EC2_ENABLE_REACHABILITY_ANALYZER_ORGANIZATION_SHARING = """<EnableReachabilityAnalyzerOrganizationSharingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</EnableReachabilityAnalyzerOrganizationSharingResponse>"""

EC2_ENABLE_SERIAL_CONSOLE_ACCESS = """<EnableSerialConsoleAccessResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</EnableSerialConsoleAccessResponse>"""

EC2_GET_ALLOWED_IMAGES_SETTINGS = """<GetAllowedImagesSettingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetAllowedImagesSettingsResponse>"""

EC2_GET_AWS_NETWORK_PERFORMANCE_DATA = """<GetAwsNetworkPerformanceDataResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetAwsNetworkPerformanceDataResponse>"""

EC2_GET_CAPACITY_MANAGER_ATTRIBUTES = """<GetCapacityManagerAttributesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetCapacityManagerAttributesResponse>"""

EC2_GET_EBS_DEFAULT_KMS_KEY_ID = """<GetEbsDefaultKmsKeyIdResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetEbsDefaultKmsKeyIdResponse>"""

EC2_GET_ENABLED_IPAM_POLICY = """<GetEnabledIpamPolicyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetEnabledIpamPolicyResponse>"""

EC2_GET_IMAGE_BLOCK_PUBLIC_ACCESS_STATE = """<GetImageBlockPublicAccessStateResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetImageBlockPublicAccessStateResponse>"""

EC2_GET_INSTANCE_METADATA_DEFAULTS = """<GetInstanceMetadataDefaultsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetInstanceMetadataDefaultsResponse>"""

EC2_GET_SERIAL_CONSOLE_ACCESS_STATUS = """<GetSerialConsoleAccessStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetSerialConsoleAccessStatusResponse>"""

EC2_GET_SNAPSHOT_BLOCK_PUBLIC_ACCESS_STATE = """<GetSnapshotBlockPublicAccessStateResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetSnapshotBlockPublicAccessStateResponse>"""

EC2_GET_VPN_CONNECTION_DEVICE_TYPES = """<GetVpnConnectionDeviceTypesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</GetVpnConnectionDeviceTypesResponse>"""

EC2_IMPORT_IMAGE = """<ImportImageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</ImportImageResponse>"""

EC2_IMPORT_SNAPSHOT = """<ImportSnapshotResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
</ImportSnapshotResponse>"""

EC2_LIST_IMAGES_IN_RECYCLE_BIN = """<ListImagesInRecycleBinResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <imagesInRecycleBinSet/>
</ListImagesInRecycleBinResponse>"""

EC2_LIST_SNAPSHOTS_IN_RECYCLE_BIN = """<ListSnapshotsInRecycleBinResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <snapshotsInRecycleBinSet/>
</ListSnapshotsInRecycleBinResponse>"""

EC2_LIST_VOLUMES_IN_RECYCLE_BIN = """<ListVolumesInRecycleBinResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <volumesInRecycleBinSet/>
</ListVolumesInRecycleBinResponse>"""

EC2_MODIFY_INSTANCE_METADATA_DEFAULTS = """<ModifyInstanceMetadataDefaultsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</ModifyInstanceMetadataDefaultsResponse>"""

EC2_REJECT_TRANSIT_GATEWAY_MULTICAST_DOMAIN_ASSOCIATIONS = """<RejectTransitGatewayMulticastDomainAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</RejectTransitGatewayMulticastDomainAssociationsResponse>"""

EC2_REPLACE_IMAGE_CRITERIA_IN_ALLOWED_IMAGES_SETTINGS = """<ReplaceImageCriteriaInAllowedImagesSettingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</ReplaceImageCriteriaInAllowedImagesSettingsResponse>"""

EC2_RESET_EBS_DEFAULT_KMS_KEY_ID = """<ResetEbsDefaultKmsKeyIdResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</ResetEbsDefaultKmsKeyIdResponse>"""


EC2_ACCEPT_CAPACITY_RESERVATION_BILLING_OWNERSHIP = """<AcceptCapacityReservationBillingOwnershipResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</AcceptCapacityReservationBillingOwnershipResponse>"""

EC2_ACCEPT_RESERVED_INSTANCES_EXCHANGE_QUOTE = """<AcceptReservedInstancesExchangeQuoteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <exchangeId>riex-stub</exchangeId>
</AcceptReservedInstancesExchangeQuoteResponse>"""

EC2_ACCEPT_TRANSIT_GATEWAY_VPC_ATTACHMENT = """<AcceptTransitGatewayVpcAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</AcceptTransitGatewayVpcAttachmentResponse>"""

EC2_ADVERTISE_BYOIP_CIDR = """<AdvertiseByoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <byoipCidr>
        <cidr></cidr>
        <state>advertised</state>
    </byoipCidr>
</AdvertiseByoipCidrResponse>"""

EC2_APPLY_SECURITY_GROUPS_TO_CLIENT_VPN_TARGET_NETWORK = """<ApplySecurityGroupsToClientVpnTargetNetworkResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <securityGroupIds/>
</ApplySecurityGroupsToClientVpnTargetNetworkResponse>"""

EC2_ASSIGN_PRIVATE_NAT_GATEWAY_ADDRESS = """<AssignPrivateNatGatewayAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <natGatewayId></natGatewayId>
    <natGatewayAddressSet/>
</AssignPrivateNatGatewayAddressResponse>"""

EC2_ASSOCIATE_CLIENT_VPN_TARGET_NETWORK = """<AssociateClientVpnTargetNetworkResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <associationId>cvpn-assoc-stub</associationId>
    <status>
        <code>associating</code>
    </status>
</AssociateClientVpnTargetNetworkResponse>"""

EC2_ASSOCIATE_ENCLAVE_CERTIFICATE_IAM_ROLE = """<AssociateEnclaveCertificateIamRoleResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</AssociateEnclaveCertificateIamRoleResponse>"""

EC2_ASSOCIATE_IPAM_BYOASN = """<AssociateIpamByoasnResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</AssociateIpamByoasnResponse>"""

EC2_ASSOCIATE_IPAM_RESOURCE_DISCOVERY = """<AssociateIpamResourceDiscoveryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</AssociateIpamResourceDiscoveryResponse>"""

EC2_ASSOCIATE_NAT_GATEWAY_ADDRESS = """<AssociateNatGatewayAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <natGatewayId></natGatewayId>
    <natGatewayAddressSet/>
</AssociateNatGatewayAddressResponse>"""

EC2_ASSOCIATE_TRANSIT_GATEWAY_MULTICAST_DOMAIN = """<AssociateTransitGatewayMulticastDomainResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <associations>
        <subnets/>
        <state>associating</state>
    </associations>
</AssociateTransitGatewayMulticastDomainResponse>"""

EC2_ASSOCIATE_TRANSIT_GATEWAY_POLICY_TABLE = """<AssociateTransitGatewayPolicyTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <association>
        <state>associating</state>
    </association>
</AssociateTransitGatewayPolicyTableResponse>"""

EC2_ATTACH_CLASSIC_LINK_VPC = """<AttachClassicLinkVpcResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</AttachClassicLinkVpcResponse>"""

EC2_ATTACH_VERIFIED_ACCESS_TRUST_PROVIDER = """<AttachVerifiedAccessTrustProviderResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</AttachVerifiedAccessTrustProviderResponse>"""

EC2_BUNDLE_INSTANCE = """<BundleInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <bundleInstanceTask>
        <instanceId></instanceId>
        <bundleId>bun-stub</bundleId>
        <state>pending</state>
    </bundleInstanceTask>
</BundleInstanceResponse>"""

EC2_CANCEL_BUNDLE_TASK = """<CancelBundleTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <bundleInstanceTask>
        <bundleId></bundleId>
        <state>cancelling</state>
    </bundleInstanceTask>
</CancelBundleTaskResponse>"""

EC2_CANCEL_CONVERSION_TASK = """<CancelConversionTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</CancelConversionTaskResponse>"""

EC2_CANCEL_DECLARATIVE_POLICIES_REPORT = """<CancelDeclarativePoliciesReportResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</CancelDeclarativePoliciesReportResponse>"""

EC2_CANCEL_EXPORT_TASK = """<CancelExportTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</CancelExportTaskResponse>"""

EC2_CANCEL_IMAGE_LAUNCH_PERMISSION = """<CancelImageLaunchPermissionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <return>true</return>
</CancelImageLaunchPermissionResponse>"""

EC2_CANCEL_RESERVED_INSTANCES_LISTING = """<CancelReservedInstancesListingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <reservedInstancesListingsSet/>
</CancelReservedInstancesListingResponse>"""

EC2_COPY_FPGA_IMAGE = """<CopyFpgaImageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <fpgaImageId>afi-stub</fpgaImageId>
</CopyFpgaImageResponse>"""

EC2_CREATE_CAPACITY_RESERVATION_BY_SPLITTING = """<CreateCapacityReservationBySplittingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <sourceCapacityReservation/>
    <destinationCapacityReservation/>
</CreateCapacityReservationBySplittingResponse>"""

EC2_CREATE_CLIENT_VPN_ROUTE = """<CreateClientVpnRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <status>
        <code>creating</code>
    </status>
</CreateClientVpnRouteResponse>"""

EC2_CREATE_FPGA_IMAGE = """<CreateFpgaImageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <fpgaImageId>afi-stub</fpgaImageId>
    <fpgaImageGlobalId>agfi-stub</fpgaImageGlobalId>
</CreateFpgaImageResponse>"""

EC2_CREATE_INSTANCE_EXPORT_TASK = """<CreateInstanceExportTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <exportTask>
        <exportTaskId>export-stub</exportTaskId>
        <state>active</state>
    </exportTask>
</CreateInstanceExportTaskResponse>"""

EC2_CREATE_IPAM_EXTERNAL_RESOURCE_VERIFICATION_TOKEN = """<CreateIpamExternalResourceVerificationTokenResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <ipamExternalResourceVerificationToken>
        <ipamExternalResourceVerificationTokenId>ipam-evrt-stub</ipamExternalResourceVerificationTokenId>
    </ipamExternalResourceVerificationToken>
</CreateIpamExternalResourceVerificationTokenResponse>"""

EC2_CREATE_LOCAL_GATEWAY_ROUTE_TABLE_VIRTUAL_INTERFACE_GROUP_ASSOCIATION = """<CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <localGatewayRouteTableVirtualInterfaceGroupAssociation>
        <state>associating</state>
    </localGatewayRouteTableVirtualInterfaceGroupAssociation>
</CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociationResponse>"""

EC2_CREATE_LOCAL_GATEWAY_ROUTE_TABLE_VPC_ASSOCIATION = """<CreateLocalGatewayRouteTableVpcAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <localGatewayRouteTableVpcAssociation>
        <state>associating</state>
    </localGatewayRouteTableVpcAssociation>
</CreateLocalGatewayRouteTableVpcAssociationResponse>"""

EC2_CREATE_NETWORK_INTERFACE_PERMISSION = """<CreateNetworkInterfacePermissionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <interfacePermission>
        <networkInterfacePermissionId>eni-perm-stub</networkInterfacePermissionId>
        <permissionState>
            <state>granted</state>
        </permissionState>
    </interfacePermission>
</CreateNetworkInterfacePermissionResponse>"""

EC2_CREATE_RESERVED_INSTANCES_LISTING = """<CreateReservedInstancesListingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <reservedInstancesListingsSet/>
</CreateReservedInstancesListingResponse>"""

EC2_CREATE_RESTORE_IMAGE_TASK = """<CreateRestoreImageTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <imageId>ami-stub</imageId>
</CreateRestoreImageTaskResponse>"""

EC2_CREATE_TRANSIT_GATEWAY_MULTICAST_DOMAIN = """<CreateTransitGatewayMulticastDomainResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <transitGatewayMulticastDomain>
        <transitGatewayMulticastDomainId>tgw-mcast-domain-stub</transitGatewayMulticastDomainId>
        <state>pending</state>
    </transitGatewayMulticastDomain>
</CreateTransitGatewayMulticastDomainResponse>"""

EC2_CREATE_TRANSIT_GATEWAY_POLICY_TABLE = """<CreateTransitGatewayPolicyTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{{ request_id }}</requestId>
    <transitGatewayPolicyTable>
        <transitGatewayPolicyTableId>tgw-policy-tbl-stub</transitGatewayPolicyTableId>
        <state>pending</state>
    </transitGatewayPolicyTable>
</CreateTransitGatewayPolicyTableResponse>"""
