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

    # ======== User operations =
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

    # ======== Profile operations =
