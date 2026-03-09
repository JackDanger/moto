from typing import Optional

from moto.core.exceptions import JsonRESTError


class InvalidParameterValueException(JsonRESTError):
    def __init__(self, message: str):
        super().__init__("InvalidParameterValueException", message)


class ClusterNotFoundFault(JsonRESTError):
    def __init__(self, name: Optional[str] = None):
        # DescribeClusters and DeleteCluster use a different message for the same error
        msg = f"Cluster {name} not found." if name else "Cluster not found."
        super().__init__("ClusterNotFoundFault", msg)


class ParameterGroupNotFoundFault(JsonRESTError):
    def __init__(self, name: Optional[str] = None):
        msg = f"ParameterGroup {name} not found." if name else "ParameterGroup not found."
        super().__init__("ParameterGroupNotFoundFault", msg)


class ParameterGroupAlreadyExistsFault(JsonRESTError):
    def __init__(self, name: str):
        super().__init__(
            "ParameterGroupAlreadyExistsFault",
            f"ParameterGroup {name} already exists.",
        )


class SubnetGroupNotFoundFault(JsonRESTError):
    def __init__(self, name: Optional[str] = None):
        msg = f"SubnetGroup {name} not found." if name else "SubnetGroup not found."
        super().__init__("SubnetGroupNotFoundFault", msg)


class SubnetGroupAlreadyExistsFault(JsonRESTError):
    def __init__(self, name: str):
        super().__init__(
            "SubnetGroupAlreadyExistsFault",
            f"SubnetGroup {name} already exists.",
        )


class NodeNotFoundFault(JsonRESTError):
    def __init__(self, node_id: str):
        super().__init__("NodeNotFoundFault", f"Node {node_id} not found.")


class InvalidClusterStateFault(JsonRESTError):
    def __init__(self) -> None:
        super().__init__(
            "InvalidClusterStateFault",
            "Cluster is not in a valid state to perform this operation.",
        )
