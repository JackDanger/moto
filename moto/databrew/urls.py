from .responses import DataBrewResponse

url_bases = [r"https?://databrew\.(.+)\.amazonaws.com"]

url_paths = {
    "{0}/recipeVersions$": DataBrewResponse.dispatch,
    "{0}/recipes$": DataBrewResponse.dispatch,
    "{0}/recipes/(?P<recipe_name>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/recipes/(?P<recipe_name>[^/]+)/recipeVersion/(?P<recipe_version>[^/]+)": DataBrewResponse.dispatch,
    "{0}/recipes/(?P<recipe_name>[^/]+)/publishRecipe$": DataBrewResponse.dispatch,
    "{0}/rulesets$": DataBrewResponse.dispatch,
    "{0}/rulesets/(?P<ruleset_name>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/datasets$": DataBrewResponse.dispatch,
    "{0}/datasets/(?P<dataset_name>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/projects$": DataBrewResponse.dispatch,
    "{0}/projects/(?P<project_name>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/schedules$": DataBrewResponse.dispatch,
    "{0}/schedules/(?P<schedule_name>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/jobs$": DataBrewResponse.dispatch,
    "{0}/jobs/(?P<job_name>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/profileJobs$": DataBrewResponse.dispatch,
    "{0}/recipeJobs$": DataBrewResponse.dispatch,
    "{0}/profileJobs/(?P<job_name>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/recipeJobs/(?P<job_name>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/tags/(?P<resource_arn>.+)$": DataBrewResponse.dispatch,
    "{0}/jobs/(?P<job_name>[^/]+)/jobRuns$": DataBrewResponse.dispatch,
    "{0}/jobs/(?P<job_name>[^/]+)/jobRun/(?P<run_id>[^/]+)/stopJobRun$": DataBrewResponse.dispatch,
    "{0}/jobs/(?P<job_name>[^/]+)/jobRun/(?P<run_id>[^/]+)$": DataBrewResponse.dispatch,
    "{0}/jobs/(?P<job_name>[^/]+)/startJobRun$": DataBrewResponse.dispatch,
    "{0}/recipes/(?P<recipe_name>[^/]+)/batchDeleteRecipeVersion$": DataBrewResponse.dispatch,
    "{0}/projects/(?P<project_name>[^/]+)/startProjectSession$": DataBrewResponse.dispatch,
    "{0}/projects/(?P<project_name>[^/]+)/sendProjectSessionAction$": DataBrewResponse.dispatch,
}
