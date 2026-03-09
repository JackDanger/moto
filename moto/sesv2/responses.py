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
            # Template-based sending: use simple email as fallback
            template_name = content["Template"].get("TemplateName", "")
            template_data = content["Template"].get("TemplateData", "{}")
            message = self.sesv2_backend.send_email(  # type: ignore
                source=from_email_address,
                destinations=destination,
                subject=f"Template: {template_name}",
                body=template_data,
            )
        else:
            message = self.sesv2_backend.send_email(  # type: ignore
                source=from_email_address,
                destinations=destination,
                subject="(no subject)",
                body="",
            )

        return json.dumps({"MessageId": message.id})

    def send_bulk_email(self) -> str:
        params = json.loads(self.body)
        results = self.sesv2_backend.send_bulk_email(
            from_email_address=params.get("FromEmailAddress"),
            default_content=params.get("DefaultContent", {}),
            bulk_email_entries=params.get("BulkEmailEntries", []),
        )
        return json.dumps({"BulkEmailEntryResults": results})

    def send_custom_verification_email(self) -> str:
        params = json.loads(self.body)
        message_id = self.sesv2_backend.send_custom_verification_email(
            email_address=params["EmailAddress"],
            template_name=params["TemplateName"],
            configuration_set_name=params.get("ConfigurationSetName"),
        )
        return json.dumps({"MessageId": message_id})

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

    def update_contact_list(self) -> str:
        contact_list_name = self._get_param("ContactListName")
        params = json.loads(self.body)
        self.sesv2_backend.update_contact_list(contact_list_name, params)
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

    def update_contact(self) -> str:
        contact_list_name = self._get_param("ContactListName")
        email_address = self._get_param("EmailAddress")
        params = json.loads(self.body)
        self.sesv2_backend.update_contact(contact_list_name, email_address, params)
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
        self.sesv2_backend.create_email_template(
            template_name=params["TemplateName"],
            template_content=params["TemplateContent"],
        )
        return json.dumps({})

    def get_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        template = self.sesv2_backend.get_email_template(template_name=template_name)
        return json.dumps({
            "TemplateName": template.template_name,
            "TemplateContent": template.template_content,
        })

    def update_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        params = json.loads(self.body)
        self.sesv2_backend.update_email_template(
            template_name=template_name,
            template_content=params["TemplateContent"],
        )
        return json.dumps({})

    def delete_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        self.sesv2_backend.delete_email_template(template_name=template_name)
        return json.dumps({})

    def list_email_templates(self) -> str:
        next_token = self._get_param("NextToken")
        page_size = self._get_param("PageSize")
        templates, next_token = self.sesv2_backend.list_email_templates(
            next_token=next_token, page_size=page_size
        )
        return json.dumps({
            "TemplatesMetadata": [t.to_metadata_dict() for t in templates],
            "NextToken": next_token,
        })

    def test_render_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        params = json.loads(self.body)
        rendered = self.sesv2_backend.test_render_email_template(
            template_name=template_name,
            template_data=params.get("TemplateData", "{}"),
        )
        return json.dumps({"RenderedTemplate": rendered})

    # ===== Configuration Set Event Destination handlers =====

    def create_configuration_set_event_destination(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.create_configuration_set_event_destination(
            configuration_set_name=configuration_set_name,
            event_destination_name=params["EventDestinationName"],
            event_destination=params["EventDestination"],
        )
        return json.dumps({})

    def get_configuration_set_event_destinations(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        destinations = self.sesv2_backend.get_configuration_set_event_destinations(
            configuration_set_name=configuration_set_name
        )
        return json.dumps({"EventDestinations": [d.to_dict() for d in destinations]})

    def update_configuration_set_event_destination(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        event_destination_name = self._get_param("EventDestinationName")
        params = json.loads(self.body)
        self.sesv2_backend.update_configuration_set_event_destination(
            configuration_set_name=configuration_set_name,
            event_destination_name=event_destination_name,
            event_destination=params["EventDestination"],
        )
        return json.dumps({})

    def delete_configuration_set_event_destination(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        event_destination_name = self._get_param("EventDestinationName")
        self.sesv2_backend.delete_configuration_set_event_destination(
            configuration_set_name=configuration_set_name,
            event_destination_name=event_destination_name,
        )
        return json.dumps({})

    # ===== Custom Verification Email Template handlers =====

    def create_custom_verification_email_template(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.create_custom_verification_email_template(
            template_name=params["TemplateName"],
            from_email_address=params["FromEmailAddress"],
            template_subject=params["TemplateSubject"],
            template_content=params["TemplateContent"],
            success_redirection_url=params["SuccessRedirectionURL"],
            failure_redirection_url=params["FailureRedirectionURL"],
        )
        return json.dumps({})

    def get_custom_verification_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        tmpl = self.sesv2_backend.get_custom_verification_email_template(
            template_name=template_name
        )
        return json.dumps({
            "TemplateName": tmpl.template_name,
            "FromEmailAddress": tmpl.from_email_address,
            "TemplateSubject": tmpl.template_subject,
            "TemplateContent": tmpl.template_content,
            "SuccessRedirectionURL": tmpl.success_redirection_url,
            "FailureRedirectionURL": tmpl.failure_redirection_url,
        })

    def update_custom_verification_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        params = json.loads(self.body)
        self.sesv2_backend.update_custom_verification_email_template(
            template_name=template_name,
            from_email_address=params["FromEmailAddress"],
            template_subject=params["TemplateSubject"],
            template_content=params["TemplateContent"],
            success_redirection_url=params["SuccessRedirectionURL"],
            failure_redirection_url=params["FailureRedirectionURL"],
        )
        return json.dumps({})

    def delete_custom_verification_email_template(self) -> str:
        template_name = self._get_param("TemplateName")
        self.sesv2_backend.delete_custom_verification_email_template(
            template_name=template_name
        )
        return json.dumps({})

    def list_custom_verification_email_templates(self) -> str:
        next_token = self._get_param("NextToken")
        page_size = self._get_param("PageSize")
        templates, next_token = self.sesv2_backend.list_custom_verification_email_templates(
            next_token=next_token, page_size=page_size
        )
        return json.dumps({
            "CustomVerificationEmailTemplates": [
                {
                    "TemplateName": t.template_name,
                    "FromEmailAddress": t.from_email_address,
                    "TemplateSubject": t.template_subject,
                    "SuccessRedirectionURL": t.success_redirection_url,
                    "FailureRedirectionURL": t.failure_redirection_url,
                }
                for t in templates
            ],
            "NextToken": next_token,
        })

    # ===== Account handlers =====

    def put_account_details(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_account_details(
            mail_type=params["MailType"],
            website_url=params["WebsiteURL"],
            contact_language=params.get("ContactLanguage"),
            use_case_description=params.get("UseCaseDescription"),
            additional_contact_email_addresses=params.get("AdditionalContactEmailAddresses"),
            production_access_enabled=params.get("ProductionAccessEnabled"),
        )
        return json.dumps({})

    def get_account(self) -> str:
        return json.dumps(self.sesv2_backend.get_account())

    def put_account_sending_attributes(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_account_sending_attributes(
            sending_enabled=params.get("SendingEnabled", False)
        )
        return json.dumps({})

    def put_account_suppression_attributes(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_account_suppression_attributes(
            suppressed_reasons=params.get("SuppressedReasons", [])
        )
        return json.dumps({})

    def put_account_dedicated_ip_warmup_attributes(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_account_dedicated_ip_warmup_attributes(
            auto_warmup_enabled=params.get("AutoWarmupEnabled", False)
        )
        return json.dumps({})

    def put_account_vdm_attributes(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_account_vdm_attributes(
            vdm_attributes=params.get("VdmAttributes", {})
        )
        return json.dumps({})

    # ===== Configuration Set options handlers =====

    def put_configuration_set_sending_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_sending_options(
            configuration_set_name=configuration_set_name,
            sending_enabled=params.get("SendingEnabled", False),
        )
        return json.dumps({})

    def put_configuration_set_reputation_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_reputation_options(
            configuration_set_name=configuration_set_name,
            reputation_metrics_enabled=params.get("ReputationMetricsEnabled", False),
        )
        return json.dumps({})

    def put_configuration_set_delivery_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_delivery_options(
            configuration_set_name=configuration_set_name,
            tls_policy=params.get("TlsPolicy"),
            sending_pool_name=params.get("SendingPoolName"),
        )
        return json.dumps({})

    def put_configuration_set_suppression_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_suppression_options(
            configuration_set_name=configuration_set_name,
            suppressed_reasons=params.get("SuppressedReasons"),
        )
        return json.dumps({})

    def put_configuration_set_tracking_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_tracking_options(
            configuration_set_name=configuration_set_name,
            custom_redirect_domain=params.get("CustomRedirectDomain"),
        )
        return json.dumps({})

    def put_configuration_set_archiving_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_archiving_options(
            configuration_set_name=configuration_set_name,
            archive_arn=params.get("ArchiveArn"),
        )
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
        # TagKeys come as query params for DELETE requests
        tag_keys = self.querystring.get("TagKeys", [])
        if not tag_keys and hasattr(self, "data") and isinstance(self.data, dict):
            tag_keys = self.data.get("TagKeys", [])
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

    # ===== Suppressed Destinations =====

    def put_suppressed_destination(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_suppressed_destination(
            email_address=params["EmailAddress"],
            reason=params["Reason"],
        )
        return json.dumps({})

    def get_suppressed_destination(self) -> str:
        email_address = self._get_param("EmailAddress")
        suppressed = self.sesv2_backend.get_suppressed_destination(email_address)
        return json.dumps({"SuppressedDestination": suppressed.to_full_dict()})

    def list_suppressed_destinations(self) -> str:
        suppressed = self.sesv2_backend.list_suppressed_destinations()
        return json.dumps({
            "SuppressedDestinationSummaries": [s.to_dict() for s in suppressed],
        })

    def delete_suppressed_destination(self) -> str:
        email_address = self._get_param("EmailAddress")
        self.sesv2_backend.delete_suppressed_destination(email_address)
        return json.dumps({})

    # ===== Dedicated IP =====

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
            ip=ip, warmup_percentage=params.get("WarmupPercentage", 0)
        )
        return json.dumps({})

    def put_dedicated_ip_in_pool(self) -> str:
        ip = self._get_param("IP")
        params = json.loads(self.body)
        self.sesv2_backend.put_dedicated_ip_in_pool(
            ip=ip,
            destination_pool_name=params.get("DestinationPoolName", ""),
        )
        return json.dumps({})

    def put_dedicated_ip_pool_scaling_attributes(self) -> str:
        pool_name = self._get_param("PoolName")
        params = json.loads(self.body)
        self.sesv2_backend.put_dedicated_ip_pool_scaling_attributes(
            pool_name=pool_name,
            scaling_mode=params.get("ScalingMode", "STANDARD"),
        )
        return json.dumps({})

    # ===== Deliverability Dashboard =====

    def get_deliverability_dashboard_options(self) -> str:
        result = self.sesv2_backend.get_deliverability_dashboard_options()
        return json.dumps(result)

    def put_deliverability_dashboard_option(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.put_deliverability_dashboard_option(
            dashboard_enabled=params.get("DashboardEnabled", False)
        )
        return json.dumps({})

    def create_deliverability_test_report(self) -> str:
        params = json.loads(self.body)
        result = self.sesv2_backend.create_deliverability_test_report(
            from_email_address=params.get("FromEmailAddress", ""),
            content=params.get("Content", {}),
            report_name=params.get("ReportName"),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def get_deliverability_test_report(self) -> str:
        report_id = self._get_param("ReportId")
        result = self.sesv2_backend.get_deliverability_test_report(report_id)
        return json.dumps(result)

    def list_deliverability_test_reports(self) -> str:
        reports = self.sesv2_backend.list_deliverability_test_reports()
        return json.dumps({"DeliverabilityTestReports": reports})

    def get_domain_statistics_report(self) -> str:
        domain = self._get_param("Domain")
        result = self.sesv2_backend.get_domain_statistics_report(domain)
        return json.dumps(result)

    def get_domain_deliverability_campaign(self) -> str:
        campaign_id = self._get_param("CampaignId")
        result = self.sesv2_backend.get_domain_deliverability_campaign(campaign_id)
        return json.dumps(result)

    def list_domain_deliverability_campaigns(self) -> str:
        subscribed_domain = self._get_param("SubscribedDomain")
        campaigns = self.sesv2_backend.list_domain_deliverability_campaigns(
            subscribed_domain=subscribed_domain
        )
        return json.dumps({"DomainDeliverabilityCampaigns": campaigns})

    # ===== Blacklist =====

    def get_blacklist_reports(self) -> str:
        result = self.sesv2_backend.get_blacklist_reports()
        return json.dumps(result)

    # ===== VDM Attributes =====

    def put_configuration_set_vdm_options(self) -> str:
        configuration_set_name = self._get_param("ConfigurationSetName")
        params = json.loads(self.body)
        self.sesv2_backend.put_configuration_set_vdm_attributes(
            configuration_set_name=configuration_set_name,
            vdm_options=params.get("VdmOptions", {}),
        )
        return json.dumps({})

    # ===== Email Identity Config Set =====

    def put_email_identity_configuration_set_attributes(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        params = json.loads(self.body)
        self.sesv2_backend.put_email_identity_configuration_set_attributes(
            email_identity=email_identity,
            configuration_set_name=params.get("ConfigurationSetName"),
        )
        return json.dumps({})

    # ===== DKIM =====

    def put_email_identity_dkim_signing_attributes(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        params = json.loads(self.body)
        result = self.sesv2_backend.put_email_identity_dkim_signing_attributes(
            email_identity=email_identity,
            signing_attributes_origin=params.get("SigningAttributesOrigin", "AWS_SES"),
            signing_attributes=params.get("SigningAttributes"),
        )
        return json.dumps(result)

    def put_email_identity_dkim_attributes(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        params = json.loads(self.body)
        self.sesv2_backend.put_email_identity_dkim_attributes(
            email_identity=email_identity,
            signing_enabled=params.get("SigningEnabled", True),
        )
        return json.dumps({})

    def put_email_identity_feedback_attributes(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        params = json.loads(self.body)
        self.sesv2_backend.put_email_identity_feedback_attributes(
            email_identity=email_identity,
            email_forwarding_enabled=params.get("EmailForwardingEnabled", True),
        )
        return json.dumps({})

    def put_email_identity_mail_from_attributes(self) -> str:
        email_identity = self._get_param("EmailIdentity")
        params = json.loads(self.body)
        self.sesv2_backend.put_email_identity_mail_from_attributes(
            email_identity=email_identity,
            mail_from_domain=params.get("MailFromDomain"),
            behavior_on_mx_failure=params.get("BehaviorOnMxFailure"),
        )
        return json.dumps({})

    # ===== Multi-Region Endpoints =====

    def list_multi_region_endpoints(self) -> str:
        endpoints = self.sesv2_backend.list_multi_region_endpoints()
        return json.dumps({"MultiRegionEndpoints": endpoints})

    def create_multi_region_endpoint(self) -> str:
        params = json.loads(self.body)
        result = self.sesv2_backend.create_multi_region_endpoint(
            endpoint_name=params["EndpointName"],
            details=params.get("Details", {}),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def get_multi_region_endpoint(self) -> str:
        endpoint_name = self._get_param("EndpointName")
        result = self.sesv2_backend.get_multi_region_endpoint(endpoint_name)
        return json.dumps(result)

    def delete_multi_region_endpoint(self) -> str:
        endpoint_name = self._get_param("EndpointName")
        self.sesv2_backend.delete_multi_region_endpoint(endpoint_name)
        return json.dumps({"Status": "SHUTTING_DOWN"})

    # ===== Import Jobs =====

    def create_import_job(self) -> str:
        params = json.loads(self.body)
        job_id = self.sesv2_backend.create_import_job(
            import_destination=params.get("ImportDestination", {}),
            import_data_source=params.get("ImportDataSource", {}),
        )
        return json.dumps({"JobId": job_id})

    def get_import_job(self) -> str:
        job_id = self._get_param("JobId")
        job = self.sesv2_backend.get_import_job(job_id)
        return json.dumps(job.to_full_dict())

    def list_import_jobs(self) -> str:
        jobs = self.sesv2_backend.list_import_jobs()
        return json.dumps({"ImportJobs": [j.to_dict() for j in jobs]})

    # ===== Export Jobs =====

    def create_export_job(self) -> str:
        params = json.loads(self.body)
        job_id = self.sesv2_backend.create_export_job(
            export_data_source=params.get("ExportDataSource", {}),
            export_destination=params.get("ExportDestination", {}),
        )
        return json.dumps({"JobId": job_id})

    def get_export_job(self) -> str:
        job_id = self._get_param("JobId")
        job = self.sesv2_backend.get_export_job(job_id)
        return json.dumps(job.to_full_dict())

    def list_export_jobs(self) -> str:
        jobs = self.sesv2_backend.list_export_jobs()
        return json.dumps({"ExportJobs": [j.to_dict() for j in jobs]})

    def cancel_export_job(self) -> str:
        job_id = self._get_param("JobId")
        self.sesv2_backend.cancel_export_job(job_id)
        return json.dumps({})

    # ===== Insights =====

    def get_message_insights(self) -> str:
        message_id = self._get_param("MessageId")
        result = self.sesv2_backend.get_message_insights(message_id)
        return json.dumps(result)

    def get_email_address_insights(self) -> str:
        params = json.loads(self.body)
        result = self.sesv2_backend.get_email_address_insights(
            email_address=params.get("EmailAddress", "")
        )
        return json.dumps(result)

    # ===== Recommendations =====

    def list_recommendations(self) -> str:
        recommendations = self.sesv2_backend.list_recommendations()
        return json.dumps({"Recommendations": recommendations})

    # ===== Metrics =====

    def batch_get_metric_data(self) -> str:
        params = json.loads(self.body)
        results = self.sesv2_backend.batch_get_metric_data(
            queries=params.get("Queries", [])
        )
        return json.dumps({"Results": results})

    # ===== Tenants =====

    def create_tenant(self) -> str:
        params = json.loads(self.body)
        result = self.sesv2_backend.create_tenant(params)
        return json.dumps(result)

    def delete_tenant(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.delete_tenant(params)
        return json.dumps({})

    def get_tenant(self) -> str:
        params = json.loads(self.body)
        result = self.sesv2_backend.get_tenant(params)
        return json.dumps(result)

    def list_tenants(self) -> str:
        return json.dumps({"Tenants": self.sesv2_backend.list_tenants()})

    def create_tenant_resource_association(self) -> str:
        params = json.loads(self.body)
        result = self.sesv2_backend.create_tenant_resource_association(params)
        return json.dumps(result)

    def delete_tenant_resource_association(self) -> str:
        params = json.loads(self.body)
        self.sesv2_backend.delete_tenant_resource_association(params)
        return json.dumps({})

    def list_tenant_resources(self) -> str:
        params = json.loads(self.body)
        result = self.sesv2_backend.list_tenant_resources(params)
        return json.dumps({"TenantResources": result})

    def list_resource_tenants(self) -> str:
        params = json.loads(self.body)
        result = self.sesv2_backend.list_resource_tenants(params)
        return json.dumps({"ResourceTenants": result})

    # ===== Reputation Entities =====

    def get_reputation_entity(self) -> str:
        entity_type = self._get_param("ReputationEntityType")
        entity_reference = self._get_param("ReputationEntityReference")
        result = self.sesv2_backend.get_reputation_entity(entity_type, entity_reference)
        return json.dumps(result)

    def list_reputation_entities(self) -> str:
        result = self.sesv2_backend.list_reputation_entities()
        return json.dumps({"ReputationEntities": result})

    def update_reputation_entity_customer_managed_status(self) -> str:
        entity_type = self._get_param("ReputationEntityType")
        entity_reference = self._get_param("ReputationEntityReference")
        params = json.loads(self.body)
        self.sesv2_backend.update_reputation_entity_customer_managed_status(
            entity_type=entity_type,
            entity_reference=entity_reference,
            customer_managed_status=params.get("CustomerManagedStatus", "DISABLED"),
        )
        return json.dumps({})

    def update_reputation_entity_policy(self) -> str:
        entity_type = self._get_param("ReputationEntityType")
        entity_reference = self._get_param("ReputationEntityReference")
        params = json.loads(self.body)
        self.sesv2_backend.update_reputation_entity_policy(
            entity_type=entity_type,
            entity_reference=entity_reference,
            policy=params.get("Policy", ""),
        )
        return json.dumps({})
