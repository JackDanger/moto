"""Handles incoming directconnect requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import LAG, Connection, DirectConnectBackend, directconnect_backends


class DirectConnectResponse(BaseResponse):
    """Handler for DirectConnect requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="directconnect")

    @property
    def directconnect_backend(self) -> DirectConnectBackend:
        return directconnect_backends[self.current_account][self.region]

    def describe_connections(self) -> str:
        params = json.loads(self.body)
        connections = self.directconnect_backend.describe_connections(
            connection_id=params.get("connectionId"),
        )
        return json.dumps(
            {"connections": [connection.to_dict() for connection in connections]}
        )

    def create_connection(self) -> str:
        params = json.loads(self.body)
        connection: Connection = self.directconnect_backend.create_connection(
            location=params.get("location"),
            bandwidth=params.get("bandwidth"),
            connection_name=params.get("connectionName"),
            lag_id=params.get("lagId"),
            tags=params.get("tags"),
            provider_name=params.get("providerName"),
            request_mac_sec=params.get("requestMACSec"),
        )
        return json.dumps(connection.to_dict())

    def delete_connection(self) -> str:
        params = json.loads(self.body)
        connection: Connection = self.directconnect_backend.delete_connection(
            connection_id=params.get("connectionId"),
        )
        return json.dumps(connection.to_dict())

    def update_connection(self) -> str:
        params = json.loads(self.body)
        connection: Connection = self.directconnect_backend.update_connection(
            connection_id=params.get("connectionId"),
            new_connection_name=params.get("connectionName"),
            new_encryption_mode=params.get("encryptionMode"),
        )
        return json.dumps(connection.to_dict())

    def confirm_connection(self) -> str:
        params = json.loads(self.body)
        connection = self.directconnect_backend.confirm_connection(
            connection_id=params.get("connectionId"),
        )
        return json.dumps({"connectionState": connection.connection_state})

    def describe_hosted_connections(self) -> str:
        params = json.loads(self.body)
        connections = self.directconnect_backend.describe_hosted_connections(
            connection_id=params.get("connectionId"),
        )
        return json.dumps({"connections": [c.to_dict() for c in connections]})

    def describe_connection_loa(self) -> str:
        params = json.loads(self.body)
        result = self.directconnect_backend.describe_connection_loa(
            connection_id=params.get("connectionId"),
            provider_name=params.get("providerName"),
            loa_content_type=params.get("loaContentType"),
        )
        return json.dumps(result)

    def associate_mac_sec_key(self) -> str:
        params = json.loads(self.body)
        connection_id = params.get("connectionId")
        secret_arn = params.get("secretARN")
        ckn = params.get("ckn")
        cak = params.get("cak")
        connection_id, mac_sec_keys = self.directconnect_backend.associate_mac_sec_key(
            connection_id=connection_id,
            secret_arn=secret_arn,
            ckn=ckn,
            cak=cak,
        )
        return json.dumps(
            {
                "connectionId": connection_id,
                "macSecKeys": [mac_sec_key.to_dict() for mac_sec_key in mac_sec_keys],
            }
        )

    def disassociate_mac_sec_key(self) -> str:
        params = json.loads(self.body)
        connection_id = params.get("connectionId")
        secret_arn = params.get("secretARN")
        connection_id, mac_sec_key = (
            self.directconnect_backend.disassociate_mac_sec_key(
                connection_id=connection_id,
                secret_arn=secret_arn,
            )
        )
        return json.dumps(
            {
                "connectionId": connection_id,
                "macSecKeys": [mac_sec_key.to_dict()],
            }
        )

    # LAG operations

    def create_lag(self) -> str:
        params = json.loads(self.body)
        lag: LAG = self.directconnect_backend.create_lag(
            number_of_connections=params.get("numberOfConnections"),
            location=params.get("location"),
            connections_bandwidth=params.get("connectionsBandwidth"),
            lag_name=params.get("lagName"),
            connection_id=params.get("connectionId"),
            tags=params.get("tags"),
            child_connection_tags=params.get("childConnectionTags"),
            provider_name=params.get("providerName"),
            request_mac_sec=params.get("requestMACSec"),
        )
        return json.dumps(lag.to_dict())

    def describe_lags(self) -> str:
        params = json.loads(self.body)
        lags = self.directconnect_backend.describe_lags(
            lag_id=params.get("lagId"),
        )
        return json.dumps({"lags": [lag.to_dict() for lag in lags]})

    def delete_lag(self) -> str:
        params = json.loads(self.body)
        lag = self.directconnect_backend.delete_lag(lag_id=params.get("lagId"))
        return json.dumps(lag.to_dict())

    def update_lag(self) -> str:
        params = json.loads(self.body)
        lag = self.directconnect_backend.update_lag(
            lag_id=params.get("lagId"),
            lag_name=params.get("lagName"),
            minimum_links=params.get("minimumLinks"),
            encryption_mode=params.get("encryptionMode"),
        )
        return json.dumps(lag.to_dict())

    def associate_connection_with_lag(self) -> str:
        params = json.loads(self.body)
        connection = self.directconnect_backend.associate_connection_with_lag(
            connection_id=params.get("connectionId"),
            lag_id=params.get("lagId"),
        )
        return json.dumps(connection.to_dict())

    def disassociate_connection_from_lag(self) -> str:
        params = json.loads(self.body)
        connection = self.directconnect_backend.disassociate_connection_from_lag(
            connection_id=params.get("connectionId"),
            lag_id=params.get("lagId"),
        )
        return json.dumps(connection.to_dict())

    # Virtual Interface operations

    def create_private_virtual_interface(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.create_private_virtual_interface(
            connection_id=params.get("connectionId"),
            new_private_virtual_interface=params.get("newPrivateVirtualInterface", {}),
            tags=params.get("tags"),
        )
        return json.dumps(vif.to_dict())

    def create_public_virtual_interface(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.create_public_virtual_interface(
            connection_id=params.get("connectionId"),
            new_public_virtual_interface=params.get("newPublicVirtualInterface", {}),
            tags=params.get("tags"),
        )
        return json.dumps(vif.to_dict())

    def create_transit_virtual_interface(self) -> str:
        params = json.loads(self.body)
        result = self.directconnect_backend.create_transit_virtual_interface(
            connection_id=params.get("connectionId"),
            new_transit_virtual_interface=params.get("newTransitVirtualInterface", {}),
            tags=params.get("tags"),
        )
        return json.dumps({"virtualInterface": result.to_dict()})

    def allocate_private_virtual_interface(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.allocate_private_virtual_interface(
            connection_id=params.get("connectionId"),
            owner_account=params.get("ownerAccount"),
            new_private_virtual_interface_allocation=params.get(
                "newPrivateVirtualInterfaceAllocation", {}
            ),
            tags=params.get("tags"),
        )
        return json.dumps(vif.to_dict())

    def allocate_public_virtual_interface(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.allocate_public_virtual_interface(
            connection_id=params.get("connectionId"),
            owner_account=params.get("ownerAccount"),
            new_public_virtual_interface_allocation=params.get(
                "newPublicVirtualInterfaceAllocation", {}
            ),
            tags=params.get("tags"),
        )
        return json.dumps(vif.to_dict())

    def allocate_transit_virtual_interface(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.allocate_transit_virtual_interface(
            connection_id=params.get("connectionId"),
            owner_account=params.get("ownerAccount"),
            new_transit_virtual_interface_allocation=params.get(
                "newTransitVirtualInterfaceAllocation", {}
            ),
            tags=params.get("tags"),
        )
        return json.dumps({"virtualInterface": vif.to_dict()})

    def allocate_hosted_connection(self) -> str:
        params = json.loads(self.body)
        connection = self.directconnect_backend.allocate_hosted_connection(
            connection_id=params.get("connectionId"),
            owner_account=params.get("ownerAccount"),
            bandwidth=params.get("bandwidth"),
            connection_name=params.get("connectionName"),
            vlan=params.get("vlan", 0),
            tags=params.get("tags"),
        )
        return json.dumps(connection.to_dict())

    def describe_virtual_interfaces(self) -> str:
        params = json.loads(self.body)
        vifs = self.directconnect_backend.describe_virtual_interfaces(
            connection_id=params.get("connectionId"),
            virtual_interface_id=params.get("virtualInterfaceId"),
        )
        return json.dumps({"virtualInterfaces": [v.to_dict() for v in vifs]})

    def delete_virtual_interface(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.delete_virtual_interface(
            virtual_interface_id=params.get("virtualInterfaceId"),
        )
        return json.dumps({"virtualInterfaceState": vif.virtual_interface_state})

    def confirm_private_virtual_interface(self) -> str:
        params = json.loads(self.body)
        state = self.directconnect_backend.confirm_private_virtual_interface(
            virtual_interface_id=params.get("virtualInterfaceId"),
            virtual_gateway_id=params.get("virtualGatewayId"),
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
        )
        return json.dumps({"virtualInterfaceState": state})

    def confirm_public_virtual_interface(self) -> str:
        params = json.loads(self.body)
        state = self.directconnect_backend.confirm_public_virtual_interface(
            virtual_interface_id=params.get("virtualInterfaceId"),
        )
        return json.dumps({"virtualInterfaceState": state})

    def confirm_transit_virtual_interface(self) -> str:
        params = json.loads(self.body)
        state = self.directconnect_backend.confirm_transit_virtual_interface(
            virtual_interface_id=params.get("virtualInterfaceId"),
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
        )
        return json.dumps({"virtualInterfaceState": state})

    def update_virtual_interface_attributes(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.update_virtual_interface_attributes(
            virtual_interface_id=params.get("virtualInterfaceId"),
            mtu=params.get("mtu"),
            enable_site_link=params.get("enableSiteLink"),
            virtual_interface_name=params.get("virtualInterfaceName"),
        )
        return json.dumps(vif.to_dict())

    def create_bgp_peer(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.create_bgp_peer(
            virtual_interface_id=params.get("virtualInterfaceId"),
            new_bgp_peer=params.get("newBGPPeer", {}),
        )
        return json.dumps({"virtualInterface": vif.to_dict()})

    def delete_bgp_peer(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.delete_bgp_peer(
            virtual_interface_id=params.get("virtualInterfaceId"),
            asn=params.get("asn"),
            customer_address=params.get("customerAddress"),
            bgp_peer_id=params.get("bgpPeerId"),
        )
        return json.dumps({"virtualInterface": vif.to_dict()})

    # Direct Connect Gateway operations

    def create_direct_connect_gateway(self) -> str:
        params = json.loads(self.body)
        gateway = self.directconnect_backend.create_direct_connect_gateway(
            direct_connect_gateway_name=params.get("directConnectGatewayName"),
            amazon_side_asn=params.get("amazonSideAsn"),
        )
        return json.dumps({"directConnectGateway": gateway.to_dict()})

    def describe_direct_connect_gateways(self) -> str:
        params = json.loads(self.body)
        gateways = self.directconnect_backend.describe_direct_connect_gateways(
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
        )
        return json.dumps({"directConnectGateways": [g.to_dict() for g in gateways]})

    def delete_direct_connect_gateway(self) -> str:
        params = json.loads(self.body)
        gateway = self.directconnect_backend.delete_direct_connect_gateway(
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
        )
        return json.dumps({"directConnectGateway": gateway.to_dict()})

    def update_direct_connect_gateway(self) -> str:
        params = json.loads(self.body)
        gateway = self.directconnect_backend.update_direct_connect_gateway(
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
            new_direct_connect_gateway_name=params.get("newDirectConnectGatewayName"),
        )
        return json.dumps({"directConnectGateway": gateway.to_dict()})

    def create_direct_connect_gateway_association(self) -> str:
        params = json.loads(self.body)
        assoc = self.directconnect_backend.create_direct_connect_gateway_association(
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
            gateway_id=params.get("gatewayId"),
            add_allowed_prefixes=params.get("addAllowedPrefixesToDirectConnectGateway"),
            virtual_gateway_id=params.get("virtualGatewayId"),
        )
        return json.dumps({"directConnectGatewayAssociation": assoc.to_dict()})

    def describe_direct_connect_gateway_associations(self) -> str:
        params = json.loads(self.body)
        assocs = self.directconnect_backend.describe_direct_connect_gateway_associations(
            association_id=params.get("associationId"),
            associated_gateway_id=params.get("associatedGatewayId"),
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
        )
        return json.dumps(
            {"directConnectGatewayAssociations": [a.to_dict() for a in assocs]}
        )

    def delete_direct_connect_gateway_association(self) -> str:
        params = json.loads(self.body)
        assoc = self.directconnect_backend.delete_direct_connect_gateway_association(
            association_id=params.get("associationId"),
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
            virtual_gateway_id=params.get("virtualGatewayId"),
        )
        return json.dumps({"directConnectGatewayAssociation": assoc.to_dict()})

    def update_direct_connect_gateway_association(self) -> str:
        params = json.loads(self.body)
        assoc = self.directconnect_backend.update_direct_connect_gateway_association(
            association_id=params.get("associationId"),
            add_allowed_prefixes=params.get("addAllowedPrefixesToDirectConnectGateway"),
            remove_allowed_prefixes=params.get(
                "removeAllowedPrefixesToDirectConnectGateway"
            ),
        )
        return json.dumps({"directConnectGatewayAssociation": assoc.to_dict()})

    def create_direct_connect_gateway_association_proposal(self) -> str:
        params = json.loads(self.body)
        proposal = self.directconnect_backend.create_direct_connect_gateway_association_proposal(
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
            direct_connect_gateway_owner_account=params.get(
                "directConnectGatewayOwnerAccount"
            ),
            gateway_id=params.get("gatewayId"),
            add_allowed_prefixes=params.get(
                "addAllowedPrefixesToDirectConnectGateway"
            ),
            remove_allowed_prefixes=params.get(
                "removeAllowedPrefixesToDirectConnectGateway"
            ),
        )
        return json.dumps(
            {"directConnectGatewayAssociationProposal": proposal.to_dict()}
        )

    def describe_direct_connect_gateway_association_proposals(self) -> str:
        params = json.loads(self.body)
        proposals = self.directconnect_backend.describe_direct_connect_gateway_association_proposals(
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
            proposal_id=params.get("proposalId"),
            associated_gateway_id=params.get("associatedGatewayId"),
        )
        return json.dumps(
            {
                "directConnectGatewayAssociationProposals": [
                    p.to_dict() for p in proposals
                ]
            }
        )

    def delete_direct_connect_gateway_association_proposal(self) -> str:
        params = json.loads(self.body)
        proposal = self.directconnect_backend.delete_direct_connect_gateway_association_proposal(
            proposal_id=params.get("proposalId"),
        )
        return json.dumps(
            {"directConnectGatewayAssociationProposal": proposal.to_dict()}
        )

    def accept_direct_connect_gateway_association_proposal(self) -> str:
        params = json.loads(self.body)
        assoc = self.directconnect_backend.accept_direct_connect_gateway_association_proposal(
            proposal_id=params.get("proposalId"),
            associated_gateway_owner_account=params.get(
                "associatedGatewayOwnerAccount"
            ),
            override_allowed_prefixes=params.get(
                "overrideAllowedPrefixesToDirectConnectGateway"
            ),
        )
        return json.dumps({"directConnectGatewayAssociation": assoc.to_dict()})

    def describe_direct_connect_gateway_attachments(self) -> str:
        params = json.loads(self.body)
        attachments = self.directconnect_backend.describe_direct_connect_gateway_attachments(
            direct_connect_gateway_id=params.get("directConnectGatewayId"),
            virtual_interface_id=params.get("virtualInterfaceId"),
        )
        return json.dumps({"directConnectGatewayAttachments": attachments})

    # Interconnect operations

    def create_interconnect(self) -> str:
        params = json.loads(self.body)
        interconnect = self.directconnect_backend.create_interconnect(
            interconnect_name=params.get("interconnectName"),
            bandwidth=params.get("bandwidth"),
            location=params.get("location"),
            lag_id=params.get("lagId"),
            tags=params.get("tags"),
            provider_name=params.get("providerName"),
        )
        return json.dumps(interconnect.to_dict())

    def describe_interconnects(self) -> str:
        params = json.loads(self.body)
        interconnects = self.directconnect_backend.describe_interconnects(
            interconnect_id=params.get("interconnectId"),
        )
        return json.dumps({"interconnects": [ic.to_dict() for ic in interconnects]})

    def delete_interconnect(self) -> str:
        params = json.loads(self.body)
        state = self.directconnect_backend.delete_interconnect(
            interconnect_id=params.get("interconnectId"),
        )
        return json.dumps({"interconnectState": state})

    def describe_connections_on_interconnect(self) -> str:
        params = json.loads(self.body)
        connections = self.directconnect_backend.describe_connections_on_interconnect(
            interconnect_id=params.get("interconnectId"),
        )
        return json.dumps({"connections": [c.to_dict() for c in connections]})

    def describe_interconnect_loa(self) -> str:
        params = json.loads(self.body)
        result = self.directconnect_backend.describe_interconnect_loa(
            interconnect_id=params.get("interconnectId"),
            provider_name=params.get("providerName"),
            loa_content_type=params.get("loaContentType"),
        )
        return json.dumps(result)

    def describe_loa(self) -> str:
        params = json.loads(self.body)
        result = self.directconnect_backend.describe_loa(
            connection_id=params.get("connectionId"),
            provider_name=params.get("providerName"),
            loa_content_type=params.get("loaContentType"),
        )
        return json.dumps(result)

    # Virtual Gateway operations

    def describe_virtual_gateways(self) -> str:
        gateways = self.directconnect_backend.describe_virtual_gateways()
        return json.dumps({"virtualGateways": [g.to_dict() for g in gateways]})

    # Misc

    def associate_hosted_connection(self) -> str:
        params = json.loads(self.body)
        connection = self.directconnect_backend.associate_hosted_connection(
            connection_id=params.get("connectionId"),
            parent_connection_id=params.get("parentConnectionId"),
        )
        return json.dumps(connection.to_dict())

    def associate_virtual_interface(self) -> str:
        params = json.loads(self.body)
        vif = self.directconnect_backend.associate_virtual_interface(
            virtual_interface_id=params.get("virtualInterfaceId"),
            connection_id=params.get("connectionId"),
        )
        return json.dumps(vif.to_dict())

    def confirm_customer_agreement(self) -> str:
        params = json.loads(self.body)
        status = self.directconnect_backend.confirm_customer_agreement(
            agreement_name=params.get("agreementName"),
        )
        return json.dumps({"status": status})

    def describe_customer_metadata(self) -> str:
        result = self.directconnect_backend.describe_customer_metadata()
        return json.dumps(result)

    def describe_locations(self) -> str:
        locations = self.directconnect_backend.describe_locations()
        return json.dumps({"locations": locations})

    def describe_router_configuration(self) -> str:
        params = json.loads(self.body)
        result = self.directconnect_backend.describe_router_configuration(
            virtual_interface_id=params.get("virtualInterfaceId"),
            router_type_identifier=params.get("routerTypeIdentifier"),
        )
        return json.dumps(result)

    def list_virtual_interface_test_history(self) -> str:
        params = json.loads(self.body)
        tests = self.directconnect_backend.list_virtual_interface_test_history(
            test_id=params.get("testId"),
            virtual_interface_id=params.get("virtualInterfaceId"),
            bgp_peers=params.get("bgpPeers"),
            status=params.get("status"),
        )
        return json.dumps({"virtualInterfaceTestHistory": tests})

    def start_bgp_failover_test(self) -> str:
        params = json.loads(self.body)
        result = self.directconnect_backend.start_bgp_failover_test(
            virtual_interface_id=params.get("virtualInterfaceId"),
            bgp_peers=params.get("bgpPeers"),
            test_duration_in_minutes=params.get("testDurationInMinutes"),
        )
        return json.dumps(result)

    def stop_bgp_failover_test(self) -> str:
        params = json.loads(self.body)
        result = self.directconnect_backend.stop_bgp_failover_test(
            virtual_interface_id=params.get("virtualInterfaceId"),
        )
        return json.dumps(result)

    def allocate_connection_on_interconnect(self) -> str:
        params = json.loads(self.body)
        connection = self.directconnect_backend.allocate_connection_on_interconnect(
            bandwidth=params.get("bandwidth"),
            connection_name=params.get("connectionName"),
            owner_account=params.get("ownerAccount"),
            interconnect_id=params.get("interconnectId"),
            vlan=params.get("vlan", 0),
        )
        return json.dumps(connection.to_dict())

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tags = params.get("tags")
        self.directconnect_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tag_keys = params.get("tagKeys", [])
        self.directconnect_backend.untag_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )
        return json.dumps({})

    def describe_tags(self) -> str:
        params = json.loads(self.body)
        resource_arns = params.get("resourceArns")
        tags = self.directconnect_backend.list_tags_for_resources(
            resource_arns=resource_arns
        )
        return json.dumps(tags)
