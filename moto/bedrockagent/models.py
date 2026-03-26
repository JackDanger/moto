"""AgentsforBedrockBackend class with methods for supported APIs."""

from typing import Any, Optional

from moto.bedrockagent.exceptions import (
    ConflictException,
    ResourceNotFoundException,
    ValidationException,
)
from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition


class Agent(BaseModel):
    def __init__(
        self,
        agent_name: str,
        agent_resource_role_arn: str,
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        instruction: Optional[str],
        foundation_model: Optional[str],
        description: Optional[str],
        idle_session_ttl_in_seconds: Optional[int],
        customer_encryption_key_arn: Optional[str],
        prompt_override_configuration: Optional[dict[str, Any]],
    ):
        self.agent_name = agent_name
        self.client_token = client_token
        self.instruction = instruction
        self.foundation_model = foundation_model
        self.description = description
        self.idle_session_ttl_in_seconds = idle_session_ttl_in_seconds
        self.agent_resource_role_arn = agent_resource_role_arn
        self.customer_encryption_key_arn = customer_encryption_key_arn
        self.prompt_override_configuration = prompt_override_configuration
        self.region_name = region_name
        self.account_id = account_id
        self.created_at = unix_time()
        self.updated_at = unix_time()
        self.prepared_at = unix_time()
        self.agent_status = "PREPARED"
        self.agent_id = self.agent_name + str(mock_random.uuid4())[:8]
        self.agent_arn = f"arn:{get_partition(self.region_name)}:bedrock:{self.region_name}:{self.account_id}:agent/{self.agent_id}"
        self.agent_version = "DRAFT"
        self.failure_reasons: list[str] = []
        self.recommended_actions: list[str] = ["action"]
        self.aliases: dict[str, "AgentAlias"] = {}
        self.action_groups: dict[str, "AgentActionGroup"] = {}
        self.agent_knowledge_bases: dict[str, "AgentKnowledgeBase"] = {}

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "agentId": self.agent_id,
            "agentName": self.agent_name,
            "agentArn": self.agent_arn,
            "agentVersion": self.agent_version,
            "clientToken": self.client_token,
            "instruction": self.instruction,
            "agentStatus": self.agent_status,
            "foundationModel": self.foundation_model,
            "description": self.description,
            "idleSessionTTLInSeconds": self.idle_session_ttl_in_seconds,
            "agentResourceRoleArn": self.agent_resource_role_arn,
            "customerEncryptionKeyArn": self.customer_encryption_key_arn,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "preparedAt": self.prepared_at,
            "failureReasons": self.failure_reasons,
            "recommendedActions": self.recommended_actions,
            "promptOverrideConfiguration": self.prompt_override_configuration,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "agentId": self.agent_id,
            "agentName": self.agent_name,
            "agentStatus": self.agent_status,
            "description": self.description,
            "updatedAt": self.updated_at,
            "latestAgentVersion": self.agent_version,
        }
        return {k: v for k, v in dct.items() if v is not None}


class AgentAlias(BaseModel):
    def __init__(
        self,
        agent_id: str,
        agent_alias_name: str,
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        description: Optional[str],
        routing_configuration: Optional[list[dict[str, Any]]],
        tags: Optional[dict[str, str]],
    ):
        self.agent_id = agent_id
        self.agent_alias_name = agent_alias_name
        self.region_name = region_name
        self.account_id = account_id
        self.client_token = client_token
        self.description = description
        self.routing_configuration = routing_configuration or []
        self.tags = tags or {}
        self.agent_alias_id = str(mock_random.uuid4()).replace("-", "")[:10].upper()
        self.agent_alias_arn = f"arn:{get_partition(region_name)}:bedrock:{region_name}:{account_id}:agent-alias/{agent_id}/{self.agent_alias_id}"
        self.created_at = unix_time()
        self.updated_at = unix_time()
        self.agent_alias_status = "PREPARED"

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "agentId": self.agent_id,
            "agentAliasId": self.agent_alias_id,
            "agentAliasName": self.agent_alias_name,
            "agentAliasArn": self.agent_alias_arn,
            "agentAliasStatus": self.agent_alias_status,
            "clientToken": self.client_token,
            "description": self.description,
            "routingConfiguration": self.routing_configuration,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "agentId": self.agent_id,
            "agentAliasId": self.agent_alias_id,
            "agentAliasName": self.agent_alias_name,
            "agentAliasStatus": self.agent_alias_status,
            "description": self.description,
            "routingConfiguration": self.routing_configuration,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class AgentActionGroup(BaseModel):
    def __init__(
        self,
        agent_id: str,
        agent_version: str,
        action_group_name: str,
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        description: Optional[str],
        parent_action_group_signature: Optional[str],
        action_group_executor: Optional[dict[str, Any]],
        api_schema: Optional[dict[str, Any]],
        function_schema: Optional[dict[str, Any]],
        action_group_state: Optional[str],
    ):
        self.agent_id = agent_id
        self.agent_version = agent_version
        self.action_group_name = action_group_name
        self.region_name = region_name
        self.account_id = account_id
        self.client_token = client_token
        self.description = description
        self.parent_action_group_signature = parent_action_group_signature
        self.action_group_executor = action_group_executor
        self.api_schema = api_schema
        self.function_schema = function_schema
        self.action_group_state = action_group_state or "ENABLED"
        self.action_group_id = str(mock_random.uuid4())[:8]
        self.created_at = unix_time()
        self.updated_at = unix_time()

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "agentId": self.agent_id,
            "agentVersion": self.agent_version,
            "actionGroupId": self.action_group_id,
            "actionGroupName": self.action_group_name,
            "actionGroupState": self.action_group_state,
            "clientToken": self.client_token,
            "description": self.description,
            "parentActionGroupSignature": self.parent_action_group_signature,
            "actionGroupExecutor": self.action_group_executor,
            "apiSchema": self.api_schema,
            "functionSchema": self.function_schema,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "actionGroupId": self.action_group_id,
            "actionGroupName": self.action_group_name,
            "actionGroupState": self.action_group_state,
            "description": self.description,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class AgentKnowledgeBase(BaseModel):
    def __init__(
        self,
        agent_id: str,
        agent_version: str,
        knowledge_base_id: str,
        knowledge_base_state: str,
        description: str,
    ):
        self.agent_id = agent_id
        self.agent_version = agent_version
        self.knowledge_base_id = knowledge_base_id
        self.knowledge_base_state = knowledge_base_state or "ENABLED"
        self.description = description
        self.created_at = unix_time()
        self.updated_at = unix_time()

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "agentId": self.agent_id,
            "agentVersion": self.agent_version,
            "knowledgeBaseId": self.knowledge_base_id,
            "knowledgeBaseState": self.knowledge_base_state,
            "description": self.description,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        return self.to_dict()


class KnowledgeBase(BaseModel):
    def __init__(
        self,
        name: str,
        role_arn: str,
        region_name: str,
        account_id: str,
        knowledge_base_configuration: dict[str, Any],
        storage_configuration: dict[str, Any],
        client_token: Optional[str],
        description: Optional[str],
    ):
        self.client_token = client_token
        self.name = name
        self.description = description
        self.role_arn = role_arn
        if knowledge_base_configuration["type"] != "VECTOR":
            raise ValidationException(
                "Validation error detected: "
                f"Value '{knowledge_base_configuration['type']}' at 'knowledgeBaseConfiguration' failed to satisfy constraint: "
                "Member must contain 'type' as 'VECTOR'"
            )
        self.knowledge_base_configuration = knowledge_base_configuration
        if storage_configuration["type"] not in [
            "OPENSEARCH_SERVERLESS",
            "PINECONE",
            "REDIS_ENTERPRISE_CLOUD",
            "RDS",
        ]:
            raise ValidationException(
                "Validation error detected: "
                f"Value '{storage_configuration['type']}' at 'storageConfiguration' failed to satisfy constraint: "
                "Member 'type' must be one of: OPENSEARCH_SERVERLESS | PINECONE | REDIS_ENTERPRISE_CLOUD | RDS"
            )
        self.storage_configuration = storage_configuration
        self.region_name = region_name
        self.account_id = account_id
        self.knowledge_base_id = self.name + str(mock_random.uuid4())[:8]
        self.knowledge_base_arn = f"arn:{get_partition(self.region_name)}:bedrock:{self.region_name}:{self.account_id}:knowledge-base/{self.knowledge_base_id}"
        self.created_at = unix_time()
        self.updated_at = unix_time()
        self.status = "Active"
        self.failure_reasons: list[str] = []
        self.data_sources: dict[str, "DataSource"] = {}

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "knowledgeBaseId": self.knowledge_base_id,
            "name": self.name,
            "knowledgeBaseArn": self.knowledge_base_arn,
            "description": self.description,
            "roleArn": self.role_arn,
            "knowledgeBaseConfiguration": self.knowledge_base_configuration,
            "storageConfiguration": self.storage_configuration,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "failureReasons": self.failure_reasons,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "knowledgeBaseId": self.knowledge_base_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class DataSource(BaseModel):
    def __init__(
        self,
        knowledge_base_id: str,
        name: str,
        data_source_configuration: dict[str, Any],
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        description: Optional[str],
        server_side_encryption_configuration: Optional[dict[str, Any]],
        vector_ingestion_configuration: Optional[dict[str, Any]],
    ):
        self.knowledge_base_id = knowledge_base_id
        self.name = name
        self.data_source_configuration = data_source_configuration
        self.region_name = region_name
        self.account_id = account_id
        self.client_token = client_token
        self.description = description
        self.server_side_encryption_configuration = server_side_encryption_configuration
        self.vector_ingestion_configuration = vector_ingestion_configuration
        self.data_source_id = str(mock_random.uuid4())[:8]
        self.created_at = unix_time()
        self.updated_at = unix_time()
        self.status = "AVAILABLE"
        self.ingestion_jobs: dict[str, "IngestionJob"] = {}

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "knowledgeBaseId": self.knowledge_base_id,
            "dataSourceId": self.data_source_id,
            "name": self.name,
            "description": self.description,
            "dataSourceConfiguration": self.data_source_configuration,
            "serverSideEncryptionConfiguration": self.server_side_encryption_configuration,
            "vectorIngestionConfiguration": self.vector_ingestion_configuration,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "knowledgeBaseId": self.knowledge_base_id,
            "dataSourceId": self.data_source_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class IngestionJob(BaseModel):
    def __init__(
        self,
        knowledge_base_id: str,
        data_source_id: str,
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        description: Optional[str],
    ):
        self.knowledge_base_id = knowledge_base_id
        self.data_source_id = data_source_id
        self.region_name = region_name
        self.account_id = account_id
        self.client_token = client_token
        self.description = description
        self.ingestion_job_id = str(mock_random.uuid4())
        self.status = "COMPLETE"
        self.started_at = unix_time()
        self.updated_at = unix_time()
        self.statistics = {
            "numberOfDocumentsScanned": 0,
            "numberOfNewDocumentsIndexed": 0,
            "numberOfModifiedDocumentsIndexed": 0,
            "numberOfDocumentsDeleted": 0,
            "numberOfDocumentsFailed": 0,
        }

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "knowledgeBaseId": self.knowledge_base_id,
            "dataSourceId": self.data_source_id,
            "ingestionJobId": self.ingestion_job_id,
            "description": self.description,
            "status": self.status,
            "statistics": self.statistics,
            "startedAt": self.started_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        return self.to_dict()


class Flow(BaseModel):
    def __init__(
        self,
        name: str,
        execution_role_arn: str,
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        description: Optional[str],
        customer_encryption_key_arn: Optional[str],
        definition: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ):
        self.name = name
        self.execution_role_arn = execution_role_arn
        self.region_name = region_name
        self.account_id = account_id
        self.client_token = client_token
        self.description = description
        self.customer_encryption_key_arn = customer_encryption_key_arn
        self.definition = definition
        self.tags = tags or {}
        self.id = str(mock_random.uuid4())[:8]
        self.arn = f"arn:{get_partition(region_name)}:bedrock:{region_name}:{account_id}:flow/{self.id}"
        self.created_at = unix_time()
        self.updated_at = unix_time()
        self.status = "NOT_PREPARED"
        self.version = "DRAFT"
        self.aliases: dict[str, "FlowAlias"] = {}
        self.versions: dict[str, "FlowVersion"] = {}

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "name": self.name,
            "description": self.description,
            "executionRoleArn": self.execution_role_arn,
            "customerEncryptionKeyArn": self.customer_encryption_key_arn,
            "definition": self.definition,
            "status": self.status,
            "version": self.version,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "version": self.version,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class FlowAlias(BaseModel):
    def __init__(
        self,
        flow_id: str,
        name: str,
        region_name: str,
        account_id: str,
        description: Optional[str],
        routing_configuration: Optional[list[dict[str, Any]]],
        tags: Optional[dict[str, str]],
    ):
        self.flow_id = flow_id
        self.name = name
        self.region_name = region_name
        self.account_id = account_id
        self.description = description
        self.routing_configuration = routing_configuration or []
        self.tags = tags or {}
        self.id = str(mock_random.uuid4())[:8]
        self.arn = f"arn:{get_partition(region_name)}:bedrock:{region_name}:{account_id}:flow/{flow_id}/alias/{self.id}"
        self.created_at = unix_time()
        self.updated_at = unix_time()

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "flowId": self.flow_id,
            "name": self.name,
            "description": self.description,
            "routingConfiguration": self.routing_configuration,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "flowId": self.flow_id,
            "name": self.name,
            "description": self.description,
            "routingConfiguration": self.routing_configuration,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class FlowVersion(BaseModel):
    def __init__(
        self,
        flow_id: str,
        flow_arn: str,
        flow_name: str,
        flow_status: str,
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        description: Optional[str],
        definition: Optional[dict[str, Any]],
        execution_role_arn: str,
    ):
        self.flow_id = flow_id
        self.flow_arn = flow_arn
        self.flow_name = flow_name
        self.flow_status = flow_status
        self.region_name = region_name
        self.account_id = account_id
        self.client_token = client_token
        self.description = description
        self.definition = definition
        self.execution_role_arn = execution_role_arn
        self.version = str(int(unix_time()))[-4:]
        self.created_at = unix_time()
        self.status = "Available"

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "id": self.flow_id,
            "arn": self.flow_arn,
            "name": self.flow_name,
            "version": self.version,
            "description": self.description,
            "definition": self.definition,
            "executionRoleArn": self.execution_role_arn,
            "status": self.status,
            "createdAt": self.created_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "id": self.flow_id,
            "arn": self.flow_arn,
            "name": self.flow_name,
            "version": self.version,
            "description": self.description,
            "status": self.status,
            "createdAt": self.created_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class Prompt(BaseModel):
    def __init__(
        self,
        name: str,
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        description: Optional[str],
        customer_encryption_key_arn: Optional[str],
        default_variant: Optional[str],
        variants: Optional[list[dict[str, Any]]],
        tags: Optional[dict[str, str]],
    ):
        self.name = name
        self.region_name = region_name
        self.account_id = account_id
        self.client_token = client_token
        self.description = description
        self.customer_encryption_key_arn = customer_encryption_key_arn
        self.default_variant = default_variant
        self.variants = variants or []
        self.tags = tags or {}
        self.id = str(mock_random.uuid4())[:8]
        self.arn = f"arn:{get_partition(region_name)}:bedrock:{region_name}:{account_id}:prompt/{self.id}"
        self.created_at = unix_time()
        self.updated_at = unix_time()
        self.version = "DRAFT"
        self.versions: dict[str, "PromptVersion"] = {}

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "name": self.name,
            "description": self.description,
            "customerEncryptionKeyArn": self.customer_encryption_key_arn,
            "defaultVariant": self.default_variant,
            "variants": self.variants,
            "version": self.version,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class PromptVersion(BaseModel):
    def __init__(
        self,
        prompt_id: str,
        prompt_arn: str,
        prompt_name: str,
        region_name: str,
        account_id: str,
        client_token: Optional[str],
        description: Optional[str],
        customer_encryption_key_arn: Optional[str],
        default_variant: Optional[str],
        variants: Optional[list[dict[str, Any]]],
    ):
        self.prompt_id = prompt_id
        self.prompt_arn = prompt_arn
        self.prompt_name = prompt_name
        self.region_name = region_name
        self.account_id = account_id
        self.client_token = client_token
        self.description = description
        self.customer_encryption_key_arn = customer_encryption_key_arn
        self.default_variant = default_variant
        self.variants = variants or []
        self.id = prompt_id
        self.arn = prompt_arn
        self.version = str(int(unix_time()))[-4:]
        self.created_at = unix_time()
        self.updated_at = unix_time()

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "name": self.prompt_name,
            "description": self.description,
            "customerEncryptionKeyArn": self.customer_encryption_key_arn,
            "defaultVariant": self.default_variant,
            "variants": self.variants,
            "version": self.version,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}

    def dict_summary(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "name": self.prompt_name,
            "description": self.description,
            "version": self.version,
            "updatedAt": self.updated_at,
        }
        return {k: v for k, v in dct.items() if v is not None}


class AgentsforBedrockBackend(BaseBackend):
    """Implementation of AgentsforBedrock APIs."""

    PAGINATION_MODEL = {
        "list_agents": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "agent_id",
        },
        "list_knowledge_bases": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "knowledge_base_id",
        },
        "list_flows": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "id",
        },
        "list_prompts": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "id",
        },
    }

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.agents: dict[str, Agent] = {}
        self.knowledge_bases: dict[str, KnowledgeBase] = {}
        self.flows: dict[str, Flow] = {}
        self.prompts: dict[str, Prompt] = {}
        self.tagger = TaggingService()

    def _list_arns(self) -> list[str]:
        return (
            [agent.agent_arn for agent in self.agents.values()]
            + [kb.knowledge_base_arn for kb in self.knowledge_bases.values()]
            + [flow.arn for flow in self.flows.values()]
            + [prompt.arn for prompt in self.prompts.values()]
        )

    # ========== Agent operations ==========

    def create_agent(
        self,
        agent_name: str,
        agent_resource_role_arn: str,
        client_token: Optional[str],
        instruction: Optional[str],
        foundation_model: Optional[str],
        description: Optional[str],
        idle_session_ttl_in_seconds: Optional[int],
        customer_encryption_key_arn: Optional[str],
        tags: Optional[dict[str, str]],
        prompt_override_configuration: Optional[dict[str, Any]],
    ) -> Agent:
        agent = Agent(
            agent_name,
            agent_resource_role_arn,
            self.region_name,
            self.account_id,
            client_token,
            instruction,
            foundation_model,
            description,
            idle_session_ttl_in_seconds,
            customer_encryption_key_arn,
            prompt_override_configuration,
        )
        self.agents[agent.agent_id] = agent
        if tags:
            self.tag_resource(agent.agent_arn, tags)
        return agent

    def get_agent(self, agent_id: str) -> Agent:
        if agent_id not in self.agents:
            raise ResourceNotFoundException(f"Agent {agent_id} not found")
        return self.agents[agent_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_agents(self) -> list[Agent]:
        return list(self.agents.values())

    def delete_agent(
        self, agent_id: str, skip_resource_in_use_check: Optional[bool]
    ) -> tuple[str, str]:
        if agent_id in self.agents:
            if (
                skip_resource_in_use_check
                or self.agents[agent_id].agent_status == "PREPARED"
            ):
                self.agents[agent_id].agent_status = "DELETING"
                agent_status = self.agents[agent_id].agent_status
                del self.agents[agent_id]
            else:
                raise ConflictException(f"Agent {agent_id} is in use")
        else:
            raise ResourceNotFoundException(f"Agent {agent_id} not found")
        return agent_id, agent_status

    def update_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_resource_role_arn: str,
        foundation_model: Optional[str],
        instruction: Optional[str],
        description: Optional[str],
        idle_session_ttl_in_seconds: Optional[int],
        customer_encryption_key_arn: Optional[str],
        prompt_override_configuration: Optional[dict[str, Any]],
    ) -> Agent:
        agent = self.get_agent(agent_id)
        agent.agent_name = agent_name
        agent.agent_resource_role_arn = agent_resource_role_arn
        if foundation_model is not None:
            agent.foundation_model = foundation_model
        if instruction is not None:
            agent.instruction = instruction
        if description is not None:
            agent.description = description
        if idle_session_ttl_in_seconds is not None:
            agent.idle_session_ttl_in_seconds = idle_session_ttl_in_seconds
        if customer_encryption_key_arn is not None:
            agent.customer_encryption_key_arn = customer_encryption_key_arn
        if prompt_override_configuration is not None:
            agent.prompt_override_configuration = prompt_override_configuration
        agent.updated_at = unix_time()
        return agent

    def prepare_agent(self, agent_id: str) -> tuple[str, str, str, float]:
        agent = self.get_agent(agent_id)
        agent.agent_status = "PREPARED"
        agent.prepared_at = unix_time()
        return agent_id, agent.agent_arn, agent.agent_version, agent.prepared_at

    def get_agent_version(self, agent_id: str, agent_version: str) -> dict[str, Any]:
        agent = self.get_agent(agent_id)
        return {
            "agentId": agent.agent_id,
            "agentName": agent.agent_name,
            "agentArn": agent.agent_arn,
            "version": agent_version,
            "agentStatus": agent.agent_status,
            "foundationModel": agent.foundation_model,
            "description": agent.description,
            "instruction": agent.instruction,
            "idleSessionTTLInSeconds": agent.idle_session_ttl_in_seconds,
            "agentResourceRoleArn": agent.agent_resource_role_arn,
            "createdAt": agent.created_at,
            "updatedAt": agent.updated_at,
        }

    def list_agent_versions(
        self, agent_id: str, max_results: Optional[int], next_token: Optional[str]
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        agent = self.get_agent(agent_id)
        version_summary = {
            "agentId": agent.agent_id,
            "agentName": agent.agent_name,
            "agentStatus": agent.agent_status,
            "agentVersion": agent.agent_version,
            "description": agent.description,
            "updatedAt": agent.updated_at,
        }
        return [version_summary], None

    def delete_agent_version(
        self,
        agent_id: str,
        agent_version: str,
        skip_resource_in_use_check: Optional[bool],
    ) -> tuple[str, str, str]:
        agent = self.get_agent(agent_id)
        return agent.agent_id, agent_version, "DELETING"

    # ========== Agent Alias operations ==========

    def create_agent_alias(
        self,
        agent_id: str,
        agent_alias_name: str,
        client_token: Optional[str],
        description: Optional[str],
        routing_configuration: Optional[list[dict[str, Any]]],
        tags: Optional[dict[str, str]],
    ) -> AgentAlias:
        agent = self.get_agent(agent_id)
        alias = AgentAlias(
            agent_id=agent_id,
            agent_alias_name=agent_alias_name,
            region_name=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
            description=description,
            routing_configuration=routing_configuration,
            tags=tags,
        )
        agent.aliases[alias.agent_alias_id] = alias
        return alias

    def get_agent_alias(self, agent_id: str, agent_alias_id: str) -> AgentAlias:
        agent = self.get_agent(agent_id)
        if agent_alias_id not in agent.aliases:
            raise ResourceNotFoundException(
                f"Agent alias {agent_alias_id} not found for agent {agent_id}"
            )
        return agent.aliases[agent_alias_id]

    def list_agent_aliases(
        self,
        agent_id: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[AgentAlias], Optional[str]]:
        agent = self.get_agent(agent_id)
        return list(agent.aliases.values()), None

    def delete_agent_alias(
        self, agent_id: str, agent_alias_id: str
    ) -> tuple[str, str, str]:
        agent = self.get_agent(agent_id)
        if agent_alias_id not in agent.aliases:
            raise ResourceNotFoundException(
                f"Agent alias {agent_alias_id} not found for agent {agent_id}"
            )
        agent.aliases[agent_alias_id].agent_alias_status = "DELETING"
        status = agent.aliases[agent_alias_id].agent_alias_status
        del agent.aliases[agent_alias_id]
        return agent_id, agent_alias_id, status

    def update_agent_alias(
        self,
        agent_id: str,
        agent_alias_id: str,
        agent_alias_name: str,
        description: Optional[str],
        routing_configuration: Optional[list[dict[str, Any]]],
    ) -> AgentAlias:
        alias = self.get_agent_alias(agent_id, agent_alias_id)
        alias.agent_alias_name = agent_alias_name
        if description is not None:
            alias.description = description
        if routing_configuration is not None:
            alias.routing_configuration = routing_configuration
        alias.updated_at = unix_time()
        return alias

    # ========== Agent Action Group operations ==========

    def create_agent_action_group(
        self,
        agent_id: str,
        agent_version: str,
        action_group_name: str,
        client_token: Optional[str],
        description: Optional[str],
        parent_action_group_signature: Optional[str],
        action_group_executor: Optional[dict[str, Any]],
        api_schema: Optional[dict[str, Any]],
        function_schema: Optional[dict[str, Any]],
        action_group_state: Optional[str],
    ) -> AgentActionGroup:
        agent = self.get_agent(agent_id)
        action_group = AgentActionGroup(
            agent_id=agent_id,
            agent_version=agent_version,
            action_group_name=action_group_name,
            region_name=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
            description=description,
            parent_action_group_signature=parent_action_group_signature,
            action_group_executor=action_group_executor,
            api_schema=api_schema,
            function_schema=function_schema,
            action_group_state=action_group_state,
        )
        agent.action_groups[action_group.action_group_id] = action_group
        return action_group

    def get_agent_action_group(
        self, agent_id: str, agent_version: str, action_group_id: str
    ) -> AgentActionGroup:
        agent = self.get_agent(agent_id)
        if action_group_id not in agent.action_groups:
            raise ResourceNotFoundException(
                f"Action group {action_group_id} not found for agent {agent_id}"
            )
        return agent.action_groups[action_group_id]

    def list_agent_action_groups(
        self,
        agent_id: str,
        agent_version: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[AgentActionGroup], Optional[str]]:
        agent = self.get_agent(agent_id)
        groups = [
            g for g in agent.action_groups.values() if g.agent_version == agent_version
        ]
        return groups, None

    def delete_agent_action_group(
        self,
        agent_id: str,
        agent_version: str,
        action_group_id: str,
        skip_resource_in_use_check: Optional[bool],
    ) -> None:
        agent = self.get_agent(agent_id)
        if action_group_id not in agent.action_groups:
            raise ResourceNotFoundException(
                f"Action group {action_group_id} not found for agent {agent_id}"
            )
        del agent.action_groups[action_group_id]

    def update_agent_action_group(
        self,
        agent_id: str,
        agent_version: str,
        action_group_id: str,
        action_group_name: str,
        description: Optional[str],
        parent_action_group_signature: Optional[str],
        action_group_executor: Optional[dict[str, Any]],
        api_schema: Optional[dict[str, Any]],
        function_schema: Optional[dict[str, Any]],
        action_group_state: Optional[str],
    ) -> AgentActionGroup:
        ag = self.get_agent_action_group(agent_id, agent_version, action_group_id)
        ag.action_group_name = action_group_name
        if description is not None:
            ag.description = description
        if parent_action_group_signature is not None:
            ag.parent_action_group_signature = parent_action_group_signature
        if action_group_executor is not None:
            ag.action_group_executor = action_group_executor
        if api_schema is not None:
            ag.api_schema = api_schema
        if function_schema is not None:
            ag.function_schema = function_schema
        if action_group_state is not None:
            ag.action_group_state = action_group_state
        ag.updated_at = unix_time()
        return ag

    # ========== Agent Knowledge Base operations ==========

    def associate_agent_knowledge_base(
        self,
        agent_id: str,
        agent_version: str,
        knowledge_base_id: str,
        knowledge_base_state: str,
        description: str,
    ) -> AgentKnowledgeBase:
        agent = self.get_agent(agent_id)
        akb = AgentKnowledgeBase(
            agent_id=agent_id,
            agent_version=agent_version,
            knowledge_base_id=knowledge_base_id,
            knowledge_base_state=knowledge_base_state,
            description=description,
        )
        agent.agent_knowledge_bases[knowledge_base_id] = akb
        return akb

    def get_agent_knowledge_base(
        self, agent_id: str, agent_version: str, knowledge_base_id: str
    ) -> AgentKnowledgeBase:
        agent = self.get_agent(agent_id)
        if knowledge_base_id not in agent.agent_knowledge_bases:
            raise ResourceNotFoundException(
                f"Knowledge base association {knowledge_base_id} not found for agent {agent_id}"
            )
        return agent.agent_knowledge_bases[knowledge_base_id]

    def list_agent_knowledge_bases(
        self,
        agent_id: str,
        agent_version: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[AgentKnowledgeBase], Optional[str]]:
        agent = self.get_agent(agent_id)
        bases = [
            akb
            for akb in agent.agent_knowledge_bases.values()
            if akb.agent_version == agent_version
        ]
        return bases, None

    def disassociate_agent_knowledge_base(
        self, agent_id: str, agent_version: str, knowledge_base_id: str
    ) -> None:
        agent = self.get_agent(agent_id)
        if knowledge_base_id not in agent.agent_knowledge_bases:
            raise ResourceNotFoundException(
                f"Knowledge base association {knowledge_base_id} not found for agent {agent_id}"
            )
        del agent.agent_knowledge_bases[knowledge_base_id]

    def update_agent_knowledge_base(
        self,
        agent_id: str,
        agent_version: str,
        knowledge_base_id: str,
        knowledge_base_state: Optional[str],
        description: Optional[str],
    ) -> AgentKnowledgeBase:
        akb = self.get_agent_knowledge_base(agent_id, agent_version, knowledge_base_id)
        if knowledge_base_state is not None:
            akb.knowledge_base_state = knowledge_base_state
        if description is not None:
            akb.description = description
        akb.updated_at = unix_time()
        return akb

    # ========== Knowledge Base operations ==========

    def create_knowledge_base(
        self,
        name: str,
        role_arn: str,
        knowledge_base_configuration: dict[str, Any],
        storage_configuration: dict[str, Any],
        client_token: Optional[str],
        description: Optional[str],
        tags: Optional[dict[str, str]],
    ) -> KnowledgeBase:
        knowledge_base = KnowledgeBase(
            name,
            role_arn,
            self.region_name,
            self.account_id,
            knowledge_base_configuration,
            storage_configuration,
            client_token,
            description,
        )
        self.knowledge_bases[knowledge_base.knowledge_base_id] = knowledge_base
        if tags:
            self.tag_resource(knowledge_base.knowledge_base_arn, tags)
        return knowledge_base

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_knowledge_bases(self) -> list[KnowledgeBase]:
        return list(self.knowledge_bases.values())

    def delete_knowledge_base(self, knowledge_base_id: str) -> tuple[str, str]:
        if knowledge_base_id in self.knowledge_bases:
            self.knowledge_bases[knowledge_base_id].status = "DELETING"
            knowledge_base_status = self.knowledge_bases[knowledge_base_id].status
            del self.knowledge_bases[knowledge_base_id]
        else:
            raise ResourceNotFoundException(
                f"Knowledge base {knowledge_base_id} not found"
            )
        return knowledge_base_id, knowledge_base_status

    def get_knowledge_base(self, knowledge_base_id: str) -> KnowledgeBase:
        if knowledge_base_id not in self.knowledge_bases:
            raise ResourceNotFoundException(
                f"Knowledge base {knowledge_base_id} not found"
            )
        return self.knowledge_bases[knowledge_base_id]

    def update_knowledge_base(
        self,
        knowledge_base_id: str,
        name: str,
        role_arn: str,
        knowledge_base_configuration: dict[str, Any],
        storage_configuration: dict[str, Any],
        description: Optional[str],
    ) -> KnowledgeBase:
        kb = self.get_knowledge_base(knowledge_base_id)
        kb.name = name
        kb.role_arn = role_arn
        kb.knowledge_base_configuration = knowledge_base_configuration
        kb.storage_configuration = storage_configuration
        if description is not None:
            kb.description = description
        kb.updated_at = unix_time()
        return kb

    # ========== Data Source operations ==========

    def create_data_source(
        self,
        knowledge_base_id: str,
        name: str,
        data_source_configuration: dict[str, Any],
        client_token: Optional[str],
        description: Optional[str],
        server_side_encryption_configuration: Optional[dict[str, Any]],
        vector_ingestion_configuration: Optional[dict[str, Any]],
    ) -> DataSource:
        kb = self.get_knowledge_base(knowledge_base_id)
        ds = DataSource(
            knowledge_base_id=knowledge_base_id,
            name=name,
            data_source_configuration=data_source_configuration,
            region_name=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
            description=description,
            server_side_encryption_configuration=server_side_encryption_configuration,
            vector_ingestion_configuration=vector_ingestion_configuration,
        )
        kb.data_sources[ds.data_source_id] = ds
        return ds

    def get_data_source(
        self, knowledge_base_id: str, data_source_id: str
    ) -> DataSource:
        kb = self.get_knowledge_base(knowledge_base_id)
        if data_source_id not in kb.data_sources:
            raise ResourceNotFoundException(
                f"Data source {data_source_id} not found for knowledge base {knowledge_base_id}"
            )
        return kb.data_sources[data_source_id]

    def list_data_sources(
        self,
        knowledge_base_id: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[DataSource], Optional[str]]:
        kb = self.get_knowledge_base(knowledge_base_id)
        return list(kb.data_sources.values()), None

    def delete_data_source(
        self, knowledge_base_id: str, data_source_id: str
    ) -> tuple[str, str, str]:
        kb = self.get_knowledge_base(knowledge_base_id)
        if data_source_id not in kb.data_sources:
            raise ResourceNotFoundException(
                f"Data source {data_source_id} not found for knowledge base {knowledge_base_id}"
            )
        del kb.data_sources[data_source_id]
        return knowledge_base_id, data_source_id, "DELETING"

    def update_data_source(
        self,
        knowledge_base_id: str,
        data_source_id: str,
        name: str,
        data_source_configuration: dict[str, Any],
        description: Optional[str],
        server_side_encryption_configuration: Optional[dict[str, Any]],
        vector_ingestion_configuration: Optional[dict[str, Any]],
    ) -> DataSource:
        ds = self.get_data_source(knowledge_base_id, data_source_id)
        ds.name = name
        ds.data_source_configuration = data_source_configuration
        if description is not None:
            ds.description = description
        if server_side_encryption_configuration is not None:
            ds.server_side_encryption_configuration = server_side_encryption_configuration
        if vector_ingestion_configuration is not None:
            ds.vector_ingestion_configuration = vector_ingestion_configuration
        ds.updated_at = unix_time()
        return ds

    # ========== Ingestion Job operations ==========

    def start_ingestion_job(
        self,
        knowledge_base_id: str,
        data_source_id: str,
        client_token: Optional[str],
        description: Optional[str],
    ) -> IngestionJob:
        ds = self.get_data_source(knowledge_base_id, data_source_id)
        job = IngestionJob(
            knowledge_base_id=knowledge_base_id,
            data_source_id=data_source_id,
            region_name=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
            description=description,
        )
        ds.ingestion_jobs[job.ingestion_job_id] = job
        return job

    def get_ingestion_job(
        self,
        knowledge_base_id: str,
        data_source_id: str,
        ingestion_job_id: str,
    ) -> IngestionJob:
        ds = self.get_data_source(knowledge_base_id, data_source_id)
        if ingestion_job_id not in ds.ingestion_jobs:
            raise ResourceNotFoundException(
                f"Ingestion job {ingestion_job_id} not found"
            )
        return ds.ingestion_jobs[ingestion_job_id]

    def list_ingestion_jobs(
        self,
        knowledge_base_id: str,
        data_source_id: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[IngestionJob], Optional[str]]:
        ds = self.get_data_source(knowledge_base_id, data_source_id)
        return list(ds.ingestion_jobs.values()), None

    def stop_ingestion_job(
        self,
        knowledge_base_id: str,
        data_source_id: str,
        ingestion_job_id: str,
    ) -> IngestionJob:
        job = self.get_ingestion_job(knowledge_base_id, data_source_id, ingestion_job_id)
        job.status = "STOPPED"
        return job

    # ========== Flow operations ==========

    def create_flow(
        self,
        name: str,
        execution_role_arn: str,
        client_token: Optional[str],
        description: Optional[str],
        customer_encryption_key_arn: Optional[str],
        definition: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> Flow:
        flow = Flow(
            name=name,
            execution_role_arn=execution_role_arn,
            region_name=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
            description=description,
            customer_encryption_key_arn=customer_encryption_key_arn,
            definition=definition,
            tags=tags,
        )
        self.flows[flow.id] = flow
        return flow

    def get_flow(self, flow_identifier: str) -> Flow:
        if flow_identifier not in self.flows:
            raise ResourceNotFoundException(f"Flow {flow_identifier} not found")
        return self.flows[flow_identifier]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_flows(self) -> list[Flow]:
        return list(self.flows.values())

    def delete_flow(
        self, flow_identifier: str, skip_resource_in_use_check: Optional[bool]
    ) -> str:
        if flow_identifier not in self.flows:
            raise ResourceNotFoundException(f"Flow {flow_identifier} not found")
        del self.flows[flow_identifier]
        return flow_identifier

    def update_flow(
        self,
        flow_identifier: str,
        name: str,
        execution_role_arn: str,
        description: Optional[str],
        customer_encryption_key_arn: Optional[str],
        definition: Optional[dict[str, Any]],
    ) -> Flow:
        flow = self.get_flow(flow_identifier)
        flow.name = name
        flow.execution_role_arn = execution_role_arn
        if description is not None:
            flow.description = description
        if customer_encryption_key_arn is not None:
            flow.customer_encryption_key_arn = customer_encryption_key_arn
        if definition is not None:
            flow.definition = definition
        flow.updated_at = unix_time()
        return flow

    def prepare_flow(self, flow_identifier: str) -> Flow:
        flow = self.get_flow(flow_identifier)
        flow.status = "PREPARED"
        return flow

    # ========== Flow Alias operations ==========

    def create_flow_alias(
        self,
        flow_identifier: str,
        name: str,
        description: Optional[str],
        routing_configuration: Optional[list[dict[str, Any]]],
        tags: Optional[dict[str, str]],
    ) -> FlowAlias:
        flow = self.get_flow(flow_identifier)
        alias = FlowAlias(
            flow_id=flow_identifier,
            name=name,
            region_name=self.region_name,
            account_id=self.account_id,
            description=description,
            routing_configuration=routing_configuration,
            tags=tags,
        )
        flow.aliases[alias.id] = alias
        return alias

    def get_flow_alias(self, flow_identifier: str, alias_identifier: str) -> FlowAlias:
        flow = self.get_flow(flow_identifier)
        if alias_identifier not in flow.aliases:
            raise ResourceNotFoundException(
                f"Flow alias {alias_identifier} not found for flow {flow_identifier}"
            )
        return flow.aliases[alias_identifier]

    def list_flow_aliases(
        self,
        flow_identifier: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[FlowAlias], Optional[str]]:
        flow = self.get_flow(flow_identifier)
        return list(flow.aliases.values()), None

    def delete_flow_alias(
        self, flow_identifier: str, alias_identifier: str
    ) -> tuple[str, str]:
        flow = self.get_flow(flow_identifier)
        if alias_identifier not in flow.aliases:
            raise ResourceNotFoundException(
                f"Flow alias {alias_identifier} not found for flow {flow_identifier}"
            )
        del flow.aliases[alias_identifier]
        return flow_identifier, alias_identifier

    def update_flow_alias(
        self,
        flow_identifier: str,
        alias_identifier: str,
        name: str,
        description: Optional[str],
        routing_configuration: Optional[list[dict[str, Any]]],
    ) -> FlowAlias:
        alias = self.get_flow_alias(flow_identifier, alias_identifier)
        alias.name = name
        if description is not None:
            alias.description = description
        if routing_configuration is not None:
            alias.routing_configuration = routing_configuration
        alias.updated_at = unix_time()
        return alias

    # ========== Flow Version operations ==========

    def create_flow_version(
        self,
        flow_identifier: str,
        client_token: Optional[str],
        description: Optional[str],
    ) -> FlowVersion:
        flow = self.get_flow(flow_identifier)
        version = FlowVersion(
            flow_id=flow.id,
            flow_arn=flow.arn,
            flow_name=flow.name,
            flow_status=flow.status,
            region_name=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
            description=description,
            definition=flow.definition,
            execution_role_arn=flow.execution_role_arn,
        )
        flow.versions[version.version] = version
        return version

    def get_flow_version(self, flow_identifier: str, flow_version: str) -> FlowVersion:
        flow = self.get_flow(flow_identifier)
        if flow_version not in flow.versions:
            raise ResourceNotFoundException(
                f"Flow version {flow_version} not found for flow {flow_identifier}"
            )
        return flow.versions[flow_version]

    def list_flow_versions(
        self,
        flow_identifier: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[FlowVersion], Optional[str]]:
        flow = self.get_flow(flow_identifier)
        return list(flow.versions.values()), None

    def delete_flow_version(
        self,
        flow_identifier: str,
        flow_version: str,
        skip_resource_in_use_check: Optional[bool],
    ) -> tuple[str, str]:
        flow = self.get_flow(flow_identifier)
        if flow_version not in flow.versions:
            raise ResourceNotFoundException(
                f"Flow version {flow_version} not found for flow {flow_identifier}"
            )
        del flow.versions[flow_version]
        return flow_identifier, flow_version

    # ========== Prompt operations ==========

    def create_prompt(
        self,
        name: str,
        client_token: Optional[str],
        description: Optional[str],
        customer_encryption_key_arn: Optional[str],
        default_variant: Optional[str],
        variants: Optional[list[dict[str, Any]]],
        tags: Optional[dict[str, str]],
    ) -> Prompt:
        prompt = Prompt(
            name=name,
            region_name=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
            description=description,
            customer_encryption_key_arn=customer_encryption_key_arn,
            default_variant=default_variant,
            variants=variants,
            tags=tags,
        )
        self.prompts[prompt.id] = prompt
        return prompt

    def get_prompt(self, prompt_identifier: str, prompt_version: Optional[str]) -> Prompt:
        if prompt_identifier not in self.prompts:
            raise ResourceNotFoundException(f"Prompt {prompt_identifier} not found")
        return self.prompts[prompt_identifier]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_prompts(self) -> list[Prompt]:
        return list(self.prompts.values())

    def delete_prompt(
        self, prompt_identifier: str, prompt_version: Optional[str]
    ) -> tuple[str, Optional[str]]:
        if prompt_identifier not in self.prompts:
            raise ResourceNotFoundException(f"Prompt {prompt_identifier} not found")
        del self.prompts[prompt_identifier]
        return prompt_identifier, prompt_version

    def update_prompt(
        self,
        prompt_identifier: str,
        name: str,
        description: Optional[str],
        customer_encryption_key_arn: Optional[str],
        default_variant: Optional[str],
        variants: Optional[list[dict[str, Any]]],
    ) -> Prompt:
        prompt = self.get_prompt(prompt_identifier, None)
        prompt.name = name
        if description is not None:
            prompt.description = description
        if customer_encryption_key_arn is not None:
            prompt.customer_encryption_key_arn = customer_encryption_key_arn
        if default_variant is not None:
            prompt.default_variant = default_variant
        if variants is not None:
            prompt.variants = variants
        prompt.updated_at = unix_time()
        return prompt

    def create_prompt_version(
        self,
        prompt_identifier: str,
        client_token: Optional[str],
        description: Optional[str],
        tags: Optional[dict[str, str]],
    ) -> PromptVersion:
        prompt = self.get_prompt(prompt_identifier, None)
        version = PromptVersion(
            prompt_id=prompt.id,
            prompt_arn=prompt.arn,
            prompt_name=prompt.name,
            region_name=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
            description=description,
            customer_encryption_key_arn=prompt.customer_encryption_key_arn,
            default_variant=prompt.default_variant,
            variants=prompt.variants,
        )
        prompt.versions[version.version] = version
        return version

    # ========== Tagging operations ==========

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        if resource_arn not in self._list_arns():
            raise ResourceNotFoundException(f"Resource {resource_arn} not found")
        tags_input = TaggingService.convert_dict_to_tags_input(tags or {})
        self.tagger.tag_resource(resource_arn, tags_input)
        return

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        if resource_arn not in self._list_arns():
            raise ResourceNotFoundException(f"Resource {resource_arn} not found")
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)
        return

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        if resource_arn not in self._list_arns():
            raise ResourceNotFoundException(f"Resource {resource_arn} not found")
        return self.tagger.get_tag_dict_for_resource(resource_arn)


bedrockagent_backends = BackendDict(AgentsforBedrockBackend, "bedrock")
