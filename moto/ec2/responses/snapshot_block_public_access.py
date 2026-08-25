from moto.core.responses import ActionResult, EmptyResult

from ._base_response import EC2BaseResponse


class SnapshotBlockPublicAccessResponse(EC2BaseResponse):
    def get_snapshot_block_public_access_state(self) -> ActionResult:
        state = self.ec2_backend.get_snapshot_block_public_access_state()
        result = {"State": state}
        return ActionResult(result)

    def enable_snapshot_block_public_access(self) -> ActionResult:
        state = self._get_param("State")
        result_state = self.ec2_backend.enable_snapshot_block_public_access(state=state)
        result = {"State": result_state}
        return ActionResult(result)

    def disable_snapshot_block_public_access(self) -> ActionResult:
        result_state = self.ec2_backend.disable_snapshot_block_public_access()
        result = {"State": result_state}
        return ActionResult(result)
