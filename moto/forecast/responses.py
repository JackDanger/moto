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

    # ---- Dataset Group ----

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

    # ---- Dataset ----

    def create_dataset(self) -> TYPE_RESPONSE:
        name = self._get_param("DatasetName")
        data = {k: v for k, v in json.loads(self.body).items() if k != "DatasetName"}
        arn = self.forecast_backend.create_dataset(name=name, data=data)
        return 200, {}, json.dumps({"DatasetArn": arn})

    def describe_dataset(self) -> TYPE_RESPONSE:
        arn = self._get_param("DatasetArn")
        resource = self.forecast_backend.describe_dataset(arn)
        response = {
            "DatasetArn": resource.arn,
            "DatasetName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_dataset(self) -> TYPE_RESPONSE:
        arn = self._get_param("DatasetArn")
        self.forecast_backend.delete_dataset(arn)
        return 200, {}, ""

    def list_datasets(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.datasets.values())
        items = [
            {
                "DatasetArn": r.arn,
                "DatasetName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"Datasets": items})

    # ---- Dataset Import Job ----

    def create_dataset_import_job(self) -> TYPE_RESPONSE:
        name = self._get_param("DatasetImportJobName")
        data = {
            k: v
            for k, v in json.loads(self.body).items()
            if k != "DatasetImportJobName"
        }
        arn = self.forecast_backend.create_dataset_import_job(name=name, data=data)
        return 200, {}, json.dumps({"DatasetImportJobArn": arn})

    def describe_dataset_import_job(self) -> TYPE_RESPONSE:
        arn = self._get_param("DatasetImportJobArn")
        resource = self.forecast_backend.describe_dataset_import_job(arn)
        response = {
            "DatasetImportJobArn": resource.arn,
            "DatasetImportJobName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_dataset_import_job(self) -> TYPE_RESPONSE:
        arn = self._get_param("DatasetImportJobArn")
        self.forecast_backend.delete_dataset_import_job(arn)
        return 200, {}, ""

    def list_dataset_import_jobs(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.dataset_import_jobs.values())
        items = [
            {
                "DatasetImportJobArn": r.arn,
                "DatasetImportJobName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"DatasetImportJobs": items})

    # ---- Predictor ----

    def create_predictor(self) -> TYPE_RESPONSE:
        name = self._get_param("PredictorName")
        data = {k: v for k, v in json.loads(self.body).items() if k != "PredictorName"}
        arn = self.forecast_backend.create_predictor(name=name, data=data)
        return 200, {}, json.dumps({"PredictorArn": arn})

    def describe_predictor(self) -> TYPE_RESPONSE:
        arn = self._get_param("PredictorArn")
        resource = self.forecast_backend.describe_predictor(arn)
        response = {
            "PredictorArn": resource.arn,
            "PredictorName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_predictor(self) -> TYPE_RESPONSE:
        arn = self._get_param("PredictorArn")
        self.forecast_backend.delete_predictor(arn)
        return 200, {}, ""

    def list_predictors(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.predictors.values())
        items = [
            {
                "PredictorArn": r.arn,
                "PredictorName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"Predictors": items})

    def get_accuracy_metrics(self) -> TYPE_RESPONSE:
        predictor_arn = self._get_param("PredictorArn")
        result = self.forecast_backend.get_accuracy_metrics(predictor_arn)
        return 200, {}, json.dumps(result)

    # ---- Auto Predictor ----

    def create_auto_predictor(self) -> TYPE_RESPONSE:
        name = self._get_param("PredictorName")
        data = {k: v for k, v in json.loads(self.body).items() if k != "PredictorName"}
        arn = self.forecast_backend.create_auto_predictor(name=name, data=data)
        return 200, {}, json.dumps({"PredictorArn": arn})

    def describe_auto_predictor(self) -> TYPE_RESPONSE:
        arn = self._get_param("PredictorArn")
        resource = self.forecast_backend.describe_auto_predictor(arn)
        response = {
            "PredictorArn": resource.arn,
            "PredictorName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    # ---- Forecast ----

    def create_forecast(self) -> TYPE_RESPONSE:
        name = self._get_param("ForecastName")
        data = {k: v for k, v in json.loads(self.body).items() if k != "ForecastName"}
        arn = self.forecast_backend.create_forecast(name=name, data=data)
        return 200, {}, json.dumps({"ForecastArn": arn})

    def describe_forecast(self) -> TYPE_RESPONSE:
        arn = self._get_param("ForecastArn")
        resource = self.forecast_backend.describe_forecast(arn)
        response = {
            "ForecastArn": resource.arn,
            "ForecastName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_forecast(self) -> TYPE_RESPONSE:
        arn = self._get_param("ForecastArn")
        self.forecast_backend.delete_forecast(arn)
        return 200, {}, ""

    def list_forecasts(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.forecasts.values())
        items = [
            {
                "ForecastArn": r.arn,
                "ForecastName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"Forecasts": items})

    # ---- Forecast Export Job ----

    def create_forecast_export_job(self) -> TYPE_RESPONSE:
        name = self._get_param("ForecastExportJobName")
        data = {
            k: v
            for k, v in json.loads(self.body).items()
            if k != "ForecastExportJobName"
        }
        arn = self.forecast_backend.create_forecast_export_job(name=name, data=data)
        return 200, {}, json.dumps({"ForecastExportJobArn": arn})

    def describe_forecast_export_job(self) -> TYPE_RESPONSE:
        arn = self._get_param("ForecastExportJobArn")
        resource = self.forecast_backend.describe_forecast_export_job(arn)
        response = {
            "ForecastExportJobArn": resource.arn,
            "ForecastExportJobName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_forecast_export_job(self) -> TYPE_RESPONSE:
        arn = self._get_param("ForecastExportJobArn")
        self.forecast_backend.delete_forecast_export_job(arn)
        return 200, {}, ""

    def list_forecast_export_jobs(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.forecast_export_jobs.values())
        items = [
            {
                "ForecastExportJobArn": r.arn,
                "ForecastExportJobName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"ForecastExportJobs": items})

    # ---- Predictor Backtest Export Job ----

    def create_predictor_backtest_export_job(self) -> TYPE_RESPONSE:
        name = self._get_param("PredictorBacktestExportJobName")
        data = {
            k: v
            for k, v in json.loads(self.body).items()
            if k != "PredictorBacktestExportJobName"
        }
        arn = self.forecast_backend.create_predictor_backtest_export_job(
            name=name, data=data
        )
        return 200, {}, json.dumps({"PredictorBacktestExportJobArn": arn})

    def describe_predictor_backtest_export_job(self) -> TYPE_RESPONSE:
        arn = self._get_param("PredictorBacktestExportJobArn")
        resource = self.forecast_backend.describe_predictor_backtest_export_job(arn)
        response = {
            "PredictorBacktestExportJobArn": resource.arn,
            "PredictorBacktestExportJobName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_predictor_backtest_export_job(self) -> TYPE_RESPONSE:
        arn = self._get_param("PredictorBacktestExportJobArn")
        self.forecast_backend.delete_predictor_backtest_export_job(arn)
        return 200, {}, ""

    def list_predictor_backtest_export_jobs(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.predictor_backtest_export_jobs.values())
        items = [
            {
                "PredictorBacktestExportJobArn": r.arn,
                "PredictorBacktestExportJobName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"PredictorBacktestExportJobs": items})

    # ---- Explainability ----

    def create_explainability(self) -> TYPE_RESPONSE:
        name = self._get_param("ExplainabilityName")
        data = {
            k: v
            for k, v in json.loads(self.body).items()
            if k != "ExplainabilityName"
        }
        arn = self.forecast_backend.create_explainability(name=name, data=data)
        return 200, {}, json.dumps({"ExplainabilityArn": arn})

    def describe_explainability(self) -> TYPE_RESPONSE:
        arn = self._get_param("ExplainabilityArn")
        resource = self.forecast_backend.describe_explainability(arn)
        response = {
            "ExplainabilityArn": resource.arn,
            "ExplainabilityName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_explainability(self) -> TYPE_RESPONSE:
        arn = self._get_param("ExplainabilityArn")
        self.forecast_backend.delete_explainability(arn)
        return 200, {}, ""

    def list_explainabilities(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.explainabilities.values())
        items = [
            {
                "ExplainabilityArn": r.arn,
                "ExplainabilityName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"Explainabilities": items})

    # ---- Explainability Export ----

    def create_explainability_export(self) -> TYPE_RESPONSE:
        name = self._get_param("ExplainabilityExportName")
        data = {
            k: v
            for k, v in json.loads(self.body).items()
            if k != "ExplainabilityExportName"
        }
        arn = self.forecast_backend.create_explainability_export(name=name, data=data)
        return 200, {}, json.dumps({"ExplainabilityExportArn": arn})

    def describe_explainability_export(self) -> TYPE_RESPONSE:
        arn = self._get_param("ExplainabilityExportArn")
        resource = self.forecast_backend.describe_explainability_export(arn)
        response = {
            "ExplainabilityExportArn": resource.arn,
            "ExplainabilityExportName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_explainability_export(self) -> TYPE_RESPONSE:
        arn = self._get_param("ExplainabilityExportArn")
        self.forecast_backend.delete_explainability_export(arn)
        return 200, {}, ""

    def list_explainability_exports(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.explainability_exports.values())
        items = [
            {
                "ExplainabilityExportArn": r.arn,
                "ExplainabilityExportName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"ExplainabilityExports": items})

    # ---- Monitor ----

    def create_monitor(self) -> TYPE_RESPONSE:
        name = self._get_param("MonitorName")
        data = {k: v for k, v in json.loads(self.body).items() if k != "MonitorName"}
        arn = self.forecast_backend.create_monitor(name=name, data=data)
        return 200, {}, json.dumps({"MonitorArn": arn})

    def describe_monitor(self) -> TYPE_RESPONSE:
        arn = self._get_param("MonitorArn")
        resource = self.forecast_backend.describe_monitor(arn)
        response = {
            "MonitorArn": resource.arn,
            "MonitorName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_monitor(self) -> TYPE_RESPONSE:
        arn = self._get_param("MonitorArn")
        self.forecast_backend.delete_monitor(arn)
        return 200, {}, ""

    def list_monitors(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.monitors.values())
        items = [
            {
                "MonitorArn": r.arn,
                "MonitorName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"Monitors": items})

    def list_monitor_evaluations(self) -> TYPE_RESPONSE:
        return 200, {}, json.dumps({"PredictorMonitorEvaluations": []})

    # ---- What-If Analysis ----

    def create_what_if_analysis(self) -> TYPE_RESPONSE:
        name = self._get_param("WhatIfAnalysisName")
        data = {
            k: v
            for k, v in json.loads(self.body).items()
            if k != "WhatIfAnalysisName"
        }
        arn = self.forecast_backend.create_what_if_analysis(name=name, data=data)
        return 200, {}, json.dumps({"WhatIfAnalysisArn": arn})

    def describe_what_if_analysis(self) -> TYPE_RESPONSE:
        arn = self._get_param("WhatIfAnalysisArn")
        resource = self.forecast_backend.describe_what_if_analysis(arn)
        response = {
            "WhatIfAnalysisArn": resource.arn,
            "WhatIfAnalysisName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_what_if_analysis(self) -> TYPE_RESPONSE:
        arn = self._get_param("WhatIfAnalysisArn")
        self.forecast_backend.delete_what_if_analysis(arn)
        return 200, {}, ""

    def list_what_if_analyses(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.what_if_analyses.values())
        items = [
            {
                "WhatIfAnalysisArn": r.arn,
                "WhatIfAnalysisName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"WhatIfAnalyses": items})

    # ---- What-If Forecast ----

    def create_what_if_forecast(self) -> TYPE_RESPONSE:
        name = self._get_param("WhatIfForecastName")
        data = {
            k: v
            for k, v in json.loads(self.body).items()
            if k != "WhatIfForecastName"
        }
        arn = self.forecast_backend.create_what_if_forecast(name=name, data=data)
        return 200, {}, json.dumps({"WhatIfForecastArn": arn})

    def describe_what_if_forecast(self) -> TYPE_RESPONSE:
        arn = self._get_param("WhatIfForecastArn")
        resource = self.forecast_backend.describe_what_if_forecast(arn)
        response = {
            "WhatIfForecastArn": resource.arn,
            "WhatIfForecastName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_what_if_forecast(self) -> TYPE_RESPONSE:
        arn = self._get_param("WhatIfForecastArn")
        self.forecast_backend.delete_what_if_forecast(arn)
        return 200, {}, ""

    def list_what_if_forecasts(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.what_if_forecasts.values())
        items = [
            {
                "WhatIfForecastArn": r.arn,
                "WhatIfForecastName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"WhatIfForecasts": items})

    # ---- What-If Forecast Export ----

    def create_what_if_forecast_export(self) -> TYPE_RESPONSE:
        name = self._get_param("WhatIfForecastExportName")
        data = {
            k: v
            for k, v in json.loads(self.body).items()
            if k != "WhatIfForecastExportName"
        }
        arn = self.forecast_backend.create_what_if_forecast_export(name=name, data=data)
        return 200, {}, json.dumps({"WhatIfForecastExportArn": arn})

    def describe_what_if_forecast_export(self) -> TYPE_RESPONSE:
        arn = self._get_param("WhatIfForecastExportArn")
        resource = self.forecast_backend.describe_what_if_forecast_export(arn)
        response = {
            "WhatIfForecastExportArn": resource.arn,
            "WhatIfForecastExportName": resource.name,
            "CreationTime": resource.creation_time,
            "LastModificationTime": resource.last_modification_time,
            "Status": resource.status,
            **resource.data,
        }
        return 200, {}, json.dumps(response)

    def delete_what_if_forecast_export(self) -> TYPE_RESPONSE:
        arn = self._get_param("WhatIfForecastExportArn")
        self.forecast_backend.delete_what_if_forecast_export(arn)
        return 200, {}, ""

    def list_what_if_forecast_exports(self) -> TYPE_RESPONSE:
        resources = list(self.forecast_backend.what_if_forecast_exports.values())
        items = [
            {
                "WhatIfForecastExportArn": r.arn,
                "WhatIfForecastExportName": r.name,
                "CreationTime": r.creation_time,
                "LastModificationTime": r.last_modification_time,
                "Status": r.status,
            }
            for r in resources
        ]
        return 200, {}, json.dumps({"WhatIfForecastExports": items})

    # ---- Resume / Stop / Delete Tree ----

    def resume_resource(self) -> TYPE_RESPONSE:
        resource_arn = self._get_param("ResourceArn")
        self.forecast_backend.resume_resource(resource_arn)
        return 200, {}, ""

    def stop_resource(self) -> TYPE_RESPONSE:
        resource_arn = self._get_param("ResourceArn")
        self.forecast_backend.stop_resource(resource_arn)
        return 200, {}, ""

    def delete_resource_tree(self) -> TYPE_RESPONSE:
        resource_arn = self._get_param("ResourceArn")
        self.forecast_backend.delete_resource_tree(resource_arn)
        return 200, {}, ""

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
