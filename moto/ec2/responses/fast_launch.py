from ._base_response import EC2BaseResponse


class FastLaunchResponse(EC2BaseResponse):
    def enable_fast_launch(self) -> str:
        image_id = self._get_param("ImageId")
        resource_type = self._get_param("ResourceType", "snapshot")
        max_parallel = int(
            self._get_param("MaxParallelLaunches", "6")
        )
        snapshot_config = self._get_param("SnapshotConfiguration")
        launch_template = self._get_param("LaunchTemplate")
        fli = self.ec2_backend.enable_fast_launch(
            image_id=image_id,
            resource_type=resource_type,
            max_parallel_launches=max_parallel,
            snapshot_configuration=snapshot_config,
            launch_template=launch_template,
        )
        template = self.response_template(ENABLE_FAST_LAUNCH)
        return template.render(fli=fli)

    def describe_fast_launch_images(self) -> str:
        image_ids = self._get_param("ImageId", [])
        images = self.ec2_backend.describe_fast_launch_images(
            image_ids=image_ids or None,
        )
        template = self.response_template(DESCRIBE_FAST_LAUNCH_IMAGES)
        return template.render(images=images)

    def disable_fast_launch(self) -> str:
        image_id = self._get_param("ImageId")
        fli = self.ec2_backend.disable_fast_launch(image_id=image_id)
        template = self.response_template(DISABLE_FAST_LAUNCH)
        return template.render(fli=fli)


ENABLE_FAST_LAUNCH = """<EnableFastLaunchResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <imageId>{{ fli.image_id }}</imageId>
  <resourceType>{{ fli.resource_type }}</resourceType>
  <snapshotConfiguration>
    <targetResourceCount>{{ fli.snapshot_configuration.get('TargetResourceCount', 5) }}</targetResourceCount>
  </snapshotConfiguration>
  <maxParallelLaunches>{{ fli.max_parallel_launches }}</maxParallelLaunches>
  <ownerId>{{ fli.owner_id }}</ownerId>
  <state>{{ fli.state }}</state>
  <stateTransitionReason>{{ fli.state_transition_reason }}</stateTransitionReason>
  <stateTransitionTime>{{ fli.state_transition_time }}</stateTransitionTime>
</EnableFastLaunchResponse>"""

DESCRIBE_FAST_LAUNCH_IMAGES = """<DescribeFastLaunchImagesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <fastLaunchImageSet>
    {% for fli in images %}
    <item>
      <imageId>{{ fli.image_id }}</imageId>
      <resourceType>{{ fli.resource_type }}</resourceType>
      <snapshotConfiguration>
        <targetResourceCount>{{ fli.snapshot_configuration.get('TargetResourceCount', 5) }}</targetResourceCount>
      </snapshotConfiguration>
      <maxParallelLaunches>{{ fli.max_parallel_launches }}</maxParallelLaunches>
      <ownerId>{{ fli.owner_id }}</ownerId>
      <state>{{ fli.state }}</state>
      <stateTransitionReason>{{ fli.state_transition_reason }}</stateTransitionReason>
      <stateTransitionTime>{{ fli.state_transition_time }}</stateTransitionTime>
    </item>
    {% endfor %}
  </fastLaunchImageSet>
</DescribeFastLaunchImagesResponse>"""

DISABLE_FAST_LAUNCH = """<DisableFastLaunchResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <imageId>{{ fli.image_id }}</imageId>
  <resourceType>{{ fli.resource_type }}</resourceType>
  <maxParallelLaunches>{{ fli.max_parallel_launches }}</maxParallelLaunches>
  <ownerId>{{ fli.owner_id }}</ownerId>
  <state>{{ fli.state }}</state>
  <stateTransitionReason>{{ fli.state_transition_reason }}</stateTransitionReason>
  <stateTransitionTime>{{ fli.state_transition_time }}</stateTransitionTime>
</DisableFastLaunchResponse>"""
