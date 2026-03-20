import math
import uuid
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend, InstanceTrackerMeta
from moto.core.common_models import BaseModel
from moto.core.utils import camelcase_to_pascal, underscores_to_camelcase, utcnow
from moto.utilities.paginator import paginate
from moto.utilities.utils import get_partition

from .exceptions import (
    AlreadyExistsException,
    ConflictException,
    ResourceNotFoundException,
    RulesetAlreadyExistsException,
    RulesetNotFoundException,
    ValidationException,
)


class DataBrewBackend(BaseBackend):
    PAGINATION_MODEL = {
        "list_recipes": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "name",
        },
        "list_recipe_versions": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "name",
        },
        "list_rulesets": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "name",
        },
        "list_datasets": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "name",
        },
        "list_jobs": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "name",
        },
        "list_projects": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "name",
        },
        "list_schedules": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "name",
        },
    }

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.recipes: dict[str, FakeRecipe] = OrderedDict()
        self.rulesets: dict[str, FakeRuleset] = OrderedDict()
        self.datasets: dict[str, FakeDataset] = OrderedDict()
        self.jobs: dict[str, FakeJob] = OrderedDict()
        self.projects: dict[str, FakeProject] = OrderedDict()
        self.schedules: dict[str, FakeSchedule] = OrderedDict()

    @staticmethod
    def validate_length(param: str, param_name: str, max_length: int) -> None:
        if len(param) > max_length:
            raise ValidationException(
                f"1 validation error detected: Value '{param}' at '{param_name}' failed to "
                f"satisfy constraint: Member must have length less than or equal to {max_length}"
            )

    def create_recipe(
        self,
        recipe_name: str,
        recipe_description: str,
        recipe_steps: list[dict[str, Any]],
        tags: dict[str, str],
    ) -> "FakeRecipeVersion":
        # https://docs.aws.amazon.com/databrew/latest/dg/API_CreateRecipe.html
        if recipe_name in self.recipes:
            raise ConflictException(f"The recipe {recipe_name} already exists")

        recipe = FakeRecipe(
            self.region_name, recipe_name, recipe_description, recipe_steps, tags
        )
        self.recipes[recipe_name] = recipe
        return recipe.latest_working

    def delete_recipe_version(self, recipe_name: str, recipe_version: str) -> None:
        if not FakeRecipe.version_is_valid(recipe_version, latest_published=False):
            raise ValidationException(
                f"Recipe {recipe_name} version {recipe_version} is invalid."
            )

        try:
            recipe = self.recipes[recipe_name]
        except KeyError:
            raise ResourceNotFoundException(f"The recipe {recipe_name} wasn't found")

        if (
            recipe_version != FakeRecipe.LATEST_WORKING
            and float(recipe_version) not in recipe.versions
        ):
            raise ResourceNotFoundException(
                f"The recipe {recipe_name} version {recipe_version} wasn't found."
            )

        if recipe_version in (
            FakeRecipe.LATEST_WORKING,
            str(recipe.latest_working.version),
        ):
            if recipe.latest_published is not None:
                # Can only delete latest working version when there are no others
                raise ValidationException(
                    f"Recipe version {recipe_version} is not allowed to be deleted"
                )
            else:
                del self.recipes[recipe_name]
        else:
            recipe.delete_published_version(recipe_version)

    def update_recipe(
        self,
        recipe_name: str,
        recipe_description: str,
        recipe_steps: list[dict[str, Any]],
    ) -> None:
        if recipe_name not in self.recipes:
            raise ResourceNotFoundException(f"The recipe {recipe_name} wasn't found")

        recipe = self.recipes[recipe_name]
        recipe.update(recipe_description, recipe_steps)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_recipes(
        self, recipe_version: Optional[str] = None
    ) -> list["FakeRecipeVersion"]:
        # https://docs.aws.amazon.com/databrew/latest/dg/API_ListRecipes.html
        if recipe_version == FakeRecipe.LATEST_WORKING:
            version = "latest_working"
        elif recipe_version in (None, FakeRecipe.LATEST_PUBLISHED):
            version = "latest_published"
        else:
            raise ValidationException(
                f"Invalid version {recipe_version}. "
                "Valid versions are LATEST_PUBLISHED and LATEST_WORKING."
            )
        recipes = [getattr(self.recipes[key], version) for key in self.recipes]
        return [r for r in recipes if r is not None]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_recipe_versions(self, recipe_name: str) -> list["FakeRecipeVersion"]:
        # https://docs.aws.amazon.com/databrew/latest/dg/API_ListRecipeVersions.html
        self.validate_length(recipe_name, "name", 255)

        recipe = self.recipes.get(recipe_name)
        if recipe is None:
            return []

        latest_working = recipe.latest_working

        recipe_versions = [
            recipe_version
            for recipe_version in recipe.versions.values()
            if recipe_version is not latest_working
        ]
        return [r for r in recipe_versions if r is not None]

    def describe_recipe(
        self, recipe_name: str, recipe_version: Optional[str] = None
    ) -> "FakeRecipeVersion":
        # https://docs.aws.amazon.com/databrew/latest/dg/API_DescribeRecipe.html
        self.validate_length(recipe_name, "name", 255)

        if recipe_version is None:
            recipe_version = FakeRecipe.LATEST_PUBLISHED
        else:
            self.validate_length(recipe_version, "recipeVersion", 16)
            if not FakeRecipe.version_is_valid(recipe_version):
                raise ValidationException(
                    f"Recipe {recipe_name} version {recipe_version} isn't valid."
                )

        recipe = None
        if recipe_name in self.recipes:
            if recipe_version == FakeRecipe.LATEST_PUBLISHED:
                recipe = self.recipes[recipe_name].latest_published
            elif recipe_version == FakeRecipe.LATEST_WORKING:
                recipe = self.recipes[recipe_name].latest_working
            else:
                recipe = self.recipes[recipe_name].versions.get(float(recipe_version))
        if recipe is None:
            raise ResourceNotFoundException(
                f"The recipe {recipe_name} for version {recipe_version} wasn't found."
            )
        return recipe

    def publish_recipe(
        self, recipe_name: str, description: Optional[str] = None
    ) -> None:
        # https://docs.aws.amazon.com/databrew/latest/dg/API_PublishRecipe.html
        self.validate_length(recipe_name, "name", 255)
        try:
            self.recipes[recipe_name].publish(description)
        except KeyError:
            raise ResourceNotFoundException(f"Recipe {recipe_name} wasn't found")

    def create_ruleset(
        self,
        ruleset_name: str,
        ruleset_description: str,
        ruleset_rules: list[dict[str, Any]],
        ruleset_target_arn: str,
        tags: dict[str, str],
    ) -> "FakeRuleset":
        if ruleset_name in self.rulesets:
            raise RulesetAlreadyExistsException()

        ruleset = FakeRuleset(
            self.region_name,
            ruleset_name,
            ruleset_description,
            ruleset_rules,
            ruleset_target_arn,
            tags,
        )
        self.rulesets[ruleset_name] = ruleset
        return ruleset

    def update_ruleset(
        self,
        ruleset_name: str,
        ruleset_description: str,
        ruleset_rules: list[dict[str, Any]],
        tags: dict[str, str],
    ) -> "FakeRuleset":
        if ruleset_name not in self.rulesets:
            raise RulesetNotFoundException(ruleset_name)

        ruleset = self.rulesets[ruleset_name]
        if ruleset_description is not None:
            ruleset.description = ruleset_description
        if ruleset_rules is not None:
            ruleset.rules = ruleset_rules
        if tags is not None:
            ruleset.tags = tags

        return ruleset

    def describe_ruleset(self, ruleset_name: str) -> "FakeRuleset":
        if ruleset_name not in self.rulesets:
            raise RulesetNotFoundException(ruleset_name)
        return self.rulesets[ruleset_name]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_rulesets(self) -> list["FakeRuleset"]:
        return list(self.rulesets.values())

    def delete_ruleset(self, ruleset_name: str) -> None:
        if ruleset_name not in self.rulesets:
            raise RulesetNotFoundException(ruleset_name)

        del self.rulesets[ruleset_name]

    def create_dataset(
        self,
        dataset_name: str,
        dataset_format: str,
        dataset_format_options: dict[str, Any],
        dataset_input: dict[str, Any],
        dataset_path_options: dict[str, Any],
        tags: dict[str, str],
    ) -> "FakeDataset":
        if dataset_name in self.datasets:
            raise AlreadyExistsException(dataset_name)

        dataset = FakeDataset(
            self.region_name,
            self.account_id,
            dataset_name,
            dataset_format,
            dataset_format_options,
            dataset_input,
            dataset_path_options,
            tags,
        )
        self.datasets[dataset_name] = dataset
        return dataset

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_datasets(self) -> list["FakeDataset"]:
        return list(self.datasets.values())

    def update_dataset(
        self,
        dataset_name: str,
        dataset_format: str,
        dataset_format_options: dict[str, Any],
        dataset_input: dict[str, Any],
        dataset_path_options: dict[str, Any],
        tags: dict[str, str],
    ) -> "FakeDataset":
        if dataset_name not in self.datasets:
            raise ResourceNotFoundException("One or more resources can't be found.")

        dataset = self.datasets[dataset_name]

        if dataset_format is not None:
            dataset.format = dataset_format
        if dataset_format_options is not None:
            dataset.format_options = dataset_format_options
        if dataset_input is not None:
            dataset.input = dataset_input
        if dataset_path_options is not None:
            dataset.path_options = dataset_path_options
        if tags is not None:
            dataset.tags = tags

        return dataset

    def delete_dataset(self, dataset_name: str) -> None:
        if dataset_name not in self.datasets:
            raise ResourceNotFoundException("One or more resources can't be found.")

        del self.datasets[dataset_name]

    def describe_dataset(self, dataset_name: str) -> "FakeDataset":
        if dataset_name not in self.datasets:
            raise ResourceNotFoundException("One or more resources can't be found.")

        return self.datasets[dataset_name]

    def describe_job(self, job_name: str) -> "FakeJob":
        # https://docs.aws.amazon.com/databrew/latest/dg/API_DescribeJob.html
        self.validate_length(job_name, "name", 240)

        if job_name not in self.jobs:
            raise ResourceNotFoundException(f"Job {job_name} wasn't found.")

        return self.jobs[job_name]

    def delete_job(self, job_name: str) -> None:
        # https://docs.aws.amazon.com/databrew/latest/dg/API_DeleteJob.html
        self.validate_length(job_name, "name", 240)

        if job_name not in self.jobs:
            raise ResourceNotFoundException(f"The job {job_name} wasn't found.")

        del self.jobs[job_name]

    def create_profile_job(self, **kwargs: Any) -> "FakeProfileJob":
        # https://docs.aws.amazon.com/databrew/latest/dg/API_CreateProfileJob.html
        job_name = kwargs["name"]
        self.validate_length(job_name, "name", 240)

        if job_name in self.jobs:
            raise ConflictException(
                f"The job {job_name} {self.jobs[job_name].job_type.lower()} job already exists."
            )

        job = FakeProfileJob(
            account_id=self.account_id, region_name=self.region_name, **kwargs
        )

        self.jobs[job_name] = job
        return job

    def create_recipe_job(self, **kwargs: Any) -> "FakeRecipeJob":
        # https://docs.aws.amazon.com/databrew/latest/dg/API_CreateRecipeJob.html
        job_name = kwargs["name"]
        self.validate_length(job_name, "name", 240)

        if job_name in self.jobs:
            raise ConflictException(
                f"The job {job_name} {self.jobs[job_name].job_type.lower()} job already exists."
            )

        job = FakeRecipeJob(
            account_id=self.account_id, region_name=self.region_name, **kwargs
        )

        self.jobs[job_name] = job
        return job

    def update_job(self, **kwargs: Any) -> "FakeJob":
        job_name = kwargs["name"]
        self.validate_length(job_name, "name", 240)

        if job_name not in self.jobs:
            raise ResourceNotFoundException(f"The job {job_name} wasn't found")

        job = self.jobs[job_name]

        for param, value in kwargs.items():
            setattr(job, param, value)
        return job

    def update_recipe_job(self, **kwargs: Any) -> "FakeJob":
        # https://docs.aws.amazon.com/databrew/latest/dg/API_UpdateRecipeJob.html
        return self.update_job(**kwargs)

    def update_profile_job(self, **kwargs: Any) -> "FakeJob":
        # https://docs.aws.amazon.com/databrew/latest/dg/API_UpdateProfileJob.html
        return self.update_job(**kwargs)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_jobs(
        self, dataset_name: Optional[str] = None, project_name: Optional[str] = None
    ) -> list["FakeJob"]:
        # https://docs.aws.amazon.com/databrew/latest/dg/API_ListJobs.html
        if dataset_name is not None:
            self.validate_length(dataset_name, "datasetName", 255)
        if project_name is not None:
            self.validate_length(project_name, "projectName", 255)

        def filter_jobs(job: FakeJob) -> bool:
            if dataset_name is not None and job.dataset_name != dataset_name:
                return False
            if (
                project_name is not None
                and getattr(job, "project_name", None) != project_name
            ):
                return False
            return True

        return list(filter(filter_jobs, self.jobs.values()))

    def create_project(
        self,
        project_name: str,
        dataset_name: str,
        recipe_name: str,
        role_arn: str,
        sample: dict[str, Any] | None,
        tags: dict[str, str] | None,
    ) -> "FakeProject":
        if project_name in self.projects:
            raise ConflictException(f"The project {project_name} already exists.")

        project = FakeProject(
            self.region_name,
            self.account_id,
            project_name,
            dataset_name,
            recipe_name,
            role_arn,
            sample,
            tags or {},
        )
        self.projects[project_name] = project
        return project

    def describe_project(self, project_name: str) -> "FakeProject":
        if project_name not in self.projects:
            raise ResourceNotFoundException("One or more resources can't be found.")
        return self.projects[project_name]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_projects(self) -> list["FakeProject"]:
        return list(self.projects.values())

    def update_project(
        self,
        project_name: str,
        role_arn: str | None,
        sample: dict[str, Any] | None,
    ) -> "FakeProject":
        if project_name not in self.projects:
            raise ResourceNotFoundException("One or more resources can't be found.")
        project = self.projects[project_name]
        if role_arn is not None:
            project.role_arn = role_arn
        if sample is not None:
            project.sample = sample
        project.last_modified_date = utcnow()
        return project

    def delete_project(self, project_name: str) -> None:
        if project_name not in self.projects:
            raise ResourceNotFoundException("One or more resources can't be found.")
        del self.projects[project_name]

    def create_schedule(
        self,
        schedule_name: str,
        cron_expression: str,
        job_names: list[str] | None,
        tags: dict[str, str] | None,
    ) -> "FakeSchedule":
        if schedule_name in self.schedules:
            raise ConflictException(f"The schedule {schedule_name} already exists.")

        schedule = FakeSchedule(
            self.region_name,
            self.account_id,
            schedule_name,
            cron_expression,
            job_names or [],
            tags or {},
        )
        self.schedules[schedule_name] = schedule
        return schedule

    def describe_schedule(self, schedule_name: str) -> "FakeSchedule":
        if schedule_name not in self.schedules:
            raise ResourceNotFoundException("One or more resources can't be found.")
        return self.schedules[schedule_name]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_schedules(self) -> list["FakeSchedule"]:
        return list(self.schedules.values())

    def update_schedule(
        self,
        schedule_name: str,
        cron_expression: str | None,
        job_names: list[str] | None,
    ) -> "FakeSchedule":
        if schedule_name not in self.schedules:
            raise ResourceNotFoundException("One or more resources can't be found.")
        schedule = self.schedules[schedule_name]
        if cron_expression is not None:
            schedule.cron_expression = cron_expression
        if job_names is not None:
            schedule.job_names = job_names
        schedule.last_modified_date = utcnow()
        return schedule

    def delete_schedule(self, schedule_name: str) -> None:
        if schedule_name not in self.schedules:
            raise ResourceNotFoundException("One or more resources can't be found.")
        del self.schedules[schedule_name]

    def _find_resource_by_arn(self, resource_arn: str) -> Any:
        """Find any DataBrew resource by its ARN."""
        # ARN format: arn:aws:databrew:{region}:{account}:{type}/{name}
        # Extract the resource type and name from the ARN
        try:
            resource_part = resource_arn.split(":", 5)[5]  # e.g. "dataset/my-ds"
            resource_type, resource_name = resource_part.split("/", 1)
        except (IndexError, ValueError):
            return None

        store_map = {
            "dataset": self.datasets,
            "job": self.jobs,
            "recipe": self.recipes,
            "ruleset": self.rulesets,
            "project": self.projects,
            "schedule": self.schedules,
        }
        store = store_map.get(resource_type)
        if store is None:
            return None
        return store.get(resource_name)

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        resource = self._find_resource_by_arn(resource_arn)
        if resource is None:
            raise ResourceNotFoundException(
                f"The resource with ARN {resource_arn} wasn't found."
            )
        if resource.tags is None:
            resource.tags = {}
        resource.tags.update(tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        resource = self._find_resource_by_arn(resource_arn)
        if resource is None:
            raise ResourceNotFoundException(
                f"The resource with ARN {resource_arn} wasn't found."
            )
        if resource.tags:
            for key in tag_keys:
                resource.tags.pop(key, None)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        resource = self._find_resource_by_arn(resource_arn)
        if resource is None:
            raise ResourceNotFoundException(
                f"The resource with ARN {resource_arn} wasn't found."
            )
        return resource.tags or {}

    def start_job_run(self, job_name: str) -> str:
        if job_name not in self.jobs:
            raise ResourceNotFoundException(f"Job {job_name} wasn't found.")
        run_id = str(uuid.uuid4())
        run = {
            "RunId": run_id,
            "JobName": job_name,
            "State": "RUNNING",
            "StartedOn": utcnow().timestamp(),
        }
        self.jobs[job_name]._job_runs = getattr(self.jobs[job_name], "_job_runs", {})
        self.jobs[job_name]._job_runs[run_id] = run
        return run_id

    def stop_job_run(self, job_name: str, run_id: str) -> str:
        if job_name not in self.jobs:
            raise ResourceNotFoundException(f"Job {job_name} wasn't found.")
        job = self.jobs[job_name]
        runs = getattr(job, "_job_runs", {})
        if run_id not in runs:
            raise ResourceNotFoundException(f"Job run {run_id} wasn't found.")
        runs[run_id]["State"] = "STOPPED"
        return run_id

    def list_job_runs(self, job_name: str) -> list[dict[str, Any]]:
        if job_name not in self.jobs:
            raise ResourceNotFoundException(f"Job {job_name} wasn't found.")
        job = self.jobs[job_name]
        runs = getattr(job, "_job_runs", {})
        return list(runs.values())

    def describe_job_run(self, job_name: str, run_id: str) -> dict[str, Any]:
        if job_name not in self.jobs:
            raise ResourceNotFoundException(f"Job {job_name} wasn't found.")
        job = self.jobs[job_name]
        runs = getattr(job, "_job_runs", {})
        if run_id not in runs:
            raise ResourceNotFoundException(f"Job run {run_id} wasn't found.")
        return runs[run_id]

    def batch_delete_recipe_version(
        self, recipe_name: str, recipe_versions: list[str]
    ) -> list[dict[str, Any]]:
        if recipe_name not in self.recipes:
            raise ResourceNotFoundException(f"The recipe {recipe_name} wasn't found")
        errors = []
        for version in recipe_versions:
            try:
                self.delete_recipe_version(recipe_name, version)
            except ResourceNotFoundException:
                errors.append(
                    {
                        "RecipeName": recipe_name,
                        "RecipeVersion": version,
                        "ErrorCode": "ResourceNotFoundException",
                        "Message": f"Recipe version {version} wasn't found.",
                    }
                )
            except ValidationException as e:
                errors.append(
                    {
                        "RecipeName": recipe_name,
                        "RecipeVersion": version,
                        "ErrorCode": "ValidationException",
                        "Message": str(e),
                    }
                )
        return errors

    def start_project_session(self, project_name: str) -> tuple[str, bool]:
        if project_name not in self.projects:
            raise ResourceNotFoundException("One or more resources can't be found.")
        project = self.projects[project_name]
        client_session_id = str(uuid.uuid4())
        project._session_id = client_session_id
        project._session_status = "ASSIGNED"
        return project_name, client_session_id

    def send_project_session_action(
        self, project_name: str, **kwargs: Any
    ) -> dict[str, Any]:
        if project_name not in self.projects:
            raise ResourceNotFoundException("One or more resources can't be found.")
        return {
            "Name": project_name,
            "ActionId": 0,
            "Result": "{}",
        }


class FakeRecipe(BaseModel):
    INITIAL_VERSION = 0.1
    LATEST_WORKING = "LATEST_WORKING"
    LATEST_PUBLISHED = "LATEST_PUBLISHED"

    @classmethod
    def version_is_valid(
        cls, version: str, latest_working: bool = True, latest_published: bool = True
    ) -> bool:
        validity = True

        if len(version) < 1 or len(version) > 16:
            validity = False
        else:
            try:
                float(version)
            except ValueError:
                if not (
                    (version == cls.LATEST_WORKING and latest_working)
                    or (version == cls.LATEST_PUBLISHED and latest_published)
                ):
                    validity = False
        return validity

    def __init__(
        self,
        region_name: str,
        recipe_name: str,
        recipe_description: str,
        recipe_steps: list[dict[str, Any]],
        tags: dict[str, str],
    ):
        self.versions: dict[float, FakeRecipeVersion] = OrderedDict()
        self.versions[self.INITIAL_VERSION] = FakeRecipeVersion(
            region_name,
            recipe_name,
            recipe_description,
            recipe_steps,
            tags,
            version=self.INITIAL_VERSION,
        )
        self.latest_working = self.versions[self.INITIAL_VERSION]
        self.latest_published: Optional[FakeRecipeVersion] = None

    def publish(self, description: Optional[str] = None) -> None:
        self.latest_published = self.latest_working
        self.latest_working = deepcopy(self.latest_working)
        self.latest_published.publish(description)
        del self.versions[self.latest_working.version]
        self.versions[self.latest_published.version] = self.latest_published
        self.latest_working.version = self.latest_published.version + 0.1

        if self.latest_published.published_date:
            self.latest_working.created_time = self.latest_published.published_date
        self.versions[self.latest_working.version] = self.latest_working

    def update(
        self, description: Optional[str], steps: Optional[list[dict[str, Any]]]
    ) -> None:
        if description is not None:
            self.latest_working.description = description
        if steps is not None:
            self.latest_working.steps = steps

    def delete_published_version(self, version: str) -> None:
        float_version = float(version)
        assert float_version.is_integer()
        if float_version == self.latest_published.version:  # type: ignore[union-attr]
            prev_version = float_version - 1.0
            # Iterate back through the published versions until we find one that exists
            while prev_version >= 1.0:
                if prev_version in self.versions:
                    self.latest_published = self.versions[prev_version]
                    break
                prev_version -= 1.0
            else:
                # Didn't find an earlier published version
                self.latest_published = None
        del self.versions[float_version]


class FakeRecipeVersion(BaseModel):
    def __init__(
        self,
        region_name: str,
        recipe_name: str,
        recipe_description: str,
        recipe_steps: list[dict[str, Any]],
        tags: dict[str, str],
        version: float,
    ):
        self.region_name = region_name
        self.name = recipe_name
        self.description = recipe_description
        self.steps = recipe_steps
        self.created_time = datetime.now()
        self.tags = tags
        self.published_date: Optional[datetime] = None
        self.version = version

    def as_dict(self) -> dict[str, Any]:
        dict_recipe = {
            "Name": self.name,
            "Steps": self.steps,
            "Description": self.description,
            "CreateDate": f"{self.created_time.timestamp():.3f}",
            "Tags": self.tags or {},
            "RecipeVersion": str(self.version),
        }
        if self.published_date is not None:
            dict_recipe["PublishedDate"] = f"{self.published_date.timestamp():.3f}"

        return dict_recipe

    def publish(self, description: Optional[str]) -> None:
        self.version = float(math.ceil(self.version))
        self.published_date = utcnow()
        if description is not None:
            self.description = description


class FakeRuleset(BaseModel):
    def __init__(
        self,
        region_name: str,
        ruleset_name: str,
        ruleset_description: str,
        ruleset_rules: list[dict[str, Any]],
        ruleset_target_arn: str,
        tags: dict[str, str],
    ):
        self.region_name = region_name
        self.name = ruleset_name
        self.description = ruleset_description
        self.rules = ruleset_rules
        self.target_arn = ruleset_target_arn
        self.created_time = datetime.now()

        self.tags = tags

    def as_dict(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Rules": self.rules,
            "Description": self.description,
            "TargetArn": self.target_arn,
            "CreateDate": f"{self.created_time.timestamp():.3f}",
            "Tags": self.tags or {},
        }


class FakeDataset(BaseModel):
    def __init__(
        self,
        region_name: str,
        account_id: str,
        dataset_name: str,
        dataset_format: str,
        dataset_format_options: dict[str, Any],
        dataset_input: dict[str, Any],
        dataset_path_options: dict[str, Any],
        tags: dict[str, str],
    ):
        self.region_name = region_name
        self.account_id = account_id
        self.name = dataset_name
        self.format = dataset_format
        self.format_options = dataset_format_options
        self.input = dataset_input
        self.path_options = dataset_path_options
        self.created_time = datetime.now()
        self.tags = tags

    @property
    def resource_arn(self) -> str:
        return f"arn:{get_partition(self.region_name)}:databrew:{self.region_name}:{self.account_id}:dataset/{self.name}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Format": self.format,
            "FormatOptions": self.format_options,
            "Input": self.input,
            "PathOptions": self.path_options,
            "CreateDate": f"{self.created_time.timestamp():.3f}",
            "Tags": self.tags or {},
            "ResourceArn": self.resource_arn,
        }


class FakeProject(BaseModel):
    def __init__(
        self,
        region_name: str,
        account_id: str,
        project_name: str,
        dataset_name: str,
        recipe_name: str,
        role_arn: str,
        sample: dict[str, Any] | None,
        tags: dict[str, str],
    ):
        self.region_name = region_name
        self.account_id = account_id
        self.name = project_name
        self.dataset_name = dataset_name
        self.recipe_name = recipe_name
        self.role_arn = role_arn
        self.sample = sample or {}
        self.tags = tags
        self.create_date = utcnow()
        self.last_modified_date = utcnow()

    @property
    def resource_arn(self) -> str:
        return f"arn:{get_partition(self.region_name)}:databrew:{self.region_name}:{self.account_id}:project/{self.name}"

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "Name": self.name,
            "DatasetName": self.dataset_name,
            "RecipeName": self.recipe_name,
            "RoleArn": self.role_arn,
            "CreateDate": self.create_date.timestamp(),
            "LastModifiedDate": self.last_modified_date.timestamp(),
            "Tags": self.tags or {},
            "ResourceArn": self.resource_arn,
        }
        if self.sample:
            result["Sample"] = self.sample
        return result


class FakeSchedule(BaseModel):
    def __init__(
        self,
        region_name: str,
        account_id: str,
        schedule_name: str,
        cron_expression: str,
        job_names: list[str],
        tags: dict[str, str],
    ):
        self.region_name = region_name
        self.account_id = account_id
        self.name = schedule_name
        self.cron_expression = cron_expression
        self.job_names = job_names
        self.tags = tags
        self.create_date = utcnow()
        self.last_modified_date = utcnow()

    @property
    def resource_arn(self) -> str:
        return f"arn:{get_partition(self.region_name)}:databrew:{self.region_name}:{self.account_id}:schedule/{self.name}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "CronExpression": self.cron_expression,
            "JobNames": self.job_names,
            "Tags": self.tags or {},
            "CreateDate": self.create_date.timestamp(),
            "LastModifiedDate": self.last_modified_date.timestamp(),
            "ResourceArn": self.resource_arn,
        }


class JobMetaclass(ABCMeta, InstanceTrackerMeta):
    pass


class FakeJob(BaseModel, metaclass=JobMetaclass):
    ENCRYPTION_MODES = ("SSE-S3", "SSE-KMS")
    LOG_SUBSCRIPTION_VALUES = ("ENABLE", "DISABLE")

    @property
    @abstractmethod
    def local_attrs(self) -> list[str]:
        raise NotImplementedError

    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.account_id = account_id
        self.region_name = region_name
        self.name = kwargs.get("name")
        self.created_time = datetime.now()
        self.dataset_name = kwargs.get("dataset_name")
        self.encryption_mode = kwargs.get("encryption_mode")
        self.log_subscription = kwargs.get("log_subscription")
        self.max_capacity = kwargs.get("max_capacity")
        self.max_retries = kwargs.get("max_retries")
        self.role_arn = kwargs.get("role_arn")
        self.tags = kwargs.get("tags")
        self.validate()
        # Set attributes specific to subclass
        for k in self.local_attrs:
            setattr(self, k, kwargs.get(k))

    def validate(self) -> None:
        if self.encryption_mode is not None:
            if self.encryption_mode not in FakeJob.ENCRYPTION_MODES:
                raise ValidationException(
                    f"1 validation error detected: Value '{self.encryption_mode}' at 'encryptionMode' failed to satisfy constraint: Member must satisfy enum value set: [{', '.join(self.ENCRYPTION_MODES)}]"
                )
        if self.log_subscription is not None:
            if self.log_subscription not in FakeJob.LOG_SUBSCRIPTION_VALUES:
                raise ValidationException(
                    f"1 validation error detected: Value '{self.log_subscription}' at 'logSubscription' failed to satisfy constraint: Member must satisfy enum value set: [{', '.join(self.LOG_SUBSCRIPTION_VALUES)}]"
                )

    @property
    @abstractmethod
    def job_type(self) -> str:
        pass

    @property
    def resource_arn(self) -> str:
        return f"arn:{get_partition(self.region_name)}:databrew:{self.region_name}:{self.account_id}:job/{self.name}"

    def as_dict(self) -> dict[str, Any]:
        rtn_dict = {
            "Name": self.name,
            "AccountId": self.account_id,
            "CreateDate": f"{self.created_time.timestamp():.3f}",
            "DatasetName": self.dataset_name,
            "EncryptionMode": self.encryption_mode,
            "Tags": self.tags or {},
            "LogSubscription": self.log_subscription,
            "MaxCapacity": self.max_capacity,
            "MaxRetries": self.max_retries,
            "ResourceArn": self.resource_arn,
            "RoleArn": self.role_arn,
            "Type": self.job_type,
        }

        # Add in subclass attributes
        for k in self.local_attrs:
            rtn_dict[camelcase_to_pascal(underscores_to_camelcase(k))] = getattr(
                self, k
            )

        # Remove items that have a value of None
        rtn_dict = {k: v for k, v in rtn_dict.items() if v is not None}

        return rtn_dict


class FakeProfileJob(FakeJob):
    job_type = "PROFILE"
    local_attrs = ["output_location", "configuration", "validation_configurations"]


class FakeRecipeJob(FakeJob):
    local_attrs = [
        "database_outputs",
        "data_catalog_outputs",
        "outputs",
        "project_name",
        "recipe_reference",
    ]
    job_type = "RECIPE"


databrew_backends = BackendDict(DataBrewBackend, "databrew")
