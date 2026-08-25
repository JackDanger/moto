"""Handles incoming bedrockagent requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import AgentsforBedrockBackend, bedrockagent_backends


class AgentsforBedrockResponse(BaseResponse):
    """Handler for AgentsforBedrock requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="bedrock-agent")

    @property
    def bedrockagent_backend(self) -> AgentsforBedrockBackend:
        """Return backend instance specific for this region."""
        return bedrockagent_backends[self.current_account][self.region]

    # ========== Agent handlers ==========

    def create_agent(self) -> str:
        params = json.loads(self.body)
        agent = self.bedrockagent_backend.create_agent(
            agent_name=params.get("agentName"),
            client_token=params.get("clientToken"),
            instruction=params.get("instruction"),
            foundation_model=params.get("foundationModel"),
            description=params.get("description"),
            idle_session_ttl_in_seconds=params.get("idleSessionTTLInSeconds"),
            agent_resource_role_arn=params.get("agentResourceRoleArn"),
            customer_encryption_key_arn=params.get("customerEncryptionKeyArn"),
            tags=params.get("tags"),
            prompt_override_configuration=params.get("promptOverrideConfiguration"),
        )
        return json.dumps({"agent": dict(agent.to_dict())})

    def get_agent(self) -> str:
        agent_id = self.path.split("/")[-2]
        agent = self.bedrockagent_backend.get_agent(agent_id=agent_id)
        return json.dumps({"agent": dict(agent.to_dict())})

    def list_agents(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults")
        next_token = params.get("nextToken")
        max_results = int(max_results) if max_results else None
        agents, next_token = self.bedrockagent_backend.list_agents(
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {
                "agentSummaries": [a.dict_summary() for a in agents],
                "nextToken": next_token,
            }
        )

    def delete_agent(self) -> str:
        params = self._get_params()
        skip_resource_in_use_check = params.get("skipResourceInUseCheck")
        agent_id = self.path.split("/")[-2]
        agent_id, agent_status = self.bedrockagent_backend.delete_agent(
            agent_id=agent_id, skip_resource_in_use_check=skip_resource_in_use_check
        )
        return json.dumps({"agentId": agent_id, "agentStatus": agent_status})

    def update_agent(self) -> str:
        agent_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        agent = self.bedrockagent_backend.update_agent(
            agent_id=agent_id,
            agent_name=params.get("agentName"),
            agent_resource_role_arn=params.get("agentResourceRoleArn"),
            foundation_model=params.get("foundationModel"),
            instruction=params.get("instruction"),
            description=params.get("description"),
            idle_session_ttl_in_seconds=params.get("idleSessionTTLInSeconds"),
            customer_encryption_key_arn=params.get("customerEncryptionKeyArn"),
            prompt_override_configuration=params.get("promptOverrideConfiguration"),
        )
        return json.dumps({"agent": agent.to_dict()})

    def prepare_agent(self) -> str:
        agent_id = self.path.split("/")[-2]
        agent_id, agent_arn, agent_version, prepared_at = self.bedrockagent_backend.prepare_agent(
            agent_id=agent_id
        )
        return json.dumps({
            "agentId": agent_id,
            "agentArn": agent_arn,
            "agentVersion": agent_version,
            "agentStatus": "PREPARED",
        })

    def get_agent_version(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1].rstrip("/")
        version_dict = self.bedrockagent_backend.get_agent_version(
            agent_id=agent_id, agent_version=agent_version
        )
        return json.dumps({"agentVersion": version_dict})

    def list_agent_versions(self) -> str:
        agent_id = self.path.split("/")[2]
        params = json.loads(self.body) if self.body else {}
        max_results = params.get("maxResults")
        next_token = params.get("nextToken")
        versions, next_token = self.bedrockagent_backend.list_agent_versions(
            agent_id=agent_id,
            max_results=int(max_results) if max_results else None,
            next_token=next_token,
        )
        return json.dumps({"agentVersionSummaries": versions, "nextToken": next_token})

    def delete_agent_version(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1].rstrip("/")
        params = self._get_params()
        agent_id, agent_version, status = self.bedrockagent_backend.delete_agent_version(
            agent_id=agent_id,
            agent_version=agent_version,
            skip_resource_in_use_check=params.get("skipResourceInUseCheck"),
        )
        return json.dumps({"agentId": agent_id, "agentVersion": agent_version, "agentStatus": status})

    # ========== Agent Alias handlers ==========

    def create_agent_alias(self) -> str:
        agent_id = self.path.split("/")[2]
        params = json.loads(self.body)
        alias = self.bedrockagent_backend.create_agent_alias(
            agent_id=agent_id,
            agent_alias_name=params.get("agentAliasName"),
            client_token=params.get("clientToken"),
            description=params.get("description"),
            routing_configuration=params.get("routingConfiguration"),
            tags=params.get("tags"),
        )
        return json.dumps({"agentAlias": alias.to_dict()})

    def get_agent_alias(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_alias_id = parts[parts.index("agentaliases") + 1].rstrip("/")
        alias = self.bedrockagent_backend.get_agent_alias(
            agent_id=agent_id, agent_alias_id=agent_alias_id
        )
        return json.dumps({"agentAlias": alias.to_dict()})

    def list_agent_aliases(self) -> str:
        agent_id = self.path.split("/")[2]
        params = json.loads(self.body) if self.body else {}
        max_results = params.get("maxResults")
        next_token = params.get("nextToken")
        aliases, next_token = self.bedrockagent_backend.list_agent_aliases(
            agent_id=agent_id,
            max_results=int(max_results) if max_results else None,
            next_token=next_token,
        )
        return json.dumps({"agentAliasSummaries": [a.dict_summary() for a in aliases], "nextToken": next_token})

    def delete_agent_alias(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_alias_id = parts[parts.index("agentaliases") + 1].rstrip("/")
        agent_id, alias_id, status = self.bedrockagent_backend.delete_agent_alias(
            agent_id=agent_id, agent_alias_id=agent_alias_id
        )
        return json.dumps({"agentId": agent_id, "agentAliasId": alias_id, "agentAliasStatus": status})

    def update_agent_alias(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_alias_id = parts[parts.index("agentaliases") + 1].rstrip("/")
        params = json.loads(self.body)
        alias = self.bedrockagent_backend.update_agent_alias(
            agent_id=agent_id,
            agent_alias_id=agent_alias_id,
            agent_alias_name=params.get("agentAliasName"),
            description=params.get("description"),
            routing_configuration=params.get("routingConfiguration"),
        )
        return json.dumps({"agentAlias": alias.to_dict()})

    # ========== Agent Action Group handlers ==========

    def create_agent_action_group(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        params = json.loads(self.body)
        ag = self.bedrockagent_backend.create_agent_action_group(
            agent_id=agent_id,
            agent_version=agent_version,
            action_group_name=params.get("actionGroupName"),
            client_token=params.get("clientToken"),
            description=params.get("description"),
            parent_action_group_signature=params.get("parentActionGroupSignature"),
            action_group_executor=params.get("actionGroupExecutor"),
            api_schema=params.get("apiSchema"),
            function_schema=params.get("functionSchema"),
            action_group_state=params.get("actionGroupState"),
        )
        return json.dumps({"agentActionGroup": ag.to_dict()})

    def get_agent_action_group(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        action_group_id = parts[parts.index("actiongroups") + 1].rstrip("/")
        ag = self.bedrockagent_backend.get_agent_action_group(
            agent_id=agent_id,
            agent_version=agent_version,
            action_group_id=action_group_id,
        )
        return json.dumps({"agentActionGroup": ag.to_dict()})

    def list_agent_action_groups(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        params = json.loads(self.body) if self.body else {}
        groups, next_token = self.bedrockagent_backend.list_agent_action_groups(
            agent_id=agent_id,
            agent_version=agent_version,
            max_results=params.get("maxResults"),
            next_token=params.get("nextToken"),
        )
        return json.dumps({"actionGroupSummaries": [g.dict_summary() for g in groups], "nextToken": next_token})

    def delete_agent_action_group(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        action_group_id = parts[parts.index("actiongroups") + 1].rstrip("/")
        params = self._get_params()
        self.bedrockagent_backend.delete_agent_action_group(
            agent_id=agent_id,
            agent_version=agent_version,
            action_group_id=action_group_id,
            skip_resource_in_use_check=params.get("skipResourceInUseCheck"),
        )
        return json.dumps({})

    def update_agent_action_group(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        action_group_id = parts[parts.index("actiongroups") + 1].rstrip("/")
        params = json.loads(self.body)
        ag = self.bedrockagent_backend.update_agent_action_group(
            agent_id=agent_id,
            agent_version=agent_version,
            action_group_id=action_group_id,
            action_group_name=params.get("actionGroupName"),
            description=params.get("description"),
            parent_action_group_signature=params.get("parentActionGroupSignature"),
            action_group_executor=params.get("actionGroupExecutor"),
            api_schema=params.get("apiSchema"),
            function_schema=params.get("functionSchema"),
            action_group_state=params.get("actionGroupState"),
        )
        return json.dumps({"agentActionGroup": ag.to_dict()})

    # ========== Agent Knowledge Base handlers ==========

    def associate_agent_knowledge_base(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        params = json.loads(self.body)
        akb = self.bedrockagent_backend.associate_agent_knowledge_base(
            agent_id=agent_id,
            agent_version=agent_version,
            knowledge_base_id=params.get("knowledgeBaseId"),
            knowledge_base_state=params.get("knowledgeBaseState", "ENABLED"),
            description=params.get("description", ""),
        )
        return json.dumps({"agentKnowledgeBase": akb.to_dict()})

    def get_agent_knowledge_base(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        knowledge_base_id = parts[parts.index("knowledgebases") + 1].rstrip("/")
        akb = self.bedrockagent_backend.get_agent_knowledge_base(
            agent_id=agent_id,
            agent_version=agent_version,
            knowledge_base_id=knowledge_base_id,
        )
        return json.dumps({"agentKnowledgeBase": akb.to_dict()})

    def list_agent_knowledge_bases(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        params = json.loads(self.body) if self.body else {}
        bases, next_token = self.bedrockagent_backend.list_agent_knowledge_bases(
            agent_id=agent_id,
            agent_version=agent_version,
            max_results=params.get("maxResults"),
            next_token=params.get("nextToken"),
        )
        return json.dumps({"agentKnowledgeBaseSummaries": [b.dict_summary() for b in bases], "nextToken": next_token})

    def disassociate_agent_knowledge_base(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        knowledge_base_id = parts[parts.index("knowledgebases") + 1].rstrip("/")
        self.bedrockagent_backend.disassociate_agent_knowledge_base(
            agent_id=agent_id,
            agent_version=agent_version,
            knowledge_base_id=knowledge_base_id,
        )
        return json.dumps({})

    def update_agent_knowledge_base(self) -> str:
        parts = self.path.split("/")
        agent_id = parts[parts.index("agents") + 1]
        agent_version = parts[parts.index("agentversions") + 1]
        knowledge_base_id = parts[parts.index("knowledgebases") + 1].rstrip("/")
        params = json.loads(self.body)
        akb = self.bedrockagent_backend.update_agent_knowledge_base(
            agent_id=agent_id,
            agent_version=agent_version,
            knowledge_base_id=knowledge_base_id,
            knowledge_base_state=params.get("knowledgeBaseState"),
            description=params.get("description"),
        )
        return json.dumps({"agentKnowledgeBase": akb.to_dict()})

    # ========== Knowledge Base handlers ==========

    def create_knowledge_base(self) -> str:
        params = json.loads(self.body)
        knowledge_base = self.bedrockagent_backend.create_knowledge_base(
            client_token=params.get("clientToken"),
            name=params.get("name"),
            description=params.get("description"),
            role_arn=params.get("roleArn"),
            knowledge_base_configuration=params.get("knowledgeBaseConfiguration"),
            storage_configuration=params.get("storageConfiguration"),
            tags=params.get("tags"),
        )
        return json.dumps({"knowledgeBase": dict(knowledge_base.to_dict())})

    def list_knowledge_bases(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults")
        next_token = params.get("nextToken")
        max_results = int(max_results) if max_results else None
        knowledge_bases, next_token = self.bedrockagent_backend.list_knowledge_bases(
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {
                "knowledgeBaseSummaries": [kb.dict_summary() for kb in knowledge_bases],
                "nextToken": next_token,
            }
        )

    def delete_knowledge_base(self) -> str:
        knowledge_base_id = self.path.split("/")[-1]
        (
            knowledge_base_id,
            knowledge_base_status,
        ) = self.bedrockagent_backend.delete_knowledge_base(
            knowledge_base_id=knowledge_base_id
        )
        return json.dumps(
            {"knowledgeBaseId": knowledge_base_id, "status": knowledge_base_status}
        )

    def get_knowledge_base(self) -> str:
        knowledge_base_id = self.path.split("/")[-1]
        knowledge_base = self.bedrockagent_backend.get_knowledge_base(
            knowledge_base_id=knowledge_base_id
        )
        return json.dumps({"knowledgeBase": knowledge_base.to_dict()})

    def update_knowledge_base(self) -> str:
        knowledge_base_id = self.path.split("/")[-1]
        params = json.loads(self.body)
        kb = self.bedrockagent_backend.update_knowledge_base(
            knowledge_base_id=knowledge_base_id,
            name=params.get("name"),
            role_arn=params.get("roleArn"),
            knowledge_base_configuration=params.get("knowledgeBaseConfiguration"),
            storage_configuration=params.get("storageConfiguration"),
            description=params.get("description"),
        )
        return json.dumps({"knowledgeBase": kb.to_dict()})

    # ========== Data Source handlers ==========

    def create_data_source(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        params = json.loads(self.body)
        ds = self.bedrockagent_backend.create_data_source(
            knowledge_base_id=knowledge_base_id,
            name=params.get("name"),
            data_source_configuration=params.get("dataSourceConfiguration"),
            client_token=params.get("clientToken"),
            description=params.get("description"),
            server_side_encryption_configuration=params.get("serverSideEncryptionConfiguration"),
            vector_ingestion_configuration=params.get("vectorIngestionConfiguration"),
        )
        return json.dumps({"dataSource": ds.to_dict()})

    def get_data_source(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        data_source_id = parts[parts.index("datasources") + 1]
        ds = self.bedrockagent_backend.get_data_source(
            knowledge_base_id=knowledge_base_id,
            data_source_id=data_source_id,
        )
        return json.dumps({"dataSource": ds.to_dict()})

    def list_data_sources(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        params = json.loads(self.body) if self.body else {}
        data_sources, next_token = self.bedrockagent_backend.list_data_sources(
            knowledge_base_id=knowledge_base_id,
            max_results=params.get("maxResults"),
            next_token=params.get("nextToken"),
        )
        return json.dumps({"dataSourceSummaries": [ds.dict_summary() for ds in data_sources], "nextToken": next_token})

    def delete_data_source(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        data_source_id = parts[parts.index("datasources") + 1]
        kb_id, ds_id, status = self.bedrockagent_backend.delete_data_source(
            knowledge_base_id=knowledge_base_id,
            data_source_id=data_source_id,
        )
        return json.dumps({"knowledgeBaseId": kb_id, "dataSourceId": ds_id, "status": status})

    def update_data_source(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        data_source_id = parts[parts.index("datasources") + 1]
        params = json.loads(self.body)
        ds = self.bedrockagent_backend.update_data_source(
            knowledge_base_id=knowledge_base_id,
            data_source_id=data_source_id,
            name=params.get("name"),
            data_source_configuration=params.get("dataSourceConfiguration"),
            description=params.get("description"),
            server_side_encryption_configuration=params.get("serverSideEncryptionConfiguration"),
            vector_ingestion_configuration=params.get("vectorIngestionConfiguration"),
        )
        return json.dumps({"dataSource": ds.to_dict()})

    # ========== Ingestion Job handlers ==========

    def start_ingestion_job(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        data_source_id = parts[parts.index("datasources") + 1]
        params = json.loads(self.body) if self.body else {}
        job = self.bedrockagent_backend.start_ingestion_job(
            knowledge_base_id=knowledge_base_id,
            data_source_id=data_source_id,
            client_token=params.get("clientToken"),
            description=params.get("description"),
        )
        return json.dumps({"ingestionJob": job.to_dict()})

    def get_ingestion_job(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        data_source_id = parts[parts.index("datasources") + 1]
        ingestion_job_id = parts[parts.index("ingestionjobs") + 1]
        job = self.bedrockagent_backend.get_ingestion_job(
            knowledge_base_id=knowledge_base_id,
            data_source_id=data_source_id,
            ingestion_job_id=ingestion_job_id,
        )
        return json.dumps({"ingestionJob": job.to_dict()})

    def list_ingestion_jobs(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        data_source_id = parts[parts.index("datasources") + 1]
        params = json.loads(self.body) if self.body else {}
        jobs, next_token = self.bedrockagent_backend.list_ingestion_jobs(
            knowledge_base_id=knowledge_base_id,
            data_source_id=data_source_id,
            max_results=params.get("maxResults"),
            next_token=params.get("nextToken"),
        )
        return json.dumps({"ingestionJobSummaries": [j.dict_summary() for j in jobs], "nextToken": next_token})

    def stop_ingestion_job(self) -> str:
        parts = self.path.split("/")
        knowledge_base_id = parts[parts.index("knowledgebases") + 1]
        data_source_id = parts[parts.index("datasources") + 1]
        ingestion_job_id = parts[parts.index("ingestionjobs") + 1]
        job = self.bedrockagent_backend.stop_ingestion_job(
            knowledge_base_id=knowledge_base_id,
            data_source_id=data_source_id,
            ingestion_job_id=ingestion_job_id,
        )
        return json.dumps({"ingestionJob": job.to_dict()})

    # ========== Flow handlers ==========

    def create_flow(self) -> str:
        params = json.loads(self.body)
        flow = self.bedrockagent_backend.create_flow(
            name=params.get("name"),
            execution_role_arn=params.get("executionRoleArn"),
            client_token=params.get("clientToken"),
            description=params.get("description"),
            customer_encryption_key_arn=params.get("customerEncryptionKeyArn"),
            definition=params.get("definition"),
            tags=params.get("tags"),
        )
        return json.dumps(flow.to_dict())

    def get_flow(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        flow = self.bedrockagent_backend.get_flow(flow_identifier=flow_identifier)
        return json.dumps(flow.to_dict())

    def list_flows(self) -> str:
        params = self._get_params()
        max_results = params.get("maxResults")
        next_token = params.get("nextToken")
        flows, next_token = self.bedrockagent_backend.list_flows(
            max_results=int(max_results) if max_results else None,
            next_token=next_token,
        )
        return json.dumps({"flowSummaries": [f.dict_summary() for f in flows], "nextToken": next_token})

    def delete_flow(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        params = self._get_params()
        flow_id = self.bedrockagent_backend.delete_flow(
            flow_identifier=flow_identifier,
            skip_resource_in_use_check=params.get("skipResourceInUseCheck"),
        )
        return json.dumps({"id": flow_id})

    def update_flow(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        params = json.loads(self.body)
        flow = self.bedrockagent_backend.update_flow(
            flow_identifier=flow_identifier,
            name=params.get("name"),
            execution_role_arn=params.get("executionRoleArn"),
            description=params.get("description"),
            customer_encryption_key_arn=params.get("customerEncryptionKeyArn"),
            definition=params.get("definition"),
        )
        return json.dumps(flow.to_dict())

    def prepare_flow(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        flow = self.bedrockagent_backend.prepare_flow(flow_identifier=flow_identifier)
        return json.dumps(flow.to_dict())

    # ========== Flow Alias handlers ==========

    def create_flow_alias(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        params = json.loads(self.body)
        alias = self.bedrockagent_backend.create_flow_alias(
            flow_identifier=flow_identifier,
            name=params.get("name"),
            description=params.get("description"),
            routing_configuration=params.get("routingConfiguration"),
            tags=params.get("tags"),
        )
        return json.dumps(alias.to_dict())

    def get_flow_alias(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        alias_identifier = parts[parts.index("aliases") + 1]
        alias = self.bedrockagent_backend.get_flow_alias(
            flow_identifier=flow_identifier,
            alias_identifier=alias_identifier,
        )
        return json.dumps(alias.to_dict())

    def list_flow_aliases(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        aliases, next_token = self.bedrockagent_backend.list_flow_aliases(
            flow_identifier=flow_identifier,
            max_results=None,
            next_token=None,
        )
        return json.dumps({"flowAliasSummaries": [a.dict_summary() for a in aliases], "nextToken": next_token})

    def delete_flow_alias(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        alias_identifier = parts[parts.index("aliases") + 1]
        flow_id, alias_id = self.bedrockagent_backend.delete_flow_alias(
            flow_identifier=flow_identifier,
            alias_identifier=alias_identifier,
        )
        return json.dumps({"flowId": flow_id, "id": alias_id})

    def update_flow_alias(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        alias_identifier = parts[parts.index("aliases") + 1]
        params = json.loads(self.body)
        alias = self.bedrockagent_backend.update_flow_alias(
            flow_identifier=flow_identifier,
            alias_identifier=alias_identifier,
            name=params.get("name"),
            description=params.get("description"),
            routing_configuration=params.get("routingConfiguration"),
        )
        return json.dumps(alias.to_dict())

    # ========== Flow Version handlers ==========

    def create_flow_version(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        params = json.loads(self.body) if self.body else {}
        version = self.bedrockagent_backend.create_flow_version(
            flow_identifier=flow_identifier,
            client_token=params.get("clientToken"),
            description=params.get("description"),
        )
        return json.dumps(version.to_dict())

    def get_flow_version(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        flow_version = parts[parts.index("versions") + 1]
        version = self.bedrockagent_backend.get_flow_version(
            flow_identifier=flow_identifier,
            flow_version=flow_version,
        )
        return json.dumps(version.to_dict())

    def list_flow_versions(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        versions, next_token = self.bedrockagent_backend.list_flow_versions(
            flow_identifier=flow_identifier,
            max_results=None,
            next_token=None,
        )
        return json.dumps({"flowVersionSummaries": [v.dict_summary() for v in versions], "nextToken": next_token})

    def delete_flow_version(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        flow_identifier = parts[parts.index("flows") + 1]
        flow_version = parts[parts.index("versions") + 1]
        params = self._get_params()
        flow_id, version = self.bedrockagent_backend.delete_flow_version(
            flow_identifier=flow_identifier,
            flow_version=flow_version,
            skip_resource_in_use_check=params.get("skipResourceInUseCheck"),
        )
        return json.dumps({"id": flow_id, "version": version})

    # ========== Prompt handlers ==========

    def create_prompt(self) -> str:
        params = json.loads(self.body)
        prompt = self.bedrockagent_backend.create_prompt(
            name=params.get("name"),
            client_token=params.get("clientToken"),
            description=params.get("description"),
            customer_encryption_key_arn=params.get("customerEncryptionKeyArn"),
            default_variant=params.get("defaultVariant"),
            variants=params.get("variants"),
            tags=params.get("tags"),
        )
        return json.dumps(prompt.to_dict())

    def get_prompt(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        prompt_identifier = parts[parts.index("prompts") + 1]
        params = self._get_params()
        prompt = self.bedrockagent_backend.get_prompt(
            prompt_identifier=prompt_identifier,
            prompt_version=params.get("promptVersion"),
        )
        return json.dumps(prompt.to_dict())

    def list_prompts(self) -> str:
        params = self._get_params()
        max_results = params.get("maxResults")
        next_token = params.get("nextToken")
        prompts, next_token = self.bedrockagent_backend.list_prompts(
            max_results=int(max_results) if max_results else None,
            next_token=next_token,
        )
        return json.dumps({"promptSummaries": [p.dict_summary() for p in prompts], "nextToken": next_token})

    def delete_prompt(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        prompt_identifier = parts[parts.index("prompts") + 1]
        params = self._get_params()
        prompt_id, prompt_version = self.bedrockagent_backend.delete_prompt(
            prompt_identifier=prompt_identifier,
            prompt_version=params.get("promptVersion"),
        )
        return json.dumps({"id": prompt_id, "version": prompt_version})

    def update_prompt(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        prompt_identifier = parts[parts.index("prompts") + 1]
        params = json.loads(self.body)
        prompt = self.bedrockagent_backend.update_prompt(
            prompt_identifier=prompt_identifier,
            name=params.get("name"),
            description=params.get("description"),
            customer_encryption_key_arn=params.get("customerEncryptionKeyArn"),
            default_variant=params.get("defaultVariant"),
            variants=params.get("variants"),
        )
        return json.dumps(prompt.to_dict())

    def create_prompt_version(self) -> str:
        parts = [p for p in self.path.split("/") if p]
        prompt_identifier = parts[parts.index("prompts") + 1]
        params = json.loads(self.body) if self.body else {}
        version = self.bedrockagent_backend.create_prompt_version(
            prompt_identifier=prompt_identifier,
            client_token=params.get("clientToken"),
            description=params.get("description"),
            tags=params.get("tags"),
        )
        return json.dumps(version.to_dict())

    # ========== Tagging handlers ==========

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tags = params.get("tags")
        self.bedrockagent_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tag_keys = self.querystring.get("tagKeys", [])
        self.bedrockagent_backend.untag_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tags = self.bedrockagent_backend.list_tags_for_resource(
            resource_arn=resource_arn
        )
        return json.dumps({"tags": tags})
