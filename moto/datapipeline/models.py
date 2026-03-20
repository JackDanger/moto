import datetime
from collections import OrderedDict
from collections.abc import Iterable
from typing import Any

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel, CloudFormationModel
from moto.core.utils import utcnow

from .utils import get_random_pipeline_id, remove_capitalization_of_dict_keys


class PipelineObject(BaseModel):
    def __init__(self, object_id: str, name: str, fields: Any):
        self.object_id = object_id
        self.name = name
        self.fields = fields

    def to_json(self) -> dict[str, Any]:
        return {"fields": self.fields, "id": self.object_id, "name": self.name}


class Pipeline(CloudFormationModel):
    def __init__(self, name: str, unique_id: str, **kwargs: Any):
        self.name = name
        self.unique_id = unique_id
        self.description = kwargs.get("description", "")
        self.pipeline_id = get_random_pipeline_id()
        self.creation_time = utcnow()
        self.objects: list[Any] = []
        self.status = "PENDING"
        self.tags = kwargs.get("tags", [])

    @property
    def physical_resource_id(self) -> str:
        return self.pipeline_id

    def to_meta_json(self) -> dict[str, str]:
        return {"id": self.pipeline_id, "name": self.name}

    def to_json(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "fields": [
                {"key": "@pipelineState", "stringValue": self.status},
                {"key": "description", "stringValue": self.description},
                {"key": "name", "stringValue": self.name},
                {
                    "key": "@creationTime",
                    "stringValue": datetime.datetime.strftime(
                        self.creation_time, "%Y-%m-%dT%H-%M-%S"
                    ),
                },
                {"key": "@id", "stringValue": self.pipeline_id},
                {"key": "@sphere", "stringValue": "PIPELINE"},
                {"key": "@version", "stringValue": "1"},
                {"key": "@userId", "stringValue": "924374875933"},
                {"key": "@accountId", "stringValue": "924374875933"},
                {"key": "uniqueId", "stringValue": self.unique_id},
            ],
            "name": self.name,
            "pipelineId": self.pipeline_id,
            "tags": self.tags,
        }

    def set_pipeline_objects(self, pipeline_objects: Any) -> None:
        self.objects = [
            PipelineObject(
                pipeline_object["id"],
                pipeline_object["name"],
                pipeline_object["fields"],
            )
            for pipeline_object in remove_capitalization_of_dict_keys(pipeline_objects)
        ]

    def activate(self) -> None:
        self.status = "SCHEDULED"

    def deactivate(self) -> None:
        self.status = "DEACTIVATING"

    def add_tags(self, tags: list[dict[str, str]]) -> None:
        # Merge: new tags override existing ones with same key
        existing_keys = {t["key"]: i for i, t in enumerate(self.tags)}
        for tag in tags:
            if tag["key"] in existing_keys:
                self.tags[existing_keys[tag["key"]]] = tag
            else:
                self.tags.append(tag)

    def remove_tags(self, tag_keys: list[str]) -> None:
        self.tags = [t for t in self.tags if t["key"] not in tag_keys]

    @staticmethod
    def cloudformation_name_type() -> str:
        return "Name"

    @staticmethod
    def cloudformation_type() -> str:
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html
        return "AWS::DataPipeline::Pipeline"

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: dict[str, Any],
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "Pipeline":
        datapipeline_backend = datapipeline_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]

        cloudformation_unique_id = "cf-" + resource_name
        pipeline = datapipeline_backend.create_pipeline(
            resource_name, cloudformation_unique_id
        )
        datapipeline_backend.put_pipeline_definition(
            pipeline.pipeline_id, properties["PipelineObjects"]
        )

        if properties["Activate"]:
            pipeline.activate()
        return pipeline


class DataPipelineBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.pipelines: dict[str, Pipeline] = OrderedDict()

    def create_pipeline(self, name: str, unique_id: str, **kwargs: Any) -> Pipeline:
        pipeline = Pipeline(name, unique_id, **kwargs)
        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline

    def list_pipelines(self) -> Iterable[Pipeline]:
        return self.pipelines.values()

    def describe_pipelines(self, pipeline_ids: list[str]) -> list[Pipeline]:
        pipelines = [
            pipeline
            for pipeline in self.pipelines.values()
            if pipeline.pipeline_id in pipeline_ids
        ]
        return pipelines

    def get_pipeline(self, pipeline_id: str) -> Pipeline:
        return self.pipelines[pipeline_id]

    def delete_pipeline(self, pipeline_id: str) -> None:
        self.pipelines.pop(pipeline_id, None)

    def put_pipeline_definition(self, pipeline_id: str, pipeline_objects: Any) -> None:
        pipeline = self.get_pipeline(pipeline_id)
        pipeline.set_pipeline_objects(pipeline_objects)

    def get_pipeline_definition(self, pipeline_id: str) -> Any:
        pipeline = self.get_pipeline(pipeline_id)
        return pipeline.objects

    def describe_objects(self, object_ids: list[str], pipeline_id: str) -> list[Any]:
        pipeline = self.get_pipeline(pipeline_id)
        pipeline_objects = [
            pipeline_object
            for pipeline_object in pipeline.objects
            if pipeline_object.object_id in object_ids
        ]
        return pipeline_objects

    def activate_pipeline(self, pipeline_id: str) -> None:
        pipeline = self.get_pipeline(pipeline_id)
        pipeline.activate()

    def deactivate_pipeline(self, pipeline_id: str) -> None:
        pipeline = self.get_pipeline(pipeline_id)
        pipeline.deactivate()

    def add_tags(self, pipeline_id: str, tags: list[dict[str, str]]) -> None:
        pipeline = self.get_pipeline(pipeline_id)
        pipeline.add_tags(tags)

    def remove_tags(self, pipeline_id: str, tag_keys: list[str]) -> None:
        pipeline = self.get_pipeline(pipeline_id)
        pipeline.remove_tags(tag_keys)

    def validate_pipeline_definition(
        self, pipeline_id: str, pipeline_objects: Any
    ) -> dict[str, Any]:
        # Basic validation: just check that the pipeline exists
        self.get_pipeline(pipeline_id)
        return {"errored": False, "validationErrors": [], "validationWarnings": []}

    def query_objects(
        self, pipeline_id: str, sphere: str
    ) -> list[str]:
        pipeline = self.get_pipeline(pipeline_id)
        if sphere == "INSTANCE":
            return []
        elif sphere == "ATTEMPT":
            return []
        else:
            # COMPONENT sphere - return object IDs
            return [obj.object_id for obj in pipeline.objects]

    def evaluate_expression(
        self, pipeline_id: str, object_id: str, expression: str
    ) -> str:
        self.get_pipeline(pipeline_id)
        # Return the expression as-is (basic stub)
        return expression

    def set_status(
        self, pipeline_id: str, object_ids: list[str], status: str
    ) -> None:
        pipeline = self.get_pipeline(pipeline_id)
        for obj in pipeline.objects:
            if obj.object_id in object_ids:
                # Update the status field
                for field in obj.fields:
                    if field.get("key") == "@status":
                        field["stringValue"] = status
                        break
                else:
                    obj.fields.append({"key": "@status", "stringValue": status})

    def set_task_status(self, task_id: str, task_status: str) -> None:
        # Task management is a stub - just acknowledge
        pass

    def report_task_progress(self, task_id: str) -> bool:
        # Return False = not canceled
        return False

    def report_task_runner_heartbeat(self, taskrunner_id: str) -> bool:
        # Return False = do not terminate
        return False

    def poll_for_task(self, worker_group: str) -> dict[str, Any]:
        # No tasks to return in mock
        return {}


datapipeline_backends = BackendDict(DataPipelineBackend, "datapipeline")
