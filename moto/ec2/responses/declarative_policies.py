from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class DeclarativePoliciesResponse(EC2BaseResponse):
    def describe_declarative_policies_reports(self) -> ActionResult:
        report_ids = self._get_param("ReportId", [])
        reports = self.ec2_backend.describe_declarative_policies_reports(
            report_ids=report_ids or None,
        )
        result = {
            "Reports": [
                {
                    "ReportId": report.id,
                    "TargetId": report.target_id,
                    "Status": report.status,
                    "StartTime": report.start_time,
                    "EndTime": report.end_time,
                }
                for report in reports
            ]
        }
        return ActionResult(result)

    def get_declarative_policies_report_summary(self) -> ActionResult:
        report_id = self._get_param("ReportId")
        report = self.ec2_backend.get_declarative_policies_report_summary(
            report_id=report_id,
        )
        result = {}
        if report:
            result = {
                "ReportId": report.id,
                "TargetId": report.target_id,
                "Status": report.status,
                "StartTime": report.start_time,
                "EndTime": report.end_time,
            }
        return ActionResult(result)

    def get_declarative_policies_report(self) -> ActionResult:
        report_id = self._get_param("ReportId")
        report = self.ec2_backend.get_declarative_policies_report(
            report_id=report_id,
        )
        result = {}
        if report:
            result = {
                "ReportId": report.id,
                "TargetId": report.target_id,
                "Status": report.status,
                "StartTime": report.start_time,
                "EndTime": report.end_time,
            }
        return ActionResult(result)
