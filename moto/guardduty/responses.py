import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import GuardDutyBackend, guardduty_backends


class GuardDutyResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="guardduty")

    @property
    def guardduty_backend(self) -> GuardDutyBackend:
        return guardduty_backends[self.current_account][self.region]

    def create_filter(self) -> str:
        detector_id = self.path.split("/")[-2]
        name = self._get_param("name")
        action = self._get_param("action")
        description = self._get_param("description")
        finding_criteria = self._get_param("findingCriteria")
        rank = self._get_param("rank")

        self.guardduty_backend.create_filter(
            detector_id, name, action, description, finding_criteria, rank
        )
        return json.dumps({"name": name})

    def create_detector(self) -> str:
        enable = self._get_param("enable")
        finding_publishing_frequency = self._get_param("findingPublishingFrequency")
        data_sources = self._get_param("dataSources")
        tags = self._get_param("tags")
        features = self._get_param("features")

        detector_id = self.guardduty_backend.create_detector(
            enable, finding_publishing_frequency, data_sources, tags, features
        )

        return json.dumps({"detectorId": detector_id})

    def delete_detector(self) -> str:
        detector_id = self.path.split("/")[-1]

        self.guardduty_backend.delete_detector(detector_id)
        return "{}"

    def delete_filter(self) -> str:
        detector_id = self.path.split("/")[-3]
        filter_name = unquote(self.path.split("/")[-1])

        self.guardduty_backend.delete_filter(detector_id, filter_name)
        return "{}"

    def enable_organization_admin_account(self) -> str:
        admin_account = self._get_param("adminAccountId")
        self.guardduty_backend.enable_organization_admin_account(admin_account)

        return "{}"

    def list_organization_admin_accounts(self) -> str:
        account_ids = self.guardduty_backend.list_organization_admin_accounts()
        accounts = [
            {"adminAccountId": a, "adminStatus": "ENABLED"} for a in account_ids
        ]

        return json.dumps({"adminAccounts": accounts})

    def list_detectors(self) -> str:
        detector_ids = self.guardduty_backend.list_detectors()

        return json.dumps({"detectorIds": detector_ids})

    def get_detector(self) -> str:
        detector_id = self.path.split("/")[-1]

        detector = self.guardduty_backend.get_detector(detector_id)
        return json.dumps(detector.to_json())

    def get_filter(self) -> str:
        detector_id = self.path.split("/")[-3]
        filter_name = unquote(self.path.split("/")[-1])

        _filter = self.guardduty_backend.get_filter(detector_id, filter_name)
        return json.dumps(_filter.to_json())

    def list_filters(self) -> str:
        detector_id = self.path.split("/")[-2]
        filter_names = self.guardduty_backend.list_filters(detector_id)
        return json.dumps({"filterNames": filter_names})

    def update_detector(self) -> str:
        detector_id = self.path.split("/")[-1]
        enable = self._get_param("enable")
        finding_publishing_frequency = self._get_param("findingPublishingFrequency")
        data_sources = self._get_param("dataSources")
        features = self._get_param("features")

        self.guardduty_backend.update_detector(
            detector_id, enable, finding_publishing_frequency, data_sources, features
        )
        return "{}"

    def update_filter(self) -> str:
        detector_id = self.path.split("/")[-3]
        filter_name = unquote(self.path.split("/")[-1])
        action = self._get_param("action")
        description = self._get_param("description")
        finding_criteria = self._get_param("findingCriteria")
        rank = self._get_param("rank")

        self.guardduty_backend.update_filter(
            detector_id,
            filter_name,
            action=action,
            description=description,
            finding_criteria=finding_criteria,
            rank=rank,
        )
        return json.dumps({"name": filter_name})

    def get_administrator_account(self) -> str:
        """Get administrator account details."""
        detector_id = self.path.split("/")[-2]
        result = self.guardduty_backend.get_administrator_account(detector_id)
        return json.dumps(result)

    # IPSet operations
    def create_ip_set(self) -> str:
        detector_id = self.path.split("/")[-2]
        name = self._get_param("name")
        ip_format = self._get_param("format")
        location = self._get_param("location")
        activate = self._get_param("activate")
        tags = self._get_param("tags")
        ip_set_id = self.guardduty_backend.create_ip_set(
            detector_id=detector_id,
            name=name,
            ip_format=ip_format,
            location=location,
            activate=activate,
            tags=tags,
        )
        return json.dumps({"ipSetId": ip_set_id})

    def get_ip_set(self) -> str:
        detector_id = self.path.split("/")[-3]
        ip_set_id = self.path.split("/")[-1]
        ip_set = self.guardduty_backend.get_ip_set(detector_id, ip_set_id)
        return json.dumps(ip_set.to_json())

    def update_ip_set(self) -> str:
        detector_id = self.path.split("/")[-3]
        ip_set_id = self.path.split("/")[-1]
        name = self._get_param("name")
        location = self._get_param("location")
        activate = self._get_param("activate")
        self.guardduty_backend.update_ip_set(
            detector_id=detector_id,
            ip_set_id=ip_set_id,
            name=name,
            location=location,
            activate=activate,
        )
        return "{}"

    def delete_ip_set(self) -> str:
        detector_id = self.path.split("/")[-3]
        ip_set_id = self.path.split("/")[-1]
        self.guardduty_backend.delete_ip_set(detector_id, ip_set_id)
        return "{}"

    def list_ip_sets(self) -> str:
        detector_id = self.path.split("/")[-2]
        ip_set_ids = self.guardduty_backend.list_ip_sets(detector_id)
        return json.dumps({"ipSetIds": ip_set_ids})

    # ThreatIntelSet operations
    def create_threat_intel_set(self) -> str:
        detector_id = self.path.split("/")[-2]
        name = self._get_param("name")
        tis_format = self._get_param("format")
        location = self._get_param("location")
        activate = self._get_param("activate")
        tags = self._get_param("tags")
        threat_intel_set_id = self.guardduty_backend.create_threat_intel_set(
            detector_id=detector_id,
            name=name,
            tis_format=tis_format,
            location=location,
            activate=activate,
            tags=tags,
        )
        return json.dumps({"threatIntelSetId": threat_intel_set_id})

    def get_threat_intel_set(self) -> str:
        detector_id = self.path.split("/")[-3]
        threat_intel_set_id = self.path.split("/")[-1]
        tis = self.guardduty_backend.get_threat_intel_set(
            detector_id, threat_intel_set_id
        )
        return json.dumps(tis.to_json())

    def update_threat_intel_set(self) -> str:
        detector_id = self.path.split("/")[-3]
        threat_intel_set_id = self.path.split("/")[-1]
        name = self._get_param("name")
        location = self._get_param("location")
        activate = self._get_param("activate")
        self.guardduty_backend.update_threat_intel_set(
            detector_id=detector_id,
            threat_intel_set_id=threat_intel_set_id,
            name=name,
            location=location,
            activate=activate,
        )
        return "{}"

    def delete_threat_intel_set(self) -> str:
        detector_id = self.path.split("/")[-3]
        threat_intel_set_id = self.path.split("/")[-1]
        self.guardduty_backend.delete_threat_intel_set(
            detector_id, threat_intel_set_id
        )
        return "{}"

    def list_threat_intel_sets(self) -> str:
        detector_id = self.path.split("/")[-2]
        threat_intel_set_ids = self.guardduty_backend.list_threat_intel_sets(
            detector_id
        )
        return json.dumps({"threatIntelSetIds": threat_intel_set_ids})

    # Tagging operations
    def tag_resource(self) -> str:
        resource_arn = self._get_resource_arn_from_path()
        tags = self._get_param("tags")
        self.guardduty_backend.tag_resource(resource_arn, tags or {})
        return "{}"

    def untag_resource(self) -> str:
        resource_arn = self._get_resource_arn_from_path()
        tag_keys = self.querystring.get("tagKeys", [])
        self.guardduty_backend.untag_resource(resource_arn, tag_keys)
        return "{}"

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_resource_arn_from_path()
        tags = self.guardduty_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"tags": tags})

    # Findings operations
    def get_findings(self) -> str:
        detector_id = self.path.split("/")[-3]
        finding_ids = self._get_param("findingIds")
        findings = self.guardduty_backend.get_findings(detector_id, finding_ids or [])
        return json.dumps({"findings": findings})

    def list_findings(self) -> str:
        detector_id = self.path.split("/")[-2]
        finding_ids = self.guardduty_backend.list_findings(detector_id)
        return json.dumps({"findingIds": finding_ids})

    def get_findings_statistics(self) -> str:
        detector_id = self.path.split("/")[-3]
        stats = self.guardduty_backend.get_findings_statistics(detector_id)
        return json.dumps({"findingStatistics": stats})

    def create_sample_findings(self) -> str:
        detector_id = self.path.split("/")[-3]
        finding_types = self._get_param("findingTypes")
        self.guardduty_backend.create_sample_findings(detector_id, finding_types or [])
        return "{}"

    # Organization / admin
    def describe_organization_configuration(self) -> str:
        detector_id = self.path.split("/")[-2]
        result = self.guardduty_backend.describe_organization_configuration(detector_id)
        return json.dumps(result)

    def get_master_account(self) -> str:
        detector_id = self.path.split("/")[-2]
        result = self.guardduty_backend.get_master_account(detector_id)
        return json.dumps(result)

    def get_member_detectors(self) -> str:
        detector_id = self.path.split("/")[-4]
        account_ids = self._get_param("accountIds")
        members, unprocessed = self.guardduty_backend.get_member_detectors(
            detector_id, account_ids or []
        )
        return json.dumps({
            "members": members,
            "unprocessedAccounts": unprocessed,
        })

    def get_remaining_free_trial_days(self) -> str:
        detector_id = self.path.split("/")[-3]
        account_ids = self._get_param("accountIds")
        accounts = self.guardduty_backend.get_remaining_free_trial_days(
            detector_id, account_ids or []
        )
        return json.dumps({"accounts": accounts, "unprocessedAccounts": []})

    def get_usage_statistics(self) -> str:
        detector_id = self.path.split("/")[-3]
        result = self.guardduty_backend.get_usage_statistics(detector_id)
        return json.dumps(result)

    def list_invitations(self) -> str:
        invitations = self.guardduty_backend.list_invitations()
        return json.dumps({"invitations": invitations})

    # Malware scan operations
    def describe_malware_scans(self) -> str:
        detector_id = self.path.split("/")[-2]
        scans = self.guardduty_backend.describe_malware_scans(detector_id)
        return json.dumps({"scans": scans})

    def get_malware_scan_settings(self) -> str:
        detector_id = self.path.split("/")[-2]
        settings = self.guardduty_backend.get_malware_scan_settings(detector_id)
        return json.dumps(settings)

    # Publishing destinations
    def create_publishing_destination(self) -> str:
        detector_id = self.path.split("/")[-2]
        destination_type = self._get_param("destinationType")
        destination_properties = self._get_param("destinationProperties")
        dest_id = self.guardduty_backend.create_publishing_destination(
            detector_id, destination_type, destination_properties or {}
        )
        return json.dumps({"destinationId": dest_id})

    def describe_publishing_destination(self) -> str:
        detector_id = self.path.split("/")[-3]
        destination_id = self.path.split("/")[-1]
        result = self.guardduty_backend.describe_publishing_destination(
            detector_id, destination_id
        )
        return json.dumps(result)

    # Coverage statistics
    def get_coverage_statistics(self) -> str:
        detector_id = self.path.split("/")[-3]
        result = self.guardduty_backend.get_coverage_statistics(detector_id)
        return json.dumps(result)

    def _get_resource_arn_from_path(self) -> str:
        path = unquote(self.path)
        idx = path.find("/tags/")
        if idx >= 0:
            return path[idx + 6:]
        return ""
