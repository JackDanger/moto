"""Handles incoming backup requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .models import BackupBackend, backup_backends


class BackupResponse(BaseResponse):
    """Handler for Backup requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="backup")

    @property
    def backup_backend(self) -> BackupBackend:
        """Return backend instance specific for this region."""
        return backup_backends[self.current_account][self.region]

    def create_backup_plan(self) -> str:
        params = json.loads(self.body)
        backup_plan = params.get("BackupPlan")
        backup_plan_tags = params.get("BackupPlanTags")
        creator_request_id = params.get("CreatorRequestId")
        plan = self.backup_backend.create_backup_plan(
            backup_plan=backup_plan,
            backup_plan_tags=backup_plan_tags,
            creator_request_id=creator_request_id,
        )
        return json.dumps(dict(plan.to_dict()))

    def get_backup_plan(self) -> str:
        params = self._get_params()
        backup_plan_id = self.path.split("/plans/")[-1]
        backup_plan_id = backup_plan_id.replace("/", "")
        version_id = params.get("versionId")
        plan = self.backup_backend.get_backup_plan(
            backup_plan_id=backup_plan_id, version_id=version_id
        )
        return json.dumps(dict(plan.to_get_dict()))

    def delete_backup_plan(self) -> str:
        backup_plan_id = self.path.split("/")[-1]
        (
            backup_plan_id,
            backup_plan_arn,
            deletion_date,
            version_id,
        ) = self.backup_backend.delete_backup_plan(
            backup_plan_id=backup_plan_id,
        )
        return json.dumps(
            {
                "BackupPlanId": backup_plan_id,
                "BackupPlanArn": backup_plan_arn,
                "DeletionDate": deletion_date,
                "VersionId": version_id,
            }
        )

    def list_backup_plans(self) -> str:
        params = self._get_params()
        include_deleted = params.get("includeDeleted")
        backup_plans_list = self.backup_backend.list_backup_plans(
            include_deleted=include_deleted
        )
        return json.dumps(
            {
                "BackupPlansList": [
                    p.to_list_dict() for p in backup_plans_list
                ]
            }
        )

    def update_backup_plan(self) -> str:
        backup_plan_id = self.path.split("/")[-1]
        params = json.loads(self.body)
        backup_plan = params.get("BackupPlan")
        plan = self.backup_backend.update_backup_plan(
            backup_plan_id=backup_plan_id,
            backup_plan=backup_plan,
        )
        return json.dumps(dict(plan.to_dict()))

    def create_backup_vault(self) -> str:
        params = json.loads(self.body)
        backup_vault_name = self.path.split("/")[-1]
        backup_vault_tags = params.get("BackupVaultTags")
        encryption_key_arn = params.get("EncryptionKeyArn")
        creator_request_id = params.get("CreatorRequestId")
        backup_vault = self.backup_backend.create_backup_vault(
            backup_vault_name=backup_vault_name,
            backup_vault_tags=backup_vault_tags,
            encryption_key_arn=encryption_key_arn,
            creator_request_id=creator_request_id,
        )
        return json.dumps(dict(backup_vault.to_dict()))

    def delete_backup_vault(self) -> EmptyResult:
        backup_vault_name = self.path.split("/")[-1]
        self.backup_backend.delete_backup_vault(backup_vault_name)
        return EmptyResult()

    def describe_backup_vault(self) -> ActionResult:
        backup_vault_name = self.path.split("/")[-1]
        vault = self.backup_backend.describe_backup_vault(backup_vault_name)
        return ActionResult(result=vault)

    def list_backup_vaults(self) -> str:
        backup_vault_list = self.backup_backend.list_backup_vaults()
        return json.dumps(
            {
                "BackupVaultList": [
                    v.to_list_dict() for v in backup_vault_list
                ]
            }
        )

    def list_tags(self) -> str:
        resource_arn = unquote(self.path.split("/")[-2])
        tags = self.backup_backend.list_tags(
            resource_arn=resource_arn,
        )
        return json.dumps({"Tags": tags})

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = unquote(self.path.split("/")[-1])
        tags = params.get("Tags")
        self.backup_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return "{}"

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = unquote(self.path.split("/")[-1])
        tag_key_list = params.get("TagKeyList")
        self.backup_backend.untag_resource(
            resource_arn=resource_arn,
            tag_key_list=tag_key_list,
        )
        return "{}"

    # --- Backup Selections ---

    def create_backup_selection(self) -> str:
        parts = self.path.split("/")
        plan_idx = parts.index("plans")
        backup_plan_id = parts[plan_idx + 1]
        params = json.loads(self.body)
        backup_selection = params.get("BackupSelection")
        creator_request_id = params.get("CreatorRequestId")
        selection = self.backup_backend.create_backup_selection(
            backup_plan_id=backup_plan_id,
            backup_selection=backup_selection,
            creator_request_id=creator_request_id,
        )
        return json.dumps(dict(selection.to_dict()))

    def get_backup_selection(self) -> str:
        parts = self.path.split("/")
        plan_idx = parts.index("plans")
        backup_plan_id = parts[plan_idx + 1]
        sel_idx = parts.index("selections")
        selection_id = parts[sel_idx + 1].rstrip("/")
        selection = self.backup_backend.get_backup_selection(
            backup_plan_id=backup_plan_id,
            selection_id=selection_id,
        )
        return json.dumps(dict(selection.to_get_dict()))

    def delete_backup_selection(self) -> EmptyResult:
        parts = self.path.split("/")
        plan_idx = parts.index("plans")
        backup_plan_id = parts[plan_idx + 1]
        sel_idx = parts.index("selections")
        selection_id = parts[sel_idx + 1].rstrip("/")
        self.backup_backend.delete_backup_selection(
            backup_plan_id=backup_plan_id,
            selection_id=selection_id,
        )
        return EmptyResult()

    def list_backup_selections(self) -> str:
        parts = self.path.split("/")
        plan_idx = parts.index("plans")
        backup_plan_id = parts[plan_idx + 1]
        selections = self.backup_backend.list_backup_selections(
            backup_plan_id=backup_plan_id,
        )
        return json.dumps(
            {
                "BackupSelectionsList": [
                    s.to_list_dict() for s in selections
                ]
            }
        )

    # --- Backup Jobs ---

    def start_backup_job(self) -> str:
        params = json.loads(self.body)
        job = self.backup_backend.start_backup_job(
            backup_vault_name=params.get("BackupVaultName"),
            resource_arn=params.get("ResourceArn"),
            iam_role_arn=params.get("IamRoleArn"),
            idempotency_token=params.get("IdempotencyToken"),
            start_window_minutes=params.get("StartWindowMinutes"),
            complete_window_minutes=params.get("CompleteWindowMinutes"),
            lifecycle=params.get("Lifecycle"),
            recovery_point_tags=params.get("RecoveryPointTags"),
            backup_options=params.get("BackupOptions"),
        )
        return json.dumps(
            {
                "BackupJobId": job.backup_job_id,
                "RecoveryPointArn": job.recovery_point_arn,
                "CreationDate": job.creation_date,
            }
        )

    def describe_backup_job(self) -> str:
        backup_job_id = self.path.split("/")[-1].rstrip("/")
        job = self.backup_backend.describe_backup_job(
            backup_job_id=backup_job_id
        )
        return json.dumps(dict(job.to_dict()))

    def list_backup_jobs(self) -> str:
        params = self._get_params()
        jobs = self.backup_backend.list_backup_jobs(
            by_backup_vault_name=params.get("backupVaultName"),
            by_state=params.get("state"),
            by_resource_arn=params.get("resourceArn"),
            by_resource_type=params.get("resourceType"),
            by_account_id=params.get("accountId"),
        )
        return json.dumps(
            {"BackupJobs": [j.to_list_dict() for j in jobs]}
        )

    def stop_backup_job(self) -> EmptyResult:
        backup_job_id = self.path.split("/")[-1].rstrip("/")
        self.backup_backend.stop_backup_job(backup_job_id=backup_job_id)
        return EmptyResult()

    # --- Frameworks ---

    def create_framework(self) -> str:
        params = json.loads(self.body)
        framework = self.backup_backend.create_framework(
            framework_name=params.get("FrameworkName"),
            framework_description=params.get("FrameworkDescription"),
            framework_controls=params.get("FrameworkControls", []),
            idempotency_token=params.get("IdempotencyToken"),
            framework_tags=params.get("FrameworkTags"),
        )
        return json.dumps(dict(framework.to_dict()))

    def describe_framework(self) -> str:
        framework_name = self.path.split("/")[-1].rstrip("/")
        framework = self.backup_backend.describe_framework(
            framework_name=framework_name,
        )
        return json.dumps(dict(framework.to_describe_dict()))

    def delete_framework(self) -> EmptyResult:
        framework_name = self.path.split("/")[-1].rstrip("/")
        self.backup_backend.delete_framework(
            framework_name=framework_name
        )
        return EmptyResult()

    def list_frameworks(self) -> str:
        frameworks = self.backup_backend.list_frameworks()
        return json.dumps(
            {"Frameworks": [f.to_list_dict() for f in frameworks]}
        )

    def update_framework(self) -> str:
        framework_name = self.path.split("/")[-1].rstrip("/")
        params = json.loads(self.body)
        framework = self.backup_backend.update_framework(
            framework_name=framework_name,
            framework_description=params.get("FrameworkDescription"),
            framework_controls=params.get("FrameworkControls"),
            idempotency_token=params.get("IdempotencyToken"),
        )
        return json.dumps(dict(framework.to_dict()))

    # --- Vault Lock ---

    def put_backup_vault_lock_configuration(self) -> str:
        backup_vault_name = self.path.split("/")[-2]
        params = json.loads(self.body) if self.body else {}
        min_retention_days = params.get("MinRetentionDays")
        max_retention_days = params.get("MaxRetentionDays")
        changeable_for_days = params.get("ChangeableForDays")

        self.backup_backend.put_backup_vault_lock_configuration(
            backup_vault_name=backup_vault_name,
            min_retention_days=min_retention_days,
            max_retention_days=max_retention_days,
            changeable_for_days=changeable_for_days,
        )

        return "{}"

    def delete_backup_vault_lock_configuration(self) -> str:
        backup_vault_name = self.path.split("/")[-2]

        self.backup_backend.delete_backup_vault_lock_configuration(
            backup_vault_name=backup_vault_name,
        )

        return "{}"

    # --- Report Plans ---

    def list_report_plans(self) -> ActionResult:
        report_plans = self.backup_backend.list_report_plans()
        return ActionResult(result={"ReportPlans": report_plans})

    def create_report_plan(self) -> ActionResult:
        report_plan_name = self._get_param("ReportPlanName")
        report_plan_description = self._get_param("ReportPlanDescription")
        report_delivery_channel = self._get_param("ReportDeliveryChannel")
        report_setting = self._get_param("ReportSetting")
        report_plan = self.backup_backend.create_report_plan(
            report_plan_name=report_plan_name,
            report_plan_description=report_plan_description,
            report_delivery_channel=report_delivery_channel,
            report_setting=report_setting,
        )
        return ActionResult(result=report_plan)

    def describe_report_plan(self) -> ActionResult:
        report_plan_name = self._get_param("reportPlanName")
        report_plan = self.backup_backend.describe_report_plan(
            report_plan_name=report_plan_name
        )
        return ActionResult(result={"ReportPlan": report_plan})

    def delete_report_plan(self) -> EmptyResult:
        report_plan_name = self.path.split("/report-plans/")[-1]
        plan_name = report_plan_name.replace("/", "")
        self.backup_backend.delete_report_plan(
            report_plan_name=plan_name
        )
        return EmptyResult()

    # --- Global/Region Settings ---

    def describe_global_settings(self) -> str:
        settings = self.backup_backend.describe_global_settings()
        return json.dumps({"GlobalSettings": settings})

    def update_global_settings(self) -> str:
        params = json.loads(self.body)
        global_settings = params.get("GlobalSettings", {})
        self.backup_backend.update_global_settings(global_settings)
        return "{}"

    def describe_region_settings(self) -> str:
        settings = self.backup_backend.describe_region_settings()
        return json.dumps({"ResourceTypeOptInPreference": settings})

    def update_region_settings(self) -> str:
        params = json.loads(self.body)
        pref = params.get("ResourceTypeOptInPreference")
        self.backup_backend.update_region_settings(pref)
        return "{}"

    # --- Supported Resource Types ---

    def get_supported_resource_types(self) -> str:
        types = self.backup_backend.get_supported_resource_types()
        return json.dumps({"ResourceTypes": types})

    # --- Backup Plan Templates ---

    def list_backup_plan_templates(self) -> str:
        templates = self.backup_backend.list_backup_plan_templates()
        return json.dumps({"BackupPlanTemplatesList": templates})

    def get_backup_plan_from_json(self) -> str:
        params = json.loads(self.body)
        template_json = params.get("BackupPlanTemplateJson", "{}")
        plan = self.backup_backend.get_backup_plan_from_json(
            backup_plan_template_json=template_json,
        )
        return json.dumps({"BackupPlan": plan})

    # --- Backup Plan Versions ---

    def list_backup_plan_versions(self) -> str:
        backup_plan_id = self.path.split("/plans/")[1].split("/")[0]
        versions = self.backup_backend.list_backup_plan_versions(
            backup_plan_id=backup_plan_id,
        )
        return json.dumps(
            {
                "BackupPlanVersionsList": [
                    v.to_list_dict() for v in versions
                ]
            }
        )

    # --- Copy Jobs ---

    def start_copy_job(self) -> str:
        params = json.loads(self.body)
        job = self.backup_backend.start_copy_job(
            source_backup_vault_name=params.get("SourceBackupVaultName"),
            destination_backup_vault_arn=params.get(
                "DestinationBackupVaultArn"
            ),
            recovery_point_arn=params.get("RecoveryPointArn"),
            iam_role_arn=params.get("IamRoleArn"),
            idempotency_token=params.get("IdempotencyToken"),
            lifecycle=params.get("Lifecycle"),
        )
        return json.dumps(
            {
                "CopyJobId": job.copy_job_id,
                "CreationDate": job.creation_date,
            }
        )

    def describe_copy_job(self) -> str:
        copy_job_id = self.path.split("/")[-1].rstrip("/")
        job = self.backup_backend.describe_copy_job(
            copy_job_id=copy_job_id
        )
        return json.dumps({"CopyJob": job.to_dict()})

    def list_copy_jobs(self) -> str:
        params = self._get_params()
        jobs = self.backup_backend.list_copy_jobs(
            by_state=params.get("state"),
            by_resource_arn=params.get("resourceArn"),
            by_resource_type=params.get("resourceType"),
            by_account_id=params.get("accountId"),
            by_destination_vault_arn=params.get("destinationVaultArn"),
        )
        return json.dumps(
            {"CopyJobs": [j.to_dict() for j in jobs]}
        )

    # --- Recovery Points ---

    def describe_recovery_point(self) -> str:
        # Path: /backup-vaults/{name}/recovery-points/{arn}
        parts = self.path.split("/")
        vault_idx = parts.index("backup-vaults")
        backup_vault_name = parts[vault_idx + 1]
        rp_idx = parts.index("recovery-points")
        recovery_point_arn = unquote("/".join(parts[rp_idx + 1:]).rstrip("/"))
        rp = self.backup_backend.describe_recovery_point(
            backup_vault_name=backup_vault_name,
            recovery_point_arn=recovery_point_arn,
        )
        return json.dumps(rp.to_dict())

    # --- Protected Resources ---

    def describe_protected_resource(self) -> str:
        # Path: /resources/{arn}
        resource_arn = unquote(self.path.split("/resources/")[1].rstrip("/"))
        result = self.backup_backend.describe_protected_resource(
            resource_arn=resource_arn,
        )
        return json.dumps(result)

    def list_protected_resources(self) -> str:
        resources = self.backup_backend.list_protected_resources()
        return json.dumps({"Results": resources})

    # --- Vault Access Policy ---

    def put_backup_vault_access_policy(self) -> str:
        backup_vault_name = self.path.split("/backup-vaults/")[1].split("/")[0]
        params = json.loads(self.body) if self.body else {}
        policy = params.get("Policy", "")
        self.backup_backend.put_backup_vault_access_policy(
            backup_vault_name=backup_vault_name,
            policy=policy,
        )
        return "{}"

    def get_backup_vault_access_policy(self) -> str:
        backup_vault_name = self.path.split("/backup-vaults/")[1].split("/")[0]
        result = self.backup_backend.get_backup_vault_access_policy(
            backup_vault_name=backup_vault_name,
        )
        return json.dumps(result)

    def delete_backup_vault_access_policy(self) -> str:
        backup_vault_name = self.path.split("/backup-vaults/")[1].split("/")[0]
        self.backup_backend.delete_backup_vault_access_policy(
            backup_vault_name=backup_vault_name,
        )
        return "{}"

    # --- Vault Notifications ---

    def put_backup_vault_notifications(self) -> str:
        backup_vault_name = self.path.split("/backup-vaults/")[1].split("/")[0]
        params = json.loads(self.body) if self.body else {}
        sns_topic_arn = params.get("SNSTopicArn", "")
        events = params.get("BackupVaultEvents", [])
        self.backup_backend.put_backup_vault_notifications(
            backup_vault_name=backup_vault_name,
            sns_topic_arn=sns_topic_arn,
            backup_vault_events=events,
        )
        return "{}"

    def get_backup_vault_notifications(self) -> str:
        backup_vault_name = self.path.split("/backup-vaults/")[1].split("/")[0]
        result = self.backup_backend.get_backup_vault_notifications(
            backup_vault_name=backup_vault_name,
        )
        return json.dumps(result)

    def delete_backup_vault_notifications(self) -> str:
        backup_vault_name = self.path.split("/backup-vaults/")[1].split("/")[0]
        self.backup_backend.delete_backup_vault_notifications(
            backup_vault_name=backup_vault_name,
        )
        return "{}"

    # --- Restore Testing Plans ---

    def create_restore_testing_plan(self) -> str:
        params = json.loads(self.body)
        rtp = params.get("RestoreTestingPlan", {})
        tags = params.get("Tags")
        plan = self.backup_backend.create_restore_testing_plan(
            restore_testing_plan_name=rtp.get("RestoreTestingPlanName"),
            schedule_expression=rtp.get("ScheduleExpression"),
            recovery_point_selection=rtp.get("RecoveryPointSelection", {}),
            schedule_expression_timezone=rtp.get("ScheduleExpressionTimezone"),
            start_window_hours=rtp.get("StartWindowHours"),
            tags=tags,
        )
        return json.dumps(
            {
                "CreationTime": plan.creation_time,
                "RestoreTestingPlanArn": plan.restore_testing_plan_arn,
                "RestoreTestingPlanName": plan.restore_testing_plan_name,
            }
        )

    def get_restore_testing_plan(self) -> str:
        plan_name = self.path.split("/restore-testing/plans/")[1].rstrip("/")
        plan = self.backup_backend.get_restore_testing_plan(
            restore_testing_plan_name=plan_name,
        )
        return json.dumps({"RestoreTestingPlan": plan.to_dict()})

    def delete_restore_testing_plan(self) -> EmptyResult:
        plan_name = self.path.split("/restore-testing/plans/")[1].rstrip("/")
        self.backup_backend.delete_restore_testing_plan(
            restore_testing_plan_name=plan_name,
        )
        return EmptyResult()

    def list_restore_testing_plans(self) -> str:
        plans = self.backup_backend.list_restore_testing_plans()
        return json.dumps(
            {
                "RestoreTestingPlans": [
                    p.to_list_dict() for p in plans
                ]
            }
        )

    # --- Restore Testing Selections ---

    def create_restore_testing_selection(self) -> str:
        parts = self.path.split("/")
        plan_idx = parts.index("plans")
        plan_name = parts[plan_idx + 1]
        params = json.loads(self.body)
        rts = params.get("RestoreTestingSelection", {})
        selection = self.backup_backend.create_restore_testing_selection(
            restore_testing_plan_name=plan_name,
            restore_testing_selection_name=rts.get(
                "RestoreTestingSelectionName"
            ),
            protected_resource_type=rts.get("ProtectedResourceType"),
            iam_role_arn=rts.get("IamRoleArn"),
            protected_resource_arns=rts.get("ProtectedResourceArns"),
            protected_resource_conditions=rts.get(
                "ProtectedResourceConditions"
            ),
            restore_metadata_overrides=rts.get("RestoreMetadataOverrides"),
            validation_window_hours=rts.get("ValidationWindowHours"),
        )
        return json.dumps(
            {
                "CreationTime": selection.creation_time,
                "RestoreTestingPlanArn": self.backup_backend.restore_testing_plans[
                    plan_name
                ].restore_testing_plan_arn,
                "RestoreTestingPlanName": plan_name,
                "RestoreTestingSelectionName": selection.restore_testing_selection_name,
            }
        )

    def get_restore_testing_selection(self) -> str:
        parts = self.path.split("/")
        plan_idx = parts.index("plans")
        plan_name = parts[plan_idx + 1]
        sel_idx = parts.index("selections")
        sel_name = parts[sel_idx + 1].rstrip("/")
        selection = self.backup_backend.get_restore_testing_selection(
            restore_testing_plan_name=plan_name,
            restore_testing_selection_name=sel_name,
        )
        return json.dumps({"RestoreTestingSelection": selection.to_dict()})

    def delete_restore_testing_selection(self) -> EmptyResult:
        parts = self.path.split("/")
        plan_idx = parts.index("plans")
        plan_name = parts[plan_idx + 1]
        sel_idx = parts.index("selections")
        sel_name = parts[sel_idx + 1].rstrip("/")
        self.backup_backend.delete_restore_testing_selection(
            restore_testing_plan_name=plan_name,
            restore_testing_selection_name=sel_name,
        )
        return EmptyResult()

    def list_restore_testing_selections(self) -> str:
        parts = self.path.split("/")
        plan_idx = parts.index("plans")
        plan_name = parts[plan_idx + 1]
        selections = self.backup_backend.list_restore_testing_selections(
            restore_testing_plan_name=plan_name,
        )
        return json.dumps(
            {
                "RestoreTestingSelections": [
                    s.to_dict() for s in selections
                ]
            }
        )
