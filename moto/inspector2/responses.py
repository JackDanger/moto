import json
from typing import Any
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import Inspector2Backend, inspector2_backends


class Inspector2Response(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="inspector2")

    @property
    def inspector2_backend(self) -> Inspector2Backend:
        return inspector2_backends[self.current_account][self.region]

    def create_filter(self) -> str:
        action = self._get_param("action")
        description = self._get_param("description")
        filter_criteria = self._get_param("filterCriteria")
        name = self._get_param("name")
        reason = self._get_param("reason")
        tags = self._get_param("tags")
        arn = self.inspector2_backend.create_filter(
            action=action,
            description=description,
            filter_criteria=filter_criteria,
            name=name,
            reason=reason,
            tags=tags,
        )
        return json.dumps({"arn": arn})

    def update_filter(self) -> str:
        filter_arn = self._get_param("filterArn")
        action = self._get_param("action")
        description = self._get_param("description")
        filter_criteria = self._get_param("filterCriteria")
        name = self._get_param("name")
        reason = self._get_param("reason")
        arn = self.inspector2_backend.update_filter(
            filter_arn=filter_arn,
            action=action,
            description=description,
            filter_criteria=filter_criteria,
            name=name,
            reason=reason,
        )
        return json.dumps({"arn": arn})

    def delete_filter(self) -> str:
        arn = self._get_param("arn")
        self.inspector2_backend.delete_filter(arn=arn)
        return json.dumps({"arn": arn})

    def list_filters(self) -> str:
        action = self._get_param("action")
        arns = self._get_param("arns")
        filters = self.inspector2_backend.list_filters(action=action, arns=arns)
        return json.dumps({"filters": [f.to_json() for f in filters]})

    def list_findings(self) -> str:
        filter_criteria = self._get_param("filterCriteria")
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        sort_criteria = self._get_param("sortCriteria")
        findings = self.inspector2_backend.list_findings(
            filter_criteria=filter_criteria,
            max_results=max_results,
            next_token=next_token,
            sort_criteria=sort_criteria,
        )
        return json.dumps({"findings": findings})

    def list_delegated_admin_accounts(self) -> str:
        accounts = self.inspector2_backend.list_delegated_admin_accounts()
        return json.dumps(
            {
                "delegatedAdminAccounts": [
                    {"accountId": key, "status": val} for key, val in accounts.items()
                ]
            }
        )

    def enable_delegated_admin_account(self) -> str:
        account_id = self._get_param("delegatedAdminAccountId")
        self.inspector2_backend.enable_delegated_admin_account(account_id)
        return json.dumps({"delegatedAdminAccountId": account_id})

    def disable_delegated_admin_account(self) -> str:
        account_id = self._get_param("delegatedAdminAccountId")
        self.inspector2_backend.disable_delegated_admin_account(account_id)
        return json.dumps({"delegatedAdminAccountId": account_id})

    def get_delegated_admin_account(self) -> str:
        result = self.inspector2_backend.get_delegated_admin_account()
        if result:
            return json.dumps({"delegatedAdmin": result})
        return json.dumps({})

    def describe_organization_configuration(self) -> str:
        config = self.inspector2_backend.describe_organization_configuration()
        return json.dumps(config)

    def update_organization_configuration(self) -> str:
        auto_enable = self._get_param("autoEnable")
        config = self.inspector2_backend.update_organization_configuration(auto_enable)
        return json.dumps(config)

    def enable(self) -> str:
        account_ids = self._get_param("accountIds")
        resource_types = self._get_param("resourceTypes")
        accounts = self.inspector2_backend.enable(account_ids, resource_types)
        failed: list[dict[str, Any]] = []
        return json.dumps({"accounts": accounts, "failedAccounts": failed})

    def disable(self) -> str:
        account_ids = self._get_param("accountIds")
        resource_types = self._get_param("resourceTypes")
        accounts = self.inspector2_backend.disable(account_ids, resource_types)
        failed: list[dict[str, Any]] = []
        return json.dumps({"accounts": accounts, "failedAccounts": failed})

    def batch_get_account_status(self) -> str:
        account_ids = self._get_param("accountIds")
        accounts = self.inspector2_backend.batch_get_account_status(account_ids)
        failed: list[dict[str, Any]] = []
        return json.dumps({"accounts": accounts, "failedAccounts": failed})

    def batch_get_free_trial_info(self) -> str:
        account_ids = self._get_param("accountIds")
        accounts, failed = self.inspector2_backend.batch_get_free_trial_info(
            account_ids
        )
        return json.dumps({"accounts": accounts, "failedAccounts": failed})

    def batch_get_code_snippet(self) -> str:
        finding_arns = self._get_param("findingArns")
        results, errors = self.inspector2_backend.batch_get_code_snippet(finding_arns)
        return json.dumps({"codeSnippetResults": results, "errors": errors})

    def batch_get_finding_details(self) -> str:
        finding_arns = self._get_param("findingArns")
        details, errors = self.inspector2_backend.batch_get_finding_details(
            finding_arns
        )
        return json.dumps({"findingDetails": details, "errors": errors})

    def batch_get_member_ec2_deep_inspection_status(self) -> str:
        account_ids = self._get_param("accountIds")
        results, failed = (
            self.inspector2_backend.batch_get_member_ec2_deep_inspection_status(
                account_ids
            )
        )
        return json.dumps({"accountIds": results, "failedAccountIds": failed})

    def batch_update_member_ec2_deep_inspection_status(self) -> str:
        account_ids = self._get_param("accountIds")
        results, failed = (
            self.inspector2_backend.batch_update_member_ec2_deep_inspection_status(
                account_ids
            )
        )
        return json.dumps({"accountIds": results, "failedAccountIds": failed})

    def list_members(self) -> str:
        members = self.inspector2_backend.list_members()
        return json.dumps({"members": [m.to_json() for m in members]})

    def associate_member(self) -> str:
        account_id = self._get_param("accountId")
        self.inspector2_backend.associate_member(account_id)
        return json.dumps({"accountId": account_id})

    def disassociate_member(self) -> str:
        account_id = self._get_param("accountId")
        self.inspector2_backend.disassociate_member(account_id)
        return json.dumps({"accountId": account_id})

    def get_member(self) -> str:
        account_id = self._get_param("accountId")
        member = self.inspector2_backend.get_member(account_id)
        return json.dumps({"member": member.to_json()})

    def list_tags_for_resource(self) -> str:
        arn = unquote(self.path.split("/tags/")[-1])
        tags = self.inspector2_backend.list_tags_for_resource(arn)
        return json.dumps({"tags": tags})

    def tag_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tags = self._get_param("tags")
        self.inspector2_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return "{}"

    def untag_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tag_keys = self.querystring.get("tagKeys")
        self.inspector2_backend.untag_resource(resource_arn, tag_keys)  # type: ignore
        return "{}"

    # CIS Scan Configuration operations

    def create_cis_scan_configuration(self) -> str:
        scan_name = self._get_param("scanName")
        security_level = self._get_param("securityLevel")
        schedule = self._get_param("schedule")
        targets = self._get_param("targets")
        tags = self._get_param("tags")
        arn = self.inspector2_backend.create_cis_scan_configuration(
            scan_name=scan_name,
            security_level=security_level,
            schedule=schedule,
            targets=targets,
            tags=tags,
        )
        return json.dumps({"scanConfigurationArn": arn})

    def delete_cis_scan_configuration(self) -> str:
        scan_configuration_arn = self._get_param("scanConfigurationArn")
        arn = self.inspector2_backend.delete_cis_scan_configuration(
            scan_configuration_arn
        )
        return json.dumps({"scanConfigurationArn": arn})

    def list_cis_scan_configurations(self) -> str:
        configs = self.inspector2_backend.list_cis_scan_configurations()
        return json.dumps(
            {"scanConfigurations": [c.to_json() for c in configs]}
        )

    def update_cis_scan_configuration(self) -> str:
        scan_configuration_arn = self._get_param("scanConfigurationArn")
        scan_name = self._get_param("scanName")
        security_level = self._get_param("securityLevel")
        schedule = self._get_param("schedule")
        targets = self._get_param("targets")
        arn = self.inspector2_backend.update_cis_scan_configuration(
            scan_configuration_arn=scan_configuration_arn,
            scan_name=scan_name,
            security_level=security_level,
            schedule=schedule,
            targets=targets,
        )
        return json.dumps({"scanConfigurationArn": arn})

    def list_cis_scans(self) -> str:
        scans = self.inspector2_backend.list_cis_scans()
        return json.dumps({"scans": scans})

    def get_cis_scan_report(self) -> str:
        scan_arn = self._get_param("scanArn")
        result = self.inspector2_backend.get_cis_scan_report(scan_arn)
        return json.dumps(result)

    def get_cis_scan_result_details(self) -> str:
        scan_arn = self._get_param("scanArn")
        target_resource_id = self._get_param("targetResourceId")
        account_id = self._get_param("accountId")
        details = self.inspector2_backend.get_cis_scan_result_details(
            scan_arn, target_resource_id, account_id
        )
        return json.dumps({"scanResultDetails": details})

    def list_cis_scan_results_aggregated_by_checks(self) -> str:
        scan_arn = self._get_param("scanArn")
        results = (
            self.inspector2_backend.list_cis_scan_results_aggregated_by_checks(
                scan_arn
            )
        )
        return json.dumps({"checkAggregations": results})

    def list_cis_scan_results_aggregated_by_target_resource(self) -> str:
        scan_arn = self._get_param("scanArn")
        results = self.inspector2_backend.list_cis_scan_results_aggregated_by_target_resource(
            scan_arn
        )
        return json.dumps({"targetResourceAggregations": results})

    def start_cis_session(self) -> str:
        scan_job_id = self._get_param("scanJobId")
        message = self._get_param("message")
        self.inspector2_backend.start_cis_session(scan_job_id, message)
        return "{}"

    def stop_cis_session(self) -> str:
        scan_job_id = self._get_param("scanJobId")
        session_token = self._get_param("sessionToken")
        message = self._get_param("message")
        self.inspector2_backend.stop_cis_session(scan_job_id, session_token, message)
        return "{}"

    def send_cis_session_health(self) -> str:
        scan_job_id = self._get_param("scanJobId")
        session_token = self._get_param("sessionToken")
        self.inspector2_backend.send_cis_session_health(scan_job_id, session_token)
        return "{}"

    def send_cis_session_telemetry(self) -> str:
        scan_job_id = self._get_param("scanJobId")
        session_token = self._get_param("sessionToken")
        messages = self._get_param("messages")
        self.inspector2_backend.send_cis_session_telemetry(
            scan_job_id, session_token, messages
        )
        return "{}"

    # Findings reports

    def create_findings_report(self) -> str:
        report_format = self._get_param("reportFormat")
        s3_destination = self._get_param("s3Destination")
        filter_criteria = self._get_param("filterCriteria")
        report_id = self.inspector2_backend.create_findings_report(
            report_format=report_format,
            s3_destination=s3_destination,
            filter_criteria=filter_criteria,
        )
        return json.dumps({"reportId": report_id})

    def cancel_findings_report(self) -> str:
        report_id = self._get_param("reportId")
        result = self.inspector2_backend.cancel_findings_report(report_id)
        return json.dumps({"reportId": result})

    def get_findings_report_status(self) -> str:
        report_id = self._get_param("reportId")
        result = self.inspector2_backend.get_findings_report_status(report_id)
        return json.dumps(result)

    # SBOM exports

    def create_sbom_export(self) -> str:
        report_format = self._get_param("reportFormat")
        s3_destination = self._get_param("s3Destination")
        resource_filter_criteria = self._get_param("resourceFilterCriteria")
        report_id = self.inspector2_backend.create_sbom_export(
            report_format=report_format,
            s3_destination=s3_destination,
            resource_filter_criteria=resource_filter_criteria,
        )
        return json.dumps({"reportId": report_id})

    def cancel_sbom_export(self) -> str:
        report_id = self._get_param("reportId")
        result = self.inspector2_backend.cancel_sbom_export(report_id)
        return json.dumps({"reportId": result})

    def get_sbom_export(self) -> str:
        report_id = self._get_param("reportId")
        result = self.inspector2_backend.get_sbom_export(report_id)
        return json.dumps(result)

    # Configuration

    def get_configuration(self) -> str:
        result = self.inspector2_backend.get_configuration()
        return json.dumps(result)

    def update_configuration(self) -> str:
        ecr_configuration = self._get_param("ecrConfiguration")
        ec2_configuration = self._get_param("ec2Configuration")
        self.inspector2_backend.update_configuration(
            ecr_configuration=ecr_configuration,
            ec2_configuration=ec2_configuration,
        )
        return "{}"

    # EC2 Deep Inspection

    def get_ec2_deep_inspection_configuration(self) -> str:
        result = self.inspector2_backend.get_ec2_deep_inspection_configuration()
        return json.dumps(result)

    def update_ec2_deep_inspection_configuration(self) -> str:
        activate = self._get_param("activateDeepInspection")
        package_paths = self._get_param("packagePaths")
        result = self.inspector2_backend.update_ec2_deep_inspection_configuration(
            activate_deep_inspection=activate,
            package_paths=package_paths,
        )
        return json.dumps(result)

    def update_org_ec2_deep_inspection_configuration(self) -> str:
        org_package_paths = self._get_param("orgPackagePaths")
        self.inspector2_backend.update_org_ec2_deep_inspection_configuration(
            org_package_paths
        )
        return "{}"

    # Encryption key

    def get_encryption_key(self) -> str:
        scan_type = self._get_param("scanType") or self.querystring.get(
            "scanType", [""]
        )[0]
        resource_type = self._get_param("resourceType") or self.querystring.get(
            "resourceType", [""]
        )[0]
        kms_key_id = self.inspector2_backend.get_encryption_key(
            scan_type, resource_type
        )
        return json.dumps({"kmsKeyId": kms_key_id})

    def update_encryption_key(self) -> str:
        kms_key_id = self._get_param("kmsKeyId")
        scan_type = self._get_param("scanType")
        resource_type = self._get_param("resourceType")
        self.inspector2_backend.update_encryption_key(
            kms_key_id, scan_type, resource_type
        )
        return "{}"

    def reset_encryption_key(self) -> str:
        scan_type = self._get_param("scanType")
        resource_type = self._get_param("resourceType")
        self.inspector2_backend.reset_encryption_key(scan_type, resource_type)
        return "{}"

    # Coverage

    def list_coverage(self) -> str:
        resources = self.inspector2_backend.list_coverage()
        return json.dumps({"coveredResources": resources})

    def list_coverage_statistics(self) -> str:
        counts, total = self.inspector2_backend.list_coverage_statistics()
        return json.dumps({"countsByGroup": counts, "totalCounts": total})

    # Finding aggregations

    def list_finding_aggregations(self) -> str:
        aggregation_type = self._get_param("aggregationType")
        agg_type, responses = self.inspector2_backend.list_finding_aggregations(
            aggregation_type
        )
        return json.dumps(
            {"aggregationType": agg_type, "responses": responses}
        )

    # Account permissions

    def list_account_permissions(self) -> str:
        permissions = self.inspector2_backend.list_account_permissions()
        return json.dumps({"permissions": permissions})

    # Usage totals

    def list_usage_totals(self) -> str:
        account_ids = self._get_param("accountIds")
        totals = self.inspector2_backend.list_usage_totals(account_ids)
        return json.dumps({"totals": totals})

    # Search vulnerabilities

    def search_vulnerabilities(self) -> str:
        filter_criteria = self._get_param("filterCriteria")
        vulns = self.inspector2_backend.search_vulnerabilities(filter_criteria)
        return json.dumps({"vulnerabilities": vulns})

    # Get clusters for image

    def get_clusters_for_image(self) -> str:
        image_filter = self._get_param("filter")
        clusters = self.inspector2_backend.get_clusters_for_image(image_filter)
        return json.dumps({"cluster": clusters})

    # Code Security Integration operations

    def create_code_security_integration(self) -> str:
        name = self._get_param("name")
        integration_type = self._get_param("type")
        details = self._get_param("details")
        tags = self._get_param("tags")
        arn, status, auth_url = (
            self.inspector2_backend.create_code_security_integration(
                name=name,
                integration_type=integration_type,
                details=details,
                tags=tags,
            )
        )
        result: dict[str, Any] = {"integrationArn": arn, "status": status}
        if auth_url:
            result["authorizationUrl"] = auth_url
        return json.dumps(result)

    def delete_code_security_integration(self) -> str:
        integration_arn = self._get_param("integrationArn")
        arn = self.inspector2_backend.delete_code_security_integration(integration_arn)
        return json.dumps({"integrationArn": arn})

    def get_code_security_integration(self) -> str:
        integration_arn = self._get_param("integrationArn")
        result = self.inspector2_backend.get_code_security_integration(integration_arn)
        return json.dumps(result)

    def list_code_security_integrations(self) -> str:
        integrations = self.inspector2_backend.list_code_security_integrations()
        return json.dumps({"integrations": integrations})

    def update_code_security_integration(self) -> str:
        integration_arn = self._get_param("integrationArn")
        details = self._get_param("details")
        arn, status = self.inspector2_backend.update_code_security_integration(
            integration_arn, details
        )
        return json.dumps({"integrationArn": arn, "status": status})

    # Code Security Scan Configuration operations

    def create_code_security_scan_configuration(self) -> str:
        name = self._get_param("name")
        level = self._get_param("level")
        configuration = self._get_param("configuration")
        scope_settings = self._get_param("scopeSettings")
        tags = self._get_param("tags")
        arn = self.inspector2_backend.create_code_security_scan_configuration(
            name=name,
            level=level,
            configuration=configuration,
            scope_settings=scope_settings,
            tags=tags,
        )
        return json.dumps({"scanConfigurationArn": arn})

    def delete_code_security_scan_configuration(self) -> str:
        scan_configuration_arn = self._get_param("scanConfigurationArn")
        arn = self.inspector2_backend.delete_code_security_scan_configuration(
            scan_configuration_arn
        )
        return json.dumps({"scanConfigurationArn": arn})

    def get_code_security_scan_configuration(self) -> str:
        scan_configuration_arn = self._get_param("scanConfigurationArn")
        result = self.inspector2_backend.get_code_security_scan_configuration(
            scan_configuration_arn
        )
        return json.dumps(result)

    def list_code_security_scan_configurations(self) -> str:
        configs = self.inspector2_backend.list_code_security_scan_configurations()
        return json.dumps({"configurations": configs})

    def update_code_security_scan_configuration(self) -> str:
        scan_configuration_arn = self._get_param("scanConfigurationArn")
        configuration = self._get_param("configuration")
        arn = self.inspector2_backend.update_code_security_scan_configuration(
            scan_configuration_arn, configuration
        )
        return json.dumps({"scanConfigurationArn": arn})

    def batch_associate_code_security_scan_configuration(self) -> str:
        requests_list = self._get_param("associateConfigurationRequests")
        failed, successful = (
            self.inspector2_backend.batch_associate_code_security_scan_configuration(
                requests_list
            )
        )
        return json.dumps(
            {"failedAssociations": failed, "successfulAssociations": successful}
        )

    def batch_disassociate_code_security_scan_configuration(self) -> str:
        requests_list = self._get_param("disassociateConfigurationRequests")
        failed, successful = (
            self.inspector2_backend.batch_disassociate_code_security_scan_configuration(
                requests_list
            )
        )
        return json.dumps(
            {"failedAssociations": failed, "successfulAssociations": successful}
        )

    def list_code_security_scan_configuration_associations(self) -> str:
        scan_configuration_arn = self._get_param("scanConfigurationArn")
        associations = (
            self.inspector2_backend.list_code_security_scan_configuration_associations(
                scan_configuration_arn
            )
        )
        return json.dumps({"associations": associations})

    def start_code_security_scan(self) -> str:
        resource = self._get_param("resource")
        scan_id, status = self.inspector2_backend.start_code_security_scan(resource)
        return json.dumps({"scanId": scan_id, "status": status})

    def get_code_security_scan(self) -> str:
        resource = self._get_param("resource")
        scan_id = self._get_param("scanId")
        result = self.inspector2_backend.get_code_security_scan(resource, scan_id)
        return json.dumps(result)
