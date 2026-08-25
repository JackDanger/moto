"""Handles incoming networkmanager requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import NetworkManagerBackend, networkmanager_backends


class NetworkManagerResponse(BaseResponse):
    """Handler for NetworkManager requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="networkmanager")

    @property
    def networkmanager_backend(self) -> NetworkManagerBackend:
        return networkmanager_backends[self.current_account][self.partition]

    # --- Global Network ---

    def create_global_network(self) -> str:
        params = json.loads(self.body)
        gn = self.networkmanager_backend.create_global_network(
            description=params.get("Description"), tags=params.get("Tags"),
        )
        self.networkmanager_backend.update_resource_state(gn.global_network_arn, "AVAILABLE")
        return json.dumps({"GlobalNetwork": gn.to_dict()})

    def delete_global_network(self) -> str:
        gn_id = unquote(self.path.split("/")[-1])
        gn = self.networkmanager_backend.delete_global_network(global_network_id=gn_id)
        return json.dumps({"GlobalNetwork": gn.to_dict()})

    def update_global_network(self) -> str:
        gn_id = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        gn = self.networkmanager_backend.update_global_network(
            global_network_id=gn_id, description=params.get("Description"),
        )
        return json.dumps({"GlobalNetwork": gn.to_dict()})

    def describe_global_networks(self) -> str:
        params = self._get_params()
        gns, next_token = self.networkmanager_backend.describe_global_networks(
            global_network_ids=params.get("globalNetworkIds"),
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"GlobalNetworks": [g.to_dict() for g in gns], "nextToken": next_token})

    # --- Core Network ---

    def create_core_network(self) -> str:
        params = json.loads(self.body)
        cn = self.networkmanager_backend.create_core_network(
            global_network_id=params.get("GlobalNetworkId"),
            description=params.get("Description"), tags=params.get("Tags"),
            policy_document=params.get("PolicyDocument"), client_token=params.get("ClientToken"),
        )
        self.networkmanager_backend.update_resource_state(cn.core_network_arn, "AVAILABLE")
        return json.dumps({"CoreNetwork": cn.to_dict()})

    def delete_core_network(self) -> str:
        cn_id = unquote(self.path.split("/")[-1])
        cn = self.networkmanager_backend.delete_core_network(core_network_id=cn_id)
        return json.dumps({"CoreNetwork": cn.to_dict()})

    def update_core_network(self) -> str:
        cn_id = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        cn = self.networkmanager_backend.update_core_network(
            core_network_id=cn_id, description=params.get("Description"),
        )
        return json.dumps({"CoreNetwork": cn.to_dict()})

    def list_core_networks(self) -> str:
        params = self._get_params()
        cns, next_token = self.networkmanager_backend.list_core_networks(
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"CoreNetworks": [cn.to_dict() for cn in cns], "NextToken": next_token})

    def get_core_network(self) -> str:
        cn_id = unquote(self.path.split("/")[-1])
        cn = self.networkmanager_backend.get_core_network(core_network_id=cn_id)
        return json.dumps({"CoreNetwork": cn.to_dict()})

    # --- Tags ---

    def tag_resource(self) -> TYPE_RESPONSE:
        params = json.loads(self.body)
        resource_arn = unquote(self.path.split("/tags/")[-1])
        self.networkmanager_backend.tag_resource(resource_arn=resource_arn, tags=params.get("Tags"))
        return 200, {}, json.dumps({})

    def untag_resource(self) -> TYPE_RESPONSE:
        params = self._get_params()
        resource_arn = unquote(self.path.split("/tags/")[-1])
        self.networkmanager_backend.untag_resource(resource_arn=resource_arn, tag_keys=params.get("tagKeys"))
        return 200, {}, json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        return json.dumps({"TagList": self.networkmanager_backend.list_tags_for_resource(resource_arn=resource_arn)})

    # --- Site ---

    def create_site(self) -> str:
        params = json.loads(self.body)
        gn_id = unquote(self.path.split("/")[-2])
        site = self.networkmanager_backend.create_site(
            global_network_id=gn_id, description=params.get("Description"),
            location=params.get("Location"), tags=params.get("Tags"),
        )
        self.networkmanager_backend.update_resource_state(site.site_arn, "AVAILABLE")
        return json.dumps({"Site": site.to_dict()})

    def delete_site(self) -> str:
        gn_id = unquote(self.path.split("/")[-3])
        site_id = unquote(self.path.split("/")[-1])
        site = self.networkmanager_backend.delete_site(global_network_id=gn_id, site_id=site_id)
        return json.dumps({"Site": site.to_dict()})

    def update_site(self) -> str:
        gn_id = unquote(self.path.split("/")[-3])
        site_id = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        site = self.networkmanager_backend.update_site(
            global_network_id=gn_id, site_id=site_id,
            description=params.get("Description"), location=params.get("Location"),
        )
        return json.dumps({"Site": site.to_dict()})

    def get_sites(self) -> str:
        params = self._get_params()
        gn_id = unquote(self.path.split("/")[-2])
        sites, next_token = self.networkmanager_backend.get_sites(
            global_network_id=gn_id, site_ids=self.querystring.get("siteIds"),
            max_results=params.get("MaxResults"), next_token=params.get("NextToken"),
        )
        return json.dumps({"Sites": [s.to_dict() for s in sites], "nextToken": next_token})

    # --- Link ---

    def create_link(self) -> str:
        params = json.loads(self.body)
        gn_id = unquote(self.path.split("/")[-2])
        link = self.networkmanager_backend.create_link(
            global_network_id=gn_id, description=params.get("Description"),
            type=params.get("Type"), bandwidth=params.get("Bandwidth"),
            provider=params.get("Provider"), site_id=params.get("SiteId"), tags=params.get("Tags"),
        )
        self.networkmanager_backend.update_resource_state(link.link_arn, "AVAILABLE")
        return json.dumps({"Link": link.to_dict()})

    def get_links(self) -> str:
        params = self._get_params()
        gn_id = unquote(self.path.split("/")[-2])
        links, next_token = self.networkmanager_backend.get_links(
            global_network_id=gn_id, link_ids=self.querystring.get("linkIds"),
            site_id=params.get("SiteId"), type=params.get("Type"),
            provider=params.get("Provider"), max_results=params.get("MaxResults"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"Links": [l.to_dict() for l in links], "nextToken": next_token})

    def delete_link(self) -> str:
        gn_id = unquote(self.path.split("/")[-3])
        link_id = unquote(self.path.split("/")[-1])
        link = self.networkmanager_backend.delete_link(global_network_id=gn_id, link_id=link_id)
        return json.dumps({"Link": link.to_dict()})

    def update_link(self) -> str:
        gn_id = unquote(self.path.split("/")[-3])
        link_id = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        link = self.networkmanager_backend.update_link(
            global_network_id=gn_id, link_id=link_id,
            description=params.get("Description"), type=params.get("Type"),
            bandwidth=params.get("Bandwidth"), provider=params.get("Provider"),
        )
        return json.dumps({"Link": link.to_dict()})

    # --- Device ---

    def create_device(self) -> str:
        params = json.loads(self.body)
        gn_id = unquote(self.path.split("/")[-2])
        device = self.networkmanager_backend.create_device(
            global_network_id=gn_id, aws_location=params.get("AWSLocation"),
            description=params.get("Description"), type=params.get("Type"),
            vendor=params.get("Vendor"), model=params.get("Model"),
            serial_number=params.get("SerialNumber"), location=params.get("Location"),
            site_id=params.get("SiteId"), tags=params.get("Tags"),
        )
        self.networkmanager_backend.update_resource_state(device.device_arn, "AVAILABLE")
        return json.dumps({"Device": device.to_dict()})

    def get_devices(self) -> str:
        params = self._get_params()
        gn_id = unquote(self.path.split("/")[-2])
        devices, next_token = self.networkmanager_backend.get_devices(
            global_network_id=gn_id, device_ids=self.querystring.get("deviceIds"),
            site_id=params.get("SiteId"), max_results=params.get("MaxResults"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"Devices": [d.to_dict() for d in devices], "nextToken": next_token})

    def delete_device(self) -> str:
        gn_id = unquote(self.path.split("/")[-3])
        device_id = unquote(self.path.split("/")[-1])
        device = self.networkmanager_backend.delete_device(global_network_id=gn_id, device_id=device_id)
        return json.dumps({"Device": device.to_dict()})

    def update_device(self) -> str:
        gn_id = unquote(self.path.split("/")[-3])
        device_id = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        device = self.networkmanager_backend.update_device(
            global_network_id=gn_id, device_id=device_id,
            aws_location=params.get("AWSLocation"), description=params.get("Description"),
            type=params.get("Type"), vendor=params.get("Vendor"), model=params.get("Model"),
            serial_number=params.get("SerialNumber"), location=params.get("Location"),
            site_id=params.get("SiteId"),
        )
        return json.dumps({"Device": device.to_dict()})

    # --- Connection ---

    def create_connection(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        conn = self.networkmanager_backend.create_connection(
            global_network_id=gn_id, device_id=params.get("DeviceId"),
            connected_device_id=params.get("ConnectedDeviceId"),
            link_id=params.get("LinkId"), connected_link_id=params.get("ConnectedLinkId"),
            description=params.get("Description"), tags=params.get("Tags"),
        )
        return json.dumps({"Connection": conn.to_dict()})

    def delete_connection(self) -> str:
        parts = self.path.split("/")
        gn_id = unquote(parts[-3])
        conn_id = unquote(parts[-1])
        conn = self.networkmanager_backend.delete_connection(global_network_id=gn_id, connection_id=conn_id)
        return json.dumps({"Connection": conn.to_dict()})

    def update_connection(self) -> str:
        parts = self.path.split("/")
        gn_id = unquote(parts[-3])
        conn_id = unquote(parts[-1])
        params = json.loads(self.body)
        conn = self.networkmanager_backend.update_connection(
            global_network_id=gn_id, connection_id=conn_id,
            link_id=params.get("LinkId"), connected_link_id=params.get("ConnectedLinkId"),
            description=params.get("Description"),
        )
        return json.dumps({"Connection": conn.to_dict()})

    def get_connections(self) -> str:
        params = self._get_params()
        gn_id = unquote(self.path.split("/")[-2])
        conns, next_token = self.networkmanager_backend.get_connections(
            global_network_id=gn_id, connection_ids=self.querystring.get("connectionIds"),
            device_id=params.get("deviceId"), max_results=params.get("maxResults"),
            next_token=params.get("nextToken"),
        )
        return json.dumps({"Connections": [c.to_dict() for c in conns], "NextToken": next_token})

    # --- VPC Attachment ---

    def create_vpc_attachment(self) -> str:
        params = json.loads(self.body)
        att = self.networkmanager_backend.create_vpc_attachment(
            core_network_id=params.get("CoreNetworkId"), vpc_arn=params.get("VpcArn"),
            subnet_arns=params.get("SubnetArns", []), options=params.get("Options"),
            tags=params.get("Tags"), client_token=params.get("ClientToken"),
        )
        return json.dumps({"VpcAttachment": att.to_dict()})

    def get_vpc_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-1])
        return json.dumps({"VpcAttachment": self.networkmanager_backend.get_vpc_attachment(attachment_id=att_id).to_dict()})

    def update_vpc_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        att = self.networkmanager_backend.update_vpc_attachment(
            attachment_id=att_id, add_subnet_arns=params.get("AddSubnetArns"),
            remove_subnet_arns=params.get("RemoveSubnetArns"), options=params.get("Options"),
        )
        return json.dumps({"VpcAttachment": att.to_dict()})

    # --- Connect Attachment ---

    def create_connect_attachment(self) -> str:
        params = json.loads(self.body)
        att = self.networkmanager_backend.create_connect_attachment(
            core_network_id=params.get("CoreNetworkId"), edge_location=params.get("EdgeLocation"),
            transport_attachment_id=params.get("TransportAttachmentId"),
            options=params.get("Options"), tags=params.get("Tags"),
            client_token=params.get("ClientToken"),
        )
        return json.dumps({"ConnectAttachment": att.to_dict()})

    def get_connect_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-1])
        return json.dumps({"ConnectAttachment": self.networkmanager_backend.get_connect_attachment(attachment_id=att_id).to_dict()})

    # --- Site-to-Site VPN Attachment ---

    def create_site_to_site_vpn_attachment(self) -> str:
        params = json.loads(self.body)
        att = self.networkmanager_backend.create_site_to_site_vpn_attachment(
            core_network_id=params.get("CoreNetworkId"),
            vpn_connection_arn=params.get("VpnConnectionArn"),
            tags=params.get("Tags"), client_token=params.get("ClientToken"),
        )
        return json.dumps({"SiteToSiteVpnAttachment": att.to_dict()})

    def get_site_to_site_vpn_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-1])
        return json.dumps({"SiteToSiteVpnAttachment": self.networkmanager_backend.get_site_to_site_vpn_attachment(attachment_id=att_id).to_dict()})

    # --- Transit Gateway Route Table Attachment ---

    def create_transit_gateway_route_table_attachment(self) -> str:
        params = json.loads(self.body)
        att = self.networkmanager_backend.create_transit_gateway_route_table_attachment(
            peering_id=params.get("PeeringId"),
            transit_gateway_route_table_arn=params.get("TransitGatewayRouteTableArn"),
            tags=params.get("Tags"), client_token=params.get("ClientToken"),
        )
        return json.dumps({"TransitGatewayRouteTableAttachment": att.to_dict()})

    def get_transit_gateway_route_table_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-1])
        return json.dumps({"TransitGatewayRouteTableAttachment": self.networkmanager_backend.get_transit_gateway_route_table_attachment(attachment_id=att_id).to_dict()})

    # --- Direct Connect Gateway Attachment ---

    def create_direct_connect_gateway_attachment(self) -> str:
        params = json.loads(self.body)
        att = self.networkmanager_backend.create_direct_connect_gateway_attachment(
            core_network_id=params.get("CoreNetworkId"),
            direct_connect_gateway_arn=params.get("DirectConnectGatewayArn"),
            edge_locations=params.get("EdgeLocations"), tags=params.get("Tags"),
            client_token=params.get("ClientToken"),
        )
        return json.dumps({"DirectConnectGatewayAttachment": att.to_dict()})

    def get_direct_connect_gateway_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-1])
        return json.dumps({"DirectConnectGatewayAttachment": self.networkmanager_backend.get_direct_connect_gateway_attachment(attachment_id=att_id).to_dict()})

    def update_direct_connect_gateway_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        att = self.networkmanager_backend.update_direct_connect_gateway_attachment(
            attachment_id=att_id, edge_locations=params.get("EdgeLocations"),
        )
        return json.dumps({"DirectConnectGatewayAttachment": att.to_dict()})

    # --- Generic Attachment ---

    def delete_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-1])
        att = self.networkmanager_backend.delete_attachment(attachment_id=att_id)
        return json.dumps({"Attachment": att.to_dict()})

    def accept_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-2])
        att = self.networkmanager_backend.accept_attachment(attachment_id=att_id)
        return json.dumps({"Attachment": att.to_dict()})

    def reject_attachment(self) -> str:
        att_id = unquote(self.path.split("/")[-2])
        att = self.networkmanager_backend.reject_attachment(attachment_id=att_id)
        return json.dumps({"Attachment": att.to_dict()})

    def list_attachments(self) -> str:
        params = self._get_params()
        atts, next_token = self.networkmanager_backend.list_attachments(
            core_network_id=params.get("coreNetworkId"),
            attachment_type=params.get("attachmentType"),
            edge_location=params.get("edgeLocation"), state=params.get("state"),
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"Attachments": [a.to_dict() for a in atts], "NextToken": next_token})

    # --- Connect Peer ---

    def create_connect_peer(self) -> str:
        params = json.loads(self.body)
        cp = self.networkmanager_backend.create_connect_peer(
            connect_attachment_id=params.get("ConnectAttachmentId"),
            core_network_address=params.get("CoreNetworkAddress"),
            peer_address=params.get("PeerAddress"), bgp_options=params.get("BgpOptions"),
            inside_cidr_blocks=params.get("InsideCidrBlocks"), tags=params.get("Tags"),
            client_token=params.get("ClientToken"), subnet_arn=params.get("SubnetArn"),
        )
        return json.dumps({"ConnectPeer": cp.to_dict()})

    def get_connect_peer(self) -> str:
        cp_id = unquote(self.path.split("/")[-1])
        return json.dumps({"ConnectPeer": self.networkmanager_backend.get_connect_peer(connect_peer_id=cp_id).to_dict()})

    def delete_connect_peer(self) -> str:
        cp_id = unquote(self.path.split("/")[-1])
        cp = self.networkmanager_backend.delete_connect_peer(connect_peer_id=cp_id)
        return json.dumps({"ConnectPeer": cp.to_dict()})

    def list_connect_peers(self) -> str:
        params = self._get_params()
        cps, next_token = self.networkmanager_backend.list_connect_peers(
            core_network_id=params.get("coreNetworkId"),
            connect_attachment_id=params.get("connectAttachmentId"),
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"ConnectPeers": [cp.to_dict() for cp in cps], "NextToken": next_token})

    # --- Peering ---

    def create_transit_gateway_peering(self) -> str:
        params = json.loads(self.body)
        tgp = self.networkmanager_backend.create_transit_gateway_peering(
            core_network_id=params.get("CoreNetworkId"),
            transit_gateway_arn=params.get("TransitGatewayArn"),
            tags=params.get("Tags"), client_token=params.get("ClientToken"),
        )
        return json.dumps({"TransitGatewayPeering": tgp.to_dict()})

    def get_transit_gateway_peering(self) -> str:
        pid = unquote(self.path.split("/")[-1])
        return json.dumps({"TransitGatewayPeering": self.networkmanager_backend.get_transit_gateway_peering(peering_id=pid).to_dict()})

    def delete_peering(self) -> str:
        pid = unquote(self.path.split("/")[-1])
        peering = self.networkmanager_backend.delete_peering(peering_id=pid)
        return json.dumps({"Peering": peering.to_dict()})

    def list_peerings(self) -> str:
        params = self._get_params()
        peerings, next_token = self.networkmanager_backend.list_peerings(
            core_network_id=params.get("coreNetworkId"), peering_type=params.get("peeringType"),
            edge_location=params.get("edgeLocation"), state=params.get("state"),
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"Peerings": [p.to_dict() for p in peerings], "NextToken": next_token})

    # --- Core Network Policy ---

    def put_core_network_policy(self) -> str:
        cn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        policy = self.networkmanager_backend.put_core_network_policy(
            core_network_id=cn_id, policy_document=params.get("PolicyDocument", ""),
            description=params.get("Description"), latest_version_id=params.get("LatestVersionId"),
            client_token=params.get("ClientToken"),
        )
        return json.dumps({"CoreNetworkPolicy": policy.to_dict()})

    def get_core_network_policy(self) -> str:
        cn_id = unquote(self.path.split("/")[-2])
        params = self._get_params()
        pvid = params.get("policyVersionId")
        if pvid:
            pvid = int(pvid)
        policy = self.networkmanager_backend.get_core_network_policy(
            core_network_id=cn_id, policy_version_id=pvid, alias=params.get("alias"),
        )
        return json.dumps({"CoreNetworkPolicy": policy.to_dict()})

    def delete_core_network_policy_version(self) -> str:
        parts = self.path.split("/")
        cn_id = unquote(parts[-3])
        pvid = int(unquote(parts[-1]))
        policy = self.networkmanager_backend.delete_core_network_policy_version(
            core_network_id=cn_id, policy_version_id=pvid,
        )
        return json.dumps({"CoreNetworkPolicy": policy.to_dict()})

    def restore_core_network_policy_version(self) -> str:
        parts = self.path.split("/")
        cn_id = unquote(parts[-4])
        pvid = int(unquote(parts[-2]))
        policy = self.networkmanager_backend.restore_core_network_policy_version(
            core_network_id=cn_id, policy_version_id=pvid,
        )
        return json.dumps({"CoreNetworkPolicy": policy.to_dict()})

    def list_core_network_policy_versions(self) -> str:
        cn_id = unquote(self.path.split("/")[-2])
        params = self._get_params()
        versions, next_token = self.networkmanager_backend.list_core_network_policy_versions(
            core_network_id=cn_id, max_results=params.get("maxResults"),
            next_token=params.get("nextToken"),
        )
        return json.dumps({"CoreNetworkPolicyVersions": [v.to_version_dict() for v in versions], "NextToken": next_token})

    def execute_core_network_change_set(self) -> str:
        parts = self.path.split("/")
        cn_id = unquote(parts[-4])
        pvid = int(unquote(parts[-2]))
        self.networkmanager_backend.execute_core_network_change_set(core_network_id=cn_id, policy_version_id=pvid)
        return json.dumps({})

    def get_core_network_change_set(self) -> str:
        parts = self.path.split("/")
        cn_id = unquote(parts[-3])
        pvid = int(unquote(parts[-1]))
        changes = self.networkmanager_backend.get_core_network_change_set(core_network_id=cn_id, policy_version_id=pvid)
        return json.dumps({"CoreNetworkChanges": changes})

    def get_core_network_change_events(self) -> str:
        parts = self.path.split("/")
        cn_id = unquote(parts[-3])
        pvid = int(unquote(parts[-1]))
        events = self.networkmanager_backend.get_core_network_change_events(core_network_id=cn_id, policy_version_id=pvid)
        return json.dumps({"CoreNetworkChangeEvents": events})

    # --- Resource Policy ---

    def put_resource_policy(self) -> str:
        resource_arn = unquote(self.path.split("/resource-policy/")[-1])
        params = json.loads(self.body)
        self.networkmanager_backend.put_resource_policy(resource_arn=resource_arn, policy_document=params.get("PolicyDocument", ""))
        return json.dumps({})

    def get_resource_policy(self) -> str:
        resource_arn = unquote(self.path.split("/resource-policy/")[-1])
        doc = self.networkmanager_backend.get_resource_policy(resource_arn=resource_arn)
        if doc is None:
            return json.dumps({})
        return json.dumps({"PolicyDocument": doc})

    def delete_resource_policy(self) -> str:
        resource_arn = unquote(self.path.split("/resource-policy/")[-1])
        self.networkmanager_backend.delete_resource_policy(resource_arn=resource_arn)
        return json.dumps({})

    # --- Connect Peer Association ---

    def associate_connect_peer(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        assoc = self.networkmanager_backend.associate_connect_peer(
            global_network_id=gn_id, connect_peer_id=params.get("ConnectPeerId"),
            device_id=params.get("DeviceId"), link_id=params.get("LinkId"),
        )
        return json.dumps({"ConnectPeerAssociation": assoc.to_dict()})

    def disassociate_connect_peer(self) -> str:
        parts = self.path.split("/")
        gn_id = unquote(parts[-3])
        cp_id = unquote(parts[-1])
        assoc = self.networkmanager_backend.disassociate_connect_peer(global_network_id=gn_id, connect_peer_id=cp_id)
        return json.dumps({"ConnectPeerAssociation": assoc.to_dict()})

    def get_connect_peer_associations(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = self._get_params()
        assocs, next_token = self.networkmanager_backend.get_connect_peer_associations(
            global_network_id=gn_id, connect_peer_ids=self.querystring.get("connectPeerIds"),
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"ConnectPeerAssociations": [a.to_dict() for a in assocs], "NextToken": next_token})

    # --- Customer Gateway Association ---

    def associate_customer_gateway(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        assoc = self.networkmanager_backend.associate_customer_gateway(
            global_network_id=gn_id, customer_gateway_arn=params.get("CustomerGatewayArn"),
            device_id=params.get("DeviceId"), link_id=params.get("LinkId"),
        )
        return json.dumps({"CustomerGatewayAssociation": assoc.to_dict()})

    def disassociate_customer_gateway(self) -> str:
        parts = self.path.split("/")
        gn_id = unquote(parts[-3])
        cgw_arn = unquote(parts[-1])
        assoc = self.networkmanager_backend.disassociate_customer_gateway(global_network_id=gn_id, customer_gateway_arn=cgw_arn)
        return json.dumps({"CustomerGatewayAssociation": assoc.to_dict()})

    def get_customer_gateway_associations(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = self._get_params()
        assocs, next_token = self.networkmanager_backend.get_customer_gateway_associations(
            global_network_id=gn_id, customer_gateway_arns=self.querystring.get("customerGatewayArns"),
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"CustomerGatewayAssociations": [a.to_dict() for a in assocs], "NextToken": next_token})

    # --- Link Association ---

    def associate_link(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        assoc = self.networkmanager_backend.associate_link(
            global_network_id=gn_id, device_id=params.get("DeviceId"), link_id=params.get("LinkId"),
        )
        return json.dumps({"LinkAssociation": assoc.to_dict()})

    def disassociate_link(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = self._get_params()
        assoc = self.networkmanager_backend.disassociate_link(
            global_network_id=gn_id, device_id=params.get("deviceId"), link_id=params.get("linkId"),
        )
        return json.dumps({"LinkAssociation": assoc.to_dict()})

    def get_link_associations(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = self._get_params()
        assocs, next_token = self.networkmanager_backend.get_link_associations(
            global_network_id=gn_id, device_id=params.get("deviceId"),
            link_id=params.get("linkId"), max_results=params.get("maxResults"),
            next_token=params.get("nextToken"),
        )
        return json.dumps({"LinkAssociations": [a.to_dict() for a in assocs], "NextToken": next_token})

    # --- Transit Gateway Connect Peer Association ---

    def associate_transit_gateway_connect_peer(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        assoc = self.networkmanager_backend.associate_transit_gateway_connect_peer(
            global_network_id=gn_id,
            transit_gateway_connect_peer_arn=params.get("TransitGatewayConnectPeerArn"),
            device_id=params.get("DeviceId"), link_id=params.get("LinkId"),
        )
        return json.dumps({"TransitGatewayConnectPeerAssociation": assoc.to_dict()})

    def disassociate_transit_gateway_connect_peer(self) -> str:
        parts = self.path.split("/")
        gn_id = unquote(parts[-3])
        tgw_cp_arn = unquote(parts[-1])
        assoc = self.networkmanager_backend.disassociate_transit_gateway_connect_peer(
            global_network_id=gn_id, transit_gateway_connect_peer_arn=tgw_cp_arn,
        )
        return json.dumps({"TransitGatewayConnectPeerAssociation": assoc.to_dict()})

    def get_transit_gateway_connect_peer_associations(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = self._get_params()
        assocs, next_token = self.networkmanager_backend.get_transit_gateway_connect_peer_associations(
            global_network_id=gn_id,
            transit_gateway_connect_peer_arns=self.querystring.get("transitGatewayConnectPeerArns"),
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"TransitGatewayConnectPeerAssociations": [a.to_dict() for a in assocs], "NextToken": next_token})

    # --- Transit Gateway Registration ---

    def register_transit_gateway(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        reg = self.networkmanager_backend.register_transit_gateway(
            global_network_id=gn_id, transit_gateway_arn=params.get("TransitGatewayArn"),
        )
        return json.dumps({"TransitGatewayRegistration": reg.to_dict()})

    def deregister_transit_gateway(self) -> str:
        parts = self.path.split("/")
        gn_id = unquote(parts[-3])
        tgw_arn = unquote(parts[-1])
        reg = self.networkmanager_backend.deregister_transit_gateway(
            global_network_id=gn_id, transit_gateway_arn=tgw_arn,
        )
        return json.dumps({"TransitGatewayRegistration": reg.to_dict()})

    def get_transit_gateway_registrations(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = self._get_params()
        regs, next_token = self.networkmanager_backend.get_transit_gateway_registrations(
            global_network_id=gn_id, transit_gateway_arns=self.querystring.get("transitGatewayArns"),
            max_results=params.get("maxResults"), next_token=params.get("nextToken"),
        )
        return json.dumps({"TransitGatewayRegistrations": [r.to_dict() for r in regs], "NextToken": next_token})

    # --- Route Analysis ---

    def start_route_analysis(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        ra = self.networkmanager_backend.start_route_analysis(
            global_network_id=gn_id, source=params.get("Source"),
            destination=params.get("Destination"),
            include_return_path=params.get("IncludeReturnPath", False),
            use_middleboxes=params.get("UseMiddleboxes", False),
        )
        return json.dumps({"RouteAnalysis": ra.to_dict()})

    def get_route_analysis(self) -> str:
        parts = self.path.split("/")
        gn_id = unquote(parts[-3])
        ra_id = unquote(parts[-1])
        ra = self.networkmanager_backend.get_route_analysis(global_network_id=gn_id, route_analysis_id=ra_id)
        return json.dumps({"RouteAnalysis": ra.to_dict()})

    # --- Network Resources ---

    def get_network_resources(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        return json.dumps({"NetworkResources": self.networkmanager_backend.get_network_resources(global_network_id=gn_id)})

    def get_network_resource_relationships(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        return json.dumps({"Relationships": self.networkmanager_backend.get_network_resource_relationships(global_network_id=gn_id)})

    def get_network_resource_counts(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        return json.dumps({"NetworkResourceCounts": self.networkmanager_backend.get_network_resource_counts(global_network_id=gn_id)})

    def get_network_routes(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        result = self.networkmanager_backend.get_network_routes(
            global_network_id=gn_id, route_table_identifier=params.get("RouteTableIdentifier"),
        )
        return json.dumps(result)

    def get_network_telemetry(self) -> str:
        gn_id = unquote(self.path.split("/")[-2])
        return json.dumps({"NetworkTelemetry": self.networkmanager_backend.get_network_telemetry(global_network_id=gn_id)})

    def update_network_resource_metadata(self) -> str:
        parts = self.path.split("/")
        gn_id = unquote(parts[-4])
        resource_arn = unquote(parts[-2])
        params = json.loads(self.body)
        result = self.networkmanager_backend.update_network_resource_metadata(
            global_network_id=gn_id, resource_arn=resource_arn, metadata=params.get("Metadata", {}),
        )
        return json.dumps(result)

    # --- Core Network Prefix List Association ---

    def create_core_network_prefix_list_association(self) -> str:
        params = json.loads(self.body)
        assoc = self.networkmanager_backend.create_core_network_prefix_list_association(
            core_network_id=params.get("CoreNetworkId"), prefix_list=params.get("PrefixList"),
            segment_name=params.get("SegmentName"),
        )
        return json.dumps({"PrefixListAssociation": assoc.to_dict()})

    def delete_core_network_prefix_list_association(self) -> str:
        parts = self.path.split("/")
        prefix_list_arn = unquote(parts[-3])
        cn_id = unquote(parts[-1])
        assoc = self.networkmanager_backend.delete_core_network_prefix_list_association(
            core_network_id=cn_id, prefix_list_arn=prefix_list_arn,
        )
        return json.dumps({"PrefixListAssociation": assoc.to_dict()})

    def list_core_network_prefix_list_associations(self) -> str:
        cn_id = unquote(self.path.split("/")[-1])
        assocs = self.networkmanager_backend.list_core_network_prefix_list_associations(core_network_id=cn_id)
        return json.dumps({"PrefixListAssociations": [a.to_dict() for a in assocs]})

    # --- Routing Policy Label ---

    def put_attachment_routing_policy_label(self) -> str:
        params = json.loads(self.body)
        result = self.networkmanager_backend.put_attachment_routing_policy_label(
            attachment_id=params.get("AttachmentId"), label=params.get("Label", ""),
        )
        return json.dumps(result)

    def remove_attachment_routing_policy_label(self) -> str:
        parts = self.path.split("/")
        cn_id = unquote(parts[-3])
        att_id = unquote(parts[-1])
        result = self.networkmanager_backend.remove_attachment_routing_policy_label(
            core_network_id=cn_id, attachment_id=att_id,
        )
        return json.dumps(result)

    def list_attachment_routing_policy_associations(self) -> str:
        cn_id = unquote(self.path.split("/")[-1])
        assocs = self.networkmanager_backend.list_attachment_routing_policy_associations(core_network_id=cn_id)
        return json.dumps({"AttachmentRoutingPolicyAssociations": assocs})

    # --- Core Network Routing Information ---

    def list_core_network_routing_information(self) -> str:
        cn_id = unquote(self.path.split("/")[-2])
        info = self.networkmanager_backend.list_core_network_routing_information(core_network_id=cn_id)
        return json.dumps({"CoreNetworkRoutingInformation": info})

    # --- Organization Service Access ---

    def start_organization_service_access_update(self) -> str:
        params = json.loads(self.body)
        result = self.networkmanager_backend.start_organization_service_access_update(action=params.get("Action", "ENABLE"))
        return json.dumps(result)

    def list_organization_service_access_status(self) -> str:
        return json.dumps(self.networkmanager_backend.list_organization_service_access_status())
