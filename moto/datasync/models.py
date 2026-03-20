from collections import OrderedDict
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.utils import get_partition

from .exceptions import InvalidRequestException


class Agent(BaseModel):
    def __init__(
        self,
        activation_key: str,
        agent_name: str,
        region_name: str,
        tags: Optional[list[dict[str, str]]],
        arn_counter: int = 0,
    ):
        self.activation_key = activation_key
        self.agent_name = agent_name
        self.region_name = region_name
        self.tags = tags or []
        self.status = "ONLINE"
        self.arn = f"arn:{get_partition(region_name)}:datasync:{region_name}:111222333444:agent/agent-{str(arn_counter).zfill(17)}"


class Location(BaseModel):
    def __init__(
        self,
        location_uri: str,
        region_name: str,
        typ: str,
        metadata: dict[str, Any],
        arn_counter: int = 0,
    ):
        self.uri = location_uri
        self.region_name = region_name
        self.metadata = metadata
        self.typ = typ
        # Generate ARN
        self.arn = f"arn:{get_partition(region_name)}:datasync:{region_name}:111222333444:location/loc-{str(arn_counter).zfill(17)}"


class Task(BaseModel):
    def __init__(
        self,
        source_location_arn: str,
        destination_location_arn: str,
        name: str,
        region_name: str,
        metadata: dict[str, Any],
        arn_counter: int = 0,
    ):
        self.source_location_arn = source_location_arn
        self.destination_location_arn = destination_location_arn
        self.name = name
        self.metadata = metadata
        # For simplicity Tasks are either available or running
        self.status = "AVAILABLE"
        self.current_task_execution_arn: Optional[str] = None
        # Generate ARN
        self.arn = f"arn:{get_partition(region_name)}:datasync:{region_name}:111222333444:task/task-{str(arn_counter).zfill(17)}"


class TaskExecution(BaseModel):
    # For simplicity, task_execution can never fail
    # Some documentation refers to this list:
    # 'Status': 'QUEUED'|'LAUNCHING'|'PREPARING'|'TRANSFERRING'|'VERIFYING'|'SUCCESS'|'ERROR'
    # Others refers to this list:
    # INITIALIZING | PREPARING | TRANSFERRING | VERIFYING | SUCCESS/FAILURE
    # Checking with AWS Support...
    TASK_EXECUTION_INTERMEDIATE_STATES = (
        "INITIALIZING",
        # 'QUEUED', 'LAUNCHING',
        "PREPARING",
        "TRANSFERRING",
        "VERIFYING",
    )

    TASK_EXECUTION_FAILURE_STATES = ("ERROR",)
    TASK_EXECUTION_SUCCESS_STATES = ("SUCCESS",)
    # Also COMPLETED state?

    def __init__(self, task_arn: str, arn_counter: int = 0):
        self.task_arn = task_arn
        self.arn = f"{task_arn}/execution/exec-{str(arn_counter).zfill(17)}"
        self.status = self.TASK_EXECUTION_INTERMEDIATE_STATES[0]

    # Simulate a task execution
    def iterate_status(self) -> None:
        if self.status in self.TASK_EXECUTION_FAILURE_STATES:
            return
        if self.status in self.TASK_EXECUTION_SUCCESS_STATES:
            return
        if self.status in self.TASK_EXECUTION_INTERMEDIATE_STATES:
            for i, status in enumerate(self.TASK_EXECUTION_INTERMEDIATE_STATES):
                if status == self.status:
                    if i < len(self.TASK_EXECUTION_INTERMEDIATE_STATES) - 1:
                        self.status = self.TASK_EXECUTION_INTERMEDIATE_STATES[i + 1]
                    else:
                        self.status = self.TASK_EXECUTION_SUCCESS_STATES[0]
                    return
        raise Exception(f"TaskExecution.iterate_status: Unknown status={self.status}")

    def cancel(self) -> None:
        if self.status not in self.TASK_EXECUTION_INTERMEDIATE_STATES:
            raise InvalidRequestException(
                f"Sync task cannot be cancelled in its current status: {self.status}"
            )
        self.status = "ERROR"


class DataSyncBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        # Always increase when new things are created
        # This ensures uniqueness
        self.arn_counter = 0
        self.agents: dict[str, Agent] = OrderedDict()
        self.locations: dict[str, Location] = OrderedDict()
        self.tasks: dict[str, Task] = OrderedDict()
        self.task_executions: dict[str, TaskExecution] = OrderedDict()
        self._tags: dict[str, list[dict[str, str]]] = {}

    def create_agent(
        self,
        activation_key: str,
        agent_name: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        self.arn_counter += 1
        agent = Agent(
            activation_key=activation_key,
            agent_name=agent_name,
            region_name=self.region_name,
            tags=tags,
            arn_counter=self.arn_counter,
        )
        self.agents[agent.arn] = agent
        return agent.arn

    def describe_agent(self, agent_arn: str) -> Agent:
        if agent_arn not in self.agents:
            raise InvalidRequestException(f"Agent {agent_arn} is not found.")
        return self.agents[agent_arn]

    def update_agent(
        self, agent_arn: str, name: Optional[str] = None
    ) -> dict[str, Any]:
        if agent_arn not in self.agents:
            raise InvalidRequestException(f"Agent {agent_arn} is not found.")
        if name is not None:
            self.agents[agent_arn].agent_name = name
        return {}

    def delete_agent(self, agent_arn: str) -> dict[str, Any]:
        if agent_arn not in self.agents:
            raise InvalidRequestException(f"Agent {agent_arn} is not found.")
        del self.agents[agent_arn]
        return {}

    def create_location(
        self, location_uri: str, typ: str, metadata: dict[str, Any]
    ) -> str:
        """
        # AWS DataSync allows for duplicate LocationUris
        for arn, location in self.locations.items():
            if location.uri == location_uri:
                raise Exception('Location already exists')
        """
        if not typ:
            raise Exception("Location type must be specified")
        self.arn_counter = self.arn_counter + 1
        location = Location(
            location_uri,
            region_name=self.region_name,
            arn_counter=self.arn_counter,
            metadata=metadata,
            typ=typ,
        )
        self.locations[location.arn] = location
        return location.arn

    def _get_location(self, location_arn: str, typ: str) -> Location:
        if location_arn not in self.locations:
            raise InvalidRequestException(f"Location {location_arn} is not found.")
        location = self.locations[location_arn]
        if location.typ != typ:
            raise InvalidRequestException(f"Invalid Location type: {location.typ}")
        return location

    def delete_location(self, location_arn: str) -> None:
        if location_arn in self.locations:
            del self.locations[location_arn]
        else:
            raise InvalidRequestException

    def create_task(
        self,
        source_location_arn: str,
        destination_location_arn: str,
        name: str,
        metadata: dict[str, Any],
    ) -> str:
        if source_location_arn not in self.locations:
            raise InvalidRequestException(f"Location {source_location_arn} not found.")
        if destination_location_arn not in self.locations:
            raise InvalidRequestException(
                f"Location {destination_location_arn} not found."
            )
        self.arn_counter = self.arn_counter + 1
        task = Task(
            source_location_arn,
            destination_location_arn,
            name,
            region_name=self.region_name,
            arn_counter=self.arn_counter,
            metadata=metadata,
        )
        self.tasks[task.arn] = task
        return task.arn

    def _get_task(self, task_arn: str) -> Task:
        if task_arn in self.tasks:
            return self.tasks[task_arn]
        else:
            raise InvalidRequestException

    def update_task(self, task_arn: str, name: str, metadata: dict[str, Any]) -> None:
        if task_arn in self.tasks:
            task = self.tasks[task_arn]
            task.name = name
            task.metadata = metadata
        else:
            raise InvalidRequestException(f"Sync task {task_arn} is not found.")

    def delete_task(self, task_arn: str) -> None:
        if task_arn in self.tasks:
            del self.tasks[task_arn]
        else:
            raise InvalidRequestException

    def start_task_execution(self, task_arn: str) -> str:
        self.arn_counter = self.arn_counter + 1
        if task_arn in self.tasks:
            task = self.tasks[task_arn]
            if task.status == "AVAILABLE":
                task_execution = TaskExecution(task_arn, arn_counter=self.arn_counter)
                self.task_executions[task_execution.arn] = task_execution
                self.tasks[task_arn].current_task_execution_arn = task_execution.arn
                self.tasks[task_arn].status = "RUNNING"
                return task_execution.arn
        raise InvalidRequestException("Invalid request.")

    def _get_task_execution(self, task_execution_arn: str) -> TaskExecution:
        if task_execution_arn in self.task_executions:
            return self.task_executions[task_execution_arn]
        else:
            raise InvalidRequestException

    def cancel_task_execution(self, task_execution_arn: str) -> None:
        if task_execution_arn in self.task_executions:
            task_execution = self.task_executions[task_execution_arn]
            task_execution.cancel()
            task_arn = task_execution.task_arn
            self.tasks[task_arn].current_task_execution_arn = None
            self.tasks[task_arn].status = "AVAILABLE"
            return
        raise InvalidRequestException(f"Sync task {task_execution_arn} is not found.")

    def list_task_executions(self, task_arn: Optional[str] = None) -> list[dict]:
        executions = list(self.task_executions.values())
        if task_arn:
            executions = [e for e in executions if e.task_arn == task_arn]
        return [{"TaskExecutionArn": e.arn, "Status": e.status} for e in executions]

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self._tags[resource_arn] = self._tags.get(resource_arn, []) + tags

    def untag_resource(self, resource_arn: str, keys: list[str]) -> None:
        existing = self._tags.get(resource_arn, [])
        self._tags[resource_arn] = [t for t in existing if t.get("Key") not in keys]

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        return self._tags.get(resource_arn, [])

    def update_location(self, location_arn: str, **kwargs: Any) -> Location:
        if location_arn not in self.locations:
            raise InvalidRequestException(f"Location {location_arn} is not found.")
        return self.locations[location_arn]


datasync_backends = BackendDict(DataSyncBackend, "datasync")
