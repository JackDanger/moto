import re
import uuid
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.utils import iso_8601_datetime_without_milliseconds
from moto.utilities.utils import get_partition

from .exceptions import (
    InvalidInputException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
    ValidationException,
)


class DatasetGroup:
    accepted_dataset_group_name_format = re.compile(r"^[a-zA-Z][a-z-A-Z0-9_]*")
    accepted_dataset_group_arn_format = re.compile(r"^[a-zA-Z0-9\-\_\.\/\:]+$")
    accepted_dataset_types = [
        "INVENTORY_PLANNING",
        "METRICS",
        "RETAIL",
        "EC2_CAPACITY",
        "CUSTOM",
        "WEB_TRAFFIC",
        "WORK_FORCE",
    ]

    def __init__(
        self,
        account_id: str,
        region_name: str,
        dataset_arns: list[str],
        dataset_group_name: str,
        domain: str,
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.creation_date = iso_8601_datetime_without_milliseconds(datetime.now())
        self.modified_date = self.creation_date

        self.arn = f"arn:{get_partition(region_name)}:forecast:{region_name}:{account_id}:dataset-group/{dataset_group_name}"
        self.dataset_arns = dataset_arns if dataset_arns else []
        self.dataset_group_name = dataset_group_name
        self.domain = domain
        self.tags = tags
        self._validate()

    def update(self, dataset_arns: list[str]) -> None:
        self.dataset_arns = dataset_arns
        self.last_modified_date = iso_8601_datetime_without_milliseconds(datetime.now())

    def _validate(self) -> None:
        errors = []

        errors.extend(self._validate_dataset_group_name())
        errors.extend(self._validate_dataset_group_name_len())
        errors.extend(self._validate_dataset_group_domain())

        if errors:
            err_count = len(errors)
            message = str(err_count) + " validation error"
            message += "s" if err_count > 1 else ""
            message += " detected: "
            message += "; ".join(errors)
            raise ValidationException(message)

    def _validate_dataset_group_name(self) -> list[str]:
        errors = []
        if not re.match(
            self.accepted_dataset_group_name_format, self.dataset_group_name
        ):
            errors.append(
                "Value '"
                + self.dataset_group_name
                + "' at 'datasetGroupName' failed to satisfy constraint: Member must satisfy regular expression pattern "
                + self.accepted_dataset_group_name_format.pattern
            )
        return errors

    def _validate_dataset_group_name_len(self) -> list[str]:
        errors = []
        if len(self.dataset_group_name) >= 64:
            errors.append(
                "Value '"
                + self.dataset_group_name
                + "' at 'datasetGroupName' failed to satisfy constraint: Member must have length less than or equal to 63"
            )
        return errors

    def _validate_dataset_group_domain(self) -> list[str]:
        errors = []
        if self.domain not in self.accepted_dataset_types:
            errors.append(
                "Value '"
                + self.domain
                + "' at 'domain' failed to satisfy constraint: Member must satisfy enum value set "
                + str(self.accepted_dataset_types)
            )
        return errors


def _now() -> str:
    return iso_8601_datetime_without_milliseconds(datetime.now())


class ForecastResource:
    """Generic stub resource for forecast objects."""

    def __init__(self, arn: str, name: str, data: dict[str, Any]):
        self.arn = arn
        self.name = name
        self.data = data
        self.creation_time = _now()
        self.last_modification_time = self.creation_time
        self.status = "ACTIVE"


class ForecastBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.dataset_groups: dict[str, DatasetGroup] = {}
        self.datasets: dict[str, ForecastResource] = {}
        self.dataset_import_jobs: dict[str, ForecastResource] = {}
        self.predictors: dict[str, ForecastResource] = {}
        self.auto_predictors: dict[str, ForecastResource] = {}
        self.forecasts: dict[str, ForecastResource] = {}
        self.forecast_export_jobs: dict[str, ForecastResource] = {}
        self.predictor_backtest_export_jobs: dict[str, ForecastResource] = {}
        self.explainabilities: dict[str, ForecastResource] = {}
        self.explainability_exports: dict[str, ForecastResource] = {}
        self.monitors: dict[str, ForecastResource] = {}
        self.what_if_analyses: dict[str, ForecastResource] = {}
        self.what_if_forecasts: dict[str, ForecastResource] = {}
        self.what_if_forecast_exports: dict[str, ForecastResource] = {}

    def _make_arn(self, resource_type: str, name: str) -> str:
        partition = get_partition(self.region_name)
        return f"arn:{partition}:forecast:{self.region_name}:{self.account_id}:{resource_type}/{name}"

    def create_dataset_group(
        self,
        dataset_group_name: str,
        domain: str,
        dataset_arns: list[str],
        tags: list[dict[str, str]],
    ) -> DatasetGroup:
        dataset_group = DatasetGroup(
            account_id=self.account_id,
            region_name=self.region_name,
            dataset_group_name=dataset_group_name,
            domain=domain,
            dataset_arns=dataset_arns,
            tags=tags,
        )

        if dataset_arns:
            for dataset_arn in dataset_arns:
                if dataset_arn not in self.datasets:
                    raise InvalidInputException(
                        "Dataset arns: [" + dataset_arn + "] are not found"
                    )

        if self.dataset_groups.get(dataset_group.arn):
            raise ResourceAlreadyExistsException(
                "A dataset group already exists with the arn: " + dataset_group.arn
            )

        self.dataset_groups[dataset_group.arn] = dataset_group
        return dataset_group

    def describe_dataset_group(self, dataset_group_arn: str) -> DatasetGroup:
        try:
            return self.dataset_groups[dataset_group_arn]
        except KeyError:
            raise ResourceNotFoundException("No resource found " + dataset_group_arn)

    def delete_dataset_group(self, dataset_group_arn: str) -> None:
        try:
            del self.dataset_groups[dataset_group_arn]
        except KeyError:
            raise ResourceNotFoundException("No resource found " + dataset_group_arn)

    def update_dataset_group(
        self, dataset_group_arn: str, dataset_arns: list[str]
    ) -> None:
        try:
            dsg = self.dataset_groups[dataset_group_arn]
        except KeyError:
            raise ResourceNotFoundException("No resource found " + dataset_group_arn)

        for dataset_arn in dataset_arns:
            if dataset_arn not in dsg.dataset_arns:
                raise InvalidInputException(
                    "Dataset arns: [" + dataset_arn + "] are not found"
                )

        dsg.update(dataset_arns)

    def list_dataset_groups(self) -> list[DatasetGroup]:
        return [v for (_, v) in self.dataset_groups.items()]

    # ---- Dataset ----

    def create_dataset(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("dataset", name)
        if arn in self.datasets:
            raise ResourceAlreadyExistsException(f"Dataset already exists: {name}")
        self.datasets[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_dataset(self, dataset_arn: str) -> ForecastResource:
        if dataset_arn not in self.datasets:
            raise ResourceNotFoundException("No resource found " + dataset_arn)
        return self.datasets[dataset_arn]

    def delete_dataset(self, dataset_arn: str) -> None:
        if dataset_arn not in self.datasets:
            raise ResourceNotFoundException("No resource found " + dataset_arn)
        del self.datasets[dataset_arn]

    # ---- Dataset Import Job ----

    def create_dataset_import_job(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("dataset-import-job", f"{name}/{job_id}")
        self.dataset_import_jobs[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_dataset_import_job(self, arn: str) -> ForecastResource:
        if arn not in self.dataset_import_jobs:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.dataset_import_jobs[arn]

    def delete_dataset_import_job(self, arn: str) -> None:
        if arn not in self.dataset_import_jobs:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.dataset_import_jobs[arn]

    # ---- Predictor ----

    def create_predictor(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("predictor", name)
        self.predictors[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_predictor(self, arn: str) -> ForecastResource:
        if arn not in self.predictors:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.predictors[arn]

    def delete_predictor(self, arn: str) -> None:
        if arn not in self.predictors:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.predictors[arn]

    def get_accuracy_metrics(self, predictor_arn: str) -> dict[str, Any]:
        if predictor_arn not in self.predictors:
            raise ResourceNotFoundException("No resource found " + predictor_arn)
        return {"PredictorEvaluationResults": []}

    # ---- Auto Predictor ----

    def create_auto_predictor(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("predictor", name)
        self.auto_predictors[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_auto_predictor(self, arn: str) -> ForecastResource:
        if arn not in self.auto_predictors:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.auto_predictors[arn]

    # ---- Forecast ----

    def create_forecast(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("forecast", name)
        self.forecasts[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_forecast(self, arn: str) -> ForecastResource:
        if arn not in self.forecasts:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.forecasts[arn]

    def delete_forecast(self, arn: str) -> None:
        if arn not in self.forecasts:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.forecasts[arn]

    # ---- Forecast Export Job ----

    def create_forecast_export_job(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("forecast-export-job", f"{name}/{job_id}")
        self.forecast_export_jobs[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_forecast_export_job(self, arn: str) -> ForecastResource:
        if arn not in self.forecast_export_jobs:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.forecast_export_jobs[arn]

    def delete_forecast_export_job(self, arn: str) -> None:
        if arn not in self.forecast_export_jobs:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.forecast_export_jobs[arn]

    # ---- Predictor Backtest Export Job ----

    def create_predictor_backtest_export_job(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("predictor-backtest-export-job", f"{name}/{job_id}")
        self.predictor_backtest_export_jobs[arn] = ForecastResource(
            arn=arn, name=name, data=data
        )
        return arn

    def describe_predictor_backtest_export_job(self, arn: str) -> ForecastResource:
        if arn not in self.predictor_backtest_export_jobs:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.predictor_backtest_export_jobs[arn]

    def delete_predictor_backtest_export_job(self, arn: str) -> None:
        if arn not in self.predictor_backtest_export_jobs:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.predictor_backtest_export_jobs[arn]

    # ---- Explainability ----

    def create_explainability(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("explainability", name)
        self.explainabilities[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_explainability(self, arn: str) -> ForecastResource:
        if arn not in self.explainabilities:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.explainabilities[arn]

    def delete_explainability(self, arn: str) -> None:
        if arn not in self.explainabilities:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.explainabilities[arn]

    # ---- Explainability Export ----

    def create_explainability_export(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("explainability-export", f"{name}/{job_id}")
        self.explainability_exports[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_explainability_export(self, arn: str) -> ForecastResource:
        if arn not in self.explainability_exports:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.explainability_exports[arn]

    def delete_explainability_export(self, arn: str) -> None:
        if arn not in self.explainability_exports:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.explainability_exports[arn]

    # ---- Monitor ----

    def create_monitor(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("monitor", name)
        self.monitors[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_monitor(self, arn: str) -> ForecastResource:
        if arn not in self.monitors:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.monitors[arn]

    def delete_monitor(self, arn: str) -> None:
        if arn not in self.monitors:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.monitors[arn]

    # ---- What-If Analysis ----

    def create_what_if_analysis(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("what-if-analysis", name)
        self.what_if_analyses[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_what_if_analysis(self, arn: str) -> ForecastResource:
        if arn not in self.what_if_analyses:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.what_if_analyses[arn]

    def delete_what_if_analysis(self, arn: str) -> None:
        if arn not in self.what_if_analyses:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.what_if_analyses[arn]

    # ---- What-If Forecast ----

    def create_what_if_forecast(self, name: str, data: dict[str, Any]) -> str:
        arn = self._make_arn("what-if-forecast", name)
        self.what_if_forecasts[arn] = ForecastResource(arn=arn, name=name, data=data)
        return arn

    def describe_what_if_forecast(self, arn: str) -> ForecastResource:
        if arn not in self.what_if_forecasts:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.what_if_forecasts[arn]

    def delete_what_if_forecast(self, arn: str) -> None:
        if arn not in self.what_if_forecasts:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.what_if_forecasts[arn]

    # ---- What-If Forecast Export ----

    def create_what_if_forecast_export(self, name: str, data: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        arn = self._make_arn("what-if-forecast-export", f"{name}/{job_id}")
        self.what_if_forecast_exports[arn] = ForecastResource(
            arn=arn, name=name, data=data
        )
        return arn

    def describe_what_if_forecast_export(self, arn: str) -> ForecastResource:
        if arn not in self.what_if_forecast_exports:
            raise ResourceNotFoundException("No resource found " + arn)
        return self.what_if_forecast_exports[arn]

    def delete_what_if_forecast_export(self, arn: str) -> None:
        if arn not in self.what_if_forecast_exports:
            raise ResourceNotFoundException("No resource found " + arn)
        del self.what_if_forecast_exports[arn]

    # ---- Resume / Stop ----

    def resume_resource(self, resource_arn: str) -> None:
        # Find resource in any store and mark active
        for store in [
            self.monitors,
            self.predictors,
            self.auto_predictors,
        ]:
            if resource_arn in store:
                store[resource_arn].status = "ACTIVE"
                return
        raise ResourceNotFoundException("No resource found " + resource_arn)

    def stop_resource(self, resource_arn: str) -> None:
        for store in [
            self.predictors,
            self.auto_predictors,
            self.forecast_export_jobs,
            self.predictor_backtest_export_jobs,
            self.explainability_exports,
            self.what_if_forecast_exports,
            self.dataset_import_jobs,
        ]:
            if resource_arn in store:
                store[resource_arn].status = "STOPPED"
                return
        raise ResourceNotFoundException("No resource found " + resource_arn)

    def delete_resource_tree(self, resource_arn: str) -> None:
        # Delete from any store that has this ARN
        for store in [
            self.datasets,
            self.dataset_import_jobs,
            self.predictors,
            self.auto_predictors,
            self.forecasts,
            self.forecast_export_jobs,
            self.predictor_backtest_export_jobs,
            self.explainabilities,
            self.explainability_exports,
            self.monitors,
            self.what_if_analyses,
            self.what_if_forecasts,
            self.what_if_forecast_exports,
        ]:
            store.pop(resource_arn, None)
        self.dataset_groups.pop(resource_arn, None)


forecast_backends = BackendDict(ForecastBackend, "forecast")
