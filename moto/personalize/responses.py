"""Handles incoming personalize requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import PersonalizeBackend, personalize_backends


class PersonalizeResponse(BaseResponse):
    """Handler for Personalize requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="personalize")

    @property
    def personalize_backend(self) -> PersonalizeBackend:
        """Return backend instance specific for this region."""
        return personalize_backends[self.current_account][self.region]

    def create_schema(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        schema = params.get("schema")
        domain = params.get("domain")
        schema_arn = self.personalize_backend.create_schema(
            name=name,
            schema_dict=schema,
            domain=domain,
        )
        return json.dumps({"schemaArn": schema_arn})

    def delete_schema(self) -> str:
        params = json.loads(self.body)
        schema_arn = params.get("schemaArn")
        self.personalize_backend.delete_schema(schema_arn=schema_arn)
        return "{}"

    def describe_schema(self) -> str:
        params = json.loads(self.body)
        schema_arn = params.get("schemaArn")
        schema = self.personalize_backend.describe_schema(schema_arn=schema_arn)
        return json.dumps({"schema": schema.to_dict()})

    def list_schemas(self) -> str:
        schemas = self.personalize_backend.list_schemas()
        resp = {"schemas": [s.to_dict(full=False) for s in schemas]}
        return json.dumps(resp)

    # ---- Stub list operations ----

    def list_datasets(self) -> str:
        return json.dumps({"datasets": []})

    def list_dataset_groups(self) -> str:
        return json.dumps({"datasetGroups": []})

    def list_dataset_import_jobs(self) -> str:
        return json.dumps({"datasetImportJobs": []})

    def list_dataset_export_jobs(self) -> str:
        return json.dumps({"datasetExportJobs": []})

    def list_campaigns(self) -> str:
        return json.dumps({"campaigns": []})

    def list_solutions(self) -> str:
        return json.dumps({"solutions": []})

    def list_solution_versions(self) -> str:
        return json.dumps({"solutionVersions": []})

    def list_recommenders(self) -> str:
        return json.dumps({"recommenders": []})

    def list_filters(self) -> str:
        return json.dumps({"Filters": []})

    def list_recipes(self) -> str:
        return json.dumps({"recipes": []})

    def list_event_trackers(self) -> str:
        return json.dumps({"eventTrackers": []})

    def list_batch_inference_jobs(self) -> str:
        return json.dumps({"batchInferenceJobs": []})

    def list_batch_segment_jobs(self) -> str:
        return json.dumps({"batchSegmentJobs": []})

    def list_metric_attributions(self) -> str:
        return json.dumps({"metricAttributions": []})

    def list_metric_attribution_metrics(self) -> str:
        return json.dumps({"metrics": []})

    def list_data_deletion_jobs(self) -> str:
        return json.dumps({"dataDeletionJobs": []})

    # ---- Tags ----

    def _tags_store(self) -> dict:
        if not hasattr(self.personalize_backend, "_tags"):
            self.personalize_backend._tags = {}
        return self.personalize_backend._tags

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tags = params.get("tags") or {}
        store = self._tags_store()
        store[resource_arn] = {**store.get(resource_arn, {}), **tags}
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tag_keys = params.get("tagKeys") or []
        store = self._tags_store()
        existing = store.get(resource_arn, {})
        store[resource_arn] = {k: v for k, v in existing.items() if k not in tag_keys}
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        store = self._tags_store()
        return json.dumps({"tags": store.get(resource_arn, {})})
