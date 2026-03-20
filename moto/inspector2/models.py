import json
from collections.abc import Iterable
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition


class FilterResource(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        name: str,
        reason: Optional[str],
        action: str,
        description: Optional[str],
        filter_criteria: dict[str, Any],
        backend: "Inspector2Backend",
    ):
        filter_id = mock_random.get_random_hex(10)
        self.owner_id = account_id
        self.arn = f"arn:{get_partition(region)}:inspector2:{region}:{account_id}:owner/{self.owner_id}/filter/{filter_id}"
        self.name = name
        self.reason = reason
        self.action = action
        self.description = description
        self.filter_criteria = filter_criteria
        self.created_at = unix_time()
        self.backend = backend

    def to_json(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "arn": self.arn,
            "createdAt": self.created_at,
            "criteria": self.filter_criteria,
            "description": self.description,
            "name": self.name,
            "ownerId": self.owner_id,
            "reason": self.reason,
            "tags": self.backend.list_tags_for_resource(self.arn),
        }


class AccountStatus(BaseModel):
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.ec2 = "DISABLED"
        self.ecr = "DISABLED"
        self._lambda = "DISABLED"
        self.lambda_code = "DISABLED"

    def toggle(self, resource_types: list[str], enable: bool) -> None:
        if "EC2" in resource_types:
            self.ec2 = "ENABLED" if enable else "DISABLED"
        if "ECR" in resource_types:
            self.ecr = "ENABLED" if enable else "DISABLED"
        if "LAMBDA" in resource_types:
            self._lambda = "ENABLED" if enable else "DISABLED"
        if "LAMBDA_CODE" in resource_types or "LAMBDACODE" in resource_types:
            self.lambda_code = "ENABLED" if enable else "DISABLED"

    def to_json(self) -> dict[str, Any]:
        return {
            "accountId": self.account_id,
            "resourceStatus": {
                "ec2": self.ec2,
                "ecr": self.ecr,
                "lambda": self._lambda,
                "lambdaCode": self.lambda_code,
            },
            "status": self._status(),
        }

    def _status(self) -> str:
        return (
            "ENABLED"
            if "ENABLED" in [self.ec2, self.ecr, self._lambda, self.lambda_code]
            else "DISABLED"
        )

    def to_batch_json(self) -> dict[str, Any]:
        return {
            "accountId": self.account_id,
            "resourceState": {
                "ec2": {"status": self.ec2},
                "ecr": {"status": self.ecr},
                "lambda": {"status": self._lambda},
                "lambdaCode": {"status": self.lambda_code},
            },
            "state": {"status": self._status()},
        }


class Member(BaseModel):
    def __init__(self, account_id: str, admin_account_id: str):
        self.account_id = account_id
        self.admin_account_id = admin_account_id
        self.status = "ENABLED"
        self.updated_at = unix_time()

    def to_json(self) -> dict[str, Any]:
        return {
            "accountId": self.account_id,
            "delegatedAdminAccountId": self.admin_account_id,
            "relationshipStatus": self.status,
            "updatedAt": self.updated_at,
        }


class CisScanConfiguration(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        scan_name: str,
        security_level: str,
        schedule: dict[str, Any],
        targets: dict[str, Any],
        backend: "Inspector2Backend",
    ):
        config_id = mock_random.get_random_hex(16)
        partition = get_partition(region)
        self.arn = f"arn:{partition}:inspector2:{region}:{account_id}:owner/{account_id}/cis-configuration/{config_id}"
        self.scan_name = scan_name
        self.security_level = security_level
        self.schedule = schedule
        self.targets = targets
        self.owner_id = account_id
        self.backend = backend

    def to_json(self) -> dict[str, Any]:
        return {
            "scanConfigurationArn": self.arn,
            "scanName": self.scan_name,
            "securityLevel": self.security_level,
            "schedule": self.schedule,
            "targets": self.targets,
            "ownerId": self.owner_id,
            "tags": self.backend.list_tags_for_resource(self.arn),
        }


class FindingsReport(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        report_format: str,
        s3_destination: dict[str, Any],
        filter_criteria: Optional[dict[str, Any]],
    ):
        self.report_id = mock_random.get_random_hex(16)
        self.report_format = report_format
        self.s3_destination = s3_destination
        self.filter_criteria = filter_criteria
        self.status = "COMPLETE"

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "reportId": self.report_id,
            "status": self.status,
        }
        if self.s3_destination:
            result["destination"] = {"s3Destination": self.s3_destination}
        if self.filter_criteria:
            result["filterCriteria"] = self.filter_criteria
        return result


class SbomExport(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        report_format: str,
        s3_destination: dict[str, Any],
        resource_filter_criteria: Optional[dict[str, Any]],
    ):
        self.report_id = mock_random.get_random_hex(16)
        self.report_format = report_format
        self.s3_destination = s3_destination
        self.resource_filter_criteria = resource_filter_criteria
        self.status = "COMPLETE"

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "reportId": self.report_id,
            "format": self.report_format,
            "status": self.status,
            "s3Destination": self.s3_destination,
        }
        if self.resource_filter_criteria:
            result["filterCriteria"] = self.resource_filter_criteria
        return result


class CodeSecurityIntegration(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        name: str,
        integration_type: str,
        details: Optional[dict[str, Any]],
        backend: "Inspector2Backend",
    ):
        integration_id = mock_random.get_random_hex(16)
        partition = get_partition(region)
        self.arn = f"arn:{partition}:inspector2:{region}:{account_id}:owner/{account_id}/code-security-integration/{integration_id}"
        self.name = name
        self.integration_type = integration_type
        self.details = details
        self.status = "PENDING"
        self.status_reason = ""
        self.created_on = unix_time()
        self.last_update_on = unix_time()
        self.backend = backend

    def to_json(self) -> dict[str, Any]:
        return {
            "integrationArn": self.arn,
            "name": self.name,
            "type": self.integration_type,
            "status": self.status,
            "statusReason": self.status_reason,
            "createdOn": self.created_on,
            "lastUpdateOn": self.last_update_on,
            "tags": self.backend.list_tags_for_resource(self.arn),
        }


class CodeSecurityScanConfiguration(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        name: str,
        level: str,
        configuration: dict[str, Any],
        scope_settings: Optional[dict[str, Any]],
        backend: "Inspector2Backend",
    ):
        config_id = mock_random.get_random_hex(16)
        partition = get_partition(region)
        self.arn = f"arn:{partition}:inspector2:{region}:{account_id}:owner/{account_id}/code-security-scan-configuration/{config_id}"
        self.name = name
        self.level = level
        self.configuration = configuration
        self.scope_settings = scope_settings
        self.created_at = unix_time()
        self.last_updated_at = unix_time()
        self.backend = backend
        self.associations: list[dict[str, Any]] = []

    def to_json(self) -> dict[str, Any]:
        return {
            "scanConfigurationArn": self.arn,
            "name": self.name,
            "configuration": self.configuration,
            "level": self.level,
            "scopeSettings": self.scope_settings,
            "createdAt": self.created_at,
            "lastUpdatedAt": self.last_updated_at,
            "tags": self.backend.list_tags_for_resource(self.arn),
        }


class Inspector2Backend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.filters: dict[str, FilterResource] = {}
        self.admin_accounts: dict[str, str] = {}
        self.account_status: dict[str, AccountStatus] = {}
        self.members: dict[str, Member] = {}
        self.org_config = {
            "ec2": False,
            "ecr": False,
            "lambda": False,
            "lambdaCode": False,
        }
        self.tagger = TaggingService()
        self.findings_queue: list[Any] = []
        self.findings: dict[str, Any] = {}
        self.cis_scan_configurations: dict[str, CisScanConfiguration] = {}
        self.findings_reports: dict[str, FindingsReport] = {}
        self.sbom_exports: dict[str, SbomExport] = {}
        self.code_security_integrations: dict[str, CodeSecurityIntegration] = {}
        self.code_security_scan_configurations: dict[
            str, CodeSecurityScanConfiguration
        ] = {}
        self.code_security_scans: dict[str, dict[str, Any]] = {}
        self.ec2_deep_inspection_config: dict[str, Any] = {
            "packagePaths": [],
            "orgPackagePaths": [],
            "status": "DISABLED",
        }
        self.encryption_keys: dict[str, str] = {}
        self.configuration: dict[str, Any] = {
            "ecrConfiguration": {
                "rescanDuration": "LIFETIME",
            },
        }

    def create_filter(
        self,
        action: str,
        description: str,
        filter_criteria: dict[str, Any],
        name: str,
        reason: str,
        tags: dict[str, str],
    ) -> str:
        _filter = FilterResource(
            region=self.region_name,
            account_id=self.account_id,
            action=action,
            description=description,
            filter_criteria=filter_criteria,
            name=name,
            reason=reason,
            backend=self,
        )
        self.filters[_filter.arn] = _filter
        self.tag_resource(_filter.arn, tags)
        return _filter.arn

    def update_filter(
        self,
        filter_arn: str,
        action: Optional[str],
        description: Optional[str],
        filter_criteria: Optional[dict[str, Any]],
        name: Optional[str],
        reason: Optional[str],
    ) -> str:
        f = self.filters[filter_arn]
        if action is not None:
            f.action = action
        if description is not None:
            f.description = description
        if filter_criteria is not None:
            f.filter_criteria = filter_criteria
        if name is not None:
            f.name = name
        if reason is not None:
            f.reason = reason
        return f.arn

    def delete_filter(self, arn: str) -> None:
        self.filters.pop(arn, None)

    def list_filters(self, action: str, arns: list[str]) -> Iterable[FilterResource]:
        """
        Pagination is not yet implemented
        """
        return [
            f
            for f in self.filters.values()
            if (arns and f.arn in arns)
            or (action and f.action == action)
            or (not arns and not action)
        ]

    def list_findings(
        self,
        filter_criteria: list[dict[str, Any]],
        max_results: str,
        next_token: str,
        sort_criteria: str,
    ) -> list[dict[str, Any]]:
        """
        This call will always return 0 findings by default.

        You can use a dedicated API to override this, by configuring a queue of expected results.

        A request to `list_findings` will take the first result from that queue, and assign it to the provided arguments. Subsequent calls using the same arguments will return the same result. Other requests using a different SQL-query will take the next result from the queue, or return an empty result if the queue is empty.

        Configure this queue by making an HTTP request to `/moto-api/static/inspector2/findings-results`. An example invocation looks like this:

        .. sourcecode:: python

            findings = {
                "results": [
                    [{
                        "awsAccountId": "111122223333",
                        "codeVulnerabilityDetails": {"cwes": ["a"], "detectorId": ".."},
                    }],
                    # .. other findings as required
                ],
                "account_id": "123456789012",  # This is the default - can be omitted
                "region": "us-east-1",  # This is the default - can be omitted
            }
            resp = requests.post(
                "http://motoapi.amazonaws.com/moto-api/static/inspector2/findings-results",
                json=findings,
            )

            inspector2 = boto3.client("inspector2", region_name="us-east-1")
            findings = inspector2.list_findings()["findings"]

        """
        key = f"{json.dumps(filter_criteria)}--{max_results}--{next_token}--{sort_criteria}"
        if key not in self.findings and self.findings_queue:
            self.findings[key] = self.findings_queue.pop(0)
        if key in self.findings:
            return self.findings[key]
        else:
            return []

    def list_delegated_admin_accounts(self) -> dict[str, str]:
        return self.admin_accounts

    def enable_delegated_admin_account(self, account_id: str) -> None:
        self.admin_accounts[account_id] = "ENABLED"

    def disable_delegated_admin_account(self, account_id: str) -> None:
        self.admin_accounts[account_id] = "DISABLED"

    def get_delegated_admin_account(self) -> dict[str, Any]:
        for acct_id, status in self.admin_accounts.items():
            if status == "ENABLED":
                return {"accountId": acct_id, "status": status}
        return {}

    def describe_organization_configuration(self) -> dict[str, Any]:
        return {"autoEnable": self.org_config, "maxAccountLimitReached": False}

    def update_organization_configuration(
        self, auto_enable: dict[str, bool]
    ) -> dict[str, Any]:
        self.org_config.update(auto_enable)
        return {"autoEnable": self.org_config}

    def disable(
        self, account_ids: list[str], resource_types: list[str]
    ) -> list[dict[str, Any]]:
        for acct in account_ids:
            if acct not in self.account_status:
                self.account_status[acct] = AccountStatus(acct)
            self.account_status[acct].toggle(resource_types, enable=False)

        return [
            status.to_json()
            for a_id, status in self.account_status.items()
            if a_id in account_ids
        ]

    def enable(
        self, account_ids: list[str], resource_types: list[str]
    ) -> list[dict[str, Any]]:
        for acct in account_ids:
            if acct not in self.account_status:
                self.account_status[acct] = AccountStatus(acct)
            self.account_status[acct].toggle(resource_types, enable=True)

        return [
            status.to_json()
            for a_id, status in self.account_status.items()
            if a_id in account_ids
        ]

    def batch_get_account_status(self, account_ids: list[str]) -> list[dict[str, Any]]:
        return [
            status.to_batch_json()
            for a_id, status in self.account_status.items()
            if a_id in account_ids
        ]

    def batch_get_free_trial_info(
        self, account_ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        accounts = []
        for acct_id in account_ids:
            accounts.append(
                {
                    "accountId": acct_id,
                    "freeTrialInfo": [
                        {
                            "end": unix_time() + 86400 * 15,
                            "start": unix_time(),
                            "status": "ACTIVE",
                            "type": "EC2",
                        },
                        {
                            "end": unix_time() + 86400 * 15,
                            "start": unix_time(),
                            "status": "ACTIVE",
                            "type": "ECR",
                        },
                        {
                            "end": unix_time() + 86400 * 15,
                            "start": unix_time(),
                            "status": "ACTIVE",
                            "type": "LAMBDA",
                        },
                    ],
                }
            )
        return accounts, []

    def batch_get_code_snippet(
        self, finding_arns: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        errors = [
            {
                "findingArn": arn,
                "errorCode": "INTERNAL_ERROR",
                "errorMessage": "Finding not found",
            }
            for arn in finding_arns
        ]
        return [], errors

    def batch_get_finding_details(
        self, finding_arns: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        errors = [
            {
                "findingArn": arn,
                "errorCode": "INTERNAL_ERROR",
                "errorMessage": "Finding not found",
            }
            for arn in finding_arns
        ]
        return [], errors

    def batch_get_member_ec2_deep_inspection_status(
        self, account_ids: Optional[list[str]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        results = []
        if account_ids:
            for acct_id in account_ids:
                results.append(
                    {
                        "accountId": acct_id,
                        "status": "DISABLED",
                    }
                )
        return results, []

    def batch_update_member_ec2_deep_inspection_status(
        self, account_ids: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        results = []
        for item in account_ids:
            results.append(
                {
                    "accountId": item.get("accountId", ""),
                    "status": "SUCCESSFUL",
                }
            )
        return results, []

    def list_members(self) -> Iterable[Member]:
        return self.members.values()

    def associate_member(self, account_id: str) -> None:
        self.members[account_id] = Member(
            account_id=account_id, admin_account_id=self.account_id
        )

    def disassociate_member(self, account_id: str) -> None:
        self.members[account_id].status = "DISABLED"

    def get_member(self, account_id: str) -> Member:
        return self.members[account_id]

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(
            resource_arn, TaggingService.convert_dict_to_tags_input(tags)
        )

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def untag_resource(self, arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(arn, tag_keys)

    # CIS Scan Configuration operations

    def create_cis_scan_configuration(
        self,
        scan_name: str,
        security_level: str,
        schedule: dict[str, Any],
        targets: dict[str, Any],
        tags: Optional[dict[str, str]],
    ) -> str:
        config = CisScanConfiguration(
            region=self.region_name,
            account_id=self.account_id,
            scan_name=scan_name,
            security_level=security_level,
            schedule=schedule,
            targets=targets,
            backend=self,
        )
        self.cis_scan_configurations[config.arn] = config
        if tags:
            self.tag_resource(config.arn, tags)
        return config.arn

    def delete_cis_scan_configuration(self, scan_configuration_arn: str) -> str:
        self.cis_scan_configurations.pop(scan_configuration_arn, None)
        return scan_configuration_arn

    def list_cis_scan_configurations(self) -> list[CisScanConfiguration]:
        return list(self.cis_scan_configurations.values())

    def update_cis_scan_configuration(
        self,
        scan_configuration_arn: str,
        scan_name: Optional[str],
        security_level: Optional[str],
        schedule: Optional[dict[str, Any]],
        targets: Optional[dict[str, Any]],
    ) -> str:
        config = self.cis_scan_configurations.get(scan_configuration_arn)
        if config:
            if scan_name is not None:
                config.scan_name = scan_name
            if security_level is not None:
                config.security_level = security_level
            if schedule is not None:
                config.schedule = schedule
            if targets is not None:
                config.targets = targets
        return scan_configuration_arn

    def list_cis_scans(self) -> list[dict[str, Any]]:
        return []

    def get_cis_scan_report(
        self, scan_arn: str
    ) -> dict[str, Any]:
        return {"url": "", "status": "NO_FINDINGS_FOUND"}

    def get_cis_scan_result_details(
        self, scan_arn: str, target_resource_id: str, account_id: str
    ) -> list[dict[str, Any]]:
        return []

    def list_cis_scan_results_aggregated_by_checks(
        self, scan_arn: str
    ) -> list[dict[str, Any]]:
        return []

    def list_cis_scan_results_aggregated_by_target_resource(
        self, scan_arn: str
    ) -> list[dict[str, Any]]:
        return []

    def start_cis_session(
        self, scan_job_id: str, message: dict[str, Any]
    ) -> None:
        pass

    def stop_cis_session(
        self, scan_job_id: str, session_token: str, message: dict[str, Any]
    ) -> None:
        pass

    def send_cis_session_health(
        self, scan_job_id: str, session_token: str
    ) -> None:
        pass

    def send_cis_session_telemetry(
        self, scan_job_id: str, session_token: str, messages: list[dict[str, Any]]
    ) -> None:
        pass

    # Findings reports

    def create_findings_report(
        self,
        report_format: str,
        s3_destination: dict[str, Any],
        filter_criteria: Optional[dict[str, Any]],
    ) -> str:
        report = FindingsReport(
            region=self.region_name,
            account_id=self.account_id,
            report_format=report_format,
            s3_destination=s3_destination,
            filter_criteria=filter_criteria,
        )
        self.findings_reports[report.report_id] = report
        return report.report_id

    def cancel_findings_report(self, report_id: str) -> str:
        report = self.findings_reports.get(report_id)
        if report:
            report.status = "CANCELLED"
        return report_id

    def get_findings_report_status(
        self, report_id: Optional[str]
    ) -> dict[str, Any]:
        if report_id and report_id in self.findings_reports:
            return self.findings_reports[report_id].to_json()
        return {"reportId": report_id or "", "status": "NOT_FOUND"}

    # SBOM exports

    def create_sbom_export(
        self,
        report_format: str,
        s3_destination: dict[str, Any],
        resource_filter_criteria: Optional[dict[str, Any]],
    ) -> str:
        export = SbomExport(
            region=self.region_name,
            account_id=self.account_id,
            report_format=report_format,
            s3_destination=s3_destination,
            resource_filter_criteria=resource_filter_criteria,
        )
        self.sbom_exports[export.report_id] = export
        return export.report_id

    def cancel_sbom_export(self, report_id: str) -> str:
        export = self.sbom_exports.get(report_id)
        if export:
            export.status = "CANCELLED"
        return report_id

    def get_sbom_export(self, report_id: str) -> dict[str, Any]:
        if report_id in self.sbom_exports:
            return self.sbom_exports[report_id].to_json()
        return {"reportId": report_id, "status": "NOT_FOUND"}

    # Configuration

    def get_configuration(self) -> dict[str, Any]:
        return self.configuration

    def update_configuration(
        self,
        ecr_configuration: Optional[dict[str, Any]],
        ec2_configuration: Optional[dict[str, Any]],
    ) -> None:
        if ecr_configuration is not None:
            self.configuration["ecrConfiguration"] = ecr_configuration
        if ec2_configuration is not None:
            self.configuration["ec2Configuration"] = ec2_configuration

    # EC2 Deep Inspection

    def get_ec2_deep_inspection_configuration(self) -> dict[str, Any]:
        return self.ec2_deep_inspection_config

    def update_ec2_deep_inspection_configuration(
        self,
        activate_deep_inspection: Optional[bool],
        package_paths: Optional[list[str]],
    ) -> dict[str, Any]:
        if activate_deep_inspection is not None:
            self.ec2_deep_inspection_config["status"] = (
                "ACTIVATED" if activate_deep_inspection else "DEACTIVATED"
            )
        if package_paths is not None:
            self.ec2_deep_inspection_config["packagePaths"] = package_paths
        return self.ec2_deep_inspection_config

    def update_org_ec2_deep_inspection_configuration(
        self, org_package_paths: list[str]
    ) -> None:
        self.ec2_deep_inspection_config["orgPackagePaths"] = org_package_paths

    # Encryption key

    def get_encryption_key(
        self, scan_type: str, resource_type: str
    ) -> str:
        key = f"{scan_type}:{resource_type}"
        return self.encryption_keys.get(key, "")

    def update_encryption_key(
        self, kms_key_id: str, scan_type: str, resource_type: str
    ) -> None:
        key = f"{scan_type}:{resource_type}"
        self.encryption_keys[key] = kms_key_id

    def reset_encryption_key(self, scan_type: str, resource_type: str) -> None:
        key = f"{scan_type}:{resource_type}"
        self.encryption_keys.pop(key, None)

    # Coverage

    def list_coverage(self) -> list[dict[str, Any]]:
        return []

    def list_coverage_statistics(self) -> tuple[list[dict[str, Any]], int]:
        return [], 0

    # Finding aggregations

    def list_finding_aggregations(
        self, aggregation_type: str
    ) -> tuple[str, list[dict[str, Any]]]:
        return aggregation_type, []

    # Account permissions

    def list_account_permissions(self) -> list[dict[str, Any]]:
        return [
            {
                "service": "inspector2",
                "operation": "ENABLE_SCANNING",
            }
        ]

    # Usage totals

    def list_usage_totals(
        self, account_ids: Optional[list[str]]
    ) -> list[dict[str, Any]]:
        return []

    # Search vulnerabilities

    def search_vulnerabilities(
        self, filter_criteria: dict[str, Any]
    ) -> list[dict[str, Any]]:
        return []

    # Get clusters for image

    def get_clusters_for_image(
        self, image_filter: dict[str, Any]
    ) -> list[dict[str, Any]]:
        return []

    # Code Security Integration operations

    def create_code_security_integration(
        self,
        name: str,
        integration_type: str,
        details: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> tuple[str, str, str]:
        integration = CodeSecurityIntegration(
            region=self.region_name,
            account_id=self.account_id,
            name=name,
            integration_type=integration_type,
            details=details,
            backend=self,
        )
        self.code_security_integrations[integration.arn] = integration
        if tags:
            self.tag_resource(integration.arn, tags)
        return integration.arn, integration.status, ""

    def delete_code_security_integration(self, integration_arn: str) -> str:
        self.code_security_integrations.pop(integration_arn, None)
        return integration_arn

    def get_code_security_integration(
        self, integration_arn: str
    ) -> dict[str, Any]:
        integration = self.code_security_integrations.get(integration_arn)
        if integration:
            return integration.to_json()
        return {}

    def list_code_security_integrations(self) -> list[dict[str, Any]]:
        return [i.to_json() for i in self.code_security_integrations.values()]

    def update_code_security_integration(
        self, integration_arn: str, details: dict[str, Any]
    ) -> tuple[str, str]:
        integration = self.code_security_integrations.get(integration_arn)
        if integration:
            integration.details = details
            integration.last_update_on = unix_time()
            return integration.arn, integration.status
        return integration_arn, "NOT_FOUND"

    # Code Security Scan Configuration operations

    def create_code_security_scan_configuration(
        self,
        name: str,
        level: str,
        configuration: dict[str, Any],
        scope_settings: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> str:
        config = CodeSecurityScanConfiguration(
            region=self.region_name,
            account_id=self.account_id,
            name=name,
            level=level,
            configuration=configuration,
            scope_settings=scope_settings,
            backend=self,
        )
        self.code_security_scan_configurations[config.arn] = config
        if tags:
            self.tag_resource(config.arn, tags)
        return config.arn

    def delete_code_security_scan_configuration(
        self, scan_configuration_arn: str
    ) -> str:
        self.code_security_scan_configurations.pop(scan_configuration_arn, None)
        return scan_configuration_arn

    def get_code_security_scan_configuration(
        self, scan_configuration_arn: str
    ) -> dict[str, Any]:
        config = self.code_security_scan_configurations.get(scan_configuration_arn)
        if config:
            return config.to_json()
        return {}

    def list_code_security_scan_configurations(self) -> list[dict[str, Any]]:
        return [
            {"scanConfigurationArn": c.arn, "name": c.name, "level": c.level}
            for c in self.code_security_scan_configurations.values()
        ]

    def update_code_security_scan_configuration(
        self, scan_configuration_arn: str, configuration: dict[str, Any]
    ) -> str:
        config = self.code_security_scan_configurations.get(scan_configuration_arn)
        if config:
            config.configuration = configuration
            config.last_updated_at = unix_time()
        return scan_configuration_arn

    def batch_associate_code_security_scan_configuration(
        self, requests_list: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        successful = []
        failed = []
        for req in requests_list:
            arn = req.get("scanConfigurationArn", "")
            resource = req.get("resource", {})
            config = self.code_security_scan_configurations.get(arn)
            if config:
                config.associations.append(resource)
                successful.append(
                    {"scanConfigurationArn": arn, "resource": resource}
                )
            else:
                failed.append(
                    {
                        "scanConfigurationArn": arn,
                        "resource": resource,
                        "errorCode": "INTERNAL_ERROR",
                        "errorMessage": "Configuration not found",
                    }
                )
        return failed, successful

    def batch_disassociate_code_security_scan_configuration(
        self, requests_list: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        successful = []
        failed = []
        for req in requests_list:
            arn = req.get("scanConfigurationArn", "")
            resource = req.get("resource", {})
            config = self.code_security_scan_configurations.get(arn)
            if config:
                successful.append(
                    {"scanConfigurationArn": arn, "resource": resource}
                )
            else:
                failed.append(
                    {
                        "scanConfigurationArn": arn,
                        "resource": resource,
                        "errorCode": "INTERNAL_ERROR",
                        "errorMessage": "Configuration not found",
                    }
                )
        return failed, successful

    def list_code_security_scan_configuration_associations(
        self, scan_configuration_arn: str
    ) -> list[dict[str, Any]]:
        config = self.code_security_scan_configurations.get(scan_configuration_arn)
        if config:
            return [
                {"scanConfigurationArn": scan_configuration_arn, "resource": r}
                for r in config.associations
            ]
        return []

    def start_code_security_scan(
        self, resource: dict[str, Any]
    ) -> tuple[str, str]:
        scan_id = mock_random.get_random_hex(16)
        self.code_security_scans[scan_id] = {
            "scanId": scan_id,
            "resource": resource,
            "accountId": self.account_id,
            "status": "IN_PROGRESS",
            "createdAt": unix_time(),
            "updatedAt": unix_time(),
        }
        return scan_id, "IN_PROGRESS"

    def get_code_security_scan(
        self, resource: dict[str, Any], scan_id: str
    ) -> dict[str, Any]:
        scan = self.code_security_scans.get(scan_id)
        if scan:
            return scan
        return {
            "scanId": scan_id,
            "resource": resource,
            "accountId": self.account_id,
            "status": "NOT_FOUND",
            "createdAt": unix_time(),
            "updatedAt": unix_time(),
        }


inspector2_backends = BackendDict(Inspector2Backend, "inspector2")
