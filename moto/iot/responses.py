from urllib.parse import unquote

from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .models import IoTBackend, iot_backends


class IoTResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="iot")

    @property
    def iot_backend(self) -> IoTBackend:
        return iot_backends[self.current_account][self.region]

    def create_certificate_from_csr(self) -> ActionResult:
        certificate_signing_request = self._get_param("certificateSigningRequest")
        set_as_active = self._get_param("setAsActive")
        cert = self.iot_backend.create_certificate_from_csr(
            certificate_signing_request, set_as_active=set_as_active
        )
        return ActionResult(
            {
                "certificateId": cert.certificate_id,
                "certificateArn": cert.arn,
                "certificatePem": cert.certificate_pem,
            }
        )

    def create_thing(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        thing_type_name = self._get_param("thingTypeName")
        attribute_payload = self._get_param("attributePayload")
        billing_group_name = self._get_param("billingGroupName")
        thing = self.iot_backend.create_thing(
            thing_name=thing_name,
            thing_type_name=thing_type_name,
            attribute_payload=attribute_payload,
            billing_group_name=billing_group_name,
        )
        return ActionResult(
            {
                "thingName": thing.thing_name,
                "thingArn": thing.arn,
                "thingId": thing.thing_id,
            }
        )

    def create_thing_type(self) -> ActionResult:
        thing_type_name = self._get_param("thingTypeName")
        thing_type_properties = self._get_param("thingTypeProperties")
        thing_type_name, thing_type_arn = self.iot_backend.create_thing_type(
            thing_type_name=thing_type_name, thing_type_properties=thing_type_properties
        )
        return ActionResult(
            {"thingTypeName": thing_type_name, "thingTypeArn": thing_type_arn}
        )

    def list_thing_types(self) -> ActionResult:
        previous_next_token = self._get_param("nextToken")
        max_results = self._get_int_param(
            "maxResults", 50
        )  # not the default, but makes testing easier
        thing_type_name = self._get_param("thingTypeName")
        _types = self.iot_backend.list_thing_types(thing_type_name=thing_type_name)
        thing_types = [_.to_dict() for _ in _types]
        if previous_next_token is None:
            result = thing_types[0:max_results]
            next_token = str(max_results) if len(thing_types) > max_results else None
        else:
            token = int(previous_next_token)
            result = thing_types[token : token + max_results]
            next_token = (
                str(token + max_results)
                if len(thing_types) > token + max_results
                else None
            )

        return ActionResult({"thingTypes": result, "nextToken": next_token})

    def list_things(self) -> ActionResult:
        previous_next_token = self._get_param("nextToken")
        max_results = self._get_int_param(
            "maxResults", 50
        )  # not the default, but makes testing easier
        attribute_name = self._get_param("attributeName")
        attribute_value = self._get_param("attributeValue")
        thing_type_name = self._get_param("thingTypeName")
        things, next_token = self.iot_backend.list_things(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            thing_type_name=thing_type_name,
            max_results=max_results,
            token=previous_next_token,
        )

        return ActionResult({"things": things, "nextToken": next_token})

    def describe_thing(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        thing = self.iot_backend.describe_thing(thing_name=thing_name)
        return ActionResult(
            thing.to_dict(include_default_client_id=True, include_thing_id=True)
        )

    def describe_thing_type(self) -> ActionResult:
        thing_type_name = self._get_param("thingTypeName")
        thing_type = self.iot_backend.describe_thing_type(
            thing_type_name=thing_type_name
        )
        return ActionResult(thing_type.to_dict())

    def describe_endpoint(self) -> ActionResult:
        endpoint_type = self._get_param("endpointType", "iot:Data-ATS")
        endpoint = self.iot_backend.describe_endpoint(endpoint_type=endpoint_type)
        return ActionResult(endpoint.to_dict())

    def describe_encryption_configuration(self) -> ActionResult:
        result = self.iot_backend.describe_encryption_configuration()
        return ActionResult(result)

    def get_thing_connectivity_data(self) -> ActionResult:
        thing_name = self._get_param("thingName") or unquote(
            self.path.split("/things/")[-1].split("/")[0]
        )
        result = self.iot_backend.get_thing_connectivity_data(thing_name)
        return ActionResult(result)

    def delete_thing(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        self.iot_backend.delete_thing(thing_name=thing_name)
        return EmptyResult()

    def delete_thing_type(self) -> ActionResult:
        thing_type_name = self._get_param("thingTypeName")
        self.iot_backend.delete_thing_type(thing_type_name=thing_type_name)
        return EmptyResult()

    def deprecate_thing_type(self) -> ActionResult:
        thing_type_name = self._get_param("thingTypeName")
        undo_deprecate = self._get_param("undoDeprecate")
        thing_type = self.iot_backend.deprecate_thing_type(
            thing_type_name=thing_type_name, undo_deprecate=undo_deprecate
        )
        return ActionResult(thing_type.to_dict())

    def update_thing(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        thing_type_name = self._get_param("thingTypeName")
        attribute_payload = self._get_param("attributePayload")
        remove_thing_type = self._get_param("removeThingType")
        self.iot_backend.update_thing(
            thing_name=thing_name,
            thing_type_name=thing_type_name,
            attribute_payload=attribute_payload,
            remove_thing_type=remove_thing_type,
        )
        return EmptyResult()

    def create_job(self) -> ActionResult:
        job_arn, job_id, description = self.iot_backend.create_job(
            job_id=self._get_param("jobId"),
            targets=self._get_param("targets"),
            description=self._get_param("description"),
            document_source=self._get_param("documentSource"),
            document=self._get_param("document"),
            presigned_url_config=self._get_param("presignedUrlConfig"),
            target_selection=self._get_param("targetSelection"),
            job_executions_rollout_config=self._get_param("jobExecutionsRolloutConfig"),
            document_parameters=self._get_param("documentParameters"),
            abort_config=self._get_param("abortConfig"),
            job_execution_retry_config=self._get_param("jobExecutionsRetryConfig"),
            scheduling_config=self._get_param("schedulingConfig"),
            timeout_config=self._get_param("timeoutConfig"),
        )

        return ActionResult(
            {"jobArn": job_arn, "jobId": job_id, "description": description}
        )

    def describe_job(self) -> ActionResult:
        job = self.iot_backend.describe_job(job_id=self._get_param("jobId"))
        return ActionResult(
            {
                "documentSource": job.document_source,
                "job": {
                    "comment": job.comment,
                    "completedAt": job.completed_at,
                    "createdAt": job.created_at,
                    "description": job.description,
                    "documentParameters": job.document_parameters,
                    "forceCanceled": job.force,
                    "reasonCode": job.reason_code,
                    "jobArn": job.job_arn,
                    "jobExecutionsRolloutConfig": job.job_executions_rollout_config,
                    "jobExecutionsRetryConfig": job.job_execution_retry_config,
                    "schedulingConfig": job.scheduling_config,
                    "timeoutConfig": job.timeout_config,
                    "abortConfig": job.abort_config,
                    "jobId": job.job_id,
                    "jobProcessDetails": job.job_process_details,
                    "lastUpdatedAt": job.last_updated_at,
                    "presignedUrlConfig": job.presigned_url_config,
                    "status": job.status,
                    "targets": job.targets,
                    "targetSelection": job.target_selection,
                },
            }
        )

    def delete_job(self) -> ActionResult:
        job_id = self._get_param("jobId")
        force = self._get_bool_param("force")

        self.iot_backend.delete_job(job_id=job_id, force=force)

        return EmptyResult()

    def cancel_job(self) -> ActionResult:
        job_id = self._get_param("jobId")
        reason_code = self._get_param("reasonCode")
        comment = self._get_param("comment")
        force = self._get_bool_param("force")

        job = self.iot_backend.cancel_job(
            job_id=job_id, reason_code=reason_code, comment=comment, force=force
        )

        return ActionResult(job.to_dict())

    def get_job_document(self) -> ActionResult:
        job = self.iot_backend.get_job_document(job_id=self._get_param("jobId"))

        if job.document is not None:
            return ActionResult({"document": job.document})
        else:
            # job.document_source is not None:
            # TODO: needs to be implemented to get document_source's content from S3
            return ActionResult({"document": ""})

    def list_jobs(self) -> ActionResult:
        # not the default, but makes testing easier
        max_results = self._get_int_param("maxResults", 50)
        previous_next_token = self._get_param("nextToken")
        jobs, next_token = self.iot_backend.list_jobs(
            max_results=max_results, next_token=previous_next_token
        )

        return ActionResult(
            {"jobs": [job.to_dict() for job in jobs], "nextToken": next_token}
        )

    def describe_job_execution(self) -> ActionResult:
        job_id = self._get_param("jobId")
        thing_name = self._get_param("thingName")
        execution_number = self._get_int_param("executionNumber")
        job_execution = self.iot_backend.describe_job_execution(
            job_id=job_id, thing_name=thing_name, execution_number=execution_number
        )

        return ActionResult({"execution": job_execution.to_get_dict()})

    def cancel_job_execution(self) -> ActionResult:
        job_id = self._get_param("jobId")
        thing_name = self._get_param("thingName")
        force = self._get_bool_param("force")

        self.iot_backend.cancel_job_execution(
            job_id=job_id, thing_name=thing_name, force=force
        )

        return EmptyResult()

    def delete_job_execution(self) -> ActionResult:
        job_id = self._get_param("jobId")
        thing_name = self._get_param("thingName")
        execution_number = self._get_int_param("executionNumber")
        force = self._get_bool_param("force")

        self.iot_backend.delete_job_execution(
            job_id=job_id,
            thing_name=thing_name,
            execution_number=execution_number,
            force=force,
        )

        return EmptyResult()

    def list_job_executions_for_job(self) -> ActionResult:
        job_id = self._get_param("jobId")
        status = self._get_param("status")
        max_results = self._get_int_param(
            "maxResults", 50
        )  # not the default, but makes testing easier
        next_token = self._get_param("nextToken")
        job_executions, next_token = self.iot_backend.list_job_executions_for_job(
            job_id=job_id, status=status, max_results=max_results, token=next_token
        )

        return ActionResult(
            {
                "executionSummaries": [je.to_dict() for je in job_executions],
                "nextToken": next_token,
            }
        )

    def list_job_executions_for_thing(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        status = self._get_param("status")
        max_results = self._get_int_param(
            "maxResults", 50
        )  # not the default, but makes testing easier
        next_token = self._get_param("nextToken")
        job_executions, next_token = self.iot_backend.list_job_executions_for_thing(
            thing_name=thing_name,
            status=status,
            max_results=max_results,
            next_token=next_token,
        )

        return ActionResult(
            {
                "executionSummaries": [je.to_dict() for je in job_executions],
                "nextToken": next_token,
            }
        )

    def create_keys_and_certificate(self) -> ActionResult:
        set_as_active = self._get_bool_param("setAsActive")
        cert, key_pair = self.iot_backend.create_keys_and_certificate(
            set_as_active=set_as_active
        )
        return ActionResult(
            {
                "certificateArn": cert.arn,
                "certificateId": cert.certificate_id,
                "certificatePem": cert.certificate_pem,
                "keyPair": key_pair,
            }
        )

    def delete_ca_certificate(self) -> ActionResult:
        certificate_id = self.path.split("/")[-1]
        self.iot_backend.delete_ca_certificate(certificate_id=certificate_id)
        return EmptyResult()

    def delete_certificate(self) -> ActionResult:
        certificate_id = self._get_param("certificateId")
        force_delete = self._get_bool_param("forceDelete", False)
        self.iot_backend.delete_certificate(certificate_id, force_delete)
        return EmptyResult()

    def describe_ca_certificate(self) -> ActionResult:
        certificate_id = self.path.split("/")[-1]
        certificate = self.iot_backend.describe_ca_certificate(
            certificate_id=certificate_id
        )
        return ActionResult(
            {
                "certificateDescription": certificate.to_description_dict(),
                "registrationConfig": certificate.registration_config,
            }
        )

    def describe_certificate(self) -> ActionResult:
        certificate_id = self._get_param("certificateId")
        certificate = self.iot_backend.describe_certificate(
            certificate_id=certificate_id
        )
        return ActionResult(
            {"certificateDescription": certificate.to_description_dict()}
        )

    def get_registration_code(self) -> ActionResult:
        code = self.iot_backend.get_registration_code()
        return ActionResult({"registrationCode": code})

    def list_certificates(self) -> ActionResult:
        # page_size = self._get_int_param("pageSize")
        # marker = self._get_param("marker")
        # ascending_order = self._get_param("ascendingOrder")
        certificates = self.iot_backend.list_certificates()
        return ActionResult({"certificates": [_.to_dict() for _ in certificates]})

    def list_certificates_by_ca(self) -> ActionResult:
        ca_certificate_id = self._get_param("caCertificateId")
        certificates = self.iot_backend.list_certificates_by_ca(ca_certificate_id)
        return ActionResult({"certificates": [_.to_dict() for _ in certificates]})

    def register_ca_certificate(self) -> ActionResult:
        ca_certificate = self._get_param("caCertificate")
        set_as_active = self._get_bool_param("setAsActive")
        registration_config = self._get_param("registrationConfig")

        cert = self.iot_backend.register_ca_certificate(
            ca_certificate=ca_certificate,
            set_as_active=set_as_active,
            registration_config=registration_config,
        )
        return ActionResult(
            {"certificateId": cert.certificate_id, "certificateArn": cert.arn}
        )

    def register_certificate(self) -> ActionResult:
        certificate_pem = self._get_param("certificatePem")
        ca_certificate_pem = self._get_param("caCertificatePem")
        set_as_active = self._get_bool_param("setAsActive")
        status = self._get_param("status")

        cert = self.iot_backend.register_certificate(
            certificate_pem=certificate_pem,
            ca_certificate_pem=ca_certificate_pem,
            set_as_active=set_as_active,
            status=status,
        )
        return ActionResult(
            {"certificateId": cert.certificate_id, "certificateArn": cert.arn}
        )

    def register_certificate_without_ca(self) -> ActionResult:
        certificate_pem = self._get_param("certificatePem")
        status = self._get_param("status")

        cert = self.iot_backend.register_certificate_without_ca(
            certificate_pem=certificate_pem, status=status
        )
        return ActionResult(
            {"certificateId": cert.certificate_id, "certificateArn": cert.arn}
        )

    def update_ca_certificate(self) -> ActionResult:
        certificate_id = self.path.split("/")[-1]
        new_status = self._get_param("newStatus")
        config = self._get_param("registrationConfig")
        self.iot_backend.update_ca_certificate(
            certificate_id=certificate_id, new_status=new_status, config=config
        )
        return EmptyResult()

    def update_certificate(self) -> ActionResult:
        certificate_id = self._get_param("certificateId")
        new_status = self._get_param("newStatus")
        self.iot_backend.update_certificate(
            certificate_id=certificate_id, new_status=new_status
        )
        return EmptyResult()

    def create_policy(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        policy_document = self._get_param("policyDocument")
        policy = self.iot_backend.create_policy(
            policy_name=policy_name, policy_document=policy_document
        )
        return ActionResult(policy.to_dict_at_creation())

    def list_policies(self) -> ActionResult:
        policies = self.iot_backend.list_policies()

        return ActionResult({"policies": [_.to_dict() for _ in policies]})

    def get_policy(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        policy = self.iot_backend.get_policy(policy_name=policy_name)
        return ActionResult(policy.to_get_dict())

    def delete_policy(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        self.iot_backend.delete_policy(policy_name=policy_name)
        return EmptyResult()

    def create_policy_version(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        policy_document = self._get_param("policyDocument")
        set_as_default = self._get_bool_param("setAsDefault")
        policy_version = self.iot_backend.create_policy_version(
            policy_name, policy_document, set_as_default
        )

        return ActionResult(dict(policy_version.to_dict_at_creation()))

    def set_default_policy_version(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        version_id = self._get_param("policyVersionId")
        self.iot_backend.set_default_policy_version(policy_name, version_id)

        return EmptyResult()

    def get_policy_version(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        version_id = self._get_param("policyVersionId")
        policy_version = self.iot_backend.get_policy_version(policy_name, version_id)
        return ActionResult(dict(policy_version.to_get_dict()))

    def list_policy_versions(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        policiy_versions = self.iot_backend.list_policy_versions(
            policy_name=policy_name
        )

        return ActionResult({"policyVersions": [_.to_dict() for _ in policiy_versions]})

    def delete_policy_version(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        version_id = self._get_param("policyVersionId")
        self.iot_backend.delete_policy_version(policy_name, version_id)

        return EmptyResult()

    def attach_policy(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        target = self._get_param("target")
        self.iot_backend.attach_policy(policy_name=policy_name, target=target)
        return EmptyResult()

    def list_attached_policies(self) -> ActionResult:
        principal = self._get_param("target")
        policies = self.iot_backend.list_attached_policies(target=principal)
        return ActionResult({"policies": [_.to_dict() for _ in policies]})

    def attach_principal_policy(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        principal = self.headers.get("x-amzn-iot-principal")
        self.iot_backend.attach_principal_policy(
            policy_name=policy_name, principal_arn=principal
        )
        return EmptyResult()

    def detach_policy(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        target = self._get_param("target")
        self.iot_backend.detach_policy(policy_name=policy_name, target=target)
        return EmptyResult()

    def detach_principal_policy(self) -> ActionResult:
        policy_name = self._get_param("policyName")
        principal = self.headers.get("x-amzn-iot-principal")
        self.iot_backend.detach_principal_policy(
            policy_name=policy_name, principal_arn=principal
        )
        return EmptyResult()

    def list_principal_policies(self) -> ActionResult:
        principal = self.headers.get("x-amzn-iot-principal")
        policies = self.iot_backend.list_principal_policies(principal_arn=principal)
        return ActionResult({"policies": [_.to_dict() for _ in policies]})

    def list_policy_principals(self) -> ActionResult:
        policy_name = self.headers.get("x-amzn-iot-policy")
        principals = self.iot_backend.list_policy_principals(policy_name=policy_name)
        return ActionResult({"principals": principals})

    def list_targets_for_policy(self) -> ActionResult:
        """https://docs.aws.amazon.com/iot/latest/apireference/API_ListTargetsForPolicy.html"""
        policy_name = self._get_param("policyName")
        principals = self.iot_backend.list_targets_for_policy(policy_name=policy_name)
        return ActionResult({"targets": principals})

    def attach_thing_principal(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        principal = self.headers.get("x-amzn-principal")
        self.iot_backend.attach_thing_principal(
            thing_name=thing_name, principal_arn=principal
        )
        return EmptyResult()

    def detach_thing_principal(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        principal = self.headers.get("x-amzn-principal")
        self.iot_backend.detach_thing_principal(
            thing_name=thing_name, principal_arn=principal
        )
        return EmptyResult()

    def list_principal_things(self) -> ActionResult:
        next_token = self._get_param("nextToken")
        # max_results = self._get_int_param("maxResults")
        principal = self.headers.get("x-amzn-principal")
        things = self.iot_backend.list_principal_things(principal_arn=principal)
        # TODO: implement pagination in the future
        next_token = None
        return ActionResult({"things": things, "nextToken": next_token})

    def list_thing_principals(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        principals = self.iot_backend.list_thing_principals(thing_name=thing_name)
        return ActionResult({"principals": principals})

    def list_thing_principals_v2(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        # Call the new function that was just written in the brain (models.py).
        principals = self.iot_backend.list_thing_principals_v2(thing_name=thing_name)

        # [Key Difference] V2 requires a "list of objects" format, not the original "list of strings".
        # Wrap each principal into a dictionary using a loop.
        thing_principal_objects = [
            {"thingName": thing_name, "principal": p} for p in principals
        ]

        # Return V2 specifications key: "thingPrincipalObjects"
        return ActionResult({"thingPrincipalObjects": thing_principal_objects})

    def describe_thing_group(self) -> ActionResult:
        thing_group_name = unquote(self.path.split("/thing-groups/")[-1])
        thing_group = self.iot_backend.describe_thing_group(
            thing_group_name=thing_group_name
        )
        return ActionResult(thing_group.to_dict())

    def create_thing_group(self) -> ActionResult:
        thing_group_name = unquote(self.path.split("/thing-groups/")[-1])
        parent_group_name = self._get_param("parentGroupName")
        thing_group_properties = self._get_param("thingGroupProperties")
        (
            thing_group_name,
            thing_group_arn,
            thing_group_id,
        ) = self.iot_backend.create_thing_group(
            thing_group_name=thing_group_name,
            parent_group_name=parent_group_name,
            thing_group_properties=thing_group_properties,
        )
        return ActionResult(
            {
                "thingGroupName": thing_group_name,
                "thingGroupArn": thing_group_arn,
                "thingGroupId": thing_group_id,
            }
        )

    def delete_thing_group(self) -> ActionResult:
        thing_group_name = unquote(self.path.split("/thing-groups/")[-1])
        self.iot_backend.delete_thing_group(thing_group_name=thing_group_name)
        return EmptyResult()

    def list_thing_groups(self) -> ActionResult:
        # next_token = self._get_param("nextToken")
        # max_results = self._get_int_param("maxResults")
        parent_group = self._get_param("parentGroup")
        name_prefix_filter = self._get_param("namePrefixFilter")
        recursive = self._get_bool_param("recursive")
        thing_groups = self.iot_backend.list_thing_groups(
            parent_group=parent_group,
            name_prefix_filter=name_prefix_filter,
            recursive=recursive,
        )
        next_token = None
        rets = [
            {"groupName": _.thing_group_name, "groupArn": _.arn} for _ in thing_groups
        ]
        # TODO: implement pagination in the future
        return ActionResult({"thingGroups": rets, "nextToken": next_token})

    def update_thing_group(self) -> ActionResult:
        thing_group_name = unquote(self.path.split("/thing-groups/")[-1])
        thing_group_properties = self._get_param("thingGroupProperties")
        expected_version = self._get_param("expectedVersion")
        version = self.iot_backend.update_thing_group(
            thing_group_name=thing_group_name,
            thing_group_properties=thing_group_properties,
            expected_version=expected_version,
        )
        return ActionResult({"version": version})

    def add_thing_to_thing_group(self) -> ActionResult:
        thing_group_name = self._get_param("thingGroupName")
        thing_group_arn = self._get_param("thingGroupArn")
        thing_name = self._get_param("thingName")
        thing_arn = self._get_param("thingArn")
        self.iot_backend.add_thing_to_thing_group(
            thing_group_name=thing_group_name,
            thing_group_arn=thing_group_arn,
            thing_name=thing_name,
            thing_arn=thing_arn,
        )
        return EmptyResult()

    def remove_thing_from_thing_group(self) -> ActionResult:
        thing_group_name = self._get_param("thingGroupName")
        thing_group_arn = self._get_param("thingGroupArn")
        thing_name = self._get_param("thingName")
        thing_arn = self._get_param("thingArn")
        self.iot_backend.remove_thing_from_thing_group(
            thing_group_name=thing_group_name,
            thing_group_arn=thing_group_arn,
            thing_name=thing_name,
            thing_arn=thing_arn,
        )
        return EmptyResult()

    def list_things_in_thing_group(self) -> ActionResult:
        thing_group_name = self._get_param("thingGroupName")
        things = self.iot_backend.list_things_in_thing_group(
            thing_group_name=thing_group_name
        )
        next_token = None
        thing_names = [_.thing_name for _ in things]
        return ActionResult({"things": thing_names, "nextToken": next_token})

    def list_thing_groups_for_thing(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        # next_token = self._get_param("nextToken")
        # max_results = self._get_int_param("maxResults")
        thing_groups = self.iot_backend.list_thing_groups_for_thing(
            thing_name=thing_name
        )
        next_token = None
        return ActionResult({"thingGroups": thing_groups, "nextToken": next_token})

    def update_thing_groups_for_thing(self) -> ActionResult:
        thing_name = self._get_param("thingName")
        thing_groups_to_add = self._get_param("thingGroupsToAdd") or []
        thing_groups_to_remove = self._get_param("thingGroupsToRemove") or []
        self.iot_backend.update_thing_groups_for_thing(
            thing_name=thing_name,
            thing_groups_to_add=thing_groups_to_add,
            thing_groups_to_remove=thing_groups_to_remove,
        )
        return EmptyResult()

    def list_topic_rules(self) -> ActionResult:
        return ActionResult({"rules": self.iot_backend.list_topic_rules()})

    def get_topic_rule(self) -> ActionResult:
        return ActionResult(
            self.iot_backend.get_topic_rule(rule_name=self._get_param("ruleName"))
        )

    def create_topic_rule(self) -> ActionResult:
        self.iot_backend.create_topic_rule(
            rule_name=self._get_param("ruleName"),
            description=self._get_param("description"),
            rule_disabled=self._get_param("ruleDisabled"),
            actions=self._get_param("actions"),
            error_action=self._get_param("errorAction"),
            sql=self._get_param("sql"),
            aws_iot_sql_version=self._get_param("awsIotSqlVersion"),
        )
        return EmptyResult()

    def replace_topic_rule(self) -> ActionResult:
        self.iot_backend.replace_topic_rule(
            rule_name=self._get_param("ruleName"),
            description=self._get_param("description"),
            rule_disabled=self._get_param("ruleDisabled"),
            actions=self._get_param("actions"),
            error_action=self._get_param("errorAction"),
            sql=self._get_param("sql"),
            aws_iot_sql_version=self._get_param("awsIotSqlVersion"),
        )
        return EmptyResult()

    def delete_topic_rule(self) -> ActionResult:
        self.iot_backend.delete_topic_rule(rule_name=self._get_param("ruleName"))
        return EmptyResult()

    def enable_topic_rule(self) -> ActionResult:
        self.iot_backend.enable_topic_rule(rule_name=self._get_param("ruleName"))
        return EmptyResult()

    def disable_topic_rule(self) -> ActionResult:
        self.iot_backend.disable_topic_rule(rule_name=self._get_param("ruleName"))
        return EmptyResult()

    def create_domain_configuration(self) -> ActionResult:
        domain_configuration = self.iot_backend.create_domain_configuration(
            domain_configuration_name=self._get_param("domainConfigurationName"),
            domain_name=self._get_param("domainName"),
            server_certificate_arns=self._get_param("serverCertificateArns"),
            authorizer_config=self._get_param("authorizerConfig"),
            service_type=self._get_param("serviceType"),
        )
        return ActionResult(domain_configuration.to_dict())

    def delete_domain_configuration(self) -> ActionResult:
        self.iot_backend.delete_domain_configuration(
            domain_configuration_name=self._get_param("domainConfigurationName")
        )
        return EmptyResult()

    def describe_domain_configuration(self) -> ActionResult:
        domain_configuration = self.iot_backend.describe_domain_configuration(
            domain_configuration_name=self._get_param("domainConfigurationName")
        )
        return ActionResult(domain_configuration.to_description_dict())

    def list_domain_configurations(self) -> ActionResult:
        return ActionResult(
            {"domainConfigurations": self.iot_backend.list_domain_configurations()}
        )

    def update_domain_configuration(self) -> ActionResult:
        domain_configuration = self.iot_backend.update_domain_configuration(
            domain_configuration_name=self._get_param("domainConfigurationName"),
            authorizer_config=self._get_param("authorizerConfig"),
            domain_configuration_status=self._get_param("domainConfigurationStatus"),
            remove_authorizer_config=self._get_bool_param("removeAuthorizerConfig"),
        )
        return ActionResult(domain_configuration.to_dict())

    def search_index(self) -> ActionResult:
        query = self._get_param("queryString")
        things = self.iot_backend.search_index(query)
        return ActionResult({"things": things, "thingGroups": []})

    def create_role_alias(self) -> ActionResult:
        role_alias_name = self._get_param("roleAlias")
        role_arn = self._get_param("roleArn")
        credential_duration_seconds = self._get_int_param(
            "credentialDurationSeconds", 3600
        )
        created_role_alias = self.iot_backend.create_role_alias(
            role_alias_name=role_alias_name,
            role_arn=role_arn,
            credential_duration_seconds=credential_duration_seconds,
        )
        return ActionResult(
            {
                "roleAlias": created_role_alias.role_alias,
                "roleAliasArn": created_role_alias.arn,
            }
        )

    def list_role_aliases(self) -> ActionResult:
        # page_size = self._get_int_param("pageSize")
        # marker = self._get_param("marker")
        # ascending_order = self._get_param("ascendingOrder")
        return ActionResult(
            {
                "roleAliases": [
                    _.role_alias for _ in self.iot_backend.list_role_aliases()
                ]
            }
        )

    def describe_role_alias(self) -> ActionResult:
        role_alias_name = self._get_param("roleAlias")
        role_alias = self.iot_backend.describe_role_alias(
            role_alias_name=role_alias_name
        )
        return ActionResult({"roleAliasDescription": role_alias.to_dict()})

    def update_role_alias(self) -> ActionResult:
        role_alias_name = self._get_param("roleAlias")
        role_arn = self._get_param("roleArn", None)
        credential_duration_seconds = self._get_int_param(
            "credentialDurationSeconds", 0
        )

        role_alias = self.iot_backend.update_role_alias(
            role_alias_name=role_alias_name,
            role_arn=role_arn,
            credential_duration_seconds=credential_duration_seconds,
        )

        return ActionResult(
            {"roleAlias": role_alias.role_alias, "roleAliasArn": role_alias.arn}
        )

    def delete_role_alias(self) -> ActionResult:
        role_alias_name = self._get_param("roleAlias")
        self.iot_backend.delete_role_alias(role_alias_name=role_alias_name)
        return EmptyResult()

    def get_indexing_configuration(self) -> ActionResult:
        return ActionResult(self.iot_backend.get_indexing_configuration())

    def update_indexing_configuration(self) -> ActionResult:
        self.iot_backend.update_indexing_configuration(
            self._get_param("thingIndexingConfiguration", {}),
            self._get_param("thingGroupIndexingConfiguration", {}),
        )
        return EmptyResult()

    def create_job_template(self) -> ActionResult:
        job_template = self.iot_backend.create_job_template(
            job_template_id=self._get_param("jobTemplateId"),
            description=self._get_param("description"),
            document_source=self._get_param("documentSource"),
            document=self._get_param("document"),
            presigned_url_config=self._get_param("presignedUrlConfig"),
            job_executions_rollout_config=self._get_param("jobExecutionsRolloutConfig"),
            abort_config=self._get_param("abortConfig"),
            job_execution_retry_config=self._get_param("jobExecutionsRetryConfig"),
            timeout_config=self._get_param("timeoutConfig"),
        )

        return ActionResult(
            {
                "jobTemplateArn": job_template.job_template_arn,
                "jobTemplateId": job_template.job_template_id,
            }
        )

    def list_job_templates(self) -> ActionResult:
        max_results = self._get_int_param("maxResults", 50)
        current_next_token = self._get_param("nextToken")
        job_templates, future_next_token = self.iot_backend.list_job_templates(
            max_results=max_results, next_token=current_next_token
        )

        return ActionResult(
            {"jobTemplates": job_templates, "nextToken": future_next_token}
        )

    def delete_job_template(self) -> ActionResult:
        job_template_id = self._get_param("jobTemplateId")

        self.iot_backend.delete_job_template(job_template_id=job_template_id)

        return EmptyResult()

    def describe_job_template(self) -> ActionResult:
        job_template_id = self._get_param("jobTemplateId")
        job_template = self.iot_backend.describe_job_template(job_template_id)

        return ActionResult(
            {
                "jobTemplateArn": job_template.job_template_arn,
                "jobTemplateId": job_template.job_template_id,
                "description": job_template.description,
                "documentSource": job_template.document_source,
                "document": job_template.document,
                "createdAt": job_template.created_at,
                "presignedUrlConfig": job_template.presigned_url_config,
                "jobExecutionsRolloutConfig": job_template.job_executions_rollout_config,
                "abortConfig": job_template.abort_config,
                "timeoutConfig": job_template.timeout_config,
                "jobExecutionsRetryConfig": job_template.job_execution_retry_config,
            }
        )

    def create_billing_group(self) -> ActionResult:
        billing_group_name = self._get_param("billingGroupName")
        billing_group_properties = self._get_param("billingGroupProperties")
        billing_group = self.iot_backend.create_billing_group(
            billing_group_name=billing_group_name,
            billing_group_properties=billing_group_properties,
        )
        return ActionResult(billing_group.to_dict())

    def describe_billing_group(self) -> ActionResult:
        billing_group_name = self._get_param("billingGroupName")
        billing_group = self.iot_backend.describe_billing_group(
            billing_group_name=billing_group_name
        )
        return ActionResult(billing_group.to_description_dict())

    def delete_billing_group(self) -> ActionResult:
        billing_group_name = self._get_param("billingGroupName")

        self.iot_backend.delete_billing_group(billing_group_name=billing_group_name)
        return EmptyResult()

    def list_billing_groups(self) -> ActionResult:
        name_prefix_filter = self._get_param("namePrefixFilter")
        max_results = self._get_int_param("maxResults", 100)
        token = self._get_param("nextToken")

        billing_groups, next_token = self.iot_backend.list_billing_groups(
            name_prefix_filter=name_prefix_filter, max_results=max_results, token=token
        )

        return ActionResult({"billingGroups": billing_groups, "nextToken": next_token})

    def update_billing_group(self) -> ActionResult:
        billing_group_name = self._get_param("billingGroupName")
        billing_group_properties = self._get_param("billingGroupProperties")
        expected_version = self._get_param("expectedVersion")

        version = self.iot_backend.update_billing_group(
            billing_group_name=billing_group_name,
            billing_group_properties=billing_group_properties,
            expected_version=expected_version,
        )

        return ActionResult({"version": version})

    def add_thing_to_billing_group(self) -> ActionResult:
        self.iot_backend.add_thing_to_billing_group(
            billing_group_name=self._get_param("billingGroupName"),
            billing_group_arn=self._get_param("billingGroupArn"),
            thing_name=self._get_param("thingName"),
            thing_arn=self._get_param("thingArn"),
        )

        return EmptyResult()

    def remove_thing_from_billing_group(self) -> ActionResult:
        self.iot_backend.remove_thing_from_billing_group(
            billing_group_name=self._get_param("billingGroupName"),
            billing_group_arn=self._get_param("billingGroupArn"),
            thing_name=self._get_param("thingName"),
            thing_arn=self._get_param("thingArn"),
        )

        return EmptyResult()

    def list_things_in_billing_group(self) -> ActionResult:
        billing_group_name = self._get_param("billingGroupName")
        max_results = self._get_int_param("maxResults", 100)
        token = self._get_param("nextToken")
        things, next_token = self.iot_backend.list_things_in_billing_group(
            billing_group_name=billing_group_name,
            max_results=max_results,
            token=token,
        )
        return ActionResult(
            {"things": [thing.thing_name for thing in things], "nextToken": next_token}
        )

    # --- Security Profiles ---

    def create_security_profile(self) -> ActionResult:
        security_profile_name = self._get_param("securityProfileName")
        profile = self.iot_backend.create_security_profile(
            security_profile_name=security_profile_name,
            security_profile_description=self._get_param("securityProfileDescription"),
            behaviors=self._get_param("behaviors"),
            alert_targets=self._get_param("alertTargets"),
            additional_metrics_to_retain_v2=self._get_param(
                "additionalMetricsToRetainV2"
            ),
            tags=self._get_param("tags"),
        )
        return ActionResult(profile.to_dict())

    def describe_security_profile(self) -> ActionResult:
        security_profile_name = self._get_param("securityProfileName")
        profile = self.iot_backend.describe_security_profile(
            security_profile_name=security_profile_name
        )
        return ActionResult(profile.to_description_dict())

    def update_security_profile(self) -> ActionResult:
        security_profile_name = self._get_param("securityProfileName")
        profile = self.iot_backend.update_security_profile(
            security_profile_name=security_profile_name,
            security_profile_description=self._get_param("securityProfileDescription"),
            behaviors=self._get_param("behaviors"),
            alert_targets=self._get_param("alertTargets"),
            additional_metrics_to_retain_v2=self._get_param(
                "additionalMetricsToRetainV2"
            ),
        )
        return ActionResult(profile.to_description_dict())

    def delete_security_profile(self) -> ActionResult:
        security_profile_name = self._get_param("securityProfileName")
        self.iot_backend.delete_security_profile(
            security_profile_name=security_profile_name
        )
        return EmptyResult()

    def list_security_profiles(self) -> ActionResult:
        profiles = self.iot_backend.list_security_profiles()
        return ActionResult(
            {"securityProfileIdentifiers": [p.to_list_dict() for p in profiles]}
        )

    def attach_security_profile(self) -> ActionResult:
        security_profile_name = self._get_param("securityProfileName")
        security_profile_target_arn = self._get_param("securityProfileTargetArn")
        self.iot_backend.attach_security_profile(
            security_profile_name=security_profile_name,
            security_profile_target_arn=security_profile_target_arn,
        )
        return EmptyResult()

    def detach_security_profile(self) -> ActionResult:
        security_profile_name = self._get_param("securityProfileName")
        security_profile_target_arn = self._get_param("securityProfileTargetArn")
        self.iot_backend.detach_security_profile(
            security_profile_name=security_profile_name,
            security_profile_target_arn=security_profile_target_arn,
        )
        return EmptyResult()

    def list_targets_for_security_profile(self) -> ActionResult:
        security_profile_name = self._get_param("securityProfileName")
        targets = self.iot_backend.list_targets_for_security_profile(
            security_profile_name=security_profile_name
        )
        return ActionResult({"securityProfileTargets": targets})

    def list_security_profiles_for_target(self) -> ActionResult:
        security_profile_target_arn = self._get_param("securityProfileTargetArn")
        profiles = self.iot_backend.list_security_profiles_for_target(
            security_profile_target_arn=security_profile_target_arn
        )
        return ActionResult(
            {
                "securityProfileTargetMappings": [
                    {
                        "securityProfileIdentifier": p,
                        "target": {"arn": security_profile_target_arn},
                    }
                    for p in profiles
                ]
            }
        )

    # --- Authorizers ---

    def create_authorizer(self) -> ActionResult:
        authorizer_name = self._get_param("authorizerName")
        authorizer = self.iot_backend.create_authorizer(
            authorizer_name=authorizer_name,
            authorizer_function_arn=self._get_param("authorizerFunctionArn"),
            token_key_name=self._get_param("tokenKeyName"),
            token_signing_public_keys=self._get_param("tokenSigningPublicKeys"),
            status=self._get_param("status"),
            signing_disabled=self._get_bool_param("signingDisabled"),
            enable_caching_for_http=self._get_bool_param("enableCachingForHttp"),
        )
        return ActionResult(
            {
                "authorizerName": authorizer.authorizer_name,
                "authorizerArn": authorizer.arn,
            }
        )

    def describe_authorizer(self) -> ActionResult:
        authorizer_name = self._get_param("authorizerName")
        authorizer = self.iot_backend.describe_authorizer(
            authorizer_name=authorizer_name
        )
        return ActionResult({"authorizerDescription": authorizer.to_description_dict()})

    def update_authorizer(self) -> ActionResult:
        authorizer_name = self._get_param("authorizerName")
        authorizer = self.iot_backend.update_authorizer(
            authorizer_name=authorizer_name,
            authorizer_function_arn=self._get_param("authorizerFunctionArn"),
            token_key_name=self._get_param("tokenKeyName"),
            token_signing_public_keys=self._get_param("tokenSigningPublicKeys"),
            status=self._get_param("status"),
            enable_caching_for_http=self._get_bool_param("enableCachingForHttp"),
        )
        return ActionResult(
            {
                "authorizerName": authorizer.authorizer_name,
                "authorizerArn": authorizer.arn,
            }
        )

    def delete_authorizer(self) -> ActionResult:
        authorizer_name = self._get_param("authorizerName")
        self.iot_backend.delete_authorizer(authorizer_name=authorizer_name)
        return EmptyResult()

    def list_authorizers(self) -> ActionResult:
        authorizers = self.iot_backend.list_authorizers()
        return ActionResult(
            {"authorizers": [a.to_description_dict() for a in authorizers]}
        )

    def set_default_authorizer(self) -> ActionResult:
        authorizer_name = self._get_param("authorizerName")
        authorizer = self.iot_backend.set_default_authorizer(
            authorizer_name=authorizer_name
        )
        return ActionResult(
            {
                "authorizerName": authorizer.authorizer_name,
                "authorizerArn": authorizer.arn,
            }
        )

    def describe_default_authorizer(self) -> ActionResult:
        authorizer = self.iot_backend.describe_default_authorizer()
        return ActionResult({"authorizerDescription": authorizer.to_description_dict()})

    # --- Provisioning Templates ---

    def create_provisioning_template(self) -> ActionResult:
        template_name = self._get_param("templateName")
        template = self.iot_backend.create_provisioning_template(
            template_name=template_name,
            description=self._get_param("description"),
            template_body=self._get_param("templateBody"),
            enabled=self._get_param("enabled"),
            provisioning_role_arn=self._get_param("provisioningRoleArn"),
            pre_provisioning_hook=self._get_param("preProvisioningHook"),
            tags=self._get_param("tags"),
            template_type=self._get_param("type"),
        )
        return ActionResult(
            {
                "templateName": template.template_name,
                "templateArn": template.arn,
                "defaultVersionId": template.default_version_id,
            }
        )

    def describe_provisioning_template(self) -> ActionResult:
        template_name = self._get_param("templateName")
        template = self.iot_backend.describe_provisioning_template(
            template_name=template_name
        )
        return ActionResult(template.to_description_dict())

    def update_provisioning_template(self) -> ActionResult:
        template_name = self._get_param("templateName")
        self.iot_backend.update_provisioning_template(
            template_name=template_name,
            description=self._get_param("description"),
            enabled=self._get_param("enabled"),
            provisioning_role_arn=self._get_param("provisioningRoleArn"),
            pre_provisioning_hook=self._get_param("preProvisioningHook"),
            default_version_id=self._get_param("defaultVersionId"),
        )
        return EmptyResult()

    def delete_provisioning_template(self) -> ActionResult:
        template_name = self._get_param("templateName")
        self.iot_backend.delete_provisioning_template(template_name=template_name)
        return EmptyResult()

    def list_provisioning_templates(self) -> ActionResult:
        templates = self.iot_backend.list_provisioning_templates()
        return ActionResult({"templates": [t.to_dict() for t in templates]})

    # --- Dimensions ---

    def create_dimension(self) -> ActionResult:
        name = self._get_param("name")
        dimension = self.iot_backend.create_dimension(
            name=name,
            dimension_type=self._get_param("type"),
            string_values=self._get_param("stringValues"),
            tags=self._get_param("tags"),
        )
        return ActionResult({"name": dimension.name, "arn": dimension.arn})

    def describe_dimension(self) -> ActionResult:
        name = self._get_param("name")
        dimension = self.iot_backend.describe_dimension(name=name)
        return ActionResult(dimension.to_description_dict())

    def update_dimension(self) -> ActionResult:
        name = self._get_param("name")
        dimension = self.iot_backend.update_dimension(
            name=name,
            string_values=self._get_param("stringValues"),
        )
        return ActionResult(dimension.to_description_dict())

    def delete_dimension(self) -> ActionResult:
        name = self._get_param("name")
        self.iot_backend.delete_dimension(name=name)
        return EmptyResult()

    def list_dimensions(self) -> ActionResult:
        dimension_names = self.iot_backend.list_dimensions()
        return ActionResult({"dimensionNames": dimension_names})

    # --- Custom Metrics ---

    def create_custom_metric(self) -> ActionResult:
        metric_name = self._get_param("metricName")
        metric = self.iot_backend.create_custom_metric(
            metric_name=metric_name,
            display_name=self._get_param("displayName"),
            metric_type=self._get_param("metricType"),
            tags=self._get_param("tags"),
        )
        return ActionResult({"metricName": metric.metric_name, "metricArn": metric.arn})

    def describe_custom_metric(self) -> ActionResult:
        metric_name = self._get_param("metricName")
        metric = self.iot_backend.describe_custom_metric(metric_name=metric_name)
        return ActionResult(metric.to_description_dict())

    def update_custom_metric(self) -> ActionResult:
        metric_name = self._get_param("metricName")
        metric = self.iot_backend.update_custom_metric(
            metric_name=metric_name,
            display_name=self._get_param("displayName"),
        )
        return ActionResult(metric.to_description_dict())

    def delete_custom_metric(self) -> ActionResult:
        metric_name = self._get_param("metricName")
        self.iot_backend.delete_custom_metric(metric_name=metric_name)
        return EmptyResult()

    def list_custom_metrics(self) -> ActionResult:
        metric_names = self.iot_backend.list_custom_metrics()
        return ActionResult({"metricNames": metric_names})

    # --- Fleet Metrics ---

    def create_fleet_metric(self) -> ActionResult:
        metric_name = self._get_param("metricName")
        fleet_metric = self.iot_backend.create_fleet_metric(
            metric_name=metric_name,
            query_string=self._get_param("queryString"),
            aggregation_type=self._get_param("aggregationType"),
            period=self._get_int_param("period"),
            aggregation_field=self._get_param("aggregationField"),
            description=self._get_param("description"),
            query_version=self._get_param("queryVersion"),
            index_name=self._get_param("indexName"),
            unit=self._get_param("unit"),
            tags=self._get_param("tags"),
        )
        return ActionResult(
            {"metricName": fleet_metric.metric_name, "metricArn": fleet_metric.arn}
        )

    def describe_fleet_metric(self) -> ActionResult:
        metric_name = self._get_param("metricName")
        fleet_metric = self.iot_backend.describe_fleet_metric(metric_name=metric_name)
        return ActionResult(fleet_metric.to_description_dict())

    def update_fleet_metric(self) -> ActionResult:
        metric_name = self._get_param("metricName")
        self.iot_backend.update_fleet_metric(
            metric_name=metric_name,
            query_string=self._get_param("queryString"),
            aggregation_type=self._get_param("aggregationType"),
            period=self._get_int_param("period"),
            aggregation_field=self._get_param("aggregationField"),
            description=self._get_param("description"),
            query_version=self._get_param("queryVersion"),
            index_name=self._get_param("indexName"),
            unit=self._get_param("unit"),
        )
        return EmptyResult()

    def delete_fleet_metric(self) -> ActionResult:
        metric_name = self._get_param("metricName")
        self.iot_backend.delete_fleet_metric(metric_name=metric_name)
        return EmptyResult()

    def list_fleet_metrics(self) -> ActionResult:
        fleet_metrics = self.iot_backend.list_fleet_metrics()
        return ActionResult({"fleetMetrics": [fm.to_dict() for fm in fleet_metrics]})

    def get_statistics(self) -> ActionResult:
        index_name = self._get_param("indexName")
        query_string = self._get_param("queryString")
        aggregation_field = self._get_param("aggregationField")
        query_version = self._get_param("queryVersion")
        statistics = self.iot_backend.get_statistics(
            index_name=index_name,
            query_string=query_string,
            aggregation_field=aggregation_field,
            query_version=query_version,
        )
        return ActionResult({"statistics": statistics})

    def get_topic_rule_destination(self) -> ActionResult:
        arn = self._get_param("arn")
        destination = self.iot_backend.get_topic_rule_destination(arn=arn)
        return ActionResult({"topicRuleDestination": destination})

    def get_v2_logging_options(self) -> ActionResult:
        options = self.iot_backend.get_v2_logging_options()
        return ActionResult(options)

    def list_audit_findings(self) -> ActionResult:
        result = self.iot_backend.list_audit_findings(
            task_id=self._get_param("taskId"),
            check_name=self._get_param("checkName"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_audit_mitigation_actions_executions(self) -> ActionResult:
        result = self.iot_backend.list_audit_mitigation_actions_executions(
            task_id=self._get_param("taskId"),
            finding_id=self._get_param("findingId"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_audit_mitigation_actions_tasks(self) -> ActionResult:
        result = self.iot_backend.list_audit_mitigation_actions_tasks(
            start_time=self._get_param("startTime"),
            end_time=self._get_param("endTime"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_audit_suppressions(self) -> ActionResult:
        result = self.iot_backend.list_audit_suppressions(
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_audit_tasks(self) -> ActionResult:
        result = self.iot_backend.list_audit_tasks(
            start_time=self._get_param("startTime"),
            end_time=self._get_param("endTime"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def start_thing_registration_task(self) -> ActionResult:
        template_body = self._get_param("templateBody")
        input_file_bucket = self._get_param("inputFileBucket")
        input_file_key = self._get_param("inputFileKey")
        role_arn = self._get_param("roleArn")
        task_id = self.iot_backend.start_thing_registration_task(
            template_body=template_body,
            input_file_bucket=input_file_bucket,
            input_file_key=input_file_key,
            role_arn=role_arn,
        )
        return ActionResult({"taskId": task_id})

    def describe_thing_registration_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        result = self.iot_backend.describe_thing_registration_task(task_id=task_id)
        return ActionResult(result)

    def stop_thing_registration_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        self.iot_backend.stop_thing_registration_task(task_id=task_id)
        return EmptyResult()

    def list_detect_mitigation_actions_executions(self) -> ActionResult:
        result = self.iot_backend.list_detect_mitigation_actions_executions(
            task_id=self._get_param("taskId"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_detect_mitigation_actions_tasks(self) -> ActionResult:
        result = self.iot_backend.list_detect_mitigation_actions_tasks(
            start_time=self._get_param("startTime"),
            end_time=self._get_param("endTime"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    # --- Streams ---

    def create_stream(self) -> ActionResult:
        stream_id = self._get_param("streamId")
        description = self._get_param("description")
        files = self._get_param("files")
        role_arn = self._get_param("roleArn")
        tags = self._get_param("tags")
        stream = self.iot_backend.create_stream(
            stream_id=stream_id,
            description=description,
            files=files,
            role_arn=role_arn,
            tags=tags,
        )
        return ActionResult(
            {
                "streamId": stream.stream_id,
                "streamArn": stream.arn,
                "streamVersion": stream.stream_version,
                "description": stream.description,
            }
        )

    def describe_stream(self) -> ActionResult:
        stream_id = self._get_param("streamId")
        stream = self.iot_backend.describe_stream(stream_id=stream_id)
        return ActionResult(stream.to_description_dict())

    def list_streams(self) -> ActionResult:
        streams = self.iot_backend.list_streams()
        return ActionResult({"streams": [s.to_dict() for s in streams]})

    def delete_stream(self) -> ActionResult:
        stream_id = self._get_param("streamId")
        self.iot_backend.delete_stream(stream_id=stream_id)
        return EmptyResult()

    def update_stream(self) -> ActionResult:
        stream_id = self._get_param("streamId")
        description = self._get_param("description")
        files = self._get_param("files")
        role_arn = self._get_param("roleArn")
        stream = self.iot_backend.update_stream(
            stream_id=stream_id,
            description=description,
            files=files,
            role_arn=role_arn,
        )
        return ActionResult(
            {
                "streamId": stream.stream_id,
                "streamArn": stream.arn,
                "streamVersion": stream.stream_version,
                "description": stream.description,
            }
        )

    # --- Mitigation Actions ---

    def create_mitigation_action(self) -> ActionResult:
        action_name = self._get_param("actionName")
        role_arn = self._get_param("roleArn")
        action_params = self._get_param("actionParams")
        tags = self._get_param("tags")
        action = self.iot_backend.create_mitigation_action(
            action_name=action_name,
            role_arn=role_arn,
            action_params=action_params,
            tags=tags,
        )
        return ActionResult(
            {
                "actionArn": action.arn,
                "actionId": action.action_id,
            }
        )

    def describe_mitigation_action(self) -> ActionResult:
        action_name = self._get_param("actionName")
        action = self.iot_backend.describe_mitigation_action(action_name=action_name)
        return ActionResult(action.to_description_dict())

    def list_mitigation_actions(self) -> ActionResult:
        actions = self.iot_backend.list_mitigation_actions()
        return ActionResult({"actionIdentifiers": [a.to_dict() for a in actions]})

    def delete_mitigation_action(self) -> ActionResult:
        action_name = self._get_param("actionName")
        self.iot_backend.delete_mitigation_action(action_name=action_name)
        return EmptyResult()

    def update_mitigation_action(self) -> ActionResult:
        action_name = self._get_param("actionName")
        role_arn = self._get_param("roleArn")
        action_params = self._get_param("actionParams")
        action = self.iot_backend.update_mitigation_action(
            action_name=action_name,
            role_arn=role_arn,
            action_params=action_params,
        )
        return ActionResult({"actionArn": action.arn, "actionId": action.action_id})

    # --- Scheduled Audits ---

    def create_scheduled_audit(self) -> ActionResult:
        scheduled_audit_name = self._get_param("scheduledAuditName")
        frequency = self._get_param("frequency")
        day_of_month = self._get_param("dayOfMonth")
        day_of_week = self._get_param("dayOfWeek")
        target_check_names = self._get_param("targetCheckNames")
        tags = self._get_param("tags")
        audit = self.iot_backend.create_scheduled_audit(
            scheduled_audit_name=scheduled_audit_name,
            frequency=frequency,
            day_of_month=day_of_month,
            day_of_week=day_of_week,
            target_check_names=target_check_names,
            tags=tags,
        )
        return ActionResult({"scheduledAuditArn": audit.arn})

    def describe_scheduled_audit(self) -> ActionResult:
        scheduled_audit_name = self._get_param("scheduledAuditName")
        audit = self.iot_backend.describe_scheduled_audit(
            scheduled_audit_name=scheduled_audit_name
        )
        return ActionResult(audit.to_description_dict())

    def list_scheduled_audits(self) -> ActionResult:
        audits = self.iot_backend.list_scheduled_audits()
        return ActionResult({"scheduledAudits": [a.to_dict() for a in audits]})

    def delete_scheduled_audit(self) -> ActionResult:
        scheduled_audit_name = self._get_param("scheduledAuditName")
        self.iot_backend.delete_scheduled_audit(
            scheduled_audit_name=scheduled_audit_name
        )
        return EmptyResult()

    def update_scheduled_audit(self) -> ActionResult:
        scheduled_audit_name = self._get_param("scheduledAuditName")
        audit = self.iot_backend.update_scheduled_audit(
            scheduled_audit_name=scheduled_audit_name,
            frequency=self._get_param("frequency"),
            day_of_month=self._get_param("dayOfMonth"),
            day_of_week=self._get_param("dayOfWeek"),
            target_check_names=self._get_param("targetCheckNames"),
        )
        return ActionResult({"scheduledAuditArn": audit.arn})

    # --- OTA Updates ---

    def create_ota_update(self) -> ActionResult:
        ota_update_id = self._get_param("otaUpdateId")
        description = self._get_param("description")
        targets = self._get_param("targets")
        protocols = self._get_param("protocols")
        target_selection = self._get_param("targetSelection")
        files = self._get_param("files")
        role_arn = self._get_param("roleArn")
        tags = self._get_param("tags")
        ota = self.iot_backend.create_ota_update(
            ota_update_id=ota_update_id,
            description=description,
            targets=targets,
            protocols=protocols,
            target_selection=target_selection,
            files=files,
            role_arn=role_arn,
            tags=tags,
        )
        return ActionResult(
            {
                "otaUpdateId": ota.ota_update_id,
                "otaUpdateArn": ota.arn,
                "otaUpdateStatus": ota.ota_update_status,
            }
        )

    def list_ota_updates(self) -> ActionResult:
        updates = self.iot_backend.list_ota_updates()
        return ActionResult({"otaUpdates": [u.to_dict() for u in updates]})

    def delete_ota_update(self) -> ActionResult:
        ota_update_id = self._get_param("otaUpdateId")
        self.iot_backend.delete_ota_update(ota_update_id=ota_update_id)
        return EmptyResult()

    def get_ota_update(self) -> ActionResult:
        ota_update_id = self._get_param("otaUpdateId")
        ota = self.iot_backend.describe_ota_update(ota_update_id=ota_update_id)
        return ActionResult({"otaUpdateInfo": ota.to_description_dict()})

    # --- CA Certificates listing ---

    def list_ca_certificates(self) -> ActionResult:
        certs = self.iot_backend.list_ca_certificates()
        return ActionResult({"certificates": [c.to_dict() for c in certs]})

    # --- Provisioning Template Versions ---

    def create_provisioning_template_version(self) -> ActionResult:
        template_name = self._get_param("templateName")
        template_body = self._get_param("templateBody")
        set_as_default = self._get_bool_param("setAsDefault") or False
        result = self.iot_backend.create_provisioning_template_version(
            template_name=template_name,
            template_body=template_body,
            set_as_default=set_as_default,
        )
        return ActionResult(result)

    def list_provisioning_template_versions(self) -> ActionResult:
        template_name = self._get_param("templateName")
        versions = self.iot_backend.list_provisioning_template_versions(
            template_name=template_name
        )
        return ActionResult({"versions": versions})

    def describe_provisioning_template_version(self) -> ActionResult:
        template_name = self._get_param("templateName")
        version_id = self._get_int_param("versionId") or 1
        result = self.iot_backend.describe_provisioning_template_version(
            template_name=template_name, version_id=version_id
        )
        return ActionResult(result)

    def delete_provisioning_template_version(self) -> ActionResult:
        template_name = self._get_param("templateName")
        version_id = self._get_int_param("versionId") or 1
        self.iot_backend.delete_provisioning_template_version(
            template_name=template_name, version_id=version_id
        )
        return EmptyResult()

    # --- Account Audit Configuration ---

    def describe_account_audit_configuration(self) -> ActionResult:
        result = self.iot_backend.describe_account_audit_configuration()
        return ActionResult(result)

    def update_account_audit_configuration(self) -> ActionResult:
        role_arn = self._get_param("roleArn")
        audit_notification_target_configurations = self._get_param(
            "auditNotificationTargetConfigurations"
        )
        audit_check_configurations = self._get_param("auditCheckConfigurations")
        self.iot_backend.update_account_audit_configuration(
            role_arn=role_arn,
            audit_notification_target_configurations=audit_notification_target_configurations,
            audit_check_configurations=audit_check_configurations,
        )
        return EmptyResult()

    # --- Describe stubs for audit/detect resources ---

    def describe_audit_finding(self) -> ActionResult:
        finding_id = self._get_param("findingId")
        result = self.iot_backend.describe_audit_finding(finding_id=finding_id)
        return ActionResult(result)

    def describe_audit_mitigation_actions_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        result = self.iot_backend.describe_audit_mitigation_actions_task(
            task_id=task_id
        )
        return ActionResult(result)

    def describe_audit_suppression(self) -> ActionResult:
        check_name = self._get_param("checkName")
        resource_identifier = self._get_param("resourceIdentifier")
        result = self.iot_backend.describe_audit_suppression(
            check_name=check_name, resource_identifier=resource_identifier
        )
        return ActionResult(result)

    def describe_audit_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        result = self.iot_backend.describe_audit_task(task_id=task_id)
        return ActionResult(result)

    def start_detect_mitigation_actions_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        target = self._get_param("target")
        actions = self._get_param("actions")
        result_task_id = self.iot_backend.start_detect_mitigation_actions_task(
            task_id=task_id,
            target=target,
            actions=actions,
        )
        return ActionResult({"taskId": result_task_id})

    def describe_detect_mitigation_actions_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        result = self.iot_backend.describe_detect_mitigation_actions_task(
            task_id=task_id
        )
        return ActionResult(result)

    # --- Stub lists ---

    def list_active_violations(self) -> ActionResult:
        result = self.iot_backend.list_active_violations(
            thing_name=self._get_param("thingName"),
            security_profile_name=self._get_param("securityProfileName"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_violation_events(self) -> ActionResult:
        result = self.iot_backend.list_violation_events(
            start_time=self._get_param("startTime"),
            end_time=self._get_param("endTime"),
            thing_name=self._get_param("thingName"),
            security_profile_name=self._get_param("securityProfileName"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_metric_values(self) -> ActionResult:
        result = self.iot_backend.list_metric_values(
            thing_name=self._get_param("thingName"),
            metric_name=self._get_param("metricName"),
            dimension_name=self._get_param("dimensionName"),
            dimension_value_operator=self._get_param("dimensionValueOperator"),
            start_time=self._get_param("startTime"),
            end_time=self._get_param("endTime"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_related_resources_for_audit_finding(self) -> ActionResult:
        result = self.iot_backend.list_related_resources_for_audit_finding(
            finding_id=self._get_param("findingId"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def list_managed_job_templates(self) -> ActionResult:
        result = self.iot_backend.list_managed_job_templates(
            template_name=self._get_param("templateName"),
            max_results=self._get_int_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        return ActionResult(result)

    def describe_managed_job_template(self) -> ActionResult:
        template_name = self._get_param("templateName")
        template_version = self._get_param("templateVersion")
        result = self.iot_backend.describe_managed_job_template(
            template_name=template_name, template_version=template_version
        )
        return ActionResult(result)

    # --- Dynamic Thing Groups ---

    def create_dynamic_thing_group(self) -> ActionResult:
        thing_group_name = self._get_param("thingGroupName")
        query_string = self._get_param("queryString")
        thing_group_properties = self._get_param("thingGroupProperties")
        index_name = self._get_param("indexName")
        query_version = self._get_param("queryVersion")
        tags = self._get_param("tags")
        group = self.iot_backend.create_dynamic_thing_group(
            thing_group_name=thing_group_name,
            query_string=query_string,
            thing_group_properties=thing_group_properties,
            index_name=index_name,
            query_version=query_version,
            tags=tags,
        )
        return ActionResult(group.to_dict())

    def update_dynamic_thing_group(self) -> ActionResult:
        thing_group_name = self._get_param("thingGroupName")
        version = self.iot_backend.update_dynamic_thing_group(
            thing_group_name=thing_group_name,
            thing_group_properties=self._get_param("thingGroupProperties"),
            index_name=self._get_param("indexName"),
            query_string=self._get_param("queryString"),
            query_version=self._get_param("queryVersion"),
            expected_version=self._get_int_param("expectedVersion"),
        )
        return ActionResult({"version": version})

    def delete_dynamic_thing_group(self) -> ActionResult:
        thing_group_name = self._get_param("thingGroupName")
        self.iot_backend.delete_dynamic_thing_group(thing_group_name=thing_group_name)
        return EmptyResult()

    # --- Certificate Transfer ---

    def transfer_certificate(self) -> ActionResult:
        certificate_id = self._get_param("certificateId")
        target_aws_account = self._get_param("targetAwsAccount")
        transfer_message = self._get_param("transferMessage")
        result = self.iot_backend.transfer_certificate(
            certificate_id=certificate_id,
            target_aws_account=target_aws_account,
            transfer_message=transfer_message,
        )
        return ActionResult(result)

    def accept_certificate_transfer(self) -> ActionResult:
        certificate_id = self._get_param("certificateId")
        set_as_active = self._get_bool_param("setAsActive") or False
        self.iot_backend.accept_certificate_transfer(
            certificate_id=certificate_id, set_as_active=set_as_active
        )
        return EmptyResult()

    def cancel_certificate_transfer(self) -> ActionResult:
        certificate_id = self._get_param("certificateId")
        self.iot_backend.cancel_certificate_transfer(certificate_id=certificate_id)
        return EmptyResult()

    def reject_certificate_transfer(self) -> ActionResult:
        certificate_id = self._get_param("certificateId")
        reject_reason = self._get_param("rejectReason")
        self.iot_backend.reject_certificate_transfer(
            certificate_id=certificate_id, reject_reason=reject_reason
        )
        return EmptyResult()

    def list_outgoing_certificates(self) -> ActionResult:
        certs = self.iot_backend.list_outgoing_certificates()
        return ActionResult({"outgoingCertificates": certs})

    # --- Packages ---

    def create_package(self) -> ActionResult:
        package_name = self._get_param("packageName")
        description = self._get_param("description")
        tags = self._get_param("tags")
        pkg = self.iot_backend.create_package(
            package_name=package_name, description=description, tags=tags
        )
        return ActionResult(pkg.to_dict())

    def get_package(self) -> ActionResult:
        package_name = self._get_param("packageName")
        pkg = self.iot_backend.get_package(package_name=package_name)
        return ActionResult(pkg.to_dict())

    def update_package(self) -> ActionResult:
        package_name = self._get_param("packageName")
        self.iot_backend.update_package(
            package_name=package_name,
            description=self._get_param("description"),
            default_version_name=self._get_param("defaultVersionName"),
        )
        return EmptyResult()

    def delete_package(self) -> ActionResult:
        package_name = self._get_param("packageName")
        self.iot_backend.delete_package(package_name=package_name)
        return EmptyResult()

    def list_packages(self) -> ActionResult:
        packages = self.iot_backend.list_packages()
        return ActionResult({"packagesSummary": [p.to_dict() for p in packages]})

    def get_package_configuration(self) -> ActionResult:
        result = self.iot_backend.get_package_configuration()
        return ActionResult(result)

    def update_package_configuration(self) -> ActionResult:
        self.iot_backend.update_package_configuration(
            version_update_by_jobs_config=self._get_param("versionUpdateByJobsConfig"),
        )
        return EmptyResult()

    # --- Package Versions ---

    def create_package_version(self) -> ActionResult:
        package_name = self._get_param("packageName")
        version_name = self._get_param("versionName")
        description = self._get_param("description")
        attributes = self._get_param("attributes")
        tags = self._get_param("tags")
        ver = self.iot_backend.create_package_version(
            package_name=package_name,
            version_name=version_name,
            description=description,
            attributes=attributes,
            tags=tags,
        )
        return ActionResult(ver.to_dict())

    def get_package_version(self) -> ActionResult:
        ver = self.iot_backend.get_package_version(
            package_name=self._get_param("packageName"),
            version_name=self._get_param("versionName"),
        )
        return ActionResult(ver.to_dict())

    def update_package_version(self) -> ActionResult:
        self.iot_backend.update_package_version(
            package_name=self._get_param("packageName"),
            version_name=self._get_param("versionName"),
            description=self._get_param("description"),
            attributes=self._get_param("attributes"),
            action=self._get_param("action"),
        )
        return EmptyResult()

    def delete_package_version(self) -> ActionResult:
        self.iot_backend.delete_package_version(
            package_name=self._get_param("packageName"),
            version_name=self._get_param("versionName"),
        )
        return EmptyResult()

    def list_package_versions(self) -> ActionResult:
        versions = self.iot_backend.list_package_versions(
            package_name=self._get_param("packageName"),
        )
        return ActionResult(
            {"packageVersionSummaries": [v.to_dict() for v in versions]}
        )

    # --- Topic Rule Destinations ---

    def create_topic_rule_destination(self) -> ActionResult:
        destination_configuration = self._get_param("destinationConfiguration")
        dest = self.iot_backend.create_topic_rule_destination(
            destination_configuration=destination_configuration,
        )
        return ActionResult({"topicRuleDestination": dest.to_dict()})

    def delete_topic_rule_destination(self) -> ActionResult:
        arn = self._get_param("arn")
        self.iot_backend.delete_topic_rule_destination(arn=arn)
        return EmptyResult()

    def list_topic_rule_destinations(self) -> ActionResult:
        destinations = self.iot_backend.list_topic_rule_destinations()
        return ActionResult({"destinationSummaries": destinations})

    def update_topic_rule_destination(self) -> ActionResult:
        arn = self._get_param("arn")
        status = self._get_param("status")
        self.iot_backend.update_topic_rule_destination(arn=arn, status=status)
        return EmptyResult()

    def confirm_topic_rule_destination(self) -> ActionResult:
        confirmation_token = self._get_param("confirmationToken")
        self.iot_backend.confirm_topic_rule_destination(
            confirmation_token=confirmation_token
        )
        return EmptyResult()

    # --- Event Configurations ---

    def describe_event_configurations(self) -> ActionResult:
        result = self.iot_backend.describe_event_configurations()
        return ActionResult(result)

    def update_event_configurations(self) -> ActionResult:
        event_configurations = self._get_param("eventConfigurations")
        self.iot_backend.update_event_configurations(
            event_configurations=event_configurations
        )
        return EmptyResult()

    # --- Logging ---

    def get_logging_options(self) -> ActionResult:
        result = self.iot_backend.get_logging_options()
        return ActionResult(result)

    def set_logging_options(self) -> ActionResult:
        logging_options_payload = self._get_param("loggingOptionsPayload")
        self.iot_backend.set_logging_options(
            logging_options_payload=logging_options_payload
        )
        return EmptyResult()

    def set_v2_logging_options(self) -> ActionResult:
        self.iot_backend.set_v2_logging_options(
            role_arn=self._get_param("roleArn"),
            default_log_level=self._get_param("defaultLogLevel"),
            disable_all_logs=self._get_bool_param("disableAllLogs"),
        )
        return EmptyResult()

    def set_v2_logging_level(self) -> ActionResult:
        log_target = self._get_param("logTarget")
        log_level = self._get_param("logLevel")
        self.iot_backend.set_v2_logging_level(
            log_target=log_target, log_level=log_level
        )
        return EmptyResult()

    def list_v2_logging_levels(self) -> ActionResult:
        levels = self.iot_backend.list_v2_logging_levels()
        return ActionResult({"logTargetConfigurations": levels})

    def delete_v2_logging_level(self) -> ActionResult:
        target_type = self._get_param("targetType")
        target_name = self._get_param("targetName")
        self.iot_backend.delete_v2_logging_level(
            target_type=target_type, target_name=target_name
        )
        return EmptyResult()

    # --- Update Job ---

    def update_job(self) -> ActionResult:
        self.iot_backend.update_job(
            job_id=self._get_param("jobId"),
            description=self._get_param("description"),
            presigned_url_config=self._get_param("presignedUrlConfig"),
            job_executions_rollout_config=self._get_param("jobExecutionsRolloutConfig"),
            abort_config=self._get_param("abortConfig"),
            timeout_config=self._get_param("timeoutConfig"),
        )
        return EmptyResult()

    # --- Audit Suppressions ---

    def create_audit_suppression(self) -> ActionResult:
        self.iot_backend.create_audit_suppression(
            check_name=self._get_param("checkName"),
            resource_identifier=self._get_param("resourceIdentifier"),
            expiration_date=self._get_param("expirationDate"),
            suppress_indefinitely=self._get_bool_param("suppressIndefinitely"),
            description=self._get_param("description"),
        )
        return EmptyResult()

    def delete_audit_suppression(self) -> ActionResult:
        self.iot_backend.delete_audit_suppression(
            check_name=self._get_param("checkName"),
            resource_identifier=self._get_param("resourceIdentifier"),
        )
        return EmptyResult()

    def update_audit_suppression(self) -> ActionResult:
        self.iot_backend.update_audit_suppression(
            check_name=self._get_param("checkName"),
            resource_identifier=self._get_param("resourceIdentifier"),
            expiration_date=self._get_param("expirationDate"),
            suppress_indefinitely=self._get_bool_param("suppressIndefinitely"),
            description=self._get_param("description"),
        )
        return EmptyResult()

    def delete_account_audit_configuration(self) -> ActionResult:
        self.iot_backend.delete_account_audit_configuration()
        return EmptyResult()

    def start_on_demand_audit_task(self) -> ActionResult:
        target_check_names = self._get_param("targetCheckNames")
        task_id = self.iot_backend.start_on_demand_audit_task(
            target_check_names=target_check_names
        )
        return ActionResult({"taskId": task_id})

    def cancel_audit_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        self.iot_backend.cancel_audit_task(task_id=task_id)
        return EmptyResult()

    def start_audit_mitigation_actions_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        target = self._get_param("target")
        audit_check_to_actions_mapping = self._get_param("auditCheckToActionsMapping")
        result_task_id = self.iot_backend.start_audit_mitigation_actions_task(
            task_id=task_id,
            target=target,
            audit_check_to_actions_mapping=audit_check_to_actions_mapping,
        )
        return ActionResult({"taskId": result_task_id})

    def cancel_audit_mitigation_actions_task(self) -> ActionResult:
        task_id = self._get_param("taskId")
        self.iot_backend.cancel_audit_mitigation_actions_task(task_id=task_id)
        return EmptyResult()

    # --- Misc ---

    def get_effective_policies(self) -> ActionResult:
        principal = self._get_param("principal") or self.headers.get(
            "x-amzn-iot-principal"
        )
        thing_name = self._get_param("thingName")
        policies = self.iot_backend.get_effective_policies(
            principal=principal, thing_name=thing_name
        )
        return ActionResult({"effectivePolicies": policies})

    def update_thing_type(self) -> ActionResult:
        thing_type_name = self._get_param("thingTypeName")
        thing_type_properties = self._get_param("thingTypeProperties")
        self.iot_backend.update_thing_type(
            thing_type_name=thing_type_name,
            thing_type_properties=thing_type_properties,
        )
        return EmptyResult()

    def describe_index(self) -> ActionResult:
        index_name = self._get_param("indexName")
        result = self.iot_backend.describe_index(index_name=index_name)
        return ActionResult(result)

    def list_indices(self) -> ActionResult:
        indices = self.iot_backend.list_indices()
        return ActionResult({"indexNames": indices})

    def validate_security_profile_behaviors(self) -> ActionResult:
        behaviors = self._get_param("behaviors")
        result = self.iot_backend.validate_security_profile_behaviors(
            behaviors=behaviors
        )
        return ActionResult(result)

    # --- Tags ---

    def tag_resource(self) -> ActionResult:
        resource_arn = self._get_param("resourceArn")
        tags = self._get_param("tags")
        self.iot_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return EmptyResult()

    def untag_resource(self) -> ActionResult:
        resource_arn = self._get_param("resourceArn")
        tag_keys = self._get_param("tagKeys")
        self.iot_backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)
        return EmptyResult()

    def list_tags_for_resource(self) -> ActionResult:
        resource_arn = self._get_param("resourceArn")
        tags = self.iot_backend.list_tags_for_resource(resource_arn=resource_arn)
        return ActionResult({"tags": tags})

    def create_certificate_provider(self) -> ActionResult:
        certificate_provider = self.iot_backend.create_certificate_provider(
            certificate_provider_name=self._get_param("certificateProviderName"),
            lambda_function_arn=self._get_param("lambdaFunctionArn"),
            account_default_for_operations=self._get_param(
                "accountDefaultForOperations"
            ),
            tags=self._get_param("tags"),
        )
        return ActionResult(
            {
                "certificateProviderName": certificate_provider.certificate_provider_name,
                "certificateProviderArn": certificate_provider.arn,
            }
        )

    def describe_certificate_provider(self) -> ActionResult:
        certificate_provider = self.iot_backend.describe_certificate_provider(
            certificate_provider_name=self._get_param("certificateProviderName"),
        )
        return ActionResult(certificate_provider.to_description_dict())

    def list_certificate_providers(self) -> ActionResult:
        return ActionResult(
            {"certificateProviders": self.iot_backend.list_certificate_providers()}
        )

    def update_certificate_provider(self) -> ActionResult:
        certificate_provider = self.iot_backend.update_certificate_provider(
            certificate_provider_name=self._get_param("certificateProviderName"),
            lambda_function_arn=self._get_param("lambdaFunctionArn"),
            account_default_for_operations=self._get_param(
                "accountDefaultForOperations"
            ),
        )
        return ActionResult(
            {
                "certificateProviderName": certificate_provider.certificate_provider_name,
                "certificateProviderArn": certificate_provider.arn,
            }
        )

    def delete_certificate_provider(self) -> ActionResult:
        self.iot_backend.delete_certificate_provider(
            certificate_provider_name=self._get_param("certificateProviderName"),
        )
        return EmptyResult()

    # --- Commands ---

    def create_command(self) -> ActionResult:
        command_id = self._get_param("commandId")
        command = self.iot_backend.create_command(command_id=command_id)
        return ActionResult(
            {
                "commandId": command.command_id,
                "commandArn": command.arn,
            }
        )

    def get_command(self) -> ActionResult:
        command_id = self._get_param("commandId")
        command = self.iot_backend.get_command(command_id=command_id)
        return ActionResult(command.to_description_dict())

    def list_commands(self) -> ActionResult:
        commands = self.iot_backend.list_commands()
        return ActionResult({"commands": commands})

    def delete_command(self) -> ActionResult:
        command_id = self._get_param("commandId")
        self.iot_backend.delete_command(command_id=command_id)
        return EmptyResult()

    def update_command(self) -> ActionResult:
        command_id = self._get_param("commandId")
        command = self.iot_backend.update_command(
            command_id=command_id,
            display_name=self._get_param("displayName"),
            description=self._get_param("description"),
            deprecated=self._get_param("deprecated"),
        )
        return ActionResult(command.to_description_dict())

    # --- Command Executions ---

    def get_command_execution(self) -> ActionResult:
        return ActionResult(
            {
                "executionId": self._get_param("executionId"),
                "commandArn": "",
                "targetArn": self._get_param("targetArn") or "",
                "status": "SUCCEEDED",
            }
        )

    def list_command_executions(self) -> ActionResult:
        return ActionResult({"commandExecutions": [], "nextToken": None})

    def delete_command_execution(self) -> EmptyResult:
        return EmptyResult()

    # --- Registration / Provisioning ---

    def delete_registration_code(self) -> EmptyResult:
        return EmptyResult()

    def register_thing(self) -> ActionResult:
        return ActionResult(
            {
                "certificatePem": "",
                "resourceArns": {},
            }
        )

    def create_provisioning_claim(self) -> ActionResult:
        return ActionResult(
            {
                "certificateId": "stub-cert-id",
                "certificatePem": "-----BEGIN CERTIFICATE-----\nstub\n-----END CERTIFICATE-----",
                "keyPair": {
                    "PublicKey": "stub-public-key",
                    "PrivateKey": "stub-private-key",
                },
                "expiration": None,
            }
        )

    # --- SBOM ---

    def associate_sbom_with_package_version(self) -> ActionResult:
        return ActionResult(
            {
                "packageName": self._get_param("packageName") or "",
                "versionName": self._get_param("versionName") or "",
                "sbom": {},
                "sbomValidationStatus": "NOT_APPLICABLE",
            }
        )

    def disassociate_sbom_from_package_version(self) -> ActionResult:
        return ActionResult(
            {
                "packageName": self._get_param("packageName") or "",
                "versionName": self._get_param("versionName") or "",
            }
        )

    def list_sbom_validation_results(self) -> ActionResult:
        return ActionResult({"validationResultSummaries": [], "nextToken": None})

    # --- Jobs ---

    def associate_targets_with_job(self) -> ActionResult:
        return ActionResult(
            {
                "jobArn": "",
                "jobId": self._get_param("jobId") or "",
                "description": "",
            }
        )

    # --- Anomaly Detection / DD ---

    def get_behavior_model_training_summaries(self) -> ActionResult:
        return ActionResult({"summaries": [], "nextToken": None})

    def cancel_detect_mitigation_actions_task(self) -> EmptyResult:
        return EmptyResult()

    def start_detect_mitigation_actions_task(self) -> ActionResult:
        return ActionResult({"taskId": self._get_param("taskId") or "stub-task"})

    def list_thing_registration_tasks(self) -> ActionResult:
        return ActionResult({"taskIds": [], "nextToken": None})

    def list_thing_registration_task_reports(self) -> ActionResult:
        return ActionResult({"resourceLinks": [], "reportType": "", "nextToken": None})

    def put_verification_state_on_violation(self) -> EmptyResult:
        return EmptyResult()

    # --- Fleet Indexing / Search ---

    def get_buckets_aggregation(self) -> ActionResult:
        return ActionResult({"totalCount": 0, "buckets": []})

    def get_cardinality(self) -> ActionResult:
        return ActionResult({"cardinality": 0})

    def get_percentiles(self) -> ActionResult:
        return ActionResult({"percentiles": []})

    # --- Authorizer Testing ---

    def test_authorization(self) -> ActionResult:
        return ActionResult({"authResults": [], "missing": []})

    def test_invoke_authorizer(self) -> ActionResult:
        return ActionResult(
            {
                "isAuthenticated": True,
                "principalId": "stub-principal",
                "policyDocuments": [],
                "refreshAfterInSeconds": 3600,
                "disconnectAfterInSeconds": 86400,
            }
        )

    # --- Auth ---

    def clear_default_authorizer(self) -> EmptyResult:
        return EmptyResult()

    # --- Encryption ---

    def update_encryption_configuration(self) -> EmptyResult:
        return EmptyResult()

    # --- PrincipalThings V2 ---

    def list_principal_things_v2(self) -> ActionResult:
        return ActionResult({"principalThingObjects": [], "nextToken": None})
