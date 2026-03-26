import json
from uuid import uuid4

from moto.core.responses import BaseResponse
from moto.core.utils import unix_time

from .models import SSOAdminBackend, ssoadmin_backends


class SSOAdminResponse(BaseResponse):
    """Handler for SSOAdmin requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="sso-admin")

    @property
    def ssoadmin_backend(self) -> SSOAdminBackend:
        """Return backend instance specific for this region."""
        return ssoadmin_backends[self.current_account][self.region]

    def create_account_assignment(self) -> str:
        params = json.loads(self.body)
        instance_arn = params.get("InstanceArn")
        target_id = params.get("TargetId")
        target_type = params.get("TargetType")
        permission_set_arn = params.get("PermissionSetArn")
        principal_type = params.get("PrincipalType")
        principal_id = params.get("PrincipalId")
        summary = self.ssoadmin_backend.create_account_assignment(
            instance_arn=instance_arn,
            target_id=target_id,
            target_type=target_type,
            permission_set_arn=permission_set_arn,
            principal_type=principal_type,
            principal_id=principal_id,
        )
        summary["Status"] = "SUCCEEDED"
        return json.dumps({"AccountAssignmentCreationStatus": summary})

    def delete_account_assignment(self) -> str:
        params = json.loads(self.body)
        instance_arn = params.get("InstanceArn")
        target_id = params.get("TargetId")
        target_type = params.get("TargetType")
        permission_set_arn = params.get("PermissionSetArn")
        principal_type = params.get("PrincipalType")
        principal_id = params.get("PrincipalId")
        summary = self.ssoadmin_backend.delete_account_assignment(
            instance_arn=instance_arn,
            target_id=target_id,
            target_type=target_type,
            permission_set_arn=permission_set_arn,
            principal_type=principal_type,
            principal_id=principal_id,
        )
        summary["Status"] = "SUCCEEDED"
        return json.dumps({"AccountAssignmentDeletionStatus": summary})

    def list_account_assignments(self) -> str:
        params = json.loads(self.body)
        instance_arn = params.get("InstanceArn")
        account_id = params.get("AccountId")
        permission_set_arn = params.get("PermissionSetArn")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")

        assignments, next_token = self.ssoadmin_backend.list_account_assignments(
            instance_arn=instance_arn,
            account_id=account_id,
            permission_set_arn=permission_set_arn,
            next_token=next_token,
            max_results=max_results,
        )

        return json.dumps({"AccountAssignments": assignments, "NextToken": next_token})

    def list_account_assignments_for_principal(self) -> str:
        filter_ = self._get_param("Filter", {})
        instance_arn = self._get_param("InstanceArn")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        principal_id = self._get_param("PrincipalId")
        principal_type = self._get_param("PrincipalType")

        (
            assignments,
            next_token,
        ) = self.ssoadmin_backend.list_account_assignments_for_principal(
            filter_=filter_,
            instance_arn=instance_arn,
            max_results=max_results,
            next_token=next_token,
            principal_id=principal_id,
            principal_type=principal_type,
        )

        return json.dumps({"AccountAssignments": assignments, "NextToken": next_token})

    def create_permission_set(self) -> str:
        name = self._get_param("Name")
        description = self._get_param("Description")
        instance_arn = self._get_param("InstanceArn")
        session_duration = self._get_param("SessionDuration", 3600)
        relay_state = self._get_param("RelayState")
        tags = self._get_param("Tags")

        permission_set = self.ssoadmin_backend.create_permission_set(
            name=name,
            description=description,
            instance_arn=instance_arn,
            session_duration=session_duration,
            relay_state=relay_state,
            tags=tags,
        )

        return json.dumps({"PermissionSet": permission_set})

    def delete_permission_set(self) -> str:
        params = json.loads(self.body)
        instance_arn = params.get("InstanceArn")
        permission_set_arn = params.get("PermissionSetArn")
        self.ssoadmin_backend.delete_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
        )
        return "{}"

    def update_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        description = self._get_param("Description")
        session_duration = self._get_param("SessionDuration", 3600)
        relay_state = self._get_param("RelayState")

        self.ssoadmin_backend.update_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            description=description,
            session_duration=session_duration,
            relay_state=relay_state,
        )
        return "{}"

    def describe_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")

        permission_set = self.ssoadmin_backend.describe_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
        )
        return json.dumps({"PermissionSet": permission_set})

    def list_permission_sets(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        permission_sets, next_token = self.ssoadmin_backend.list_permission_sets(
            instance_arn=instance_arn, max_results=max_results, next_token=next_token
        )
        permission_set_ids = []
        for permission_set in permission_sets:
            permission_set_ids.append(permission_set.permission_set_arn)
        response = {"PermissionSets": permission_set_ids, "NextToken": next_token}
        return json.dumps(response)

    def put_inline_policy_to_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        inline_policy = self._get_param("InlinePolicy")
        self.ssoadmin_backend.put_inline_policy_to_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            inline_policy=inline_policy,
        )
        return json.dumps({})

    def get_inline_policy_for_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        inline_policy = self.ssoadmin_backend.get_inline_policy_for_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
        )
        return json.dumps({"InlinePolicy": inline_policy})

    def delete_inline_policy_from_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        self.ssoadmin_backend.delete_inline_policy_from_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
        )
        return json.dumps({})

    def attach_managed_policy_to_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        managed_policy_arn = self._get_param("ManagedPolicyArn")
        self.ssoadmin_backend.attach_managed_policy_to_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            managed_policy_arn=managed_policy_arn,
        )
        return json.dumps({})

    def list_managed_policies_in_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")

        (
            managed_policies,
            next_token,
        ) = self.ssoadmin_backend.list_managed_policies_in_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            max_results=max_results,
            next_token=next_token,
        )

        managed_policies_response = [
            {"Arn": managed_policy.arn, "Name": managed_policy.name}
            for managed_policy in managed_policies
        ]
        return json.dumps(
            {
                "AttachedManagedPolicies": managed_policies_response,
                "NextToken": next_token,
            }
        )

    def detach_managed_policy_from_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        managed_policy_arn = self._get_param("ManagedPolicyArn")
        self.ssoadmin_backend.detach_managed_policy_from_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            managed_policy_arn=managed_policy_arn,
        )
        return json.dumps({})

    def attach_customer_managed_policy_reference_to_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        customer_managed_policy_reference = self._get_param(
            "CustomerManagedPolicyReference"
        )
        self.ssoadmin_backend.attach_customer_managed_policy_reference_to_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            customer_managed_policy_reference=customer_managed_policy_reference,
        )
        return json.dumps({})

    def list_customer_managed_policy_references_in_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")

        (
            customer_managed_policy_references,
            next_token,
        ) = self.ssoadmin_backend.list_customer_managed_policy_references_in_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            max_results=max_results,
            next_token=next_token,
        )

        customer_managed_policy_references_response = [
            {
                "Name": customer_managed_policy_reference.name,
                "Path": customer_managed_policy_reference.path,
            }
            for customer_managed_policy_reference in customer_managed_policy_references
        ]
        return json.dumps(
            {
                "CustomerManagedPolicyReferences": customer_managed_policy_references_response,
                "NextToken": next_token,
            }
        )

    def detach_customer_managed_policy_reference_from_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        customer_managed_policy_reference = self._get_param(
            "CustomerManagedPolicyReference"
        )
        self.ssoadmin_backend.detach_customer_managed_policy_reference_from_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            customer_managed_policy_reference=customer_managed_policy_reference,
        )
        return json.dumps({})

    def describe_account_assignment_creation_status(self) -> str:
        account_assignment_creation_request_id = self._get_param(
            "AccountAssignmentCreationRequestId"
        )
        instance_arn = self._get_param("InstanceArn")
        account_assignment_creation_status = self.ssoadmin_backend.describe_account_assignment_creation_status(
            account_assignment_creation_request_id=account_assignment_creation_request_id,
            instance_arn=instance_arn,
        )
        account_assignment_creation_status["Status"] = "SUCCEEDED"
        return json.dumps(
            {"AccountAssignmentCreationStatus": account_assignment_creation_status}
        )

    def describe_account_assignment_deletion_status(self) -> str:
        account_assignment_deletion_request_id = self._get_param(
            "AccountAssignmentDeletionRequestId"
        )
        instance_arn = self._get_param("InstanceArn")
        account_assignment_deletion_status = self.ssoadmin_backend.describe_account_assignment_deletion_status(
            account_assignment_deletion_request_id=account_assignment_deletion_request_id,
            instance_arn=instance_arn,
        )
        account_assignment_deletion_status["Status"] = "SUCCEEDED"
        return json.dumps(
            {"AccountAssignmentDeletionStatus": account_assignment_deletion_status}
        )

    def list_instances(self) -> str:
        instances = self.ssoadmin_backend.list_instances()

        return json.dumps({"Instances": [i.to_json() for i in instances]})

    def update_instance(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        name = self._get_param("Name")

        self.ssoadmin_backend.update_instance(instance_arn=instance_arn, name=name)

        return "{}"

    def provision_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")

        self.ssoadmin_backend.provision_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
        )
        return json.dumps(
            {
                "PermissionSetProvisioningStatus": {
                    "AccountId": self.current_account,
                    "CreatedDate": unix_time(),
                    "PermissionSetArn": permission_set_arn,
                    "RequestId": str(uuid4()),
                    "Status": "SUCCEEDED",
                }
            }
        )

    def list_permission_sets_provisioned_to_account(self) -> str:
        instance_arn = self._get_param("InstanceArn")

        permission_sets = (
            self.ssoadmin_backend.list_permission_sets_provisioned_to_account(
                instance_arn
            )
        )
        arns = [p.permission_set_arn for p in permission_sets]
        return json.dumps({"PermissionSets": arns})

    def list_accounts_for_provisioned_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")

        account_ids = (
            self.ssoadmin_backend.list_accounts_for_provisioned_permission_set(
                instance_arn=instance_arn, permission_set_arn=permission_set_arn
            )
        )
        return json.dumps({"AccountIds": account_ids})

    # --- Tagging ---

    def tag_resource(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags", [])
        self.ssoadmin_backend.tag_resource(
            instance_arn=instance_arn, resource_arn=resource_arn, tags=tags
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys", [])
        self.ssoadmin_backend.untag_resource(
            instance_arn=instance_arn, resource_arn=resource_arn, tag_keys=tag_keys
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        resource_arn = self._get_param("ResourceArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        tags, next_token = self.ssoadmin_backend.list_tags_for_resource(
            instance_arn=instance_arn,
            resource_arn=resource_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"Tags": tags, "NextToken": next_token})

    # --- Permissions Boundary ---

    def put_permissions_boundary_to_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        permissions_boundary = self._get_param("PermissionsBoundary")
        self.ssoadmin_backend.put_permissions_boundary_to_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            permissions_boundary=permissions_boundary,
        )
        return json.dumps({})

    def get_permissions_boundary_for_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        boundary = self.ssoadmin_backend.get_permissions_boundary_for_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
        )
        return json.dumps({"PermissionsBoundary": boundary})

    def delete_permissions_boundary_from_permission_set(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        permission_set_arn = self._get_param("PermissionSetArn")
        self.ssoadmin_backend.delete_permissions_boundary_from_permission_set(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
        )
        return json.dumps({})

    # --- Instance CRUD ---

    def create_instance(self) -> str:
        client_token = self._get_param("ClientToken")
        name = self._get_param("Name")
        tags = self._get_param("Tags", [])
        instance = self.ssoadmin_backend.create_instance(
            client_token=client_token, name=name, tags=tags
        )
        return json.dumps({"InstanceArn": instance.instance_arn})

    def delete_instance(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        self.ssoadmin_backend.delete_instance(instance_arn=instance_arn)
        return json.dumps({})

    def describe_instance(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        instance = self.ssoadmin_backend.describe_instance(instance_arn=instance_arn)
        return json.dumps({"InstanceMetadata": instance.to_json()})

    # --- Instance Access Control Attribute Configuration ---

    def create_instance_access_control_attribute_configuration(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        config = self._get_param("InstanceAccessControlAttributeConfiguration")
        self.ssoadmin_backend.create_instance_access_control_attribute_configuration(
            instance_arn=instance_arn,
            instance_access_control_attribute_configuration=config,
        )
        return json.dumps({})

    def describe_instance_access_control_attribute_configuration(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        config = self.ssoadmin_backend.describe_instance_access_control_attribute_configuration(
            instance_arn=instance_arn
        )
        return json.dumps(
            {"InstanceAccessControlAttributeConfiguration": config, "Status": config["Status"]}
        )

    def update_instance_access_control_attribute_configuration(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        config = self._get_param("InstanceAccessControlAttributeConfiguration")
        self.ssoadmin_backend.update_instance_access_control_attribute_configuration(
            instance_arn=instance_arn,
            instance_access_control_attribute_configuration=config,
        )
        return json.dumps({})

    def delete_instance_access_control_attribute_configuration(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        self.ssoadmin_backend.delete_instance_access_control_attribute_configuration(
            instance_arn=instance_arn
        )
        return json.dumps({})

    # --- Account assignment status lists ---

    def list_account_assignment_creation_status(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        filter_ = self._get_param("Filter")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        statuses, next_token = self.ssoadmin_backend.list_account_assignment_creation_status(
            instance_arn=instance_arn,
            filter_=filter_,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"AccountAssignmentsCreationStatus": statuses, "NextToken": next_token}
        )

    def list_account_assignment_deletion_status(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        filter_ = self._get_param("Filter")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        statuses, next_token = self.ssoadmin_backend.list_account_assignment_deletion_status(
            instance_arn=instance_arn,
            filter_=filter_,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"AccountAssignmentsDeletionStatus": statuses, "NextToken": next_token}
        )

    def list_permission_set_provisioning_status(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        filter_ = self._get_param("Filter")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        statuses, next_token = self.ssoadmin_backend.list_permission_set_provisioning_status(
            instance_arn=instance_arn,
            filter_=filter_,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"PermissionSetsProvisioningStatus": statuses, "NextToken": next_token}
        )

    # --- Applications ---

    def create_application(self) -> str:
        application_provider_arn = self._get_param("ApplicationProviderArn")
        instance_arn = self._get_param("InstanceArn")
        name = self._get_param("Name")
        description = self._get_param("Description")
        portal_options = self._get_param("PortalOptions")
        status = self._get_param("Status", "ENABLED")
        tags = self._get_param("Tags", [])
        client_token = self._get_param("ClientToken")
        application = self.ssoadmin_backend.create_application(
            application_provider_arn=application_provider_arn,
            instance_arn=instance_arn,
            name=name,
            description=description,
            portal_options=portal_options,
            status=status,
            tags=tags,
            client_token=client_token,
        )
        return json.dumps({"ApplicationArn": application.application_arn})

    def delete_application(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        self.ssoadmin_backend.delete_application(application_arn=application_arn)
        return json.dumps({})

    def describe_application(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        application = self.ssoadmin_backend.describe_application(
            application_arn=application_arn
        )
        return json.dumps(application.to_json())

    def update_application(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        description = self._get_param("Description")
        name = self._get_param("Name")
        portal_options = self._get_param("PortalOptions")
        status = self._get_param("Status")
        self.ssoadmin_backend.update_application(
            application_arn=application_arn,
            description=description,
            name=name,
            portal_options=portal_options,
            status=status,
        )
        return json.dumps({})

    def list_applications(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        filter_ = self._get_param("Filter")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        applications, next_token = self.ssoadmin_backend.list_applications(
            instance_arn=instance_arn,
            filter_=filter_,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {
                "Applications": [a.to_json() for a in applications],
                "NextToken": next_token,
            }
        )

    # --- Application Access Scopes ---

    def put_application_access_scope(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        scope = self._get_param("Scope")
        authorized_targets = self._get_param("AuthorizedTargets")
        self.ssoadmin_backend.put_application_access_scope(
            application_arn=application_arn,
            scope=scope,
            authorized_targets=authorized_targets,
        )
        return json.dumps({})

    def get_application_access_scope(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        scope = self._get_param("Scope")
        result = self.ssoadmin_backend.get_application_access_scope(
            application_arn=application_arn, scope=scope
        )
        return json.dumps(result)

    def delete_application_access_scope(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        scope = self._get_param("Scope")
        self.ssoadmin_backend.delete_application_access_scope(
            application_arn=application_arn, scope=scope
        )
        return json.dumps({})

    def list_application_access_scopes(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        scopes, next_token = self.ssoadmin_backend.list_application_access_scopes(
            application_arn=application_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"Scopes": scopes, "NextToken": next_token})

    # --- Application Assignments ---

    def create_application_assignment(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        principal_type = self._get_param("PrincipalType")
        principal_id = self._get_param("PrincipalId")
        self.ssoadmin_backend.create_application_assignment(
            application_arn=application_arn,
            principal_type=principal_type,
            principal_id=principal_id,
        )
        return json.dumps({})

    def delete_application_assignment(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        principal_type = self._get_param("PrincipalType")
        principal_id = self._get_param("PrincipalId")
        self.ssoadmin_backend.delete_application_assignment(
            application_arn=application_arn,
            principal_type=principal_type,
            principal_id=principal_id,
        )
        return json.dumps({})

    def describe_application_assignment(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        principal_type = self._get_param("PrincipalType")
        principal_id = self._get_param("PrincipalId")
        assignment = self.ssoadmin_backend.describe_application_assignment(
            application_arn=application_arn,
            principal_type=principal_type,
            principal_id=principal_id,
        )
        return json.dumps(assignment.to_json())

    def list_application_assignments(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        assignments, next_token = self.ssoadmin_backend.list_application_assignments(
            application_arn=application_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {
                "ApplicationAssignments": [a.to_json() for a in assignments],
                "NextToken": next_token,
            }
        )

    def list_application_assignments_for_principal(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        principal_type = self._get_param("PrincipalType")
        principal_id = self._get_param("PrincipalId")
        filter_ = self._get_param("Filter")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        assignments, next_token = self.ssoadmin_backend.list_application_assignments_for_principal(
            instance_arn=instance_arn,
            principal_type=principal_type,
            principal_id=principal_id,
            filter_=filter_,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"ApplicationAssignments": assignments, "NextToken": next_token}
        )

    # --- Application Assignment Configuration ---

    def put_application_assignment_configuration(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        assignment_required = self._get_param("AssignmentRequired", False)
        self.ssoadmin_backend.put_application_assignment_configuration(
            application_arn=application_arn,
            assignment_required=assignment_required,
        )
        return json.dumps({})

    def get_application_assignment_configuration(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        config = self.ssoadmin_backend.get_application_assignment_configuration(
            application_arn=application_arn
        )
        return json.dumps(config)

    # --- Application Authentication Methods ---

    def put_application_authentication_method(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        authentication_method_type = self._get_param("AuthenticationMethodType")
        authentication_method = self._get_param("AuthenticationMethod")
        self.ssoadmin_backend.put_application_authentication_method(
            application_arn=application_arn,
            authentication_method_type=authentication_method_type,
            authentication_method=authentication_method,
        )
        return json.dumps({})

    def get_application_authentication_method(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        authentication_method_type = self._get_param("AuthenticationMethodType")
        result = self.ssoadmin_backend.get_application_authentication_method(
            application_arn=application_arn,
            authentication_method_type=authentication_method_type,
        )
        return json.dumps(result)

    def delete_application_authentication_method(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        authentication_method_type = self._get_param("AuthenticationMethodType")
        self.ssoadmin_backend.delete_application_authentication_method(
            application_arn=application_arn,
            authentication_method_type=authentication_method_type,
        )
        return json.dumps({})

    def list_application_authentication_methods(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        methods, next_token = self.ssoadmin_backend.list_application_authentication_methods(
            application_arn=application_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"AuthenticationMethods": methods, "NextToken": next_token})

    # --- Application Grants ---

    def put_application_grant(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        grant_type = self._get_param("GrantType")
        grant = self._get_param("Grant")
        self.ssoadmin_backend.put_application_grant(
            application_arn=application_arn,
            grant_type=grant_type,
            grant=grant,
        )
        return json.dumps({})

    def get_application_grant(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        grant_type = self._get_param("GrantType")
        result = self.ssoadmin_backend.get_application_grant(
            application_arn=application_arn,
            grant_type=grant_type,
        )
        return json.dumps(result)

    def delete_application_grant(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        grant_type = self._get_param("GrantType")
        self.ssoadmin_backend.delete_application_grant(
            application_arn=application_arn,
            grant_type=grant_type,
        )
        return json.dumps({})

    def list_application_grants(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        grants, next_token = self.ssoadmin_backend.list_application_grants(
            application_arn=application_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"Grants": grants, "NextToken": next_token})

    # --- Application Session Configuration ---

    def put_application_session_configuration(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        session_configuration = self._get_param("SessionConfiguration")
        self.ssoadmin_backend.put_application_session_configuration(
            application_arn=application_arn,
            session_configuration=session_configuration,
        )
        return json.dumps({})

    def get_application_session_configuration(self) -> str:
        application_arn = self._get_param("ApplicationArn")
        config = self.ssoadmin_backend.get_application_session_configuration(
            application_arn=application_arn
        )
        return json.dumps(config)

    # --- Trusted Token Issuers ---

    def create_trusted_token_issuer(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        name = self._get_param("Name")
        trusted_token_issuer_type = self._get_param("TrustedTokenIssuerType")
        trusted_token_issuer_configuration = self._get_param(
            "TrustedTokenIssuerConfiguration"
        )
        tags = self._get_param("Tags", [])
        client_token = self._get_param("ClientToken")
        tti = self.ssoadmin_backend.create_trusted_token_issuer(
            instance_arn=instance_arn,
            name=name,
            trusted_token_issuer_type=trusted_token_issuer_type,
            trusted_token_issuer_configuration=trusted_token_issuer_configuration,
            tags=tags,
            client_token=client_token,
        )
        return json.dumps({"TrustedTokenIssuerArn": tti.trusted_token_issuer_arn})

    def delete_trusted_token_issuer(self) -> str:
        trusted_token_issuer_arn = self._get_param("TrustedTokenIssuerArn")
        self.ssoadmin_backend.delete_trusted_token_issuer(
            trusted_token_issuer_arn=trusted_token_issuer_arn
        )
        return json.dumps({})

    def describe_trusted_token_issuer(self) -> str:
        trusted_token_issuer_arn = self._get_param("TrustedTokenIssuerArn")
        tti = self.ssoadmin_backend.describe_trusted_token_issuer(
            trusted_token_issuer_arn=trusted_token_issuer_arn
        )
        return json.dumps(tti.to_json())

    def update_trusted_token_issuer(self) -> str:
        trusted_token_issuer_arn = self._get_param("TrustedTokenIssuerArn")
        name = self._get_param("Name")
        trusted_token_issuer_configuration = self._get_param(
            "TrustedTokenIssuerConfiguration"
        )
        self.ssoadmin_backend.update_trusted_token_issuer(
            trusted_token_issuer_arn=trusted_token_issuer_arn,
            name=name,
            trusted_token_issuer_configuration=trusted_token_issuer_configuration,
        )
        return json.dumps({})

    def list_trusted_token_issuers(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        issuers, next_token = self.ssoadmin_backend.list_trusted_token_issuers(
            instance_arn=instance_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {
                "TrustedTokenIssuers": [tti.to_json() for tti in issuers],
                "NextToken": next_token,
            }
        )

    # --- Application Providers ---

    def list_application_providers(self) -> str:
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        providers, next_token = self.ssoadmin_backend.list_application_providers(
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"ApplicationProviders": providers, "NextToken": next_token})

    def describe_application_provider(self) -> str:
        application_provider_arn = self._get_param("ApplicationProviderArn")
        provider = self.ssoadmin_backend.describe_application_provider(
            application_provider_arn=application_provider_arn
        )
        return json.dumps(provider)

    # --- Region management ---

    def add_region(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        region_to_add = self._get_param("RegionToAdd")
        client_token = self._get_param("ClientToken")
        self.ssoadmin_backend.add_region(
            instance_arn=instance_arn,
            region_to_add=region_to_add,
            client_token=client_token,
        )
        return json.dumps({})

    def remove_region(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        region_to_remove = self._get_param("RegionToRemove")
        client_token = self._get_param("ClientToken")
        self.ssoadmin_backend.remove_region(
            instance_arn=instance_arn,
            region_to_remove=region_to_remove,
            client_token=client_token,
        )
        return json.dumps({})

    def list_regions(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        max_results = self._get_int_param("MaxResults")
        next_token = self._get_param("NextToken")
        regions, next_token = self.ssoadmin_backend.list_regions(
            instance_arn=instance_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"Regions": regions, "NextToken": next_token})

    def describe_region(self) -> str:
        instance_arn = self._get_param("InstanceArn")
        region = self._get_param("Region")
        result = self.ssoadmin_backend.describe_region(
            instance_arn=instance_arn, region=region
        )
        return json.dumps(result)
