from moto.core.responses import ActionResult, BaseResponse, EmptyResult, PaginatedResult

from .models import MediaLiveBackend, medialive_backends


class MediaLiveResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="medialive")
        self.automated_parameter_parsing = True

    @property
    def medialive_backend(self) -> MediaLiveBackend:
        return medialive_backends[self.current_account][self.region]

    def create_channel(self) -> ActionResult:
        cdi_input_specification = self._get_param("CdiInputSpecification")
        channel_class = self._get_param("ChannelClass")
        destinations = self._get_param("Destinations")
        encoder_settings = self._get_param("EncoderSettings")
        input_attachments = self._get_param("InputAttachments")
        input_specification = self._get_param("InputSpecification")
        log_level = self._get_param("LogLevel")
        name = self._get_param("Name")
        role_arn = self._get_param("RoleArn")
        tags = self._get_param("Tags")

        channel = self.medialive_backend.create_channel(
            cdi_input_specification=cdi_input_specification,
            channel_class=channel_class,
            destinations=destinations,
            encoder_settings=encoder_settings,
            input_attachments=input_attachments,
            input_specification=input_specification,
            log_level=log_level,
            name=name,
            role_arn=role_arn,
            tags=tags,
        )

        return ActionResult({"Channel": channel})

    def list_channels(self) -> ActionResult:
        channels = self.medialive_backend.list_channels()
        return PaginatedResult({"Channels": channels})

    def describe_channel(self) -> ActionResult:
        channel_id = self._get_param("ChannelId")
        channel = self.medialive_backend.describe_channel(channel_id=channel_id)
        return ActionResult(channel)

    def delete_channel(self) -> ActionResult:
        channel_id = self._get_param("ChannelId")
        channel = self.medialive_backend.delete_channel(channel_id=channel_id)
        return ActionResult(channel)

    def start_channel(self) -> ActionResult:
        channel_id = self._get_param("ChannelId")
        channel = self.medialive_backend.start_channel(channel_id=channel_id)
        return ActionResult(channel)

    def stop_channel(self) -> ActionResult:
        channel_id = self._get_param("ChannelId")
        channel = self.medialive_backend.stop_channel(channel_id=channel_id)
        return ActionResult(channel)

    def update_channel(self) -> ActionResult:
        channel_id = self._get_param("ChannelId")
        cdi_input_specification = self._get_param("CdiInputSpecification")
        destinations = self._get_param("Destinations")
        encoder_settings = self._get_param("EncoderSettings")
        input_attachments = self._get_param("InputAttachments")
        input_specification = self._get_param("InputSpecification")
        log_level = self._get_param("LogLevel")
        name = self._get_param("Name")
        role_arn = self._get_param("RoleArn")
        channel = self.medialive_backend.update_channel(
            channel_id=channel_id,
            cdi_input_specification=cdi_input_specification,
            destinations=destinations,
            encoder_settings=encoder_settings,
            input_attachments=input_attachments,
            input_specification=input_specification,
            log_level=log_level,
            name=name,
            role_arn=role_arn,
        )
        return ActionResult({"Channel": channel})

    def update_channel_class(self) -> str:
        channel_id = self._get_param("channelId")
        channel_class = self._get_param("channelClass")
        destinations = self._get_param("destinations")
        channel = self.medialive_backend.update_channel_class(
            channel_id=channel_id,
            channel_class=channel_class,
            destinations=destinations,
        )
        return json.dumps({"channel": channel.to_dict()})

    def restart_channel_pipelines(self) -> str:
        channel_id = self._get_param("channelId")
        pipeline_ids = self._get_param("pipelineIds")
        channel = self.medialive_backend.restart_channel_pipelines(
            channel_id=channel_id,
            pipeline_ids=pipeline_ids,
        )
        return json.dumps(channel.to_dict())

    # ---- Input ----

    def create_input(self) -> ActionResult:
        destinations = self._get_param("Destinations")
        input_devices = self._get_param("InputDevices")
        input_security_groups = self._get_param("InputSecurityGroups")
        media_connect_flows = self._get_param("MediaConnectFlows")
        name = self._get_param("Name")
        role_arn = self._get_param("RoleArn")
        sources = self._get_param("Sources")
        tags = self._get_param("Tags")
        input_type = self._get_param("Type")

        a_input = self.medialive_backend.create_input(
            destinations=destinations,
            input_devices=input_devices,
            input_security_groups=input_security_groups,
            media_connect_flows=media_connect_flows,
            name=name,
            role_arn=role_arn,
            sources=sources,
            tags=tags,
            input_type=input_type,
        )
        return ActionResult({"Input": a_input})

    def describe_input(self) -> ActionResult:
        input_id = self._get_param("InputId")
        a_input = self.medialive_backend.describe_input(input_id=input_id)
        return ActionResult(a_input)

    def list_inputs(self) -> ActionResult:
        inputs = self.medialive_backend.list_inputs()
        return PaginatedResult({"Inputs": inputs})

    def delete_input(self) -> ActionResult:
        input_id = self._get_param("InputId")
        self.medialive_backend.delete_input(input_id=input_id)
        return EmptyResult()

    def update_input(self) -> ActionResult:
        destinations = self._get_param("Destinations")
        input_devices = self._get_param("InputDevices")
        input_id = self._get_param("InputId")
        input_security_groups = self._get_param("InputSecurityGroups")
        media_connect_flows = self._get_param("MediaConnectFlows")
        name = self._get_param("Name")
        role_arn = self._get_param("RoleArn")
        sources = self._get_param("Sources")
        a_input = self.medialive_backend.update_input(
            destinations=destinations,
            input_devices=input_devices,
            input_id=input_id,
            input_security_groups=input_security_groups,
            media_connect_flows=media_connect_flows,
            name=name,
            role_arn=role_arn,
            sources=sources,
        )
        return json.dumps({"input": a_input.to_dict()})

    def create_partner_input(self) -> str:
        input_id = self._get_param("inputId")
        request_id = self._get_param("requestId")
        tags = self._get_param("tags")
        a_input = self.medialive_backend.create_partner_input(
            input_id=input_id,
            request_id=request_id,
            tags=tags,
        )
        return json.dumps({"input": a_input.to_dict()})

    # ---- InputSecurityGroup ----

    def create_input_security_group(self) -> str:
        tags = self._get_param("tags")
        whitelist_rules = self._get_param("whitelistRules")
        group = self.medialive_backend.create_input_security_group(
            tags=tags,
            whitelist_rules=whitelist_rules,
        )
        return json.dumps({"securityGroup": group.to_dict()})

    def describe_input_security_group(self) -> str:
        group_id = self._get_param("inputSecurityGroupId")
        group = self.medialive_backend.describe_input_security_group(group_id=group_id)
        return json.dumps(group.to_dict())

    def list_input_security_groups(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        groups, next_token = self.medialive_backend.list_input_security_groups(
            max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {
                "inputSecurityGroups": [g.to_dict() for g in groups],
                "nextToken": next_token,
            }
        )

    def delete_input_security_group(self) -> str:
        group_id = self._get_param("inputSecurityGroupId")
        self.medialive_backend.delete_input_security_group(group_id=group_id)
        return json.dumps({})

    def update_input_security_group(self) -> str:
        group_id = self._get_param("inputSecurityGroupId")
        tags = self._get_param("tags")
        whitelist_rules = self._get_param("whitelistRules")
        group = self.medialive_backend.update_input_security_group(
            group_id=group_id,
            tags=tags,
            whitelist_rules=whitelist_rules,
        )
        return json.dumps({"securityGroup": group.to_dict()})

    # ---- Multiplex ----

    def create_multiplex(self) -> str:
        availability_zones = self._get_param("availabilityZones")
        multiplex_settings = self._get_param("multiplexSettings")
        name = self._get_param("name")
        tags = self._get_param("tags")
        multiplex = self.medialive_backend.create_multiplex(
            availability_zones=availability_zones,
            multiplex_settings=multiplex_settings,
            name=name,
            tags=tags,
        )
        return json.dumps({"multiplex": multiplex.to_dict()})

    def describe_multiplex(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        multiplex = self.medialive_backend.describe_multiplex(multiplex_id=multiplex_id)
        return json.dumps(multiplex.to_dict())

    def list_multiplexes(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        multiplexes, next_token = self.medialive_backend.list_multiplexes(
            max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {
                "multiplexes": [m.to_dict() for m in multiplexes],
                "nextToken": next_token,
            }
        )

    def delete_multiplex(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        multiplex = self.medialive_backend.delete_multiplex(multiplex_id=multiplex_id)
        return json.dumps(multiplex.to_dict())

    def start_multiplex(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        multiplex = self.medialive_backend.start_multiplex(multiplex_id=multiplex_id)
        return json.dumps(multiplex.to_dict())

    def stop_multiplex(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        multiplex = self.medialive_backend.stop_multiplex(multiplex_id=multiplex_id)
        return json.dumps(multiplex.to_dict())

    def update_multiplex(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        multiplex_settings = self._get_param("multiplexSettings")
        name = self._get_param("name")
        multiplex = self.medialive_backend.update_multiplex(
            multiplex_id=multiplex_id,
            multiplex_settings=multiplex_settings,
            name=name,
        )
        return json.dumps({"multiplex": multiplex.to_dict()})

    # ---- MultiplexProgram ----

    def create_multiplex_program(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        multiplex_program_settings = self._get_param("multiplexProgramSettings")
        program_name = self._get_param("programName")
        program = self.medialive_backend.create_multiplex_program(
            multiplex_id=multiplex_id,
            multiplex_program_settings=multiplex_program_settings,
            program_name=program_name,
        )
        return json.dumps({"multiplexProgram": program.to_dict()})

    def describe_multiplex_program(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        program_name = self._get_param("programName")
        program = self.medialive_backend.describe_multiplex_program(
            multiplex_id=multiplex_id,
            program_name=program_name,
        )
        return json.dumps(program.to_dict())

    def list_multiplex_programs(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        programs = self.medialive_backend.list_multiplex_programs(
            multiplex_id=multiplex_id
        )
        return json.dumps(
            {"multiplexPrograms": [p.to_dict() for p in programs], "nextToken": None}
        )

    def delete_multiplex_program(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        program_name = self._get_param("programName")
        program = self.medialive_backend.delete_multiplex_program(
            multiplex_id=multiplex_id,
            program_name=program_name,
        )
        return json.dumps(program.to_dict())

    def update_multiplex_program(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        multiplex_program_settings = self._get_param("multiplexProgramSettings")
        program_name = self._get_param("programName")
        program = self.medialive_backend.update_multiplex_program(
            multiplex_id=multiplex_id,
            multiplex_program_settings=multiplex_program_settings,
            program_name=program_name,
        )
        return json.dumps({"multiplexProgram": program.to_dict()})

    # ---- Cluster ----

    def create_cluster(self) -> str:
        cluster_type = self._get_param("clusterType")
        instance_role_arn = self._get_param("instanceRoleArn")
        name = self._get_param("name")
        network_settings = self._get_param("networkSettings")
        tags = self._get_param("tags")
        cluster = self.medialive_backend.create_cluster(
            cluster_type=cluster_type,
            instance_role_arn=instance_role_arn,
            name=name,
            network_settings=network_settings,
            tags=tags,
        )
        return json.dumps(cluster.to_dict())

    def describe_cluster(self) -> str:
        cluster_id = self._get_param("clusterId")
        cluster = self.medialive_backend.describe_cluster(cluster_id=cluster_id)
        return json.dumps(cluster.to_dict())

    def list_clusters(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        clusters, next_token = self.medialive_backend.list_clusters(
            max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {"clusters": [c.to_dict() for c in clusters], "nextToken": next_token}
        )

    def delete_cluster(self) -> str:
        cluster_id = self._get_param("clusterId")
        cluster = self.medialive_backend.delete_cluster(cluster_id=cluster_id)
        return json.dumps(cluster.to_dict())

    def update_cluster(self) -> str:
        cluster_id = self._get_param("clusterId")
        name = self._get_param("name")
        network_settings = self._get_param("networkSettings")
        cluster = self.medialive_backend.update_cluster(
            cluster_id=cluster_id,
            name=name,
            network_settings=network_settings,
        )
        return json.dumps(cluster.to_dict())

    # ---- Network ----

    def create_network(self) -> str:
        ip_pools = self._get_param("ipPools")
        name = self._get_param("name")
        routes = self._get_param("routes")
        tags = self._get_param("tags")
        network = self.medialive_backend.create_network(
            ip_pools=ip_pools,
            name=name,
            routes=routes,
            tags=tags,
        )
        return json.dumps(network.to_dict())

    def describe_network(self) -> str:
        network_id = self._get_param("networkId")
        network = self.medialive_backend.describe_network(network_id=network_id)
        return json.dumps(network.to_dict())

    def list_networks(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        networks, next_token = self.medialive_backend.list_networks(
            max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {"networks": [n.to_dict() for n in networks], "nextToken": next_token}
        )

    def delete_network(self) -> str:
        network_id = self._get_param("networkId")
        network = self.medialive_backend.delete_network(network_id=network_id)
        return json.dumps(network.to_dict())

    def update_network(self) -> str:
        network_id = self._get_param("networkId")
        ip_pools = self._get_param("ipPools")
        name = self._get_param("name")
        routes = self._get_param("routes")
        network = self.medialive_backend.update_network(
            network_id=network_id,
            ip_pools=ip_pools,
            name=name,
            routes=routes,
        )
        return json.dumps(network.to_dict())

    # ---- Node ----

    def create_node(self) -> str:
        cluster_id = self._get_param("clusterId")
        name = self._get_param("name")
        node_interface_mappings = self._get_param("nodeInterfaceMappings")
        role = self._get_param("role")
        tags = self._get_param("tags")
        node = self.medialive_backend.create_node(
            cluster_id=cluster_id,
            name=name,
            node_interface_mappings=node_interface_mappings,
            role=role,
            tags=tags,
        )
        return json.dumps(node.to_dict())

    def describe_node(self) -> str:
        cluster_id = self._get_param("clusterId")
        node_id = self._get_param("nodeId")
        node = self.medialive_backend.describe_node(
            cluster_id=cluster_id, node_id=node_id
        )
        return json.dumps(node.to_dict())

    def list_nodes(self) -> str:
        cluster_id = self._get_param("clusterId")
        nodes = self.medialive_backend.list_nodes(cluster_id=cluster_id)
        return json.dumps({"nodes": [n.to_dict() for n in nodes], "nextToken": None})

    def delete_node(self) -> str:
        cluster_id = self._get_param("clusterId")
        node_id = self._get_param("nodeId")
        node = self.medialive_backend.delete_node(
            cluster_id=cluster_id, node_id=node_id
        )
        return json.dumps(node.to_dict())

    def update_node(self) -> str:
        cluster_id = self._get_param("clusterId")
        node_id = self._get_param("nodeId")
        name = self._get_param("name")
        role = self._get_param("role")
        node = self.medialive_backend.update_node(
            cluster_id=cluster_id,
            node_id=node_id,
            name=name,
            role=role,
        )
        return json.dumps(node.to_dict())

    def update_node_state(self) -> str:
        cluster_id = self._get_param("clusterId")
        node_id = self._get_param("nodeId")
        state = self._get_param("state")
        node = self.medialive_backend.update_node_state(
            cluster_id=cluster_id,
            node_id=node_id,
            state=state,
        )
        return json.dumps(node.to_dict())

    def create_node_registration_script(self) -> str:
        cluster_id = self._get_param("clusterId")
        node_id = self._get_param("id")
        name = self._get_param("name")
        script = self.medialive_backend.create_node_registration_script(
            cluster_id=cluster_id,
            node_id=node_id,
            name=name,
        )
        return json.dumps({"nodeRegistrationScript": script})

    # ---- ChannelPlacementGroup ----

    def create_channel_placement_group(self) -> str:
        cluster_id = self._get_param("clusterId")
        name = self._get_param("name")
        nodes = self._get_param("nodes")
        tags = self._get_param("tags")
        group = self.medialive_backend.create_channel_placement_group(
            cluster_id=cluster_id,
            name=name,
            nodes=nodes,
            tags=tags,
        )
        return json.dumps(group.to_dict())

    def describe_channel_placement_group(self) -> str:
        cluster_id = self._get_param("clusterId")
        group_id = self._get_param("channelPlacementGroupId")
        group = self.medialive_backend.describe_channel_placement_group(
            cluster_id=cluster_id, group_id=group_id
        )
        return json.dumps(group.to_dict())

    def list_channel_placement_groups(self) -> str:
        cluster_id = self._get_param("clusterId")
        groups = self.medialive_backend.list_channel_placement_groups(
            cluster_id=cluster_id
        )
        return json.dumps(
            {
                "channelPlacementGroups": [g.to_dict() for g in groups],
                "nextToken": None,
            }
        )

    def delete_channel_placement_group(self) -> str:
        cluster_id = self._get_param("clusterId")
        group_id = self._get_param("channelPlacementGroupId")
        group = self.medialive_backend.delete_channel_placement_group(
            cluster_id=cluster_id, group_id=group_id
        )
        return json.dumps(group.to_dict())

    def update_channel_placement_group(self) -> str:
        cluster_id = self._get_param("clusterId")
        group_id = self._get_param("channelPlacementGroupId")
        name = self._get_param("name")
        nodes = self._get_param("nodes")
        group = self.medialive_backend.update_channel_placement_group(
            cluster_id=cluster_id,
            group_id=group_id,
            name=name,
            nodes=nodes,
        )
        return json.dumps(group.to_dict())

    # ---- SdiSource ----

    def create_sdi_source(self) -> str:
        mode = self._get_param("mode")
        name = self._get_param("name")
        tags = self._get_param("tags")
        sdi_type = self._get_param("type")
        source = self.medialive_backend.create_sdi_source(
            mode=mode,
            name=name,
            tags=tags,
            sdi_type=sdi_type,
        )
        return json.dumps(source.to_dict())

    def describe_sdi_source(self) -> str:
        sdi_source_id = self._get_param("sdiSourceId")
        source = self.medialive_backend.describe_sdi_source(sdi_source_id=sdi_source_id)
        return json.dumps(source.to_dict())

    def list_sdi_sources(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        sources, next_token = self.medialive_backend.list_sdi_sources(
            max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {"sdiSources": [s.to_dict() for s in sources], "nextToken": next_token}
        )

    def delete_sdi_source(self) -> str:
        sdi_source_id = self._get_param("sdiSourceId")
        self.medialive_backend.delete_sdi_source(sdi_source_id=sdi_source_id)
        return json.dumps({})

    def update_sdi_source(self) -> str:
        sdi_source_id = self._get_param("sdiSourceId")
        mode = self._get_param("mode")
        name = self._get_param("name")
        sdi_type = self._get_param("type")
        source = self.medialive_backend.update_sdi_source(
            sdi_source_id=sdi_source_id,
            mode=mode,
            name=name,
            sdi_type=sdi_type,
        )
        return json.dumps(source.to_dict())

    # ---- CloudWatchAlarmTemplateGroup ----

    def create_cloud_watch_alarm_template_group(self) -> str:
        description = self._get_param("description")
        name = self._get_param("name")
        tags = self._get_param("tags")
        group = self.medialive_backend.create_cloud_watch_alarm_template_group(
            description=description, name=name, tags=tags
        )
        return json.dumps(group.to_dict())

    def get_cloud_watch_alarm_template_group(self) -> str:
        identifier = self._get_param("identifier")
        group = self.medialive_backend.get_cloud_watch_alarm_template_group(
            identifier=identifier
        )
        return json.dumps(group.to_dict())

    def list_cloud_watch_alarm_template_groups(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        groups, next_token = (
            self.medialive_backend.list_cloud_watch_alarm_template_groups(
                max_results=max_results, next_token=next_token
            )
        )
        return json.dumps(
            {
                "cloudWatchAlarmTemplateGroups": [g.to_dict() for g in groups],
                "nextToken": next_token,
            }
        )

    def delete_cloud_watch_alarm_template_group(self) -> str:
        identifier = self._get_param("identifier")
        self.medialive_backend.delete_cloud_watch_alarm_template_group(
            identifier=identifier
        )
        return json.dumps({})

    def update_cloud_watch_alarm_template_group(self) -> str:
        identifier = self._get_param("identifier")
        description = self._get_param("description")
        group = self.medialive_backend.update_cloud_watch_alarm_template_group(
            identifier=identifier, description=description
        )
        return json.dumps(group.to_dict())

    # ---- CloudWatchAlarmTemplate ----

    def create_cloud_watch_alarm_template(self) -> str:
        template = self.medialive_backend.create_cloud_watch_alarm_template(
            comparison_operator=self._get_param("comparisonOperator"),
            datapoints_to_alarm=self._get_param("datapointsToAlarm"),
            description=self._get_param("description"),
            evaluation_periods=self._get_param("evaluationPeriods"),
            group_identifier=self._get_param("groupIdentifier"),
            metric_name=self._get_param("metricName"),
            name=self._get_param("name"),
            period=self._get_param("period"),
            statistic=self._get_param("statistic"),
            tags=self._get_param("tags"),
            target_resource_type=self._get_param("targetResourceType"),
            threshold=self._get_param("threshold"),
            treat_missing_data=self._get_param("treatMissingData"),
        )
        return json.dumps(template.to_dict())

    def get_cloud_watch_alarm_template(self) -> str:
        identifier = self._get_param("identifier")
        template = self.medialive_backend.get_cloud_watch_alarm_template(
            identifier=identifier
        )
        return json.dumps(template.to_dict())

    def list_cloud_watch_alarm_templates(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        templates, next_token = self.medialive_backend.list_cloud_watch_alarm_templates(
            max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {
                "cloudWatchAlarmTemplates": [t.to_dict() for t in templates],
                "nextToken": next_token,
            }
        )

    def delete_cloud_watch_alarm_template(self) -> str:
        identifier = self._get_param("identifier")
        self.medialive_backend.delete_cloud_watch_alarm_template(identifier=identifier)
        return json.dumps({})

    def update_cloud_watch_alarm_template(self) -> str:
        identifier = self._get_param("identifier")
        template = self.medialive_backend.update_cloud_watch_alarm_template(
            identifier=identifier,
            comparison_operator=self._get_param("comparisonOperator"),
            datapoints_to_alarm=self._get_param("datapointsToAlarm"),
            description=self._get_param("description"),
            evaluation_periods=self._get_param("evaluationPeriods"),
            group_identifier=self._get_param("groupIdentifier"),
            metric_name=self._get_param("metricName"),
            period=self._get_param("period"),
            statistic=self._get_param("statistic"),
            target_resource_type=self._get_param("targetResourceType"),
            threshold=self._get_param("threshold"),
            treat_missing_data=self._get_param("treatMissingData"),
        )
        return json.dumps(template.to_dict())

    # ---- EventBridgeRuleTemplateGroup ----

    def create_event_bridge_rule_template_group(self) -> str:
        description = self._get_param("description")
        name = self._get_param("name")
        tags = self._get_param("tags")
        group = self.medialive_backend.create_event_bridge_rule_template_group(
            description=description, name=name, tags=tags
        )
        return json.dumps(group.to_dict())

    def get_event_bridge_rule_template_group(self) -> str:
        identifier = self._get_param("identifier")
        group = self.medialive_backend.get_event_bridge_rule_template_group(
            identifier=identifier
        )
        return json.dumps(group.to_dict())

    def list_event_bridge_rule_template_groups(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        groups, next_token = (
            self.medialive_backend.list_event_bridge_rule_template_groups(
                max_results=max_results, next_token=next_token
            )
        )
        return json.dumps(
            {
                "eventBridgeRuleTemplateGroups": [g.to_dict() for g in groups],
                "nextToken": next_token,
            }
        )

    def delete_event_bridge_rule_template_group(self) -> str:
        identifier = self._get_param("identifier")
        self.medialive_backend.delete_event_bridge_rule_template_group(
            identifier=identifier
        )
        return json.dumps({})

    def update_event_bridge_rule_template_group(self) -> str:
        identifier = self._get_param("identifier")
        description = self._get_param("description")
        group = self.medialive_backend.update_event_bridge_rule_template_group(
            identifier=identifier, description=description
        )
        return json.dumps(group.to_dict())

    # ---- EventBridgeRuleTemplate ----

    def create_event_bridge_rule_template(self) -> str:
        template = self.medialive_backend.create_event_bridge_rule_template(
            description=self._get_param("description"),
            event_targets=self._get_param("eventTargets"),
            event_type=self._get_param("eventType"),
            group_identifier=self._get_param("groupIdentifier"),
            name=self._get_param("name"),
            tags=self._get_param("tags"),
        )
        return json.dumps(template.to_dict())

    def get_event_bridge_rule_template(self) -> str:
        identifier = self._get_param("identifier")
        template = self.medialive_backend.get_event_bridge_rule_template(
            identifier=identifier
        )
        return json.dumps(template.to_dict())

    def list_event_bridge_rule_templates(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        templates, next_token = self.medialive_backend.list_event_bridge_rule_templates(
            max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {
                "eventBridgeRuleTemplates": [t.to_dict() for t in templates],
                "nextToken": next_token,
            }
        )

    def delete_event_bridge_rule_template(self) -> str:
        identifier = self._get_param("identifier")
        self.medialive_backend.delete_event_bridge_rule_template(identifier=identifier)
        return json.dumps({})

    def update_event_bridge_rule_template(self) -> str:
        identifier = self._get_param("identifier")
        template = self.medialive_backend.update_event_bridge_rule_template(
            identifier=identifier,
            description=self._get_param("description"),
            event_targets=self._get_param("eventTargets"),
            event_type=self._get_param("eventType"),
            group_identifier=self._get_param("groupIdentifier"),
        )
        return json.dumps(template.to_dict())

    # ---- SignalMap ----

    def create_signal_map(self) -> str:
        signal_map = self.medialive_backend.create_signal_map(
            cloud_watch_alarm_template_group_identifiers=self._get_param(
                "cloudWatchAlarmTemplateGroupIdentifiers"
            ),
            description=self._get_param("description"),
            discovery_entry_point_arn=self._get_param("discoveryEntryPointArn"),
            event_bridge_rule_template_group_identifiers=self._get_param(
                "eventBridgeRuleTemplateGroupIdentifiers"
            ),
            name=self._get_param("name"),
            tags=self._get_param("tags"),
        )
        return json.dumps(signal_map.to_dict())

    def get_signal_map(self) -> str:
        identifier = self._get_param("identifier")
        signal_map = self.medialive_backend.get_signal_map(identifier=identifier)
        return json.dumps(signal_map.to_dict())

    def list_signal_maps(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        signal_maps, next_token = self.medialive_backend.list_signal_maps(
            max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {
                "signalMaps": [sm.to_dict() for sm in signal_maps],
                "nextToken": next_token,
            }
        )

    def delete_signal_map(self) -> str:
        identifier = self._get_param("identifier")
        self.medialive_backend.delete_signal_map(identifier=identifier)
        return json.dumps({})

    def start_update_signal_map(self) -> str:
        identifier = self._get_param("identifier")
        signal_map = self.medialive_backend.start_update_signal_map(
            identifier=identifier,
            cloud_watch_alarm_template_group_identifiers=self._get_param(
                "cloudWatchAlarmTemplateGroupIdentifiers"
            ),
            description=self._get_param("description"),
            discovery_entry_point_arn=self._get_param("discoveryEntryPointArn"),
            event_bridge_rule_template_group_identifiers=self._get_param(
                "eventBridgeRuleTemplateGroupIdentifiers"
            ),
            name=self._get_param("name"),
        )
        return json.dumps(signal_map.to_dict())

    def start_monitor_deployment(self) -> str:
        identifier = self._get_param("identifier")
        dry_run = self._get_param("dryRun") or False
        signal_map = self.medialive_backend.start_monitor_deployment(
            identifier=identifier, dry_run=dry_run
        )
        return json.dumps(signal_map.to_dict())

    def start_delete_monitor_deployment(self) -> str:
        identifier = self._get_param("identifier")
        signal_map = self.medialive_backend.start_delete_monitor_deployment(
            identifier=identifier
        )
        return json.dumps(signal_map.to_dict())

    # ---- Tags ----

    def create_tags(self) -> str:
        resource_arn = self._get_param("resource-arn")
        tags = self._get_param("tags")
        self.medialive_backend.create_tags(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def delete_tags(self) -> str:
        resource_arn = self._get_param("resource-arn")
        tag_keys = self._get_param("tagKeys") or []
        self.medialive_backend.delete_tags(resource_arn=resource_arn, tag_keys=tag_keys)
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_param("resource-arn")
        tags = self.medialive_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"tags": tags})

    # ---- Schedule ----

    def batch_update_schedule(self) -> str:
        channel_id = self._get_param("channelId")
        creates = self._get_param("creates")
        deletes = self._get_param("deletes")
        result = self.medialive_backend.batch_update_schedule(
            channel_id=channel_id,
            creates=creates,
            deletes=deletes,
        )
        return json.dumps(result)

    def describe_schedule(self) -> str:
        channel_id = self._get_param("channelId")
        actions = self.medialive_backend.describe_schedule(channel_id=channel_id)
        return json.dumps({"scheduleActions": actions, "nextToken": None})

    def delete_schedule(self) -> str:
        channel_id = self._get_param("channelId")
        self.medialive_backend.delete_schedule(channel_id=channel_id)
        return json.dumps({})

    # ---- Batch operations ----

    def batch_delete(self) -> str:
        result = self.medialive_backend.batch_delete(
            channel_ids=self._get_param("channelIds"),
            input_ids=self._get_param("inputIds"),
            input_security_group_ids=self._get_param("inputSecurityGroupIds"),
            multiplex_ids=self._get_param("multiplexIds"),
        )
        return json.dumps(result)

    def batch_start(self) -> str:
        result = self.medialive_backend.batch_start(
            channel_ids=self._get_param("channelIds"),
            multiplex_ids=self._get_param("multiplexIds"),
        )
        return json.dumps(result)

    def batch_stop(self) -> str:
        result = self.medialive_backend.batch_stop(
            channel_ids=self._get_param("channelIds"),
            multiplex_ids=self._get_param("multiplexIds"),
        )
        return json.dumps(result)

    # ---- Account Configuration ----

    def describe_account_configuration(self) -> str:
        result = self.medialive_backend.describe_account_configuration()
        return json.dumps(result)

    def update_account_configuration(self) -> str:
        account_configuration = self._get_param("accountConfiguration")
        result = self.medialive_backend.update_account_configuration(
            account_configuration=account_configuration
        )
        return json.dumps(result)

    # ---- InputDevice stubs ----

    def list_input_devices(self) -> str:
        self.medialive_backend.list_input_devices()
        return json.dumps({"inputDevices": [], "nextToken": None})

    def describe_input_device(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.describe_input_device(input_device_id=input_device_id)
        return json.dumps({})  # unreachable

    def update_input_device(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.update_input_device(input_device_id=input_device_id)
        return json.dumps({})  # unreachable

    def accept_input_device_transfer(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.accept_input_device_transfer(
            input_device_id=input_device_id
        )
        return json.dumps({})

    def cancel_input_device_transfer(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.cancel_input_device_transfer(
            input_device_id=input_device_id
        )
        return json.dumps({})

    def reject_input_device_transfer(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.reject_input_device_transfer(
            input_device_id=input_device_id
        )
        return json.dumps({})

    def reboot_input_device(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.reboot_input_device(input_device_id=input_device_id)
        return json.dumps({})

    def start_input_device(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.start_input_device(input_device_id=input_device_id)
        return json.dumps({})

    def stop_input_device(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.stop_input_device(input_device_id=input_device_id)
        return json.dumps({})

    def start_input_device_maintenance_window(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.start_input_device_maintenance_window(
            input_device_id=input_device_id
        )
        return json.dumps({})

    def transfer_input_device(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        self.medialive_backend.transfer_input_device(input_device_id=input_device_id)
        return json.dumps({})

    def describe_input_device_thumbnail(self) -> str:
        input_device_id = self._get_param("inputDeviceId")
        accept = self._get_param("accept")
        self.medialive_backend.describe_input_device_thumbnail(
            input_device_id=input_device_id, accept=accept
        )
        return json.dumps({})  # unreachable

    def list_input_device_transfers(self) -> str:
        self.medialive_backend.list_input_device_transfers(transfer_type="")
        return json.dumps({"inputDeviceTransfers": [], "nextToken": None})

    def claim_device(self) -> str:
        self.medialive_backend.claim_device()
        return json.dumps({})

    # ---- Offering / Reservation stubs ----

    def list_offerings(self) -> str:
        self.medialive_backend.list_offerings()
        return json.dumps({"offerings": [], "nextToken": None})

    def describe_offering(self) -> str:
        offering_id = self._get_param("offeringId")
        self.medialive_backend.describe_offering(offering_id=offering_id)
        return json.dumps({})  # unreachable

    def purchase_offering(self) -> str:
        offering_id = self._get_param("offeringId")
        self.medialive_backend.purchase_offering(offering_id=offering_id)
        return json.dumps({})  # unreachable

    def list_reservations(self) -> str:
        self.medialive_backend.list_reservations()
        return json.dumps({"reservations": [], "nextToken": None})

    def describe_reservation(self) -> str:
        reservation_id = self._get_param("reservationId")
        self.medialive_backend.describe_reservation(reservation_id=reservation_id)
        return json.dumps({})  # unreachable

    def delete_reservation(self) -> str:
        reservation_id = self._get_param("reservationId")
        self.medialive_backend.delete_reservation(reservation_id=reservation_id)
        return json.dumps({})  # unreachable

    def update_reservation(self) -> str:
        reservation_id = self._get_param("reservationId")
        self.medialive_backend.update_reservation(reservation_id=reservation_id)
        return json.dumps({})  # unreachable

    # ---- Misc stubs ----

    def describe_thumbnails(self) -> str:
        channel_id = self._get_param("channelId")
        pipeline_id = self._get_param("pipelineId")
        thumbnail_type = self._get_param("thumbnailType")
        self.medialive_backend.describe_thumbnails(
            channel_id=channel_id,
            pipeline_id=pipeline_id,
            thumbnail_type=thumbnail_type,
        )
        return json.dumps({"thumbnailDetails": []})

    def list_alerts(self) -> str:
        channel_id = self._get_param("channelId")
        self.medialive_backend.list_alerts(channel_id=channel_id)
        return json.dumps({"alerts": [], "nextToken": None})

    def list_cluster_alerts(self) -> str:
        cluster_id = self._get_param("clusterId")
        self.medialive_backend.list_cluster_alerts(cluster_id=cluster_id)
        return json.dumps({"alerts": [], "nextToken": None})

    def list_multiplex_alerts(self) -> str:
        multiplex_id = self._get_param("multiplexId")
        self.medialive_backend.list_multiplex_alerts(multiplex_id=multiplex_id)
        return json.dumps({"alerts": [], "nextToken": None})

    def list_versions(self) -> str:
        versions = self.medialive_backend.list_versions()
        return json.dumps({"versions": versions})

