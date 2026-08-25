"""AccountBackend class with methods for supported APIs."""

from dataclasses import dataclass, field
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.utils import PARTITION_NAMES

from .exceptions import UnspecifiedContactType

ALLOWED_CONTACT_TYPES = ["SECURITY", "OPERATIONS", "BILLING"]

# Standard AWS regions with default opt-in status
_DEFAULT_REGIONS = [
    ("us-east-1", "ENABLED"),
    ("us-east-2", "ENABLED"),
    ("us-west-1", "ENABLED"),
    ("us-west-2", "ENABLED"),
    ("ap-south-1", "ENABLED"),
    ("ap-northeast-1", "ENABLED"),
    ("ap-northeast-2", "ENABLED"),
    ("ap-northeast-3", "ENABLED"),
    ("ap-southeast-1", "ENABLED"),
    ("ap-southeast-2", "ENABLED"),
    ("ca-central-1", "ENABLED"),
    ("eu-central-1", "ENABLED"),
    ("eu-west-1", "ENABLED"),
    ("eu-west-2", "ENABLED"),
    ("eu-west-3", "ENABLED"),
    ("eu-north-1", "ENABLED"),
    ("sa-east-1", "ENABLED"),
    # Opt-in regions
    ("ap-east-1", "DISABLED"),
    ("ap-south-2", "DISABLED"),
    ("ap-southeast-3", "DISABLED"),
    ("ap-southeast-4", "DISABLED"),
    ("ca-west-1", "DISABLED"),
    ("eu-central-2", "DISABLED"),
    ("eu-south-1", "DISABLED"),
    ("eu-south-2", "DISABLED"),
    ("il-central-1", "DISABLED"),
    ("me-central-1", "DISABLED"),
    ("me-south-1", "DISABLED"),
    ("mx-central-1", "DISABLED"),
]


@dataclass
class AlternateContact(BaseModel):
    alternate_contact_type: str
    title: str
    name: str
    email_address: str
    phone_number: str


@dataclass
class ContactInformation(BaseModel):
    full_name: str = ""
    address_line_1: str = ""
    city: str = ""
    state_or_region: str = ""
    postal_code: str = ""
    country_code: str = "US"
    phone_number: str = ""


class AccountBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self._alternate_contacts: dict[str, AlternateContact] = {}
        self._contact_information: Optional[ContactInformation] = None
        self._region_opt_status: dict[str, str] = dict(_DEFAULT_REGIONS)
        self._account_name: Optional[str] = None
        self._pending_primary_email: Optional[str] = None

    def put_alternate_contact(
        self,
        alternate_contact_type: str,
        email_address: str,
        name: str,
        phone_number: str,
        title: str,
    ) -> None:
        self._alternate_contacts[alternate_contact_type] = AlternateContact(
            alternate_contact_type=alternate_contact_type,
            name=name,
            title=title,
            email_address=email_address,
            phone_number=phone_number,
        )

    def get_alternate_contact(self, alternate_contact_type: str) -> AlternateContact:
        if alternate_contact_type not in self._alternate_contacts:
            raise UnspecifiedContactType
        return self._alternate_contacts[alternate_contact_type]

    def delete_alternate_contact(self, alternate_contact_type: str) -> None:
        self._alternate_contacts.pop(alternate_contact_type, None)

    def get_account_information(self) -> dict[str, Any]:
        return {
            "AccountId": self.account_id,
            "AccountName": f"Account {self.account_id}",
            "AccountType": "Standard",
        }

    def get_contact_information(self) -> dict[str, Any]:
        if self._contact_information is None:
            return {
                "ContactInformation": {
                    "FullName": "",
                    "AddressLine1": "",
                    "City": "",
                    "PostalCode": "",
                    "CountryCode": "US",
                    "PhoneNumber": "",
                }
            }
        ci = self._contact_information
        return {
            "ContactInformation": {
                "FullName": ci.full_name,
                "AddressLine1": ci.address_line_1,
                "City": ci.city,
                "StateOrRegion": ci.state_or_region,
                "PostalCode": ci.postal_code,
                "CountryCode": ci.country_code,
                "PhoneNumber": ci.phone_number,
            }
        }

    def put_contact_information(
        self,
        full_name: str,
        address_line_1: str,
        city: str,
        state_or_region: str,
        postal_code: str,
        country_code: str,
        phone_number: str,
    ) -> None:
        self._contact_information = ContactInformation(
            full_name=full_name,
            address_line_1=address_line_1,
            city=city,
            state_or_region=state_or_region,
            postal_code=postal_code,
            country_code=country_code,
            phone_number=phone_number,
        )

    def get_gov_cloud_account_information(self) -> dict[str, Any]:
        # GovCloud pairing is not simulated; return empty
        return {}

    def get_primary_email(self) -> dict[str, Any]:
        return {"PrimaryEmail": f"account-{self.account_id}@example.com"}

    def get_region_opt_status(self, region_name: str) -> dict[str, Any]:
        status = self._region_opt_status.get(region_name, "ENABLED")
        return {"RegionName": region_name, "RegionOptStatus": status}

    def enable_region(self, region_name: str) -> None:
        self._region_opt_status[region_name] = "ENABLED"

    def disable_region(self, region_name: str) -> None:
        self._region_opt_status[region_name] = "DISABLED"

    def list_regions(
        self, region_opt_status_contains: Optional[list[str]] = None
    ) -> dict[str, Any]:
        regions = []
        for region_name, status in self._region_opt_status.items():
            if region_opt_status_contains and status not in region_opt_status_contains:
                continue
            regions.append({"RegionName": region_name, "RegionOptStatus": status})
        return {"Regions": regions}

    def put_account_name(self, account_name: str) -> None:
        self._account_name = account_name

    def start_primary_email_update(self, primary_email: str) -> dict[str, Any]:
        self._pending_primary_email = primary_email
        return {}

    def accept_primary_email_update(self, otp: str, primary_email: str) -> dict[str, Any]:
        return {}


account_backends = BackendDict(
    AccountBackend,
    "account",
    use_boto3_regions=False,
    additional_regions=PARTITION_NAMES,
)
