"""SyntheticsBackend class with methods for supported APIs."""

import uuid
from typing import Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition


class CanaryRun(BaseModel):
    """Represents a single canary run."""

    def __init__(self, canary_name: str, status: str = "PASSED"):
        self.id = str(uuid.uuid4())
        self.name = canary_name
        self.status = status
        now = utcnow()
        self.timeline = {
            "Started": now,
            "Completed": now,
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "Id": self.id,
            "Name": self.name,
            "Status": {
                "State": self.status,
                "StateReason": "",
                "StateReasonCode": "",
            },
            "Timeline": {
                "Started": iso_8601_datetime_with_milliseconds(
                    self.timeline["Started"]
                ),
                "Completed": iso_8601_datetime_with_milliseconds(
                    self.timeline["Completed"]
                ),
            },
            "ArtifactS3Location": "s3://cw-syn-results/canary",
        }


class Group(BaseModel):
    """Represents a Synthetics Group."""

    def __init__(
        self,
        name: str,
        account_id: str,
        region: str,
        tags: Optional[dict[str, str]],
    ):
        self.name = name
        self.id = str(uuid.uuid4())
        partition = get_partition(region)
        self.arn = f"arn:{partition}:synthetics:{region}:{account_id}:group:{self.name}"
        self.tags = tags or {}
        self.resource_arns: list[str] = []
        now = utcnow()
        self.created_time = now
        self.last_modified_time = now

    def to_dict(self) -> dict[str, object]:
        return {
            "Id": self.id,
            "Name": self.name,
            "Arn": self.arn,
            "Tags": self.tags,
            "CreatedTime": iso_8601_datetime_with_milliseconds(self.created_time),
            "LastModifiedTime": iso_8601_datetime_with_milliseconds(
                self.last_modified_time
            ),
        }

    def summary_dict(self) -> dict[str, object]:
        return {
            "Id": self.id,
            "Name": self.name,
            "Arn": self.arn,
        }


class Canary(BaseModel):
    """
    Represents a CloudWatch Synthetics Canary resource.
    """

    def __init__(
        self,
        name: str,
        code: dict[str, object],
        artifact_s3_location: str,
        execution_role_arn: str,
        schedule: dict[str, object],
        run_config: dict[str, object],
        success_retention_period_in_days: int,
        failure_retention_period_in_days: int,
        runtime_version: str,
        vpc_config: Optional[dict[str, object]],
        resources_to_replicate_tags: Optional[list[str]],
        provisioned_resource_cleanup: Optional[str],
        browser_configs: Optional[list[dict[str, object]]],
        tags: Optional[dict[str, str]],
        artifact_config: Optional[dict[str, object]],
        account_id: str = "123456789012",
        region: str = "us-east-1",
    ):
        self.name = name
        self.id = str(uuid.uuid4())
        self.code = code
        self.artifact_s3_location = artifact_s3_location
        self.execution_role_arn = execution_role_arn
        self.schedule = schedule
        self.run_config = run_config
        self.success_retention_period_in_days = success_retention_period_in_days
        self.failure_retention_period_in_days = failure_retention_period_in_days
        self.runtime_version = runtime_version
        self.vpc_config = vpc_config
        self.resources_to_replicate_tags = resources_to_replicate_tags
        self.provisioned_resource_cleanup = provisioned_resource_cleanup
        self.browser_configs = browser_configs or []
        self.tags = tags or {}
        self.artifact_config = artifact_config
        self.state = "READY"
        partition = get_partition(region)
        self.arn = f"arn:{partition}:synthetics:{region}:{account_id}:canary:{self.name}"
        self.runs: list[CanaryRun] = []
        self.last_run: Optional[CanaryRun] = None

        now = utcnow()
        self.timeline = {
            "Created": now,
            "LastModified": now,
            "LastStarted": None,
            "LastStopped": None,
        }

    def to_dict(self) -> dict[str, object]:
        """
        Convert the Canary object to a dictionary representation.
        """
        return {
            "Id": self.id,
            "Name": self.name,
            "Code": self.code,
            "ArtifactS3Location": self.artifact_s3_location,
            "ExecutionRoleArn": self.execution_role_arn,
            "Schedule": self.schedule,
            "RunConfig": self.run_config,
            "SuccessRetentionPeriodInDays": self.success_retention_period_in_days,
            "FailureRetentionPeriodInDays": self.failure_retention_period_in_days,
            "RuntimeVersion": self.runtime_version,
            "VpcConfig": self.vpc_config,
            "ProvisionedResourceCleanup": self.provisioned_resource_cleanup,
            "BrowserConfigs": self.browser_configs,
            "Tags": self.tags,
            "ArtifactConfig": self.artifact_config,
            "Status": {
                "State": self.state,
                "StateReason": "Created by Moto",
                "StateReasonCode": "CREATE_COMPLETE",
            },
            "Timeline": {
                "Created": iso_8601_datetime_with_milliseconds(
                    self.timeline["Created"]
                ),
                "LastModified": iso_8601_datetime_with_milliseconds(
                    self.timeline["LastModified"]
                ),
                "LastStarted": (
                    iso_8601_datetime_with_milliseconds(self.timeline["LastStarted"])
                    if self.timeline["LastStarted"]
                    else None
                ),
                "LastStopped": (
                    iso_8601_datetime_with_milliseconds(self.timeline["LastStopped"])
                    if self.timeline["LastStopped"]
                    else None
                ),
            },
        }


RUNTIME_VERSIONS = [
    {
        "VersionName": "syn-nodejs-puppeteer-9.1",
        "Description": "Node.js Puppeteer 9.1",
        "ReleaseDate": "2024-01-01T00:00:00Z",
        "DeprecationDate": None,
    },
    {
        "VersionName": "syn-nodejs-puppeteer-7.0",
        "Description": "Node.js Puppeteer 7.0",
        "ReleaseDate": "2023-06-01T00:00:00Z",
        "DeprecationDate": None,
    },
    {
        "VersionName": "syn-nodejs-puppeteer-6.2",
        "Description": "Node.js Puppeteer 6.2",
        "ReleaseDate": "2023-01-01T00:00:00Z",
        "DeprecationDate": None,
    },
    {
        "VersionName": "syn-nodejs-puppeteer-3.8",
        "Description": "Node.js Puppeteer 3.8",
        "ReleaseDate": "2022-01-01T00:00:00Z",
        "DeprecationDate": "2024-06-01T00:00:00Z",
    },
    {
        "VersionName": "syn-python-selenium-3.0",
        "Description": "Python Selenium 3.0",
        "ReleaseDate": "2023-03-01T00:00:00Z",
        "DeprecationDate": None,
    },
]


class SyntheticsBackend(BaseBackend):
    """Implementation of Synthetics APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.canaries: dict[str, Canary] = {}
        self.groups: dict[str, Group] = {}
        self.tagger = TaggingService()

    def create_canary(
        self,
        name: str,
        code: dict[str, object],
        artifact_s3_location: str,
        execution_role_arn: str,
        schedule: dict[str, object],
        run_config: dict[str, object],
        success_retention_period_in_days: int,
        failure_retention_period_in_days: int,
        runtime_version: str,
        vpc_config: Optional[dict[str, object]],
        resources_to_replicate_tags: Optional[list[str]],
        provisioned_resource_cleanup: Optional[str],
        browser_configs: Optional[list[dict[str, object]]],
        tags: Optional[dict[str, str]],
        artifact_config: Optional[dict[str, object]],
    ) -> Canary:
        canary = Canary(
            name,
            code,
            artifact_s3_location,
            execution_role_arn,
            schedule,
            run_config,
            success_retention_period_in_days,
            failure_retention_period_in_days,
            runtime_version,
            vpc_config,
            resources_to_replicate_tags,
            provisioned_resource_cleanup,
            browser_configs,
            tags,
            artifact_config,
            account_id=self.account_id,
            region=self.region_name,
        )
        self.canaries[name] = canary
        if tags:
            self.tagger.tag_resource(
                canary.arn, self.tagger.convert_dict_to_tags_input(tags)
            )
        return canary

    def get_canary(self, name: str, dry_run_id: Optional[str] = None) -> Canary:
        """
        The dry-run_id-parameter is not yet supported
        """
        if name not in self.canaries:
            from moto.core.exceptions import JsonRESTError

            raise JsonRESTError(
                "ResourceNotFoundException",
                f"Canary {name} not found",
                body={"resourceName": name},
            )
        return self.canaries[name]

    def delete_canary(self, name: str) -> None:
        canary = self.get_canary(name)
        self.tagger.delete_all_tags_for_resource(canary.arn)
        del self.canaries[name]

    def update_canary(
        self,
        name: str,
        code: Optional[dict[str, object]],
        execution_role_arn: Optional[str],
        runtime_version: Optional[str],
        schedule: Optional[dict[str, object]],
        run_config: Optional[dict[str, object]],
        success_retention_period_in_days: Optional[int],
        failure_retention_period_in_days: Optional[int],
        vpc_config: Optional[dict[str, object]],
        artifact_s3_location: Optional[str],
        artifact_config: Optional[dict[str, object]],
        provisioned_resource_cleanup: Optional[str],
        browser_configs: Optional[list[dict[str, object]]],
    ) -> None:
        canary = self.get_canary(name)
        if code is not None:
            canary.code = code
        if execution_role_arn is not None:
            canary.execution_role_arn = execution_role_arn
        if runtime_version is not None:
            canary.runtime_version = runtime_version
        if schedule is not None:
            canary.schedule = schedule
        if run_config is not None:
            canary.run_config = run_config
        if success_retention_period_in_days is not None:
            canary.success_retention_period_in_days = success_retention_period_in_days
        if failure_retention_period_in_days is not None:
            canary.failure_retention_period_in_days = failure_retention_period_in_days
        if vpc_config is not None:
            canary.vpc_config = vpc_config
        if artifact_s3_location is not None:
            canary.artifact_s3_location = artifact_s3_location
        if artifact_config is not None:
            canary.artifact_config = artifact_config
        if provisioned_resource_cleanup is not None:
            canary.provisioned_resource_cleanup = provisioned_resource_cleanup
        if browser_configs is not None:
            canary.browser_configs = browser_configs
        canary.timeline["LastModified"] = utcnow()

    def start_canary(self, name: str) -> None:
        canary = self.get_canary(name)
        canary.state = "RUNNING"
        now = utcnow()
        canary.timeline["LastStarted"] = now
        # Create a run record
        run = CanaryRun(canary_name=name, status="PASSED")
        canary.runs.append(run)
        canary.last_run = run

    def stop_canary(self, name: str) -> None:
        canary = self.get_canary(name)
        canary.state = "STOPPED"
        canary.timeline["LastStopped"] = utcnow()

    def start_canary_dry_run(self, name: str) -> dict[str, object]:
        """Start a dry run — just returns a stub DryRunConfig."""
        self.get_canary(name)  # validate it exists
        return {
            "DryRunId": str(uuid.uuid4()),
        }

    def describe_canaries(
        self,
        next_token: Optional[str],
        max_results: Optional[int],
        names: Optional[list[str]],
    ) -> tuple[list[Canary], None]:
        """
        Pagination is not yet supported
        """
        canaries = list(self.canaries.values())
        if names:
            canaries = [c for c in canaries if c.name in names]
        return canaries, None

    def describe_canaries_last_run(
        self,
        names: Optional[list[str]],
    ) -> list[dict[str, object]]:
        canaries = list(self.canaries.values())
        if names:
            canaries = [c for c in canaries if c.name in names]
        result = []
        for canary in canaries:
            entry: dict[str, object] = {"CanaryName": canary.name}
            if canary.last_run:
                entry["LastRun"] = canary.last_run.to_dict()
            result.append(entry)
        return result

    def describe_runtime_versions(self) -> list[dict[str, object]]:
        return RUNTIME_VERSIONS

    def get_canary_runs(
        self,
        name: str,
    ) -> list[CanaryRun]:
        canary = self.get_canary(name)
        return canary.runs

    def create_group(
        self,
        name: str,
        tags: Optional[dict[str, str]],
    ) -> Group:
        group = Group(
            name=name,
            account_id=self.account_id,
            region=self.region_name,
            tags=tags,
        )
        self.groups[name] = group
        if tags:
            self.tagger.tag_resource(
                group.arn, self.tagger.convert_dict_to_tags_input(tags)
            )
        return group

    def get_group(self, group_identifier: str) -> Group:
        # Can look up by name or ARN
        for group in self.groups.values():
            if group.name == group_identifier or group.arn == group_identifier:
                return group
        from moto.core.exceptions import JsonRESTError

        raise JsonRESTError(
            "ResourceNotFoundException",
            f"Group {group_identifier} not found",
        )

    def delete_group(self, group_identifier: str) -> None:
        group = self.get_group(group_identifier)
        self.tagger.delete_all_tags_for_resource(group.arn)
        del self.groups[group.name]

    def list_groups(self) -> list[Group]:
        return list(self.groups.values())

    def associate_resource(self, group_identifier: str, resource_arn: str) -> None:
        group = self.get_group(group_identifier)
        if resource_arn not in group.resource_arns:
            group.resource_arns.append(resource_arn)
        group.last_modified_time = utcnow()

    def disassociate_resource(self, group_identifier: str, resource_arn: str) -> None:
        group = self.get_group(group_identifier)
        if resource_arn in group.resource_arns:
            group.resource_arns.remove(resource_arn)
        group.last_modified_time = utcnow()

    def list_group_resources(self, group_identifier: str) -> list[str]:
        group = self.get_group(group_identifier)
        return group.resource_arns

    def list_associated_groups(self, resource_arn: str) -> list[Group]:
        result = []
        for group in self.groups.values():
            if resource_arn in group.resource_arns:
                result.append(group)
        return result

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        tag_list = self.tagger.convert_dict_to_tags_input(tags)
        self.tagger.tag_resource(resource_arn, tag_list)
        # Also update inline tags on canaries/groups
        for canary in self.canaries.values():
            if canary.arn == resource_arn:
                canary.tags.update(tags)
                return
        for group in self.groups.values():
            if group.arn == resource_arn:
                group.tags.update(tags)
                return

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)
        for canary in self.canaries.values():
            if canary.arn == resource_arn:
                for key in tag_keys:
                    canary.tags.pop(key, None)
                return
        for group in self.groups.values():
            if group.arn == resource_arn:
                for key in tag_keys:
                    group.tags.pop(key, None)
                return

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)


# Exported backend dict for Moto Synthetics
synthetics_backends = BackendDict(SyntheticsBackend, "synthetics")
