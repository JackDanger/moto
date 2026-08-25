import uuid
from collections.abc import Iterable
from typing import Any

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.utilities.utils import get_partition

from .exceptions import ResourceNotFoundException


class Schema(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        schema: dict[str, Any],
        domain: str,
    ):
        self.name = name
        self.schema = schema
        self.domain = domain
        self.arn = f"arn:{get_partition(region)}:personalize:{region}:{account_id}:schema/{name}"
        self.created = unix_time()

    def to_dict(self, full: bool = True) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "schemaArn": self.arn,
            "domain": self.domain,
            "creationDateTime": self.created,
            "lastUpdatedDateTime": self.created,
        }
        if full:
            d["schema"] = self.schema
        return d


class PersonalizeResource:
    """Generic stub resource for personalize objects."""

    def __init__(self, arn: str, name: str, data: dict[str, Any]):
        self.arn = arn
        self.name = name
        self.data = data
        self.created = unix_time()
        self.updated = self.created
        self.status = "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arn": self.arn,
            "status": self.status,
            "creationDateTime": self.created,
            "lastUpdatedDateTime": self.updated,
            **self.data,
        }


class PersonalizeBackend(BaseBackend):
    """Implementation of Personalize APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.schemas: dict[str, Schema] = {}
        self.datasets: dict[str, PersonalizeResource] = {}
        self.dataset_groups: dict[str, PersonalizeResource] = {}
        self.dataset_import_jobs: dict[str, PersonalizeResource] = {}
        self.dataset_export_jobs: dict[str, PersonalizeResource] = {}
        self.batch_inference_jobs: dict[str, PersonalizeResource] = {}
        self.batch_segment_jobs: dict[str, PersonalizeResource] = {}
        self.campaigns: dict[str, PersonalizeResource] = {}
        self.data_deletion_jobs: dict[str, PersonalizeResource] = {}
        self.event_trackers: dict[str, PersonalizeResource] = {}
        self.filters: dict[str, PersonalizeResource] = {}
        self.metric_attributions: dict[str, PersonalizeResource] = {}
        self.recommenders: dict[str, PersonalizeResource] = {}
        self.solutions: dict[str, PersonalizeResource] = {}
        self.solution_versions: dict[str, PersonalizeResource] = {}

    def _make_arn(self, resource_type: str, name: str) -> str:
        partition = get_partition(self.region_name)
        return f"arn:{partition}:personalize:{self.region_name}:{self.account_id}:{resource_type}/{name}"

    # ---- Schema ----

    def create_schema(self, name: str, schema_dict: dict[str, Any], domain: str) -> str:
        schema = Schema(
            region=self.region_name,
            account_id=self.account_id,
            name=name,
            schema=schema_dict,
            domain=domain,
        )
        self.schemas[schema.arn] = schema
        return schema.arn

    def delete_schema(self, schema_arn: str) -> None:
        if schema_arn not in self.schemas:
            raise ResourceNotFoundException(schema_arn)
        self.schemas.pop(schema_arn, None)

    def describe_schema(self, schema_arn: str) -> Schema:
        if schema_arn not in self.schemas:
            raise ResourceNotFoundException(schema_arn)
        return self.schemas[schema_arn]

    def list_schemas(self) -> Iterable[Schema]:
        """
        Pagination is not yet implemented
        """
        return self.schemas.values()

    # ---- Dataset Group ----

    def create_dataset_group(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("dataset-group", name)
        self.dataset_groups[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_dataset_group(self, arn: str) -> PersonalizeResource:
        if arn not in self.dataset_groups:
            raise ResourceNotFoundException(arn)
        return self.dataset_groups[arn]

    def delete_dataset_group(self, arn: str) -> None:
        if arn not in self.dataset_groups:
            raise ResourceNotFoundException(arn)
        del self.dataset_groups[arn]

    # ---- Dataset ----

    def create_dataset(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("dataset", name)
        self.datasets[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_dataset(self, arn: str) -> PersonalizeResource:
        if arn not in self.datasets:
            raise ResourceNotFoundException(arn)
        return self.datasets[arn]

    def delete_dataset(self, arn: str) -> None:
        if arn not in self.datasets:
            raise ResourceNotFoundException(arn)
        del self.datasets[arn]

    def update_dataset(self, arn: str, data: dict[str, Any]) -> str:
        if arn not in self.datasets:
            raise ResourceNotFoundException(arn)
        self.datasets[arn].data.update(data)
        self.datasets[arn].updated = unix_time()
        return arn

    # ---- Dataset Import Job ----

    def create_dataset_import_job(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("dataset-import-job", f"{name}/{job_id}")
        self.dataset_import_jobs[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_dataset_import_job(self, arn: str) -> PersonalizeResource:
        if arn not in self.dataset_import_jobs:
            raise ResourceNotFoundException(arn)
        return self.dataset_import_jobs[arn]

    # ---- Dataset Export Job ----

    def create_dataset_export_job(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("dataset-export-job", f"{name}/{job_id}")
        self.dataset_export_jobs[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_dataset_export_job(self, arn: str) -> PersonalizeResource:
        if arn not in self.dataset_export_jobs:
            raise ResourceNotFoundException(arn)
        return self.dataset_export_jobs[arn]

    # ---- Batch Inference Job ----

    def create_batch_inference_job(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("batch-inference-job", f"{name}/{job_id}")
        self.batch_inference_jobs[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_batch_inference_job(self, arn: str) -> PersonalizeResource:
        if arn not in self.batch_inference_jobs:
            raise ResourceNotFoundException(arn)
        return self.batch_inference_jobs[arn]

    # ---- Batch Segment Job ----

    def create_batch_segment_job(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("batch-segment-job", f"{name}/{job_id}")
        self.batch_segment_jobs[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_batch_segment_job(self, arn: str) -> PersonalizeResource:
        if arn not in self.batch_segment_jobs:
            raise ResourceNotFoundException(arn)
        return self.batch_segment_jobs[arn]

    # ---- Campaign ----

    def create_campaign(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("campaign", name)
        self.campaigns[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_campaign(self, arn: str) -> PersonalizeResource:
        if arn not in self.campaigns:
            raise ResourceNotFoundException(arn)
        return self.campaigns[arn]

    def delete_campaign(self, arn: str) -> None:
        if arn not in self.campaigns:
            raise ResourceNotFoundException(arn)
        del self.campaigns[arn]

    def update_campaign(self, arn: str, data: dict[str, Any]) -> str:
        if arn not in self.campaigns:
            raise ResourceNotFoundException(arn)
        self.campaigns[arn].data.update(data)
        self.campaigns[arn].updated = unix_time()
        return arn

    # ---- Data Deletion Job ----

    def create_data_deletion_job(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("data-deletion-job", f"{name}/{job_id}")
        self.data_deletion_jobs[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_data_deletion_job(self, arn: str) -> PersonalizeResource:
        if arn not in self.data_deletion_jobs:
            raise ResourceNotFoundException(arn)
        return self.data_deletion_jobs[arn]

    # ---- Event Tracker ----

    def create_event_tracker(self, name: str, data: dict[str, Any]) -> tuple[str, str]:
        arn = self._make_arn("event-tracker", name)
        tracking_id = str(uuid.uuid4())
        resource = PersonalizeResource(arn=arn, name=name, data=data)
        resource.data["trackingId"] = tracking_id
        self.event_trackers[arn] = resource
        return arn, tracking_id

    def describe_event_tracker(self, arn: str) -> PersonalizeResource:
        if arn not in self.event_trackers:
            raise ResourceNotFoundException(arn)
        return self.event_trackers[arn]

    def delete_event_tracker(self, arn: str) -> None:
        if arn not in self.event_trackers:
            raise ResourceNotFoundException(arn)
        del self.event_trackers[arn]

    # ---- Filter ----

    def create_filter(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("filter", name)
        self.filters[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_filter(self, arn: str) -> PersonalizeResource:
        if arn not in self.filters:
            raise ResourceNotFoundException(arn)
        return self.filters[arn]

    def delete_filter(self, arn: str) -> None:
        if arn not in self.filters:
            raise ResourceNotFoundException(arn)
        del self.filters[arn]

    # ---- Metric Attribution ----

    def create_metric_attribution(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("metric-attribution", name)
        self.metric_attributions[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_metric_attribution(self, arn: str) -> PersonalizeResource:
        if arn not in self.metric_attributions:
            raise ResourceNotFoundException(arn)
        return self.metric_attributions[arn]

    def delete_metric_attribution(self, arn: str) -> None:
        if arn not in self.metric_attributions:
            raise ResourceNotFoundException(arn)
        del self.metric_attributions[arn]

    def update_metric_attribution(self, arn: str, data: dict[str, Any]) -> str:
        if arn not in self.metric_attributions:
            raise ResourceNotFoundException(arn)
        self.metric_attributions[arn].data.update(data)
        self.metric_attributions[arn].updated = unix_time()
        return arn

    # ---- Recommender ----

    def create_recommender(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("recommender", name)
        self.recommenders[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_recommender(self, arn: str) -> PersonalizeResource:
        if arn not in self.recommenders:
            raise ResourceNotFoundException(arn)
        return self.recommenders[arn]

    def delete_recommender(self, arn: str) -> None:
        if arn not in self.recommenders:
            raise ResourceNotFoundException(arn)
        del self.recommenders[arn]

    def update_recommender(self, arn: str, data: dict[str, Any]) -> str:
        if arn not in self.recommenders:
            raise ResourceNotFoundException(arn)
        self.recommenders[arn].data.update(data)
        self.recommenders[arn].updated = unix_time()
        return arn

    def start_recommender(self, arn: str) -> str:
        if arn not in self.recommenders:
            raise ResourceNotFoundException(arn)
        self.recommenders[arn].status = "ACTIVE"
        return arn

    def stop_recommender(self, arn: str) -> str:
        if arn not in self.recommenders:
            raise ResourceNotFoundException(arn)
        self.recommenders[arn].status = "INACTIVE"
        return arn

    # ---- Solution ----

    def create_solution(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("solution", name)
        self.solutions[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_solution(self, arn: str) -> PersonalizeResource:
        if arn not in self.solutions:
            raise ResourceNotFoundException(arn)
        return self.solutions[arn]

    def delete_solution(self, arn: str) -> None:
        if arn not in self.solutions:
            raise ResourceNotFoundException(arn)
        del self.solutions[arn]

    def update_solution(self, arn: str, data: dict[str, Any]) -> str:
        if arn not in self.solutions:
            raise ResourceNotFoundException(arn)
        self.solutions[arn].data.update(data)
        self.solutions[arn].updated = unix_time()
        return arn

    # ---- Solution Version ----

    def create_solution_version(self, solution_arn: str, data: dict[str, Any]) -> str:
        version_id = str(uuid.uuid4())
        # Derive name from solution ARN
        name = solution_arn.split("/")[-1] if "/" in solution_arn else solution_arn
        arn = self._make_arn("solution", f"{name}/solutionVersion/{version_id}")
        self.solution_versions[arn] = PersonalizeResource(arn=arn, name=name, data=data)
        return arn

    def describe_solution_version(self, arn: str) -> PersonalizeResource:
        if arn not in self.solution_versions:
            raise ResourceNotFoundException(arn)
        return self.solution_versions[arn]

    def get_solution_metrics(self, solution_version_arn: str) -> dict[str, Any]:
        if solution_version_arn not in self.solution_versions:
            raise ResourceNotFoundException(solution_version_arn)
        return {
            "solutionVersionArn": solution_version_arn,
            "metrics": {},
        }

    def stop_solution_version_creation(self, arn: str) -> None:
        if arn not in self.solution_versions:
            raise ResourceNotFoundException(arn)
        self.solution_versions[arn].status = "STOP PENDING"

    # ---- Describe read-only resources (no create) ----

    def describe_algorithm(self, algorithm_arn: str) -> dict[str, Any]:
        return {
            "algorithmArn": algorithm_arn,
            "name": algorithm_arn.split("/")[-1],
            "creationDateTime": unix_time(),
            "lastUpdatedDateTime": unix_time(),
        }

    def describe_feature_transformation(self, arn: str) -> dict[str, Any]:
        return {
            "featureTransformationArn": arn,
            "name": arn.split("/")[-1],
            "creationDateTime": unix_time(),
            "lastUpdatedDateTime": unix_time(),
        }

    def describe_recipe(self, recipe_arn: str) -> dict[str, Any]:
        return {
            "recipeArn": recipe_arn,
            "name": recipe_arn.split("/")[-1],
            "creationDateTime": unix_time(),
            "lastUpdatedDateTime": unix_time(),
            "status": "ACTIVE",
        }


personalize_backends = BackendDict(PersonalizeBackend, "personalize")
