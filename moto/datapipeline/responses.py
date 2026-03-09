import json

from moto.core.responses import BaseResponse

from .models import DataPipelineBackend, datapipeline_backends


class DataPipelineResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="datapipeline")

    @property
    def datapipeline_backend(self) -> DataPipelineBackend:
        return datapipeline_backends[self.current_account][self.region]

    def create_pipeline(self) -> str:
        name = self._get_param("name")
        unique_id = self._get_param("uniqueId")
        description = self._get_param("description", "")
        tags = self._get_param("tags", [])
        pipeline = self.datapipeline_backend.create_pipeline(
            name, unique_id, description=description, tags=tags
        )
        return json.dumps({"pipelineId": pipeline.pipeline_id})

    def list_pipelines(self) -> str:
        pipelines = list(self.datapipeline_backend.list_pipelines())
        pipeline_ids = [pipeline.pipeline_id for pipeline in pipelines]
        max_pipelines = 50
        marker = self._get_param("marker")
        if marker:
            start = pipeline_ids.index(marker) + 1
        else:
            start = 0
        pipelines_resp = pipelines[start : start + max_pipelines]
        has_more_results = False
        marker = None
        if start + max_pipelines < len(pipeline_ids) - 1:
            has_more_results = True
            marker = pipelines_resp[-1].pipeline_id
        return json.dumps(
            {
                "hasMoreResults": has_more_results,
                "marker": marker,
                "pipelineIdList": [
                    pipeline.to_meta_json() for pipeline in pipelines_resp
                ],
            }
        )

    def describe_pipelines(self) -> str:
        pipeline_ids = self._get_param("pipelineIds")
        pipelines = self.datapipeline_backend.describe_pipelines(pipeline_ids)

        return json.dumps(
            {"pipelineDescriptionList": [pipeline.to_json() for pipeline in pipelines]}
        )

    def delete_pipeline(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        self.datapipeline_backend.delete_pipeline(pipeline_id)
        return json.dumps({})

    def put_pipeline_definition(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        pipeline_objects = self._get_param("pipelineObjects")

        self.datapipeline_backend.put_pipeline_definition(pipeline_id, pipeline_objects)
        return json.dumps({"errored": False})

    def get_pipeline_definition(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        pipeline_definition = self.datapipeline_backend.get_pipeline_definition(
            pipeline_id
        )
        return json.dumps(
            {
                "pipelineObjects": [
                    pipeline_object.to_json() for pipeline_object in pipeline_definition
                ]
            }
        )

    def describe_objects(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        object_ids = self._get_param("objectIds")

        pipeline_objects = self.datapipeline_backend.describe_objects(
            object_ids, pipeline_id
        )
        return json.dumps(
            {
                "hasMoreResults": False,
                "marker": None,
                "pipelineObjects": [
                    pipeline_object.to_json() for pipeline_object in pipeline_objects
                ],
            }
        )

    def activate_pipeline(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        self.datapipeline_backend.activate_pipeline(pipeline_id)
        return json.dumps({})

    def deactivate_pipeline(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        self.datapipeline_backend.deactivate_pipeline(pipeline_id)
        return json.dumps({})

    def add_tags(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        tags = self._get_param("tags", [])
        self.datapipeline_backend.add_tags(pipeline_id, tags)
        return json.dumps({})

    def remove_tags(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        tag_keys = self._get_param("tagKeys", [])
        self.datapipeline_backend.remove_tags(pipeline_id, tag_keys)
        return json.dumps({})

    def validate_pipeline_definition(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        pipeline_objects = self._get_param("pipelineObjects")
        result = self.datapipeline_backend.validate_pipeline_definition(
            pipeline_id, pipeline_objects
        )
        return json.dumps(result)

    def query_objects(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        sphere = self._get_param("sphere")
        ids = self.datapipeline_backend.query_objects(pipeline_id, sphere)
        return json.dumps(
            {"hasMoreResults": False, "ids": ids, "marker": None}
        )

    def evaluate_expression(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        object_id = self._get_param("objectId")
        expression = self._get_param("expression")
        result = self.datapipeline_backend.evaluate_expression(
            pipeline_id, object_id, expression
        )
        return json.dumps({"evaluatedExpression": result})

    def set_status(self) -> str:
        pipeline_id = self._get_param("pipelineId")
        object_ids = self._get_param("objectIds", [])
        status = self._get_param("status")
        self.datapipeline_backend.set_status(pipeline_id, object_ids, status)
        return json.dumps({})

    def set_task_status(self) -> str:
        task_id = self._get_param("taskId")
        task_status = self._get_param("taskStatus")
        self.datapipeline_backend.set_task_status(task_id, task_status)
        return json.dumps({})

    def report_task_progress(self) -> str:
        task_id = self._get_param("taskId")
        canceled = self.datapipeline_backend.report_task_progress(task_id)
        return json.dumps({"canceled": canceled})

    def report_task_runner_heartbeat(self) -> str:
        taskrunner_id = self._get_param("taskrunnerId")
        terminate = self.datapipeline_backend.report_task_runner_heartbeat(
            taskrunner_id
        )
        return json.dumps({"terminate": terminate})

    def poll_for_task(self) -> str:
        worker_group = self._get_param("workerGroup")
        task_object = self.datapipeline_backend.poll_for_task(worker_group)
        return json.dumps({"taskObject": task_object})
