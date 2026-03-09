from copy import deepcopy
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time, utcnow
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    AlreadyExistsException,
    InvalidParameterValueException,
    InvalidRequestException,
    ResourceNotFoundException,
)


class ReportPlan(BaseModel):
    def __init__(
        self,
        name: str,
        report_plan_description: Optional[str],
        report_delivery_channel: dict[str, Any],
        report_setting: dict[str, Any],
        backend: "BackupBackend",
    ):
        self.report_plan_name = name
        self.report_plan_description = report_plan_description
        self.report_plan_arn = f"arn:{get_partition(backend.region_name)}:backup:{backend.region_name}:{backend.account_id}:report-plan:{name}"
        self.creation_time = utcnow()
        self.report_setting = report_setting
        self.report_delivery_channel = report_delivery_channel
        self.deployment_status = "COMPLETED"


class Plan(BaseModel):
    def __init__(
        self,
        backup_plan: dict[str, Any],
        creator_request_id: str,
        backend: "BackupBackend",
    ):
        self.backup_plan_id = str(mock_random.uuid4())
        self.backup_plan_arn = f"arn:{get_partition(backend.region_name)}:backup:{backend.region_name}:{backend.account_id}:backup-plan:{self.backup_plan_id}"
        self.creation_date = unix_time()
        ran_str = mock_random.get_random_string(length=48)
        self.version_id = ran_str
        self.creator_request_id = creator_request_id
        self.backup_plan = backup_plan
        adv_settings = backup_plan.get("AdvancedBackupSettings")
        self.advanced_backup_settings = adv_settings or []
        self.deletion_date: Optional[float] = None
        # Deletion Date is updated when the backup_plan is deleted
        self.last_execution_date = None  # start_restore_job not yet supported
        rules = backup_plan["Rules"]
        for rule in rules:
            rule["ScheduleExpression"] = rule.get(
                "ScheduleExpression", "cron(0 5 ? * * *)"
            )  # Default CRON expression in UTC
            rule["StartWindowMinutes"] = rule.get(
                "StartWindowMinutes", 480
            )  # Default=480
            rule["CompletionWindowMinutes"] = rule.get(
                "CompletionWindowMinutes", 10080
            )  # Default=10080
            rule["ScheduleExpressionTimezone"] = rule.get(
                "ScheduleExpressionTimezone", "Etc/UTC"
            )  # set to Etc/UTc by default
            rule["RuleId"] = str(mock_random.uuid4())

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "BackupPlanId": self.backup_plan_id,
            "BackupPlanArn": self.backup_plan_arn,
            "CreationDate": self.creation_date,
            "VersionId": self.version_id,
            "AdvancedBackupSettings": self.advanced_backup_settings,
        }
        return {k: v for k, v in dct.items() if v}

    def to_get_dict(self) -> dict[str, Any]:
        dct = self.to_dict()
        dct_options = {
            "BackupPlan": self.backup_plan,
            "CreatorRequestId": self.creator_request_id,
            "DeletionDate": self.deletion_date,
            "LastExecutionDate": self.last_execution_date,
        }
        for key, value in dct_options.items():
            if value is not None:
                dct[key] = value
        return dct

    def to_list_dict(self) -> dict[str, Any]:
        dct = self.to_get_dict()
        dct.pop("BackupPlan")
        dct["BackupPlanName"] = self.backup_plan.get("BackupPlanName")
        return dct


class Vault(BaseModel):
    def __init__(
        self,
        backup_vault_name: str,
        encryption_key_arn: str,
        creator_request_id: str,
        backend: "BackupBackend",
    ):
        self.backup_vault_name = backup_vault_name
        self.backup_vault_arn = f"arn:{get_partition(backend.region_name)}:backup:{backend.region_name}:{backend.account_id}:backup-vault:{backup_vault_name}"
        self.creation_date = unix_time()
        self.encryption_key_arn = encryption_key_arn
        self.creator_request_id = creator_request_id
        self.num_of_recovery_points = 0
        self.locked = False
        self.min_retention_days: Optional[int] = None
        self.max_retention_days: Optional[int] = None
        self.lock_date: Optional[float] = None
        self.changeable_for_days: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "BackupVaultName": self.backup_vault_name,
            "BackupVaultArn": self.backup_vault_arn,
            "CreationDate": self.creation_date,
        }
        return dct

    def to_list_dict(self) -> dict[str, Any]:
        dct = self.to_dict()
        dct_options = {
            "EncryptionKeyArn": self.encryption_key_arn,
            "CreatorRequestId": self.creator_request_id,
            "NumberOfRecoveryPoints": self.num_of_recovery_points,
            "Locked": self.locked,
            "MinRetentionDays": self.min_retention_days,
            "MaxRetentionDays": self.max_retention_days,
            "LockDate": self.lock_date,
        }
        for key, value in dct_options.items():
            if value is not None:
                dct[key] = value
        return dct


class Selection(BaseModel):
    def __init__(
        self,
        backup_plan_id: str,
        selection: dict[str, Any],
        creator_request_id: Optional[str],
        backend: "BackupBackend",
    ):
        self.selection_id = str(mock_random.uuid4())
        self.backup_plan_id = backup_plan_id
        self.selection_name = selection.get("SelectionName", "")
        self.iam_role_arn = selection.get("IamRoleArn", "")
        self.resources = selection.get("Resources", [])
        self.not_resources = selection.get("NotResources", [])
        self.list_of_tags = selection.get("ListOfTags", [])
        self.conditions = selection.get("Conditions", {})
        self.creator_request_id = creator_request_id
        self.creation_date = unix_time()
        self.backup_selection = selection

    def to_dict(self) -> dict[str, Any]:
        return {
            "SelectionId": self.selection_id,
            "BackupPlanId": self.backup_plan_id,
            "CreationDate": self.creation_date,
        }

    def to_get_dict(self) -> dict[str, Any]:
        dct = self.to_dict()
        dct["BackupSelection"] = self.backup_selection
        if self.creator_request_id:
            dct["CreatorRequestId"] = self.creator_request_id
        return dct

    def to_list_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "SelectionId": self.selection_id,
            "SelectionName": self.selection_name,
            "BackupPlanId": self.backup_plan_id,
            "CreationDate": self.creation_date,
            "IamRoleArn": self.iam_role_arn,
        }
        if self.creator_request_id:
            dct["CreatorRequestId"] = self.creator_request_id
        return dct


class BackupJob(BaseModel):
    def __init__(
        self,
        backup_vault_name: str,
        resource_arn: str,
        iam_role_arn: str,
        backend: "BackupBackend",
        idempotency_token: Optional[str] = None,
        start_window_minutes: Optional[int] = None,
        complete_window_minutes: Optional[int] = None,
        lifecycle: Optional[dict[str, Any]] = None,
        recovery_point_tags: Optional[dict[str, str]] = None,
        backup_options: Optional[dict[str, str]] = None,
    ):
        self.backup_job_id = str(mock_random.uuid4())
        self.backup_vault_name = backup_vault_name
        partition = get_partition(backend.region_name)
        self.backup_vault_arn = (
            f"arn:{partition}:backup:{backend.region_name}"
            f":{backend.account_id}:backup-vault:{backup_vault_name}"
        )
        self.resource_arn = resource_arn
        self.iam_role_arn = iam_role_arn
        self.idempotency_token = idempotency_token
        self.start_window_minutes = start_window_minutes or 480
        self.complete_window_minutes = complete_window_minutes or 10080
        self.lifecycle = lifecycle if lifecycle is not None else {}
        self.recovery_point_tags = recovery_point_tags or {}
        self.backup_options = backup_options if backup_options is not None else {}
        self.creation_date = unix_time()
        self.completion_date: Optional[float] = None
        self.state = "CREATED"
        self.status_message = ""
        self.percent_done = "0.0"
        self.backup_size_in_bytes = 0
        self.account_id = backend.account_id
        self.region_name = backend.region_name
        self.resource_type = self._derive_resource_type(resource_arn)
        self.recovery_point_arn = (
            f"arn:{partition}:backup:{backend.region_name}"
            f":{backend.account_id}:recovery-point:{str(mock_random.uuid4())}"
        )

    @staticmethod
    def _derive_resource_type(resource_arn: str) -> str:
        parts = resource_arn.split(":")
        if len(parts) >= 3:
            service = parts[2]
            type_map = {
                "dynamodb": "DynamoDB",
                "ec2": "EC2",
                "rds": "RDS",
                "s3": "S3",
                "efs": "EFS",
                "ebs": "EBS",
            }
            return type_map.get(service, service)
        return "Unknown"

    def to_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "BackupJobId": self.backup_job_id,
            "BackupVaultName": self.backup_vault_name,
            "BackupVaultArn": self.backup_vault_arn,
            "ResourceArn": self.resource_arn,
            "IamRoleArn": self.iam_role_arn,
            "CreationDate": self.creation_date,
            "State": self.state,
            "StatusMessage": self.status_message,
            "PercentDone": self.percent_done,
            "BackupSizeInBytes": self.backup_size_in_bytes,
            "ResourceType": self.resource_type,
            "RecoveryPointArn": self.recovery_point_arn,
            "StartWindowMinutes": self.start_window_minutes,
            "CompleteWindowMinutes": self.complete_window_minutes,
            "AccountId": self.account_id,
        }
        if self.completion_date:
            dct["CompletionDate"] = self.completion_date
        if self.lifecycle:
            dct["RecoveryPointLifecycle"] = self.lifecycle
        if self.backup_options:
            dct["BackupOptions"] = self.backup_options
        return dct

    def to_list_dict(self) -> dict[str, Any]:
        return self.to_dict()


class Framework(BaseModel):
    def __init__(
        self,
        framework_name: str,
        framework_description: Optional[str],
        framework_controls: list[dict[str, Any]],
        idempotency_token: Optional[str],
        framework_tags: Optional[dict[str, str]],
        backend: "BackupBackend",
    ):
        self.framework_name = framework_name
        self.framework_description = framework_description or ""
        self.framework_controls = framework_controls
        self.idempotency_token = idempotency_token
        partition = get_partition(backend.region_name)
        short_id = str(mock_random.uuid4())[:8]
        self.framework_arn = (
            f"arn:{partition}:backup:{backend.region_name}"
            f":{backend.account_id}:framework:{framework_name}-{short_id}"
        )
        self.creation_time = unix_time()
        self.deployment_status = "COMPLETED"
        self.number_of_controls = len(framework_controls)

    def to_dict(self) -> dict[str, Any]:
        return {
            "FrameworkName": self.framework_name,
            "FrameworkArn": self.framework_arn,
        }

    def to_describe_dict(self) -> dict[str, Any]:
        return {
            "FrameworkName": self.framework_name,
            "FrameworkArn": self.framework_arn,
            "FrameworkDescription": self.framework_description,
            "FrameworkControls": self.framework_controls,
            "CreationTime": self.creation_time,
            "DeploymentStatus": self.deployment_status,
        }

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "FrameworkName": self.framework_name,
            "FrameworkArn": self.framework_arn,
            "FrameworkDescription": self.framework_description,
            "NumberOfControls": self.number_of_controls,
            "CreationTime": self.creation_time,
            "DeploymentStatus": self.deployment_status,
        }


class BackupBackend(BaseBackend):
    """Implementation of Backup APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)

        self.vaults: dict[str, Vault] = {}
        self.plans: dict[str, Plan] = {}
        self.report_plans: dict[str, ReportPlan] = {}
        self.selections: dict[str, dict[str, Selection]] = {}
        self.backup_jobs: dict[str, BackupJob] = {}
        self.frameworks: dict[str, Framework] = {}
        self.tagger = TaggingService()

    def create_backup_plan(
        self,
        backup_plan: dict[str, Any],
        backup_plan_tags: dict[str, str],
        creator_request_id: str,
    ) -> Plan:
        if backup_plan["BackupPlanName"] in [
            p.backup_plan["BackupPlanName"] for p in list(self.plans.values())
        ]:
            raise AlreadyExistsException(
                msg="Backup plan with the same plan document already exists"
            )
        plan = Plan(
            backup_plan=backup_plan,
            creator_request_id=creator_request_id,
            backend=self,
        )
        if backup_plan_tags:
            self.tag_resource(plan.backup_plan_arn, backup_plan_tags)
        self.plans[plan.backup_plan_id] = plan
        return plan

    def get_backup_plan(
        self, backup_plan_id: str, version_id: Optional[Any]
    ) -> Plan:
        msg = "Failed reading Backup plan with provided version"
        if backup_plan_id not in self.plans:
            raise ResourceNotFoundException(msg=msg)
        plan = self.plans[backup_plan_id]
        if version_id:
            if plan.version_id == version_id:
                return plan
            else:
                raise ResourceNotFoundException(msg=msg)
        return plan

    def delete_backup_plan(
        self, backup_plan_id: str
    ) -> tuple[str, str, float, str]:
        if backup_plan_id not in self.plans:
            raise ResourceNotFoundException(
                msg="Failed reading Backup plan with provided version"
            )
        deletion_date = unix_time()
        res = self.plans[backup_plan_id]
        res.deletion_date = deletion_date
        return (
            res.backup_plan_id,
            res.backup_plan_arn,
            deletion_date,
            res.version_id,
        )

    def list_backup_plans(self, include_deleted: Any) -> list[Plan]:
        """
        Pagination is not yet implemented
        """
        plans_list = deepcopy(self.plans)

        for plan in list(plans_list.values()):
            backup_plan_id = plan.backup_plan_id
            if plan.deletion_date is not None:
                plans_list.pop(backup_plan_id)
        if include_deleted:
            return list(self.plans.values())
        return list(plans_list.values())

    def update_backup_plan(
        self,
        backup_plan_id: str,
        backup_plan: dict[str, Any],
    ) -> Plan:
        if backup_plan_id not in self.plans:
            raise ResourceNotFoundException(
                msg="Failed reading Backup plan with provided version"
            )
        plan = self.plans[backup_plan_id]
        plan.backup_plan = backup_plan
        plan.creation_date = unix_time()
        ran_str = mock_random.get_random_string(length=48)
        plan.version_id = ran_str
        adv_settings = backup_plan.get("AdvancedBackupSettings")
        plan.advanced_backup_settings = adv_settings or []
        rules = backup_plan["Rules"]
        for rule in rules:
            rule["ScheduleExpression"] = rule.get(
                "ScheduleExpression", "cron(0 5 ? * * *)"
            )
            rule["StartWindowMinutes"] = rule.get(
                "StartWindowMinutes", 480
            )
            rule["CompletionWindowMinutes"] = rule.get(
                "CompletionWindowMinutes", 10080
            )
            rule["ScheduleExpressionTimezone"] = rule.get(
                "ScheduleExpressionTimezone", "Etc/UTC"
            )
            if "RuleId" not in rule:
                rule["RuleId"] = str(mock_random.uuid4())
        return plan

    def create_backup_vault(
        self,
        backup_vault_name: str,
        backup_vault_tags: dict[str, str],
        encryption_key_arn: str,
        creator_request_id: str,
    ) -> Vault:
        if backup_vault_name in self.vaults:
            raise AlreadyExistsException(
                msg="Backup vault with the same name already exists"
            )
        vault = Vault(
            backup_vault_name=backup_vault_name,
            encryption_key_arn=encryption_key_arn,
            creator_request_id=creator_request_id,
            backend=self,
        )
        if backup_vault_tags:
            self.tag_resource(vault.backup_vault_arn, backup_vault_tags)
        self.vaults[backup_vault_name] = vault
        return vault

    def describe_backup_vault(self, backup_vault_name: str) -> Vault:
        if backup_vault_name not in self.vaults:
            raise ResourceNotFoundException(backup_vault_name)
        return self.vaults[backup_vault_name]

    def delete_backup_vault(self, backup_vault_name: str) -> None:
        self.vaults.pop(backup_vault_name, None)

    def put_backup_vault_lock_configuration(
        self,
        backup_vault_name: str,
        min_retention_days: Optional[int],
        max_retention_days: Optional[int],
        changeable_for_days: Optional[int],
    ) -> None:
        if backup_vault_name not in self.vaults:
            raise ResourceNotFoundException(
                msg=f"Backup vault {backup_vault_name} not found"
            )

        vault = self.vaults[backup_vault_name]

        if vault.lock_date is not None and unix_time() >= vault.lock_date:
            raise InvalidRequestException(
                msg="Vault Lock configuration is immutable and cannot be modified"
            )

        if min_retention_days is not None and min_retention_days < 1:
            raise InvalidParameterValueException(
                msg="MinRetentionDays must be at least 1 day"
            )

        if max_retention_days is not None and max_retention_days > 36500:
            raise InvalidParameterValueException(
                msg="MaxRetentionDays cannot exceed 36500 days"
            )

        if (
            min_retention_days is not None
            and max_retention_days is not None
            and min_retention_days > max_retention_days
        ):
            raise InvalidParameterValueException(
                msg="MinRetentionDays cannot be greater than MaxRetentionDays"
            )

        if changeable_for_days is not None and changeable_for_days < 3:
            raise InvalidParameterValueException(
                msg="ChangeableForDays must be at least 3 days"
            )

        vault.locked = True
        vault.min_retention_days = min_retention_days
        vault.max_retention_days = max_retention_days
        vault.changeable_for_days = changeable_for_days

        if changeable_for_days is not None:
            vault.lock_date = unix_time() + (
                changeable_for_days * 24 * 60 * 60
            )

    def delete_backup_vault_lock_configuration(
        self,
        backup_vault_name: str,
    ) -> None:
        if backup_vault_name not in self.vaults:
            raise ResourceNotFoundException(
                msg=f"Backup vault {backup_vault_name} not found"
            )

        vault = self.vaults[backup_vault_name]

        if vault.lock_date is not None and unix_time() >= vault.lock_date:
            raise InvalidRequestException(
                msg="Vault Lock configuration is immutable and cannot be deleted"
            )

        vault.locked = False
        vault.min_retention_days = None
        vault.max_retention_days = None
        vault.lock_date = None
        vault.changeable_for_days = None

    def list_backup_vaults(self) -> list[Vault]:
        """
        Pagination is not yet implemented
        """
        return list(self.vaults.values())

    def list_tags(self, resource_arn: str) -> dict[str, str]:
        """
        Pagination is not yet implemented
        """
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        tags_input = TaggingService.convert_dict_to_tags_input(tags or {})
        self.tagger.tag_resource(resource_arn, tags_input)

    def untag_resource(
        self, resource_arn: str, tag_key_list: list[str]
    ) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_key_list)

    # --- Backup Selections ---

    def create_backup_selection(
        self,
        backup_plan_id: str,
        backup_selection: dict[str, Any],
        creator_request_id: Optional[str],
    ) -> Selection:
        if backup_plan_id not in self.plans:
            raise ResourceNotFoundException(
                msg="Failed reading Backup plan with provided version"
            )
        selection = Selection(
            backup_plan_id=backup_plan_id,
            selection=backup_selection,
            creator_request_id=creator_request_id,
            backend=self,
        )
        if backup_plan_id not in self.selections:
            self.selections[backup_plan_id] = {}
        self.selections[backup_plan_id][selection.selection_id] = selection
        return selection

    def get_backup_selection(
        self, backup_plan_id: str, selection_id: str
    ) -> Selection:
        if backup_plan_id not in self.plans:
            raise ResourceNotFoundException(
                msg="Failed reading Backup plan with provided version"
            )
        plan_selections = self.selections.get(backup_plan_id, {})
        if selection_id not in plan_selections:
            raise ResourceNotFoundException(
                msg=f"Backup Selection {selection_id} not found"
            )
        return plan_selections[selection_id]

    def delete_backup_selection(
        self, backup_plan_id: str, selection_id: str
    ) -> None:
        plan_selections = self.selections.get(backup_plan_id, {})
        plan_selections.pop(selection_id, None)

    def list_backup_selections(
        self, backup_plan_id: str
    ) -> list[Selection]:
        """
        Pagination is not yet implemented
        """
        if backup_plan_id not in self.plans:
            raise ResourceNotFoundException(
                msg="Failed reading Backup plan with provided version"
            )
        plan_selections = self.selections.get(backup_plan_id, {})
        return list(plan_selections.values())

    # --- Backup Jobs ---

    def start_backup_job(
        self,
        backup_vault_name: str,
        resource_arn: str,
        iam_role_arn: str,
        idempotency_token: Optional[str] = None,
        start_window_minutes: Optional[int] = None,
        complete_window_minutes: Optional[int] = None,
        lifecycle: Optional[dict[str, Any]] = None,
        recovery_point_tags: Optional[dict[str, str]] = None,
        backup_options: Optional[dict[str, str]] = None,
    ) -> BackupJob:
        if backup_vault_name not in self.vaults:
            raise ResourceNotFoundException(
                msg=f"Backup vault {backup_vault_name} not found"
            )
        job = BackupJob(
            backup_vault_name=backup_vault_name,
            resource_arn=resource_arn,
            iam_role_arn=iam_role_arn,
            backend=self,
            idempotency_token=idempotency_token,
            start_window_minutes=start_window_minutes,
            complete_window_minutes=complete_window_minutes,
            lifecycle=lifecycle,
            recovery_point_tags=recovery_point_tags,
            backup_options=backup_options,
        )
        # Simulate immediate completion
        job.state = "COMPLETED"
        job.completion_date = unix_time()
        job.percent_done = "100.0"
        self.backup_jobs[job.backup_job_id] = job
        return job

    def describe_backup_job(self, backup_job_id: str) -> BackupJob:
        if backup_job_id not in self.backup_jobs:
            raise ResourceNotFoundException(
                msg=f"Backup job {backup_job_id} not found"
            )
        return self.backup_jobs[backup_job_id]

    def list_backup_jobs(
        self,
        by_backup_vault_name: Optional[str] = None,
        by_state: Optional[str] = None,
        by_resource_arn: Optional[str] = None,
        by_resource_type: Optional[str] = None,
        by_account_id: Optional[str] = None,
    ) -> list[BackupJob]:
        """
        Pagination is not yet implemented
        """
        jobs = list(self.backup_jobs.values())
        if by_backup_vault_name:
            jobs = [
                j for j in jobs
                if j.backup_vault_name == by_backup_vault_name
            ]
        if by_state:
            jobs = [j for j in jobs if j.state == by_state]
        if by_resource_arn:
            jobs = [j for j in jobs if j.resource_arn == by_resource_arn]
        if by_resource_type:
            jobs = [j for j in jobs if j.resource_type == by_resource_type]
        if by_account_id:
            jobs = [j for j in jobs if j.account_id == by_account_id]
        return jobs

    def stop_backup_job(self, backup_job_id: str) -> None:
        if backup_job_id not in self.backup_jobs:
            raise ResourceNotFoundException(
                msg=f"Backup job {backup_job_id} not found"
            )
        job = self.backup_jobs[backup_job_id]
        if job.state not in ("CREATED", "RUNNING"):
            raise InvalidRequestException(
                msg=f"Backup job {backup_job_id} is not in a cancelable state"
            )
        job.state = "ABORTED"
        job.completion_date = unix_time()
        job.status_message = "Backup job was stopped by user"

    # --- Frameworks ---

    def create_framework(
        self,
        framework_name: str,
        framework_description: Optional[str],
        framework_controls: list[dict[str, Any]],
        idempotency_token: Optional[str],
        framework_tags: Optional[dict[str, str]],
    ) -> Framework:
        if framework_name in self.frameworks:
            raise AlreadyExistsException(
                msg=f"Framework {framework_name} already exists"
            )
        framework = Framework(
            framework_name=framework_name,
            framework_description=framework_description,
            framework_controls=framework_controls,
            idempotency_token=idempotency_token,
            framework_tags=framework_tags,
            backend=self,
        )
        if framework_tags:
            self.tag_resource(framework.framework_arn, framework_tags)
        self.frameworks[framework_name] = framework
        return framework

    def describe_framework(self, framework_name: str) -> Framework:
        if framework_name not in self.frameworks:
            raise ResourceNotFoundException(
                msg=f"Framework {framework_name} not found"
            )
        return self.frameworks[framework_name]

    def delete_framework(self, framework_name: str) -> None:
        if framework_name not in self.frameworks:
            raise ResourceNotFoundException(
                msg=f"Framework {framework_name} not found"
            )
        self.frameworks.pop(framework_name)

    def list_frameworks(self) -> list[Framework]:
        """
        Pagination is not yet implemented
        """
        return list(self.frameworks.values())

    def update_framework(
        self,
        framework_name: str,
        framework_description: Optional[str],
        framework_controls: Optional[list[dict[str, Any]]],
        idempotency_token: Optional[str],
    ) -> Framework:
        if framework_name not in self.frameworks:
            raise ResourceNotFoundException(
                msg=f"Framework {framework_name} not found"
            )
        framework = self.frameworks[framework_name]
        if framework_description is not None:
            framework.framework_description = framework_description
        if framework_controls is not None:
            framework.framework_controls = framework_controls
            framework.number_of_controls = len(framework_controls)
        if idempotency_token is not None:
            framework.idempotency_token = idempotency_token
        return framework

    # --- Report Plans ---

    def create_report_plan(
        self,
        report_plan_name: str,
        report_plan_description: Optional[str],
        report_delivery_channel: dict[str, Any],
        report_setting: dict[str, Any],
    ) -> ReportPlan:
        """
        The parameters ReportPlanTags and IdempotencyToken are not yet
        supported
        """
        report_plan = ReportPlan(
            name=report_plan_name,
            report_setting=report_setting,
            report_plan_description=report_plan_description,
            report_delivery_channel=report_delivery_channel,
            backend=self,
        )
        self.report_plans[report_plan_name] = report_plan
        return report_plan

    def describe_report_plan(
        self, report_plan_name: str
    ) -> ReportPlan:
        if report_plan_name not in self.report_plans:
            raise ResourceNotFoundException(
                msg=f"Report Plan {report_plan_name} not found"
            )
        return self.report_plans[report_plan_name]

    def delete_report_plan(self, report_plan_name: str) -> None:
        self.report_plans.pop(report_plan_name, None)

    def list_report_plans(self) -> list[ReportPlan]:
        """
        Pagination is not yet implemented
        """
        return list(self.report_plans.values())


backup_backends = BackendDict(BackupBackend, "backup")
