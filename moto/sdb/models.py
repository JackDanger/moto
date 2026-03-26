"""SimpleDBBackend class with methods for supported APIs."""

import re
import time
from collections import defaultdict
from collections.abc import Iterable
from threading import Lock
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel

from .exceptions import InvalidDomainName, UnknownDomainName


class FakeItem(BaseModel):
    def __init__(self, name: str = "") -> None:
        self.name = name
        self.attributes: list[dict[str, Any]] = []
        self.lock = Lock()

    def get_attributes(self, names: Optional[list[str]]) -> list[dict[str, Any]]:
        if not names:
            return self.attributes
        return [attr for attr in self.attributes if attr["Name"] in names]

    def put_attributes(self, attributes: list[dict[str, Any]]) -> None:
        # Replacing attributes involves quite a few loops
        # Lock this, so we know noone else touches this list while we're operating on it
        with self.lock:
            for attr in attributes:
                if attr.get("Replace", False):
                    self._remove_attributes(attr["Name"])
                self.attributes.append(attr)

    def delete_attributes(self, attributes: Optional[list[dict[str, Any]]]) -> None:
        """Delete specific attributes, or all attributes if none specified."""
        with self.lock:
            if not attributes:
                self.attributes = []
                return
            for attr in attributes:
                name = attr.get("Name")
                value = attr.get("Value")
                if value is not None:
                    self.attributes = [
                        a
                        for a in self.attributes
                        if not (a["Name"] == name and a.get("Value") == value)
                    ]
                else:
                    self._remove_attributes(name)

    def _remove_attributes(self, name: str) -> None:
        self.attributes = [attr for attr in self.attributes if attr["Name"] != name]


class FakeDomain(BaseModel):
    def __init__(self, name: str):
        self.name = name
        self.items: dict[str, FakeItem] = defaultdict(lambda: FakeItem())
        self.created_at: float = time.time()

    def get(self, item_name: str, attribute_names: list[str]) -> list[dict[str, Any]]:
        item = self.items[item_name]
        return item.get_attributes(attribute_names)

    def put(self, item_name: str, attributes: list[dict[str, Any]]) -> None:
        item = self.items[item_name]
        item.put_attributes(attributes)

    def delete_item_attributes(
        self, item_name: str, attributes: Optional[list[dict[str, Any]]]
    ) -> None:
        if item_name not in self.items and not attributes:
            return
        item = self.items[item_name]
        item.delete_attributes(attributes)
        # Remove item entirely if it has no attributes left
        if not item.attributes:
            self.items.pop(item_name, None)

    def metadata(self) -> dict[str, Any]:
        """Return domain metadata statistics."""
        item_count = len(self.items)
        item_names_size = sum(len(name.encode("utf-8")) for name in self.items)
        attr_names: set[str] = set()
        attr_name_size = 0
        attr_value_count = 0
        attr_value_size = 0
        for item in self.items.values():
            for attr in item.attributes:
                name = attr.get("Name", "")
                value = attr.get("Value", "")
                attr_names.add(name)
                attr_value_count += 1
                attr_name_size += len(name.encode("utf-8"))
                attr_value_size += len(str(value).encode("utf-8"))
        return {
            "ItemCount": item_count,
            "ItemNamesSizeBytes": item_names_size,
            "AttributeNameCount": len(attr_names),
            "AttributeNamesSizeBytes": attr_name_size,
            "AttributeValueCount": attr_value_count,
            "AttributeValuesSizeBytes": attr_value_size,
            "Timestamp": int(self.created_at),
        }


class SimpleDBBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.domains: dict[str, FakeDomain] = {}

    def create_domain(self, domain_name: str) -> None:
        self._validate_domain_name(domain_name)
        self.domains[domain_name] = FakeDomain(name=domain_name)

    def list_domains(self) -> Iterable[str]:
        """
        The `max_number_of_domains` and `next_token` parameter have not been implemented yet - we simply return all domains.
        """
        return self.domains.keys()

    def delete_domain(self, domain_name: str) -> None:
        self._validate_domain_name(domain_name)
        # Ignore unknown domains - AWS does the same
        self.domains.pop(domain_name, None)

    def _validate_domain_name(self, domain_name: str) -> None:
        # Domain Name needs to have at least 3 chars
        # Can only contain characters: a-z, A-Z, 0-9, '_', '-', and '.'
        if not re.match("^[a-zA-Z0-9-_.]{3,}$", domain_name):
            raise InvalidDomainName(domain_name)

    def _get_domain(self, domain_name: str) -> FakeDomain:
        if domain_name not in self.domains:
            raise UnknownDomainName()
        return self.domains[domain_name]

    def get_attributes(
        self, domain_name: str, item_name: str, attribute_names: list[str]
    ) -> list[dict[str, Any]]:
        """
        Behaviour for the consistent_read-attribute is not yet implemented
        """
        self._validate_domain_name(domain_name)
        domain = self._get_domain(domain_name)
        return domain.get(item_name, attribute_names)

    def put_attributes(
        self, domain_name: str, item_name: str, attributes: list[dict[str, Any]]
    ) -> None:
        """
        Behaviour for the expected-attribute is not yet implemented.
        """
        self._validate_domain_name(domain_name)
        domain = self._get_domain(domain_name)
        domain.put(item_name, attributes)

    def delete_attributes(
        self,
        domain_name: str,
        item_name: str,
        attributes: Optional[list[dict[str, Any]]],
    ) -> None:
        """Delete specific attributes from an item, or the item entirely if none given."""
        self._validate_domain_name(domain_name)
        domain = self._get_domain(domain_name)
        domain.delete_item_attributes(item_name, attributes)

    def batch_put_attributes(
        self, domain_name: str, items: list[dict[str, Any]]
    ) -> None:
        """Put attributes for multiple items in a single call."""
        self._validate_domain_name(domain_name)
        domain = self._get_domain(domain_name)
        for item in items or []:
            item_name = item.get("Name", "")
            item_attrs = item.get("Attributes") or []
            domain.put(item_name, item_attrs)

    def batch_delete_attributes(
        self, domain_name: str, items: list[dict[str, Any]]
    ) -> None:
        """Delete attributes for multiple items in a single call."""
        self._validate_domain_name(domain_name)
        domain = self._get_domain(domain_name)
        for item in items or []:
            item_name = item.get("Name", "")
            item_attrs = item.get("Attributes")
            domain.delete_item_attributes(item_name, item_attrs)

    def domain_metadata(self, domain_name: str) -> dict[str, Any]:
        """Return metadata/statistics for a domain."""
        self._validate_domain_name(domain_name)
        domain = self._get_domain(domain_name)
        return domain.metadata()

    def select(self, select_expression: str) -> list[dict[str, Any]]:
        """
        Execute a SELECT expression and return matching items.
        Only simple 'SELECT * FROM domain' and 'SELECT attr FROM domain' patterns
        are supported.  Complex WHERE/ORDER BY clauses are not implemented.
        """
        expr = select_expression.strip()
        # Parse: SELECT <output_list> FROM `domain_name` [WHERE ...]
        match = re.match(
            r"(?i)select\s+(.+?)\s+from\s+[`'\"]?(\w+)[`'\"]?(?:\s+.*)?$", expr
        )
        if not match:
            return []
        domain_name = match.group(2)
        if domain_name not in self.domains:
            return []
        domain = self.domains[domain_name]
        results: list[dict[str, Any]] = []
        for item_name, item in domain.items.items():
            results.append({"Name": item_name, "Attributes": item.attributes})
        return results


sdb_backends = BackendDict(SimpleDBBackend, "sdb")
