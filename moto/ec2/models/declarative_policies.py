from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_id


class DeclarativePoliciesReport:
    def __init__(
        self,
        ec2_backend: Any,
        target_id: str,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_id(prefix="dpr-")
        self.target_id = target_id
        self.s3_bucket = ""
        self.s3_prefix = ""
        self.status = "complete"
        self._created_at = utcnow()

    @property
    def start_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def end_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)


class DeclarativePoliciesBackend:
    def __init__(self) -> None:
        self.declarative_policies_reports: dict[str, DeclarativePoliciesReport] = {}

    def describe_declarative_policies_reports(
        self,
        report_ids: Optional[list[str]] = None,
    ) -> list[DeclarativePoliciesReport]:
        reports = list(self.declarative_policies_reports.values())
        if report_ids:
            reports = [r for r in reports if r.id in report_ids]
        return reports

    def get_declarative_policies_report_summary(
        self,
        report_id: str,
    ) -> Optional[DeclarativePoliciesReport]:
        return self.declarative_policies_reports.get(report_id)

    def get_declarative_policies_report(
        self,
        report_id: str,
    ) -> Optional[DeclarativePoliciesReport]:
        return self.declarative_policies_reports.get(report_id)
