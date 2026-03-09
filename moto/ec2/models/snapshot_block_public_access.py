class SnapshotBlockPublicAccessBackend:
    def __init__(self) -> None:
        self.snapshot_block_public_access_state = "unblocked"

    def get_snapshot_block_public_access_state(self) -> str:
        return self.snapshot_block_public_access_state

    def enable_snapshot_block_public_access(self, state: str) -> str:
        self.snapshot_block_public_access_state = state
        return state

    def disable_snapshot_block_public_access(self) -> str:
        self.snapshot_block_public_access_state = "unblocked"
        return "unblocked"
