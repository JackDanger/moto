from ._base_response import EC2BaseResponse


class DeclarativePoliciesResponse(EC2BaseResponse):
    def describe_declarative_policies_reports(self) -> str:
        report_ids = self._get_param("ReportId", [])
        reports = self.ec2_backend.describe_declarative_policies_reports(
            report_ids=report_ids or None,
        )
        template = self.response_template(DESCRIBE_DECLARATIVE_POLICIES_REPORTS)
        return template.render(reports=reports)

    def get_declarative_policies_report_summary(self) -> str:
        report_id = self._get_param("ReportId")
        report = self.ec2_backend.get_declarative_policies_report_summary(
            report_id=report_id,
        )
        template = self.response_template(GET_DECLARATIVE_POLICIES_REPORT_SUMMARY)
        return template.render(report=report)

    def get_declarative_policies_report(self) -> str:
        report_id = self._get_param("ReportId")
        report = self.ec2_backend.get_declarative_policies_report(
            report_id=report_id,
        )
        template = self.response_template(GET_DECLARATIVE_POLICIES_REPORT)
        return template.render(report=report)


DESCRIBE_DECLARATIVE_POLICIES_REPORTS = """<DescribeDeclarativePoliciesReportsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <reportSet>
    {% for report in reports %}
    <item>
      <reportId>{{ report.id }}</reportId>
      <targetId>{{ report.target_id }}</targetId>
      <status>{{ report.status }}</status>
      <startTime>{{ report.start_time }}</startTime>
      <endTime>{{ report.end_time }}</endTime>
    </item>
    {% endfor %}
  </reportSet>
</DescribeDeclarativePoliciesReportsResponse>"""

GET_DECLARATIVE_POLICIES_REPORT_SUMMARY = """<GetDeclarativePoliciesReportSummaryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  {% if report %}
  <reportId>{{ report.id }}</reportId>
  <targetId>{{ report.target_id }}</targetId>
  <status>{{ report.status }}</status>
  <startTime>{{ report.start_time }}</startTime>
  <endTime>{{ report.end_time }}</endTime>
  {% endif %}
</GetDeclarativePoliciesReportSummaryResponse>"""

GET_DECLARATIVE_POLICIES_REPORT = """<GetDeclarativePoliciesReportResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  {% if report %}
  <reportId>{{ report.id }}</reportId>
  <targetId>{{ report.target_id }}</targetId>
  <status>{{ report.status }}</status>
  <startTime>{{ report.start_time }}</startTime>
  <endTime>{{ report.end_time }}</endTime>
  {% endif %}
</GetDeclarativePoliciesReportResponse>"""
