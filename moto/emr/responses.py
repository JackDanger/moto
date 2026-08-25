import re
from re import Pattern
from typing import Any

from moto.core.parse import XFormedDict
from moto.core.responses import ActionResult, BaseResponse, EmptyResult, PaginatedResult

from .exceptions import ValidationException
from .models import ElasticMapReduceBackend, emr_backends
from .utils import ReleaseLabel


class ElasticMapReduceResponse(BaseResponse):
    # EMR end points are inconsistent in the placement of region name
    # in the URL, so parsing it out needs to be handled differently
    emr_region_regex: list[Pattern[str]] = [
        re.compile(r"elasticmapreduce\.(.+?)\.amazonaws\.com"),
        re.compile(r"(.+?)\.elasticmapreduce\.amazonaws\.com"),
    ]
    PROTOCOL_PARSER_MAP_TYPE = XFormedDict
    RESPONSE_KEY_PATH_TO_TRANSFORMER = {
        "Properties": lambda x: x.original_dict() if hasattr(x, "original_dict") else x,
    }

    def __init__(self) -> None:
        super().__init__(service_name="emr")
        self.automated_parameter_parsing = True

    def get_region_from_url(self, request: Any, full_url: str) -> str:
        for regex in ElasticMapReduceResponse.emr_region_regex:
            match = regex.search(self.parsed_url.netloc)
            if match:
                return match.group(1)
        return self.default_region

    @property
    def backend(self) -> ElasticMapReduceBackend:
        return emr_backends[self.current_account][self.region]

    def add_instance_groups(self) -> ActionResult:
        jobflow_id = self._get_param("JobFlowId")
        instance_groups = self._get_param("InstanceGroups", [])
        fake_groups = self.backend.add_instance_groups(jobflow_id, instance_groups)
        result = {"InstanceGroups": fake_groups}
        return ActionResult(result)

    def add_job_flow_steps(self) -> ActionResult:
        job_flow_id = self._get_param("JobFlowId")
        steps = self.backend.add_job_flow_steps(
            job_flow_id, self._get_param("Steps", [])
        )
        result = {"StepIds": [step.id for step in steps]}
        return ActionResult(result)

    def add_tags(self) -> ActionResult:
        cluster_id = self._get_param("ResourceId")
        tags = self._get_param("Tags", [])
        tags = {d["Key"]: d["Value"] for d in tags}
        self.backend.add_tags(cluster_id, tags)
        return EmptyResult()

    def create_security_configuration(self) -> ActionResult:
        name = self._get_param("Name")
        security_configuration = self._get_param("SecurityConfiguration")
        security_configuration = self.backend.create_security_configuration(
            name=name, security_configuration=security_configuration
        )
        return ActionResult(security_configuration)

    def describe_security_configuration(self) -> ActionResult:
        name = self._get_param("Name")
        security_configuration = self.backend.get_security_configuration(name=name)
        return ActionResult(security_configuration)

    def delete_security_configuration(self) -> ActionResult:
        name = self._get_param("Name")
        self.backend.delete_security_configuration(name=name)
        return EmptyResult()

    def describe_cluster(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        cluster = self.backend.describe_cluster(cluster_id)
        result = {"Cluster": cluster}
        return ActionResult(result)

    def describe_job_flows(self) -> ActionResult:
        created_after = self._get_param("CreatedAfter")
        created_before = self._get_param("CreatedBefore")
        job_flow_ids = self._get_param("JobFlowIds", [])
        job_flow_states = self._get_param("JobFlowStates", [])
        clusters = self.backend.describe_job_flows(
            job_flow_ids, job_flow_states, created_after, created_before
        )
        result = {"JobFlows": clusters}
        return ActionResult(result)

    def describe_step(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        step_id = self._get_param("StepId")
        step = self.backend.describe_step(cluster_id, step_id)
        result = {"Step": step}
        return ActionResult(result)

    def list_bootstrap_actions(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        bootstrap_actions = self.backend.list_bootstrap_actions(cluster_id)
        result = {"BootstrapActions": bootstrap_actions}
        return PaginatedResult(result)

    def list_clusters(self) -> ActionResult:
        cluster_states = self._get_param("ClusterStates", [])
        created_after = self._get_param("CreatedAfter")
        created_before = self._get_param("CreatedBefore")
        clusters = self.backend.list_clusters(
            cluster_states, created_after, created_before
        )
        result = {"Clusters": clusters}
        return PaginatedResult(result)

    def list_instance_groups(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        instance_groups = self.backend.list_instance_groups(cluster_id)
        result = {"InstanceGroups": instance_groups}
        return PaginatedResult(result)

    def list_instances(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        instance_group_id = self._get_param("InstanceGroupId")
        instance_group_types = self._get_param("InstanceGroupTypes")
        instances = self.backend.list_instances(
            cluster_id,
            instance_group_id=instance_group_id,
            instance_group_types=instance_group_types,
        )
        result = {"Instances": instances}
        return PaginatedResult(result)

    def list_steps(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        step_ids = self._get_param("StepIds", [])
        step_states = self._get_param("StepStates", [])
        steps = self.backend.list_steps(
            cluster_id, step_ids=step_ids, step_states=step_states
        )
        result = {"Steps": steps}
        return PaginatedResult(result)

    def modify_cluster(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        step_concurrency_level = self._get_param("StepConcurrencyLevel")
        cluster = self.backend.modify_cluster(cluster_id, step_concurrency_level)
        result = {"StepConcurrencyLevel": cluster.step_concurrency_level}
        return ActionResult(result)

    def modify_instance_groups(self) -> ActionResult:
        instance_groups = self._get_param("InstanceGroups", [])
        self.backend.modify_instance_groups(instance_groups)
        return EmptyResult()

    def remove_tags(self) -> ActionResult:
        cluster_id = self._get_param("ResourceId")
        tag_keys = self._get_param("TagKeys", [])
        self.backend.remove_tags(cluster_id, tag_keys)
        return EmptyResult()

    def run_job_flow(self) -> ActionResult:
        instance_attrs = {
            "master_instance_type": self._get_param("Instances.MasterInstanceType"),
            "slave_instance_type": self._get_param("Instances.SlaveInstanceType"),
            "instance_count": self._get_int_param("Instances.InstanceCount", 1),
            "ec2_key_name": self._get_param("Instances.Ec2KeyName"),
            "ec2_subnet_id": self._get_param("Instances.Ec2SubnetId"),
            "hadoop_version": self._get_param("Instances.HadoopVersion"),
            "availability_zone": self._get_param(
                "Instances.Placement.AvailabilityZone", self.backend.region_name + "a"
            ),
            "keep_job_flow_alive_when_no_steps": self._get_bool_param(
                "Instances.KeepJobFlowAliveWhenNoSteps", False
            ),
            "termination_protected": self._get_bool_param(
                "Instances.TerminationProtected", False
            ),
            "emr_managed_master_security_group": self._get_param(
                "Instances.EmrManagedMasterSecurityGroup"
            ),
            "emr_managed_slave_security_group": self._get_param(
                "Instances.EmrManagedSlaveSecurityGroup"
            ),
            "service_access_security_group": self._get_param(
                "Instances.ServiceAccessSecurityGroup"
            ),
            "additional_master_security_groups": self._get_param(
                "Instances.AdditionalMasterSecurityGroups", []
            ),
            "additional_slave_security_groups": self._get_param(
                "Instances.AdditionalSlaveSecurityGroups", []
            ),
        }

        kwargs = {
            "name": self._get_param("Name"),
            "log_uri": self._get_param("LogUri"),
            "job_flow_role": self._get_param("JobFlowRole"),
            "service_role": self._get_param("ServiceRole"),
            "auto_scaling_role": self._get_param("AutoScalingRole"),
            "steps": self._get_param("Steps", []),
            "ebs_root_volume_iops": self._get_param("EbsRootVolumeIops"),
            "ebs_root_volume_size": self._get_param("EbsRootVolumeSize"),
            "ebs_root_volume_throughput": self._get_param("EbsRootVolumeThroughput"),
            "visible_to_all_users": self._get_bool_param("VisibleToAllUsers", False),
            "instance_attrs": instance_attrs,
        }

        bootstrap_actions = self._get_param("BootstrapActions", [])
        if bootstrap_actions:
            kwargs["bootstrap_actions"] = bootstrap_actions

        configurations = self._get_param("Configurations", [])
        if configurations:
            kwargs["configurations"] = configurations

        release_label = self._get_param("ReleaseLabel")
        ami_version = self._get_param("AmiVersion")
        if release_label:
            kwargs["release_label"] = release_label
            if ami_version:
                message = (
                    "Only one AMI version and release label may be specified. "
                    f"Provided AMI: {ami_version}, release label: {release_label}."
                )
                raise ValidationException(message)
        else:
            if ami_version:
                kwargs["requested_ami_version"] = ami_version
                kwargs["running_ami_version"] = ami_version
            else:
                kwargs["running_ami_version"] = "1.0.0"

        custom_ami_id = self._get_param("CustomAmiId")
        if custom_ami_id:
            kwargs["custom_ami_id"] = custom_ami_id
            if release_label and (
                ReleaseLabel(release_label) < ReleaseLabel("emr-5.7.0")
            ):
                message = "Custom AMI is not allowed"
                raise ValidationException(message)
            elif ami_version:
                message = "Custom AMI is not supported in this version of EMR"
                raise ValidationException(message)

        step_concurrency_level = self._get_param("StepConcurrencyLevel")
        if step_concurrency_level:
            kwargs["step_concurrency_level"] = step_concurrency_level

        security_configuration = self._get_param("SecurityConfiguration")
        if security_configuration:
            kwargs["security_configuration"] = security_configuration

        kerberos_attributes = self._get_param("KerberosAttributes", {})
        kwargs["kerberos_attributes"] = kerberos_attributes

        cluster = self.backend.run_job_flow(**kwargs)

        applications = self._get_param("Applications", [])
        if applications:
            self.backend.add_applications(cluster.id, applications)
        else:
            self.backend.add_applications(
                cluster.id, [{"Name": "Hadoop", "Version": "0.18"}]
            )

        instance_groups = self._get_param("Instances.InstanceGroups", [])
        if instance_groups:
            instance_group_result = self.backend.add_instance_groups(
                cluster.id, instance_groups
            )
            for i in range(0, len(instance_group_result)):
                self.backend.run_instances(
                    cluster.id, instance_groups[i], instance_group_result[i]
                )

        # TODO: Instances also must be created when `Instances.InstanceType` and `Instances.InstanceCount` are specified in the request.

        tags = self._get_param("Tags", [])
        if tags:
            self.backend.add_tags(cluster.id, {d["key"]: d["value"] for d in tags})
        result = {
            "JobFlowId": cluster.job_flow_id,
            "ClusterArn": cluster.arn,
        }
        return ActionResult(result)

    def set_termination_protection(self) -> ActionResult:
        termination_protection = self._get_bool_param("TerminationProtected")
        job_ids = self._get_param("JobFlowIds", [])
        self.backend.set_termination_protection(job_ids, termination_protection)
        return EmptyResult()

    def set_visible_to_all_users(self) -> ActionResult:
        visible_to_all_users = self._get_bool_param("VisibleToAllUsers", False)
        job_ids = self._get_param("JobFlowIds", [])
        self.backend.set_visible_to_all_users(job_ids, visible_to_all_users)
        return EmptyResult()

    def terminate_job_flows(self) -> ActionResult:
        job_ids = self._get_param("JobFlowIds")
        self.backend.terminate_job_flows(job_ids)
        return EmptyResult()

    def put_auto_scaling_policy(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        cluster = self.backend.describe_cluster(cluster_id)
        instance_group_id = self._get_param("InstanceGroupId")
        auto_scaling_policy = self._get_param("AutoScalingPolicy")
        instance_group = self.backend.put_auto_scaling_policy(
            instance_group_id, auto_scaling_policy
        )
        assert instance_group is not None
        result = {
            "ClusterId": cluster.id,
            "InstanceGroupId": instance_group.id,
            "AutoScalingPolicy": instance_group.auto_scaling_policy,
            "ClusterArn": cluster.arn,
        }
        return ActionResult(result)

    def remove_auto_scaling_policy(self) -> ActionResult:
        instance_group_id = self._get_param("InstanceGroupId")
        self.backend.remove_auto_scaling_policy(instance_group_id)
        return EmptyResult()

    def get_block_public_access_configuration(self) -> ActionResult:
        configuration = self.backend.get_block_public_access_configuration()
        config = configuration.get("block_public_access_configuration") or {}
        metadata = configuration.get("block_public_access_configuration_metadata") or {}
        result = {
            "BlockPublicAccessConfiguration": config,
            "BlockPublicAccessConfigurationMetadata": metadata,
        }
        return ActionResult(result)

    def put_block_public_access_configuration(self) -> ActionResult:
        params = self._get_params()
        block_public_access_configuration = (
            params.get("BlockPublicAccessConfiguration") or {}
        )
        self.backend.put_block_public_access_configuration(
            block_public_security_group_rules=block_public_access_configuration.get(
                "BlockPublicSecurityGroupRules"
            )
            or True,
            rule_ranges=block_public_access_configuration.get(
                "PermittedPublicSecurityGroupRuleRanges"
            ),
        )
        return EmptyResult()

    def list_release_labels(self) -> ActionResult:
        release_labels = self.backend.list_release_labels()
        return ActionResult({"ReleaseLabels": release_labels})

    def list_supported_instance_types(self) -> ActionResult:
        release_label = self._get_param("ReleaseLabel")
        instance_types = self.backend.list_supported_instance_types(release_label)
        return ActionResult({"SupportedInstanceTypes": instance_types})

    def list_security_configurations(self) -> ActionResult:
        configs = self.backend.list_security_configurations()
        result = {
            "SecurityConfigurations": [
                {
                    "Name": c.name,
                    "CreationDateTime": c.creation_date_time,
                }
                for c in configs
            ]
        }
        return PaginatedResult(result)

    def cancel_steps(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        step_ids = self._get_param("StepIds", [])
        results = self.backend.cancel_steps(cluster_id, step_ids)
        return ActionResult({"CancelStepsInfoList": results})

    def create_studio(self) -> ActionResult:
        name = self._get_param("Name")
        auth_mode = self._get_param("AuthMode")
        vpc_id = self._get_param("VpcId")
        subnet_ids = self._get_param("SubnetIds", [])
        service_role = self._get_param("ServiceRole")
        ws_sg = self._get_param("WorkspaceSecurityGroupId")
        engine_sg = self._get_param("EngineSecurityGroupId")
        default_s3 = self._get_param("DefaultS3Location", "")
        description = self._get_param("Description", "")
        user_role = self._get_param("UserRole", "")
        tags = self._get_param("Tags", [])
        tag_dict = {d["Key"]: d["Value"] for d in tags} if tags else {}
        studio = self.backend.create_studio(
            name=name,
            auth_mode=auth_mode,
            vpc_id=vpc_id,
            subnet_ids=subnet_ids,
            service_role=service_role,
            workspace_security_group_id=ws_sg,
            engine_security_group_id=engine_sg,
            default_s3_location=default_s3,
            description=description,
            user_role=user_role,
            tags=tag_dict,
        )
        return ActionResult({"StudioId": studio.studio_id, "Url": studio.url})

    def describe_studio(self) -> ActionResult:
        studio_id = self._get_param("StudioId")
        studio = self.backend.describe_studio(studio_id)
        result = {
            "Studio": {
                "StudioId": studio.studio_id,
                "StudioArn": studio.arn,
                "Name": studio.name,
                "Description": studio.description,
                "AuthMode": studio.auth_mode,
                "VpcId": studio.vpc_id,
                "SubnetIds": studio.subnet_ids,
                "ServiceRole": studio.service_role,
                "UserRole": studio.user_role,
                "WorkspaceSecurityGroupId": (studio.workspace_security_group_id),
                "EngineSecurityGroupId": (studio.engine_security_group_id),
                "Url": studio.url,
                "DefaultS3Location": studio.default_s3_location,
                "CreationTime": studio.creation_time,
                "Tags": studio.tags,
            }
        }
        return ActionResult(result)

    def delete_studio(self) -> ActionResult:
        studio_id = self._get_param("StudioId")
        self.backend.delete_studio(studio_id)
        return EmptyResult()

    def update_studio(self) -> ActionResult:
        studio_id = self._get_param("StudioId")
        name = self._get_param("Name")
        description = self._get_param("Description")
        subnet_ids = self._get_param("SubnetIds")
        default_s3_location = self._get_param("DefaultS3Location")
        encryption_key_arn = self._get_param("EncryptionKeyArn")
        self.backend.update_studio(
            studio_id=studio_id,
            name=name,
            description=description,
            subnet_ids=subnet_ids,
            default_s3_location=default_s3_location,
            encryption_key_arn=encryption_key_arn,
        )
        return EmptyResult()

    def list_studios(self) -> ActionResult:
        studios = self.backend.list_studios()
        result = {
            "Studios": [
                {
                    "StudioId": s.studio_id,
                    "Name": s.name,
                    "Description": s.description,
                    "AuthMode": s.auth_mode,
                    "Url": s.url,
                    "CreationTime": s.creation_time,
                }
                for s in studios
            ]
        }
        return PaginatedResult(result)

    def put_managed_scaling_policy(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        policy = self._get_param("ManagedScalingPolicy")
        self.backend.put_managed_scaling_policy(cluster_id, policy)
        return EmptyResult()

    def get_managed_scaling_policy(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        policy = self.backend.get_managed_scaling_policy(cluster_id)
        result = {}
        if policy:
            result["ManagedScalingPolicy"] = policy
        return ActionResult(result)

    def remove_managed_scaling_policy(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        self.backend.remove_managed_scaling_policy(cluster_id)
        return EmptyResult()

    def put_auto_termination_policy(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        policy = self._get_param("AutoTerminationPolicy")
        self.backend.put_auto_termination_policy(cluster_id, policy)
        return EmptyResult()

    def get_auto_termination_policy(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        policy = self.backend.get_auto_termination_policy(cluster_id)
        result = {}
        if policy:
            result["AutoTerminationPolicy"] = policy
        return ActionResult(result)

    def remove_auto_termination_policy(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        self.backend.remove_auto_termination_policy(cluster_id)
        return EmptyResult()

    def add_instance_fleet(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        instance_fleet = self._get_param("InstanceFleet", {})
        fleet = self.backend.add_instance_fleet(cluster_id, instance_fleet)
        result = {
            "ClusterId": cluster_id,
            "InstanceFleetId": fleet.id,
            "ClusterArn": self.backend.describe_cluster(cluster_id).arn,
        }
        return ActionResult(result)

    def modify_instance_fleet(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        instance_fleet = self._get_param("InstanceFleet", {})
        self.backend.modify_instance_fleet(cluster_id, instance_fleet)
        return EmptyResult()

    def list_instance_fleets(self) -> ActionResult:
        cluster_id = self._get_param("ClusterId")
        fleets = self.backend.list_instance_fleets(cluster_id)
        result = {
            "InstanceFleets": [
                {
                    "Id": f.id,
                    "Name": f.name,
                    "Status": f.status,
                    "InstanceFleetType": f.instance_fleet_type,
                    "TargetOnDemandCapacity": f.target_on_demand_capacity,
                    "TargetSpotCapacity": f.target_spot_capacity,
                    "ProvisionedOnDemandCapacity": f.provisioned_on_demand_capacity,
                    "ProvisionedSpotCapacity": f.provisioned_spot_capacity,
                    "InstanceTypeSpecifications": f.instance_type_configs,
                    "LaunchSpecifications": f.launch_specifications,
                }
                for f in fleets
            ]
        }
        return PaginatedResult(result)

    def create_studio_session_mapping(self) -> ActionResult:
        studio_id = self._get_param("StudioId")
        identity_id = self._get_param("IdentityId", "")
        identity_name = self._get_param("IdentityName", "")
        identity_type = self._get_param("IdentityType")
        session_policy_arn = self._get_param("SessionPolicyArn")
        self.backend.create_studio_session_mapping(
            studio_id=studio_id,
            identity_id=identity_id,
            identity_name=identity_name,
            identity_type=identity_type,
            session_policy_arn=session_policy_arn,
        )
        return EmptyResult()

    def get_studio_session_mapping(self) -> ActionResult:
        studio_id = self._get_param("StudioId")
        identity_id = self._get_param("IdentityId")
        identity_type = self._get_param("IdentityType")
        mapping = self.backend.get_studio_session_mapping(
            studio_id=studio_id,
            identity_id=identity_id,
            identity_type=identity_type,
        )
        result = {
            "SessionMapping": {
                "StudioId": mapping.studio_id,
                "IdentityId": mapping.identity_id,
                "IdentityName": mapping.identity_name,
                "IdentityType": mapping.identity_type,
                "SessionPolicyArn": mapping.session_policy_arn,
                "CreationTime": mapping.creation_time,
                "LastModifiedTime": mapping.last_modified_time,
            }
        }
        return ActionResult(result)

    def update_studio_session_mapping(self) -> ActionResult:
        studio_id = self._get_param("StudioId")
        identity_id = self._get_param("IdentityId")
        identity_type = self._get_param("IdentityType")
        session_policy_arn = self._get_param("SessionPolicyArn")
        self.backend.update_studio_session_mapping(
            studio_id=studio_id,
            identity_id=identity_id,
            identity_type=identity_type,
            session_policy_arn=session_policy_arn,
        )
        return EmptyResult()

    def delete_studio_session_mapping(self) -> ActionResult:
        studio_id = self._get_param("StudioId")
        identity_id = self._get_param("IdentityId")
        identity_type = self._get_param("IdentityType")
        self.backend.delete_studio_session_mapping(
            studio_id=studio_id,
            identity_id=identity_id,
            identity_type=identity_type,
        )
        return EmptyResult()

    def create_notebook_execution(self) -> ActionResult:
        editor_id = self._get_param("EditorId")
        relative_path = self._get_param("RelativePath")
        execution_engine = self._get_param("ExecutionEngine")
        service_role = self._get_param("ServiceRole")
        name = self._get_param("NotebookExecutionName", "")
        params = self._get_param("NotebookParams", "")
        tags = self._get_param("Tags", [])
        tag_dict = {d["Key"]: d["Value"] for d in tags} if tags else {}
        execution = self.backend.create_notebook_execution(
            editor_id=editor_id,
            relative_path=relative_path,
            execution_engine=execution_engine,
            service_role=service_role,
            notebook_execution_name=name,
            notebook_params=params,
            tags=tag_dict,
        )
        return ActionResult({"NotebookExecutionId": execution.notebook_execution_id})

    def describe_notebook_execution(self) -> ActionResult:
        nid = self._get_param("NotebookExecutionId")
        ex = self.backend.describe_notebook_execution(nid)
        result = {
            "NotebookExecution": {
                "NotebookExecutionId": ex.notebook_execution_id,
                "NotebookExecutionName": ex.notebook_execution_name,
                "EditorId": ex.editor_id,
                "ExecutionEngine": ex.execution_engine,
                "ServiceRole": ex.service_role,
                "NotebookParams": ex.notebook_params,
                "Status": ex.status,
                "StartTime": ex.start_time,
                "EndTime": ex.end_time,
                "Tags": ex.tags,
            }
        }
        return ActionResult(result)

    def list_notebook_executions(self) -> ActionResult:
        status = self._get_param("Status")
        executions = self.backend.list_notebook_executions(status=status)
        result = {
            "NotebookExecutions": [
                {
                    "NotebookExecutionId": e.notebook_execution_id,
                    "NotebookExecutionName": (e.notebook_execution_name),
                    "EditorId": e.editor_id,
                    "Status": e.status,
                    "StartTime": e.start_time,
                    "EndTime": e.end_time,
                }
                for e in executions
            ]
        }
        return PaginatedResult(result)

    def stop_notebook_execution(self) -> ActionResult:
        nid = self._get_param("NotebookExecutionId")
        self.backend.stop_notebook_execution(nid)
        return EmptyResult()

    def describe_release_label(self) -> ActionResult:
        release_label = self._get_param("ReleaseLabel")
        result = self.backend.describe_release_label(release_label)
        return ActionResult(result)

    def create_persistent_app_ui(self) -> ActionResult:
        target_resource_arn = self._get_param("TargetResourceArn")
        app_ui = self.backend.create_persistent_app_ui(
            target_resource_arn=target_resource_arn
        )
        result = {
            "PersistentAppUIId": app_ui.persistent_app_ui_id,
            "PersistentAppUI": {
                "PersistentAppUIId": app_ui.persistent_app_ui_id,
                "PersistentAppUIStatus": "ACTIVE",
                "TargetResourceArn": app_ui.target_resource_arn,
                "CreationTime": app_ui.creation_time,
                "LastModifiedTime": app_ui.last_modified_time,
                "PersistentAppUIArn": app_ui.persistent_app_ui_arn,
            },
        }
        return ActionResult(result)

    def describe_persistent_app_ui(self) -> ActionResult:
        persistent_app_ui_id = self._get_param("PersistentAppUIId")
        app_ui = self.backend.describe_persistent_app_ui(
            persistent_app_ui_id=persistent_app_ui_id
        )
        result = {
            "PersistentAppUI": {
                "PersistentAppUIId": app_ui.persistent_app_ui_id,
                "PersistentAppUIStatus": "ACTIVE",
                "TargetResourceArn": app_ui.target_resource_arn,
                "CreationTime": app_ui.creation_time,
                "LastModifiedTime": app_ui.last_modified_time,
                "PersistentAppUIArn": app_ui.persistent_app_ui_arn,
            }
        }
        return ActionResult(result)

    def list_studio_session_mappings(self) -> "ActionResult":
        studio_id = self._get_param("StudioId")
        identity_type = self._get_param("IdentityType")
        mappings = self.backend.list_studio_session_mappings(
            studio_id=studio_id, identity_type=identity_type
        )
        return ActionResult({"SessionMappings": mappings})

    def set_keep_job_flow_alive_when_no_steps(self) -> "ActionResult":
        job_flow_ids = self._get_param("JobFlowIds", [])
        keep_alive = self._get_param("KeepJobFlowAliveWhenNoSteps", True)
        self.backend.set_keep_job_flow_alive_when_no_steps(job_flow_ids, keep_alive)
        return EmptyResult()

    def set_unhealthy_node_replacement(self) -> "ActionResult":
        job_flow_ids = self._get_param("JobFlowIds", [])
        unhealthy = self._get_param("UnhealthyNodeReplacement", True)
        self.backend.set_unhealthy_node_replacement(job_flow_ids, unhealthy)
        return EmptyResult()

    def get_cluster_session_credentials(self) -> "ActionResult":
        cluster_id = self._get_param("ClusterId")
        execution_role_arn = self._get_param("ExecutionRoleArn")
        result = self.backend.get_cluster_session_credentials(cluster_id, execution_role_arn)
        return ActionResult(result)

    def start_notebook_execution(self) -> "ActionResult":
        editor_id = self._get_param("EditorId")
        relative_path = self._get_param("RelativePath")
        execution_engine = self._get_param("ExecutionEngine")
        service_role = self._get_param("ServiceRole")
        execution = self.backend.start_notebook_execution(
            editor_id=editor_id,
            relative_path=relative_path,
            execution_engine=execution_engine,
            service_role=service_role,
            notebook_execution_name=self._get_param("NotebookExecutionName", ""),
            notebook_params=self._get_param("NotebookParams", ""),
            tags=self._get_param("Tags"),
        )
        return ActionResult({"NotebookExecutionId": execution.notebook_execution_id})

    def get_persistent_app_ui_presigned_url(self) -> "ActionResult":
        persistent_app_ui_id = self._get_param("PersistentAppUIId")
        presentation_type = self._get_param("PresentationType", "ATHENA")
        result = self.backend.get_persistent_app_ui_presigned_url(persistent_app_ui_id, presentation_type)
        return ActionResult(result)

    def get_on_cluster_app_ui_presigned_url(self) -> "ActionResult":
        cluster_id = self._get_param("ClusterId")
        app_ui_type = self._get_param("OnClusterAppUIType", "SPARK_HISTORY_SERVER")
        result = self.backend.get_on_cluster_app_ui_presigned_url(cluster_id, app_ui_type)
        return ActionResult(result)
