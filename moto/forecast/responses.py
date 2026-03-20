import json

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import ForecastBackend, forecast_backends


class ForecastResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="forecast")

    @property
    def forecast_backend(self) -> ForecastBackend:
        return forecast_backends[self.current_account][self.region]

    def create_dataset_group(self) -> TYPE_RESPONSE:
        dataset_group_name = self._get_param("DatasetGroupName")
        domain = self._get_param("Domain")
        dataset_arns = self._get_param("DatasetArns")
        tags = self._get_param("Tags")

        dataset_group = self.forecast_backend.create_dataset_group(
            dataset_group_name=dataset_group_name,
            domain=domain,
            dataset_arns=dataset_arns,
            tags=tags,
        )
        response = {"DatasetGroupArn": dataset_group.arn}
        return 200, {}, json.dumps(response)

    def describe_dataset_group(self) -> TYPE_RESPONSE:
        dataset_group_arn = self._get_param("DatasetGroupArn")

        dataset_group = self.forecast_backend.describe_dataset_group(
            dataset_group_arn=dataset_group_arn
        )
        response = {
            "CreationTime": dataset_group.creation_date,
            "DatasetArns": dataset_group.dataset_arns,
            "DatasetGroupArn": dataset_group.arn,
            "DatasetGroupName": dataset_group.dataset_group_name,
            "Domain": dataset_group.domain,
            "LastModificationTime": dataset_group.modified_date,
            "Status": "ACTIVE",
        }
        return 200, {}, json.dumps(response)

    def delete_dataset_group(self) -> TYPE_RESPONSE:
        dataset_group_arn = self._get_param("DatasetGroupArn")
        self.forecast_backend.delete_dataset_group(dataset_group_arn)
        return 200, {}, ""

    def update_dataset_group(self) -> TYPE_RESPONSE:
        dataset_group_arn = self._get_param("DatasetGroupArn")
        dataset_arns = self._get_param("DatasetArns")
        self.forecast_backend.update_dataset_group(dataset_group_arn, dataset_arns)
        return 200, {}, ""

    def list_dataset_groups(self) -> TYPE_RESPONSE:
        list_all = sorted(
            [
                {
                    "DatasetGroupArn": dsg.arn,
                    "DatasetGroupName": dsg.dataset_group_name,
                    "CreationTime": dsg.creation_date,
                    "LastModificationTime": dsg.creation_date,
                }
                for dsg in self.forecast_backend.list_dataset_groups()
            ],
            key=lambda x: x["LastModificationTime"],
            reverse=True,
        )
        response = {"DatasetGroups": list_all}
        return 200, {}, json.dumps(response)

    # ---- Stub list operations ----

    def list_datasets(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"Datasets": []})

    def list_dataset_import_jobs(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"DatasetImportJobs": []})

    def list_forecasts(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"Forecasts": []})

    def list_forecast_export_jobs(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"ForecastExportJobs": []})

    def list_predictors(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"Predictors": []})

    def list_predictor_backtest_export_jobs(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"PredictorBacktestExportJobs": []})

    def list_explainabilities(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"Explainabilities": []})

    def list_explainability_exports(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"ExplainabilityExports": []})

    def list_monitors(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"Monitors": []})

    def list_monitor_evaluations(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"PredictorMonitorEvaluations": []})

    def list_what_if_analyses(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"WhatIfAnalyses": []})

    def list_what_if_forecasts(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"WhatIfForecasts": []})

    def list_what_if_forecast_exports(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"WhatIfForecastExports": []})

    # ---- Tags ----

    def _tags_store(self) -> dict:
        if not hasattr(self.forecast_backend, "_tags"):
            self.forecast_backend._tags = {}
        return self.forecast_backend._tags

    def tag_resource(self) -> TYPE_RESPONSE:
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags") or []
        store = self._tags_store()
        store[resource_arn] = store.get(resource_arn, []) + tags
        return 200, {}, json.dumps({})

    def untag_resource(self) -> TYPE_RESPONSE:
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys") or []
        store = self._tags_store()
        existing = store.get(resource_arn, [])
        store[resource_arn] = [t for t in existing if t.get("Key") not in tag_keys]
        return 200, {}, json.dumps({})

    def list_tags_for_resource(self) -> TYPE_RESPONSE:
        resource_arn = self._get_param("ResourceArn")
        store = self._tags_store()
        return 200, {}, json.dumps({"Tags": store.get(resource_arn, [])})
