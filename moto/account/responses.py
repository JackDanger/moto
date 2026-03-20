"""Handles incoming account requests, invokes methods, returns responses."""

from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .exceptions import UnknownContactType
from .models import ALLOWED_CONTACT_TYPES, account_backends


class AccountResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="account")

    def put_alternate_contact(self) -> ActionResult:
        account_id = self._get_account_id()
        alternate_contact_type = self._get_contact_type(account_id)
        email_address = self._get_param("EmailAddress")
        name = self._get_param("Name")
        phone_number = self._get_param("PhoneNumber")
        title = self._get_param("Title")

        backend = account_backends[account_id or self.current_account][self.partition]

        backend.put_alternate_contact(
            alternate_contact_type=alternate_contact_type,
            email_address=email_address,
            name=name,
            phone_number=phone_number,
            title=title,
        )
        return EmptyResult()

    def get_alternate_contact(self) -> ActionResult:
        account_id = self._get_account_id()
        alternate_contact_type = self._get_contact_type(account_id)

        backend = account_backends[account_id][self.partition]

        contact = backend.get_alternate_contact(
            alternate_contact_type=alternate_contact_type
        )
        return ActionResult(result={"AlternateContact": contact})

    def delete_alternate_contact(self) -> EmptyResult:
        account_id = self._get_account_id()
        alternate_contact_type = self._get_contact_type(account_id)

        backend = account_backends[account_id][self.partition]

        backend.delete_alternate_contact(alternate_contact_type=alternate_contact_type)
        return EmptyResult()

    def get_account_information(self) -> ActionResult:
        account_id = self._get_account_id()
        backend = account_backends[account_id][self.partition]
        result = backend.get_account_information()
        return ActionResult(result)

    def get_contact_information(self) -> ActionResult:
        account_id = self._get_account_id()
        backend = account_backends[account_id][self.partition]
        result = backend.get_contact_information()
        return ActionResult(result)

    def put_contact_information(self) -> ActionResult:
        account_id = self._get_account_id()
        full_name = self._get_param("ContactInformation", {}).get("FullName", "")
        address_line_1 = self._get_param("ContactInformation", {}).get("AddressLine1", "")
        city = self._get_param("ContactInformation", {}).get("City", "")
        state_or_region = self._get_param("ContactInformation", {}).get("StateOrRegion", "")
        postal_code = self._get_param("ContactInformation", {}).get("PostalCode", "")
        country_code = self._get_param("ContactInformation", {}).get("CountryCode", "US")
        phone_number = self._get_param("ContactInformation", {}).get("PhoneNumber", "")
        backend = account_backends[account_id][self.partition]
        backend.put_contact_information(
            full_name=full_name,
            address_line_1=address_line_1,
            city=city,
            state_or_region=state_or_region,
            postal_code=postal_code,
            country_code=country_code,
            phone_number=phone_number,
        )
        return EmptyResult()

    def get_gov_cloud_account_information(self) -> ActionResult:
        # GovCloud is not supported in mock - return empty
        account_id = self._get_account_id()
        backend = account_backends[account_id][self.partition]
        result = backend.get_gov_cloud_account_information()
        return ActionResult(result)

    def get_primary_email(self) -> ActionResult:
        account_id = self._get_account_id()
        backend = account_backends[account_id][self.partition]
        result = backend.get_primary_email()
        return ActionResult(result)

    def get_region_opt_status(self) -> ActionResult:
        region_name = self._get_param("RegionName", self.region)
        account_id = self._get_account_id()
        backend = account_backends[account_id][self.partition]
        result = backend.get_region_opt_status(region_name=region_name)
        return ActionResult(result)

    def enable_region(self) -> ActionResult:
        region_name = self._get_param("RegionName", self.region)
        account_id = self._get_account_id()
        backend = account_backends[account_id][self.partition]
        backend.enable_region(region_name=region_name)
        return EmptyResult()

    def disable_region(self) -> ActionResult:
        region_name = self._get_param("RegionName", self.region)
        account_id = self._get_account_id()
        backend = account_backends[account_id][self.partition]
        backend.disable_region(region_name=region_name)
        return EmptyResult()

    def list_regions(self) -> ActionResult:
        region_opt_status_contains = self._get_param("RegionOptStatusContains", [])
        account_id = self._get_account_id()
        backend = account_backends[account_id][self.partition]
        result = backend.list_regions(region_opt_status_contains=region_opt_status_contains)
        return ActionResult(result)

    def _get_account_id(self) -> str:
        return self._get_param("AccountId") or self.current_account

    def _get_contact_type(self, account_id: str) -> str:
        alternate_contact_type = self._get_param("AlternateContactType")
        if alternate_contact_type not in ALLOWED_CONTACT_TYPES:
            from moto.sts.models import STSBackend, sts_backends

            access_key_id = self.get_access_key()
            sts_backend: STSBackend = sts_backends[account_id][self.partition]
            _, user_arn, _ = sts_backend.get_caller_identity(access_key_id, self.region)
            raise UnknownContactType(user_arn, action="GetAlternateContact")
        return alternate_contact_type
