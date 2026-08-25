import base64
import json
import re

from moto.core.responses import BaseResponse

from .exceptions import InvalidRepositoryNameException
from .models import CodeCommitBackend, codecommit_backends


def _is_repository_name_valid(repository_name: str) -> bool:
    name_regex = re.compile(r"[\w\.-]+")
    result = name_regex.split(repository_name)
    if len(result) > 0:
        for match in result:
            if len(match) > 0:
                return False
    return True


class CodeCommitResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="codecommit")

    @property
    def codecommit_backend(self) -> CodeCommitBackend:
        return codecommit_backends[self.current_account][self.region]

    # ── Repository operations ──

    def create_repository(self) -> str:
        if not _is_repository_name_valid(self._get_param("repositoryName")):
            raise InvalidRepositoryNameException()

        repository_metadata = self.codecommit_backend.create_repository(
            self._get_param("repositoryName"),
            self._get_param("repositoryDescription"),
            tags=self._get_param("tags"),
            kms_key_id=self._get_param("kmsKeyId"),
        )

        return json.dumps({"repositoryMetadata": repository_metadata})

    def get_repository(self) -> str:
        if not _is_repository_name_valid(self._get_param("repositoryName")):
            raise InvalidRepositoryNameException()

        repository_metadata = self.codecommit_backend.get_repository(
            self._get_param("repositoryName")
        )

        return json.dumps({"repositoryMetadata": repository_metadata})

    def delete_repository(self) -> str:
        if not _is_repository_name_valid(self._get_param("repositoryName")):
            raise InvalidRepositoryNameException()

        repository_id = self.codecommit_backend.delete_repository(
            self._get_param("repositoryName")
        )

        if repository_id:
            return json.dumps({"repositoryId": repository_id})

        return json.dumps({})

    def batch_get_repositories(self) -> str:
        repository_names = self._get_param("repositoryNames", [])
        repositories, not_found = self.codecommit_backend.batch_get_repositories(
            repository_names
        )
        return json.dumps(
            {"repositories": repositories, "repositoriesNotFound": not_found}
        )

    def list_repositories(self) -> str:
        sort_by = self._get_param("sortBy", "repositoryName")
        order = self._get_param("order", "ascending")
        next_token = self._get_param("nextToken")
        repos, token = self.codecommit_backend.list_repositories(
            sort_by, order, next_token
        )
        result: dict = {"repositories": repos}
        if token:
            result["nextToken"] = token
        return json.dumps(result)

    def update_repository_description(self) -> str:
        self.codecommit_backend.update_repository_description(
            self._get_param("repositoryName"),
            self._get_param("repositoryDescription"),
        )
        return json.dumps({})

    def update_repository_name(self) -> str:
        self.codecommit_backend.update_repository_name(
            self._get_param("oldName"),
            self._get_param("newName"),
        )
        return json.dumps({})

    def update_repository_encryption_key(self) -> str:
        result = self.codecommit_backend.update_repository_encryption_key(
            self._get_param("repositoryName"),
            self._get_param("kmsKeyId"),
        )
        return json.dumps(result)

    # ── Branch operations ──

    def create_branch(self) -> str:
        self.codecommit_backend.create_branch(
            self._get_param("repositoryName"),
            self._get_param("branchName"),
            self._get_param("commitId"),
        )
        return json.dumps({})

    def get_branch(self) -> str:
        branch = self.codecommit_backend.get_branch(
            self._get_param("repositoryName"),
            self._get_param("branchName"),
        )
        return json.dumps({"branch": branch})

    def delete_branch(self) -> str:
        branch = self.codecommit_backend.delete_branch(
            self._get_param("repositoryName"),
            self._get_param("branchName"),
        )
        return json.dumps({"deletedBranch": branch})

    def list_branches(self) -> str:
        branches, next_token = self.codecommit_backend.list_branches(
            self._get_param("repositoryName"),
            self._get_param("nextToken"),
        )
        result: dict = {"branches": branches}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    def update_default_branch(self) -> str:
        self.codecommit_backend.update_default_branch(
            self._get_param("repositoryName"),
            self._get_param("defaultBranchName"),
        )
        return json.dumps({})

    # ── Commit operations ──

    def create_commit(self) -> str:
        result = self.codecommit_backend.create_commit(
            repository_name=self._get_param("repositoryName"),
            branch_name=self._get_param("branchName"),
            parent_commit_id=self._get_param("parentCommitId"),
            author_name=self._get_param("authorName"),
            email=self._get_param("email"),
            commit_message=self._get_param("commitMessage", ""),
            put_files=self._get_param("putFiles"),
            delete_files=self._get_param("deleteFiles"),
            set_file_modes=self._get_param("setFileModes"),
        )
        return json.dumps(result)

    def get_commit(self) -> str:
        commit = self.codecommit_backend.get_commit(
            self._get_param("repositoryName"),
            self._get_param("commitId"),
        )
        return json.dumps({"commit": commit})

    def batch_get_commits(self) -> str:
        commits, errors = self.codecommit_backend.batch_get_commits(
            self._get_param("repositoryName"),
            self._get_param("commitIds", []),
        )
        return json.dumps({"commits": commits, "errors": errors})

    # ── File/Tree operations ──

    def get_file(self) -> str:
        result = self.codecommit_backend.get_file(
            self._get_param("repositoryName"),
            self._get_param("commitSpecifier"),
            self._get_param("filePath"),
        )
        return json.dumps(result)

    def get_folder(self) -> str:
        result = self.codecommit_backend.get_folder(
            self._get_param("repositoryName"),
            self._get_param("commitSpecifier"),
            self._get_param("folderPath"),
        )
        return json.dumps(result)

    def get_blob(self) -> str:
        result = self.codecommit_backend.get_blob(
            self._get_param("repositoryName"),
            self._get_param("blobId"),
        )
        return json.dumps(result)

    def put_file(self) -> str:
        file_content_b64 = self._get_param("fileContent", "")
        if file_content_b64:
            file_content = base64.b64decode(file_content_b64)
        else:
            file_content = b""
        result = self.codecommit_backend.put_file(
            repository_name=self._get_param("repositoryName"),
            branch_name=self._get_param("branchName"),
            file_content=file_content,
            file_path=self._get_param("filePath"),
            file_mode=self._get_param("fileMode", "NORMAL"),
            parent_commit_id=self._get_param("parentCommitId"),
            commit_message=self._get_param("commitMessage"),
            name=self._get_param("name"),
            email=self._get_param("email"),
        )
        return json.dumps(result)

    def delete_file(self) -> str:
        result = self.codecommit_backend.delete_file(
            repository_name=self._get_param("repositoryName"),
            branch_name=self._get_param("branchName"),
            file_path=self._get_param("filePath"),
            parent_commit_id=self._get_param("parentCommitId", ""),
            keep_empty_folders=self._get_param("keepEmptyFolders", False),
            commit_message=self._get_param("commitMessage"),
            name=self._get_param("name"),
            email=self._get_param("email"),
        )
        return json.dumps(result)

    def get_differences(self) -> str:
        differences, next_token = self.codecommit_backend.get_differences(
            repository_name=self._get_param("repositoryName"),
            before_commit_specifier=self._get_param("beforeCommitSpecifier"),
            after_commit_specifier=self._get_param("afterCommitSpecifier"),
            before_path=self._get_param("beforePath"),
            after_path=self._get_param("afterPath"),
            max_results=self._get_param("MaxResults"),
            next_token=self._get_param("NextToken"),
        )
        result: dict = {"differences": differences}
        if next_token:
            result["NextToken"] = next_token
        return json.dumps(result)

    def list_file_commit_history(self) -> str:
        revision_diffs, next_token = self.codecommit_backend.list_file_commit_history(
            repository_name=self._get_param("repositoryName"),
            commit_specifier=self._get_param("commitSpecifier"),
            file_path=self._get_param("filePath"),
            max_results=self._get_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )
        result: dict = {"revisionDag": revision_diffs}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    # ── Pull Request operations ──

    def create_pull_request(self) -> str:
        pr = self.codecommit_backend.create_pull_request(
            title=self._get_param("title"),
            description=self._get_param("description", ""),
            targets=self._get_param("targets", []),
        )
        return json.dumps({"pullRequest": pr})

    def get_pull_request(self) -> str:
        pr = self.codecommit_backend.get_pull_request(
            self._get_param("pullRequestId"),
        )
        return json.dumps({"pullRequest": pr})

    def list_pull_requests(self) -> str:
        pr_ids, next_token = self.codecommit_backend.list_pull_requests(
            repository_name=self._get_param("repositoryName"),
            author_arn=self._get_param("authorArn"),
            pull_request_status=self._get_param("pullRequestStatus"),
            next_token=self._get_param("nextToken"),
            max_results=self._get_param("maxResults"),
        )
        result: dict = {"pullRequestIds": pr_ids}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    def update_pull_request_title(self) -> str:
        pr = self.codecommit_backend.update_pull_request_title(
            self._get_param("pullRequestId"),
            self._get_param("title"),
        )
        return json.dumps({"pullRequest": pr})

    def update_pull_request_description(self) -> str:
        pr = self.codecommit_backend.update_pull_request_description(
            self._get_param("pullRequestId"),
            self._get_param("description"),
        )
        return json.dumps({"pullRequest": pr})

    def update_pull_request_status(self) -> str:
        pr = self.codecommit_backend.update_pull_request_status(
            self._get_param("pullRequestId"),
            self._get_param("pullRequestStatus"),
        )
        return json.dumps({"pullRequest": pr})

    def describe_pull_request_events(self) -> str:
        events, next_token = self.codecommit_backend.describe_pull_request_events(
            pull_request_id=self._get_param("pullRequestId"),
            pull_request_event_type=self._get_param("pullRequestEventType"),
            actor_arn=self._get_param("actorArn"),
            next_token=self._get_param("nextToken"),
            max_results=self._get_param("maxResults"),
        )
        result: dict = {"pullRequestEvents": events}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    # ── Merge operations ──

    def merge_branches_by_fast_forward(self) -> str:
        result = self.codecommit_backend.merge_branches_by_fast_forward(
            repository_name=self._get_param("repositoryName"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            target_branch=self._get_param("targetBranch"),
        )
        return json.dumps(result)

    def merge_branches_by_squash(self) -> str:
        result = self.codecommit_backend.merge_branches_by_squash(
            repository_name=self._get_param("repositoryName"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            target_branch=self._get_param("targetBranch"),
            commit_message=self._get_param("commitMessage"),
            author_name=self._get_param("authorName"),
            email=self._get_param("email"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
            conflict_resolution=self._get_param("conflictResolution"),
            keep_empty_folders=self._get_param("keepEmptyFolders", False),
        )
        return json.dumps(result)

    def merge_branches_by_three_way(self) -> str:
        result = self.codecommit_backend.merge_branches_by_three_way(
            repository_name=self._get_param("repositoryName"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            target_branch=self._get_param("targetBranch"),
            commit_message=self._get_param("commitMessage"),
            author_name=self._get_param("authorName"),
            email=self._get_param("email"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
            conflict_resolution=self._get_param("conflictResolution"),
            keep_empty_folders=self._get_param("keepEmptyFolders", False),
        )
        return json.dumps(result)

    def merge_pull_request_by_fast_forward(self) -> str:
        pr = self.codecommit_backend.merge_pull_request_by_fast_forward(
            pull_request_id=self._get_param("pullRequestId"),
            repository_name=self._get_param("repositoryName"),
            source_commit_id=self._get_param("sourceCommitId"),
        )
        return json.dumps({"pullRequest": pr})

    def merge_pull_request_by_squash(self) -> str:
        pr = self.codecommit_backend.merge_pull_request_by_squash(
            pull_request_id=self._get_param("pullRequestId"),
            repository_name=self._get_param("repositoryName"),
            source_commit_id=self._get_param("sourceCommitId"),
            commit_message=self._get_param("commitMessage"),
            author_name=self._get_param("authorName"),
            email=self._get_param("email"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
            conflict_resolution=self._get_param("conflictResolution"),
            keep_empty_folders=self._get_param("keepEmptyFolders", False),
        )
        return json.dumps({"pullRequest": pr})

    def merge_pull_request_by_three_way(self) -> str:
        pr = self.codecommit_backend.merge_pull_request_by_three_way(
            pull_request_id=self._get_param("pullRequestId"),
            repository_name=self._get_param("repositoryName"),
            source_commit_id=self._get_param("sourceCommitId"),
            commit_message=self._get_param("commitMessage"),
            author_name=self._get_param("authorName"),
            email=self._get_param("email"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
            conflict_resolution=self._get_param("conflictResolution"),
            keep_empty_folders=self._get_param("keepEmptyFolders", False),
        )
        return json.dumps({"pullRequest": pr})

    def get_merge_options(self) -> str:
        result = self.codecommit_backend.get_merge_options(
            repository_name=self._get_param("repositoryName"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            conflict_detail_level=self._get_param("conflictDetailLevel"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
        )
        return json.dumps(result)

    def get_merge_commit(self) -> str:
        result = self.codecommit_backend.get_merge_commit(
            repository_name=self._get_param("repositoryName"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            conflict_detail_level=self._get_param("conflictDetailLevel"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
        )
        return json.dumps(result)

    def get_merge_conflicts(self) -> str:
        result = self.codecommit_backend.get_merge_conflicts(
            repository_name=self._get_param("repositoryName"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            merge_option=self._get_param("mergeOption"),
            conflict_detail_level=self._get_param("conflictDetailLevel"),
            max_conflict_files=self._get_param("maxConflictFiles"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
            next_token=self._get_param("nextToken"),
        )
        return json.dumps(result)

    def batch_describe_merge_conflicts(self) -> str:
        result = self.codecommit_backend.batch_describe_merge_conflicts(
            repository_name=self._get_param("repositoryName"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            merge_option=self._get_param("mergeOption"),
            max_merge_hunks=self._get_param("maxMergeHunks"),
            max_conflict_files=self._get_param("maxConflictFiles"),
            file_paths=self._get_param("filePaths"),
            conflict_detail_level=self._get_param("conflictDetailLevel"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
            next_token=self._get_param("nextToken"),
        )
        return json.dumps(result)

    def describe_merge_conflicts(self) -> str:
        result = self.codecommit_backend.describe_merge_conflicts(
            repository_name=self._get_param("repositoryName"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            merge_option=self._get_param("mergeOption"),
            file_path=self._get_param("filePath"),
            max_merge_hunks=self._get_param("maxMergeHunks"),
            conflict_detail_level=self._get_param("conflictDetailLevel"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
            next_token=self._get_param("nextToken"),
        )
        return json.dumps(result)

    def create_unreferenced_merge_commit(self) -> str:
        result = self.codecommit_backend.create_unreferenced_merge_commit(
            repository_name=self._get_param("repositoryName"),
            source_commit_specifier=self._get_param("sourceCommitSpecifier"),
            destination_commit_specifier=self._get_param("destinationCommitSpecifier"),
            merge_option=self._get_param("mergeOption"),
            conflict_detail_level=self._get_param("conflictDetailLevel"),
            conflict_resolution_strategy=self._get_param("conflictResolutionStrategy"),
            author_name=self._get_param("authorName"),
            email=self._get_param("email"),
            commit_message=self._get_param("commitMessage"),
            keep_empty_folders=self._get_param("keepEmptyFolders", False),
            conflict_resolution=self._get_param("conflictResolution"),
        )
        return json.dumps(result)

    # ── Comment operations ──

    def post_comment_for_compared_commit(self) -> str:
        result = self.codecommit_backend.post_comment_for_compared_commit(
            repository_name=self._get_param("repositoryName"),
            before_commit_id=self._get_param("beforeCommitId"),
            after_commit_id=self._get_param("afterCommitId"),
            content=self._get_param("content"),
            location=self._get_param("location"),
        )
        return json.dumps(result)

    def post_comment_for_pull_request(self) -> str:
        result = self.codecommit_backend.post_comment_for_pull_request(
            pull_request_id=self._get_param("pullRequestId"),
            repository_name=self._get_param("repositoryName"),
            before_commit_id=self._get_param("beforeCommitId"),
            after_commit_id=self._get_param("afterCommitId"),
            content=self._get_param("content"),
            location=self._get_param("location"),
        )
        return json.dumps(result)

    def post_comment_reply(self) -> str:
        result = self.codecommit_backend.post_comment_reply(
            in_reply_to=self._get_param("inReplyTo"),
            content=self._get_param("content"),
        )
        return json.dumps(result)

    def get_comment(self) -> str:
        comment = self.codecommit_backend.get_comment(
            self._get_param("commentId"),
        )
        return json.dumps({"comment": comment})

    def update_comment(self) -> str:
        comment = self.codecommit_backend.update_comment(
            self._get_param("commentId"),
            self._get_param("content"),
        )
        return json.dumps({"comment": comment})

    def delete_comment_content(self) -> str:
        comment = self.codecommit_backend.delete_comment_content(
            self._get_param("commentId"),
        )
        return json.dumps({"comment": comment})

    def get_comments_for_compared_commit(self) -> str:
        comments, next_token = self.codecommit_backend.get_comments_for_compared_commit(
            repository_name=self._get_param("repositoryName"),
            before_commit_id=self._get_param("beforeCommitId"),
            after_commit_id=self._get_param("afterCommitId"),
            next_token=self._get_param("nextToken"),
            max_results=self._get_param("maxResults"),
        )
        result: dict = {"commentsForComparedCommitData": comments}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    def get_comments_for_pull_request(self) -> str:
        comments, next_token = self.codecommit_backend.get_comments_for_pull_request(
            pull_request_id=self._get_param("pullRequestId"),
            repository_name=self._get_param("repositoryName"),
            before_commit_id=self._get_param("beforeCommitId"),
            after_commit_id=self._get_param("afterCommitId"),
            next_token=self._get_param("nextToken"),
            max_results=self._get_param("maxResults"),
        )
        result: dict = {"commentsForPullRequestData": comments}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    def put_comment_reaction(self) -> str:
        self.codecommit_backend.put_comment_reaction(
            self._get_param("commentId"),
            self._get_param("reactionValue"),
        )
        return json.dumps({})

    def get_comment_reactions(self) -> str:
        reactions, next_token = self.codecommit_backend.get_comment_reactions(
            comment_id=self._get_param("commentId"),
            reaction_user_arn=self._get_param("reactionUserArn"),
            next_token=self._get_param("nextToken"),
            max_results=self._get_param("maxResults"),
        )
        result: dict = {"reactionsForComment": reactions}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    # ── Approval Rule operations ──

    def create_pull_request_approval_rule(self) -> str:
        rule = self.codecommit_backend.create_pull_request_approval_rule(
            self._get_param("pullRequestId"),
            self._get_param("approvalRuleName"),
            self._get_param("approvalRuleContent"),
        )
        return json.dumps({"approvalRule": rule})

    def delete_pull_request_approval_rule(self) -> str:
        result = self.codecommit_backend.delete_pull_request_approval_rule(
            self._get_param("pullRequestId"),
            self._get_param("approvalRuleName"),
        )
        return json.dumps(result)

    def update_pull_request_approval_rule_content(self) -> str:
        rule = self.codecommit_backend.update_pull_request_approval_rule_content(
            pull_request_id=self._get_param("pullRequestId"),
            approval_rule_name=self._get_param("approvalRuleName"),
            new_rule_content=self._get_param("newRuleContent"),
            existing_rule_content_sha256=self._get_param("existingRuleContentSha256"),
        )
        return json.dumps({"approvalRule": rule})

    def update_pull_request_approval_state(self) -> str:
        self.codecommit_backend.update_pull_request_approval_state(
            self._get_param("pullRequestId"),
            self._get_param("revisionId"),
            self._get_param("approvalState"),
        )
        return json.dumps({})

    def get_pull_request_approval_states(self) -> str:
        approvals = self.codecommit_backend.get_pull_request_approval_states(
            self._get_param("pullRequestId"),
            self._get_param("revisionId"),
        )
        return json.dumps({"approvals": approvals})

    def evaluate_pull_request_approval_rules(self) -> str:
        result = self.codecommit_backend.evaluate_pull_request_approval_rules(
            self._get_param("pullRequestId"),
            self._get_param("revisionId"),
        )
        return json.dumps(result)

    def override_pull_request_approval_rules(self) -> str:
        self.codecommit_backend.override_pull_request_approval_rules(
            self._get_param("pullRequestId"),
            self._get_param("revisionId"),
            self._get_param("overrideStatus"),
        )
        return json.dumps({})

    def get_pull_request_override_state(self) -> str:
        result = self.codecommit_backend.get_pull_request_override_state(
            self._get_param("pullRequestId"),
            self._get_param("revisionId"),
        )
        return json.dumps(result)

    # ── Approval Rule Template operations ──

    def create_approval_rule_template(self) -> str:
        template = self.codecommit_backend.create_approval_rule_template(
            self._get_param("approvalRuleTemplateName"),
            self._get_param("approvalRuleTemplateContent"),
            self._get_param("approvalRuleTemplateDescription", ""),
        )
        return json.dumps({"approvalRuleTemplate": template})

    def get_approval_rule_template(self) -> str:
        template = self.codecommit_backend.get_approval_rule_template(
            self._get_param("approvalRuleTemplateName"),
        )
        return json.dumps({"approvalRuleTemplate": template})

    def delete_approval_rule_template(self) -> str:
        template_id = self.codecommit_backend.delete_approval_rule_template(
            self._get_param("approvalRuleTemplateName"),
        )
        return json.dumps({"approvalRuleTemplateId": template_id})

    def list_approval_rule_templates(self) -> str:
        names, next_token = self.codecommit_backend.list_approval_rule_templates(
            next_token=self._get_param("nextToken"),
            max_results=self._get_param("maxResults"),
        )
        result: dict = {"approvalRuleTemplateNames": names}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    def update_approval_rule_template_name(self) -> str:
        template = self.codecommit_backend.update_approval_rule_template_name(
            self._get_param("oldApprovalRuleTemplateName"),
            self._get_param("newApprovalRuleTemplateName"),
        )
        return json.dumps({"approvalRuleTemplate": template})

    def update_approval_rule_template_content(self) -> str:
        template = self.codecommit_backend.update_approval_rule_template_content(
            self._get_param("approvalRuleTemplateName"),
            self._get_param("newRuleContent"),
            self._get_param("existingRuleContentSha256"),
        )
        return json.dumps({"approvalRuleTemplate": template})

    def update_approval_rule_template_description(self) -> str:
        template = self.codecommit_backend.update_approval_rule_template_description(
            self._get_param("approvalRuleTemplateName"),
            self._get_param("approvalRuleTemplateDescription"),
        )
        return json.dumps({"approvalRuleTemplate": template})

    def associate_approval_rule_template_with_repository(self) -> str:
        self.codecommit_backend.associate_approval_rule_template_with_repository(
            self._get_param("approvalRuleTemplateName"),
            self._get_param("repositoryName"),
        )
        return json.dumps({})

    def disassociate_approval_rule_template_from_repository(self) -> str:
        self.codecommit_backend.disassociate_approval_rule_template_from_repository(
            self._get_param("approvalRuleTemplateName"),
            self._get_param("repositoryName"),
        )
        return json.dumps({})

    def batch_associate_approval_rule_template_with_repositories(self) -> str:
        associated, errors = self.codecommit_backend.batch_associate_approval_rule_template_with_repositories(
            self._get_param("approvalRuleTemplateName"),
            self._get_param("repositoryNames", []),
        )
        return json.dumps(
            {
                "associatedRepositoryNames": associated,
                "errors": errors,
            }
        )

    def batch_disassociate_approval_rule_template_from_repositories(self) -> str:
        disassociated, errors = self.codecommit_backend.batch_disassociate_approval_rule_template_from_repositories(
            self._get_param("approvalRuleTemplateName"),
            self._get_param("repositoryNames", []),
        )
        return json.dumps(
            {
                "disassociatedRepositoryNames": disassociated,
                "errors": errors,
            }
        )

    def list_associated_approval_rule_templates_for_repository(self) -> str:
        names, next_token = self.codecommit_backend.list_associated_approval_rule_templates_for_repository(
            self._get_param("repositoryName"),
            self._get_param("nextToken"),
            self._get_param("maxResults"),
        )
        result: dict = {"approvalRuleTemplateNames": names}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    def list_repositories_for_approval_rule_template(self) -> str:
        names, next_token = self.codecommit_backend.list_repositories_for_approval_rule_template(
            self._get_param("approvalRuleTemplateName"),
            self._get_param("nextToken"),
            self._get_param("maxResults"),
        )
        result: dict = {"repositoryNames": names}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)

    # ── Trigger operations ──

    def get_repository_triggers(self) -> str:
        result = self.codecommit_backend.get_repository_triggers(
            self._get_param("repositoryName"),
        )
        return json.dumps(result)

    def put_repository_triggers(self) -> str:
        config_id = self.codecommit_backend.put_repository_triggers(
            self._get_param("repositoryName"),
            self._get_param("triggers", []),
        )
        return json.dumps({"configurationId": config_id})

    def test_repository_triggers(self) -> str:
        successful, failed = self.codecommit_backend.test_repository_triggers(
            self._get_param("repositoryName"),
            self._get_param("triggers", []),
        )
        return json.dumps(
            {
                "successfulExecutions": successful,
                "failedExecutions": failed,
            }
        )

    # ── Tag operations ──

    def tag_resource(self) -> str:
        self.codecommit_backend.tag_resource(
            self._get_param("resourceArn"),
            self._get_param("tags", {}),
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        self.codecommit_backend.untag_resource(
            self._get_param("resourceArn"),
            self._get_param("tagKeys", []),
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        tags, next_token = self.codecommit_backend.list_tags_for_resource(
            self._get_param("resourceArn"),
            self._get_param("nextToken"),
        )
        result: dict = {"tags": tags}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)
