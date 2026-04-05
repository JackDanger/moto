from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.moto_api._internal import mock_random
from moto.utilities.utils import get_partition

from .exceptions import (
    DetectorNotFoundException,
    FilterNotFoundException,
    IPSetNotFoundException,
    ResourceNotFoundException,
    ThreatIntelSetNotFoundException,
)


class GuardDutyBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.admin_account_ids: list[str] = []
        self.detectors: dict[str, Detector] = {}
        self.malware_protection_plans: dict[str, MalwareProtectionPlan] = {}
        self.admin_accounts: dict[
            str, Detector
        ] = {}  # Store admin accounts by detector_id

    def create_detector(
        self,
        enable: bool,
        finding_publishing_frequency: str,
        data_sources: dict[str, Any],
        tags: dict[str, str],
        features: list[dict[str, Any]],
    ) -> str:
        if finding_publishing_frequency not in [
            "FIFTEEN_MINUTES",
            "ONE_HOUR",
            "SIX_HOURS",
        ]:
            finding_publishing_frequency = "SIX_HOURS"

        detector = Detector(
            account_id=self.account_id,
            region_name=self.region_name,
            created_at=datetime.now(),
            finding_publish_freq=finding_publishing_frequency,
            enabled=enable,
            datasources=data_sources,
            tags=tags,
            features=features,
        )
        self.detectors[detector.id] = detector
        return detector.id

    def create_filter(
        self,
        detector_id: str,
        name: str,
        action: str,
        description: str,
        finding_criteria: dict[str, Any],
        rank: int,
    ) -> None:
        detector = self.get_detector(detector_id)
        _filter = Filter(name, action, description, finding_criteria, rank)
        detector.add_filter(_filter)

    def delete_detector(self, detector_id: str) -> None:
        self.detectors.pop(detector_id, None)

    def delete_filter(self, detector_id: str, filter_name: str) -> None:
        detector = self.get_detector(detector_id)
        detector.delete_filter(filter_name)

    def enable_organization_admin_account(self, admin_account_id: str) -> None:
        self.admin_account_ids.append(admin_account_id)

    def list_organization_admin_accounts(self) -> list[str]:
        """
        Pagination is not yet implemented
        """
        return self.admin_account_ids

    def list_detectors(
        self,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> tuple[list[str], str | None]:
        all_ids = [d.id for d in self.detectors.values()]
        start = 0
        if next_token:
            try:
                start = all_ids.index(next_token)
            except ValueError:
                start = 0
        limit = int(max_results) if max_results else len(all_ids)
        page = all_ids[start : start + limit]
        new_next_token = all_ids[start + limit] if start + limit < len(all_ids) else None
        return page, new_next_token

    def get_detector(self, detector_id: str) -> "Detector":
        if detector_id not in self.detectors:
            raise DetectorNotFoundException
        return self.detectors[detector_id]

    def get_administrator_account(self, detector_id: str) -> dict[str, Any]:
        """Get administrator account details."""
        detector = self.get_detector(detector_id)

        # Check detector-level administrator first (from AcceptAdministratorInvitation)
        if detector.administrator_id:
            return {
                "administrator": {
                    "accountId": detector.administrator_id,
                    "relationshipStatus": "ENABLED",
                }
            }

        if not self.admin_account_ids:
            return {}

        return {
            "administrator": {
                "accountId": self.admin_account_ids[0],
                "relationshipStatus": "ENABLED",
            }
        }

    def get_filter(self, detector_id: str, filter_name: str) -> "Filter":
        detector = self.get_detector(detector_id)
        return detector.get_filter(filter_name)

    def list_filters(
        self,
        detector_id: str,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> tuple[list[str], str | None]:
        detector = self.get_detector(detector_id)
        all_names = list(detector.filters.keys())
        start = 0
        if next_token:
            try:
                start = all_names.index(next_token)
            except ValueError:
                start = 0
        limit = int(max_results) if max_results else len(all_names)
        page = all_names[start : start + limit]
        new_next_token = all_names[start + limit] if start + limit < len(all_names) else None
        return page, new_next_token

    def update_detector(
        self,
        detector_id: str,
        enable: bool,
        finding_publishing_frequency: str,
        data_sources: dict[str, Any],
        features: list[dict[str, Any]],
    ) -> None:
        detector = self.get_detector(detector_id)
        detector.update(enable, finding_publishing_frequency, data_sources, features)

    def update_filter(
        self,
        detector_id: str,
        filter_name: str,
        action: str,
        description: str,
        finding_criteria: dict[str, Any],
        rank: int,
    ) -> None:
        detector = self.get_detector(detector_id)
        detector.update_filter(
            filter_name,
            action=action,
            description=description,
            finding_criteria=finding_criteria,
            rank=rank,
        )

    # IPSet operations
    def create_ip_set(
        self,
        detector_id: str,
        name: str,
        ip_format: str,
        location: str,
        activate: bool,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        detector = self.get_detector(detector_id)
        ip_set = IPSet(
            account_id=self.account_id,
            region_name=self.region_name,
            detector_id=detector_id,
            name=name,
            ip_format=ip_format,
            location=location,
            activate=activate,
            tags=tags,
        )
        detector.ip_sets[ip_set.id] = ip_set
        return ip_set.id

    def get_ip_set(self, detector_id: str, ip_set_id: str) -> "IPSet":
        detector = self.get_detector(detector_id)
        if ip_set_id not in detector.ip_sets:
            raise IPSetNotFoundException
        return detector.ip_sets[ip_set_id]

    def update_ip_set(
        self,
        detector_id: str,
        ip_set_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        activate: Optional[bool] = None,
    ) -> None:
        ip_set = self.get_ip_set(detector_id, ip_set_id)
        if name is not None:
            ip_set.name = name
        if location is not None:
            ip_set.location = location
        if activate is not None:
            ip_set.status = "ACTIVE" if activate else "INACTIVE"

    def delete_ip_set(self, detector_id: str, ip_set_id: str) -> None:
        detector = self.get_detector(detector_id)
        if ip_set_id not in detector.ip_sets:
            raise IPSetNotFoundException
        del detector.ip_sets[ip_set_id]

    def list_ip_sets(
        self,
        detector_id: str,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> tuple[list[str], str | None]:
        detector = self.get_detector(detector_id)
        all_ids = list(detector.ip_sets.keys())
        start = 0
        if next_token:
            try:
                start = all_ids.index(next_token)
            except ValueError:
                start = 0
        limit = int(max_results) if max_results else len(all_ids)
        page = all_ids[start : start + limit]
        new_next_token = all_ids[start + limit] if start + limit < len(all_ids) else None
        return page, new_next_token

    # ThreatIntelSet operations
    def create_threat_intel_set(
        self,
        detector_id: str,
        name: str,
        tis_format: str,
        location: str,
        activate: bool,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        detector = self.get_detector(detector_id)
        threat_intel_set = ThreatIntelSet(
            account_id=self.account_id,
            region_name=self.region_name,
            detector_id=detector_id,
            name=name,
            tis_format=tis_format,
            location=location,
            activate=activate,
            tags=tags,
        )
        detector.threat_intel_sets[threat_intel_set.id] = threat_intel_set
        return threat_intel_set.id

    def get_threat_intel_set(
        self, detector_id: str, threat_intel_set_id: str
    ) -> "ThreatIntelSet":
        detector = self.get_detector(detector_id)
        if threat_intel_set_id not in detector.threat_intel_sets:
            raise ThreatIntelSetNotFoundException
        return detector.threat_intel_sets[threat_intel_set_id]

    def update_threat_intel_set(
        self,
        detector_id: str,
        threat_intel_set_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        activate: Optional[bool] = None,
    ) -> None:
        tis = self.get_threat_intel_set(detector_id, threat_intel_set_id)
        if name is not None:
            tis.name = name
        if location is not None:
            tis.location = location
        if activate is not None:
            tis.status = "ACTIVE" if activate else "INACTIVE"

    def delete_threat_intel_set(
        self, detector_id: str, threat_intel_set_id: str
    ) -> None:
        detector = self.get_detector(detector_id)
        if threat_intel_set_id not in detector.threat_intel_sets:
            raise ThreatIntelSetNotFoundException
        del detector.threat_intel_sets[threat_intel_set_id]

    def list_threat_intel_sets(
        self,
        detector_id: str,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> tuple[list[str], str | None]:
        detector = self.get_detector(detector_id)
        all_ids = list(detector.threat_intel_sets.keys())
        start = 0
        if next_token:
            try:
                start = all_ids.index(next_token)
            except ValueError:
                start = 0
        limit = int(max_results) if max_results else len(all_ids)
        page = all_ids[start : start + limit]
        new_next_token = all_ids[start + limit] if start + limit < len(all_ids) else None
        return page, new_next_token

    # Tagging operations
    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        resource = self._get_resource_by_arn(resource_arn)
        resource.tags.update(tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        resource = self._get_resource_by_arn(resource_arn)
        for key in tag_keys:
            resource.tags.pop(key, None)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        resource = self._get_resource_by_arn(resource_arn)
        return dict(resource.tags)

    # Findings operations
    def create_sample_findings(
        self, detector_id: str, finding_types: list[str]
    ) -> None:
        detector = self.get_detector(detector_id)
        for ft in finding_types or []:
            finding_id = mock_random.get_random_hex(length=32)
            detector.findings[finding_id] = {
                "accountId": self.account_id,
                "arn": (
                    f"arn:{get_partition(self.region_name)}:guardduty:"
                    f"{self.region_name}:{self.account_id}:"
                    f"detector/{detector_id}/finding/{finding_id}"
                ),
                "id": finding_id,
                "region": self.region_name,
                "type": ft,
                "severity": 5.0,
                "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "resource": {},
                "service": {"serviceName": "guardduty"},
            }

    def get_findings(
        self, detector_id: str, finding_ids: list[str]
    ) -> list[dict[str, Any]]:
        detector = self.get_detector(detector_id)
        results = []
        for fid in finding_ids or []:
            if fid in detector.findings:
                results.append(detector.findings[fid])
        return results

    def list_findings(
        self,
        detector_id: str,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> tuple[list[str], str | None]:
        detector = self.get_detector(detector_id)
        all_ids = list(detector.findings.keys())
        start = 0
        if next_token:
            try:
                start = all_ids.index(next_token)
            except ValueError:
                start = 0
        limit = int(max_results) if max_results else len(all_ids)
        page = all_ids[start : start + limit]
        new_next_token = all_ids[start + limit] if start + limit < len(all_ids) else None
        return page, new_next_token

    def get_findings_statistics(self, detector_id: str) -> dict[str, Any]:
        detector = self.get_detector(detector_id)
        count_by_severity: dict[str, int] = {}
        for finding in detector.findings.values():
            sev = str(finding.get("severity", 0))
            count_by_severity[sev] = count_by_severity.get(sev, 0) + 1
        return {"countBySeverity": count_by_severity}

    # Organization / admin operations
    def describe_organization_configuration(self, detector_id: str) -> dict[str, Any]:
        self.get_detector(detector_id)
        return {
            "autoEnable": False,
            "memberAccountLimitReached": False,
            "dataSources": {
                "s3Logs": {"autoEnable": False},
                "kubernetes": {"auditLogs": {"autoEnable": False}},
                "malwareProtection": {
                    "scanEc2InstanceWithFindings": {"ebsVolumes": {"autoEnable": False}}
                },
            },
            "autoEnableOrganizationMembers": "NONE",
            "features": [],
        }

    def get_master_account(self, detector_id: str) -> dict[str, Any]:
        self.get_detector(detector_id)
        if not self.admin_account_ids:
            return {}
        return {
            "master": {
                "accountId": self.admin_account_ids[0],
                "relationshipStatus": "ENABLED",
            }
        }

    def get_member_detectors(
        self, detector_id: str, account_ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        self.get_detector(detector_id)
        members = []
        unprocessed = []
        for acct_id in account_ids or []:
            members.append(
                {
                    "accountId": acct_id,
                    "dataSources": {
                        "cloudTrail": {"status": "DISABLED"},
                        "dnsLogs": {"status": "DISABLED"},
                        "flowLogs": {"status": "DISABLED"},
                        "s3Logs": {"status": "DISABLED"},
                        "kubernetes": {"auditLogs": {"status": "DISABLED"}},
                        "malwareProtection": {
                            "scanEc2InstanceWithFindings": {
                                "ebsVolumes": {"status": "DISABLED"}
                            },
                        },
                    },
                    "features": [],
                }
            )
        return members, unprocessed

    def get_remaining_free_trial_days(
        self, detector_id: str, account_ids: list[str]
    ) -> list[dict[str, Any]]:
        self.get_detector(detector_id)
        accounts = []
        target_ids = account_ids if account_ids else [self.account_id]
        for acct_id in target_ids:
            accounts.append(
                {
                    "accountId": acct_id,
                    "dataSources": {
                        "cloudTrail": {"freeTrialDaysRemaining": 0},
                        "dnsLogs": {"freeTrialDaysRemaining": 0},
                        "flowLogs": {"freeTrialDaysRemaining": 0},
                        "s3Logs": {"freeTrialDaysRemaining": 0},
                        "kubernetes": {"auditLogs": {"freeTrialDaysRemaining": 0}},
                        "malwareProtection": {
                            "scanEc2InstanceWithFindings": {
                                "ebsVolumes": {"freeTrialDaysRemaining": 0}
                            },
                        },
                    },
                    "features": [],
                }
            )
        return accounts

    def get_usage_statistics(self, detector_id: str) -> dict[str, Any]:
        self.get_detector(detector_id)
        return {
            "usageStatistics": {
                "sumByAccount": [],
                "sumByDataSource": [],
                "sumByResource": [],
                "sumByFeature": [],
                "topResources": [],
            }
        }

    # Invitations
    def list_invitations(self) -> list[dict[str, Any]]:
        return []

    # Malware scan operations
    def describe_malware_scans(self, detector_id: str) -> list[dict[str, Any]]:
        self.get_detector(detector_id)
        return []

    def get_malware_scan_settings(self, detector_id: str) -> dict[str, Any]:
        self.get_detector(detector_id)
        return {
            "scanResourceCriteria": {
                "include": {},
                "exclude": {},
            },
            "ebsSnapshotPreservation": "NO_RETENTION",
        }

    # Publishing destinations
    def create_publishing_destination(
        self,
        detector_id: str,
        destination_type: str,
        destination_properties: dict[str, str],
    ) -> str:
        detector = self.get_detector(detector_id)
        dest_id = mock_random.get_random_hex(length=32)
        detector.publishing_destinations[dest_id] = {
            "destinationId": dest_id,
            "destinationType": destination_type,
            "destinationProperties": destination_properties or {},
            "publishingFailureStartTimestamp": 0,
            "status": "PUBLISHING",
        }
        return dest_id

    def describe_publishing_destination(
        self, detector_id: str, destination_id: str
    ) -> dict[str, Any]:
        detector = self.get_detector(detector_id)
        if destination_id not in detector.publishing_destinations:
            raise ResourceNotFoundException(
                f"arn:{get_partition(self.region_name)}:guardduty:"
                f"{self.region_name}:{self.account_id}:"
                f"detector/{detector_id}/publishingDestination/{destination_id}"
            )
        return detector.publishing_destinations[destination_id]

    def list_publishing_destinations(self, detector_id: str) -> list[dict[str, Any]]:
        detector = self.get_detector(detector_id)
        return [
            {
                "destinationId": d["destinationId"],
                "destinationType": d["destinationType"],
                "status": d["status"],
            }
            for d in detector.publishing_destinations.values()
        ]

    def update_publishing_destination(
        self,
        detector_id: str,
        destination_id: str,
        destination_properties: Optional[dict[str, str]] = None,
    ) -> None:
        dest = self.describe_publishing_destination(detector_id, destination_id)
        if destination_properties is not None:
            dest["destinationProperties"] = destination_properties

    def delete_publishing_destination(
        self, detector_id: str, destination_id: str
    ) -> None:
        detector = self.get_detector(detector_id)
        if destination_id not in detector.publishing_destinations:
            raise ResourceNotFoundException(
                f"arn:{get_partition(self.region_name)}:guardduty:"
                f"{self.region_name}:{self.account_id}:"
                f"detector/{detector_id}/publishingDestination/{destination_id}"
            )
        del detector.publishing_destinations[destination_id]

    # Members operations
    def create_members(
        self,
        detector_id: str,
        account_details: list[dict[str, str]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        detector = self.get_detector(detector_id)
        unprocessed: list[dict[str, Any]] = []
        for detail in account_details or []:
            acct_id = detail.get("accountId", "")
            email = detail.get("email", "")
            detector.members[acct_id] = {
                "accountId": acct_id,
                "email": email,
                "detectorId": detector_id,
                "masterId": self.account_id,
                "administratorId": self.account_id,
                "relationshipStatus": "CREATED",
                "invitedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        return [], unprocessed

    def get_members(
        self,
        detector_id: str,
        account_ids: list[str],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        detector = self.get_detector(detector_id)
        members: list[dict[str, Any]] = []
        unprocessed: list[dict[str, Any]] = []
        for acct_id in account_ids or []:
            if acct_id in detector.members:
                members.append(detector.members[acct_id])
            else:
                unprocessed.append(
                    {
                        "accountId": acct_id,
                        "result": "Account not found as a member",
                    }
                )
        return members, unprocessed

    def list_members(self, detector_id: str) -> list[dict[str, Any]]:
        detector = self.get_detector(detector_id)
        return list(detector.members.values())

    def delete_members(
        self,
        detector_id: str,
        account_ids: list[str],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        detector = self.get_detector(detector_id)
        unprocessed: list[dict[str, Any]] = []
        for acct_id in account_ids or []:
            if acct_id in detector.members:
                del detector.members[acct_id]
            else:
                unprocessed.append(
                    {
                        "accountId": acct_id,
                        "result": "Account not found as a member",
                    }
                )
        return [], unprocessed

    def start_monitoring_members(
        self,
        detector_id: str,
        account_ids: list[str],
    ) -> list[dict[str, Any]]:
        detector = self.get_detector(detector_id)
        unprocessed: list[dict[str, Any]] = []
        for acct_id in account_ids or []:
            if acct_id in detector.members:
                detector.members[acct_id]["relationshipStatus"] = "ENABLED"
            else:
                unprocessed.append(
                    {
                        "accountId": acct_id,
                        "result": "Account not found as a member",
                    }
                )
        return unprocessed

    def stop_monitoring_members(
        self,
        detector_id: str,
        account_ids: list[str],
    ) -> list[dict[str, Any]]:
        detector = self.get_detector(detector_id)
        unprocessed: list[dict[str, Any]] = []
        for acct_id in account_ids or []:
            if acct_id in detector.members:
                detector.members[acct_id]["relationshipStatus"] = "DISABLED"
            else:
                unprocessed.append(
                    {
                        "accountId": acct_id,
                        "result": "Account not found as a member",
                    }
                )
        return unprocessed

    # Organization admin operations
    def accept_administrator_invitation(
        self,
        detector_id: str,
        administrator_id: str,
        invitation_id: str,
    ) -> None:
        detector = self.get_detector(detector_id)
        detector.administrator_id = administrator_id
        detector.invitation_id = invitation_id

    def disable_organization_admin_account(self, admin_account_id: str) -> None:
        if admin_account_id in self.admin_account_ids:
            self.admin_account_ids.remove(admin_account_id)

    def update_organization_configuration(
        self,
        detector_id: str,
        auto_enable: Optional[bool] = None,
        data_sources: Optional[dict[str, Any]] = None,
        features: Optional[list[dict[str, Any]]] = None,
        auto_enable_organization_members: Optional[str] = None,
    ) -> None:
        self.get_detector(detector_id)

    # Coverage statistics
    def get_coverage_statistics(self, detector_id: str) -> dict[str, Any]:
        self.get_detector(detector_id)
        return {
            "coverageStatistics": {
                "countByResourceType": {},
                "countByCoverageStatus": {},
            }
        }

    def list_coverage(self, detector_id: str) -> list[dict[str, Any]]:
        self.get_detector(detector_id)
        return []

    # Archive / Unarchive findings
    def archive_findings(self, detector_id: str, finding_ids: list[str]) -> None:
        detector = self.get_detector(detector_id)
        for fid in finding_ids or []:
            if fid in detector.findings:
                detector.findings[fid]["service"]["archived"] = True

    def unarchive_findings(self, detector_id: str, finding_ids: list[str]) -> None:
        detector = self.get_detector(detector_id)
        for fid in finding_ids or []:
            if fid in detector.findings:
                detector.findings[fid]["service"]["archived"] = False

    def update_findings_feedback(
        self, detector_id: str, finding_ids: list[str], feedback: str
    ) -> None:
        detector = self.get_detector(detector_id)
        for fid in finding_ids or []:
            if fid in detector.findings:
                detector.findings[fid]["service"]["userFeedback"] = feedback

    # Invitation operations
    def accept_invitation(
        self, detector_id: str, master_id: str, invitation_id: str
    ) -> None:
        detector = self.get_detector(detector_id)
        detector.administrator_id = master_id
        detector.invitation_id = invitation_id

    def invite_members(
        self, detector_id: str, account_ids: list[str]
    ) -> list[dict[str, Any]]:
        detector = self.get_detector(detector_id)
        unprocessed: list[dict[str, Any]] = []
        for acct_id in account_ids or []:
            if acct_id in detector.members:
                detector.members[acct_id]["relationshipStatus"] = "INVITED"
            else:
                unprocessed.append(
                    {
                        "accountId": acct_id,
                        "result": "Account not found as a member",
                    }
                )
        return unprocessed

    def disassociate_members(
        self, detector_id: str, account_ids: list[str]
    ) -> list[dict[str, Any]]:
        detector = self.get_detector(detector_id)
        unprocessed: list[dict[str, Any]] = []
        for acct_id in account_ids or []:
            if acct_id in detector.members:
                detector.members[acct_id]["relationshipStatus"] = "REMOVED"
            else:
                unprocessed.append(
                    {
                        "accountId": acct_id,
                        "result": "Account not found as a member",
                    }
                )
        return unprocessed

    def disassociate_from_administrator_account(self, detector_id: str) -> None:
        detector = self.get_detector(detector_id)
        detector.administrator_id = None
        detector.invitation_id = None

    def disassociate_from_master_account(self, detector_id: str) -> None:
        self.disassociate_from_administrator_account(detector_id)

    def decline_invitations(self, account_ids: list[str]) -> list[dict[str, Any]]:
        # In a mock, we just accept this
        return []

    def delete_invitations(self, account_ids: list[str]) -> list[dict[str, Any]]:
        return []

    def get_invitations_count(self) -> int:
        return 0

    def update_member_detectors(
        self,
        detector_id: str,
        account_ids: list[str],
        data_sources: Optional[dict[str, Any]] = None,
        features: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        self.get_detector(detector_id)
        return []

    def get_organization_statistics(self) -> dict[str, Any]:
        return {
            "organizationDetails": {
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "organizationStatistics": {
                    "totalAccountsCount": 0,
                    "memberAccountsCount": 0,
                    "activeAccountsCount": 0,
                    "enabledAccountsCount": 0,
                    "countByFeature": [],
                },
            }
        }

    # MalwareProtectionPlan operations
    def create_malware_protection_plan(
        self,
        role: str,
        protected_resource: Optional[dict[str, Any]] = None,
        actions: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        plan = MalwareProtectionPlan(
            account_id=self.account_id,
            region_name=self.region_name,
            role=role,
            protected_resource=protected_resource,
            actions=actions,
            tags=tags,
        )
        self.malware_protection_plans[plan.id] = plan
        return plan.id

    def get_malware_protection_plan(self, plan_id: str) -> "MalwareProtectionPlan":
        if plan_id not in self.malware_protection_plans:
            raise ResourceNotFoundException(
                f"arn:{get_partition(self.region_name)}:guardduty:"
                f"{self.region_name}:{self.account_id}:"
                f"malware-protection-plan/{plan_id}"
            )
        return self.malware_protection_plans[plan_id]

    def delete_malware_protection_plan(self, plan_id: str) -> None:
        if plan_id not in self.malware_protection_plans:
            raise ResourceNotFoundException(
                f"arn:{get_partition(self.region_name)}:guardduty:"
                f"{self.region_name}:{self.account_id}:"
                f"malware-protection-plan/{plan_id}"
            )
        del self.malware_protection_plans[plan_id]

    def list_malware_protection_plans(self) -> list[dict[str, Any]]:
        return [
            {"malwareProtectionPlanId": pid} for pid in self.malware_protection_plans
        ]

    def update_malware_protection_plan(
        self,
        plan_id: str,
        role: Optional[str] = None,
        actions: Optional[dict[str, Any]] = None,
        protected_resource: Optional[dict[str, Any]] = None,
    ) -> None:
        plan = self.get_malware_protection_plan(plan_id)
        if role is not None:
            plan.role = role
        if actions is not None:
            plan.actions = actions
        if protected_resource is not None:
            plan.protected_resource = protected_resource

    # Malware scan additional operations
    def get_malware_scan(self, scan_id: str) -> dict[str, Any]:
        return {
            "scanId": scan_id,
            "status": "COMPLETED",
            "scanStartTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "scanEndTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "triggerDetails": {},
            "resourceDetails": {},
            "scanResultDetails": {"scanResult": "CLEAN"},
            "totalBytes": 0,
            "fileCount": 0,
        }

    def list_malware_scans(self) -> list[dict[str, Any]]:
        return []

    def start_malware_scan(self, resource_arn: str) -> str:
        scan_id = mock_random.get_random_hex(length=32)
        return scan_id

    def send_object_malware_scan(self, object_key: str, bucket_name: str) -> str:
        scan_id = mock_random.get_random_hex(length=32)
        return scan_id

    def update_malware_scan_settings(
        self,
        detector_id: str,
        scan_resource_criteria: Optional[dict[str, Any]] = None,
        ebs_snapshot_preservation: Optional[str] = None,
    ) -> None:
        self.get_detector(detector_id)

    # ThreatEntitySet operations
    def create_threat_entity_set(
        self,
        detector_id: str,
        name: str,
        entity_type: str,
        location: str,
        activate: bool,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        detector = self.get_detector(detector_id)
        tes = ThreatEntitySet(
            account_id=self.account_id,
            region_name=self.region_name,
            detector_id=detector_id,
            name=name,
            entity_type=entity_type,
            location=location,
            activate=activate,
            tags=tags,
        )
        detector.threat_entity_sets[tes.id] = tes
        return tes.id

    def get_threat_entity_set(
        self, detector_id: str, threat_entity_set_id: str
    ) -> "ThreatEntitySet":
        detector = self.get_detector(detector_id)
        if threat_entity_set_id not in detector.threat_entity_sets:
            raise ResourceNotFoundException(
                f"arn:{get_partition(self.region_name)}:guardduty:"
                f"{self.region_name}:{self.account_id}:"
                f"detector/{detector_id}/threatentityset/{threat_entity_set_id}"
            )
        return detector.threat_entity_sets[threat_entity_set_id]

    def delete_threat_entity_set(
        self, detector_id: str, threat_entity_set_id: str
    ) -> None:
        detector = self.get_detector(detector_id)
        if threat_entity_set_id not in detector.threat_entity_sets:
            raise ResourceNotFoundException(
                f"arn:{get_partition(self.region_name)}:guardduty:"
                f"{self.region_name}:{self.account_id}:"
                f"detector/{detector_id}/threatentityset/{threat_entity_set_id}"
            )
        del detector.threat_entity_sets[threat_entity_set_id]

    def list_threat_entity_sets(self, detector_id: str) -> list[str]:
        detector = self.get_detector(detector_id)
        return list(detector.threat_entity_sets.keys())

    def update_threat_entity_set(
        self,
        detector_id: str,
        threat_entity_set_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        activate: Optional[bool] = None,
    ) -> None:
        tes = self.get_threat_entity_set(detector_id, threat_entity_set_id)
        if name is not None:
            tes.name = name
        if location is not None:
            tes.location = location
        if activate is not None:
            tes.status = "ACTIVE" if activate else "INACTIVE"

    # TrustedEntitySet operations
    def create_trusted_entity_set(
        self,
        detector_id: str,
        name: str,
        entity_type: str,
        location: str,
        activate: bool,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        detector = self.get_detector(detector_id)
        tes = TrustedEntitySet(
            account_id=self.account_id,
            region_name=self.region_name,
            detector_id=detector_id,
            name=name,
            entity_type=entity_type,
            location=location,
            activate=activate,
            tags=tags,
        )
        detector.trusted_entity_sets[tes.id] = tes
        return tes.id

    def get_trusted_entity_set(
        self, detector_id: str, trusted_entity_set_id: str
    ) -> "TrustedEntitySet":
        detector = self.get_detector(detector_id)
        if trusted_entity_set_id not in detector.trusted_entity_sets:
            raise ResourceNotFoundException(
                f"arn:{get_partition(self.region_name)}:guardduty:"
                f"{self.region_name}:{self.account_id}:"
                f"detector/{detector_id}/trustedentityset/{trusted_entity_set_id}"
            )
        return detector.trusted_entity_sets[trusted_entity_set_id]

    def delete_trusted_entity_set(
        self, detector_id: str, trusted_entity_set_id: str
    ) -> None:
        detector = self.get_detector(detector_id)
        if trusted_entity_set_id not in detector.trusted_entity_sets:
            raise ResourceNotFoundException(
                f"arn:{get_partition(self.region_name)}:guardduty:"
                f"{self.region_name}:{self.account_id}:"
                f"detector/{detector_id}/trustedentityset/{trusted_entity_set_id}"
            )
        del detector.trusted_entity_sets[trusted_entity_set_id]

    def list_trusted_entity_sets(self, detector_id: str) -> list[str]:
        detector = self.get_detector(detector_id)
        return list(detector.trusted_entity_sets.keys())

    def update_trusted_entity_set(
        self,
        detector_id: str,
        trusted_entity_set_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        activate: Optional[bool] = None,
    ) -> None:
        tes = self.get_trusted_entity_set(detector_id, trusted_entity_set_id)
        if name is not None:
            tes.name = name
        if location is not None:
            tes.location = location
        if activate is not None:
            tes.status = "ACTIVE" if activate else "INACTIVE"

    def _get_resource_by_arn(self, resource_arn: str) -> Any:
        """Find a resource (detector, ipset, threatintelset) by its ARN."""
        # Try detectors
        for detector in self.detectors.values():
            if detector.arn == resource_arn:
                return detector
            # Try ipsets within detector
            for ip_set in detector.ip_sets.values():
                if ip_set.arn == resource_arn:
                    return ip_set
            # Try threatintelsets within detector
            for tis in detector.threat_intel_sets.values():
                if tis.arn == resource_arn:
                    return tis
        raise ResourceNotFoundException(resource_arn)


class Filter(BaseModel):
    def __init__(
        self,
        name: str,
        action: str,
        description: str,
        finding_criteria: dict[str, Any],
        rank: int,
    ):
        self.name = name
        self.action = action
        self.description = description
        self.finding_criteria = finding_criteria
        self.rank = rank or 1

    def update(
        self,
        action: Optional[str],
        description: Optional[str],
        finding_criteria: Optional[dict[str, Any]],
        rank: Optional[int],
    ) -> None:
        if action is not None:
            self.action = action
        if description is not None:
            self.description = description
        if finding_criteria is not None:
            self.finding_criteria = finding_criteria
        if rank is not None:
            self.rank = rank

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "action": self.action,
            "description": self.description,
            "findingCriteria": self.finding_criteria,
            "rank": self.rank,
        }


class IPSet(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        detector_id: str,
        name: str,
        ip_format: str,
        location: str,
        activate: bool,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = mock_random.get_random_hex(length=32)
        self.name = name
        self.format = ip_format
        self.location = location
        self.status = "ACTIVE" if activate else "INACTIVE"
        self.tags: dict[str, str] = tags or {}
        partition = get_partition(region_name)
        self.arn = (
            f"arn:{partition}:guardduty:{region_name}:{account_id}"
            f":detector/{detector_id}/ipset/{self.id}"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "format": self.format,
            "location": self.location,
            "status": self.status,
            "tags": self.tags,
        }


class ThreatIntelSet(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        detector_id: str,
        name: str,
        tis_format: str,
        location: str,
        activate: bool,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = mock_random.get_random_hex(length=32)
        self.name = name
        self.format = tis_format
        self.location = location
        self.status = "ACTIVE" if activate else "INACTIVE"
        self.tags: dict[str, str] = tags or {}
        partition = get_partition(region_name)
        self.arn = (
            f"arn:{partition}:guardduty:{region_name}:{account_id}"
            f":detector/{detector_id}/threatintelset/{self.id}"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "format": self.format,
            "location": self.location,
            "status": self.status,
            "tags": self.tags,
        }


class Detector(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        created_at: datetime,
        finding_publish_freq: str,
        enabled: bool,
        datasources: dict[str, Any],
        tags: dict[str, str],
        features: list[dict[str, Any]],
    ):
        self.id = mock_random.get_random_hex(length=32)
        self.created_at = created_at
        self.finding_publish_freq = finding_publish_freq
        partition = get_partition(region_name)
        self.service_role = (
            f"arn:{partition}:iam::{account_id}:role/aws-service-role"
            f"/guardduty.amazonaws.com/AWSServiceRoleForAmazonGuardDuty"
        )
        self.arn = (
            f"arn:{partition}:guardduty:{region_name}:{account_id}:detector/{self.id}"
        )
        self.enabled = enabled
        self.updated_at = created_at
        self.datasources = datasources or {}
        self.tags: dict[str, str] = tags or {}
        # TODO: Implement feature configuration object and validation
        # https://docs.aws.amazon.com/guardduty/latest/APIReference/API_DetectorFeatureConfiguration.html
        self.features = features or []

        self.filters: dict[str, Filter] = {}
        self.ip_sets: dict[str, IPSet] = {}
        self.threat_intel_sets: dict[str, ThreatIntelSet] = {}
        self.threat_entity_sets: dict[str, ThreatEntitySet] = {}
        self.trusted_entity_sets: dict[str, TrustedEntitySet] = {}
        self.findings: dict[str, dict[str, Any]] = {}
        self.publishing_destinations: dict[str, dict[str, Any]] = {}
        self.members: dict[str, dict[str, Any]] = {}
        self.administrator_id: Optional[str] = None
        self.invitation_id: Optional[str] = None

    def add_filter(self, _filter: Filter) -> None:
        self.filters[_filter.name] = _filter

    def delete_filter(self, filter_name: str) -> None:
        self.filters.pop(filter_name, None)

    def get_filter(self, filter_name: str) -> Filter:
        if filter_name not in self.filters:
            raise FilterNotFoundException
        return self.filters[filter_name]

    def update_filter(
        self,
        filter_name: str,
        action: str,
        description: str,
        finding_criteria: dict[str, Any],
        rank: int,
    ) -> None:
        _filter = self.get_filter(filter_name)
        _filter.update(
            action=action,
            description=description,
            finding_criteria=finding_criteria,
            rank=rank,
        )

    def update(
        self,
        enable: bool,
        finding_publishing_frequency: str,
        data_sources: dict[str, Any],
        features: list[dict[str, Any]],
    ) -> None:
        if enable is not None:
            self.enabled = enable
        if finding_publishing_frequency is not None:
            self.finding_publish_freq = finding_publishing_frequency
        if data_sources is not None:
            self.datasources = data_sources
        if features is not None:
            self.features = features
        self.updated_at = datetime.now()

    def to_json(self) -> dict[str, Any]:
        data_sources = {
            "cloudTrail": {"status": "DISABLED"},
            "dnsLogs": {"status": "DISABLED"},
            "flowLogs": {"status": "DISABLED"},
            "s3Logs": {
                "status": "ENABLED"
                if (self.datasources.get("s3Logs") or {}).get("enable")
                else "DISABLED"
            },
            "kubernetes": {
                "auditLogs": {
                    "status": "ENABLED"
                    if self.datasources.get("kubernetes", {})
                    .get("auditLogs", {})
                    .get("enable")
                    else "DISABLED"
                }
            },
        }
        return {
            "createdAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "findingPublishingFrequency": self.finding_publish_freq,
            "serviceRole": self.service_role,
            "status": "ENABLED" if self.enabled else "DISABLED",
            "updatedAt": self.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "dataSources": data_sources,
            "tags": self.tags,
            "features": self.features,
        }


class MalwareProtectionPlan(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        role: str,
        protected_resource: Optional[dict[str, Any]] = None,
        actions: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = mock_random.get_random_hex(length=32)
        self.role = role
        self.protected_resource = protected_resource or {}
        self.actions = actions or {}
        self.tags: dict[str, str] = tags or {}
        self.status = "ACTIVE"
        self.created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        partition = get_partition(region_name)
        self.arn = (
            f"arn:{partition}:guardduty:{region_name}:{account_id}"
            f":malware-protection-plan/{self.id}"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "malwareProtectionPlanId": self.id,
            "arn": self.arn,
            "role": self.role,
            "protectedResource": self.protected_resource,
            "actions": self.actions,
            "tags": self.tags,
            "status": self.status,
            "createdAt": self.created_at,
        }


class ThreatEntitySet(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        detector_id: str,
        name: str,
        entity_type: str,
        location: str,
        activate: bool,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = mock_random.get_random_hex(length=32)
        self.name = name
        self.entity_type = entity_type
        self.location = location
        self.status = "ACTIVE" if activate else "INACTIVE"
        self.tags: dict[str, str] = tags or {}
        partition = get_partition(region_name)
        self.arn = (
            f"arn:{partition}:guardduty:{region_name}:{account_id}"
            f":detector/{detector_id}/threatentityset/{self.id}"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "format": self.entity_type,
            "location": self.location,
            "status": self.status,
            "tags": self.tags,
        }


class TrustedEntitySet(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        detector_id: str,
        name: str,
        entity_type: str,
        location: str,
        activate: bool,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = mock_random.get_random_hex(length=32)
        self.name = name
        self.entity_type = entity_type
        self.location = location
        self.status = "ACTIVE" if activate else "INACTIVE"
        self.tags: dict[str, str] = tags or {}
        partition = get_partition(region_name)
        self.arn = (
            f"arn:{partition}:guardduty:{region_name}:{account_id}"
            f":detector/{detector_id}/trustedentityset/{self.id}"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "format": self.entity_type,
            "location": self.location,
            "status": self.status,
            "tags": self.tags,
        }


guardduty_backends = BackendDict(GuardDutyBackend, "guardduty")
