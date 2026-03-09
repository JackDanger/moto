"""Handles incoming sesv2 requests, invokes methods, returns responses."""

import base64
import json

from moto.core.responses import BaseResponse

from .models import SESV2Backend, sesv2_backends


class SESV2Response(BaseResponse):
    """Handler for SESV2 requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="sesv2")

    @property
    def sesv2_backend(self) -> SESV2Backend:
        """Return backend instance specific for this region."""
        return sesv2_backends[self.current_account][self.region]

    def send_email(self) -> str:
        """Piggy back on functionality from v1 mostly"""

        params = json.loads(self.body)
        from_email_address = params.get("FromEmailAddress")
        destination = params.get("Destination", {})
        content = params.get("Content")
        if "Raw" in content:
            all_destinations: list[str] = []
            if "ToAddresses" in destination:
                all_destinations = all_destinations + destination["ToAddresses"]
            if "CcAddresses" in destination:
                all_destinations = all_destinations + destination["CcAddresses"]
            if "BccAddresses" in destination:
                all_destinations = all_destinations + destination["BccAddresses"]
            message = self.sesv2_backend.send_raw_email(
                source=from_email_address,
                destinations=all_destinations,
                raw_data=base64.b64decode(content["Raw"]["Data"]).decode("utf-8"),
            )
        elif "Simple" in content:
            content_body = content["Simple"]["Body"]
            if "Html" in content_body:
                body = content_body["Html"]["Data"]
            else:
                body = content_body["Text"]["Data"]
            message = self.sesv2_backend.send_email(  # type: ignore
                source=from_email_address,
                destinations=destination,
                subject=content["Simple"]["Subject"]["Data"],
                body=body,
            )
        elif "Template" in content:
            raise NotImplementedError("Template functionality not ready")

        return json.dumps({"MessageId": message.id})

    def create_contact_list(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.create_contact_list(params)
        return json.dumps({})

    def get_contact_list(self) -> str:
        contact_list_name = self._get_param("ContactListName")
        contact_list = self.sesv2_backend.get_contact_list(contact_list_name)
        return json.dumps(contact_list.response_object)

    def list_contact_lists(self) -> str:
        contact_lists = self.sesv2_backend.list_contact_lists()
        return json.dumps({"ContactLists": [c.response_object for c in contact_lists]})

    def delete_contact_list(self) -> str:
        name = self._get_param("ContactListName")
        self.sesv2_backend.delete_contact_list(name)
        return json.dumps({})

    def create_contact(self) -> str:
        contact_list_name = self._get_param("ContactListName")
        params = json.loads(self.body)
        self.sesv2_backend.create_contact(contact_list_name, params)
        return json.dumps({})

    def get_contact(self) -> str:
        email = self._get_param("EmailAddress")
        contact_list_name = self._get_param("ContactListName")
        contact = self.sesv2_backend.get_contact(email, contact_list_name)
        return json.dumps(contact.response_object)

    def list_contacts(self) -> str:
        contact_list_name = self._get_param("ContactListName")
        contacts = self.sesv2_backend.list_contacts(contact_list_name)
        return json.dumps({"Contacts": [c.response_object for c in contacts]})

    def delete_contact(self) -> str:
        email = self._get_param("EmailAddress")
        contact_list_name = self._get_param("ContactListName")
        self.sesv2_backend.delete_contact(email, contact_list_name)
        return json.dumps({})

    def create_email_identity(self) -> str:
        email_identity_name = self._get_param("EmailIdentity")
        tags = self._get_param("Tags")
        dkim_signing_attributes = self._get_param("DkimSigningAttributes")
        configuration_set_name = self._get_param("ConfigurationSetName")
        email_identity = self.sesv2_backend.create_email_identity(
            email_identity=email_identity_name,
            tags=tags,
            dkim_signing_attributes=dkim_signing_attributes,
            configuration_set_name=configuration_set_name,
        )
        return json.dumps(
            {
                "IdentityType": email_identity.identity_type,
                "VerifiedForSendingStatus": email_identity.verified_for_sending_status,
                "DkimAttributes": email_identity.dkim_attributes,
            }
        )

    def delete_email_identity(self) -> str:
        email_identity_name = self._get_param("EmailIdentity")
        self.sesv2_backend.delete_email_identity(email_identity=email_identity_name)
        return json.dumps({})

    def get_email_identity(self) -> str:
        email_identity_name = self._get_param("EmailIdentity")
        email_identity = self.sesv2_backend.get_email_identity(
            email_identity=email_identity_name,
        )
        return json.dumps(email_identity.get_response_object)

    def list_email_identities(self) -> str:
        next_token = self._get_param("NextToken")
        page_size = self._get_param("PageSize")
        email_identities, next_token = self.sesv2_backend.list_email_identities(
            next_token=next_token,
            page_size=page_size,
        )
        if isinstance(email_identities, list):
            response = [e.list_response_object for e in email_identities]
        else:
            response = []

        return json.dumps(
            {
                "EmailIdentities": response,
                "NextToken": next_token,
            }
        )

    def create_configuration_set(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        tracking_options = self._get_param("TrackingOptions")
        delivery_options = self._get_param("DeliveryOptions")
        reputation_options = self._get_param("ReputationOptions")
        sending_options = self._get_param("SendingOptions")
        tags = self._get_param("Tags")
        suppression_options = self._get_param("SuppressionOptions")
        vdm_options = self._get_param("VdmOptions")
        self.sesv2_backend.create_configuration_set(
            configuration_set_name=configuration_set_name,
            tracking_options=tracking_options,
            delivery_options=delivery_options,
            reputation_options=reputation_options,
            sending_options=sending_options,
            tags=tags,
            suppression_options=suppression_options,
            vdm_options=vdm_options,
        )
        return json.dumps({})

    def delete_configuration_set(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        self.sesv2_backend.delete_configuration_set(
            configuration_set_name=configuration_set_name,
        )
        return json.dumps({})

    def get_configuration_set(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        config_set = self.sesv2_backend.get_configuration_set(
            configuration_set_name=configuration_set_name,
        )
        return json.dumps(config_set.to_dict_v2())

    def list_configuration_sets(self) -> str:
        next_token = self._get_param("NextToken")
        page_size = self._get_param("PageSize")
        configuration_sets, next_token = self.sesv2_backend.list_configuration_sets(
            next_token=next_token, page_size=page_size
        )
        config_set_names = [c.configuration_set_name for c in configuration_sets]

        return json.dumps(
            {"ConfigurationSets": config_set_names, "NextToken": next_token}
        )

    def create_dedicated_ip_pool(self) -> str:
        pool_name = self._get_param("PoolName")
        tags = self._get_param("Tags")
        scaling_mode = self._get_param("ScalingMode")
        self.sesv2_backend.create_dedicated_ip_pool(
            pool_name=pool_name,
            tags=tags,
            scaling_mode=scaling_mode,
        )
        return json.dumps({})

    def delete_dedicated_ip_pool(self) -> str:
        pool_name = self._get_param("PoolName")
        self.sesv2_backend.delete_dedicated_ip_pool(
            pool_name=pool_name,
        )
        return json.dumps({})

    def list_dedicated_ip_pools(self) -> str:
        next_token = self._get_param("NextToken")
        page_size = self._get_param("PageSize")
        dedicated_ip_pools, next_token = self.sesv2_backend.list_dedicated_ip_pools(
            next_token=next_token, page_size=page_size
        )
        return json.dumps(
            {"DedicatedIpPools": dedicated_ip_pools, "NextToken": next_token}
        )

    def get_dedicated_ip_pool(self) -> str:
        pool_name = self._get_param("PoolName")
        dedicated_ip_pool = self.sesv2_backend.get_dedicated_ip_pool(
            pool_name=pool_name,
        )
        return json.dumps({"DedicatedIpPool": dedicated_ip_pool.to_dict()})

    def create_email_identity_policy(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        policy_name = self._get_param("PolicyName")
        policy = self._get_param("Policy")
        self.sesv2_backend.create_email_identity_policy(
            email_identity=email_identity,
            policy_name=policy_name,
            policy=policy,
        )
        return json.dumps({})

    def delete_email_identity_policy(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        policy_name = self._get_param("PolicyName")
        self.sesv2_backend.delete_email_identity_policy(
            email_identity=email_identity,
            policy_name=policy_name,
        )
        return json.dumps({})

    def update_email_identity_policy(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        policy_name = self._get_param("PolicyName")
        policy = self._get_param("Policy")
        self.sesv2_backend.update_email_identity_policy(
            email_identity=email_identity,
            policy_name=policy_name,
            policy=policy,
        )
        return json.dumps({})

    def get_email_identity_policies(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        policies = self.sesv2_backend.get_email_identity_policies(
            email_identity=email_identity,
        )
        return json.dumps({"Policies": policies})


    # ===== Email Template handlers =====

    def create_email_template(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.create_email_template(template_name=params["TemplateName"], template_content=params["TemplateContent"])
        return json.dumps({})

    def get_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        template = self.sesv2_backend.get_email_template(template_name=template_name)
        return json.dumps({"TemplateName": template.template_name, "TemplateContent": template.template_content})

    def update_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        params = json.loads(self.body)
        self.sesv2_backend.update_email_template(template_name=template_name, template_content=params["TemplateContent"])
        return json.dumps({})

    def delete_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        self.sesv2_backend.delete_email_template(template_name=template_name)
        return json.dumps({})

    def list_email_templates(self) -> str:
        next_token = self._get_param("NextToken")
        page_size = self._get_param("PageSize")
        templates, next_token = self.sesv2_backend.list_email_templates(next_token=next_token, page_size=page_size)
        return json.dumps({"TemplatesMetadata": [t.to_metadata_dict() for t in templates], "NextToken": next_token})

    # ===== Configuration Set Event Destination handlers =====

    def create_configuration_set_event_destination(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.create_configuration_set_event_destination(configuration_set_name=configuration_set_name, event_destination_name=params["EventDestinationName"], event_destination=params["EventDestination"])
        return json.dumps({})

    def get_configuration_set_event_destinations(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        destinations = self.sesv2_backend.get_configuration_set_event_destinations(configuration_set_name=configuration_set_name)
        return json.dumps({"EventDestinations": [d.to_dict() for d in destinations]})

    def update_configuration_set_event_destination(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        event_destination_name = self._get_param("EventDestinationName")
        params = json.loads(self.body)
        self.sesv2_backend.update_configuration_set_event_destination(configuration_set_name=configuration_set_name, event_destination_name=event_destination_name, event_destination=params["EventDestination"])
        return json.dumps({})

    def delete_configuration_set_event_destination(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        event_destination_name = self._get_param("EventDestinationName")
        self.sesv2_backend.delete_configuration_set_event_destination(configuration_set_name=configuration_set_name, event_destination_name=event_destination_name)
        return json.dumps({})

    # ===== Custom Verification Email Template handlers =====

    def create_custom_verification_email_template(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.create_custom_verification_email_template(template_name=params["TemplateName"], from_email_address=params["FromEmailAddress"], template_subject=params["TemplateSubject"], template_content=params["TemplateContent"], success_redirection_url=params["SuccessRedirectionURL"], failure_redirection_url=params["FailureRedirectionURL"])
        return json.dumps({})

    def get_custom_verification_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        tmpl = self.sesv2_backend.get_custom_verification_email_template(template_name=template_name)
        return json.dumps({"TemplateName": tmpl.template_name, "FromEmailAddress": tmpl.from_email_address, "TemplateSubject": tmpl.template_subject, "TemplateContent": tmpl.template_content, "SuccessRedirectionURL": tmpl.success_redirection_url, "FailureRedirectionURL": tmpl.failure_redirection_url})

    def update_custom_verification_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        params = json.loads(self.body)
        self.sesv2_backend.update_custom_verification_email_template(template_name=template_name, from_email_address=params["FromEmailAddress"], template_subject=params["TemplateSubject"], template_content=params["TemplateContent"], success_redirection_url=params["SuccessRedirectionURL"], failure_redirection_url=params["FailureRedirectionURL"])
        return json.dumps({})

    def delete_custom_verification_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        self.sesv2_backend.delete_custom_verification_email_template(template_name=template_name)
        return json.dumps({})

    def list_custom_verification_email_templates(self) -> str:
        next_token = self._get_param("NextToken")
        page_size = self._get_param("PageSize")
        templates, next_token = self.sesv2_backend.list_custom_verification_email_templates(next_token=next_token, page_size=page_size)
        return json.dumps({"CustomVerificationEmailTemplates": [{"TemplateName": t.template_name, "FromEmailAddress": t.from_email_address, "TemplateSubject": t.template_subject, "SuccessRedirectionURL": t.success_redirection_url, "FailureRedirectionURL": t.failure_redirection_url} for t in templates], "NextToken": next_token})

    # ===== Account handlers =====

    def put_account_details(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_account_details(mail_type=params["MailType"], website_url=params["WebsiteURL"], contact_language=params.get("ContactLanguage"), use_case_description=params.get("UseCaseDescription"), additional_contact_email_addresses=params.get("AdditionalContactEmailAddresses"), production_access_enabled=params.get("ProductionAccessEnabled"))
        return json.dumps({})

    def get_account(self) -> str:
        return json.dumps(self.sesv2_backend.get_account())

    def put_account_sending_attributes(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_account_sending_attributes(sending_enabled=params.get("SendingEnabled", False))
        return json.dumps({})

    def put_account_suppression_attributes(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_account_suppression_attributes(suppressed_reasons=params.get("SuppressedReasons", []))
        return json.dumps({})

    # ===== Configuration Set options handlers =====

    def put_configuration_set_sending_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_sending_options(configuration_set_name=configuration_set_name, sending_enabled=params.get("SendingEnabled", False))
        return json.dumps({})

    def put_configuration_set_reputation_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_reputation_options(configuration_set_name=configuration_set_name, reputation_metrics_enabled=params.get("ReputationMetricsEnabled", False))
        return json.dumps({})

    def tag_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags")
        self.sesv2_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self.__dict__["data"]["TagKeys"]
        self.sesv2_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tags = self.sesv2_backend.list_tags_for_resource(
            resource_arn=resource_arn,
        )
        return json.dumps({"Tags": tags})

    # ===== Suppressed Destination handlers =====

    def put_suppressed_destination(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_suppressed_destination(
            email_address=params["EmailAddress"],
            reason=params["Reason"],
        )
        return json.dumps({})

    def get_suppressed_destination(self) -> str:
        email_address = self._get_param("EmailAddress")
        dest = self.sesv2_backend.get_suppressed_destination(email_address)
        return json.dumps({"SuppressedDestination": dest.to_full_dict()})

    def list_suppressed_destinations(self) -> str:
        destinations = self.sesv2_backend.list_suppressed_destinations()
        return json.dumps(
            {"SuppressedDestinationSummaries": [d.to_dict() for d in destinations]}
        )

    def delete_suppressed_destination(self) -> str:
        email_address = self._get_param("EmailAddress")
        self.sesv2_backend.delete_suppressed_destination(email_address)
        return json.dumps({})

    # ===== Dedicated IP handlers =====

    def get_dedicated_ips(self) -> str:
        pool_name = self._get_param("PoolName")
        ips = self.sesv2_backend.get_dedicated_ips(pool_name=pool_name)
        return json.dumps({"DedicatedIps": ips})

    def get_dedicated_ip(self) -> str:
        ip = self._get_param("IP")
        dedicated_ip = self.sesv2_backend.get_dedicated_ip(ip)
        return json.dumps({"DedicatedIp": dedicated_ip})

    def put_dedicated_ip_warmup_attributes(self) -> str:
        ip = self._get_param("IP")
        params = json.loads(self.body)
        self.sesv2_backend.put_dedicated_ip_warmup_attributes(
            ip=ip, warmup_percentage=params.get("WarmupPercentage", 100)
        )
        return json.dumps({})

    # ===== Deliverability Dashboard handlers =====

    def get_deliverability_dashboard_options(self) -> str:
        options = self.sesv2_backend.get_deliverability_dashboard_options()
        return json.dumps(options)

    def get_blacklist_reports(self) -> str:
        blacklist_item_names = self.querystring.get("BlacklistItemNames", [])
        if not blacklist_item_names:
            blacklist_item_names = ["default"]
        reports = self.sesv2_backend.get_blacklist_reports(blacklist_item_names)
        return json.dumps({"BlacklistReport": reports})

    # ===== VDM Options handler =====

    def put_configuration_set_vdm_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_vdm_options(
            configuration_set_name=configuration_set_name,
            vdm_options=params.get("VdmOptions", {}),
        )
        return json.dumps({})

    # ===== Email Identity Configuration Set / DKIM handlers =====

    def put_email_identity_configuration_set_attributes(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        params = json.loads(self.body)
        self.sesv2_backend.put_email_identity_configuration_set_attributes(
            email_identity=email_identity,
            configuration_set_name=params.get("ConfigurationSetName"),
        )
        return json.dumps({})

    def put_email_identity_dkim_signing_attributes(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        params = json.loads(self.body)
        result = self.sesv2_backend.put_email_identity_dkim_signing_attributes(
            email_identity=email_identity,
            signing_attributes_origin=params.get("SigningAttributesOrigin", "AWS_SES"),
            signing_attributes=params.get("SigningAttributes"),
        )
        return json.dumps(result)

    # ===== Multi-Region Endpoints handler =====

    def list_multi_region_endpoints(self) -> str:
        endpoints = self.sesv2_backend.list_multi_region_endpoints()
        return json.dumps({"MultiRegionEndpoints": endpoints})
