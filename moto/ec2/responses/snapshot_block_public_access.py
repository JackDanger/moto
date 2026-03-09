from ._base_response import EC2BaseResponse


class SnapshotBlockPublicAccessResponse(EC2BaseResponse):
    def get_snapshot_block_public_access_state(self) -> str:
        state = self.ec2_backend.get_snapshot_block_public_access_state()
        template = self.response_template(GET_SNAPSHOT_BLOCK_PUBLIC_ACCESS_STATE)
        return template.render(state=state)

    def enable_snapshot_block_public_access(self) -> str:
        state = self._get_param("State")
        result = self.ec2_backend.enable_snapshot_block_public_access(state=state)
        template = self.response_template(ENABLE_SNAPSHOT_BLOCK_PUBLIC_ACCESS)
        return template.render(state=result)

    def disable_snapshot_block_public_access(self) -> str:
        result = self.ec2_backend.disable_snapshot_block_public_access()
        template = self.response_template(DISABLE_SNAPSHOT_BLOCK_PUBLIC_ACCESS)
        return template.render(state=result)


GET_SNAPSHOT_BLOCK_PUBLIC_ACCESS_STATE = """<GetSnapshotBlockPublicAccessStateResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <state>{{ state }}</state>
</GetSnapshotBlockPublicAccessStateResponse>"""

ENABLE_SNAPSHOT_BLOCK_PUBLIC_ACCESS = """<EnableSnapshotBlockPublicAccessResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <state>{{ state }}</state>
</EnableSnapshotBlockPublicAccessResponse>"""

DISABLE_SNAPSHOT_BLOCK_PUBLIC_ACCESS = """<DisableSnapshotBlockPublicAccessResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <state>{{ state }}</state>
</DisableSnapshotBlockPublicAccessResponse>"""
