from moto.core.common_types import TYPE_RESPONSE
from typing import Any

import xmltodict

from moto.core.responses import (
    ActionResult,
    BaseResponse,
    EmptyResult,
)

from .models import S3ControlBackend, s3control_backends


class S3ControlResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="s3control")
        self.automated_parameter_parsing = True

    @property
    def backend(self) -> S3ControlBackend:
        return s3control_backends[self.current_account][self.partition]

    def get_public_access_block(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        public_block_config = self.backend.get_public_access_block(
            account_id=account_id
        )
        return ActionResult({"PublicAccessBlockConfiguration": public_block_config})

    def put_public_access_block(self) -> EmptyResult:
        account_id = self._get_param("AccountId")
        pab_config = self._get_param("PublicAccessBlockConfiguration", {})
        self.backend.put_public_access_block(account_id, pab_config)
        return EmptyResult()

    def delete_public_access_block(self) -> EmptyResult:
        account_id = self._get_param("AccountId")
        self.backend.delete_public_access_block(account_id=account_id)
        return EmptyResult()

    def create_access_point(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")
        bucket = self._get_param("Bucket")
        vpc_configuration = self._get_param("VpcConfiguration")
        public_access_block_configuration = self._get_param(
            "PublicAccessBlockConfiguration"
        )
        access_point = self.backend.create_access_point(
            account_id=account_id,
            name=name,
            bucket=bucket,
            vpc_configuration=vpc_configuration,
            public_access_block_configuration=public_access_block_configuration,
        )
        return ActionResult(
            {
                "AccessPointArn": access_point.arn,
                "Alias": access_point.alias,
            }
        )

    def get_access_point(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")
        access_point = self.backend.get_access_point(account_id=account_id, name=name)
        return ActionResult(
            {
                "Name": access_point.name,
                "Bucket": access_point.bucket,
                "NetworkOrigin": access_point.network_origin,
                "VpcConfiguration": {"VpcId": access_point.vpc_id}
                if access_point.vpc_id
                else None,
                "PublicAccessBlockConfiguration": access_point.pubc,
                "CreationDate": access_point.created,
                "Alias": access_point.alias,
                "AccessPointArn": access_point.arn,
                "Endpoints": {
                    "ipv4": "s3-accesspoint.us-east-1.amazonaws.com",
                    "fips": "s3-accesspoint-fips.us-east-1.amazonaws.com",
                    "fips_dualstack": "s3-accesspoint-fips.dualstack.us-east-1.amazonaws.com",
                    "dualstack": "s3-accesspoint.dualstack.us-east-1.amazonaws.com",
                },
            }
        )

    def delete_access_point(self) -> EmptyResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")
        self.backend.delete_access_point(account_id=account_id, name=name)
        return EmptyResult()

    def put_access_point_policy(self) -> EmptyResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")
        policy = self._get_param("Policy")
        self.backend.put_access_point_policy(account_id, name, policy)
        return EmptyResult()

    def get_access_point_policy(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")
        policy = self.backend.get_access_point_policy(account_id, name)
        return ActionResult({"Policy": policy})

    def delete_access_point_policy(self) -> EmptyResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")
        self.backend.delete_access_point_policy(account_id=account_id, name=name)
        return EmptyResult()

    def get_access_point_policy_status(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")
        self.backend.get_access_point_policy_status(account_id, name)
        return ActionResult({"PolicyStatus": {"IsPublic": True}})

    def put_storage_lens_configuration(self) -> EmptyResult:
        account_id = self._get_param("AccountId")
        config_id = self._get_param("ConfigId")
        storage_lens_configuration = self._get_param("StorageLensConfiguration")
        tags = self._get_param("Tags")
        self.backend.put_storage_lens_configuration(
            config_id=config_id,
            account_id=account_id,
            storage_lens_configuration=storage_lens_configuration,
            tags=tags,
        )
        return EmptyResult()

    def get_storage_lens_configuration(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        config_id = self._get_param("ConfigId")
        storage_lens_configuration = self.backend.get_storage_lens_configuration(
            config_id=config_id,
            account_id=account_id,
        )
        return ActionResult(
            {"StorageLensConfiguration": storage_lens_configuration.config}
        )

    def delete_storage_lens_configuration(self) -> EmptyResult:
        account_id = self._get_param("AccountId")
        config_id = self._get_param("ConfigId")
        self.backend.delete_storage_lens_configuration(
            config_id=config_id,
            account_id=account_id,
        )
        return EmptyResult()

    def list_storage_lens_configurations(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        next_token = self._get_param("NextToken")
        storage_lens_configuration_list, next_token = (
            self.backend.list_storage_lens_configurations(
                account_id=account_id,
                next_token=next_token,
            )
        )
        configs = [
            {
                "Id": config.config.get("Id"),
                "IsEnabled": config.config.get("IsEnabled"),
                "StorageLensArn": config.arn,
            }
            for config in storage_lens_configuration_list
        ]
        result = {"StorageLensConfigurationList": configs, "NextToken": next_token}
        return ActionResult(result)

    def put_storage_lens_configuration_tagging(self) -> EmptyResult:
        account_id = self._get_param("AccountId")
        config_id = self._get_param("ConfigId")
        tags = self._get_param("Tags")
        self.backend.put_storage_lens_configuration_tagging(
            config_id=config_id,
            account_id=account_id,
            tags=tags,
        )
        return EmptyResult()

    def get_storage_lens_configuration_tagging(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        config_id = self._get_param("ConfigId")
        storage_lens_tags = self.backend.get_storage_lens_configuration_tagging(
            config_id=config_id,
            account_id=account_id,
        )
        return ActionResult({"Tags": storage_lens_tags})

    def list_access_points(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        bucket = self._get_param("Bucket")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")

        access_points, next_token = self.backend.list_access_points(
            account_id=account_id,
            bucket=bucket,
            max_results=max_results,
            next_token=next_token,
        )

        ap_list = [
            {
                "Name": ap.name,
                "NetworkOrigin": ap.network_origin,
                "VpcConfiguration": {"VpcId": ap.vpc_id} if ap.vpc_id else None,
                "Bucket": ap.bucket,
                "AccessPointArn": ap.arn,
                "Alias": ap.alias,
            }
            for ap in access_points
        ]
        result: dict[str, Any] = {"AccessPointList": ap_list}
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    def create_multi_region_access_point(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Details.Name")
        regions = self._get_param("Details.Regions", [])
        public_access_block = self._get_param("Details.PublicAccessBlock", {})
        operation = self.backend.create_multi_region_access_point(
            account_id=account_id,
            name=name,
            public_access_block=public_access_block,
            regions=regions,
            region_name=self.region,
        )
        return ActionResult({"RequestTokenARN": operation.request_token_arn})

    def delete_multi_region_access_point(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        details = self._get_param("Details", {})
        name = details.get("Name")

        operation = self.backend.delete_multi_region_access_point(
            account_id=account_id,
            name=name,
            region_name=self.region,
        )
        return ActionResult({"RequestTokenARN": operation.request_token_arn})

    def describe_multi_region_access_point_operation(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        request_token = self._get_param("RequestTokenARN")

        operation = self.backend.describe_multi_region_access_point_operation(
            account_id=account_id,
            request_token_arn=request_token,
        )
        return ActionResult({"AsyncOperation": operation.to_dict()})

    def get_multi_region_access_point(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")

        mrap = self.backend.get_multi_region_access_point(
            account_id=account_id,
            name=name,
        )
        return ActionResult({"AccessPoint": mrap.to_dict()})

    def get_multi_region_access_point_policy(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")

        policy = self.backend.get_multi_region_access_point_policy(
            account_id=account_id,
            name=name,
        )
        return ActionResult({"Policy": {"Established": {"Policy": policy}}})

    def get_multi_region_access_point_policy_status(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        name = self._get_param("Name")

        policy_status = self.backend.get_multi_region_access_point_policy_status(
            account_id=account_id,
            name=name,
        )
        return ActionResult({"Established": {"IsPublic": policy_status["IsPublic"]}})

    def list_multi_region_access_points(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")

        mraps, next_token = self.backend.list_multi_region_access_points(
            account_id=account_id,
            max_results=max_results,
            next_token=next_token,
        )

        result: dict[str, Any] = {
            "AccessPoints": [mrap.to_dict() for mrap in mraps],
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    def put_multi_region_access_point_policy(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        details = self._get_param("Details", {})
        name = details.get("Name")
        policy = details.get("Policy")

        operation = self.backend.put_multi_region_access_point_policy(
            account_id=account_id,
            name=name,
            policy=policy,
            region_name=self.region,
        )
        return ActionResult({"RequestTokenARN": operation.request_token_arn})

    def list_tags_for_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        tags = self.backend.list_tags_for_resource(resource_arn)
        return ActionResult(result={"Tags": tags})

    def tag_resource(self) -> EmptyResult:
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags", [])
        self.backend.tag_resource(resource_arn, tags=tags)
        return EmptyResult()

    def untag_resource(self) -> EmptyResult:
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys", [])
        self.backend.untag_resource(resource_arn, tag_keys=tag_keys)
        return EmptyResult()

    # Access Grants Instance operations

    def create_access_grants_instance(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = xmltodict.parse(self.body) if self.body else {}
        identity_center_arn = None
        if "CreateAccessGrantsInstanceRequest" in params:
            identity_center_arn = params["CreateAccessGrantsInstanceRequest"].get(
                "IdentityCenterArn"
            )
        instance = self.backend.create_access_grants_instance(
            account_id=account_id,
            identity_center_arn=identity_center_arn,
        )
        result = {
            "AccessGrantsInstanceId": instance.instance_id,
            "AccessGrantsInstanceArn": instance.instance_arn,
            "CreatedAt": instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        if instance.identity_center_arn:
            result["IdentityCenterArn"] = instance.identity_center_arn
        return ActionResult(result)

    def get_access_grants_instance(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        instance = self.backend.get_access_grants_instance(account_id=account_id)
        result = {
            "AccessGrantsInstanceId": instance.instance_id,
            "AccessGrantsInstanceArn": instance.instance_arn,
            "CreatedAt": instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        if instance.identity_center_arn:
            result["IdentityCenterArn"] = instance.identity_center_arn
        return ActionResult(result)

    def get_access_grants_instance_for_prefix(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        s3_prefix = self._get_params().get("s3prefix", "")
        instance = self.backend.get_access_grants_instance_for_prefix(
            account_id=account_id,
            s3_prefix=s3_prefix,
        )
        return ActionResult(
            {
                "AccessGrantsInstanceId": instance.instance_id,
                "AccessGrantsInstanceArn": instance.instance_arn,
            }
        )

    def get_access_grants_instance_resource_policy(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        policy = self.backend.get_access_grants_instance_resource_policy(
            account_id=account_id,
        )
        return ActionResult({"Policy": policy})

    def list_access_grants_instances(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = self._get_params()
        max_results = params.get("maxResults")
        if max_results:
            max_results = int(max_results)
        instances, next_token = self.backend.list_access_grants_instances(
            account_id=account_id,
            max_results=max_results,
            next_token=params.get("nextToken"),
        )
        result: dict[str, Any] = {
            "AccessGrantsInstancesList": [
                {
                    "AccessGrantsInstanceId": instance.instance_id,
                    "AccessGrantsInstanceArn": instance.instance_arn,
                    "CreatedAt": instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
                for instance in instances
            ]
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    # Access Grants Location operations

    def create_access_grants_location(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = xmltodict.parse(self.body)["CreateAccessGrantsLocationRequest"]
        location_scope = params.get("LocationScope", "")
        iam_role_arn = params.get("IAMRoleArn", "")
        location = self.backend.create_access_grants_location(
            account_id=account_id,
            location_scope=location_scope,
            iam_role_arn=iam_role_arn,
        )
        return ActionResult(
            {
                "AccessGrantsLocationId": location.location_id,
                "AccessGrantsLocationArn": location.location_arn,
                "LocationScope": location.location_scope,
                "IAMRoleArn": location.iam_role_arn,
                "CreatedAt": location.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        )

    def get_access_grants_location(self) -> ActionResult:
        location_id = self.path.split("/")[-1]
        location = self.backend.get_access_grants_location(location_id=location_id)
        return ActionResult(
            {
                "AccessGrantsLocationId": location.location_id,
                "AccessGrantsLocationArn": location.location_arn,
                "LocationScope": location.location_scope,
                "IAMRoleArn": location.iam_role_arn,
                "CreatedAt": location.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        )

    def list_access_grants_locations(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = self._get_params()
        max_results = params.get("maxResults")
        if max_results:
            max_results = int(max_results)
        locations, next_token = self.backend.list_access_grants_locations(
            account_id=account_id,
            max_results=max_results,
            next_token=params.get("nextToken"),
        )
        result: dict[str, Any] = {
            "AccessGrantsLocationsList": [
                {
                    "AccessGrantsLocationId": location.location_id,
                    "AccessGrantsLocationArn": location.location_arn,
                    "LocationScope": location.location_scope,
                    "IAMRoleArn": location.iam_role_arn,
                    "CreatedAt": location.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
                for location in locations
            ]
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    # Access Grant operations

    def create_access_grant(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = xmltodict.parse(self.body)["CreateAccessGrantRequest"]
        location_id = params.get("AccessGrantsLocationId", "")
        grantee = params.get("Grantee", {})
        permission = params.get("Permission", "")
        location_scope = params.get("AccessGrantsLocationConfiguration", {}).get(
            "S3SubPrefix", ""
        )
        application_arn = params.get("ApplicationArn")
        grant = self.backend.create_access_grant(
            account_id=account_id,
            location_id=location_id,
            grantee=grantee,
            permission=permission,
            location_scope=location_scope,
            application_arn=application_arn,
        )
        result = {
            "AccessGrantId": grant.grant_id,
            "AccessGrantArn": grant.grant_arn,
            "AccessGrantsLocationId": grant.location_id,
            "Permission": grant.permission,
            "CreatedAt": grant.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "Grantee": {},
        }
        if grant.grantee.get("GranteeType"):
            result["Grantee"]["GranteeType"] = grant.grantee["GranteeType"]
        if grant.grantee.get("GranteeIdentifier"):
            result["Grantee"]["GranteeIdentifier"] = grant.grantee["GranteeIdentifier"]
        return ActionResult(result)

    def get_access_grant(self) -> ActionResult:
        grant_id = self.path.split("/")[-1]
        grant = self.backend.get_access_grant(grant_id=grant_id)
        result = {
            "AccessGrantId": grant.grant_id,
            "AccessGrantArn": grant.grant_arn,
            "AccessGrantsLocationId": grant.location_id,
            "Permission": grant.permission,
            "CreatedAt": grant.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "Grantee": {},
            "AccessGrantsLocationConfiguration": {
                "S3SubPrefix": grant.location_scope,
            },
        }
        if grant.grantee.get("GranteeType"):
            result["Grantee"]["GranteeType"] = grant.grantee["GranteeType"]
        if grant.grantee.get("GranteeIdentifier"):
            result["Grantee"]["GranteeIdentifier"] = grant.grantee["GranteeIdentifier"]
        return ActionResult(result)

    def list_access_grants(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = self._get_params()
        max_results = params.get("maxResults")
        if max_results:
            max_results = int(max_results)
        grants, next_token = self.backend.list_access_grants(
            account_id=account_id,
            max_results=max_results,
            next_token=params.get("nextToken"),
        )
        result: dict[str, Any] = {
            "AccessGrantsList": [
                {
                    "AccessGrantId": grant.grant_id,
                    "AccessGrantArn": grant.grant_arn,
                    "AccessGrantsLocationId": grant.location_id,
                    "Permission": grant.permission,
                    "CreatedAt": grant.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
                for grant in grants
            ]
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    # S3 Batch Operations (Jobs)

    def describe_job(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        job_id = self.path.split("/")[-1]
        job = self.backend.describe_job(account_id=account_id, job_id=job_id)
        return ActionResult(
            {
                "Job": {
                    "JobId": job.job_id,
                    "Status": job.status,
                    "Description": job.description,
                    "Priority": job.priority,
                    "RoleArn": job.role_arn,
                    "CreationTime": job.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "ProgressSummary": {
                        "NumberOfTasksSucceeded": job.progress[
                            "NumberOfTasksSucceeded"
                        ],
                        "NumberOfTasksFailed": job.progress["NumberOfTasksFailed"],
                        "TotalNumberOfTasks": job.progress["TotalNumberOfTasks"],
                    },
                }
            }
        )

    def list_jobs(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = self._get_params()
        max_results = params.get("maxResults")
        if max_results:
            max_results = int(max_results)
        jobs, next_token = self.backend.list_jobs(
            account_id=account_id,
            max_results=max_results,
            next_token=params.get("nextToken"),
        )
        result: dict[str, Any] = {
            "Jobs": [
                {
                    "JobId": job.job_id,
                    "Status": job.status,
                    "Description": job.description,
                    "Priority": job.priority,
                    "CreationTime": job.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
                for job in jobs
            ]
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    def create_job(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = xmltodict.parse(self.body)["CreateJobRequest"]
        operation = params.get("Operation", {})
        manifest = params.get("Manifest", {})
        priority = int(params.get("Priority", 0))
        role_arn = params.get("RoleArn", "")
        description = params.get("Description", "")
        confirmation = params.get("ConfirmationRequired", "false")
        confirmation_required = confirmation in ("true", "True", True)
        job = self.backend.create_job(
            account_id=account_id,
            operation=operation,
            manifest=manifest,
            priority=priority,
            role_arn=role_arn,
            description=description,
            confirmation_required=confirmation_required,
        )
        return ActionResult({"JobId": job.job_id})

    def update_job_priority(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        job_id = self.path.split("/")[-2]
        params = self._get_params()
        priority = int(params.get("priority", 0))
        job = self.backend.update_job_priority(
            account_id=account_id, job_id=job_id, priority=priority
        )
        return ActionResult(
            {
                "JobId": job.job_id,
                "Priority": job.priority,
            }
        )

    def update_job_status(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        job_id = self.path.split("/")[-2]
        params = self._get_params()
        requested_job_status = params.get("requestedJobStatus", "")
        status_update_reason = params.get("statusUpdateReason", "")
        job = self.backend.update_job_status(
            account_id=account_id,
            job_id=job_id,
            requested_job_status=requested_job_status,
            status_update_reason=status_update_reason,
        )
        return ActionResult(
            {
                "JobId": job.job_id,
                "Status": job.status,
            }
        )

    def delete_storage_lens_configuration_tagging(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        config_id = self.path.split("/")[-2]
        self.backend.delete_storage_lens_configuration_tagging(
            config_id=config_id, account_id=account_id
        )
        return 200, {}, ""

    def delete_access_grants_instance(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        self.backend.delete_access_grants_instance(account_id=account_id)
        return 200, {}, ""

    def put_access_grants_instance_resource_policy(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = xmltodict.parse(self.body) if self.body else {}
        policy = ""
        if "PutAccessGrantsInstanceResourcePolicyRequest" in params:
            policy = params["PutAccessGrantsInstanceResourcePolicyRequest"].get(
                "Policy", ""
            )
        result = self.backend.put_access_grants_instance_resource_policy(
            account_id=account_id, policy=policy
        )
        return ActionResult({"Policy": result})

    def delete_access_grants_instance_resource_policy(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        self.backend.delete_access_grants_instance_resource_policy(
            account_id=account_id
        )
        return 200, {}, ""

    def delete_access_grants_location(self) -> TYPE_RESPONSE:
        location_id = self.path.split("/")[-1]
        self.backend.delete_access_grants_location(location_id=location_id)
        return 200, {}, ""

    def update_access_grants_location(self) -> ActionResult:
        location_id = self.path.split("/")[-1]
        params = xmltodict.parse(self.body) if self.body else {}
        req = params.get("UpdateAccessGrantsLocationRequest", {})
        iam_role_arn = req.get("IAMRoleArn", "")
        location_scope = req.get("LocationScope")
        location = self.backend.update_access_grants_location(
            location_id=location_id,
            iam_role_arn=iam_role_arn,
            location_scope=location_scope,
        )
        return ActionResult(
            {
                "AccessGrantsLocationId": location.location_id,
                "AccessGrantsLocationArn": location.location_arn,
                "LocationScope": location.location_scope,
                "IAMRoleArn": location.iam_role_arn,
                "CreatedAt": location.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        )

    def delete_access_grant(self) -> TYPE_RESPONSE:
        grant_id = self.path.split("/")[-1]
        self.backend.delete_access_grant(grant_id=grant_id)
        return 200, {}, ""

    def get_multi_region_access_point_routes(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        mrap_name = self.path.split("/instances/")[1].split("/routes")[0]
        routes = self.backend.get_multi_region_access_point_routes(
            account_id=account_id, mrap=mrap_name
        )
        return ActionResult(
            {
                "Mrap": mrap_name,
                "Routes": [
                    {
                        "Bucket": route.get("Bucket"),
                        "Region": route.get("Region"),
                        "TrafficDialPercentage": route.get("TrafficDialPercentage"),
                    }
                    for route in routes
                ],
            }
        )

    def submit_multi_region_access_point_routes(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        mrap_name = self.path.split("/instances/")[1].split("/routes")[0]
        params = xmltodict.parse(self.body) if self.body else {}
        req = params.get("SubmitMultiRegionAccessPointRoutesRequest", {})
        route_updates = req.get("RouteUpdates", {}).get("Route", [])
        if isinstance(route_updates, dict):
            route_updates = [route_updates]
        self.backend.submit_multi_region_access_point_routes(
            account_id=account_id, mrap=mrap_name, route_updates=route_updates
        )
        return 200, {}, ""

    def get_access_point_policy_for_object_lambda(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-2]
        try:
            policy = self.backend.get_access_point_policy(account_id, name)
        except Exception:
            policy = ""
        return ActionResult({"Policy": policy})

    def get_access_point_policy_status_for_object_lambda(self) -> ActionResult:
        return ActionResult({"PolicyStatus": {"IsPublic": True}})

    # Bucket-level operations

    # Storage Lens Group operations

    def create_storage_lens_group(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = xmltodict.parse(self.body)["CreateStorageLensGroupRequest"]
        storage_lens_group = params.get("StorageLensGroup", {})
        name = storage_lens_group.get("Name", "")
        tags_raw = params.get("Tags", {}).get("Tag", [])
        if isinstance(tags_raw, dict):
            tags_raw = [tags_raw]
        group = self.backend.create_storage_lens_group(
            account_id=account_id,
            name=name,
            storage_lens_group=storage_lens_group,
            tags=tags_raw,
        )
        return ActionResult(
            {
                "StorageLensGroup": {
                    "Name": group.name,
                    "StorageLensGroupArn": group.arn,
                }
            }
        )

    def get_storage_lens_group(self) -> ActionResult:
        name = self.path.split("/")[-1]
        group = self.backend.get_storage_lens_group(name=name)
        return ActionResult(
            {
                "StorageLensGroup": {
                    "Name": group.name,
                    "StorageLensGroupArn": group.arn,
                }
            }
        )

    def delete_storage_lens_group(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-1]
        self.backend.delete_storage_lens_group(name=name)
        return 204, {"status": 204}, ""

    def update_storage_lens_group(self) -> TYPE_RESPONSE:
        name = self.path.split("/")[-1]
        params = xmltodict.parse(self.body)["UpdateStorageLensGroupRequest"]
        storage_lens_group = params.get("StorageLensGroup", {})
        self.backend.update_storage_lens_group(
            name=name,
            storage_lens_group=storage_lens_group,
        )
        return 200, {}, ""

    def list_storage_lens_groups(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = self._get_params()
        next_token = params.get("nextToken")
        groups, next_token = self.backend.list_storage_lens_groups(
            account_id=account_id,
            next_token=next_token,
        )
        result: dict[str, Any] = {
            "StorageLensGroupList": [
                {
                    "Name": group.name,
                    "StorageLensGroupArn": group.arn,
                }
                for group in groups
            ]
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    # Object Lambda Access Point operations

    def create_access_point_for_object_lambda(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-1]
        params = xmltodict.parse(self.body)["CreateAccessPointForObjectLambdaRequest"]
        configuration = params.get("Configuration", {})
        access_point = self.backend.create_access_point_for_object_lambda(
            account_id=account_id,
            name=name,
            configuration=configuration,
        )
        return ActionResult(
            {
                "ObjectLambdaAccessPointArn": access_point.arn,
                "Alias": {
                    "Status": "READY",
                    "Value": access_point.alias,
                },
            }
        )

    def get_access_point_for_object_lambda(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-1]
        access_point = self.backend.get_access_point_for_object_lambda(
            account_id=account_id, name=name
        )
        return ActionResult(
            {
                "Name": access_point.name,
                "ObjectLambdaAccessPointArn": access_point.arn,
                "CreationDate": access_point.created,
                "Alias": {
                    "Status": "READY",
                    "Value": access_point.alias,
                },
            }
        )

    def delete_access_point_for_object_lambda(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-1]
        self.backend.delete_access_point_for_object_lambda(
            account_id=account_id, name=name
        )
        return 204, {"status": 204}, ""

    def put_access_point_policy_for_object_lambda(self) -> EmptyResult:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-2]
        params = xmltodict.parse(self.body)[
            "PutAccessPointPolicyForObjectLambdaRequest"
        ]
        policy = params.get("Policy", "")
        self.backend.put_access_point_policy_for_object_lambda(
            account_id=account_id, name=name, policy=policy
        )
        return EmptyResult()

    def delete_access_point_policy_for_object_lambda(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-2]
        self.backend.delete_access_point_policy_for_object_lambda(
            account_id=account_id, name=name
        )
        return 204, {"status": 204}, ""

    # Access Point Scope operations

    def get_access_point_scope(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-2]
        scope = self.backend.get_access_point_scope(account_id=account_id, name=name)
        result: dict[str, Any] = {}
        if scope:
            result["Scope"] = scope
        return ActionResult(result)

    def put_access_point_scope(self) -> EmptyResult:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-2]
        params = xmltodict.parse(self.body)["PutAccessPointScopeRequest"]
        scope = params.get("Scope", {})
        self.backend.put_access_point_scope(
            account_id=account_id, name=name, scope=scope
        )
        return EmptyResult()

    def delete_access_point_scope(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        name = self.path.split("/")[-2]
        self.backend.delete_access_point_scope(account_id=account_id, name=name)
        return 204, {"status": 204}, ""

    # Job Tagging operations

    def get_job_tagging(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        job_id = self.path.split("/")[-2]
        tags = self.backend.get_job_tagging(account_id=account_id, job_id=job_id)
        return ActionResult(
            {
                "Tags": [
                    {
                        "Key": tag.get("Key"),
                        "Value": tag.get("Value"),
                    }
                    for tag in tags
                ]
            }
        )

    def put_job_tagging(self) -> EmptyResult:
        account_id = self.headers.get("x-amz-account-id")
        job_id = self.path.split("/")[-2]
        params = xmltodict.parse(self.body, force_list={"Tag": True, "member": True})
        tags_container = params.get("PutJobTaggingRequest", {}).get("Tags", {}) or {}
        # boto3 serializes list items as <member>, AWS SDKs may use <Tag>
        tags = tags_container.get("Tag", []) or tags_container.get("member", [])
        self.backend.put_job_tagging(account_id=account_id, job_id=job_id, tags=tags)
        return EmptyResult()

    def delete_job_tagging(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        job_id = self.path.split("/")[-2]
        self.backend.delete_job_tagging(account_id=account_id, job_id=job_id)
        return 200, {}, ""

    # CreateBucket / GetBucket / DeleteBucket (S3 on Outposts)

    def create_bucket(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        outpost_id = self.headers.get("x-amz-outpost-id")
        bucket = self.path.split("/")[-1]
        ob = self.backend.create_bucket(
            account_id=account_id,
            bucket=bucket,
            outpost_id=outpost_id,
        )
        location = f"/v20180820/bucket/{bucket}"
        return (
            200,
            {"Location": location},
            CREATE_BUCKET_TEMPLATE % {"bucket_arn": ob.arn},
        )

    def get_bucket(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-1]
        ob = self.backend.get_bucket(account_id=account_id, bucket=bucket)
        return ActionResult(
            {
                "Bucket": ob.bucket,
                "PublicAccessBlockEnabled": True,
                "CreationDate": ob.creation_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )

    def delete_bucket(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-1]
        self.backend.delete_bucket(account_id=account_id, bucket=bucket)
        return 204, {"status": 204}, ""

    # Put/Delete bucket-level operations

    def put_bucket_versioning(self) -> EmptyResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        params = xmltodict.parse(self.body)
        # Payload is VersioningConfiguration (may have namespace prefix)
        root_key = next(
            (k for k in params if "VersioningConfiguration" in k),
            "VersioningConfiguration",
        )
        versioning_config = params.get(root_key, {})
        status = versioning_config.get("Status", "")
        self.backend.put_bucket_versioning(
            account_id=account_id, bucket=bucket, status=status
        )
        return EmptyResult()

    def put_bucket_policy(self) -> EmptyResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        params = xmltodict.parse(self.body)["PutBucketPolicyRequest"]
        policy = params.get("Policy", "")
        self.backend.put_bucket_policy(
            account_id=account_id, bucket=bucket, policy=policy
        )
        return EmptyResult()

    def delete_bucket_policy(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        self.backend.delete_bucket_policy(account_id=account_id, bucket=bucket)
        return 204, {"status": 204}, ""

    def put_bucket_tagging(self) -> EmptyResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        params = xmltodict.parse(self.body, force_list={"member": True})
        members = params.get("Tagging", {}).get("TagSet", {}).get("member", [])
        tags = {m["Key"]: m["Value"] for m in members if isinstance(m, dict)}
        self.backend.put_bucket_tagging(
            account_id=account_id, bucket=bucket, tagging=tags
        )
        return EmptyResult()

    def delete_bucket_tagging(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        self.backend.delete_bucket_tagging(account_id=account_id, bucket=bucket)
        return 204, {"status": 204}, ""

    def put_bucket_lifecycle_configuration(self) -> EmptyResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        params = xmltodict.parse(self.body, force_list={"Rule": True})
        rules = (
            params.get("LifecycleConfiguration", {}).get("Rules", {}).get("Rule", [])
        )
        self.backend.put_bucket_lifecycle(
            account_id=account_id, bucket=bucket, rules=rules
        )
        return EmptyResult()

    def delete_bucket_lifecycle_configuration(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        self.backend.delete_bucket_lifecycle(account_id=account_id, bucket=bucket)
        return 204, {"status": 204}, ""

    def put_bucket_replication(self) -> EmptyResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        params = xmltodict.parse(self.body, force_list={"Rule": True})
        replication = params.get("ReplicationConfiguration", {})
        self.backend.put_bucket_replication(
            account_id=account_id, bucket=bucket, replication=replication
        )
        return EmptyResult()

    def delete_bucket_replication(self) -> TYPE_RESPONSE:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        self.backend.delete_bucket_replication(account_id=account_id, bucket=bucket)
        return 204, {"status": 204}, ""

    def get_bucket_lifecycle_configuration(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        rules = self.backend.get_bucket_lifecycle_configuration(
            account_id=account_id, bucket=bucket
        )
        result_rules = []
        for rule in rules or []:
            rule_dict: dict[str, Any] = {}
            if rule.id:
                rule_dict["ID"] = rule.id
            rule_dict["Status"] = rule.status
            if rule.prefix is not None:
                rule_dict["Prefix"] = rule.prefix
            elif rule.filter:
                filter_dict: dict[str, Any] = {}
                if rule.filter.prefix is not None:
                    filter_dict["Prefix"] = rule.filter.prefix
                rule_dict["Filter"] = filter_dict
            else:
                rule_dict["Filter"] = {}
            result_rules.append(rule_dict)
        return ActionResult({"Rules": result_rules})

    def get_bucket_policy(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        policy = self.backend.get_bucket_policy(account_id=account_id, bucket=bucket)
        return ActionResult({"Policy": policy or ""})

    def get_bucket_replication(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        replication = self.backend.get_bucket_replication(
            account_id=account_id, bucket=bucket
        )
        result: dict[str, Any] = {}
        if replication:
            replication_config: dict[str, Any] = {}
            if replication.get("Role"):
                replication_config["Role"] = replication["Role"]
            if replication.get("Rules"):
                rules = []
                for rule in replication["Rules"].get("Rule", []):
                    rule_dict: dict[str, Any] = {}
                    if rule.get("ID"):
                        rule_dict["ID"] = rule["ID"]
                    if rule.get("Status"):
                        rule_dict["Status"] = rule["Status"]
                    if rule.get("Priority"):
                        rule_dict["Priority"] = rule["Priority"]
                    if rule.get("Bucket"):
                        rule_dict["Bucket"] = rule["Bucket"]
                    if rule.get("Destination"):
                        dest: dict[str, Any] = {}
                        if rule["Destination"].get("Bucket"):
                            dest["Bucket"] = rule["Destination"]["Bucket"]
                        if rule["Destination"].get("Account"):
                            dest["Account"] = rule["Destination"]["Account"]
                        rule_dict["Destination"] = dest
                    if rule.get("DeleteMarkerReplication"):
                        rule_dict["DeleteMarkerReplication"] = {
                            "Status": rule["DeleteMarkerReplication"].get("Status")
                        }
                    rules.append(rule_dict)
                replication_config["Rules"] = rules
            result["ReplicationConfiguration"] = replication_config
        return ActionResult(result)

    def get_bucket_tagging(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        tag_dict = self.backend.get_bucket_tagging(account_id=account_id, bucket=bucket)
        tag_list = tag_dict.get("Tags", []) if isinstance(tag_dict, dict) else []
        return ActionResult(
            {
                "TagSet": [
                    {
                        "Key": tag.get("Key"),
                        "Value": tag.get("Value"),
                    }
                    for tag in tag_list
                ]
            }
        )

    def get_bucket_versioning(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        bucket = self.path.split("/")[-2]
        status = self.backend.get_bucket_versioning(
            account_id=account_id, bucket=bucket
        )
        return ActionResult({"Status": status or ""})

    def list_access_points_for_object_lambda(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = self._get_params()
        max_results = params.get("maxResults")
        if max_results:
            max_results = int(max_results)
        access_points, next_token = self.backend.list_access_points_for_object_lambda(
            account_id=account_id,
            max_results=max_results,
            next_token=params.get("nextToken"),
        )
        result: dict[str, Any] = {
            "ObjectLambdaAccessPointList": [
                {
                    "Name": ap.get("Name"),
                    "ObjectLambdaAccessPointArn": ap.get("ObjectLambdaAccessPointArn"),
                }
                for ap in access_points
            ]
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    def list_regional_buckets(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = self._get_params()
        max_results = params.get("maxResults")
        if max_results:
            max_results = int(max_results)
        buckets, next_token = self.backend.list_regional_buckets(
            account_id=account_id,
            outpost_id=params.get("outpostId") or self.headers.get("x-amz-outpost-id"),
            max_results=max_results,
            next_token=params.get("nextToken"),
        )
        result: dict[str, Any] = {
            "RegionalBucketList": [
                {
                    "Bucket": bucket.get("Bucket"),
                }
                for bucket in buckets
            ]
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    def list_caller_access_grants(self) -> ActionResult:
        account_id = self.headers.get("x-amz-account-id")
        params = self._get_params()
        max_results = params.get("maxResults")
        if max_results:
            max_results = int(max_results)
        grants, next_token = self.backend.list_caller_access_grants(
            account_id=account_id,
            grant_scope=params.get("grantScope"),
            max_results=max_results,
            next_token=params.get("nextToken"),
            allowed_by_application=params.get("allowedByApplication") == "true",
        )
        result: dict[str, Any] = {
            "CallerAccessGrantsList": [
                {
                    "Permission": grant.get("Permission"),
                    "GrantScope": grant.get("GrantScope"),
                }
                for grant in grants
            ]
        }
        if next_token:
            result["NextToken"] = next_token
        return ActionResult(result)

    def associate_access_grants_identity_center(self) -> EmptyResult:
        """Stub: AssociateAccessGrantsIdentityCenter."""
        return EmptyResult()

    def dissociate_access_grants_identity_center(self) -> EmptyResult:
        """Stub: DissociateAccessGrantsIdentityCenter."""
        return EmptyResult()

    def get_data_access(self) -> ActionResult:
        """Stub: GetDataAccess."""
        return ActionResult({})

    def list_access_points_for_directory_buckets(self) -> ActionResult:
        """Stub: ListAccessPointsForDirectoryBuckets."""
        return ActionResult({"AccessPointList": []})

    def get_access_point_configuration_for_object_lambda(self) -> ActionResult:
        """Stub: GetAccessPointConfigurationForObjectLambda."""
        return ActionResult({})

    def put_access_point_configuration_for_object_lambda(self) -> EmptyResult:
        """Stub: PutAccessPointConfigurationForObjectLambda."""
        return EmptyResult()


CREATE_ACCESS_POINT_TEMPLATE = """<CreateAccessPointResult>
  <ResponseMetadata>
    <RequestId>1549581b-12b7-11e3-895e-1334aEXAMPLE</RequestId>
  </ResponseMetadata>
  <Alias>{{ access_point.alias }}</Alias>
  <AccessPointArn>{{ access_point.arn }}</AccessPointArn>
</CreateAccessPointResult>
"""


GET_ACCESS_POINT_TEMPLATE = """<GetAccessPointResult>
  <ResponseMetadata>
    <RequestId>1549581b-12b7-11e3-895e-1334aEXAMPLE</RequestId>
  </ResponseMetadata>
  <Name>{{ access_point.name }}</Name>
  <Bucket>{{ access_point.bucket }}</Bucket>
  <NetworkOrigin>{{ access_point.network_origin }}</NetworkOrigin>
  {% if access_point.vpc_id %}
  <VpcConfiguration>
      <VpcId>{{ access_point.vpc_id }}</VpcId>
  </VpcConfiguration>
  {% endif %}
  <PublicAccessBlockConfiguration>
      <BlockPublicAcls>{{ access_point.pubc["BlockPublicAcls"] }}</BlockPublicAcls>
      <IgnorePublicAcls>{{ access_point.pubc["IgnorePublicAcls"] }}</IgnorePublicAcls>
      <BlockPublicPolicy>{{ access_point.pubc["BlockPublicPolicy"] }}</BlockPublicPolicy>
      <RestrictPublicBuckets>{{ access_point.pubc["RestrictPublicBuckets"] }}</RestrictPublicBuckets>
  </PublicAccessBlockConfiguration>
  <CreationDate>{{ access_point.created }}</CreationDate>
  <Alias>{{ access_point.alias }}</Alias>
  <AccessPointArn>{{ access_point.arn }}</AccessPointArn>
  <Endpoints>
      <entry>
          <key>ipv4</key>
          <value>s3-accesspoint.us-east-1.amazonaws.com</value>
      </entry>
      <entry>
          <key>fips</key>
          <value>s3-accesspoint-fips.us-east-1.amazonaws.com</value>
      </entry>
      <entry>
          <key>fips_dualstack</key>
          <value>s3-accesspoint-fips.dualstack.us-east-1.amazonaws.com</value>
      </entry>
      <entry>
          <key>dualstack</key>
          <value>s3-accesspoint.dualstack.us-east-1.amazonaws.com</value>
      </entry>
  </Endpoints>
</GetAccessPointResult>
"""


GET_ACCESS_POINT_POLICY_TEMPLATE = """<GetAccessPointPolicyResult>
  <ResponseMetadata>
    <RequestId>1549581b-12b7-11e3-895e-1334aEXAMPLE</RequestId>
  </ResponseMetadata>
  <Policy>{{ policy }}</Policy>
</GetAccessPointPolicyResult>
"""


GET_ACCESS_POINT_POLICY_STATUS_TEMPLATE = """<GetAccessPointPolicyResult>
  <ResponseMetadata>
    <RequestId>1549581b-12b7-11e3-895e-1334aEXAMPLE</RequestId>
  </ResponseMetadata>
  <PolicyStatus>
      <IsPublic>true</IsPublic>
  </PolicyStatus>
</GetAccessPointPolicyResult>
"""

XMLNS = 'xmlns="http://awss3control.amazonaws.com/doc/2018-08-20/"'

CREATE_MULTI_REGION_ACCESS_POINT_TEMPLATE = f"""<CreateMultiRegionAccessPointResult {XMLNS}>
  <RequestTokenARN>{{{{ request_token }}}}</RequestTokenARN>
</CreateMultiRegionAccessPointResult>
"""

DELETE_MULTI_REGION_ACCESS_POINT_TEMPLATE = f"""<DeleteMultiRegionAccessPointResult {XMLNS}>
  <RequestTokenARN>{{{{ request_token }}}}</RequestTokenARN>
</DeleteMultiRegionAccessPointResult>
"""

DESCRIBE_MULTI_REGION_ACCESS_POINT_OPERATION_TEMPLATE = f"""<DescribeMultiRegionAccessPointOperationResult {XMLNS}>
  <AsyncOperation>
    <CreationTime>{{{{ operation.CreationTime }}}}</CreationTime>
    <Operation>{{{{ operation.Operation }}}}</Operation>
    <RequestTokenARN>{{{{ operation.RequestTokenARN }}}}</RequestTokenARN>
    <RequestStatus>{{{{ operation.RequestStatus }}}}</RequestStatus>
    {{% if operation.RequestParameters %}}
    <RequestParameters>
      {{% if operation.RequestParameters.CreateMultiRegionAccessPointRequest %}}
      <CreateMultiRegionAccessPointRequest>
        <Name>{{{{ operation.RequestParameters.CreateMultiRegionAccessPointRequest.Name }}}}</Name>
        {{% if operation.RequestParameters.CreateMultiRegionAccessPointRequest.PublicAccessBlock %}}
        <PublicAccessBlock>
          <BlockPublicAcls>{{{{ operation.RequestParameters.CreateMultiRegionAccessPointRequest.PublicAccessBlock.BlockPublicAcls|default("true") }}}}</BlockPublicAcls>
          <IgnorePublicAcls>{{{{ operation.RequestParameters.CreateMultiRegionAccessPointRequest.PublicAccessBlock.IgnorePublicAcls|default("true") }}}}</IgnorePublicAcls>
          <BlockPublicPolicy>{{{{ operation.RequestParameters.CreateMultiRegionAccessPointRequest.PublicAccessBlock.BlockPublicPolicy|default("true") }}}}</BlockPublicPolicy>
          <RestrictPublicBuckets>{{{{ operation.RequestParameters.CreateMultiRegionAccessPointRequest.PublicAccessBlock.RestrictPublicBuckets|default("true") }}}}</RestrictPublicBuckets>
        </PublicAccessBlock>
        {{% endif %}}
        {{% if operation.RequestParameters.CreateMultiRegionAccessPointRequest.Regions %}}
        <Regions>
          {{% for region in operation.RequestParameters.CreateMultiRegionAccessPointRequest.Regions %}}
          <Region>
            <Bucket>{{{{ region.Bucket }}}}</Bucket>
          </Region>
          {{% endfor %}}
        </Regions>
        {{% endif %}}
      </CreateMultiRegionAccessPointRequest>
      {{% endif %}}
      {{% if operation.RequestParameters.DeleteMultiRegionAccessPointRequest %}}
      <DeleteMultiRegionAccessPointRequest>
        <Name>{{{{ operation.RequestParameters.DeleteMultiRegionAccessPointRequest.Name }}}}</Name>
      </DeleteMultiRegionAccessPointRequest>
      {{% endif %}}
      {{% if operation.RequestParameters.PutMultiRegionAccessPointPolicyRequest %}}
      <PutMultiRegionAccessPointPolicyRequest>
        <Name>{{{{ operation.RequestParameters.PutMultiRegionAccessPointPolicyRequest.Name }}}}</Name>
        <Policy>{{{{ operation.RequestParameters.PutMultiRegionAccessPointPolicyRequest.Policy }}}}</Policy>
      </PutMultiRegionAccessPointPolicyRequest>
      {{% endif %}}
    </RequestParameters>
    {{% endif %}}
    {{% if operation.ResponseDetails %}}
    <ResponseDetails>
      {{% if operation.ResponseDetails.MultiRegionAccessPointDetails %}}
      <MultiRegionAccessPointDetails>
        {{% if operation.ResponseDetails.MultiRegionAccessPointDetails.Regions %}}
        <Regions>
          {{% for region in operation.ResponseDetails.MultiRegionAccessPointDetails.Regions %}}
          <Region>
            <Name>{{{{ region.Name }}}}</Name>
            <RequestStatus>{{{{ region.RequestStatus }}}}</RequestStatus>
          </Region>
          {{% endfor %}}
        </Regions>
        {{% endif %}}
      </MultiRegionAccessPointDetails>
      {{% endif %}}
    </ResponseDetails>
    {{% endif %}}
  </AsyncOperation>
</DescribeMultiRegionAccessPointOperationResult>
"""

GET_MULTI_REGION_ACCESS_POINT_TEMPLATE = f"""<GetMultiRegionAccessPointResult {XMLNS}>
  <AccessPoint>
    <Name>{{{{ mrap.Name }}}}</Name>
    <Alias>{{{{ mrap.Alias }}}}</Alias>
    <CreatedAt>{{{{ mrap.CreatedAt }}}}</CreatedAt>
    <PublicAccessBlock>
      <BlockPublicAcls>{{{{ mrap.PublicAccessBlock.BlockPublicAcls|default("true") }}}}</BlockPublicAcls>
      <IgnorePublicAcls>{{{{ mrap.PublicAccessBlock.IgnorePublicAcls|default("true") }}}}</IgnorePublicAcls>
      <BlockPublicPolicy>{{{{ mrap.PublicAccessBlock.BlockPublicPolicy|default("true") }}}}</BlockPublicPolicy>
      <RestrictPublicBuckets>{{{{ mrap.PublicAccessBlock.RestrictPublicBuckets|default("true") }}}}</RestrictPublicBuckets>
    </PublicAccessBlock>
    <Status>{{{{ mrap.Status }}}}</Status>
    <Regions>
      {{% for region in mrap.Regions %}}
      <Region>
        <Bucket>{{{{ region.Bucket }}}}</Bucket>
        <Region>{{{{ region.Region }}}}</Region>
      </Region>
      {{% endfor %}}
    </Regions>
  </AccessPoint>
</GetMultiRegionAccessPointResult>
"""

GET_MULTI_REGION_ACCESS_POINT_POLICY_TEMPLATE = f"""<GetMultiRegionAccessPointPolicyResult {XMLNS}>
  <Policy>
    <Established>
      <Policy>{{{{ policy }}}}</Policy>
    </Established>
  </Policy>
</GetMultiRegionAccessPointPolicyResult>
"""

GET_MULTI_REGION_ACCESS_POINT_POLICY_STATUS_TEMPLATE = f"""<GetMultiRegionAccessPointPolicyStatusResult {XMLNS}>
  <Established>
    <IsPublic>{{{{ is_public|lower }}}}</IsPublic>
  </Established>
</GetMultiRegionAccessPointPolicyStatusResult>
"""

LIST_MULTI_REGION_ACCESS_POINTS_TEMPLATE = f"""<ListMultiRegionAccessPointsResult {XMLNS}>
  <AccessPoints>
    {{% for mrap in mraps %}}
    <AccessPoint>
      <Name>{{{{ mrap.Name }}}}</Name>
      <Alias>{{{{ mrap.Alias }}}}</Alias>
      <CreatedAt>{{{{ mrap.CreatedAt }}}}</CreatedAt>
      <PublicAccessBlock>
        <BlockPublicAcls>{{{{ mrap.PublicAccessBlock.BlockPublicAcls|default("true") }}}}</BlockPublicAcls>
        <IgnorePublicAcls>{{{{ mrap.PublicAccessBlock.IgnorePublicAcls|default("true") }}}}</IgnorePublicAcls>
        <BlockPublicPolicy>{{{{ mrap.PublicAccessBlock.BlockPublicPolicy|default("true") }}}}</BlockPublicPolicy>
        <RestrictPublicBuckets>{{{{ mrap.PublicAccessBlock.RestrictPublicBuckets|default("true") }}}}</RestrictPublicBuckets>
      </PublicAccessBlock>
      <Status>{{{{ mrap.Status }}}}</Status>
      <Regions>
        {{% for region in mrap.Regions %}}
        <Region>
          <Bucket>{{{{ region.Bucket }}}}</Bucket>
          <Region>{{{{ region.Region }}}}</Region>
        </Region>
        {{% endfor %}}
      </Regions>
    </AccessPoint>
    {{% endfor %}}
  </AccessPoints>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListMultiRegionAccessPointsResult>
"""

PUT_MULTI_REGION_ACCESS_POINT_POLICY_TEMPLATE = f"""<PutMultiRegionAccessPointPolicyResult {XMLNS}>
  <RequestTokenARN>{{{{ request_token }}}}</RequestTokenARN>
</PutMultiRegionAccessPointPolicyResult>
"""

GET_STORAGE_LENS_CONFIGURATION_TEMPLATE = """
<StorageLensConfiguration>
   <Id>{{config.get("Id")}}</Id>
   {% if config.get("DataExport") %}
   <DataExport>
      {% if config["DataExport"]["S3BucketDestination"] %}
      <S3BucketDestination>
         <AccountId>{{config["DataExport"]["S3BucketDestination"]["AccountId"]}}</AccountId>
         <Arn>{{config["DataExport"]["S3BucketDestination"]["Arn"]}}</Arn>
         {% if config["DataExport"]["S3BucketDestination"].get("Encryption") %}
         <Encryption>
            {% if config["DataExport"]["S3BucketDestination"]["Encryption"].get("SSEKMS") %}
            <SSE-KMS>
               <KeyId>config["DataExport"]["S3BucketDestination"]["Encryption"]["KeyId"]</KeyId>
            </SSE-KMS>
            {% endif %}
            {% if "SSE-S3" in config["DataExport"]["S3BucketDestination"]["Encryption"] %}
            <SSE-S3>
            </SSE-S3>
            {% endif %}
         </Encryption>
         {% endif %}
      </S3BucketDestination>
      {% endif %}
   </DataExport>
   {% endif %}
   <IsEnabled>{{config["IsEnabled"]}}</IsEnabled>
   <AccountLevel>
        <ActivityMetrics>
            <IsEnabled>{{config["AccountLevel"]["ActivityMetrics"]["IsEnabled"]}}</IsEnabled>
        </ActivityMetrics>
        <BucketLevel>
            <ActivityMetrics>
                <IsEnabled>{{config["AccountLevel"]["BucketLevel"]["ActivityMetrics"]["IsEnabled"]}}</IsEnabled>
            </ActivityMetrics>
            <PrefixLevel>
                <StorageMetrics>
                    <IsEnabled>{{config["AccountLevel"]["BucketLevel"]["PrefixLevel"]["StorageMetrics"]["IsEnabled"]}}</IsEnabled>
                    <SelectionCriteria>
                        <Delimiter>{{config["AccountLevel"]["BucketLevel"]["PrefixLevel"]["StorageMetrics"]["SelectionCriteria"]["Delimiter"]}}</Delimiter>
                        <MaxDepth>{{config["AccountLevel"]["BucketLevel"]["PrefixLevel"]["StorageMetrics"]["SelectionCriteria"]["MaxDepth"]}}</MaxDepth>
                        <MinStorageBytesPercentage>{{config["AccountLevel"]["BucketLevel"]["PrefixLevel"]["StorageMetrics"]["SelectionCriteria"]["MinStorageBytesPercentage"]}}</MinStorageBytesPercentage>
                    </SelectionCriteria>
                </StorageMetrics>
            </PrefixLevel>
            <DetailedStatusCodesMetrics>
                <IsEnabled>{{config["AccountLevel"]["BucketLevel"]["DetailedStatusCodesMetrics"]["IsEnabled"]}}</IsEnabled>
            </DetailedStatusCodesMetrics>
        </BucketLevel>
        <AdvancedDataProtectionMetrics>
            <IsEnabled>{{config["AccountLevel"]["AdvancedDataProtectionMetrics"]["IsEnabled"]}}</IsEnabled>
        </AdvancedDataProtectionMetrics>
        <DetailedStatusCodesMetrics>
            <IsEnabled>{{config["AccountLevel"]["DetailedStatusCodesMetrics"]["IsEnabled"]}}</IsEnabled>
        </DetailedStatusCodesMetrics>
   </AccountLevel>
   <AwsOrg>
        <Arn>{{config.get("AwsOrg", {}).get("Arn", "")}}</Arn>
    </AwsOrg>
    <StorageLensArn>{{config.get("StorageLensArn")}}</StorageLensArn>
</StorageLensConfiguration>
"""


LIST_STORAGE_LENS_CONFIGURATIONS_TEMPLATE = """
<ListStorageLensConfigurationsResult>
   {% if next_token %}
   <NextToken>{{ next_token }}</NextToken>
   {% endif %}
   {% for config in configs %}
   <StorageLensConfiguration>
      <HomeRegion></HomeRegion>
      <Id>{{ config.config.get("Id") }}</Id>
      <IsEnabled>{{ config.config.get("IsEnabled") }}</IsEnabled>
      <StorageLensArn>{{ config.arn }}</StorageLensArn>
    </StorageLensConfiguration>
    {% endfor %}
</ListStorageLensConfigurationsResult>
"""


GET_STORAGE_LENS_CONFIGURATION_TAGGING_TEMPLATE = """
<GetStorageLensConfigurationTaggingResult>
   <Tags>
      {% for tag in tags["Tag"] %}
      <Tag>
         <Key>{{ tag["Key"] }}</Key>
         <Value>{{ tag["Value"] }}</Value>
      </Tag>
      {% endfor %}
   </Tags>
</GetStorageLensConfigurationTaggingResult>

"""
LIST_ACCESS_POINTS_TEMPLATE = """<ListAccessPointsResult>
  <AccessPointList>
    {% for access_point in access_points %}
    <AccessPoint>
      <Name>{{ access_point.name }}</Name>
      <NetworkOrigin>{{ access_point.network_origin }}</NetworkOrigin>
      {% if access_point.vpc_id %}
      <VpcConfiguration>
        <VpcId>{{ access_point.vpc_id }}</VpcId>
      </VpcConfiguration>
      {% endif %}
      <Bucket>{{ access_point.bucket }}</Bucket>
      <AccessPointArn>{{ access_point.arn }}</AccessPointArn>
      <Alias>{{ access_point.alias }}</Alias>
    </AccessPoint>
    {% endfor %}
  </AccessPointList>
  {% if next_token %}
  <NextToken>{{ next_token }}</NextToken>
  {% endif %}
</ListAccessPointsResult>"""

# Access Grants Instance templates

CREATE_ACCESS_GRANTS_INSTANCE_TEMPLATE = f"""<CreateAccessGrantsInstanceResult {XMLNS}>
  <AccessGrantsInstanceId>{{{{ instance.instance_id }}}}</AccessGrantsInstanceId>
  <AccessGrantsInstanceArn>{{{{ instance.instance_arn }}}}</AccessGrantsInstanceArn>
  <CreatedAt>{{{{ instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
  {{% if instance.identity_center_arn %}}
  <IdentityCenterArn>{{{{ instance.identity_center_arn }}}}</IdentityCenterArn>
  {{% endif %}}
</CreateAccessGrantsInstanceResult>
"""

GET_ACCESS_GRANTS_INSTANCE_TEMPLATE = f"""<GetAccessGrantsInstanceResult {XMLNS}>
  <AccessGrantsInstanceId>{{{{ instance.instance_id }}}}</AccessGrantsInstanceId>
  <AccessGrantsInstanceArn>{{{{ instance.instance_arn }}}}</AccessGrantsInstanceArn>
  <CreatedAt>{{{{ instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
  {{% if instance.identity_center_arn %}}
  <IdentityCenterArn>{{{{ instance.identity_center_arn }}}}</IdentityCenterArn>
  {{% endif %}}
</GetAccessGrantsInstanceResult>
"""

GET_ACCESS_GRANTS_INSTANCE_FOR_PREFIX_TEMPLATE = f"""<GetAccessGrantsInstanceForPrefixResult {XMLNS}>
  <AccessGrantsInstanceId>{{{{ instance.instance_id }}}}</AccessGrantsInstanceId>
  <AccessGrantsInstanceArn>{{{{ instance.instance_arn }}}}</AccessGrantsInstanceArn>
</GetAccessGrantsInstanceForPrefixResult>
"""

GET_ACCESS_GRANTS_INSTANCE_RESOURCE_POLICY_TEMPLATE = f"""<GetAccessGrantsInstanceResourcePolicyResult {XMLNS}>
  <Policy>{{{{ policy }}}}</Policy>
</GetAccessGrantsInstanceResourcePolicyResult>
"""

LIST_ACCESS_GRANTS_INSTANCES_TEMPLATE = f"""<ListAccessGrantsInstancesResult {XMLNS}>
  <AccessGrantsInstancesList>
    {{% for instance in instances %}}
    <AccessGrantsInstance>
      <AccessGrantsInstanceId>{{{{ instance.instance_id }}}}</AccessGrantsInstanceId>
      <AccessGrantsInstanceArn>{{{{ instance.instance_arn }}}}</AccessGrantsInstanceArn>
      <CreatedAt>{{{{ instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
    </AccessGrantsInstance>
    {{% endfor %}}
  </AccessGrantsInstancesList>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListAccessGrantsInstancesResult>
"""

# Access Grants Location templates

CREATE_ACCESS_GRANTS_LOCATION_TEMPLATE = f"""<CreateAccessGrantsLocationResult {XMLNS}>
  <AccessGrantsLocationId>{{{{ location.location_id }}}}</AccessGrantsLocationId>
  <AccessGrantsLocationArn>{{{{ location.location_arn }}}}</AccessGrantsLocationArn>
  <LocationScope>{{{{ location.location_scope }}}}</LocationScope>
  <IAMRoleArn>{{{{ location.iam_role_arn }}}}</IAMRoleArn>
  <CreatedAt>{{{{ location.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
</CreateAccessGrantsLocationResult>
"""

GET_ACCESS_GRANTS_LOCATION_TEMPLATE = f"""<GetAccessGrantsLocationResult {XMLNS}>
  <AccessGrantsLocationId>{{{{ location.location_id }}}}</AccessGrantsLocationId>
  <AccessGrantsLocationArn>{{{{ location.location_arn }}}}</AccessGrantsLocationArn>
  <LocationScope>{{{{ location.location_scope }}}}</LocationScope>
  <IAMRoleArn>{{{{ location.iam_role_arn }}}}</IAMRoleArn>
  <CreatedAt>{{{{ location.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
</GetAccessGrantsLocationResult>
"""

LIST_ACCESS_GRANTS_LOCATIONS_TEMPLATE = f"""<ListAccessGrantsLocationsResult {XMLNS}>
  <AccessGrantsLocationsList>
    {{% for location in locations %}}
    <AccessGrantsLocation>
      <AccessGrantsLocationId>{{{{ location.location_id }}}}</AccessGrantsLocationId>
      <AccessGrantsLocationArn>{{{{ location.location_arn }}}}</AccessGrantsLocationArn>
      <LocationScope>{{{{ location.location_scope }}}}</LocationScope>
      <IAMRoleArn>{{{{ location.iam_role_arn }}}}</IAMRoleArn>
      <CreatedAt>{{{{ location.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
    </AccessGrantsLocation>
    {{% endfor %}}
  </AccessGrantsLocationsList>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListAccessGrantsLocationsResult>
"""

# Access Grant templates

CREATE_ACCESS_GRANT_TEMPLATE = f"""<CreateAccessGrantResult {XMLNS}>
  <AccessGrantId>{{{{ grant.grant_id }}}}</AccessGrantId>
  <AccessGrantArn>{{{{ grant.grant_arn }}}}</AccessGrantArn>
  <AccessGrantsLocationId>{{{{ grant.location_id }}}}</AccessGrantsLocationId>
  <Permission>{{{{ grant.permission }}}}</Permission>
  <CreatedAt>{{{{ grant.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
  <Grantee>
    {{% if grant.grantee.get("GranteeType") %}}<GranteeType>{{{{ grant.grantee["GranteeType"] }}}}</GranteeType>{{% endif %}}
    {{% if grant.grantee.get("GranteeIdentifier") %}}<GranteeIdentifier>{{{{ grant.grantee["GranteeIdentifier"] }}}}</GranteeIdentifier>{{% endif %}}
  </Grantee>
</CreateAccessGrantResult>
"""

GET_ACCESS_GRANT_TEMPLATE = f"""<GetAccessGrantResult {XMLNS}>
  <AccessGrantId>{{{{ grant.grant_id }}}}</AccessGrantId>
  <AccessGrantArn>{{{{ grant.grant_arn }}}}</AccessGrantArn>
  <AccessGrantsLocationId>{{{{ grant.location_id }}}}</AccessGrantsLocationId>
  <Permission>{{{{ grant.permission }}}}</Permission>
  <CreatedAt>{{{{ grant.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
  <Grantee>
    {{% if grant.grantee.get("GranteeType") %}}<GranteeType>{{{{ grant.grantee["GranteeType"] }}}}</GranteeType>{{% endif %}}
    {{% if grant.grantee.get("GranteeIdentifier") %}}<GranteeIdentifier>{{{{ grant.grantee["GranteeIdentifier"] }}}}</GranteeIdentifier>{{% endif %}}
  </Grantee>
  <AccessGrantsLocationConfiguration>
    <S3SubPrefix>{{{{ grant.location_scope }}}}</S3SubPrefix>
  </AccessGrantsLocationConfiguration>
</GetAccessGrantResult>
"""

LIST_ACCESS_GRANTS_TEMPLATE = f"""<ListAccessGrantsResult {XMLNS}>
  <AccessGrantsList>
    {{% for grant in grants %}}
    <AccessGrant>
      <AccessGrantId>{{{{ grant.grant_id }}}}</AccessGrantId>
      <AccessGrantArn>{{{{ grant.grant_arn }}}}</AccessGrantArn>
      <AccessGrantsLocationId>{{{{ grant.location_id }}}}</AccessGrantsLocationId>
      <Permission>{{{{ grant.permission }}}}</Permission>
      <CreatedAt>{{{{ grant.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
    </AccessGrant>
    {{% endfor %}}
  </AccessGrantsList>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListAccessGrantsResult>
"""

# S3 Batch Operations (Jobs) templates

DESCRIBE_JOB_TEMPLATE = f"""<DescribeJobResult {XMLNS}>
  <Job>
    <JobId>{{{{ job.job_id }}}}</JobId>
    <Status>{{{{ job.status }}}}</Status>
    <Description>{{{{ job.description }}}}</Description>
    <Priority>{{{{ job.priority }}}}</Priority>
    <RoleArn>{{{{ job.role_arn }}}}</RoleArn>
    <CreationTime>{{{{ job.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreationTime>
    <ProgressSummary>
      <NumberOfTasksSucceeded>{{{{ job.progress["NumberOfTasksSucceeded"] }}}}</NumberOfTasksSucceeded>
      <NumberOfTasksFailed>{{{{ job.progress["NumberOfTasksFailed"] }}}}</NumberOfTasksFailed>
      <TotalNumberOfTasks>{{{{ job.progress["TotalNumberOfTasks"] }}}}</TotalNumberOfTasks>
    </ProgressSummary>
  </Job>
</DescribeJobResult>
"""

LIST_JOBS_TEMPLATE = f"""<ListJobsResult {XMLNS}>
  <Jobs>
    {{% for job in jobs %}}
    <member>
      <JobId>{{{{ job.job_id }}}}</JobId>
      <Status>{{{{ job.status }}}}</Status>
      <Description>{{{{ job.description }}}}</Description>
      <Priority>{{{{ job.priority }}}}</Priority>
      <CreationTime>{{{{ job.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreationTime>
    </member>
    {{% endfor %}}
  </Jobs>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListJobsResult>
"""

# Bucket-level operation templates

GET_BUCKET_LIFECYCLE_CONFIGURATION_TEMPLATE = f"""<GetBucketLifecycleConfigurationResult {XMLNS}>
  <Rules>
    {{% for rule in rules %}}
    <Rule>
      {{% if rule.id %}}<ID>{{{{ rule.id }}}}</ID>{{% endif %}}
      <Status>{{{{ rule.status }}}}</Status>
      {{% if rule.prefix is not none %}}
      <Prefix>{{{{ rule.prefix }}}}</Prefix>
      {{% elif rule.filter %}}
      <Filter>
        {{% if rule.filter.prefix is not none %}}<Prefix>{{{{ rule.filter.prefix }}}}</Prefix>{{% endif %}}
      </Filter>
      {{% else %}}
      <Filter/>
      {{% endif %}}
    </Rule>
    {{% endfor %}}
  </Rules>
</GetBucketLifecycleConfigurationResult>
"""

GET_BUCKET_POLICY_TEMPLATE = f"""<GetBucketPolicyResult {XMLNS}>
  <Policy>{{{{ policy }}}}</Policy>
</GetBucketPolicyResult>
"""

GET_BUCKET_REPLICATION_TEMPLATE = f"""<GetBucketReplicationResult {XMLNS}>
  {{% if replication %}}
  <ReplicationConfiguration>
    {{% if replication.Role %}}<Role>{{{{ replication.Role }}}}</Role>{{% endif %}}
    {{% if replication.Rules %}}
    <Rules>
      {{% for rule in replication.Rules.Rule %}}
      <Rule>
        {{% if rule.ID %}}<ID>{{{{ rule.ID }}}}</ID>{{% endif %}}
        {{% if rule.Status %}}<Status>{{{{ rule.Status }}}}</Status>{{% endif %}}
        {{% if rule.Priority %}}<Priority>{{{{ rule.Priority }}}}</Priority>{{% endif %}}
        {{% if rule.Bucket %}}<Bucket>{{{{ rule.Bucket }}}}</Bucket>{{% endif %}}
        {{% if rule.Destination %}}
        <Destination>
          {{% if rule.Destination.Bucket %}}<Bucket>{{{{ rule.Destination.Bucket }}}}</Bucket>{{% endif %}}
          {{% if rule.Destination.Account %}}<Account>{{{{ rule.Destination.Account }}}}</Account>{{% endif %}}
        </Destination>
        {{% endif %}}
        {{% if rule.DeleteMarkerReplication %}}
        <DeleteMarkerReplication>
          <Status>{{{{ rule.DeleteMarkerReplication.Status }}}}</Status>
        </DeleteMarkerReplication>
        {{% endif %}}
      </Rule>
      {{% endfor %}}
    </Rules>
    {{% endif %}}
  </ReplicationConfiguration>
  {{% endif %}}
</GetBucketReplicationResult>
"""

GET_BUCKET_TAGGING_TEMPLATE = f"""<GetBucketTaggingResult {XMLNS}>
  <TagSet>
    {{% for tag in tags %}}
    <Tag>
      <Key>{{{{ tag.Key }}}}</Key>
      <Value>{{{{ tag.Value }}}}</Value>
    </Tag>
    {{% endfor %}}
  </TagSet>
</GetBucketTaggingResult>
"""

GET_BUCKET_VERSIONING_TEMPLATE = f"""<GetBucketVersioningResult {XMLNS}>
  <Status>{{{{ status }}}}</Status>
</GetBucketVersioningResult>
"""

CREATE_JOB_TEMPLATE = f"""<CreateJobResult {XMLNS}>
  <JobId>{{{{ job.job_id }}}}</JobId>
</CreateJobResult>
"""

UPDATE_JOB_PRIORITY_TEMPLATE = f"""<UpdateJobPriorityResult {XMLNS}>
  <JobId>{{{{ job.job_id }}}}</JobId>
  <Priority>{{{{ job.priority }}}}</Priority>
</UpdateJobPriorityResult>
"""

UPDATE_JOB_STATUS_TEMPLATE = f"""<UpdateJobStatusResult {XMLNS}>
  <JobId>{{{{ job.job_id }}}}</JobId>
  <Status>{{{{ job.status }}}}</Status>
</UpdateJobStatusResult>
"""

PUT_ACCESS_GRANTS_INSTANCE_RESOURCE_POLICY_TEMPLATE = f"""<PutAccessGrantsInstanceResourcePolicyResult {XMLNS}>
  <Policy>{{{{ policy }}}}</Policy>
</PutAccessGrantsInstanceResourcePolicyResult>
"""

UPDATE_ACCESS_GRANTS_LOCATION_TEMPLATE = f"""<UpdateAccessGrantsLocationResult {XMLNS}>
  <AccessGrantsLocationId>{{{{ location.location_id }}}}</AccessGrantsLocationId>
  <AccessGrantsLocationArn>{{{{ location.location_arn }}}}</AccessGrantsLocationArn>
  <LocationScope>{{{{ location.location_scope }}}}</LocationScope>
  <IAMRoleArn>{{{{ location.iam_role_arn }}}}</IAMRoleArn>
  <CreatedAt>{{{{ location.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") }}}}</CreatedAt>
</UpdateAccessGrantsLocationResult>
"""

GET_MRAP_ROUTES_TEMPLATE = f"""<GetMultiRegionAccessPointRoutesResult {XMLNS}>
  <Mrap>{{{{ mrap }}}}</Mrap>
  <Routes>
    {{% for route in routes %}}
    <Route>
      <Bucket>{{{{ route.Bucket }}}}</Bucket>
      <Region>{{{{ route.Region }}}}</Region>
      <TrafficDialPercentage>{{{{ route.TrafficDialPercentage }}}}</TrafficDialPercentage>
    </Route>
    {{% endfor %}}
  </Routes>
</GetMultiRegionAccessPointRoutesResult>
"""

# Storage Lens Group templates

CREATE_STORAGE_LENS_GROUP_TEMPLATE = f"""<CreateStorageLensGroupResult {XMLNS}>
  <StorageLensGroup>
    <Name>{{{{ group.name }}}}</Name>
    <StorageLensGroupArn>{{{{ group.arn }}}}</StorageLensGroupArn>
  </StorageLensGroup>
</CreateStorageLensGroupResult>
"""

GET_STORAGE_LENS_GROUP_TEMPLATE = f"""<GetStorageLensGroupResult {XMLNS}>
  <StorageLensGroup>
    <Name>{{{{ group.name }}}}</Name>
    <StorageLensGroupArn>{{{{ group.arn }}}}</StorageLensGroupArn>
  </StorageLensGroup>
</GetStorageLensGroupResult>
"""

LIST_STORAGE_LENS_GROUPS_TEMPLATE = f"""<ListStorageLensGroupsResult {XMLNS}>
  <StorageLensGroupList>
    {{% for group in groups %}}
    <StorageLensGroup>
      <Name>{{{{ group.name }}}}</Name>
      <StorageLensGroupArn>{{{{ group.arn }}}}</StorageLensGroupArn>
    </StorageLensGroup>
    {{% endfor %}}
  </StorageLensGroupList>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListStorageLensGroupsResult>
"""

# Object Lambda Access Point templates

CREATE_ACCESS_POINT_FOR_OBJECT_LAMBDA_TEMPLATE = f"""<CreateAccessPointForObjectLambdaResult {XMLNS}>
  <ObjectLambdaAccessPointArn>{{{{ access_point.arn }}}}</ObjectLambdaAccessPointArn>
  <Alias>
    <Status>READY</Status>
    <Value>{{{{ access_point.alias }}}}</Value>
  </Alias>
</CreateAccessPointForObjectLambdaResult>
"""

GET_ACCESS_POINT_FOR_OBJECT_LAMBDA_TEMPLATE = f"""<GetAccessPointForObjectLambdaResult {XMLNS}>
  <Name>{{{{ access_point.name }}}}</Name>
  <ObjectLambdaAccessPointArn>{{{{ access_point.arn }}}}</ObjectLambdaAccessPointArn>
  <CreationDate>{{{{ access_point.created }}}}</CreationDate>
  <Alias>
    <Status>READY</Status>
    <Value>{{{{ access_point.alias }}}}</Value>
  </Alias>
</GetAccessPointForObjectLambdaResult>
"""

# Access Point Scope template

GET_ACCESS_POINT_SCOPE_TEMPLATE = f"""<GetAccessPointScopeResult {XMLNS}>
  {{% if scope %}}
  <Scope>
    {{% for key, value in scope.items() %}}
    <{{{{ key }}}}>{{{{ value }}}}</{{{{ key }}}}>
    {{% endfor %}}
  </Scope>
  {{% endif %}}
</GetAccessPointScopeResult>
"""

# Job Tagging templates

GET_JOB_TAGGING_TEMPLATE = f"""<GetJobTaggingResult {XMLNS}>
  <Tags>
    {{% for tag in tags %}}
    <Tag>
      <Key>{{{{ tag.Key }}}}</Key>
      <Value>{{{{ tag.Value }}}}</Value>
    </Tag>
    {{% endfor %}}
  </Tags>
</GetJobTaggingResult>
"""

LIST_ACCESS_POINTS_FOR_OBJECT_LAMBDA_TEMPLATE = f"""<ListAccessPointsForObjectLambdaResult {XMLNS}>
  <ObjectLambdaAccessPointList>
    {{% for ap in access_points %}}
    <ObjectLambdaAccessPoint>
      <Name>{{{{ ap.Name }}}}</Name>
      <ObjectLambdaAccessPointArn>{{{{ ap.ObjectLambdaAccessPointArn }}}}</ObjectLambdaAccessPointArn>
    </ObjectLambdaAccessPoint>
    {{% endfor %}}
  </ObjectLambdaAccessPointList>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListAccessPointsForObjectLambdaResult>
"""

CREATE_BUCKET_TEMPLATE = f"""<CreateBucketResult {XMLNS}>
  <BucketArn>%(bucket_arn)s</BucketArn>
</CreateBucketResult>
"""

GET_BUCKET_TEMPLATE = f"""<GetBucketResult {XMLNS}>
  <Bucket>{{{{ ob.bucket }}}}</Bucket>
  <PublicAccessBlockEnabled>true</PublicAccessBlockEnabled>
  <CreationDate>{{{{ ob.creation_date.strftime('%Y-%m-%dT%H:%M:%SZ') }}}}</CreationDate>
</GetBucketResult>
"""

LIST_REGIONAL_BUCKETS_TEMPLATE = f"""<ListRegionalBucketsResult {XMLNS}>
  <RegionalBucketList>
    {{% for bucket in buckets %}}
    <RegionalBucket>
      <Bucket>{{{{ bucket.Bucket }}}}</Bucket>
    </RegionalBucket>
    {{% endfor %}}
  </RegionalBucketList>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListRegionalBucketsResult>
"""

LIST_CALLER_ACCESS_GRANTS_TEMPLATE = f"""<ListCallerAccessGrantsResult {XMLNS}>
  <CallerAccessGrantsList>
    {{% for grant in grants %}}
    <CallerAccessGrant>
      <Permission>{{{{ grant.Permission }}}}</Permission>
      <GrantScope>{{{{ grant.GrantScope }}}}</GrantScope>
    </CallerAccessGrant>
    {{% endfor %}}
  </CallerAccessGrantsList>
  {{% if next_token %}}
  <NextToken>{{{{ next_token }}}}</NextToken>
  {{% endif %}}
</ListCallerAccessGrantsResult>
"""
