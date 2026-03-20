import json

from moto.core.responses import BaseResponse

from .models import DataSyncBackend, Location, datasync_backends


class DataSyncResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="datasync")

    @property
    def datasync_backend(self) -> DataSyncBackend:
        return datasync_backends[self.current_account][self.region]

    # --- Agent operations ---

    def create_agent(self) -> str:
        activation_key = self._get_param("ActivationKey")
        agent_name = self._get_param("AgentName")
        tags = self._get_param("Tags")
        arn = self.datasync_backend.create_agent(
            activation_key=activation_key, agent_name=agent_name, tags=tags
        )
        return json.dumps({"AgentArn": arn})

    def describe_agent(self) -> str:
        agent_arn = self._get_param("AgentArn")
        agent = self.datasync_backend.describe_agent(agent_arn)
        return json.dumps(
            {
                "AgentArn": agent.arn,
                "Name": agent.agent_name,
                "Status": agent.status,
            }
        )

    def list_agents(self) -> str:
        agents = []
        for arn, agent in self.datasync_backend.agents.items():
            agents.append(
                {"AgentArn": arn, "Name": agent.agent_name, "Status": agent.status}
            )
        return json.dumps({"Agents": agents})

    def update_agent(self) -> str:
        agent_arn = self._get_param("AgentArn")
        name = self._get_param("Name")
        self.datasync_backend.update_agent(agent_arn, name=name)
        return json.dumps({})

    def delete_agent(self) -> str:
        agent_arn = self._get_param("AgentArn")
        self.datasync_backend.delete_agent(agent_arn)
        return json.dumps({})

    # --- Location operations ---

    def list_locations(self) -> str:
        locations = []
        for arn, location in self.datasync_backend.locations.items():
            locations.append({"LocationArn": arn, "LocationUri": location.uri})
        return json.dumps({"Locations": locations})

    def _get_location(self, location_arn: str, typ: str) -> Location:
        return self.datasync_backend._get_location(location_arn, typ)

    def create_location_s3(self) -> str:
        # s3://bucket_name/folder/
        s3_bucket_arn = self._get_param("S3BucketArn")
        subdirectory = self._get_param("Subdirectory")
        metadata = {"S3Config": self._get_param("S3Config")}
        location_uri_elts = ["s3:/", s3_bucket_arn.split(":")[-1]]
        if subdirectory:
            location_uri_elts.append(subdirectory)
        location_uri = "/".join(location_uri_elts)
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="S3"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_s3(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="S3")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "S3Config": location.metadata["S3Config"],
            }
        )

    def create_location_smb(self) -> str:
        # smb://smb.share.fqdn/AWS_Test/
        subdirectory = self._get_param("Subdirectory")
        server_hostname = self._get_param("ServerHostname")
        metadata = {
            "AgentArns": self._get_param("AgentArns"),
            "User": self._get_param("User"),
            "Domain": self._get_param("Domain"),
            "MountOptions": self._get_param("MountOptions"),
        }

        location_uri = "/".join(["smb:/", server_hostname, subdirectory])
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="SMB"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_smb(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="SMB")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "AgentArns": location.metadata["AgentArns"],
                "User": location.metadata["User"],
                "Domain": location.metadata["Domain"],
                "MountOptions": location.metadata["MountOptions"],
            }
        )

    # --- EFS ---

    def create_location_efs(self) -> str:
        efs_filesystem_arn = self._get_param("EfsFilesystemArn")
        subdirectory = self._get_param("Subdirectory", "/")
        ec2_config = self._get_param("Ec2Config")
        metadata = {"EfsFilesystemArn": efs_filesystem_arn, "Ec2Config": ec2_config}
        location_uri = f"efs://{efs_filesystem_arn.split(':')[-1]}{subdirectory}"
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="EFS"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_efs(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="EFS")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "Ec2Config": location.metadata.get("Ec2Config"),
            }
        )

    # --- NFS ---

    def create_location_nfs(self) -> str:
        server_hostname = self._get_param("ServerHostname")
        subdirectory = self._get_param("Subdirectory")
        on_prem_config = self._get_param("OnPremConfig")
        mount_options = self._get_param("MountOptions")
        metadata = {"OnPremConfig": on_prem_config, "MountOptions": mount_options}
        location_uri = f"nfs://{server_hostname}{subdirectory}"
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="NFS"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_nfs(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="NFS")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "OnPremConfig": location.metadata.get("OnPremConfig"),
                "MountOptions": location.metadata.get("MountOptions"),
            }
        )

    # --- HDFS ---

    def create_location_hdfs(self) -> str:
        subdirectory = self._get_param("Subdirectory", "/")
        name_nodes = self._get_param("NameNodes")
        authentication_type = self._get_param("AuthenticationType", "SIMPLE")
        agent_arns = self._get_param("AgentArns")
        metadata = {
            "NameNodes": name_nodes,
            "AuthenticationType": authentication_type,
            "AgentArns": agent_arns,
        }
        hostname = name_nodes[0]["Hostname"] if name_nodes else "localhost"
        location_uri = f"hdfs://{hostname}{subdirectory}"
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="HDFS"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_hdfs(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="HDFS")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "NameNodes": location.metadata.get("NameNodes"),
                "AuthenticationType": location.metadata.get("AuthenticationType"),
                "AgentArns": location.metadata.get("AgentArns"),
            }
        )

    # --- ObjectStorage ---

    def create_location_object_storage(self) -> str:
        server_hostname = self._get_param("ServerHostname")
        server_port = self._get_param("ServerPort", 443)
        server_protocol = self._get_param("ServerProtocol", "HTTPS")
        subdirectory = self._get_param("Subdirectory", "/")
        bucket_name = self._get_param("BucketName")
        agent_arns = self._get_param("AgentArns")
        metadata = {
            "ServerHostname": server_hostname,
            "ServerPort": server_port,
            "ServerProtocol": server_protocol,
            "BucketName": bucket_name,
            "AgentArns": agent_arns,
        }
        location_uri = f"object-storage://{server_hostname}/{bucket_name}{subdirectory}"
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="ObjectStorage"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_object_storage(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="ObjectStorage")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "ServerHostname": location.metadata.get("ServerHostname"),
                "ServerPort": location.metadata.get("ServerPort"),
                "ServerProtocol": location.metadata.get("ServerProtocol"),
                "BucketName": location.metadata.get("BucketName"),
                "AgentArns": location.metadata.get("AgentArns"),
            }
        )

    # --- AzureBlob ---

    def create_location_azure_blob(self) -> str:
        container_url = self._get_param("ContainerUrl")
        authentication_type = self._get_param("AuthenticationType", "SAS")
        agent_arns = self._get_param("AgentArns")
        subdirectory = self._get_param("Subdirectory", "/")
        metadata = {
            "ContainerUrl": container_url,
            "AuthenticationType": authentication_type,
            "AgentArns": agent_arns,
        }
        location_uri = f"{container_url}{subdirectory}"
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="AzureBlob"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_azure_blob(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="AzureBlob")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "ContainerUrl": location.metadata.get("ContainerUrl"),
                "AuthenticationType": location.metadata.get("AuthenticationType"),
                "AgentArns": location.metadata.get("AgentArns"),
            }
        )

    # --- FSx Lustre ---

    def create_location_fsx_lustre(self) -> str:
        fsx_filesystem_arn = self._get_param("FsxFilesystemArn")
        security_group_arns = self._get_param("SecurityGroupArns")
        subdirectory = self._get_param("Subdirectory", "/")
        metadata = {
            "FsxFilesystemArn": fsx_filesystem_arn,
            "SecurityGroupArns": security_group_arns,
        }
        location_uri = f"fsxl://{fsx_filesystem_arn.split(':')[-1]}{subdirectory}"
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="FsxLustre"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_fsx_lustre(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="FsxLustre")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "SecurityGroupArns": location.metadata.get("SecurityGroupArns"),
            }
        )

    # --- FSx ONTAP ---

    def create_location_fsx_ontap(self) -> str:
        storage_virtual_machine_arn = self._get_param("StorageVirtualMachineArn")
        protocol = self._get_param("Protocol")
        security_group_arns = self._get_param("SecurityGroupArns")
        subdirectory = self._get_param("Subdirectory", "/")
        metadata = {
            "StorageVirtualMachineArn": storage_virtual_machine_arn,
            "Protocol": protocol,
            "SecurityGroupArns": security_group_arns,
        }
        location_uri = (
            f"fsxo://{storage_virtual_machine_arn.split(':')[-1]}{subdirectory}"
        )
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="FsxOntap"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_fsx_ontap(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="FsxOntap")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "StorageVirtualMachineArn": location.metadata.get(
                    "StorageVirtualMachineArn"
                ),
                "Protocol": location.metadata.get("Protocol"),
                "SecurityGroupArns": location.metadata.get("SecurityGroupArns"),
            }
        )

    # --- FSx OpenZFS ---

    def create_location_fsx_open_zfs(self) -> str:
        fsx_filesystem_arn = self._get_param("FsxFilesystemArn")
        protocol = self._get_param("Protocol")
        security_group_arns = self._get_param("SecurityGroupArns")
        subdirectory = self._get_param("Subdirectory", "/")
        metadata = {
            "FsxFilesystemArn": fsx_filesystem_arn,
            "Protocol": protocol,
            "SecurityGroupArns": security_group_arns,
        }
        location_uri = f"fsxz://{fsx_filesystem_arn.split(':')[-1]}{subdirectory}"
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="FsxOpenZfs"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_fsx_open_zfs(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="FsxOpenZfs")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "Protocol": location.metadata.get("Protocol"),
                "SecurityGroupArns": location.metadata.get("SecurityGroupArns"),
            }
        )

    # --- FSx Windows ---

    def create_location_fsx_windows(self) -> str:
        fsx_filesystem_arn = self._get_param("FsxFilesystemArn")
        security_group_arns = self._get_param("SecurityGroupArns")
        subdirectory = self._get_param("Subdirectory", "/")
        user = self._get_param("User")
        domain = self._get_param("Domain")
        metadata = {
            "FsxFilesystemArn": fsx_filesystem_arn,
            "SecurityGroupArns": security_group_arns,
            "User": user,
            "Domain": domain,
        }
        location_uri = f"fsxw://{fsx_filesystem_arn.split(':')[-1]}{subdirectory}"
        arn = self.datasync_backend.create_location(
            location_uri, metadata=metadata, typ="FsxWindows"
        )
        return json.dumps({"LocationArn": arn})

    def describe_location_fsx_windows(self) -> str:
        location_arn = self._get_param("LocationArn")
        location = self._get_location(location_arn, typ="FsxWindows")
        return json.dumps(
            {
                "LocationArn": location.arn,
                "LocationUri": location.uri,
                "SecurityGroupArns": location.metadata.get("SecurityGroupArns"),
                "User": location.metadata.get("User"),
                "Domain": location.metadata.get("Domain"),
            }
        )

    def delete_location(self) -> str:
        location_arn = self._get_param("LocationArn")
        self.datasync_backend.delete_location(location_arn)
        return json.dumps({})

    def create_task(self) -> str:
        destination_location_arn = self._get_param("DestinationLocationArn")
        source_location_arn = self._get_param("SourceLocationArn")
        name = self._get_param("Name")
        metadata = {
            "CloudWatchLogGroupArn": self._get_param("CloudWatchLogGroupArn"),
            "Options": self._get_param("Options"),
            "Excludes": self._get_param("Excludes"),
            "Tags": self._get_param("Tags"),
        }
        arn = self.datasync_backend.create_task(
            source_location_arn, destination_location_arn, name, metadata=metadata
        )
        return json.dumps({"TaskArn": arn})

    def update_task(self) -> str:
        task_arn = self._get_param("TaskArn")
        self.datasync_backend.update_task(
            task_arn,
            name=self._get_param("Name"),
            metadata={
                "CloudWatchLogGroupArn": self._get_param("CloudWatchLogGroupArn"),
                "Options": self._get_param("Options"),
                "Excludes": self._get_param("Excludes"),
                "Tags": self._get_param("Tags"),
            },
        )
        return json.dumps({})

    def list_tasks(self) -> str:
        tasks = []
        for arn, task in self.datasync_backend.tasks.items():
            tasks.append({"Name": task.name, "Status": task.status, "TaskArn": arn})
        return json.dumps({"Tasks": tasks})

    def delete_task(self) -> str:
        task_arn = self._get_param("TaskArn")
        self.datasync_backend.delete_task(task_arn)
        return json.dumps({})

    def describe_task(self) -> str:
        task_arn = self._get_param("TaskArn")
        task = self.datasync_backend._get_task(task_arn)
        return json.dumps(
            {
                "TaskArn": task.arn,
                "Status": task.status,
                "Name": task.name,
                "CurrentTaskExecutionArn": task.current_task_execution_arn,
                "SourceLocationArn": task.source_location_arn,
                "DestinationLocationArn": task.destination_location_arn,
                "CloudWatchLogGroupArn": task.metadata["CloudWatchLogGroupArn"],
                "Options": task.metadata["Options"],
                "Excludes": task.metadata["Excludes"],
            }
        )

    def start_task_execution(self) -> str:
        task_arn = self._get_param("TaskArn")
        arn = self.datasync_backend.start_task_execution(task_arn)
        return json.dumps({"TaskExecutionArn": arn})

    def cancel_task_execution(self) -> str:
        task_execution_arn = self._get_param("TaskExecutionArn")
        self.datasync_backend.cancel_task_execution(task_execution_arn)
        return json.dumps({})

    def describe_task_execution(self) -> str:
        task_execution_arn = self._get_param("TaskExecutionArn")
        task_execution = self.datasync_backend._get_task_execution(task_execution_arn)
        result = json.dumps(
            {"TaskExecutionArn": task_execution.arn, "Status": task_execution.status}
        )
        if task_execution.status == "SUCCESS":
            self.datasync_backend.tasks[task_execution.task_arn].status = "AVAILABLE"
        # Simulate task being executed
        task_execution.iterate_status()
        return result
