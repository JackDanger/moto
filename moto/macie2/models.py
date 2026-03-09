import re
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.moto_api._internal import mock_random

from .exceptions import ResourceNotFoundException, ValidationException


class AllowList(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        criteria: dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = mock_random.get_random_hex(32)
        self.name = name
        self.criteria = criteria
        self.description = description or ""
        self.tags = tags or {}
        now = utcnow()
        self.created_at = now
        self.updated_at = now
        self.arn = f"arn:aws:macie2:{region_name}:{account_id}:allow-list/{self.id}"
        self.status = {"code": "OK"}

    def to_json(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdAt": self.created_at.isoformat(),
            "criteria": self.criteria,
            "description": self.description,
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "tags": self.tags,
            "updatedAt": self.updated_at.isoformat(),
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdAt": self.created_at.isoformat(),
            "description": self.description,
            "id": self.id,
            "name": self.name,
            "updatedAt": self.updated_at.isoformat(),
        }


class ClassificationJob(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        job_type: str,
        s3_job_definition: dict[str, Any],
        client_token: Optional[str] = None,
        description: Optional[str] = None,
        initial_run: bool = False,
        sampling_percentage: Optional[int] = None,
        schedule_frequency: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
        allow_list_ids: Optional[list[str]] = None,
        custom_data_identifier_ids: Optional[list[str]] = None,
        managed_data_identifier_ids: Optional[list[str]] = None,
        managed_data_identifier_selector: Optional[str] = None,
    ):
        self.job_id = mock_random.get_random_hex(32)
        self.name = name
        self.job_type = job_type
        self.s3_job_definition = s3_job_definition
        self.client_token = client_token or mock_random.get_random_hex(16)
        self.description = description or ""
        self.initial_run = initial_run
        self.sampling_percentage = sampling_percentage or 100
        self.schedule_frequency = schedule_frequency or {}
        self.tags = tags or {}
        self.allow_list_ids = allow_list_ids or []
        self.custom_data_identifier_ids = custom_data_identifier_ids or []
        self.managed_data_identifier_ids = managed_data_identifier_ids or []
        self.managed_data_identifier_selector = managed_data_identifier_selector or "ALL"
        self.job_status = "RUNNING"
        now = utcnow()
        self.created_at = now
        self.last_run_time = now
        self.job_arn = (
            f"arn:aws:macie2:{region_name}:{account_id}:classification-job/{self.job_id}"
        )
        self.statistics = {
            "approximateNumberOfObjectsToProcess": 0.0,
            "numberOfRuns": 0.0,
        }

    def to_json(self) -> dict[str, Any]:
        return {
            "allowListIds": self.allow_list_ids,
            "clientToken": self.client_token,
            "createdAt": self.created_at.isoformat(),
            "customDataIdentifierIds": self.custom_data_identifier_ids,
            "description": self.description,
            "initialRun": self.initial_run,
            "jobArn": self.job_arn,
            "jobId": self.job_id,
            "jobStatus": self.job_status,
            "jobType": self.job_type,
            "lastRunErrorStatus": {"code": "NONE"},
            "lastRunTime": self.last_run_time.isoformat(),
            "managedDataIdentifierIds": self.managed_data_identifier_ids,
            "managedDataIdentifierSelector": self.managed_data_identifier_selector,
            "name": self.name,
            "s3JobDefinition": self.s3_job_definition,
            "samplingPercentage": self.sampling_percentage,
            "scheduleFrequency": self.schedule_frequency,
            "statistics": self.statistics,
            "tags": self.tags,
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "bucketDefinitions": self.s3_job_definition.get("bucketDefinitions", []),
            "createdAt": self.created_at.isoformat(),
            "jobId": self.job_id,
            "jobStatus": self.job_status,
            "jobType": self.job_type,
            "name": self.name,
        }


class CustomDataIdentifier(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        regex: str,
        description: Optional[str] = None,
        ignore_words: Optional[list[str]] = None,
        keywords: Optional[list[str]] = None,
        maximum_match_distance: Optional[int] = None,
        severity_levels: Optional[list[dict[str, Any]]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = mock_random.get_random_hex(32)
        self.name = name
        self.regex = regex
        self.description = description or ""
        self.ignore_words = ignore_words or []
        self.keywords = keywords or []
        self.maximum_match_distance = maximum_match_distance or 50
        self.severity_levels = severity_levels or []
        self.tags = tags or {}
        self.deleted = False
        self.created_at = utcnow()
        self.arn = f"arn:aws:macie2:{region_name}:{account_id}:custom-data-identifier/{self.id}"

    def to_json(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdAt": self.created_at.isoformat(),
            "deleted": self.deleted,
            "description": self.description,
            "id": self.id,
            "ignoreWords": self.ignore_words,
            "keywords": self.keywords,
            "maximumMatchDistance": self.maximum_match_distance,
            "name": self.name,
            "regex": self.regex,
            "severityLevels": self.severity_levels,
            "tags": self.tags,
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdAt": self.created_at.isoformat(),
            "description": self.description,
            "id": self.id,
            "name": self.name,
        }


class FindingsFilter(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        action: str,
        finding_criteria: dict[str, Any],
        description: Optional[str] = None,
        position: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.id = mock_random.get_random_hex(32)
        self.name = name
        self.action = action
        self.finding_criteria = finding_criteria
        self.description = description or ""
        self.position = position or 0
        self.tags = tags or {}
        self.arn = (
            f"arn:aws:macie2:{region_name}:{account_id}:findings-filter/{self.id}"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "arn": self.arn,
            "description": self.description,
            "findingCriteria": self.finding_criteria,
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "tags": self.tags,
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "arn": self.arn,
            "id": self.id,
            "name": self.name,
        }


class Invitation(BaseModel):
    def __init__(self, account_id: str, region_name: str, admin_account_id: str):
        self.account_id = account_id
        self.invitation_id = mock_random.get_random_hex()
        self.invited_at = utcnow()
        self.relationship_status = "Invited"
        self.arn = f"arn:aws:macie2:{region_name}:{admin_account_id}:invitation/{self.invitation_id}"

    def to_json(self) -> dict[str, Any]:
        return {
            "accountId": self.account_id,
            "invitationId": self.invitation_id,
            "invitedAt": self.invited_at.isoformat(),
            "relationshipStatus": self.relationship_status,
        }


class Member(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        admin_account_id: str,
        invitation: Optional[Invitation] = None,
        email: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.account_id = account_id
        self.relationship_status = "Enabled"
        self.updated_at = utcnow()
        self.arn = (
            f"arn:aws:macie2:{region_name}:{admin_account_id}:member/{self.account_id}"
        )
        self.administrator_account_id = admin_account_id
        self.invited_at = invitation.invited_at if invitation else utcnow()
        self.email = email or f"{self.account_id}@example.com"
        self.tags = tags or {}

    def to_json(self) -> dict[str, Any]:
        return {
            "accountId": self.account_id,
            "administratorAccountId": self.administrator_account_id,
            "arn": self.arn,
            "email": self.email,
            "invitedAt": self.invited_at.isoformat(),
            "masterAccountId": self.administrator_account_id,
            "relationshipStatus": self.relationship_status,
            "tags": self.tags,
            "updatedAt": self.updated_at.isoformat(),
        }


class MacieBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.invitations: dict[str, Invitation] = {}
        self.members: dict[str, Member] = {}
        self.administrator_account: Optional[Member] = None
        self.organization_admin_account_id: Optional[str] = None
        self.macie_session: Optional[dict[str, Any]] = {
            "createdAt": utcnow(),
            "findingPublishingFrequency": "FIFTEEN_MINUTES",
            "serviceRole": f"arn:aws:iam::{account_id}:role/aws-service-role/macie.amazonaws.com/AWSServiceRoleForAmazonMacie",
            "status": "ENABLED",
            "updatedAt": utcnow(),
        }
        # New resource stores
        self.allow_lists: dict[str, AllowList] = {}
        self.classification_jobs: dict[str, ClassificationJob] = {}
        self.custom_data_identifiers: dict[str, CustomDataIdentifier] = {}
        self.findings_filters: dict[str, FindingsFilter] = {}
        self.classification_export_configuration: Optional[dict[str, Any]] = None
        self.reveal_configuration: dict[str, Any] = {"status": "DISABLED"}
        self.retrieval_configuration: dict[str, Any] = {
            "retrievalMode": "CALLER_CREDENTIALS",
        }
        self.automated_discovery_status: str = "DISABLED"
        self.automated_discovery_auto_enable: str = "NONE"
        self.organization_auto_enable: bool = False
        self.findings_publication_configuration: dict[str, Any] = {
            "securityHubConfiguration": {"publishClassificationFindings": True, "publishPolicyFindings": True}
        }
        # Tags keyed by resource ARN
        self.tagger: dict[str, dict[str, str]] = {}

    def _get_tags(self, arn: str) -> dict[str, str]:
        return self.tagger.get(arn, {})

    def _set_tags(self, arn: str, tags: dict[str, str]) -> None:
        if arn not in self.tagger:
            self.tagger[arn] = {}
        self.tagger[arn].update(tags)

    def _remove_tags(self, arn: str, tag_keys: list[str]) -> None:
        if arn in self.tagger:
            for key in tag_keys:
                self.tagger[arn].pop(key, None)

    # --- Invitations ---

    def create_invitations(self, account_ids: list[str]) -> None:
        for account_id in account_ids:
            invitation = Invitation(
                account_id=account_id,
                region_name=self.region_name,
                admin_account_id=self.account_id,
            )
            self.invitations[account_id] = invitation

    def list_invitations(self) -> list[Invitation]:
        return list(self.invitations.values())

    def decline_invitations(self, account_ids: list[str]) -> None:
        for account_id in account_ids:
            for backend_dict in macie2_backends.values():
                backend = backend_dict.get(self.region_name)
                if backend and account_id in backend.invitations:
                    backend.invitations.pop(account_id)

    def delete_invitations(self, account_ids: list[str]) -> list[dict[str, Any]]:
        for account_id in account_ids:
            self.invitations.pop(account_id, None)
        return []

    def get_invitations_count(self) -> int:
        return len(self.invitations)

    def accept_invitation(
        self, administrator_account_id: str, invitation_id: str
    ) -> None:
        for backend_dict in macie2_backends.values():
            backend = backend_dict.get(self.region_name)
            if not backend:
                continue

            invitation = backend.invitations.get(self.account_id)
            if invitation and invitation.invitation_id == invitation_id:
                member = Member(
                    account_id=self.account_id,
                    region_name=self.region_name,
                    admin_account_id=administrator_account_id,
                    invitation=invitation,
                )
                backend.members[self.account_id] = member
                self.administrator_account = member
                backend.invitations.pop(self.account_id)
                return

    # --- Members ---

    def create_member(
        self,
        account: dict[str, str],
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        account_id = account.get("accountId", "")
        email = account.get("email", "")
        member = Member(
            account_id=account_id,
            region_name=self.region_name,
            admin_account_id=self.account_id,
            email=email,
            tags=tags,
        )
        self.members[account_id] = member
        if tags:
            self._set_tags(member.arn, tags)
        return member.arn

    def list_members(self) -> list[Member]:
        return list(self.members.values())

    def get_member(self, member_id: str) -> Member:
        if member_id not in self.members:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        return self.members[member_id]

    def get_administrator_account(self) -> Optional[Member]:
        return self.administrator_account

    def get_master_account(self) -> Optional[Member]:
        return self.administrator_account

    def delete_member(self, member_account_id: str) -> None:
        if member_account_id not in self.members:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )

        self.members.pop(member_account_id)

        for backend_dict in macie2_backends.values():
            backend = backend_dict.get(self.region_name)
            if backend and backend.account_id == member_account_id:
                backend.administrator_account = None
                break

    def disassociate_member(self, member_account_id: str) -> None:
        if member_account_id not in self.members:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )

        self.members.pop(member_account_id)

        for backend_dict in macie2_backends.values():
            backend = backend_dict.get(self.region_name)
            if backend and backend.account_id == member_account_id:
                backend.administrator_account = None
                break

    def update_member_session(self, member_id: str, status: str) -> None:
        if member_id not in self.members:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        # Status is stored on the member but Macie doesn't expose it directly
        # It affects whether the member's Macie session is enabled/paused

    def disassociate_from_administrator_account(self) -> None:
        self.administrator_account = None

    def disassociate_from_master_account(self) -> None:
        self.administrator_account = None

    # --- Macie Session ---

    def get_macie_session(self) -> dict[str, Any]:
        if not self.macie_session:
            raise ResourceNotFoundException(
                "The request failed because the specified resource doesn't exist."
            )
        return {
            "createdAt": self.macie_session["createdAt"].isoformat(),
            "findingPublishingFrequency": self.macie_session[
                "findingPublishingFrequency"
            ],
            "serviceRole": self.macie_session["serviceRole"],
            "status": self.macie_session["status"],
            "updatedAt": self.macie_session["updatedAt"].isoformat(),
        }

    def enable_macie(
        self,
        finding_publishing_frequency: str = "FIFTEEN_MINUTES",
        status: str = "ENABLED",
    ) -> None:
        now = utcnow()
        self.macie_session = {
            "createdAt": now,
            "findingPublishingFrequency": finding_publishing_frequency,
            "serviceRole": f"arn:aws:iam::{self.account_id}:role/aws-service-role/macie.amazonaws.com/AWSServiceRoleForAmazonMacie",
            "status": status,
            "updatedAt": now,
        }

    def update_macie_session(
        self,
        finding_publishing_frequency: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        if not self.macie_session:
            raise ResourceNotFoundException(
                "The request failed because the specified resource doesn't exist."
            )
        if finding_publishing_frequency:
            self.macie_session["findingPublishingFrequency"] = finding_publishing_frequency
        if status:
            self.macie_session["status"] = status
        self.macie_session["updatedAt"] = utcnow()

    def disable_macie(self) -> None:
        self.invitations.clear()
        self.members.clear()
        self.administrator_account = None
        self.macie_session = None

    # --- Organization Admin ---

    def enable_organization_admin_account(self, admin_account_id: str) -> None:
        self.organization_admin_account_id = admin_account_id

    def disable_organization_admin_account(self, admin_account_id: str) -> None:
        if self.organization_admin_account_id == admin_account_id:
            self.organization_admin_account_id = None

    def list_organization_admin_accounts(self) -> list[dict[str, str]]:
        if self.organization_admin_account_id:
            return [
                {
                    "accountId": self.organization_admin_account_id,
                    "status": "ENABLED",
                }
            ]
        return []

    def describe_organization_configuration(self) -> dict[str, Any]:
        return {
            "autoEnable": self.organization_auto_enable,
            "maxAccountLimitReached": False,
        }

    def update_organization_configuration(self, auto_enable: bool) -> None:
        self.organization_auto_enable = auto_enable

    # --- AllowLists ---

    def create_allow_list(
        self,
        name: str,
        criteria: dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> AllowList:
        allow_list = AllowList(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            criteria=criteria,
            description=description,
            tags=tags,
        )
        self.allow_lists[allow_list.id] = allow_list
        if tags:
            self._set_tags(allow_list.arn, tags)
        return allow_list

    def get_allow_list(self, list_id: str) -> AllowList:
        if list_id not in self.allow_lists:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        return self.allow_lists[list_id]

    def update_allow_list(
        self,
        list_id: str,
        name: str,
        criteria: dict[str, Any],
        description: Optional[str] = None,
    ) -> AllowList:
        allow_list = self.get_allow_list(list_id)
        allow_list.name = name
        allow_list.criteria = criteria
        if description is not None:
            allow_list.description = description
        allow_list.updated_at = utcnow()
        return allow_list

    def delete_allow_list(self, list_id: str) -> None:
        if list_id not in self.allow_lists:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        allow_list = self.allow_lists.pop(list_id)
        self.tagger.pop(allow_list.arn, None)

    def list_allow_lists(self) -> list[AllowList]:
        return list(self.allow_lists.values())

    # --- Classification Jobs ---

    def create_classification_job(
        self,
        name: str,
        job_type: str,
        s3_job_definition: dict[str, Any],
        client_token: Optional[str] = None,
        description: Optional[str] = None,
        initial_run: bool = False,
        sampling_percentage: Optional[int] = None,
        schedule_frequency: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
        allow_list_ids: Optional[list[str]] = None,
        custom_data_identifier_ids: Optional[list[str]] = None,
        managed_data_identifier_ids: Optional[list[str]] = None,
        managed_data_identifier_selector: Optional[str] = None,
    ) -> ClassificationJob:
        job = ClassificationJob(
            account_id=self.account_id,
            region_name=self.region_name,
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
        self.classification_jobs[job.job_id] = job
        if tags:
            self._set_tags(job.job_arn, tags)
        return job

    def describe_classification_job(self, job_id: str) -> ClassificationJob:
        if job_id not in self.classification_jobs:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        return self.classification_jobs[job_id]

    def update_classification_job(self, job_id: str, job_status: str) -> None:
        job = self.describe_classification_job(job_id)
        job.job_status = job_status

    def list_classification_jobs(self) -> list[ClassificationJob]:
        return list(self.classification_jobs.values())

    # --- Custom Data Identifiers ---

    def create_custom_data_identifier(
        self,
        name: str,
        regex: str,
        description: Optional[str] = None,
        ignore_words: Optional[list[str]] = None,
        keywords: Optional[list[str]] = None,
        maximum_match_distance: Optional[int] = None,
        severity_levels: Optional[list[dict[str, Any]]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> CustomDataIdentifier:
        cdi = CustomDataIdentifier(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            regex=regex,
            description=description,
            ignore_words=ignore_words,
            keywords=keywords,
            maximum_match_distance=maximum_match_distance,
            severity_levels=severity_levels,
            tags=tags,
        )
        self.custom_data_identifiers[cdi.id] = cdi
        if tags:
            self._set_tags(cdi.arn, tags)
        return cdi

    def get_custom_data_identifier(self, identifier_id: str) -> CustomDataIdentifier:
        if identifier_id not in self.custom_data_identifiers:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        return self.custom_data_identifiers[identifier_id]

    def delete_custom_data_identifier(self, identifier_id: str) -> None:
        if identifier_id not in self.custom_data_identifiers:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        cdi = self.custom_data_identifiers[identifier_id]
        cdi.deleted = True
        self.tagger.pop(cdi.arn, None)

    def list_custom_data_identifiers(self) -> list[CustomDataIdentifier]:
        return [
            cdi
            for cdi in self.custom_data_identifiers.values()
            if not cdi.deleted
        ]

    def batch_get_custom_data_identifiers(
        self, ids: list[str]
    ) -> tuple[list[CustomDataIdentifier], list[str]]:
        found: list[CustomDataIdentifier] = []
        not_found: list[str] = []
        for cdi_id in ids:
            if cdi_id in self.custom_data_identifiers:
                cdi = self.custom_data_identifiers[cdi_id]
                if not cdi.deleted:
                    found.append(cdi)
                else:
                    not_found.append(cdi_id)
            else:
                not_found.append(cdi_id)
        return found, not_found

    def test_custom_data_identifier(
        self,
        regex: str,
        sample_text: str,
        ignore_words: Optional[list[str]] = None,
        keywords: Optional[list[str]] = None,
        maximum_match_distance: Optional[int] = None,
    ) -> int:
        try:
            matches = re.findall(regex, sample_text)
        except re.error:
            return 0
        count = len(matches)
        if ignore_words:
            count = max(0, count - sum(1 for w in ignore_words if w in sample_text))
        return count

    # --- Findings Filters ---

    def create_findings_filter(
        self,
        name: str,
        action: str,
        finding_criteria: dict[str, Any],
        description: Optional[str] = None,
        position: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> FindingsFilter:
        ff = FindingsFilter(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            action=action,
            finding_criteria=finding_criteria,
            description=description,
            position=position,
            tags=tags,
        )
        self.findings_filters[ff.id] = ff
        if tags:
            self._set_tags(ff.arn, tags)
        return ff

    def get_findings_filter(self, filter_id: str) -> FindingsFilter:
        if filter_id not in self.findings_filters:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        return self.findings_filters[filter_id]

    def update_findings_filter(
        self,
        filter_id: str,
        name: Optional[str] = None,
        action: Optional[str] = None,
        finding_criteria: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        position: Optional[int] = None,
    ) -> FindingsFilter:
        ff = self.get_findings_filter(filter_id)
        if name is not None:
            ff.name = name
        if action is not None:
            ff.action = action
        if finding_criteria is not None:
            ff.finding_criteria = finding_criteria
        if description is not None:
            ff.description = description
        if position is not None:
            ff.position = position
        return ff

    def delete_findings_filter(self, filter_id: str) -> None:
        if filter_id not in self.findings_filters:
            raise ResourceNotFoundException(
                "The request failed because the resource doesn't exist."
            )
        ff = self.findings_filters.pop(filter_id)
        self.tagger.pop(ff.arn, None)

    def list_findings_filters(self) -> list[FindingsFilter]:
        return list(self.findings_filters.values())

    # --- Classification Export Configuration ---

    def put_classification_export_configuration(
        self, configuration: dict[str, Any]
    ) -> dict[str, Any]:
        self.classification_export_configuration = configuration
        return configuration

    def get_classification_export_configuration(self) -> Optional[dict[str, Any]]:
        return self.classification_export_configuration

    # --- Reveal Configuration ---

    def get_reveal_configuration(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return self.reveal_configuration, self.retrieval_configuration

    def update_reveal_configuration(
        self,
        configuration: Optional[dict[str, Any]] = None,
        retrieval_configuration: Optional[dict[str, Any]] = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if configuration:
            self.reveal_configuration.update(configuration)
        if retrieval_configuration:
            self.retrieval_configuration.update(retrieval_configuration)
        return self.reveal_configuration, self.retrieval_configuration

    # --- Automated Discovery ---

    def get_automated_discovery_configuration(self) -> dict[str, Any]:
        now = utcnow()
        result: dict[str, Any] = {
            "autoEnableOrganizationMembers": self.automated_discovery_auto_enable,
            "classificationScopeId": "auto-discovery-scope",
            "sensitivityInspectionTemplateId": "auto-discovery-template",
            "status": self.automated_discovery_status,
        }
        if self.automated_discovery_status == "ENABLED":
            result["firstEnabledAt"] = now.isoformat()
            result["lastUpdatedAt"] = now.isoformat()
        return result

    def update_automated_discovery_configuration(
        self,
        status: Optional[str] = None,
        auto_enable_organization_members: Optional[str] = None,
    ) -> None:
        if status:
            self.automated_discovery_status = status
        if auto_enable_organization_members:
            self.automated_discovery_auto_enable = auto_enable_organization_members

    def batch_update_automated_discovery_accounts(
        self, accounts: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        # Stub: accept the request but no real processing
        return []

    def list_automated_discovery_accounts(self) -> list[dict[str, Any]]:
        return []

    # --- Findings Publication Configuration ---

    def get_findings_publication_configuration(self) -> dict[str, Any]:
        return self.findings_publication_configuration.get(
            "securityHubConfiguration",
            {"publishClassificationFindings": True, "publishPolicyFindings": True},
        )

    def put_findings_publication_configuration(
        self, security_hub_configuration: Optional[dict[str, Any]] = None
    ) -> None:
        if security_hub_configuration:
            self.findings_publication_configuration["securityHubConfiguration"] = (
                security_hub_configuration
            )

    # --- Findings (stub - returns empty) ---

    def list_findings(self) -> list[str]:
        return []

    def get_findings(self, finding_ids: list[str]) -> list[dict[str, Any]]:
        return []

    def get_finding_statistics(
        self, group_by: str
    ) -> list[dict[str, Any]]:
        return []

    def create_sample_findings(
        self, finding_types: Optional[list[str]] = None
    ) -> None:
        # Stub: sample findings are not persisted
        pass

    # --- Buckets / Search (stub) ---

    def describe_buckets(self) -> list[dict[str, Any]]:
        return []

    def get_bucket_statistics(self) -> dict[str, Any]:
        return {
            "bucketCount": 0,
            "bucketCountByEffectivePermission": {
                "publiclyAccessible": 0,
                "publiclyReadable": 0,
                "publiclyWritable": 0,
                "unknown": 0,
            },
            "bucketCountByEncryptionType": {
                "kmsManaged": 0,
                "s3Managed": 0,
                "unencrypted": 0,
                "unknown": 0,
            },
            "bucketCountByObjectEncryptionRequirement": {
                "allowsUnencryptedObjectUploads": 0,
                "deniesUnencryptedObjectUploads": 0,
                "unknown": 0,
            },
            "bucketCountBySharedAccessType": {
                "external": 0,
                "internal": 0,
                "notShared": 0,
                "unknown": 0,
            },
            "classifiableObjectCount": 0,
            "classifiableSizeInBytes": 0,
            "objectCount": 0,
            "sizeInBytes": 0,
            "sizeInBytesCompressed": 0,
            "unclassifiableObjectCount": {"fileType": 0, "storageClass": 0, "total": 0},
            "unclassifiableObjectSizeInBytes": {"fileType": 0, "storageClass": 0, "total": 0},
        }

    def search_resources(self) -> list[dict[str, Any]]:
        return []

    # --- Usage (stub) ---

    def get_usage_totals(self) -> list[dict[str, Any]]:
        return []

    def get_usage_statistics(self) -> list[dict[str, Any]]:
        return []

    # --- Classification Scope (stub) ---

    def get_classification_scope(self, scope_id: str) -> dict[str, Any]:
        return {
            "id": scope_id,
            "name": "default-scope",
            "s3": {"excludes": {"bucketNames": []}},
        }

    def update_classification_scope(self, scope_id: str, s3: Optional[dict[str, Any]] = None) -> None:
        pass

    def list_classification_scopes(self) -> list[dict[str, Any]]:
        return [
            {"id": "default-scope", "name": "default-scope"},
        ]

    # --- Sensitivity Inspection Template (stub) ---

    def get_sensitivity_inspection_template(self, template_id: str) -> dict[str, Any]:
        return {
            "id": template_id,
            "name": "default-template",
            "description": "",
            "excludes": {"managedDataIdentifierIds": []},
            "includes": {"managedDataIdentifierIds": []},
        }

    def update_sensitivity_inspection_template(
        self,
        template_id: str,
        description: Optional[str] = None,
        excludes: Optional[dict[str, Any]] = None,
        includes: Optional[dict[str, Any]] = None,
    ) -> None:
        pass

    def list_sensitivity_inspection_templates(self) -> list[dict[str, Any]]:
        return [
            {"id": "default-template", "name": "default-template"},
        ]

    # --- Resource Profile (stub) ---

    def get_resource_profile(self) -> dict[str, Any]:
        return {
            "profileUpdatedAt": utcnow().isoformat(),
            "statisticsUpdatedAt": utcnow().isoformat(),
        }

    def update_resource_profile(self, resource_arn: Optional[str] = None) -> None:
        pass

    def list_resource_profile_artifacts(self) -> list[dict[str, Any]]:
        return []

    def list_resource_profile_detections(self) -> list[dict[str, Any]]:
        return []

    def update_resource_profile_detections(self) -> None:
        pass

    # --- Sensitive Data Occurrences (stub) ---

    def get_sensitive_data_occurrences(self, finding_id: str) -> dict[str, Any]:
        return {"status": "ERROR", "error": "Finding not available"}

    def get_sensitive_data_occurrences_availability(
        self, finding_id: str
    ) -> dict[str, Any]:
        return {"code": "UNAVAILABLE", "reasons": ["FINDING_NOT_AVAILABLE"]}

    # --- Managed Data Identifiers (stub) ---

    def list_managed_data_identifiers(self) -> list[dict[str, Any]]:
        return []

    # --- Tags ---

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self._set_tags(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self._remove_tags(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self._get_tags(resource_arn)


macie2_backends = BackendDict(MacieBackend, "macie2")
