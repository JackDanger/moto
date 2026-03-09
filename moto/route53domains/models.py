from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.utils import iso_8601_datetime_with_milliseconds
from moto.moto_api._internal import mock_random
from moto.route53 import route53_backends
from moto.route53.models import Route53Backend
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import PARTITION_NAMES

from .exceptions import (
    DomainLimitExceededException,
    DuplicateRequestException,
    InvalidInputException,
    OperationLimitExceededException,
)
from .validators import (
    DOMAIN_OPERATION_STATUSES,
    DOMAIN_OPERATION_TYPES,
    DomainFilterField,
    DomainsFilter,
    DomainSortOrder,
    DomainsSortCondition,
    NameServer,
    Route53Domain,
    Route53DomainsContactDetail,
    Route53DomainsOperation,
    ValidationException,
)


class Route53DomainsBackend(BaseBackend):
    """Implementation of Route53Domains APIs."""

    DEFAULT_MAX_DOMAINS_COUNT = 20
    PAGINATION_MODEL = {
        "list_domains": {
            "input_token": "marker",
            "limit_key": "max_items",
            "limit_default": 20,
            "unique_attribute": "domain_name",
        },
        "list_operations": {
            "input_token": "marker",
            "limit_key": "max_items",
            "limit_default": 20,
            "unique_attribute": "id",
        },
    }

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.__route53_backend: Route53Backend = route53_backends[account_id][
            self.partition
        ]
        self.__domains: dict[str, Route53Domain] = {}
        self.__operations: dict[str, Route53DomainsOperation] = {}
        self.__domain_tags: dict[str, list[dict[str, str]]] = {}
        self.__pending_transfers: dict[str, dict[str, Any]] = {}
        self.__domain_transfer_locks: dict[str, bool] = {}
        self.__dnssec_keys: dict[str, list[dict[str, Any]]] = {}
        self.tagger = TaggingService()

    def register_domain(
        self,
        domain_name: str,
        duration_in_years: int,
        auto_renew: bool,
        admin_contact: dict[str, Any],
        registrant_contact: dict[str, Any],
        tech_contact: dict[str, Any],
        private_protect_admin_contact: bool,
        private_protect_registrant_contact: bool,
        private_protect_tech_contact: bool,
        extra_params: list[dict[str, Any]],
    ) -> Route53DomainsOperation:
        """Register a domain"""

        if len(self.__domains) == self.DEFAULT_MAX_DOMAINS_COUNT:
            raise DomainLimitExceededException()

        requested_operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="REGISTER_DOMAIN"
        )

        self.__validate_duplicate_operations(requested_operation)

        expiration_date = datetime.now(timezone.utc) + timedelta(
            days=365 * duration_in_years
        )

        try:
            domain = Route53Domain.validate(
                domain_name=domain_name,
                auto_renew=auto_renew,
                admin_contact=Route53DomainsContactDetail.validate_dict(admin_contact),
                registrant_contact=Route53DomainsContactDetail.validate_dict(
                    registrant_contact
                ),
                tech_contact=Route53DomainsContactDetail.validate_dict(tech_contact),
                admin_privacy=private_protect_admin_contact,
                registrant_privacy=private_protect_registrant_contact,
                tech_privacy=private_protect_tech_contact,
                expiration_date=expiration_date,
                extra_params=extra_params,
            )

        except ValidationException as e:
            raise InvalidInputException(e.errors)
        self.__operations[requested_operation.id] = requested_operation

        self.__route53_backend.create_hosted_zone(
            name=domain.domain_name, private_zone=False
        )

        self.__domains[domain_name] = domain
        self.__domain_transfer_locks[domain_name] = True
        return requested_operation

    def delete_domain(self, domain_name: str) -> Route53DomainsOperation:
        requested_operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="DELETE_DOMAIN"
        )
        self.__validate_duplicate_operations(requested_operation)

        input_errors: list[str] = []
        Route53Domain.validate_domain_name(domain_name, input_errors)

        if input_errors:
            raise InvalidInputException(input_errors)

        if domain_name not in self.__domains:
            raise InvalidInputException(
                [f"Domain {domain_name} isn't registered in the current account"]
            )

        self.__operations[requested_operation.id] = requested_operation
        del self.__domains[domain_name]
        self.__domain_tags.pop(domain_name, None)
        self.__domain_transfer_locks.pop(domain_name, None)
        self.__dnssec_keys.pop(domain_name, None)
        return requested_operation

    def __validate_duplicate_operations(
        self, requested_operation: Route53DomainsOperation
    ) -> None:
        for operation in self.__operations.values():
            if (
                operation.domain_name == requested_operation.domain_name
                and operation.type == requested_operation.type
            ):
                raise DuplicateRequestException()

    def _get_domain_or_raise(self, domain_name: str) -> Route53Domain:
        input_errors: list[str] = []
        Route53Domain.validate_domain_name(domain_name, input_errors)
        if input_errors:
            raise InvalidInputException(input_errors)
        if domain_name not in self.__domains:
            raise InvalidInputException(["Domain is not associated with this account"])
        return self.__domains[domain_name]

    def get_domain(self, domain_name: str) -> Route53Domain:
        return self._get_domain_or_raise(domain_name)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_domains(
        self,
        filter_conditions: Optional[list[dict[str, Any]]] = None,
        sort_condition: Optional[dict[str, Any]] = None,
    ) -> list[Route53Domain]:
        try:
            filters: list[DomainsFilter] = (
                [DomainsFilter.validate_dict(f) for f in filter_conditions]
                if filter_conditions
                else []
            )
            sort: Optional[DomainsSortCondition] = (
                DomainsSortCondition.validate_dict(sort_condition)
                if sort_condition
                else None
            )
        except ValidationException as e:
            raise InvalidInputException(e.errors)

        filter_fields = [f.name for f in filters]
        if sort and filter_fields and sort.name not in filter_fields:
            raise InvalidInputException(
                ["Sort condition must be the same as the filter condition"]
            )

        domains_to_return: list[Route53Domain] = []

        for domain in self.__domains.values():
            if all(f.filter(domain) for f in filters):
                domains_to_return.append(domain)

        if sort:
            if sort.name == DomainFilterField.DOMAIN_NAME:
                domains_to_return.sort(
                    key=lambda d: d.domain_name,
                    reverse=(sort.sort_order == DomainSortOrder.DESCENDING),
                )
            else:
                domains_to_return.sort(
                    key=lambda d: d.expiration_date,
                    reverse=(sort.sort_order == DomainSortOrder.DESCENDING),
                )

        return domains_to_return

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_operations(
        self,
        submitted_since_timestamp: Optional[int] = None,
        statuses: Optional[list[str]] = None,
        types: Optional[list[str]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> list[Route53DomainsOperation]:
        input_errors: list[str] = []
        statuses = statuses or []
        types = types or []

        if any(status not in DOMAIN_OPERATION_STATUSES for status in statuses):
            input_errors.append("Status is invalid")
        if any(type_ not in DOMAIN_OPERATION_TYPES for type_ in types):
            input_errors.append("Type is invalid")

        if input_errors:
            raise InvalidInputException(input_errors)

        submitted_since = (
            datetime.fromtimestamp(submitted_since_timestamp, timezone.utc)
            if submitted_since_timestamp
            else None
        )

        operations_to_return: list[Route53DomainsOperation] = []

        for operation in self.__operations.values():
            if statuses and operation.status not in statuses:
                continue

            if types and operation.type not in types:
                continue

            if submitted_since and operation.submitted_date < submitted_since:
                continue

            operations_to_return.append(operation)

        if sort_by == "SubmittedDate":
            operations_to_return.sort(
                key=lambda op: op.submitted_date,
                reverse=sort_order == DomainSortOrder.ASCENDING,
            )

        return operations_to_return

    def get_operation(self, operation_id: str) -> Route53DomainsOperation:
        if operation_id not in self.__operations:
            raise InvalidInputException(
                [f"Operation with id {operation_id} doesn't exist"]
            )

        return self.__operations[operation_id]

    def update_domain_nameservers(
        self, domain_name: str, nameservers: list[dict[str, Any]]
    ) -> Route53DomainsOperation:
        input_errors: list[str] = []
        Route53Domain.validate_domain_name(domain_name, input_errors)
        if len(nameservers) < 1:
            input_errors.append("Must supply nameservers")

        servers: list[NameServer] = []
        try:
            servers = [NameServer.validate_dict(obj) for obj in nameservers]
        except ValidationException as e:
            input_errors += e.errors

        for server in servers:
            if domain_name in server.name and not server.glue_ips:
                input_errors.append(
                    f"Must supply glue IPs for name server {server.name} because it is a subdomain of "
                    f"the domain"
                )

        if input_errors:
            raise InvalidInputException(input_errors)

        if domain_name not in self.__domains:
            raise InvalidInputException(
                [f"Domain {domain_name} is not registered to the current AWS account"]
            )

        requested_operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="UPDATE_NAMESERVER"
        )
        self.__validate_duplicate_operations(requested_operation)

        domain = self.__domains[domain_name]
        domain.nameservers = servers
        self.__operations[requested_operation.id] = requested_operation

        return requested_operation

    # --- New operations ---

    def check_domain_availability(self, domain_name: str) -> str:
        if domain_name in self.__domains:
            return "UNAVAILABLE"
        return "AVAILABLE"

    def check_domain_transferability(self, domain_name: str) -> dict[str, Any]:
        return {
            "Transferable": "TRANSFERABLE",
        }

    def get_domain_suggestions(
        self, domain_name: str, suggestion_count: int, only_available: bool
    ) -> list[dict[str, Any]]:
        base_name = domain_name.split(".")[0]
        tld = domain_name.split(".")[-1] if "." in domain_name else "com"
        suggestions = []
        suffixes = ["online", "site", "tech", "store", "shop", "app", "dev", "io", "co", "net"]
        for i, suffix in enumerate(suffixes):
            if len(suggestions) >= suggestion_count:
                break
            suggestions.append({
                "DomainName": f"{base_name}.{suffix}",
                "Availability": "AVAILABLE",
            })
        return suggestions[:suggestion_count]

    def transfer_domain(
        self,
        domain_name: str,
        duration_in_years: int,
        admin_contact: dict[str, Any],
        registrant_contact: dict[str, Any],
        tech_contact: dict[str, Any],
        auto_renew: bool = True,
        auth_code: Optional[str] = None,
        nameservers: Optional[list[dict[str, Any]]] = None,
        private_protect_admin_contact: bool = True,
        private_protect_registrant_contact: bool = True,
        private_protect_tech_contact: bool = True,
        extra_params: Optional[list[dict[str, Any]]] = None,
    ) -> Route53DomainsOperation:
        requested_operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="TRANSFER_IN_DOMAIN"
        )
        self.__validate_duplicate_operations(requested_operation)

        expiration_date = datetime.now(timezone.utc) + timedelta(days=365 * duration_in_years)

        try:
            domain = Route53Domain.validate(
                domain_name=domain_name,
                auto_renew=auto_renew,
                admin_contact=Route53DomainsContactDetail.validate_dict(admin_contact),
                registrant_contact=Route53DomainsContactDetail.validate_dict(registrant_contact),
                tech_contact=Route53DomainsContactDetail.validate_dict(tech_contact),
                admin_privacy=private_protect_admin_contact,
                registrant_privacy=private_protect_registrant_contact,
                tech_privacy=private_protect_tech_contact,
                expiration_date=expiration_date,
                nameservers=nameservers,
                extra_params=extra_params,
            )
        except ValidationException as e:
            raise InvalidInputException(e.errors)

        self.__operations[requested_operation.id] = requested_operation
        self.__domains[domain_name] = domain
        self.__domain_transfer_locks[domain_name] = True
        return requested_operation

    def transfer_domain_to_another_aws_account(
        self, domain_name: str, account_id: str
    ) -> dict[str, Any]:
        self._get_domain_or_raise(domain_name)
        password = str(mock_random.uuid4())[:12]
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="INTERNAL_TRANSFER_OUT_DOMAIN"
        )
        self.__operations[operation.id] = operation
        self.__pending_transfers[domain_name] = {
            "account_id": account_id,
            "password": password,
            "operation_id": operation.id,
        }
        return {"OperationId": operation.id, "Password": password}

    def accept_domain_transfer_from_another_aws_account(
        self, domain_name: str, password: str
    ) -> str:
        if domain_name not in self.__pending_transfers:
            raise InvalidInputException(
                [f"No pending transfer for domain {domain_name}"]
            )
        transfer = self.__pending_transfers[domain_name]
        if transfer["password"] != password:
            raise InvalidInputException(["Invalid password for transfer"])
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="INTERNAL_TRANSFER_IN_DOMAIN"
        )
        self.__operations[operation.id] = operation
        del self.__pending_transfers[domain_name]
        return operation.id

    def reject_domain_transfer_from_another_aws_account(
        self, domain_name: str
    ) -> str:
        self.__pending_transfers.pop(domain_name, None)
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="INTERNAL_TRANSFER_IN_DOMAIN"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def cancel_domain_transfer_to_another_aws_account(
        self, domain_name: str
    ) -> str:
        self.__pending_transfers.pop(domain_name, None)
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="INTERNAL_TRANSFER_OUT_DOMAIN"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def enable_domain_auto_renew(self, domain_name: str) -> None:
        domain = self._get_domain_or_raise(domain_name)
        domain.auto_renew = True

    def disable_domain_auto_renew(self, domain_name: str) -> None:
        domain = self._get_domain_or_raise(domain_name)
        domain.auto_renew = False

    def enable_domain_transfer_lock(self, domain_name: str) -> str:
        self._get_domain_or_raise(domain_name)
        self.__domain_transfer_locks[domain_name] = True
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="DOMAIN_LOCK"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def disable_domain_transfer_lock(self, domain_name: str) -> str:
        self._get_domain_or_raise(domain_name)
        self.__domain_transfer_locks[domain_name] = False
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="DOMAIN_LOCK"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def update_domain_contact(
        self,
        domain_name: str,
        admin_contact: Optional[dict[str, Any]] = None,
        registrant_contact: Optional[dict[str, Any]] = None,
        tech_contact: Optional[dict[str, Any]] = None,
        consent: Optional[dict[str, Any]] = None,
        billing_contact: Optional[dict[str, Any]] = None,
    ) -> str:
        domain = self._get_domain_or_raise(domain_name)
        try:
            if admin_contact:
                domain.admin_contact = Route53DomainsContactDetail.validate_dict(admin_contact)
            if registrant_contact:
                domain.registrant_contact = Route53DomainsContactDetail.validate_dict(registrant_contact)
            if tech_contact:
                domain.tech_contact = Route53DomainsContactDetail.validate_dict(tech_contact)
        except ValidationException as e:
            raise InvalidInputException(e.errors)
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="UPDATE_DOMAIN_CONTACT"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def update_domain_contact_privacy(
        self,
        domain_name: str,
        admin_privacy: Optional[bool] = None,
        registrant_privacy: Optional[bool] = None,
        tech_privacy: Optional[bool] = None,
    ) -> str:
        domain = self._get_domain_or_raise(domain_name)
        if admin_privacy is not None:
            domain.admin_privacy = admin_privacy
        if registrant_privacy is not None:
            domain.registrant_privacy = registrant_privacy
        if tech_privacy is not None:
            domain.tech_privacy = tech_privacy
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="CHANGE_PRIVACY_PROTECTION"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def get_contact_reachability_status(
        self, domain_name: Optional[str] = None
    ) -> dict[str, Any]:
        return {
            "domainName": domain_name or "",
            "status": "DONE",
        }

    def resend_contact_reachability_email(
        self, domain_name: Optional[str] = None
    ) -> dict[str, Any]:
        return {
            "domainName": domain_name or "",
            "emailAddress": "registrant@example.com",
            "isAlreadyVerified": True,
        }

    def resend_operation_authorization(self, operation_id: str) -> None:
        if operation_id not in self.__operations:
            raise InvalidInputException(
                [f"Operation with id {operation_id} doesn't exist"]
            )

    def retrieve_domain_auth_code(self, domain_name: str) -> str:
        self._get_domain_or_raise(domain_name)
        return str(mock_random.uuid4())[:12]

    def renew_domain(
        self, domain_name: str, current_expiry_year: int, duration_in_years: int = 1
    ) -> str:
        domain = self._get_domain_or_raise(domain_name)
        domain.expiration_date = domain.expiration_date + timedelta(days=365 * duration_in_years)
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="RENEW_DOMAIN"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def list_tags_for_domain(self, domain_name: str) -> list[dict[str, str]]:
        return self.__domain_tags.get(domain_name, [])

    def update_tags_for_domain(
        self, domain_name: str, tags_to_update: Optional[list[dict[str, str]]] = None
    ) -> None:
        if tags_to_update is None:
            return
        existing = self.__domain_tags.get(domain_name, [])
        tag_dict = {t["Key"]: t.get("Value", "") for t in existing}
        for tag in tags_to_update:
            tag_dict[tag["Key"]] = tag.get("Value", "")
        self.__domain_tags[domain_name] = [
            {"Key": k, "Value": v} for k, v in tag_dict.items()
        ]

    def delete_tags_for_domain(
        self, domain_name: str, tags_to_delete: list[str]
    ) -> None:
        existing = self.__domain_tags.get(domain_name, [])
        self.__domain_tags[domain_name] = [
            t for t in existing if t["Key"] not in tags_to_delete
        ]

    def list_prices(
        self, tld: Optional[str] = None
    ) -> list[dict[str, Any]]:
        # Return a stub price list
        tlds = [tld] if tld else ["com", "net", "org", "io", "info"]
        prices = []
        for t in tlds:
            prices.append({
                "Name": t,
                "RegistrationPrice": {"Price": 12.0, "Currency": "USD"},
                "TransferPrice": {"Price": 12.0, "Currency": "USD"},
                "RenewalPrice": {"Price": 12.0, "Currency": "USD"},
                "ChangeOwnershipPrice": {"Price": 12.0, "Currency": "USD"},
                "RestorationPrice": {"Price": 80.0, "Currency": "USD"},
            })
        return prices

    def associate_delegation_signer_to_domain(
        self, domain_name: str, signing_attributes: dict[str, Any]
    ) -> str:
        self._get_domain_or_raise(domain_name)
        key_id = str(mock_random.uuid4())
        if domain_name not in self.__dnssec_keys:
            self.__dnssec_keys[domain_name] = []
        self.__dnssec_keys[domain_name].append({
            "id": key_id,
            **signing_attributes,
        })
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="ADD_DNSSEC"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def disassociate_delegation_signer_from_domain(
        self, domain_name: str, signer_id: str
    ) -> str:
        self._get_domain_or_raise(domain_name)
        if domain_name in self.__dnssec_keys:
            self.__dnssec_keys[domain_name] = [
                k for k in self.__dnssec_keys[domain_name] if k.get("id") != signer_id
            ]
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="REMOVE_DNSSEC"
        )
        self.__operations[operation.id] = operation
        return operation.id

    def push_domain(self, domain_name: str, target: str) -> None:
        self._get_domain_or_raise(domain_name)
        operation = Route53DomainsOperation.validate(
            domain_name=domain_name, status="SUCCESSFUL", type_="PUSH_DOMAIN"
        )
        self.__operations[operation.id] = operation
        del self.__domains[domain_name]

    def view_billing(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> list[dict[str, Any]]:
        return []


route53domains_backends = BackendDict(
    Route53DomainsBackend,
    "route53domains",
    use_boto3_regions=False,
    additional_regions=PARTITION_NAMES,
)
