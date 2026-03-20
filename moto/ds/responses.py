"""Handles Directory Service requests, invokes methods, returns responses."""

import json

from moto.core.exceptions import InvalidToken
from moto.core.responses import BaseResponse
from moto.ds.exceptions import InvalidNextTokenException
from moto.ds.models import DirectoryServiceBackend, ds_backends


class DirectoryServiceResponse(BaseResponse):
    """Handler for DirectoryService requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="ds")

    @property
    def ds_backend(self) -> DirectoryServiceBackend:
        """Return backend instance specific for this region."""
        return ds_backends[self.current_account][self.region]

    def connect_directory(self) -> str:
        """Create an AD Connector to connect to a self-managed directory."""
        name = self._get_param("Name")
        short_name = self._get_param("ShortName")
        password = self._get_param("Password")
        description = self._get_param("Description")
        size = self._get_param("Size")
        connect_settings = self._get_param("ConnectSettings")
        tags = self._get_param("Tags", [])
        directory_id = self.ds_backend.connect_directory(
            region=self.region,
            name=name,
            short_name=short_name,
            password=password,
            description=description,
            size=size,
            connect_settings=connect_settings,
            tags=tags,
        )
        return json.dumps({"DirectoryId": directory_id})

    def create_directory(self) -> str:
        """Create a Simple AD directory."""
        name = self._get_param("Name")
        short_name = self._get_param("ShortName")
        password = self._get_param("Password")
        description = self._get_param("Description")
        size = self._get_param("Size")
        vpc_settings = self._get_param("VpcSettings")
        tags = self._get_param("Tags", [])
        directory_id = self.ds_backend.create_directory(
            region=self.region,
            name=name,
            short_name=short_name,
            password=password,
            description=description,
            size=size,
            vpc_settings=vpc_settings,
            tags=tags,
        )
        return json.dumps({"DirectoryId": directory_id})

    def create_alias(self) -> str:
        """Create an alias and assign the alias to the directory."""
        directory_id = self._get_param("DirectoryId")
        alias = self._get_param("Alias")
        response = self.ds_backend.create_alias(directory_id, alias)
        return json.dumps(response)

    def create_microsoft_ad(self) -> str:
        """Create a Microsoft AD directory."""
        name = self._get_param("Name")
        short_name = self._get_param("ShortName")
        password = self._get_param("Password")
        description = self._get_param("Description")
        vpc_settings = self._get_param("VpcSettings")
        edition = self._get_param("Edition")
        tags = self._get_param("Tags", [])
        directory_id = self.ds_backend.create_microsoft_ad(
            region=self.region,
            name=name,
            short_name=short_name,
            password=password,
            description=description,
            vpc_settings=vpc_settings,
            edition=edition,
            tags=tags,
        )
        return json.dumps({"DirectoryId": directory_id})

    def delete_directory(self) -> str:
        """Delete a Directory Service directory."""
        directory_id_arg = self._get_param("DirectoryId")
        directory_id = self.ds_backend.delete_directory(directory_id_arg)
        return json.dumps({"DirectoryId": directory_id})

    def describe_directories(self) -> str:
        """Return directory info for the given IDs or all IDs."""
        directory_ids = self._get_param("DirectoryIds")
        next_token = self._get_param("NextToken")
        limit = self._get_int_param("Limit")
        try:
            (directories, next_token) = self.ds_backend.describe_directories(
                directory_ids, next_token=next_token, limit=limit
            )
        except InvalidToken as exc:
            raise InvalidNextTokenException() from exc

        response = {
            "DirectoryDescriptions": [x.to_dict() for x in directories],
            "NextToken": next_token,
        }
        return json.dumps(response)

    def disable_sso(self) -> str:
        """Disable single-sign on for a directory."""
        directory_id = self._get_param("DirectoryId")
        username = self._get_param("UserName")
        password = self._get_param("Password")
        self.ds_backend.disable_sso(directory_id, username, password)
        return ""

    def enable_sso(self) -> str:
        """Enable single-sign on for a directory."""
        directory_id = self._get_param("DirectoryId")
        username = self._get_param("UserName")
        password = self._get_param("Password")
        self.ds_backend.enable_sso(directory_id, username, password)
        return ""

    def get_directory_limits(self) -> str:
        """Return directory limit information for the current region."""
        limits = self.ds_backend.get_directory_limits()
        return json.dumps({"DirectoryLimits": limits})

    def add_tags_to_resource(self) -> str:
        """Add or overwrite on or more tags for specified directory."""
        resource_id = self._get_param("ResourceId")
        tags = self._get_param("Tags")
        self.ds_backend.add_tags_to_resource(resource_id=resource_id, tags=tags)
        return ""

    def remove_tags_from_resource(self) -> str:
        """Removes tags from a directory."""
        resource_id = self._get_param("ResourceId")
        tag_keys = self._get_param("TagKeys")
        self.ds_backend.remove_tags_from_resource(
            resource_id=resource_id, tag_keys=tag_keys
        )
        return ""

    def list_tags_for_resource(self) -> str:
        """Lists all tags on a directory."""
        resource_id = self._get_param("ResourceId")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        try:
            tags, next_token = self.ds_backend.list_tags_for_resource(
                resource_id=resource_id, next_token=next_token, limit=limit
            )
        except InvalidToken as exc:
            raise InvalidNextTokenException() from exc

        response = {"Tags": tags, "NextToken": next_token}
        return json.dumps(response)

    def create_trust(self) -> str:
        directory_id = self._get_param("DirectoryId")
        remote_domain_name = self._get_param("RemoteDomainName")
        trust_password = self._get_param("TrustPassword")
        trust_direction = self._get_param("TrustDirection")
        trust_type = self._get_param("TrustType")
        conditional_forwarder_ip_addrs = self._get_param("ConditionalForwarderIpAddrs")
        selective_auth = self._get_param("SelectiveAuth")
        trust_id = self.ds_backend.create_trust(
            directory_id=directory_id,
            remote_domain_name=remote_domain_name,
            trust_password=trust_password,
            trust_direction=trust_direction,
            trust_type=trust_type,
            conditional_forwarder_ip_addrs=conditional_forwarder_ip_addrs,
            selective_auth=selective_auth,
        )
        return json.dumps({"TrustId": trust_id})

    def describe_trusts(self) -> str:
        directory_id = self._get_param("DirectoryId")
        trust_ids = self._get_param("TrustIds")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        trusts, next_token = self.ds_backend.describe_trusts(
            directory_id=directory_id,
            trust_ids=trust_ids,
            next_token=next_token,
            limit=limit,
        )
        trust_list = [trust.to_dict() for trust in trusts]
        return json.dumps({"Trusts": trust_list, "nextToken": next_token})

    def delete_trust(self) -> str:
        trust_id = self._get_param("TrustId")
        delete_associated_conditional_forwarder = self._get_param(
            "DeleteAssociatedConditionalForwarder"
        )
        trust_id = self.ds_backend.delete_trust(
            trust_id=trust_id,
            delete_associated_conditional_forwarder=delete_associated_conditional_forwarder,
        )
        return json.dumps({"TrustId": trust_id})

    def verify_trust(self) -> str:
        trust_id = self._get_param("TrustId")
        trust_id = self.ds_backend.verify_trust(trust_id=trust_id)
        return json.dumps({"TrustId": trust_id})

    def describe_ldaps_settings(self) -> str:
        directory_id = self._get_param("DirectoryId")
        type = self._get_param("Type")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        ldaps_settings_info, next_token = self.ds_backend.describe_ldaps_settings(
            directory_id=directory_id,
            type=type,
            next_token=next_token,
            limit=limit,
        )
        ldaps = [ldap.to_dict() for ldap in ldaps_settings_info]
        return json.dumps({"LDAPSSettingsInfo": ldaps, "nextToken": next_token})

    def enable_ldaps(self) -> str:
        directory_id = self._get_param("DirectoryId")
        type = self._get_param("Type")
        self.ds_backend.enable_ldaps(
            directory_id=directory_id,
            type=type,
        )
        return ""

    def disable_ldaps(self) -> str:
        directory_id = self._get_param("DirectoryId")
        type = self._get_param("Type")
        self.ds_backend.disable_ldaps(
            directory_id=directory_id,
            type=type,
        )
        return ""

    def describe_settings(self) -> str:
        directory_id = self._get_param("DirectoryId")
        status = self._get_param("Status")
        next_token = self._get_param("NextToken")
        setting_entries, next_token = self.ds_backend.describe_settings(
            directory_id=directory_id,
            status=status,
            next_token=next_token,
        )

        return json.dumps(
            {
                "DirectoryId": directory_id,
                "SettingEntries": setting_entries,
                "NextToken": next_token,
            }
        )

    def update_settings(self) -> str:
        directory_id = self._get_param("DirectoryId")
        settings = self._get_param("Settings")
        directory_id = self.ds_backend.update_settings(
            directory_id=directory_id,
            settings=settings,
        )
        return json.dumps({"DirectoryId": directory_id})

    def create_conditional_forwarder(self) -> str:
        directory_id = self._get_param("DirectoryId")
        remote_domain_name = self._get_param("RemoteDomainName")
        dns_ip_addrs = self._get_param("DnsIpAddrs")
        self.ds_backend.create_conditional_forwarder(
            directory_id=directory_id,
            remote_domain_name=remote_domain_name,
            dns_ip_addrs=dns_ip_addrs,
        )
        return json.dumps({})

    def delete_conditional_forwarder(self) -> str:
        directory_id = self._get_param("DirectoryId")
        remote_domain_name = self._get_param("RemoteDomainName")
        self.ds_backend.delete_conditional_forwarder(
            directory_id=directory_id,
            remote_domain_name=remote_domain_name,
        )
        return json.dumps({})

    def update_conditional_forwarder(self) -> str:
        directory_id = self._get_param("DirectoryId")
        remote_domain_name = self._get_param("RemoteDomainName")
        dns_ip_addrs = self._get_param("DnsIpAddrs")
        self.ds_backend.update_conditional_forwarder(
            directory_id=directory_id,
            remote_domain_name=remote_domain_name,
            dns_ip_addrs=dns_ip_addrs,
        )
        return json.dumps({})

    def describe_conditional_forwarders(self) -> str:
        directory_id = self._get_param("DirectoryId")
        remote_domain_names = self._get_param("RemoteDomainNames")
        forwarders = self.ds_backend.describe_conditional_forwarders(
            directory_id=directory_id,
            remote_domain_names=remote_domain_names,
        )
        return json.dumps({"ConditionalForwarders": forwarders})

    def describe_domain_controllers(self) -> str:
        directory_id = self._get_param("DirectoryId")
        domain_controller_ids = self._get_param("DomainControllerIds")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        controllers = self.ds_backend.describe_domain_controllers(
            directory_id=directory_id,
            domain_controller_ids=domain_controller_ids,
        )
        return json.dumps({"DomainControllers": controllers, "NextToken": None})

    def register_event_topic(self) -> str:
        directory_id = self._get_param("DirectoryId")
        topic_name = self._get_param("TopicName")
        sns_topic_arn = self._get_param("TopicName")  # AWS uses TopicName as the SNS topic
        self.ds_backend.register_event_topic(
            directory_id=directory_id,
            topic_name=topic_name,
            sns_topic_arn=sns_topic_arn,
        )
        return json.dumps({})

    def deregister_event_topic(self) -> str:
        directory_id = self._get_param("DirectoryId")
        topic_name = self._get_param("TopicName")
        self.ds_backend.deregister_event_topic(
            directory_id=directory_id,
            topic_name=topic_name,
        )
        return json.dumps({})

    def describe_event_topics(self) -> str:
        directory_id = self._get_param("DirectoryId")
        topic_names = self._get_param("TopicNames")
        topics = self.ds_backend.describe_event_topics(
            directory_id=directory_id,
            topic_names=topic_names,
        )
        return json.dumps({"EventTopics": topics})

    def create_snapshot(self) -> str:
        directory_id = self._get_param("DirectoryId")
        name = self._get_param("Name")
        snapshot_id = self.ds_backend.create_snapshot(
            directory_id=directory_id,
            name=name,
        )
        return json.dumps({"SnapshotId": snapshot_id})

    def delete_snapshot(self) -> str:
        snapshot_id = self._get_param("SnapshotId")
        snapshot_id = self.ds_backend.delete_snapshot(snapshot_id=snapshot_id)
        return json.dumps({"SnapshotId": snapshot_id})

    def restore_from_snapshot(self) -> str:
        snapshot_id = self._get_param("SnapshotId")
        self.ds_backend.restore_from_snapshot(snapshot_id=snapshot_id)
        return json.dumps({})

    def describe_snapshots(self) -> str:
        directory_id = self._get_param("DirectoryId")
        snapshot_ids = self._get_param("SnapshotIds")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        snapshots = self.ds_backend.describe_snapshots(
            directory_id=directory_id,
            snapshot_ids=snapshot_ids,
        )
        return json.dumps({"Snapshots": snapshots, "NextToken": None})

    def describe_shared_directories(self) -> str:
        owner_directory_id = self._get_param("OwnerDirectoryId")
        shared_directory_ids = self._get_param("SharedDirectoryIds")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        shared_dirs = self.ds_backend.describe_shared_directories(
            owner_directory_id=owner_directory_id,
            shared_directory_ids=shared_directory_ids,
        )
        return json.dumps({"SharedDirectories": shared_dirs, "NextToken": None})

    def describe_regions(self) -> str:
        directory_id = self._get_param("DirectoryId")
        region_name = self._get_param("RegionName")
        next_token = self._get_param("NextToken")
        regions = self.ds_backend.describe_regions(
            directory_id=directory_id,
            region_name=region_name,
        )
        return json.dumps({"RegionsDescription": regions, "NextToken": None})

    def enable_radius(self) -> str:
        directory_id = self._get_param("DirectoryId")
        radius_settings = self._get_param("RadiusSettings")
        self.ds_backend.enable_radius(
            directory_id=directory_id,
            radius_settings=radius_settings,
        )
        return json.dumps({})

    def disable_radius(self) -> str:
        directory_id = self._get_param("DirectoryId")
        self.ds_backend.disable_radius(directory_id=directory_id)
        return json.dumps({})

    def update_radius(self) -> str:
        directory_id = self._get_param("DirectoryId")
        radius_settings = self._get_param("RadiusSettings")
        self.ds_backend.update_radius(
            directory_id=directory_id,
            radius_settings=radius_settings,
        )
        return json.dumps({})

    def enable_client_authentication(self) -> str:
        directory_id = self._get_param("DirectoryId")
        type_param = self._get_param("Type")
        self.ds_backend.enable_client_authentication(
            directory_id=directory_id,
            type=type_param,
        )
        return json.dumps({})

    def disable_client_authentication(self) -> str:
        directory_id = self._get_param("DirectoryId")
        type_param = self._get_param("Type")
        self.ds_backend.disable_client_authentication(
            directory_id=directory_id,
            type=type_param,
        )
        return json.dumps({})

    def create_computer(self) -> str:
        directory_id = self._get_param("DirectoryId")
        computer_name = self._get_param("ComputerName")
        password = self._get_param("Password")
        ou_dn = self._get_param("OrganizationalUnitDistinguishedName")
        computer_attributes = self._get_param("ComputerAttributes")
        computer = self.ds_backend.create_computer(
            directory_id=directory_id,
            computer_name=computer_name,
            password=password,
            organizational_unit_distinguished_name=ou_dn,
            computer_attributes=computer_attributes,
        )
        return json.dumps({"Computer": computer})

    def reset_user_password(self) -> str:
        directory_id = self._get_param("DirectoryId")
        user_name = self._get_param("UserName")
        new_password = self._get_param("NewPassword")
        self.ds_backend.reset_user_password(
            directory_id=directory_id,
            user_name=user_name,
            new_password=new_password,
        )
        return json.dumps({})

    def describe_client_authentication_settings(self) -> str:
        directory_id = self._get_param("DirectoryId")
        type_param = self._get_param("Type")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        settings = self.ds_backend.describe_client_authentication_settings(
            directory_id=directory_id,
            type=type_param,
        )
        return json.dumps(
            {"ClientAuthenticationSettingsInfo": settings, "NextToken": None}
        )

    def describe_update_directory(self) -> str:
        directory_id = self._get_param("DirectoryId")
        update_type = self._get_param("UpdateType")
        next_token = self._get_param("NextToken")
        updates = self.ds_backend.describe_update_directory(
            directory_id=directory_id,
            update_type=update_type,
        )
        return json.dumps({"UpdateActivities": updates, "NextToken": None})

    def register_certificate(self) -> str:
        directory_id = self._get_param("DirectoryId")
        certificate_data = self._get_param("CertificateData")
        client_cert_auth_settings = self._get_param("ClientCertAuthSettings")
        cert_type = self._get_param("Type")
        certificate_id = self.ds_backend.register_certificate(
            directory_id=directory_id,
            certificate_data=certificate_data,
            client_cert_auth_settings=client_cert_auth_settings,
            cert_type=cert_type,
        )
        return json.dumps({"CertificateId": certificate_id})

    def deregister_certificate(self) -> str:
        directory_id = self._get_param("DirectoryId")
        certificate_id = self._get_param("CertificateId")
        self.ds_backend.deregister_certificate(
            directory_id=directory_id,
            certificate_id=certificate_id,
        )
        return json.dumps({})

    def list_certificates(self) -> str:
        directory_id = self._get_param("DirectoryId")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        certs = self.ds_backend.list_certificates(directory_id=directory_id)
        return json.dumps({"CertificatesInfo": certs, "NextToken": None})

    def describe_certificate(self) -> str:
        directory_id = self._get_param("DirectoryId")
        certificate_id = self._get_param("CertificateId")
        certificate = self.ds_backend.describe_certificate(
            directory_id=directory_id,
            certificate_id=certificate_id,
        )
        return json.dumps({"Certificate": certificate})

    def get_snapshot_limits(self) -> str:
        directory_id = self._get_param("DirectoryId")
        limits = self.ds_backend.get_snapshot_limits(directory_id=directory_id)
        return json.dumps({"SnapshotLimits": limits})

    def add_ip_routes(self) -> str:
        directory_id = self._get_param("DirectoryId")
        ip_routes = self._get_param("IpRoutes")
        update_sg = self._get_param("UpdateSecurityGroupForDirectoryControllers", False)
        self.ds_backend.add_ip_routes(
            directory_id=directory_id,
            ip_routes=ip_routes,
            update_security_group_for_directory_controllers=update_sg,
        )
        return json.dumps({})

    def remove_ip_routes(self) -> str:
        directory_id = self._get_param("DirectoryId")
        cidr_ips = self._get_param("CidrIps")
        self.ds_backend.remove_ip_routes(
            directory_id=directory_id,
            cidr_ips=cidr_ips,
        )
        return json.dumps({})

    def list_ip_routes(self) -> str:
        directory_id = self._get_param("DirectoryId")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        routes = self.ds_backend.list_ip_routes(directory_id=directory_id)
        return json.dumps({"IpRoutesInfo": routes, "NextToken": None})

    def start_schema_extension(self) -> str:
        directory_id = self._get_param("DirectoryId")
        create_snapshot = self._get_param(
            "CreateSnapshotBeforeSchemaExtension", False
        )
        ldif_content = self._get_param("LdifContent")
        description = self._get_param("Description")
        schema_extension_id = self.ds_backend.start_schema_extension(
            directory_id=directory_id,
            create_snapshot_before_schema_extension=create_snapshot,
            ldif_content=ldif_content,
            description=description,
        )
        return json.dumps({"SchemaExtensionId": schema_extension_id})

    def cancel_schema_extension(self) -> str:
        directory_id = self._get_param("DirectoryId")
        schema_extension_id = self._get_param("SchemaExtensionId")
        self.ds_backend.cancel_schema_extension(
            directory_id=directory_id,
            schema_extension_id=schema_extension_id,
        )
        return json.dumps({})

    def list_schema_extensions(self) -> str:
        directory_id = self._get_param("DirectoryId")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        extensions = self.ds_backend.list_schema_extensions(directory_id=directory_id)
        return json.dumps({"SchemaExtensionsInfo": extensions, "NextToken": None})

    def create_log_subscription(self) -> str:
        directory_id = self._get_param("DirectoryId")
        log_group_name = self._get_param("LogGroupName")
        self.ds_backend.create_log_subscription(
            directory_id=directory_id,
            log_group_name=log_group_name,
        )
        return json.dumps({})

    def list_log_subscriptions(self) -> str:
        directory_id = self._get_param("DirectoryId")
        next_token = self._get_param("NextToken")
        limit = self._get_param("Limit")
        log_subscriptions, next_token = self.ds_backend.list_log_subscriptions(
            directory_id=directory_id,
            next_token=next_token,
            limit=limit,
        )
        list_subscriptions = [sub.to_dict() for sub in log_subscriptions]
        return json.dumps(
            {"LogSubscriptions": list_subscriptions, "NextToken": next_token}
        )

    def delete_log_subscription(self) -> str:
        directory_id = self._get_param("DirectoryId")
        self.ds_backend.delete_log_subscription(
            directory_id=directory_id,
        )
        return json.dumps({})

    def share_directory(self) -> str:
        directory_id = self._get_param("DirectoryId")
        share_target = self._get_param("ShareTarget")
        share_method = self._get_param("ShareMethod")
        share_notes = self._get_param("ShareNotes")
        shared_directory_id = self.ds_backend.share_directory(
            directory_id=directory_id,
            share_target=share_target,
            share_method=share_method,
            share_notes=share_notes,
        )
        return json.dumps({"SharedDirectoryId": shared_directory_id})

    def unshare_directory(self) -> str:
        directory_id = self._get_param("DirectoryId")
        unshare_target = self._get_param("UnshareTarget")
        shared_directory_id = self.ds_backend.unshare_directory(
            directory_id=directory_id,
            unshare_target=unshare_target,
        )
        return json.dumps({"SharedDirectoryId": shared_directory_id})

    def accept_shared_directory(self) -> str:
        shared_directory_id = self._get_param("SharedDirectoryId")
        shared_directory = self.ds_backend.accept_shared_directory(
            shared_directory_id=shared_directory_id,
        )
        return json.dumps({"SharedDirectory": shared_directory})

    def reject_shared_directory(self) -> str:
        shared_directory_id = self._get_param("SharedDirectoryId")
        shared_directory_id = self.ds_backend.reject_shared_directory(
            shared_directory_id=shared_directory_id,
        )
        return json.dumps({"SharedDirectoryId": shared_directory_id})

    def add_region(self) -> str:
        directory_id = self._get_param("DirectoryId")
        region_name = self._get_param("RegionName")
        vpc_settings = self._get_param("VPCSettings")
        self.ds_backend.add_region(
            directory_id=directory_id,
            region_name=region_name,
            vpc_settings=vpc_settings,
        )
        return json.dumps({})

    def remove_region(self) -> str:
        directory_id = self._get_param("DirectoryId")
        self.ds_backend.remove_region(directory_id=directory_id)
        return json.dumps({})

    def start_schema_extension(self) -> str:
        directory_id = self._get_param("DirectoryId")
        create_snapshot = self._get_param(
            "CreateSnapshotBeforeSchemaExtension", False
        )
        ldif_content = self._get_param("LdifContent")
        description = self._get_param("Description")
        schema_extension_id = self.ds_backend.start_schema_extension(
            directory_id=directory_id,
            create_snapshot_before_schema_extension=create_snapshot,
            ldif_content=ldif_content,
            description=description,
        )
        return json.dumps({"SchemaExtensionId": schema_extension_id})

    def cancel_schema_extension(self) -> str:
        directory_id = self._get_param("DirectoryId")
        schema_extension_id = self._get_param("SchemaExtensionId")
        self.ds_backend.cancel_schema_extension(
            directory_id=directory_id,
            schema_extension_id=schema_extension_id,
        )
        return json.dumps({})

    def update_directory_setup(self) -> str:
        directory_id = self._get_param("DirectoryId")
        update_type = self._get_param("UpdateType")
        os_update_settings = self._get_param("OSUpdateSettings")
        create_snapshot = self._get_param("CreateSnapshotBeforeUpdate", False)
        self.ds_backend.update_directory_setup(
            directory_id=directory_id,
            update_type=update_type,
            os_update_settings=os_update_settings,
            create_snapshot_before_update=create_snapshot,
        )
        return json.dumps({})

    def update_number_of_domain_controllers(self) -> str:
        directory_id = self._get_param("DirectoryId")
        desired_number = self._get_int_param("DesiredNumber")
        self.ds_backend.update_number_of_domain_controllers(
            directory_id=directory_id,
            desired_number=desired_number,
        )
        return json.dumps({})

    def start_ad_assessment(self) -> str:
        directory_id = self._get_param("DirectoryId")
        assessment_id = self.ds_backend.start_ad_assessment(
            directory_id=directory_id,
        )
        return json.dumps({"AssessmentId": assessment_id})

    def describe_ad_assessment(self) -> str:
        assessment_id = self._get_param("AssessmentId")
        assessment = self.ds_backend.describe_ad_assessment(
            assessment_id=assessment_id,
        )
        return json.dumps({"Assessment": assessment})

    def delete_ad_assessment(self) -> str:
        assessment_id = self._get_param("AssessmentId")
        self.ds_backend.delete_ad_assessment(assessment_id=assessment_id)
        return json.dumps({})

    def list_ad_assessments(self) -> str:
        directory_id = self._get_param("DirectoryId")
        assessments = self.ds_backend.list_ad_assessments(
            directory_id=directory_id,
        )
        return json.dumps({"Assessments": assessments})

    def enable_directory_data_access(self) -> str:
        directory_id = self._get_param("DirectoryId")
        self.ds_backend.enable_directory_data_access(directory_id=directory_id)
        return json.dumps({})

    def disable_directory_data_access(self) -> str:
        directory_id = self._get_param("DirectoryId")
        self.ds_backend.disable_directory_data_access(directory_id=directory_id)
        return json.dumps({})

    def describe_directory_data_access(self) -> str:
        directory_id = self._get_param("DirectoryId")
        result = self.ds_backend.describe_directory_data_access(
            directory_id=directory_id,
        )
        return json.dumps(result)

    def enable_ca_enrollment_policy(self) -> str:
        directory_id = self._get_param("DirectoryId")
        self.ds_backend.enable_ca_enrollment_policy(directory_id=directory_id)
        return json.dumps({})

    def disable_ca_enrollment_policy(self) -> str:
        directory_id = self._get_param("DirectoryId")
        self.ds_backend.disable_ca_enrollment_policy(directory_id=directory_id)
        return json.dumps({})

    def describe_ca_enrollment_policy(self) -> str:
        directory_id = self._get_param("DirectoryId")
        policy = self.ds_backend.describe_ca_enrollment_policy(
            directory_id=directory_id,
        )
        return json.dumps(policy)

    def update_trust(self) -> str:
        """Stub: UpdateTrust is not implemented in Moto backend."""
        return json.dumps({"RequestId": "stub", "TrustId": ""})
