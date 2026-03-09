import json
from typing import Any

from moto.core.responses import BaseResponse
from moto.route53domains.models import Route53DomainsBackend, route53domains_backends
from moto.route53domains.validators import Route53Domain, Route53DomainsOperation


class Route53DomainsResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="route53-domains")

    @property
    def route53domains_backend(self) -> Route53DomainsBackend:
        return route53domains_backends[self.current_account][self.partition]

    def register_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        duration_in_years = self._get_int_param("DurationInYears")
        auto_renew = self._get_bool_param("AutoRenew", if_none=True)
        admin_contact = self._get_param("AdminContact")
        registrant_contact = self._get_param("RegistrantContact")
        tech_contact = self._get_param("TechContact")
        privacy_protection_admin_contact = self._get_bool_param(
            "PrivacyProtectAdminContact", if_none=True
        )
        privacy_protection_registrant_contact = self._get_bool_param(
            "PrivacyProtectRegistrantContact", if_none=True
        )
        privacy_protection_tech_contact = self._get_bool_param(
            "PrivacyProtectTechContact", if_none=True
        )
        extra_params = self._get_param("ExtraParams")

        operation = self.route53domains_backend.register_domain(
            domain_name=domain_name,
            duration_in_years=duration_in_years,
            auto_renew=auto_renew,
            admin_contact=admin_contact,
            registrant_contact=registrant_contact,
            tech_contact=tech_contact,
            private_protect_admin_contact=privacy_protection_admin_contact,
            private_protect_registrant_contact=privacy_protection_registrant_contact,
            private_protect_tech_contact=privacy_protection_tech_contact,
            extra_params=extra_params,
        )

        return json.dumps({"OperationId": operation.id})

    def delete_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        operation = self.route53domains_backend.delete_domain(domain_name)

        return json.dumps({"OperationId": operation.id})

    def get_domain_detail(self) -> str:
        domain_name = self._get_param("DomainName")

        return json.dumps(
            self.route53domains_backend.get_domain(domain_name=domain_name).to_json()
        )

    def list_domains(self) -> str:
        filter_conditions = self._get_param("FilterConditions")
        sort_condition = self._get_param("SortCondition")
        marker = self._get_param("Marker")
        max_items = self._get_param("MaxItems")
        domains, marker = self.route53domains_backend.list_domains(
            filter_conditions=filter_conditions,
            sort_condition=sort_condition,
            marker=marker,
            max_items=max_items,
        )
        res = {
            "Domains": list(map(self.__map_domains_to_info, domains)),
            "NextPageMarker": marker,
        }
        return json.dumps(res)

    @staticmethod
    def __map_domains_to_info(domain: Route53Domain) -> dict[str, Any]:  # type: ignore[misc]
        return {
            "DomainName": domain.domain_name,
            "AutoRenew": domain.auto_renew,
            "Expiry": domain.expiration_date.timestamp(),
            "TransferLock": True,
        }

    def list_operations(self) -> str:
        submitted_since_timestamp = self._get_int_param("SubmittedSince")
        max_items = self._get_int_param("MaxItems")
        statuses = self._get_param("Status")
        marker = self._get_param("Marker")
        types = self._get_param("Type")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")

        operations, marker = self.route53domains_backend.list_operations(
            submitted_since_timestamp=submitted_since_timestamp,
            max_items=max_items,
            marker=marker,
            statuses=statuses,
            types=types,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        res = {
            "Operations": [operation.to_json() for operation in operations],
            "NextPageMarker": marker,
        }
        return json.dumps(res)

    def get_operation_detail(self) -> str:
        operation_id = self._get_param("OperationId")
        operation: Route53DomainsOperation = self.route53domains_backend.get_operation(
            operation_id
        )

        return json.dumps(operation.to_json())

    def update_domain_nameservers(self) -> str:
        domain_name = self._get_param("DomainName")
        nameservers = self._get_param("Nameservers")

        operation: Route53DomainsOperation = (
            self.route53domains_backend.update_domain_nameservers(
                domain_name=domain_name, nameservers=nameservers
            )
        )

        return json.dumps({"OperationId": operation.id})

    # --- New operations ---

    def check_domain_availability(self) -> str:
        domain_name = self._get_param("DomainName")
        availability = self.route53domains_backend.check_domain_availability(
            domain_name=domain_name,
        )
        return json.dumps({"Availability": availability})

    def check_domain_transferability(self) -> str:
        domain_name = self._get_param("DomainName")
        result = self.route53domains_backend.check_domain_transferability(
            domain_name=domain_name,
        )
        return json.dumps({"Transferability": result, "Message": ""})

    def get_domain_suggestions(self) -> str:
        domain_name = self._get_param("DomainName")
        suggestion_count = self._get_int_param("SuggestionCount")
        only_available = self._get_bool_param("OnlyAvailable")
        suggestions = self.route53domains_backend.get_domain_suggestions(
            domain_name=domain_name,
            suggestion_count=suggestion_count,
            only_available=only_available,
        )
        return json.dumps({"SuggestionsList": suggestions})

    def transfer_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        duration_in_years = self._get_int_param("DurationInYears")
        admin_contact = self._get_param("AdminContact")
        registrant_contact = self._get_param("RegistrantContact")
        tech_contact = self._get_param("TechContact")
        auto_renew = self._get_bool_param("AutoRenew", if_none=True)
        auth_code = self._get_param("AuthCode")
        nameservers = self._get_param("Nameservers")
        privacy_protect_admin = self._get_bool_param("PrivacyProtectAdminContact", if_none=True)
        privacy_protect_registrant = self._get_bool_param("PrivacyProtectRegistrantContact", if_none=True)
        privacy_protect_tech = self._get_bool_param("PrivacyProtectTechContact", if_none=True)
        extra_params = self._get_param("ExtraParams")
        operation = self.route53domains_backend.transfer_domain(
            domain_name=domain_name,
            duration_in_years=duration_in_years,
            admin_contact=admin_contact,
            registrant_contact=registrant_contact,
            tech_contact=tech_contact,
            auto_renew=auto_renew,
            auth_code=auth_code,
            nameservers=nameservers,
            private_protect_admin_contact=privacy_protect_admin,
            private_protect_registrant_contact=privacy_protect_registrant,
            private_protect_tech_contact=privacy_protect_tech,
            extra_params=extra_params,
        )
        return json.dumps({"OperationId": operation.id})

    def transfer_domain_to_another_aws_account(self) -> str:
        domain_name = self._get_param("DomainName")
        account_id = self._get_param("AccountId")
        result = self.route53domains_backend.transfer_domain_to_another_aws_account(
            domain_name=domain_name,
            account_id=account_id,
        )
        return json.dumps(result)

    def accept_domain_transfer_from_another_aws_account(self) -> str:
        domain_name = self._get_param("DomainName")
        password = self._get_param("Password")
        operation_id = self.route53domains_backend.accept_domain_transfer_from_another_aws_account(
            domain_name=domain_name,
            password=password,
        )
        return json.dumps({"OperationId": operation_id})

    def reject_domain_transfer_from_another_aws_account(self) -> str:
        domain_name = self._get_param("DomainName")
        operation_id = self.route53domains_backend.reject_domain_transfer_from_another_aws_account(
            domain_name=domain_name,
        )
        return json.dumps({"OperationId": operation_id})

    def cancel_domain_transfer_to_another_aws_account(self) -> str:
        domain_name = self._get_param("DomainName")
        operation_id = self.route53domains_backend.cancel_domain_transfer_to_another_aws_account(
            domain_name=domain_name,
        )
        return json.dumps({"OperationId": operation_id})

    def enable_domain_auto_renew(self) -> str:
        domain_name = self._get_param("DomainName")
        self.route53domains_backend.enable_domain_auto_renew(domain_name=domain_name)
        return json.dumps({})

    def disable_domain_auto_renew(self) -> str:
        domain_name = self._get_param("DomainName")
        self.route53domains_backend.disable_domain_auto_renew(domain_name=domain_name)
        return json.dumps({})

    def enable_domain_transfer_lock(self) -> str:
        domain_name = self._get_param("DomainName")
        operation_id = self.route53domains_backend.enable_domain_transfer_lock(
            domain_name=domain_name,
        )
        return json.dumps({"OperationId": operation_id})

    def disable_domain_transfer_lock(self) -> str:
        domain_name = self._get_param("DomainName")
        operation_id = self.route53domains_backend.disable_domain_transfer_lock(
            domain_name=domain_name,
        )
        return json.dumps({"OperationId": operation_id})

    def update_domain_contact(self) -> str:
        domain_name = self._get_param("DomainName")
        admin_contact = self._get_param("AdminContact")
        registrant_contact = self._get_param("RegistrantContact")
        tech_contact = self._get_param("TechContact")
        consent = self._get_param("Consent")
        billing_contact = self._get_param("BillingContact")
        operation_id = self.route53domains_backend.update_domain_contact(
            domain_name=domain_name,
            admin_contact=admin_contact,
            registrant_contact=registrant_contact,
            tech_contact=tech_contact,
            consent=consent,
            billing_contact=billing_contact,
        )
        return json.dumps({"OperationId": operation_id})

    def update_domain_contact_privacy(self) -> str:
        domain_name = self._get_param("DomainName")
        admin_privacy = self._get_param("AdminPrivacy")
        registrant_privacy = self._get_param("RegistrantPrivacy")
        tech_privacy = self._get_param("TechPrivacy")
        operation_id = self.route53domains_backend.update_domain_contact_privacy(
            domain_name=domain_name,
            admin_privacy=admin_privacy,
            registrant_privacy=registrant_privacy,
            tech_privacy=tech_privacy,
        )
        return json.dumps({"OperationId": operation_id})

    def get_contact_reachability_status(self) -> str:
        domain_name = self._get_param("domainName")
        result = self.route53domains_backend.get_contact_reachability_status(
            domain_name=domain_name,
        )
        return json.dumps(result)

    def resend_contact_reachability_email(self) -> str:
        domain_name = self._get_param("domainName")
        result = self.route53domains_backend.resend_contact_reachability_email(
            domain_name=domain_name,
        )
        return json.dumps(result)

    def resend_operation_authorization(self) -> str:
        operation_id = self._get_param("OperationId")
        self.route53domains_backend.resend_operation_authorization(
            operation_id=operation_id,
        )
        return json.dumps({})

    def retrieve_domain_auth_code(self) -> str:
        domain_name = self._get_param("DomainName")
        auth_code = self.route53domains_backend.retrieve_domain_auth_code(
            domain_name=domain_name,
        )
        return json.dumps({"AuthCode": auth_code})

    def renew_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        current_expiry_year = self._get_int_param("CurrentExpiryYear")
        duration_in_years = self._get_int_param("DurationInYears") or 1
        operation_id = self.route53domains_backend.renew_domain(
            domain_name=domain_name,
            current_expiry_year=current_expiry_year,
            duration_in_years=duration_in_years,
        )
        return json.dumps({"OperationId": operation_id})

    def list_tags_for_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        tags = self.route53domains_backend.list_tags_for_domain(
            domain_name=domain_name,
        )
        return json.dumps({"TagList": tags})

    def update_tags_for_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        tags_to_update = self._get_param("TagsToUpdate")
        self.route53domains_backend.update_tags_for_domain(
            domain_name=domain_name,
            tags_to_update=tags_to_update,
        )
        return json.dumps({})

    def delete_tags_for_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        tags_to_delete = self._get_param("TagsToDelete")
        self.route53domains_backend.delete_tags_for_domain(
            domain_name=domain_name,
            tags_to_delete=tags_to_delete,
        )
        return json.dumps({})

    def list_prices(self) -> str:
        tld = self._get_param("Tld")
        prices = self.route53domains_backend.list_prices(tld=tld)
        return json.dumps({"Prices": prices, "NextPageMarker": None})

    def associate_delegation_signer_to_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        signing_attributes = self._get_param("SigningAttributes")
        operation_id = self.route53domains_backend.associate_delegation_signer_to_domain(
            domain_name=domain_name,
            signing_attributes=signing_attributes,
        )
        return json.dumps({"OperationId": operation_id})

    def disassociate_delegation_signer_from_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        signer_id = self._get_param("Id")
        operation_id = self.route53domains_backend.disassociate_delegation_signer_from_domain(
            domain_name=domain_name,
            signer_id=signer_id,
        )
        return json.dumps({"OperationId": operation_id})

    def push_domain(self) -> str:
        domain_name = self._get_param("DomainName")
        target = self._get_param("Target")
        self.route53domains_backend.push_domain(
            domain_name=domain_name,
            target=target,
        )
        return json.dumps({})

    def view_billing(self) -> str:
        start_time = self._get_param("Start")
        end_time = self._get_param("End")
        records = self.route53domains_backend.view_billing(
            start_time=start_time,
            end_time=end_time,
        )
        return json.dumps({"NextPageMarker": None, "BillingRecords": records})
