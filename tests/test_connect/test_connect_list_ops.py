"""Tests for Connect List operations returning data from stores."""

import json

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def client():
    with mock_aws():
        yield boto3.client("connect", region_name="us-east-1")


@pytest.fixture
def instance_id(client):
    resp = client.create_instance(
        IdentityManagementType="CONNECT_MANAGED",
        InboundCallsEnabled=True,
        OutboundCallsEnabled=True,
    )
    return resp["Id"]


class TestListContactFlows:
    def test_empty(self, client, instance_id):
        resp = client.list_contact_flows(InstanceId=instance_id)
        assert resp["ContactFlowSummaryList"] == []

    def test_after_create(self, client, instance_id):
        flow = client.create_contact_flow(
            InstanceId=instance_id,
            Name="TestFlow",
            Type="CONTACT_FLOW",
            Content='{"Version":"2019-10-30","StartAction":"id","Actions":[]}',
        )
        resp = client.list_contact_flows(InstanceId=instance_id)
        summaries = resp["ContactFlowSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == flow["ContactFlowId"]
        assert summaries[0]["Name"] == "TestFlow"
        assert summaries[0]["ContactFlowType"] == "CONTACT_FLOW"


class TestListContactFlowModules:
    def test_empty(self, client, instance_id):
        resp = client.list_contact_flow_modules(InstanceId=instance_id)
        assert resp["ContactFlowModulesSummaryList"] == []

    def test_after_create(self, client, instance_id):
        mod = client.create_contact_flow_module(
            InstanceId=instance_id,
            Name="TestModule",
            Content='{"Version":"2019-10-30"}',
        )
        resp = client.list_contact_flow_modules(InstanceId=instance_id)
        summaries = resp["ContactFlowModulesSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == mod["Id"]
        assert summaries[0]["Name"] == "TestModule"


class TestListHoursOfOperations:
    def test_empty(self, client, instance_id):
        resp = client.list_hours_of_operations(InstanceId=instance_id)
        assert resp["HoursOfOperationSummaryList"] == []

    def test_after_create(self, client, instance_id):
        hours = client.create_hours_of_operation(
            InstanceId=instance_id,
            Name="TestHours",
            TimeZone="US/Eastern",
            Config=[
                {
                    "Day": "MONDAY",
                    "StartTime": {"Hours": 8, "Minutes": 0},
                    "EndTime": {"Hours": 17, "Minutes": 0},
                }
            ],
        )
        resp = client.list_hours_of_operations(InstanceId=instance_id)
        summaries = resp["HoursOfOperationSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == hours["HoursOfOperationId"]
        assert summaries[0]["Name"] == "TestHours"


class TestListQueues:
    def test_empty(self, client, instance_id):
        resp = client.list_queues(InstanceId=instance_id)
        assert resp["QueueSummaryList"] == []

    def test_after_create(self, client, instance_id):
        hours = client.create_hours_of_operation(
            InstanceId=instance_id,
            Name="H",
            TimeZone="US/Eastern",
            Config=[
                {
                    "Day": "MONDAY",
                    "StartTime": {"Hours": 8, "Minutes": 0},
                    "EndTime": {"Hours": 17, "Minutes": 0},
                }
            ],
        )
        queue = client.create_queue(
            InstanceId=instance_id,
            Name="TestQueue",
            HoursOfOperationId=hours["HoursOfOperationId"],
        )
        resp = client.list_queues(InstanceId=instance_id)
        summaries = resp["QueueSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == queue["QueueId"]
        assert summaries[0]["Name"] == "TestQueue"


class TestListRoutingProfiles:
    def test_empty(self, client, instance_id):
        resp = client.list_routing_profiles(InstanceId=instance_id)
        assert resp["RoutingProfileSummaryList"] == []

    def test_after_create(self, client, instance_id):
        hours = client.create_hours_of_operation(
            InstanceId=instance_id,
            Name="H",
            TimeZone="US/Eastern",
            Config=[
                {
                    "Day": "MONDAY",
                    "StartTime": {"Hours": 8, "Minutes": 0},
                    "EndTime": {"Hours": 17, "Minutes": 0},
                }
            ],
        )
        queue = client.create_queue(
            InstanceId=instance_id,
            Name="Q",
            HoursOfOperationId=hours["HoursOfOperationId"],
        )
        rp = client.create_routing_profile(
            InstanceId=instance_id,
            Name="TestRP",
            Description="test",
            DefaultOutboundQueueId=queue["QueueId"],
            MediaConcurrencies=[
                {"Channel": "VOICE", "Concurrency": 1},
            ],
        )
        resp = client.list_routing_profiles(InstanceId=instance_id)
        summaries = resp["RoutingProfileSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == rp["RoutingProfileId"]
        assert summaries[0]["Name"] == "TestRP"


class TestListSecurityProfiles:
    def test_empty(self, client, instance_id):
        resp = client.list_security_profiles(InstanceId=instance_id)
        assert resp["SecurityProfileSummaryList"] == []

    def test_after_create(self, client, instance_id):
        sp = client.create_security_profile(
            InstanceId=instance_id,
            SecurityProfileName="TestSP",
        )
        resp = client.list_security_profiles(InstanceId=instance_id)
        summaries = resp["SecurityProfileSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == sp["SecurityProfileId"]
        assert summaries[0]["Name"] == "TestSP"


class TestListUsers:
    def test_empty(self, client, instance_id):
        resp = client.list_users(InstanceId=instance_id)
        assert resp["UserSummaryList"] == []

    def test_after_create(self, client, instance_id):
        sp = client.create_security_profile(
            InstanceId=instance_id,
            SecurityProfileName="SP1",
        )
        hours = client.create_hours_of_operation(
            InstanceId=instance_id,
            Name="H",
            TimeZone="US/Eastern",
            Config=[
                {
                    "Day": "MONDAY",
                    "StartTime": {"Hours": 8, "Minutes": 0},
                    "EndTime": {"Hours": 17, "Minutes": 0},
                }
            ],
        )
        queue = client.create_queue(
            InstanceId=instance_id,
            Name="Q",
            HoursOfOperationId=hours["HoursOfOperationId"],
        )
        rp = client.create_routing_profile(
            InstanceId=instance_id,
            Name="RP",
            Description="test",
            DefaultOutboundQueueId=queue["QueueId"],
            MediaConcurrencies=[
                {"Channel": "VOICE", "Concurrency": 1},
            ],
        )
        user = client.create_user(
            InstanceId=instance_id,
            Username="testuser",
            SecurityProfileIds=[sp["SecurityProfileId"]],
            RoutingProfileId=rp["RoutingProfileId"],
        )
        resp = client.list_users(InstanceId=instance_id)
        summaries = resp["UserSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == user["UserId"]
        assert summaries[0]["Username"] == "testuser"


class TestListUserHierarchyGroups:
    def test_empty(self, client, instance_id):
        resp = client.list_user_hierarchy_groups(InstanceId=instance_id)
        assert resp["UserHierarchyGroupSummaryList"] == []

    def test_after_create(self, client, instance_id):
        group = client.create_user_hierarchy_group(
            InstanceId=instance_id,
            Name="TestGroup",
        )
        resp = client.list_user_hierarchy_groups(InstanceId=instance_id)
        summaries = resp["UserHierarchyGroupSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == group["HierarchyGroupId"]
        assert summaries[0]["Name"] == "TestGroup"


class TestListPrompts:
    def test_empty(self, client, instance_id):
        resp = client.list_prompts(InstanceId=instance_id)
        assert resp["PromptSummaryList"] == []

    def test_after_create(self, client, instance_id):
        prompt = client.create_prompt(
            InstanceId=instance_id,
            Name="TestPrompt",
            S3Uri="s3://bucket/key",
        )
        resp = client.list_prompts(InstanceId=instance_id)
        summaries = resp["PromptSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == prompt["PromptId"]
        assert summaries[0]["Name"] == "TestPrompt"


class TestListAgentStatuses:
    def test_empty(self, client, instance_id):
        resp = client.list_agent_statuses(InstanceId=instance_id)
        assert resp["AgentStatusSummaryList"] == []

    def test_after_create(self, client, instance_id):
        status = client.create_agent_status(
            InstanceId=instance_id,
            Name="TestStatus",
            State="ENABLED",
        )
        resp = client.list_agent_statuses(InstanceId=instance_id)
        summaries = resp["AgentStatusSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == status["AgentStatusId"]
        assert summaries[0]["Name"] == "TestStatus"


class TestListEvaluationForms:
    def test_empty(self, client, instance_id):
        resp = client.list_evaluation_forms(InstanceId=instance_id)
        assert resp["EvaluationFormSummaryList"] == []

    def test_after_create(self, client, instance_id):
        form = client.create_evaluation_form(
            InstanceId=instance_id,
            Title="TestForm",
            Items=[
                {
                    "Section": {
                        "Title": "Section1",
                        "RefId": "s1",
                        "Items": [],
                    }
                }
            ],
        )
        resp = client.list_evaluation_forms(InstanceId=instance_id)
        summaries = resp["EvaluationFormSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["EvaluationFormId"] == form["EvaluationFormId"]
        assert summaries[0]["Title"] == "TestForm"


class TestListRules:
    def test_empty(self, client, instance_id):
        resp = client.list_rules(InstanceId=instance_id)
        assert resp["RuleSummaryList"] == []

    def test_after_create(self, client, instance_id):
        rule = client.create_rule(
            InstanceId=instance_id,
            Name="TestRule",
            TriggerEventSource={
                "EventSourceName": "OnPostCallAnalysisAvailable",
            },
            Function="function",
            Actions=[
                {
                    "ActionType": "ASSIGN_CONTACT_CATEGORY",
                    "AssignContactCategoryAction": {},
                }
            ],
            PublishStatus="DRAFT",
        )
        resp = client.list_rules(InstanceId=instance_id)
        summaries = resp["RuleSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["RuleId"] == rule["RuleId"]
        assert summaries[0]["Name"] == "TestRule"


class TestListInstanceAttributes:
    def test_returns_attributes(self, client, instance_id):
        resp = client.list_instance_attributes(InstanceId=instance_id)
        attrs = resp["Attributes"]
        assert len(attrs) > 0
        # Check that standard attributes are present
        attr_types = [a["AttributeType"] for a in attrs]
        assert "INBOUND_CALLS" in attr_types
        assert "OUTBOUND_CALLS" in attr_types


class TestListViews:
    def test_empty(self, client, instance_id):
        resp = client.list_views(InstanceId=instance_id)
        assert resp["ViewsSummaryList"] == []

    def test_after_create(self, client, instance_id):
        view = client.create_view(
            InstanceId=instance_id,
            Name="TestView",
            Status="PUBLISHED",
            Content={"Template": '{"key": "value"}'},
        )
        resp = client.list_views(InstanceId=instance_id)
        summaries = resp["ViewsSummaryList"]
        assert len(summaries) == 1
        assert summaries[0]["Id"] == view["View"]["Id"]
        assert summaries[0]["Name"] == "TestView"


class TestListEmptyOperations:
    """Test operations that return empty lists (no backing store yet)."""

    def test_list_approved_origins(self, client, instance_id):
        resp = client.list_approved_origins(InstanceId=instance_id)
        assert resp["Origins"] == []

    def test_list_bots(self, client, instance_id):
        resp = client.list_bots(InstanceId=instance_id, LexVersion="V2")
        assert resp["LexBots"] == []

    def test_list_default_vocabularies(self, client, instance_id):
        resp = client.list_default_vocabularies(InstanceId=instance_id)
        assert resp["DefaultVocabularyList"] == []

    def test_list_instance_storage_configs(self, client, instance_id):
        resp = client.list_instance_storage_configs(
            InstanceId=instance_id, ResourceType="CHAT_TRANSCRIPTS"
        )
        assert resp["StorageConfigs"] == []

    def test_list_lambda_functions(self, client, instance_id):
        resp = client.list_lambda_functions(InstanceId=instance_id)
        assert resp["LambdaFunctions"] == []

    def test_list_security_keys(self, client, instance_id):
        resp = client.list_security_keys(InstanceId=instance_id)
        assert resp["SecurityKeys"] == []

    def test_list_task_templates(self, client, instance_id):
        resp = client.list_task_templates(InstanceId=instance_id)
        assert resp["TaskTemplates"] == []

    def test_list_phone_numbers(self, client, instance_id):
        resp = client.list_phone_numbers(InstanceId=instance_id)
        assert resp["PhoneNumberSummaryList"] == []

    def test_list_security_profile_permissions(self, client, instance_id):
        sp = client.create_security_profile(
            InstanceId=instance_id,
            SecurityProfileName="SP1",
            Permissions=["BasicRouting", "OutboundCallAccess"],
        )
        resp = client.list_security_profile_permissions(
            InstanceId=instance_id,
            SecurityProfileId=sp["SecurityProfileId"],
        )
        assert "BasicRouting" in resp["Permissions"]
        assert "OutboundCallAccess" in resp["Permissions"]
