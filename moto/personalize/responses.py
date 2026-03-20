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

    # ---- Schema ----

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

    # ---- Dataset Group ----

    def create_dataset_group(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        data = {k: v for k, v in params.items() if k != "name"}
        arn = self.personalize_backend.create_dataset_group(name=name, data=data)
        return json.dumps({"datasetGroupArn": arn})

    def describe_dataset_group(self) -> str:
        params = json.loads(self.body)
        arn = params.get("datasetGroupArn")
        resource = self.personalize_backend.describe_dataset_group(arn)
        return json.dumps({"datasetGroup": resource.to_dict()})

    def delete_dataset_group(self) -> str:
        params = json.loads(self.body)
        arn = params.get("datasetGroupArn")
        self.personalize_backend.delete_dataset_group(arn)
        return "{}"

    def list_dataset_groups(self) -> str:
        resources = list(self.personalize_backend.dataset_groups.values())
        items = [
            {
                "datasetGroupArn": r.arn,
                "name": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"datasetGroups": items})

    # ---- Dataset ----

    def create_dataset(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        data = {k: v for k, v in params.items() if k != "name"}
        arn = self.personalize_backend.create_dataset(name=name, data=data)
        return json.dumps({"datasetArn": arn})

    def describe_dataset(self) -> str:
        params = json.loads(self.body)
        arn = params.get("datasetArn")
        resource = self.personalize_backend.describe_dataset(arn)
        return json.dumps({"dataset": resource.to_dict()})

    def delete_dataset(self) -> str:
        params = json.loads(self.body)
        arn = params.get("datasetArn")
        self.personalize_backend.delete_dataset(arn)
        return "{}"

    def update_dataset(self) -> str:
        params = json.loads(self.body)
        arn = params.get("datasetArn")
        data = {k: v for k, v in params.items() if k != "datasetArn"}
        result_arn = self.personalize_backend.update_dataset(arn=arn, data=data)
        return json.dumps({"datasetArn": result_arn})

    def list_datasets(self) -> str:
        resources = list(self.personalize_backend.datasets.values())
        items = [
            {
                "datasetArn": r.arn,
                "name": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"datasets": items})

    # ---- Dataset Import Job ----

    def create_dataset_import_job(self) -> str:
        params = json.loads(self.body)
        name = params.get("jobName")
        data = {k: v for k, v in params.items() if k != "jobName"}
        arn = self.personalize_backend.create_dataset_import_job(name=name, data=data)
        return json.dumps({"datasetImportJobArn": arn})

    def describe_dataset_import_job(self) -> str:
        params = json.loads(self.body)
        arn = params.get("datasetImportJobArn")
        resource = self.personalize_backend.describe_dataset_import_job(arn)
        return json.dumps({"datasetImportJob": resource.to_dict()})

    def list_dataset_import_jobs(self) -> str:
        resources = list(self.personalize_backend.dataset_import_jobs.values())
        items = [
            {
                "datasetImportJobArn": r.arn,
                "jobName": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"datasetImportJobs": items})

    # ---- Dataset Export Job ----

    def create_dataset_export_job(self) -> str:
        params = json.loads(self.body)
        name = params.get("jobName")
        data = {k: v for k, v in params.items() if k != "jobName"}
        arn = self.personalize_backend.create_dataset_export_job(name=name, data=data)
        return json.dumps({"datasetExportJobArn": arn})

    def describe_dataset_export_job(self) -> str:
        params = json.loads(self.body)
        arn = params.get("datasetExportJobArn")
        resource = self.personalize_backend.describe_dataset_export_job(arn)
        return json.dumps({"datasetExportJob": resource.to_dict()})

    def list_dataset_export_jobs(self) -> str:
        resources = list(self.personalize_backend.dataset_export_jobs.values())
        items = [
            {
                "datasetExportJobArn": r.arn,
                "jobName": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"datasetExportJobs": items})

    # ---- Batch Inference Job ----

    def create_batch_inference_job(self) -> str:
        params = json.loads(self.body)
        name = params.get("jobName")
        data = {k: v for k, v in params.items() if k != "jobName"}
        arn = self.personalize_backend.create_batch_inference_job(name=name, data=data)
        return json.dumps({"batchInferenceJobArn": arn})

    def describe_batch_inference_job(self) -> str:
        params = json.loads(self.body)
        arn = params.get("batchInferenceJobArn")
        resource = self.personalize_backend.describe_batch_inference_job(arn)
        return json.dumps({"batchInferenceJob": resource.to_dict()})

    def list_batch_inference_jobs(self) -> str:
        resources = list(self.personalize_backend.batch_inference_jobs.values())
        items = [
            {
                "batchInferenceJobArn": r.arn,
                "jobName": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"batchInferenceJobs": items})

    # ---- Batch Segment Job ----

    def create_batch_segment_job(self) -> str:
        params = json.loads(self.body)
        name = params.get("jobName")
        data = {k: v for k, v in params.items() if k != "jobName"}
        arn = self.personalize_backend.create_batch_segment_job(name=name, data=data)
        return json.dumps({"batchSegmentJobArn": arn})

    def describe_batch_segment_job(self) -> str:
        params = json.loads(self.body)
        arn = params.get("batchSegmentJobArn")
        resource = self.personalize_backend.describe_batch_segment_job(arn)
        return json.dumps({"batchSegmentJob": resource.to_dict()})

    def list_batch_segment_jobs(self) -> str:
        resources = list(self.personalize_backend.batch_segment_jobs.values())
        items = [
            {
                "batchSegmentJobArn": r.arn,
                "jobName": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"batchSegmentJobs": items})

    # ---- Campaign ----

    def create_campaign(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        data = {k: v for k, v in params.items() if k != "name"}
        arn = self.personalize_backend.create_campaign(name=name, data=data)
        return json.dumps({"campaignArn": arn})

    def describe_campaign(self) -> str:
        params = json.loads(self.body)
        arn = params.get("campaignArn")
        resource = self.personalize_backend.describe_campaign(arn)
        return json.dumps({"campaign": resource.to_dict()})

    def delete_campaign(self) -> str:
        params = json.loads(self.body)
        arn = params.get("campaignArn")
        self.personalize_backend.delete_campaign(arn)
        return "{}"

    def update_campaign(self) -> str:
        params = json.loads(self.body)
        arn = params.get("campaignArn")
        data = {k: v for k, v in params.items() if k != "campaignArn"}
        result_arn = self.personalize_backend.update_campaign(arn=arn, data=data)
        return json.dumps({"campaignArn": result_arn})

    def list_campaigns(self) -> str:
        resources = list(self.personalize_backend.campaigns.values())
        items = [
            {
                "campaignArn": r.arn,
                "name": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"campaigns": items})

    # ---- Data Deletion Job ----

    def create_data_deletion_job(self) -> str:
        params = json.loads(self.body)
        name = params.get("jobName")
        data = {k: v for k, v in params.items() if k != "jobName"}
        arn = self.personalize_backend.create_data_deletion_job(name=name, data=data)
        return json.dumps({"dataDeletionJobArn": arn})

    def describe_data_deletion_job(self) -> str:
        params = json.loads(self.body)
        arn = params.get("dataDeletionJobArn")
        resource = self.personalize_backend.describe_data_deletion_job(arn)
        return json.dumps({"dataDeletionJob": resource.to_dict()})

    def list_data_deletion_jobs(self) -> str:
        resources = list(self.personalize_backend.data_deletion_jobs.values())
        items = [
            {
                "dataDeletionJobArn": r.arn,
                "jobName": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"dataDeletionJobs": items})

    # ---- Event Tracker ----

    def create_event_tracker(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        data = {k: v for k, v in params.items() if k != "name"}
        arn, tracking_id = self.personalize_backend.create_event_tracker(
            name=name, data=data
        )
        return json.dumps({"eventTrackerArn": arn, "trackingId": tracking_id})

    def describe_event_tracker(self) -> str:
        params = json.loads(self.body)
        arn = params.get("eventTrackerArn")
        resource = self.personalize_backend.describe_event_tracker(arn)
        return json.dumps({"eventTracker": resource.to_dict()})

    def delete_event_tracker(self) -> str:
        params = json.loads(self.body)
        arn = params.get("eventTrackerArn")
        self.personalize_backend.delete_event_tracker(arn)
        return "{}"

    def list_event_trackers(self) -> str:
        resources = list(self.personalize_backend.event_trackers.values())
        items = [
            {
                "eventTrackerArn": r.arn,
                "name": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"eventTrackers": items})

    # ---- Filter ----

    def create_filter(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        data = {k: v for k, v in params.items() if k != "name"}
        arn = self.personalize_backend.create_filter(name=name, data=data)
        return json.dumps({"filterArn": arn})

    def describe_filter(self) -> str:
        params = json.loads(self.body)
        arn = params.get("filterArn")
        resource = self.personalize_backend.describe_filter(arn)
        return json.dumps({"filter": resource.to_dict()})

    def delete_filter(self) -> str:
        params = json.loads(self.body)
        arn = params.get("filterArn")
        self.personalize_backend.delete_filter(arn)
        return "{}"

    def list_filters(self) -> str:
        resources = list(self.personalize_backend.filters.values())
        items = [
            {
                "filterArn": r.arn,
                "name": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"Filters": items})

    # ---- Metric Attribution ----

    def create_metric_attribution(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        data = {k: v for k, v in params.items() if k != "name"}
        arn = self.personalize_backend.create_metric_attribution(name=name, data=data)
        return json.dumps({"metricAttributionArn": arn})

    def describe_metric_attribution(self) -> str:
        params = json.loads(self.body)
        arn = params.get("metricAttributionArn")
        resource = self.personalize_backend.describe_metric_attribution(arn)
        return json.dumps({"metricAttribution": resource.to_dict()})

    def delete_metric_attribution(self) -> str:
        params = json.loads(self.body)
        arn = params.get("metricAttributionArn")
        self.personalize_backend.delete_metric_attribution(arn)
        return "{}"

    def update_metric_attribution(self) -> str:
        params = json.loads(self.body)
        arn = params.get("metricAttributionArn")
        data = {k: v for k, v in params.items() if k != "metricAttributionArn"}
        result_arn = self.personalize_backend.update_metric_attribution(
            arn=arn, data=data
        )
        return json.dumps({"metricAttributionArn": result_arn})

    def list_metric_attributions(self) -> str:
        resources = list(self.personalize_backend.metric_attributions.values())
        items = [
            {
                "metricAttributionArn": r.arn,
                "name": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"metricAttributions": items})

    def list_metric_attribution_metrics(self) -> str:
        return json.dumps({"metrics": []})

    # ---- Recommender ----

    def create_recommender(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        data = {k: v for k, v in params.items() if k != "name"}
        arn = self.personalize_backend.create_recommender(name=name, data=data)
        return json.dumps({"recommenderArn": arn})

    def describe_recommender(self) -> str:
        params = json.loads(self.body)
        arn = params.get("recommenderArn")
        resource = self.personalize_backend.describe_recommender(arn)
        return json.dumps({"recommender": resource.to_dict()})

    def delete_recommender(self) -> str:
        params = json.loads(self.body)
        arn = params.get("recommenderArn")
        self.personalize_backend.delete_recommender(arn)
        return "{}"

    def update_recommender(self) -> str:
        params = json.loads(self.body)
        arn = params.get("recommenderArn")
        data = {k: v for k, v in params.items() if k != "recommenderArn"}
        result_arn = self.personalize_backend.update_recommender(arn=arn, data=data)
        return json.dumps({"recommenderArn": result_arn})

    def start_recommender(self) -> str:
        params = json.loads(self.body)
        arn = params.get("recommenderArn")
        result_arn = self.personalize_backend.start_recommender(arn)
        return json.dumps({"recommenderArn": result_arn})

    def stop_recommender(self) -> str:
        params = json.loads(self.body)
        arn = params.get("recommenderArn")
        result_arn = self.personalize_backend.stop_recommender(arn)
        return json.dumps({"recommenderArn": result_arn})

    def list_recommenders(self) -> str:
        resources = list(self.personalize_backend.recommenders.values())
        items = [
            {
                "recommenderArn": r.arn,
                "name": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"recommenders": items})

    # ---- Solution ----

    def create_solution(self) -> str:
        params = json.loads(self.body)
        name = params.get("name")
        data = {k: v for k, v in params.items() if k != "name"}
        arn = self.personalize_backend.create_solution(name=name, data=data)
        return json.dumps({"solutionArn": arn})

    def describe_solution(self) -> str:
        params = json.loads(self.body)
        arn = params.get("solutionArn")
        resource = self.personalize_backend.describe_solution(arn)
        return json.dumps({"solution": resource.to_dict()})

    def delete_solution(self) -> str:
        params = json.loads(self.body)
        arn = params.get("solutionArn")
        self.personalize_backend.delete_solution(arn)
        return "{}"

    def update_solution(self) -> str:
        params = json.loads(self.body)
        arn = params.get("solutionArn")
        data = {k: v for k, v in params.items() if k != "solutionArn"}
        result_arn = self.personalize_backend.update_solution(arn=arn, data=data)
        return json.dumps({"solutionArn": result_arn})

    def list_solutions(self) -> str:
        resources = list(self.personalize_backend.solutions.values())
        items = [
            {
                "solutionArn": r.arn,
                "name": r.name,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"solutions": items})

    # ---- Solution Version ----

    def create_solution_version(self) -> str:
        params = json.loads(self.body)
        solution_arn = params.get("solutionArn")
        data = {k: v for k, v in params.items() if k != "solutionArn"}
        arn = self.personalize_backend.create_solution_version(
            solution_arn=solution_arn, data=data
        )
        return json.dumps({"solutionVersionArn": arn})

    def describe_solution_version(self) -> str:
        params = json.loads(self.body)
        arn = params.get("solutionVersionArn")
        resource = self.personalize_backend.describe_solution_version(arn)
        return json.dumps({"solutionVersion": resource.to_dict()})

    def get_solution_metrics(self) -> str:
        params = json.loads(self.body)
        arn = params.get("solutionVersionArn")
        result = self.personalize_backend.get_solution_metrics(arn)
        return json.dumps(result)

    def stop_solution_version_creation(self) -> str:
        params = json.loads(self.body)
        arn = params.get("solutionVersionArn")
        self.personalize_backend.stop_solution_version_creation(arn)
        return "{}"

    def list_solution_versions(self) -> str:
        resources = list(self.personalize_backend.solution_versions.values())
        items = [
            {
                "solutionVersionArn": r.arn,
                "status": r.status,
                "creationDateTime": r.created,
                "lastUpdatedDateTime": r.updated,
            }
            for r in resources
        ]
        return json.dumps({"solutionVersions": items})

    # ---- Read-only describe ops ----

    def describe_algorithm(self) -> str:
        params = json.loads(self.body)
        arn = params.get("algorithmArn")
        result = self.personalize_backend.describe_algorithm(arn)
        return json.dumps({"algorithm": result})

    def describe_feature_transformation(self) -> str:
        params = json.loads(self.body)
        arn = params.get("featureTransformationArn")
        result = self.personalize_backend.describe_feature_transformation(arn)
        return json.dumps({"featureTransformation": result})

    def describe_recipe(self) -> str:
        params = json.loads(self.body)
        arn = params.get("recipeArn")
        result = self.personalize_backend.describe_recipe(arn)
        return json.dumps({"recipe": result})

    def list_recipes(self) -> str:
        return json.dumps({"recipes": []})

    # ---- Tags ----

    def _tags_store(self) -> dict:
        if not hasattr(self.personalize_backend, "_tags"):
            self.personalize_backend._tags = {}
        return self.personalize_backend._tags

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tags = params.get("tags") or []
        store = self._tags_store()
        store[resource_arn] = store.get(resource_arn, []) + tags
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        tag_keys = params.get("tagKeys") or []
        store = self._tags_store()
        existing = store.get(resource_arn, [])
        store[resource_arn] = [t for t in existing if t.get("tagKey") not in tag_keys]
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceArn")
        store = self._tags_store()
        return json.dumps({"tags": store.get(resource_arn, [])})
