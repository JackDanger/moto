"""bedrock base URL and path."""

from ..bedrockagent.responses import AgentsforBedrockResponse
from .responses import BedrockResponse

url_bases = [
    r"https?://bedrock\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Catch-all (must be last in dict order, but Moto uses longest-match)
    "{0}/.*$": BedrockResponse.dispatch,
    # Agents
    "{0}/agents/?$": AgentsforBedrockResponse.dispatch,
    "{0}/agents/(?P<agent_name>[^/]+)/$": AgentsforBedrockResponse.dispatch,
    # Knowledge Bases
    "{0}/knowledgebases$": AgentsforBedrockResponse.dispatch,
    "{0}/knowledgebases/(?P<kb_name>[^/]+)$": AgentsforBedrockResponse.dispatch,
    "{0}/knowledgebases/(?P<kb_name>[^/]+)/$": AgentsforBedrockResponse.dispatch,
    # Custom Models
    "{0}/custom-models$": BedrockResponse.dispatch,
    "{0}/custom-models/create-custom-model$": BedrockResponse.dispatch,
    "{0}/custom-models/(?P<modelIdentifier>[^/]+)$": BedrockResponse.dispatch,
    "{0}/custom-models/(?P<arn_prefix>[^/]+)/(?P<jobIdentifier>[^/]+)$": BedrockResponse.dispatch,
    # Model Customization Jobs
    "{0}/model-customization-jobs$": BedrockResponse.dispatch,
    "{0}/model-customization-jobs/(?P<jobIdentifier>[^/]+)$": BedrockResponse.dispatch,
    "{0}/model-customization-jobs/(?P<jobIdentifier>[^/]+)/stop$": BedrockResponse.dispatch,
    # Model Invocation Logging
    "{0}/logging/modelinvocations$": BedrockResponse.dispatch,
    # Tagging
    "{0}/listTagsForResource$": BedrockResponse.dispatch,
    "{0}/tagResource$": BedrockResponse.dispatch,
    "{0}/untagResource$": BedrockResponse.dispatch,
    "{0}/tags/(?P<resource_arn>[^/]+)$": AgentsforBedrockResponse.dispatch,
    "{0}/tags/(?P<arn_prefix>[^/]+)/(?P<name>[^/]+)$": AgentsforBedrockResponse.dispatch,
    # Guardrails
    "{0}/guardrails$": BedrockResponse.dispatch,
    "{0}/guardrails/(?P<guardrailIdentifier>[^/]+)$": BedrockResponse.dispatch,
    # Provisioned Model Throughput
    "{0}/provisioned-model-throughput$": BedrockResponse.dispatch,
    "{0}/provisioned-model-throughputs$": BedrockResponse.dispatch,
    "{0}/provisioned-model-throughput/(?P<provisionedModelId>[^/]+)$": BedrockResponse.dispatch,
    # Evaluation Jobs
    "{0}/evaluation-jobs$": BedrockResponse.dispatch,
    "{0}/evaluation-jobs/batch-delete$": BedrockResponse.dispatch,
    "{0}/evaluation-jobs/(?P<jobIdentifier>[^/]+)$": BedrockResponse.dispatch,
    "{0}/evaluation-job/(?P<jobIdentifier>[^/]+)/stop$": BedrockResponse.dispatch,
    # Inference Profiles
    "{0}/inference-profiles$": BedrockResponse.dispatch,
    "{0}/inference-profiles/(?P<inferenceProfileIdentifier>[^/]+)$": BedrockResponse.dispatch,
    # Model Import Jobs
    "{0}/model-import-jobs$": BedrockResponse.dispatch,
    "{0}/model-import-jobs/(?P<jobIdentifier>[^/]+)$": BedrockResponse.dispatch,
    # Imported Models
    "{0}/imported-models$": BedrockResponse.dispatch,
    "{0}/imported-models/(?P<modelIdentifier>[^/]+)$": BedrockResponse.dispatch,
    # Model Copy Jobs
    "{0}/model-copy-jobs$": BedrockResponse.dispatch,
    "{0}/model-copy-jobs/(?P<jobArn>[^/]+)$": BedrockResponse.dispatch,
    # Model Invocation Jobs (batch inference)
    "{0}/model-invocation-job$": BedrockResponse.dispatch,
    "{0}/model-invocation-jobs$": BedrockResponse.dispatch,
    "{0}/model-invocation-job/(?P<jobIdentifier>[^/]+)$": BedrockResponse.dispatch,
    "{0}/model-invocation-job/(?P<jobIdentifier>[^/]+)/stop$": BedrockResponse.dispatch,
    # Foundation Models
    "{0}/foundation-models$": BedrockResponse.dispatch,
    "{0}/foundation-models/(?P<modelIdentifier>[^/]+)$": BedrockResponse.dispatch,
    "{0}/foundation-model-availability/(?P<modelId>[^/]+)$": BedrockResponse.dispatch,
    # Marketplace Model Endpoints
    "{0}/marketplace-model/endpoints$": BedrockResponse.dispatch,
    "{0}/marketplace-model/endpoints/(?P<endpointArn>[^/]+)$": BedrockResponse.dispatch,
    "{0}/marketplace-model/endpoints/(?P<endpointArn>[^/]+)/registration$": BedrockResponse.dispatch,
    # Prompt Routers
    "{0}/prompt-routers$": BedrockResponse.dispatch,
    "{0}/prompt-routers/(?P<promptRouterArn>[^/]+)$": BedrockResponse.dispatch,
    # Custom Model Deployments
    "{0}/model-customization/custom-model-deployments$": BedrockResponse.dispatch,
    "{0}/model-customization/custom-model-deployments/(?P<deploymentId>[^/]+)$": BedrockResponse.dispatch,
    # Foundation Model Agreements
    "{0}/create-foundation-model-agreement$": BedrockResponse.dispatch,
    "{0}/delete-foundation-model-agreement$": BedrockResponse.dispatch,
    "{0}/list-foundation-model-agreement-offers/(?P<modelId>[^/]+)$": BedrockResponse.dispatch,
    # Enforced Guardrail Configuration
    "{0}/enforcedGuardrailsConfiguration$": BedrockResponse.dispatch,
    "{0}/enforcedGuardrailsConfiguration/(?P<configId>[^/]+)$": BedrockResponse.dispatch,
    # Use Case for Model Access
    "{0}/use-case-for-model-access$": BedrockResponse.dispatch,
    # Automated Reasoning Policies
    "{0}/automated-reasoning-policies$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/versions$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/export$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/test-cases$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/test-cases/(?P<testCaseId>[^/]+)$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)/start$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)/cancel$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)/annotations$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)/result-assets$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)/scenarios$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)/test-workflows$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)/test-results$": BedrockResponse.dispatch,
    "{0}/automated-reasoning-policies/(?P<policyArn>[^/]+)/build-workflows/(?P<buildWorkflowId>[^/]+)/test-cases/(?P<testCaseId>[^/]+)/test-results$": BedrockResponse.dispatch,
}
