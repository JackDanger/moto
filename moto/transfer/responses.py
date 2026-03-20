"""Handles incoming transfer requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import TransferBackend, transfer_backends


class TransferResponse(BaseResponse):
    """Handler for Transfer requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="transfer")

    @property
    def transfer_backend(self) -> TransferBackend:
        return transfer_backends[self.current_account][self.region]

    # ======== Server operations ========

    def create_server(self) -> str:
        params = json.loads(self.body)
        server_id = self.transfer_backend.create_server(
            certificate=params.get("Certificate"),
            domain=params.get("Domain"),
            endpoint_details=params.get("EndpointDetails"),
            endpoint_type=params.get("EndpointType"),
            host_key=params.get("HostKey"),
            identity_provider_details=params.get("IdentityProviderDetails"),
            identity_provider_type=params.get("IdentityProviderType"),
            logging_role=params.get("LoggingRole"),
            post_authentication_login_banner=params.get(
                "PostAuthenticationLoginBanner"
            ),
            pre_authentication_login_banner=params.get("PreAuthenticationLoginBanner"),
            protocols=params.get("Protocols"),
            protocol_details=params.get("ProtocolDetails"),
            security_policy_name=params.get("SecurityPolicyName"),
            structured_log_destinations=params.get("StructuredLogDestinations"),
            s3_storage_options=params.get("S3StorageOptions"),
            tags=params.get("Tags"),
            workflow_details=params.get("WorkflowDetails"),
        )
        return json.dumps({"ServerId": server_id})

    def describe_server(self) -> str:
        params = json.loads(self.body)
        server = self.transfer_backend.describe_server(
            server_id=params.get("ServerId"),
        )
        return json.dumps({"Server": server.to_dict()})

    def delete_server(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_server(
            server_id=params.get("ServerId"),
        )
        return json.dumps({})

    def update_server(self) -> str:
        params = json.loads(self.body)
        server_id = self.transfer_backend.update_server(
            server_id=params["ServerId"],
            certificate=params.get("Certificate"),
            protocol_details=params.get("ProtocolDetails"),
            endpoint_details=params.get("EndpointDetails"),
            endpoint_type=params.get("EndpointType"),
            host_key=params.get("HostKey"),
            identity_provider_details=params.get("IdentityProviderDetails"),
            logging_role=params.get("LoggingRole"),
            post_authentication_login_banner=params.get(
                "PostAuthenticationLoginBanner"
            ),
            pre_authentication_login_banner=params.get("PreAuthenticationLoginBanner"),
            protocols=params.get("Protocols"),
            security_policy_name=params.get("SecurityPolicyName"),
            workflow_details=params.get("WorkflowDetails"),
            structured_log_destinations=params.get("StructuredLogDestinations"),
            s3_storage_options=params.get("S3StorageOptions"),
        )
        return json.dumps({"ServerId": server_id})

    def start_server(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.start_server(server_id=params["ServerId"])
        return json.dumps({})

    def stop_server(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.stop_server(server_id=params["ServerId"])
        return json.dumps({})

    def list_servers(self) -> str:
        servers = self.transfer_backend.list_servers()
        return json.dumps({"Servers": [s.to_short_dict() for s in servers]})

    # ======== User operations ========

    def create_user(self) -> str:
        params = json.loads(self.body)
        server_id, user_name = self.transfer_backend.create_user(
            home_directory=params.get("HomeDirectory"),
            home_directory_type=params.get("HomeDirectoryType"),
            home_directory_mappings=params.get("HomeDirectoryMappings"),
            policy=params.get("Policy"),
            posix_profile=params.get("PosixProfile"),
            role=params.get("Role"),
            server_id=params.get("ServerId"),
            ssh_public_key_body=params.get("SshPublicKeyBody"),
            tags=params.get("Tags"),
            user_name=params.get("UserName"),
        )
        return json.dumps({"ServerId": server_id, "UserName": user_name})

    def describe_user(self) -> str:
        params = json.loads(self.body)
        server_id, user = self.transfer_backend.describe_user(
            server_id=params.get("ServerId"),
            user_name=params.get("UserName"),
        )
        return json.dumps({"ServerId": server_id, "User": user.to_dict()})

    def delete_user(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_user(
            server_id=params.get("ServerId"),
            user_name=params.get("UserName"),
        )
        return json.dumps({})

    def update_user(self) -> str:
        params = json.loads(self.body)
        server_id, user_name = self.transfer_backend.update_user(
            server_id=params["ServerId"],
            user_name=params["UserName"],
            home_directory=params.get("HomeDirectory"),
            home_directory_type=params.get("HomeDirectoryType"),
            home_directory_mappings=params.get("HomeDirectoryMappings"),
            policy=params.get("Policy"),
            posix_profile=params.get("PosixProfile"),
            role=params.get("Role"),
        )
        return json.dumps({"ServerId": server_id, "UserName": user_name})

    def list_users(self) -> str:
        params = json.loads(self.body)
        server_id, users = self.transfer_backend.list_users(
            server_id=params["ServerId"],
        )
        return json.dumps({
            "ServerId": server_id,
            "Users": [u.to_short_dict() for u in users],
        })

    # ======== SSH Public Key operations ========

    def import_ssh_public_key(self) -> str:
        params = json.loads(self.body)
        server_id, ssh_public_key_id, user_name = (
            self.transfer_backend.import_ssh_public_key(
                server_id=params.get("ServerId"),
                ssh_public_key_body=params.get("SshPublicKeyBody"),
                user_name=params.get("UserName"),
            )
        )
        return json.dumps(
            {
                "ServerId": server_id,
                "SshPublicKeyId": ssh_public_key_id,
                "UserName": user_name,
            }
        )

    def delete_ssh_public_key(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_ssh_public_key(
            server_id=params.get("ServerId"),
            ssh_public_key_id=params.get("SshPublicKeyId"),
            user_name=params.get("UserName"),
        )
        return json.dumps({})

    # ======== Access operations ========

    def create_access(self) -> str:
        params = json.loads(self.body)
        server_id, external_id = self.transfer_backend.create_access(
            server_id=params["ServerId"],
            external_id=params["ExternalId"],
            home_directory=params.get("HomeDirectory"),
            home_directory_type=params.get("HomeDirectoryType"),
            home_directory_mappings=params.get("HomeDirectoryMappings"),
            policy=params.get("Policy"),
            posix_profile=params.get("PosixProfile"),
            role=params["Role"],
        )
        return json.dumps({"ServerId": server_id, "ExternalId": external_id})

    def describe_access(self) -> str:
        params = json.loads(self.body)
        server_id, access = self.transfer_backend.describe_access(
            server_id=params["ServerId"],
            external_id=params["ExternalId"],
        )
        return json.dumps({"ServerId": server_id, "Access": access.to_dict()})

    def delete_access(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_access(
            server_id=params["ServerId"],
            external_id=params["ExternalId"],
        )
        return json.dumps({})

    def update_access(self) -> str:
        params = json.loads(self.body)
        server_id, external_id = self.transfer_backend.update_access(
            server_id=params["ServerId"],
            external_id=params["ExternalId"],
            home_directory=params.get("HomeDirectory"),
            home_directory_type=params.get("HomeDirectoryType"),
            home_directory_mappings=params.get("HomeDirectoryMappings"),
            policy=params.get("Policy"),
            posix_profile=params.get("PosixProfile"),
            role=params.get("Role"),
        )
        return json.dumps({"ServerId": server_id, "ExternalId": external_id})

    def list_accesses(self) -> str:
        params = json.loads(self.body)
        server_id, accesses = self.transfer_backend.list_accesses(
            server_id=params["ServerId"],
        )
        return json.dumps({
            "ServerId": server_id,
            "Accesses": [a.to_short_dict() for a in accesses],
        })

    # ======== Agreement operations ========

    def create_agreement(self) -> str:
        params = json.loads(self.body)
        agreement_id = self.transfer_backend.create_agreement(
            server_id=params["ServerId"],
            local_profile_id=params["LocalProfileId"],
            partner_profile_id=params["PartnerProfileId"],
            access_role=params["AccessRole"],
            description=params.get("Description"),
            base_directory=params.get("BaseDirectory"),
            status=params.get("Status"),
            tags=params.get("Tags"),
            preserve_filename=params.get("PreserveFilename"),
            enforce_message_signing=params.get("EnforceMessageSigning"),
            custom_directories=params.get("CustomDirectories"),
        )
        return json.dumps({"AgreementId": agreement_id})

    def describe_agreement(self) -> str:
        params = json.loads(self.body)
        agreement = self.transfer_backend.describe_agreement(
            agreement_id=params["AgreementId"],
            server_id=params["ServerId"],
        )
        return json.dumps({"Agreement": agreement.to_dict()})

    def delete_agreement(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_agreement(
            agreement_id=params["AgreementId"],
            server_id=params["ServerId"],
        )
        return json.dumps({})

    def update_agreement(self) -> str:
        params = json.loads(self.body)
        agreement_id = self.transfer_backend.update_agreement(
            agreement_id=params["AgreementId"],
            server_id=params["ServerId"],
            description=params.get("Description"),
            status=params.get("Status"),
            local_profile_id=params.get("LocalProfileId"),
            partner_profile_id=params.get("PartnerProfileId"),
            base_directory=params.get("BaseDirectory"),
            access_role=params.get("AccessRole"),
            preserve_filename=params.get("PreserveFilename"),
            enforce_message_signing=params.get("EnforceMessageSigning"),
            custom_directories=params.get("CustomDirectories"),
        )
        return json.dumps({"AgreementId": agreement_id})

    def list_agreements(self) -> str:
        params = json.loads(self.body)
        agreements = self.transfer_backend.list_agreements(
            server_id=params["ServerId"],
        )
        return json.dumps({
            "Agreements": [a.to_short_dict() for a in agreements],
        })

    # ======== Certificate operations ========

    def import_certificate(self) -> str:
        params = json.loads(self.body)
        certificate_id = self.transfer_backend.import_certificate(
            usage=params["Usage"],
            certificate=params["Certificate"],
            certificate_chain=params.get("CertificateChain"),
            private_key=params.get("PrivateKey"),
            active_date=params.get("ActiveDate"),
            inactive_date=params.get("InactiveDate"),
            description=params.get("Description"),
            tags=params.get("Tags"),
        )
        return json.dumps({"CertificateId": certificate_id})

    def describe_certificate(self) -> str:
        params = json.loads(self.body)
        cert = self.transfer_backend.describe_certificate(
            certificate_id=params["CertificateId"],
        )
        return json.dumps({"Certificate": cert.to_dict()})

    def delete_certificate(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_certificate(
            certificate_id=params["CertificateId"],
        )
        return json.dumps({})

    def update_certificate(self) -> str:
        params = json.loads(self.body)
        certificate_id = self.transfer_backend.update_certificate(
            certificate_id=params["CertificateId"],
            active_date=params.get("ActiveDate"),
            inactive_date=params.get("InactiveDate"),
            description=params.get("Description"),
        )
        return json.dumps({"CertificateId": certificate_id})

    def list_certificates(self) -> str:
        certs = self.transfer_backend.list_certificates()
        return json.dumps({
            "Certificates": [c.to_short_dict() for c in certs],
        })

    # ======== Connector operations ========

    def create_connector(self) -> str:
        params = json.loads(self.body)
        connector_id = self.transfer_backend.create_connector(
            url=params.get("Url"),
            as2_config=params.get("As2Config"),
            access_role=params["AccessRole"],
            logging_role=params.get("LoggingRole"),
            tags=params.get("Tags"),
            sftp_config=params.get("SftpConfig"),
            security_policy_name=params.get("SecurityPolicyName"),
            egress_config=params.get("EgressConfig"),
        )
        return json.dumps({"ConnectorId": connector_id})

    def describe_connector(self) -> str:
        params = json.loads(self.body)
        conn = self.transfer_backend.describe_connector(
            connector_id=params["ConnectorId"],
        )
        return json.dumps({"Connector": conn.to_dict()})

    def delete_connector(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_connector(
            connector_id=params["ConnectorId"],
        )
        return json.dumps({})

    def update_connector(self) -> str:
        params = json.loads(self.body)
        connector_id = self.transfer_backend.update_connector(
            connector_id=params["ConnectorId"],
            url=params.get("Url"),
            as2_config=params.get("As2Config"),
            access_role=params.get("AccessRole"),
            logging_role=params.get("LoggingRole"),
            sftp_config=params.get("SftpConfig"),
            security_policy_name=params.get("SecurityPolicyName"),
            egress_config=params.get("EgressConfig"),
        )
        return json.dumps({"ConnectorId": connector_id})

    def list_connectors(self) -> str:
        connectors = self.transfer_backend.list_connectors()
        return json.dumps({
            "Connectors": [c.to_short_dict() for c in connectors],
        })

    def test_connection(self) -> str:
        params = json.loads(self.body)
        connector_id, status, status_message = self.transfer_backend.test_connection(
            connector_id=params["ConnectorId"],
        )
        return json.dumps({
            "ConnectorId": connector_id,
            "Status": status,
            "StatusMessage": status_message,
        })

    # ======== Profile operations ========

    def create_profile(self) -> str:
        params = json.loads(self.body)
        profile_id = self.transfer_backend.create_profile(
            as2_id=params["As2Id"],
            profile_type=params["ProfileType"],
            certificate_ids=params.get("CertificateIds"),
            tags=params.get("Tags"),
        )
        return json.dumps({"ProfileId": profile_id})

    def describe_profile(self) -> str:
        params = json.loads(self.body)
        profile = self.transfer_backend.describe_profile(
            profile_id=params["ProfileId"],
        )
        return json.dumps({"Profile": profile.to_dict()})

    def delete_profile(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_profile(
            profile_id=params["ProfileId"],
        )
        return json.dumps({})

    def update_profile(self) -> str:
        params = json.loads(self.body)
        profile_id = self.transfer_backend.update_profile(
            profile_id=params["ProfileId"],
            certificate_ids=params.get("CertificateIds"),
        )
        return json.dumps({"ProfileId": profile_id})

    def list_profiles(self) -> str:
        params = json.loads(self.body)
        profiles = self.transfer_backend.list_profiles(
            profile_type=params.get("ProfileType"),
        )
        return json.dumps({
            "Profiles": [p.to_short_dict() for p in profiles],
        })

    # ======== Workflow operations ========

    def create_workflow(self) -> str:
        params = json.loads(self.body)
        workflow_id = self.transfer_backend.create_workflow(
            description=params.get("Description"),
            steps=params["Steps"],
            on_exception_steps=params.get("OnExceptionSteps"),
            tags=params.get("Tags"),
        )
        return json.dumps({"WorkflowId": workflow_id})

    def describe_workflow(self) -> str:
        params = json.loads(self.body)
        workflow = self.transfer_backend.describe_workflow(
            workflow_id=params["WorkflowId"],
        )
        return json.dumps({"Workflow": workflow.to_dict()})

    def delete_workflow(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_workflow(
            workflow_id=params["WorkflowId"],
        )
        return json.dumps({})

    def list_workflows(self) -> str:
        workflows = self.transfer_backend.list_workflows()
        return json.dumps({
            "Workflows": [w.to_short_dict() for w in workflows],
        })

    def send_workflow_step_state(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.send_workflow_step_state(
            workflow_id=params["WorkflowId"],
            execution_id=params["ExecutionId"],
            token=params["Token"],
            status=params["Status"],
        )
        return json.dumps({})

    def describe_execution(self) -> str:
        params = json.loads(self.body)
        workflow_id, execution = self.transfer_backend.describe_execution(
            workflow_id=params["WorkflowId"],
            execution_id=params["ExecutionId"],
        )
        return json.dumps({
            "WorkflowId": workflow_id,
            "Execution": execution,
        })

    def list_executions(self) -> str:
        params = json.loads(self.body)
        workflow_id, executions = self.transfer_backend.list_executions(
            workflow_id=params["WorkflowId"],
        )
        return json.dumps({
            "WorkflowId": workflow_id,
            "Executions": executions,
        })

    # ======== HostKey operations ========

    def import_host_key(self) -> str:
        params = json.loads(self.body)
        server_id, host_key_id = self.transfer_backend.import_host_key(
            server_id=params["ServerId"],
            host_key_body=params["HostKeyBody"],
            description=params.get("Description"),
            tags=params.get("Tags"),
        )
        return json.dumps({"ServerId": server_id, "HostKeyId": host_key_id})

    def describe_host_key(self) -> str:
        params = json.loads(self.body)
        host_key = self.transfer_backend.describe_host_key(
            server_id=params["ServerId"],
            host_key_id=params["HostKeyId"],
        )
        return json.dumps({"HostKey": host_key.to_dict()})

    def delete_host_key(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_host_key(
            server_id=params["ServerId"],
            host_key_id=params["HostKeyId"],
        )
        return json.dumps({})

    def update_host_key(self) -> str:
        params = json.loads(self.body)
        server_id, host_key_id = self.transfer_backend.update_host_key(
            server_id=params["ServerId"],
            host_key_id=params["HostKeyId"],
            description=params["Description"],
        )
        return json.dumps({"ServerId": server_id, "HostKeyId": host_key_id})

    def list_host_keys(self) -> str:
        params = json.loads(self.body)
        server_id, host_keys = self.transfer_backend.list_host_keys(
            server_id=params["ServerId"],
        )
        return json.dumps({
            "ServerId": server_id,
            "HostKeys": [hk.to_short_dict() for hk in host_keys],
        })

    # ======== WebApp operations ========

    def create_web_app(self) -> str:
        params = json.loads(self.body)
        web_app_id = self.transfer_backend.create_web_app(
            identity_provider_details=params["IdentityProviderDetails"],
            access_endpoint=params.get("AccessEndpoint"),
            web_app_units=params.get("WebAppUnits"),
            tags=params.get("Tags"),
            web_app_endpoint_policy=params.get("WebAppEndpointPolicy"),
            endpoint_details=params.get("EndpointDetails"),
        )
        return json.dumps({"WebAppId": web_app_id})

    def describe_web_app(self) -> str:
        params = json.loads(self.body)
        web_app = self.transfer_backend.describe_web_app(
            web_app_id=params["WebAppId"],
        )
        return json.dumps({"WebApp": web_app.to_dict()})

    def delete_web_app(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_web_app(
            web_app_id=params["WebAppId"],
        )
        return json.dumps({})

    def update_web_app(self) -> str:
        params = json.loads(self.body)
        web_app_id = self.transfer_backend.update_web_app(
            web_app_id=params["WebAppId"],
            identity_provider_details=params.get("IdentityProviderDetails"),
            access_endpoint=params.get("AccessEndpoint"),
            web_app_units=params.get("WebAppUnits"),
            endpoint_details=params.get("EndpointDetails"),
        )
        return json.dumps({"WebAppId": web_app_id})

    def list_web_apps(self) -> str:
        web_apps = self.transfer_backend.list_web_apps()
        return json.dumps({
            "WebApps": [wa.to_short_dict() for wa in web_apps],
        })

    # ======== WebApp Customization operations ========

    def update_web_app_customization(self) -> str:
        params = json.loads(self.body)
        import base64

        logo_file = None
        if params.get("LogoFile"):
            logo_file = base64.b64decode(params["LogoFile"])
        favicon_file = None
        if params.get("FaviconFile"):
            favicon_file = base64.b64decode(params["FaviconFile"])
        web_app_id = self.transfer_backend.update_web_app_customization(
            web_app_id=params["WebAppId"],
            title=params.get("Title"),
            logo_file=logo_file,
            favicon_file=favicon_file,
        )
        return json.dumps({"WebAppId": web_app_id})

    def describe_web_app_customization(self) -> str:
        params = json.loads(self.body)
        customization = self.transfer_backend.describe_web_app_customization(
            web_app_id=params["WebAppId"],
        )
        return json.dumps({"WebAppCustomization": customization.to_dict()})

    def delete_web_app_customization(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.delete_web_app_customization(
            web_app_id=params["WebAppId"],
        )
        return json.dumps({})

    # ======== Security Policy operations ========

    def describe_security_policy(self) -> str:
        params = json.loads(self.body)
        policy = self.transfer_backend.describe_security_policy(
            security_policy_name=params["SecurityPolicyName"],
        )
        return json.dumps({"SecurityPolicy": policy})

    def list_security_policies(self) -> str:
        names = self.transfer_backend.list_security_policies()
        return json.dumps({"SecurityPolicyNames": names})

    # ======== Tag operations ========

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.tag_resource(
            arn=params["Arn"],
            tags=params["Tags"],
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        self.transfer_backend.untag_resource(
            arn=params["Arn"],
            tag_keys=params["TagKeys"],
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        arn, tags = self.transfer_backend.list_tags_for_resource(
            arn=params["Arn"],
        )
        return json.dumps({"Arn": arn, "Tags": tags})

    # ======== Test Identity Provider ========

    def test_identity_provider(self) -> str:
        params = json.loads(self.body)
        result = self.transfer_backend.test_identity_provider(
            server_id=params["ServerId"],
            server_protocol=params.get("ServerProtocol"),
            source_ip=params.get("SourceIp"),
            user_name=params["UserName"],
            user_password=params.get("UserPassword"),
        )
        return json.dumps(result)

    # ======== Connector file operations ========

    def start_file_transfer(self) -> str:
        params = json.loads(self.body)
        transfer_id = self.transfer_backend.start_file_transfer(
            connector_id=params["ConnectorId"],
            send_file_paths=params.get("SendFilePaths"),
            retrieve_file_paths=params.get("RetrieveFilePaths"),
            local_directory_path=params.get("LocalDirectoryPath"),
            remote_directory_path=params.get("RemoteDirectoryPath"),
        )
        return json.dumps({"TransferId": transfer_id})

    def start_directory_listing(self) -> str:
        params = json.loads(self.body)
        listing_id, output_file_name = self.transfer_backend.start_directory_listing(
            connector_id=params["ConnectorId"],
            remote_directory_path=params["RemoteDirectoryPath"],
            max_items=params.get("MaxItems"),
            output_directory_path=params["OutputDirectoryPath"],
        )
        return json.dumps({
            "ListingId": listing_id,
            "OutputFileName": output_file_name,
        })

    def start_remote_delete(self) -> str:
        params = json.loads(self.body)
        delete_id = self.transfer_backend.start_remote_delete(
            connector_id=params["ConnectorId"],
            delete_path=params["DeletePath"],
        )
        return json.dumps({"DeleteId": delete_id})

    def start_remote_move(self) -> str:
        params = json.loads(self.body)
        move_id = self.transfer_backend.start_remote_move(
            connector_id=params["ConnectorId"],
            source_path=params["SourcePath"],
            target_path=params["TargetPath"],
        )
        return json.dumps({"MoveId": move_id})

    def list_file_transfer_results(self) -> str:
        params = json.loads(self.body)
        results = self.transfer_backend.list_file_transfer_results(
            connector_id=params["ConnectorId"],
            transfer_id=params["TransferId"],
        )
        return json.dumps({"FileTransferResults": results})
