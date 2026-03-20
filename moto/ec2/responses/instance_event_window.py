from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class InstanceEventWindowResponse(EC2BaseResponse):
    def create_instance_event_window(self) -> str:
        name = self._get_param("Name")
        time_ranges = self._get_param("TimeRange", [])
        cron_expression = self._get_param("CronExpression")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        window = self.ec2_backend.create_instance_event_window(
            name=name,
            time_ranges=time_ranges if isinstance(time_ranges, list) else [time_ranges],
            cron_expression=cron_expression,
            tags=tags,
        )
        template = self.response_template(CREATE_INSTANCE_EVENT_WINDOW)
        return template.render(window=window)

    def delete_instance_event_window(self) -> str:
        window_id = self._get_param("InstanceEventWindowId")
        force = self._get_param("ForceDelete", "false") == "true"
        window = self.ec2_backend.delete_instance_event_window(
            instance_event_window_id=window_id,
            force_delete=force,
        )
        template = self.response_template(DELETE_INSTANCE_EVENT_WINDOW)
        return template.render(window=window)

    def describe_instance_event_windows(self) -> str:
        window_ids = self._get_param("InstanceEventWindowId", [])
        windows = self.ec2_backend.describe_instance_event_windows(
            instance_event_window_ids=window_ids or None,
        )
        template = self.response_template(DESCRIBE_INSTANCE_EVENT_WINDOWS)
        return template.render(windows=windows)

    def modify_instance_event_window(self) -> str:
        window_id = self._get_param("InstanceEventWindowId")
        name = self._get_param("Name")
        time_ranges = self._get_param("TimeRange")
        cron_expression = self._get_param("CronExpression")
        window = self.ec2_backend.modify_instance_event_window(
            instance_event_window_id=window_id,
            name=name,
            time_ranges=time_ranges,
            cron_expression=cron_expression,
        )
        template = self.response_template(MODIFY_INSTANCE_EVENT_WINDOW)
        return template.render(window=window)

    def associate_instance_event_window(self) -> str:
        window_id = self._get_param("InstanceEventWindowId")
        assoc = self._get_param("AssociationTarget", {})
        instance_ids = assoc.get("InstanceId", [])
        dedicated_host_ids = assoc.get("DedicatedHostId", [])
        instance_tags = assoc.get("InstanceTag", [])
        window = self.ec2_backend.associate_instance_event_window(
            instance_event_window_id=window_id,
            instance_ids=instance_ids
            if isinstance(instance_ids, list)
            else [instance_ids],
            dedicated_host_ids=(
                dedicated_host_ids
                if isinstance(dedicated_host_ids, list)
                else [dedicated_host_ids]
            ),
            instance_tags=instance_tags
            if isinstance(instance_tags, list)
            else [instance_tags],
        )
        template = self.response_template(ASSOCIATE_INSTANCE_EVENT_WINDOW)
        return template.render(window=window)

    def disassociate_instance_event_window(self) -> str:
        window_id = self._get_param("InstanceEventWindowId")
        assoc = self._get_param("AssociationTarget", {})
        instance_ids = assoc.get("InstanceId", [])
        dedicated_host_ids = assoc.get("DedicatedHostId", [])
        instance_tags = assoc.get("InstanceTag", [])
        window = self.ec2_backend.disassociate_instance_event_window(
            instance_event_window_id=window_id,
            instance_ids=instance_ids
            if isinstance(instance_ids, list)
            else [instance_ids],
            dedicated_host_ids=(
                dedicated_host_ids
                if isinstance(dedicated_host_ids, list)
                else [dedicated_host_ids]
            ),
            instance_tags=instance_tags
            if isinstance(instance_tags, list)
            else [instance_tags],
        )
        template = self.response_template(DISASSOCIATE_INSTANCE_EVENT_WINDOW)
        return template.render(window=window)


CREATE_INSTANCE_EVENT_WINDOW = """<CreateInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceEventWindow>
    <instanceEventWindowId>{{ window.id }}</instanceEventWindowId>
    <name>{{ window.name }}</name>
    {% if window.cron_expression %}
    <cronExpression>{{ window.cron_expression }}</cronExpression>
    {% endif %}
    <state>{{ window.state }}</state>
    <timeRangeSet>
      {% for tr in window.time_ranges %}
      <item>
        {% if tr.get('StartWeekDay') %}<startWeekDay>{{ tr.StartWeekDay }}</startWeekDay>{% endif %}
        {% if tr.get('StartHour') %}<startHour>{{ tr.StartHour }}</startHour>{% endif %}
        {% if tr.get('EndWeekDay') %}<endWeekDay>{{ tr.EndWeekDay }}</endWeekDay>{% endif %}
        {% if tr.get('EndHour') %}<endHour>{{ tr.EndHour }}</endHour>{% endif %}
      </item>
      {% endfor %}
    </timeRangeSet>
    <associationTarget>
      <instanceIdSet>
        {% for iid in window.association_target.instance_ids %}
        <item>{{ iid }}</item>
        {% endfor %}
      </instanceIdSet>
      <dedicatedHostIdSet>
        {% for hid in window.association_target.dedicated_host_ids %}
        <item>{{ hid }}</item>
        {% endfor %}
      </dedicatedHostIdSet>
    </associationTarget>
    <tagSet>
      {% for tag in window.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </instanceEventWindow>
</CreateInstanceEventWindowResponse>"""

DELETE_INSTANCE_EVENT_WINDOW = """<DeleteInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceEventWindowState>
    <instanceEventWindowId>{{ window.id }}</instanceEventWindowId>
    <state>{{ window.state }}</state>
  </instanceEventWindowState>
</DeleteInstanceEventWindowResponse>"""

DESCRIBE_INSTANCE_EVENT_WINDOWS = """<DescribeInstanceEventWindowsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceEventWindowSet>
    {% for window in windows %}
    <item>
      <instanceEventWindowId>{{ window.id }}</instanceEventWindowId>
      <name>{{ window.name }}</name>
      {% if window.cron_expression %}
      <cronExpression>{{ window.cron_expression }}</cronExpression>
      {% endif %}
      <state>{{ window.state }}</state>
      <timeRangeSet>
        {% for tr in window.time_ranges %}
        <item>
          {% if tr.get('StartWeekDay') %}<startWeekDay>{{ tr.StartWeekDay }}</startWeekDay>{% endif %}
          {% if tr.get('StartHour') %}<startHour>{{ tr.StartHour }}</startHour>{% endif %}
          {% if tr.get('EndWeekDay') %}<endWeekDay>{{ tr.EndWeekDay }}</endWeekDay>{% endif %}
          {% if tr.get('EndHour') %}<endHour>{{ tr.EndHour }}</endHour>{% endif %}
        </item>
        {% endfor %}
      </timeRangeSet>
      <associationTarget>
        <instanceIdSet>
          {% for iid in window.association_target.instance_ids %}
          <item>{{ iid }}</item>
          {% endfor %}
        </instanceIdSet>
        <dedicatedHostIdSet>
          {% for hid in window.association_target.dedicated_host_ids %}
          <item>{{ hid }}</item>
          {% endfor %}
        </dedicatedHostIdSet>
      </associationTarget>
      <tagSet>
        {% for tag in window.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </instanceEventWindowSet>
</DescribeInstanceEventWindowsResponse>"""

MODIFY_INSTANCE_EVENT_WINDOW = """<ModifyInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceEventWindow>
    <instanceEventWindowId>{{ window.id }}</instanceEventWindowId>
    <name>{{ window.name }}</name>
    {% if window.cron_expression %}
    <cronExpression>{{ window.cron_expression }}</cronExpression>
    {% endif %}
    <state>{{ window.state }}</state>
  </instanceEventWindow>
</ModifyInstanceEventWindowResponse>"""

ASSOCIATE_INSTANCE_EVENT_WINDOW = """<AssociateInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceEventWindow>
    <instanceEventWindowId>{{ window.id }}</instanceEventWindowId>
    <name>{{ window.name }}</name>
    <state>{{ window.state }}</state>
    <associationTarget>
      <instanceIdSet>
        {% for iid in window.association_target.instance_ids %}
        <item>{{ iid }}</item>
        {% endfor %}
      </instanceIdSet>
      <dedicatedHostIdSet>
        {% for hid in window.association_target.dedicated_host_ids %}
        <item>{{ hid }}</item>
        {% endfor %}
      </dedicatedHostIdSet>
    </associationTarget>
  </instanceEventWindow>
</AssociateInstanceEventWindowResponse>"""

DISASSOCIATE_INSTANCE_EVENT_WINDOW = """<DisassociateInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceEventWindow>
    <instanceEventWindowId>{{ window.id }}</instanceEventWindowId>
    <name>{{ window.name }}</name>
    <state>{{ window.state }}</state>
    <associationTarget>
      <instanceIdSet>
        {% for iid in window.association_target.instance_ids %}
        <item>{{ iid }}</item>
        {% endfor %}
      </instanceIdSet>
      <dedicatedHostIdSet>
        {% for hid in window.association_target.dedicated_host_ids %}
        <item>{{ hid }}</item>
        {% endfor %}
      </dedicatedHostIdSet>
    </associationTarget>
  </instanceEventWindow>
</DisassociateInstanceEventWindowResponse>"""
