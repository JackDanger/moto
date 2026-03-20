from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class NetworkInsightsAccessScopeResponse(EC2BaseResponse):
    def create_network_insights_access_scope(self) -> str:
        match_paths = self._get_param("MatchPath", [])
        exclude_paths = self._get_param("ExcludePath", [])
        client_token = self._get_param("ClientToken")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        scope = self.ec2_backend.create_network_insights_access_scope(
            match_paths=match_paths if isinstance(match_paths, list) else [match_paths],
            exclude_paths=exclude_paths
            if isinstance(exclude_paths, list)
            else [exclude_paths],
            client_token=client_token,
            tags=tags,
        )
        template = self.response_template(CREATE_NETWORK_INSIGHTS_ACCESS_SCOPE)
        return template.render(scope=scope)

    def delete_network_insights_access_scope(self) -> str:
        scope_id = self._get_param("NetworkInsightsAccessScopeId")
        scope = self.ec2_backend.delete_network_insights_access_scope(
            network_insights_access_scope_id=scope_id,
        )
        template = self.response_template(DELETE_NETWORK_INSIGHTS_ACCESS_SCOPE)
        return template.render(scope=scope)

    def describe_network_insights_access_scopes(self) -> str:
        scope_ids = self._get_param("NetworkInsightsAccessScopeId", [])
        scopes = self.ec2_backend.describe_network_insights_access_scopes(
            scope_ids=scope_ids or None,
        )
        template = self.response_template(DESCRIBE_NETWORK_INSIGHTS_ACCESS_SCOPES)
        return template.render(scopes=scopes)

    def start_network_insights_access_scope_analysis(self) -> str:
        scope_id = self._get_param("NetworkInsightsAccessScopeId")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        analysis = self.ec2_backend.start_network_insights_access_scope_analysis(
            network_insights_access_scope_id=scope_id,
            tags=tags,
        )
        template = self.response_template(START_NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSIS)
        return template.render(analysis=analysis)

    def describe_network_insights_access_scope_analyses(self) -> str:
        analysis_ids = self._get_param("NetworkInsightsAccessScopeAnalysisId", [])
        scope_id = self._get_param("NetworkInsightsAccessScopeId")
        analyses = self.ec2_backend.describe_network_insights_access_scope_analyses(
            analysis_ids=analysis_ids or None,
            scope_id=scope_id,
        )
        template = self.response_template(
            DESCRIBE_NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSES
        )
        return template.render(analyses=analyses)

    def get_network_insights_access_scope_analysis_findings(self) -> str:
        analysis_id = self._get_param("NetworkInsightsAccessScopeAnalysisId")
        analysis, findings = (
            self.ec2_backend.get_network_insights_access_scope_analysis_findings(
                analysis_id=analysis_id,
            )
        )
        template = self.response_template(
            GET_NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSIS_FINDINGS
        )
        return template.render(analysis=analysis, findings=findings)

    def get_network_insights_access_scope_content(self) -> str:
        scope_id = self._get_param("NetworkInsightsAccessScopeId")
        scope = self.ec2_backend.get_network_insights_access_scope_content(
            network_insights_access_scope_id=scope_id,
        )
        template = self.response_template(GET_NETWORK_INSIGHTS_ACCESS_SCOPE_CONTENT)
        return template.render(scope=scope)


CREATE_NETWORK_INSIGHTS_ACCESS_SCOPE = """<CreateNetworkInsightsAccessScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsAccessScope>
    <networkInsightsAccessScopeId>{{ scope.id }}</networkInsightsAccessScopeId>
    <networkInsightsAccessScopeArn>{{ scope.arn }}</networkInsightsAccessScopeArn>
    <createdDate>{{ scope.created_date }}</createdDate>
    <tagSet>
      {% for tag in scope.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </networkInsightsAccessScope>
  <networkInsightsAccessScopeContent>
    <networkInsightsAccessScopeId>{{ scope.id }}</networkInsightsAccessScopeId>
  </networkInsightsAccessScopeContent>
</CreateNetworkInsightsAccessScopeResponse>"""

DELETE_NETWORK_INSIGHTS_ACCESS_SCOPE = """<DeleteNetworkInsightsAccessScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsAccessScopeId>{{ scope.id }}</networkInsightsAccessScopeId>
</DeleteNetworkInsightsAccessScopeResponse>"""

DESCRIBE_NETWORK_INSIGHTS_ACCESS_SCOPES = """<DescribeNetworkInsightsAccessScopesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsAccessScopeSet>
    {% for scope in scopes %}
    <item>
      <networkInsightsAccessScopeId>{{ scope.id }}</networkInsightsAccessScopeId>
      <networkInsightsAccessScopeArn>{{ scope.arn }}</networkInsightsAccessScopeArn>
      <createdDate>{{ scope.created_date }}</createdDate>
      <tagSet>
        {% for tag in scope.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </networkInsightsAccessScopeSet>
</DescribeNetworkInsightsAccessScopesResponse>"""

START_NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSIS = """<StartNetworkInsightsAccessScopeAnalysisResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsAccessScopeAnalysis>
    <networkInsightsAccessScopeAnalysisId>{{ analysis.id }}</networkInsightsAccessScopeAnalysisId>
    <networkInsightsAccessScopeAnalysisArn>{{ analysis.arn }}</networkInsightsAccessScopeAnalysisArn>
    <networkInsightsAccessScopeId>{{ analysis.network_insights_access_scope_id }}</networkInsightsAccessScopeId>
    <status>{{ analysis.status }}</status>
    <startDate>{{ analysis.start_date }}</startDate>
    <analyzedEniCount>{{ analysis.analyzed_eni_count }}</analyzedEniCount>
    <tagSet>
      {% for tag in analysis.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </networkInsightsAccessScopeAnalysis>
</StartNetworkInsightsAccessScopeAnalysisResponse>"""

DESCRIBE_NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSES = """<DescribeNetworkInsightsAccessScopeAnalysesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsAccessScopeAnalysisSet>
    {% for analysis in analyses %}
    <item>
      <networkInsightsAccessScopeAnalysisId>{{ analysis.id }}</networkInsightsAccessScopeAnalysisId>
      <networkInsightsAccessScopeAnalysisArn>{{ analysis.arn }}</networkInsightsAccessScopeAnalysisArn>
      <networkInsightsAccessScopeId>{{ analysis.network_insights_access_scope_id }}</networkInsightsAccessScopeId>
      <status>{{ analysis.status }}</status>
      <startDate>{{ analysis.start_date }}</startDate>
      <endDate>{{ analysis.end_date }}</endDate>
      <findingsFound>{{ analysis.findings_found }}</findingsFound>
      <analyzedEniCount>{{ analysis.analyzed_eni_count }}</analyzedEniCount>
      <tagSet>
        {% for tag in analysis.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </networkInsightsAccessScopeAnalysisSet>
</DescribeNetworkInsightsAccessScopeAnalysesResponse>"""

GET_NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSIS_FINDINGS = """<GetNetworkInsightsAccessScopeAnalysisFindingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  {% if analysis %}
  <networkInsightsAccessScopeAnalysisId>{{ analysis.id }}</networkInsightsAccessScopeAnalysisId>
  <analysisStatus>{{ analysis.status }}</analysisStatus>
  {% endif %}
  <analysisFindingSet/>
</GetNetworkInsightsAccessScopeAnalysisFindingsResponse>"""

GET_NETWORK_INSIGHTS_ACCESS_SCOPE_CONTENT = """<GetNetworkInsightsAccessScopeContentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  {% if scope %}
  <networkInsightsAccessScopeContent>
    <networkInsightsAccessScopeId>{{ scope.id }}</networkInsightsAccessScopeId>
    <matchPathSet>
      {% for path in scope.match_paths %}
      <item/>
      {% endfor %}
    </matchPathSet>
    <excludePathSet>
      {% for path in scope.exclude_paths %}
      <item/>
      {% endfor %}
    </excludePathSet>
  </networkInsightsAccessScopeContent>
  {% endif %}
</GetNetworkInsightsAccessScopeContentResponse>"""
