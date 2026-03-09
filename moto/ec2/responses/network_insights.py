from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class NetworkInsightsResponse(EC2BaseResponse):
    def create_network_insights_path(self) -> str:
        source = self._get_param("Source")
        destination = self._get_param("Destination")
        protocol = self._get_param("Protocol", "tcp")
        destination_port = self._get_param("DestinationPort")
        if destination_port:
            destination_port = int(destination_port)
        filter_at_source = self._get_param("FilterAtSource")
        filter_at_destination = self._get_param("FilterAtDestination")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        path = self.ec2_backend.create_network_insights_path(
            source=source,
            destination=destination,
            protocol=protocol,
            destination_port=destination_port,
            filter_at_source=filter_at_source,
            filter_at_destination=filter_at_destination,
            tags=tags,
        )
        template = self.response_template(CREATE_NETWORK_INSIGHTS_PATH)
        return template.render(path=path)

    def delete_network_insights_path(self) -> str:
        path_id = self._get_param("NetworkInsightsPathId")
        path = self.ec2_backend.delete_network_insights_path(path_id)
        template = self.response_template(DELETE_NETWORK_INSIGHTS_PATH)
        return template.render(path=path)

    def describe_network_insights_paths(self) -> str:
        path_ids = self._get_param("NetworkInsightsPathIds", [])
        filters = self._filters_from_querystring()
        paths = self.ec2_backend.describe_network_insights_paths(
            network_insights_path_ids=path_ids or None,
            filters=filters,
        )
        template = self.response_template(DESCRIBE_NETWORK_INSIGHTS_PATHS)
        return template.render(paths=paths)

    def start_network_insights_analysis(self) -> str:
        path_id = self._get_param("NetworkInsightsPathId")
        filter_in_arns = self._get_param("FilterInArns", [])
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        analysis = self.ec2_backend.start_network_insights_analysis(
            network_insights_path_id=path_id,
            filter_in_arns=filter_in_arns or None,
            tags=tags,
        )
        template = self.response_template(START_NETWORK_INSIGHTS_ANALYSIS)
        return template.render(analysis=analysis)

    def describe_network_insights_analyses(self) -> str:
        analysis_ids = self._get_param("NetworkInsightsAnalysisIds", [])
        path_id = self._get_param("NetworkInsightsPathId")
        filters = self._filters_from_querystring()
        analyses = self.ec2_backend.describe_network_insights_analyses(
            network_insights_analysis_ids=analysis_ids or None,
            network_insights_path_id=path_id,
            filters=filters,
        )
        template = self.response_template(DESCRIBE_NETWORK_INSIGHTS_ANALYSES)
        return template.render(analyses=analyses)


CREATE_NETWORK_INSIGHTS_PATH = """<CreateNetworkInsightsPathResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsPath>
    <networkInsightsPathId>{{ path.id }}</networkInsightsPathId>
    <networkInsightsPathArn>{{ path.arn }}</networkInsightsPathArn>
    <source>{{ path.source }}</source>
    {% if path.destination %}
    <destination>{{ path.destination }}</destination>
    {% endif %}
    <protocol>{{ path.protocol }}</protocol>
    {% if path.destination_port %}
    <destinationPort>{{ path.destination_port }}</destinationPort>
    {% endif %}
    <createdDate>{{ path.creation_time }}</createdDate>
    <tagSet>
      {% for tag in path.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </networkInsightsPath>
</CreateNetworkInsightsPathResponse>"""


DELETE_NETWORK_INSIGHTS_PATH = """<DeleteNetworkInsightsPathResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsPathId>{{ path.id }}</networkInsightsPathId>
</DeleteNetworkInsightsPathResponse>"""


DESCRIBE_NETWORK_INSIGHTS_PATHS = """<DescribeNetworkInsightsPathsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsPathSet>
    {% for path in paths %}
    <item>
      <networkInsightsPathId>{{ path.id }}</networkInsightsPathId>
      <networkInsightsPathArn>{{ path.arn }}</networkInsightsPathArn>
      <source>{{ path.source }}</source>
      {% if path.destination %}
      <destination>{{ path.destination }}</destination>
      {% endif %}
      <protocol>{{ path.protocol }}</protocol>
      {% if path.destination_port %}
      <destinationPort>{{ path.destination_port }}</destinationPort>
      {% endif %}
      <createdDate>{{ path.creation_time }}</createdDate>
      <tagSet>
        {% for tag in path.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </networkInsightsPathSet>
</DescribeNetworkInsightsPathsResponse>"""


START_NETWORK_INSIGHTS_ANALYSIS = """<StartNetworkInsightsAnalysisResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsAnalysis>
    <networkInsightsAnalysisId>{{ analysis.id }}</networkInsightsAnalysisId>
    <networkInsightsAnalysisArn>{{ analysis.arn }}</networkInsightsAnalysisArn>
    <networkInsightsPathId>{{ analysis.network_insights_path_id }}</networkInsightsPathId>
    <status>{{ analysis.status }}</status>
    <networkPathFound>{{ 'true' if analysis.network_path_found else 'false' }}</networkPathFound>
    <startDate>{{ analysis.start_date }}</startDate>
    <tagSet>
      {% for tag in analysis.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </networkInsightsAnalysis>
</StartNetworkInsightsAnalysisResponse>"""


DESCRIBE_NETWORK_INSIGHTS_ANALYSES = """<DescribeNetworkInsightsAnalysesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <networkInsightsAnalysisSet>
    {% for analysis in analyses %}
    <item>
      <networkInsightsAnalysisId>{{ analysis.id }}</networkInsightsAnalysisId>
      <networkInsightsAnalysisArn>{{ analysis.arn }}</networkInsightsAnalysisArn>
      <networkInsightsPathId>{{ analysis.network_insights_path_id }}</networkInsightsPathId>
      <status>{{ analysis.status }}</status>
      <networkPathFound>{{ 'true' if analysis.network_path_found else 'false' }}</networkPathFound>
      <startDate>{{ analysis.start_date }}</startDate>
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
  </networkInsightsAnalysisSet>
</DescribeNetworkInsightsAnalysesResponse>"""
