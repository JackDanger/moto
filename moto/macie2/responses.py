import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import MacieBackend, macie2_backends


class MacieResponse(BaseResponse):
    """Handles API requests for the Macie service."""

    def __init__(self) -> None:
        super().__init__(service_name="macie2")

    @property
    def macie_backend(self) -> MacieBackend:
        return macie2_backends[self.current_account][self.region]

    # --- Invitations ---

    def create_invitations(self) -> str:
        account_ids = self._get_param("accountIds", [])
        self.macie_backend.create_invitations(account_ids=account_ids)
        return json.dumps({"unprocessedAccounts": []})

    def list_invitations(self) -> str:
        invitations = self.macie_backend.list_invitations()
        return json.dumps({"invitations": [inv.to_json() for inv in invitations]})

    def decline_invitations(self) -> str:
        account_ids = self._get_param("accountIds", [])
        self.macie_backend.decline_invitations(account_ids=account_ids)
        return json.dumps({"unprocessedAccounts": []})

    def delete_invitations(self) -> str:
        account_ids = self._get_param("accountIds", [])
        self.macie_backend.delete_invitations(account_ids=account_ids)
        return json.dumps({"unprocessedAccounts": []})

    def get_invitations_count(self) -> str:
        count = self.macie_backend.get_invitations_count()
        return json.dumps({"invitationsCount": count})

    def accept_invitation(self) -> str:
        administrator_account_id = self._get_param("administratorAccountId")
        invitation_id = self._get_param("invitationId")
        self.macie_backend.accept_invitation(administrator_account_id, invitation_id)
        return "{}"

    # --- Members ---

    def create_member(self) -> str:
        account = self._get_param("account", {})
        tags = self._get_param("tags", {})
        arn = self.macie_backend.create_member(account=account, tags=tags)
        return json.dumps({"arn": arn})

    def list_members(self) -> str:
        members = self.macie_backend.list_members()
        return json.dumps({"members": [m.to_json() for m in members]})

    def get_member(self) -> str:
        member_id = self.path.split("/")[-1]
        member = self.macie_backend.get_member(member_id)
        return json.dumps(member.to_json())

    def get_administrator_account(self) -> str:
        admin = self.macie_backend.get_administrator_account()
        if admin:
            response = {
                "administrator": {
                    "accountId": admin.administrator_account_id,
                    "relationshipStatus": "Enabled",
                }
            }
        else:
            response = {}
        return json.dumps(response)

    def get_master_account(self) -> str:
        admin = self.macie_backend.get_master_account()
        if admin:
            response = {
                "master": {
                    "accountId": admin.administrator_account_id,
                    "relationshipStatus": "Enabled",
                }
            }
        else:
            response = {}
        return json.dumps(response)

    def delete_member(self) -> str:
        member_account_id = self.path.split("/")[-1]
        self.macie_backend.delete_member(member_account_id)
        return "{}"

    def disassociate_member(self) -> str:
        member_account_id = self.path.split("/")[-1]
        self.macie_backend.disassociate_member(member_account_id)
        return "{}"

    def update_member_session(self) -> str:
        member_id = self.path.split("/")[-1]
        status = self._get_param("status")
        self.macie_backend.update_member_session(member_id, status)
        return "{}"

    def disassociate_from_administrator_account(self) -> str:
        self.macie_backend.disassociate_from_administrator_account()
        return "{}"

    def disassociate_from_master_account(self) -> str:
        self.macie_backend.disassociate_from_master_account()
        return "{}"

    # --- Macie Session ---

    def get_macie_session(self) -> str:
        session = self.macie_backend.get_macie_session()
        return json.dumps(session)

    def enable_macie(self) -> str:
        finding_publishing_frequency = self._get_param(
            "findingPublishingFrequency", "FIFTEEN_MINUTES"
        )
        status = self._get_param("status", "ENABLED")
        self.macie_backend.enable_macie(finding_publishing_frequency, status)
        return "{}"

    def update_macie_session(self) -> str:
        finding_publishing_frequency = self._get_param("findingPublishingFrequency")
        status = self._get_param("status")
        self.macie_backend.update_macie_session(finding_publishing_frequency, status)
        return "{}"

    def disable_macie(self) -> str:
        self.macie_backend.disable_macie()
        return json.dumps({})

    # --- Organization Admin ---

    def enable_organization_admin_account(self) -> str:
        admin_account_id = self._get_param("adminAccountId")
        self.macie_backend.enable_organization_admin_account(
            admin_account_id=admin_account_id
        )
        return json.dumps({})

    def disable_organization_admin_account(self) -> str:
        admin_account_id = self._get_param("adminAccountId")
        self.macie_backend.disable_organization_admin_account(
            admin_account_id=admin_account_id
        )
        return json.dumps({})

    def list_organization_admin_accounts(self) -> str:
        admin_accounts = self.macie_backend.list_organization_admin_accounts()
        return json.dumps({"adminAccounts": admin_accounts})

    def describe_organization_configuration(self) -> str:
        config = self.macie_backend.describe_organization_configuration()
        return json.dumps(config)

    def update_organization_configuration(self) -> str:
        auto_enable = self._get_param("autoEnable", False)
        self.macie_backend.update_organization_configuration(auto_enable)
        return "{}"

    # --- Allow Lists ---

    def create_allow_list(self) -> str:
        name = self._get_param("name")
        criteria = self._get_param("criteria", {})
        description = self._get_param("description")
        tags = self._get_param("tags", {})
        allow_list = self.macie_backend.create_allow_list(
            name=name, criteria=criteria, description=description, tags=tags
        )
        return json.dumps({"arn": allow_list.arn, "id": allow_list.id})

    def get_allow_list(self) -> str:
        list_id = self.path.split("/")[-1]
        allow_list = self.macie_backend.get_allow_list(list_id)
        return json.dumps(allow_list.to_json())

    def update_allow_list(self) -> str:
        list_id = self.path.split("/")[-1]
        name = self._get_param("name")
        criteria = self._get_param("criteria", {})
        description = self._get_param("description")
        allow_list = self.macie_backend.update_allow_list(
            list_id=list_id, name=name, criteria=criteria, description=description
        )
        return json.dumps({"arn": allow_list.arn, "id": allow_list.id})

    def delete_allow_list(self) -> str:
        list_id = self.path.split("/")[-1]
        self.macie_backend.delete_allow_list(list_id)
        return "{}"

    def list_allow_lists(self) -> str:
        allow_lists = self.macie_backend.list_allow_lists()
        return json.dumps(
            {"allowLists": [al.to_summary() for al in allow_lists]}
        )

    # --- Classification Jobs ---

    def create_classification_job(self) -> str:
        name = self._get_param("name")
        job_type = self._get_param("jobType")
        s3_job_definition = self._get_param("s3JobDefinition", {})
        client_token = self._get_param("clientToken")
        description = self._get_param("description")
        initial_run = self._get_param("initialRun", False)
        sampling_percentage = self._get_param("samplingPercentage")
        schedule_frequency = self._get_param("scheduleFrequency")
        tags = self._get_param("tags", {})
        allow_list_ids = self._get_param("allowListIds", [])
        custom_data_identifier_ids = self._get_param("customDataIdentifierIds", [])
        managed_data_identifier_ids = self._get_param("managedDataIdentifierIds", [])
        managed_data_identifier_selector = self._get_param("managedDataIdentifierSelector")
        job = self.macie_backend.create_classification_job(
            name=name,
            job_type=job_type,
            s3_job_definition=s3_job_definition,
            client_token=client_token,
            description=description,
            initial_run=initial_run,
            sampling_percentage=sampling_percentage,
            schedule_frequency=schedule_frequency,
            tags=tags,
            allow_list_ids=allow_list_ids,
            custom_data_identifier_ids=custom_data_identifier_ids,
            managed_data_identifier_ids=managed_data_identifier_ids,
            managed_data_identifier_selector=managed_data_identifier_selector,
        )
        return json.dumps({"jobArn": job.job_arn, "jobId": job.job_id})

    def describe_classification_job(self) -> str:
        job_id = self.path.split("/")[-1]
        job = self.macie_backend.describe_classification_job(job_id)
        return json.dumps(job.to_json())

    def update_classification_job(self) -> str:
        job_id = self.path.split("/")[-1]
        job_status = self._get_param("jobStatus")
        self.macie_backend.update_classification_job(job_id, job_status)
        return "{}"

    def list_classification_jobs(self) -> str:
        jobs = self.macie_backend.list_classification_jobs()
        return json.dumps({"items": [j.to_summary() for j in jobs]})

    # --- Custom Data Identifiers ---

    def create_custom_data_identifier(self) -> str:
        name = self._get_param("name")
        regex = self._get_param("regex", "")
        description = self._get_param("description")
        ignore_words = self._get_param("ignoreWords", [])
        keywords = self._get_param("keywords", [])
        maximum_match_distance = self._get_param("maximumMatchDistance")
        severity_levels = self._get_param("severityLevels", [])
        tags = self._get_param("tags", {})
        cdi = self.macie_backend.create_custom_data_identifier(
            name=name,
            regex=regex,
            description=description,
            ignore_words=ignore_words,
            keywords=keywords,
            maximum_match_distance=maximum_match_distance,
            severity_levels=severity_levels,
            tags=tags,
        )
        return json.dumps({"customDataIdentifierId": cdi.id})

    def get_custom_data_identifier(self) -> str:
        identifier_id = self.path.split("/")[-1]
        cdi = self.macie_backend.get_custom_data_identifier(identifier_id)
        return json.dumps(cdi.to_json())

    def delete_custom_data_identifier(self) -> str:
        identifier_id = self.path.split("/")[-1]
        self.macie_backend.delete_custom_data_identifier(identifier_id)
        return "{}"

    def list_custom_data_identifiers(self) -> str:
        cdis = self.macie_backend.list_custom_data_identifiers()
        return json.dumps({"items": [c.to_summary() for c in cdis]})

    def batch_get_custom_data_identifiers(self) -> str:
        ids = self._get_param("ids", [])
        found, not_found = self.macie_backend.batch_get_custom_data_identifiers(ids)
        return json.dumps({
            "customDataIdentifiers": [c.to_json() for c in found],
            "notFoundIdentifierIds": not_found,
        })

    def test_custom_data_identifier(self) -> str:
        regex = self._get_param("regex", "")
        sample_text = self._get_param("sampleText", "")
        ignore_words = self._get_param("ignoreWords", [])
        keywords = self._get_param("keywords", [])
        maximum_match_distance = self._get_param("maximumMatchDistance")
        count = self.macie_backend.test_custom_data_identifier(
            regex=regex,
            sample_text=sample_text,
            ignore_words=ignore_words,
            keywords=keywords,
            maximum_match_distance=maximum_match_distance,
        )
        return json.dumps({"matchCount": count})

    # --- Findings Filters ---

    def create_findings_filter(self) -> str:
        name = self._get_param("name")
        action = self._get_param("action")
        finding_criteria = self._get_param("findingCriteria", {})
        description = self._get_param("description")
        position = self._get_param("position")
        tags = self._get_param("tags", {})
        ff = self.macie_backend.create_findings_filter(
            name=name,
            action=action,
            finding_criteria=finding_criteria,
            description=description,
            position=position,
            tags=tags,
        )
        return json.dumps({"arn": ff.arn, "id": ff.id})

    def get_findings_filter(self) -> str:
        filter_id = self.path.split("/")[-1]
        ff = self.macie_backend.get_findings_filter(filter_id)
        return json.dumps(ff.to_json())

    def update_findings_filter(self) -> str:
        filter_id = self.path.split("/")[-1]
        name = self._get_param("name")
        action = self._get_param("action")
        finding_criteria = self._get_param("findingCriteria")
        description = self._get_param("description")
        position = self._get_param("position")
        ff = self.macie_backend.update_findings_filter(
            filter_id=filter_id,
            name=name,
            action=action,
            finding_criteria=finding_criteria,
            description=description,
            position=position,
        )
        return json.dumps({"arn": ff.arn, "id": ff.id})

    def delete_findings_filter(self) -> str:
        filter_id = self.path.split("/")[-1]
        self.macie_backend.delete_findings_filter(filter_id)
        return "{}"

    def list_findings_filters(self) -> str:
        filters = self.macie_backend.list_findings_filters()
        return json.dumps(
            {"findingsFilterListItems": [f.to_summary() for f in filters]}
        )

    # --- Classification Export Configuration ---

    def put_classification_export_configuration(self) -> str:
        configuration = self._get_param("configuration", {})
        result = self.macie_backend.put_classification_export_configuration(configuration)
        return json.dumps({"configuration": result})

    def get_classification_export_configuration(self) -> str:
        config = self.macie_backend.get_classification_export_configuration()
        if config:
            return json.dumps({"configuration": config})
        return json.dumps({})

    # --- Reveal Configuration ---

    def get_reveal_configuration(self) -> str:
        config, retrieval = self.macie_backend.get_reveal_configuration()
        return json.dumps({
            "configuration": config,
            "retrievalConfiguration": retrieval,
        })

    def update_reveal_configuration(self) -> str:
        configuration = self._get_param("configuration")
        retrieval_configuration = self._get_param("retrievalConfiguration")
        config, retrieval = self.macie_backend.update_reveal_configuration(
            configuration=configuration,
            retrieval_configuration=retrieval_configuration,
        )
        return json.dumps({
            "configuration": config,
            "retrievalConfiguration": retrieval,
        })

    # --- Automated Discovery ---

    def get_automated_discovery_configuration(self) -> str:
        config = self.macie_backend.get_automated_discovery_configuration()
        return json.dumps(config)

    def update_automated_discovery_configuration(self) -> str:
        status = self._get_param("status")
        auto_enable = self._get_param("autoEnableOrganizationMembers")
        self.macie_backend.update_automated_discovery_configuration(
            status=status, auto_enable_organization_members=auto_enable
        )
        return "{}"

    def batch_update_automated_discovery_accounts(self) -> str:
        accounts = self._get_param("accounts", [])
        errors = self.macie_backend.batch_update_automated_discovery_accounts(accounts)
        return json.dumps({"errors": errors})

    def list_automated_discovery_accounts(self) -> str:
        items = self.macie_backend.list_automated_discovery_accounts()
        return json.dumps({"items": items})

    # --- Findings Publication Configuration ---

    def get_findings_publication_configuration(self) -> str:
        config = self.macie_backend.get_findings_publication_configuration()
        return json.dumps({"securityHubConfiguration": config})

    def put_findings_publication_configuration(self) -> str:
        security_hub_config = self._get_param("securityHubConfiguration")
        self.macie_backend.put_findings_publication_configuration(security_hub_config)
        return "{}"

    # --- Findings ---

    def list_findings(self) -> str:
        finding_ids = self.macie_backend.list_findings()
        return json.dumps({"findingIds": finding_ids})

    def get_findings(self) -> str:
        finding_ids = self._get_param("findingIds", [])
        findings = self.macie_backend.get_findings(finding_ids)
        return json.dumps({"findings": findings})

    def get_finding_statistics(self) -> str:
        group_by = self._get_param("groupBy", "")
        counts = self.macie_backend.get_finding_statistics(group_by)
        return json.dumps({"countsByGroup": counts})

    def create_sample_findings(self) -> str:
        finding_types = self._get_param("findingTypes", [])
        self.macie_backend.create_sample_findings(finding_types)
        return "{}"

    # --- Buckets / Search ---

    def describe_buckets(self) -> str:
        buckets = self.macie_backend.describe_buckets()
        return json.dumps({"buckets": buckets})

    def get_bucket_statistics(self) -> str:
        stats = self.macie_backend.get_bucket_statistics()
        return json.dumps(stats)

    def search_resources(self) -> str:
        resources = self.macie_backend.search_resources()
        return json.dumps({"matchingResources": resources})

    # --- Usage ---

    def get_usage_totals(self) -> str:
        totals = self.macie_backend.get_usage_totals()
        return json.dumps({"usageTotals": totals})

    def get_usage_statistics(self) -> str:
        records = self.macie_backend.get_usage_statistics()
        return json.dumps({"records": records})

    # --- Classification Scope ---

    def get_classification_scope(self) -> str:
        scope_id = self.path.split("/")[-1]
        scope = self.macie_backend.get_classification_scope(scope_id)
        return json.dumps(scope)

    def update_classification_scope(self) -> str:
        scope_id = self.path.split("/")[-1]
        s3 = self._get_param("s3")
        self.macie_backend.update_classification_scope(scope_id, s3)
        return "{}"

    def list_classification_scopes(self) -> str:
        scopes = self.macie_backend.list_classification_scopes()
        return json.dumps({"classificationScopes": scopes})

    # --- Sensitivity Inspection Template ---

    def get_sensitivity_inspection_template(self) -> str:
        template_id = self.path.split("/")[-1]
        template = self.macie_backend.get_sensitivity_inspection_template(template_id)
        return json.dumps(template)

    def update_sensitivity_inspection_template(self) -> str:
        template_id = self.path.split("/")[-1]
        description = self._get_param("description")
        excludes = self._get_param("excludes")
        includes = self._get_param("includes")
        self.macie_backend.update_sensitivity_inspection_template(
            template_id, description, excludes, includes
        )
        return "{}"

    def list_sensitivity_inspection_templates(self) -> str:
        templates = self.macie_backend.list_sensitivity_inspection_templates()
        return json.dumps({"sensitivityInspectionTemplates": templates})

    # --- Resource Profile ---

    def get_resource_profile(self) -> str:
        profile = self.macie_backend.get_resource_profile()
        return json.dumps(profile)

    def update_resource_profile(self) -> str:
        self.macie_backend.update_resource_profile()
        return "{}"

    def list_resource_profile_artifacts(self) -> str:
        artifacts = self.macie_backend.list_resource_profile_artifacts()
        return json.dumps({"artifacts": artifacts})

    def list_resource_profile_detections(self) -> str:
        detections = self.macie_backend.list_resource_profile_detections()
        return json.dumps({"detections": detections})

    def update_resource_profile_detections(self) -> str:
        self.macie_backend.update_resource_profile_detections()
        return "{}"

    # --- Sensitive Data Occurrences ---

    def get_sensitive_data_occurrences(self) -> str:
        # Path: /findings/{findingId}/reveal
        parts = self.path.split("/")
        finding_id = parts[-2]  # /findings/{id}/reveal
        result = self.macie_backend.get_sensitive_data_occurrences(finding_id)
        return json.dumps(result)

    def get_sensitive_data_occurrences_availability(self) -> str:
        # Path: /findings/{findingId}/reveal/availability
        parts = self.path.split("/")
        finding_id = parts[-3]  # /findings/{id}/reveal/availability
        result = self.macie_backend.get_sensitive_data_occurrences_availability(finding_id)
        return json.dumps(result)

    # --- Managed Data Identifiers ---

    def list_managed_data_identifiers(self) -> str:
        items = self.macie_backend.list_managed_data_identifiers()
        return json.dumps({"items": items})

    # --- Tags ---

    def tag_resource(self) -> str:
        # Path: /tags/{resourceArn+}
        resource_arn = _extract_arn_from_path(self.path, "/tags/")
        tags = self._get_param("tags", {})
        self.macie_backend.tag_resource(resource_arn, tags)
        return "{}"

    def untag_resource(self) -> str:
        resource_arn = _extract_arn_from_path(self.path, "/tags/")
        tag_keys = self.querystring.get("tagKeys", [])
        self.macie_backend.untag_resource(resource_arn, tag_keys)
        return "{}"

    def list_tags_for_resource(self) -> str:
        resource_arn = _extract_arn_from_path(self.path, "/tags/")
        tags = self.macie_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"tags": tags})


def _extract_arn_from_path(path: str, prefix: str) -> str:
    """Extract and decode the ARN from a URL path after the given prefix."""
    idx = path.find(prefix)
    if idx >= 0:
        return unquote(path[idx + len(prefix) :])
    return ""
