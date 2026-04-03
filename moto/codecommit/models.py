import base64
import hashlib
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_with_milliseconds
from moto.moto_api._internal import mock_random
from moto.utilities.utils import get_partition

from .exceptions import (
    ApprovalRuleDoesNotExistException,
    ApprovalRuleTemplateDoesNotExistException,
    ApprovalRuleTemplateNameAlreadyExistsException,
    BranchDoesNotExistException,
    BranchNameExistsException,
    CommentDoesNotExistException,
    DefaultBranchCannotBeDeletedException,
    FileDoesNotExistException,
    PullRequestAlreadyClosedException,
    PullRequestDoesNotExistException,
    RepositoryDoesNotExistException,
    RepositoryNameExistsException,
)


class Branch(BaseModel):
    def __init__(self, branch_name: str, commit_id: str):
        self.branch_name = branch_name
        self.commit_id = commit_id

    def to_dict(self) -> dict[str, str]:
        return {
            "branchName": self.branch_name,
            "commitId": self.commit_id,
        }


class Commit(BaseModel):
    def __init__(
        self,
        commit_id: str,
        tree_id: str,
        parents: list[str],
        message: str,
        author_name: str,
        author_email: str,
        committer_name: str,
        committer_email: str,
    ):
        self.commit_id = commit_id
        self.tree_id = tree_id
        self.parents = parents
        self.message = message
        self.author_name = author_name
        self.author_email = author_email
        self.committer_name = committer_name
        self.committer_email = committer_email
        self.author_date = iso_8601_datetime_with_milliseconds()
        self.committer_date = self.author_date
        self.additional_data = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "commitId": self.commit_id,
            "treeId": self.tree_id,
            "parents": self.parents,
            "message": self.message,
            "author": {
                "name": self.author_name,
                "email": self.author_email,
                "date": self.author_date,
            },
            "committer": {
                "name": self.committer_name,
                "email": self.committer_email,
                "date": self.committer_date,
            },
            "additionalData": self.additional_data,
        }


class FileEntry(BaseModel):
    def __init__(self, file_path: str, content: bytes, file_mode: str = "NORMAL"):
        self.file_path = file_path
        self.content = content
        self.file_mode = file_mode
        self.blob_id = hashlib.sha1(content).hexdigest()  # noqa: S324

    def to_dict(self) -> dict[str, Any]:
        return {
            "absolutePath": self.file_path,
            "blobId": self.blob_id,
            "fileMode": self.file_mode,
        }


class Comment(BaseModel):
    def __init__(
        self,
        comment_id: str,
        content: str,
        author_arn: str,
        in_reply_to: Optional[str] = None,
    ):
        self.comment_id = comment_id
        self.content = content
        self.author_arn = author_arn
        self.in_reply_to = in_reply_to
        self.creation_date = iso_8601_datetime_with_milliseconds()
        self.last_modified_date = self.creation_date
        self.deleted = False
        self.caller_reactions: list[str] = []
        self.reaction_counts: dict[str, int] = {}

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "commentId": self.comment_id,
            "content": self.content,
            "authorArn": self.author_arn,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
            "deleted": self.deleted,
            "callerReactions": self.caller_reactions,
            "reactionCounts": self.reaction_counts,
        }
        if self.in_reply_to:
            result["inReplyTo"] = self.in_reply_to
        return result


class ApprovalRule(BaseModel):
    def __init__(
        self,
        approval_rule_id: str,
        approval_rule_name: str,
        approval_rule_content: str,
    ):
        self.approval_rule_id = approval_rule_id
        self.approval_rule_name = approval_rule_name
        self.approval_rule_content = approval_rule_content
        self.creation_date = iso_8601_datetime_with_milliseconds()
        self.last_modified_date = self.creation_date
        self.last_modified_user = ""
        self.origin_approval_rule_template: Optional[dict[str, str]] = None
        self.rule_content_sha256 = hashlib.sha256(
            approval_rule_content.encode()
        ).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "approvalRuleId": self.approval_rule_id,
            "approvalRuleName": self.approval_rule_name,
            "approvalRuleContent": self.approval_rule_content,
            "ruleContentSha256": self.rule_content_sha256,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
            "lastModifiedUser": self.last_modified_user,
        }
        if self.origin_approval_rule_template:
            result["originApprovalRuleTemplate"] = self.origin_approval_rule_template
        return result


class PullRequest(BaseModel):
    def __init__(
        self,
        pull_request_id: str,
        title: str,
        description: str,
        targets: list[dict[str, str]],
        author_arn: str,
    ):
        self.pull_request_id = pull_request_id
        self.title = title
        self.description = description
        self.author_arn = author_arn
        self.pull_request_status = "OPEN"
        self.creation_date = iso_8601_datetime_with_milliseconds()
        self.last_activity_date = self.creation_date
        self.approval_rules: dict[str, ApprovalRule] = {}
        self.pull_request_targets: list[dict[str, str]] = []
        self.events: list[dict[str, Any]] = []
        self.comments: list[Comment] = []
        self.approval_states: list[dict[str, str]] = []
        self.override_status = "REVOKE"
        self.override_user = ""

        for target in targets:
            merge_commit_id = str(mock_random.uuid4()).replace("-", "")[:40]
            pr_target = {
                "repositoryName": target.get("repositoryName", ""),
                "sourceReference": target.get("sourceReference", ""),
                "destinationReference": target.get("destinationReference", "main"),
                "destinationCommit": str(mock_random.uuid4()).replace("-", "")[:40],
                "sourceCommit": str(mock_random.uuid4()).replace("-", "")[:40],
                "mergeBase": merge_commit_id,
                "mergeMetadata": {"isMerged": False},
            }
            self.pull_request_targets.append(pr_target)

        self.events.append(
            {
                "pullRequestId": self.pull_request_id,
                "eventDate": self.creation_date,
                "pullRequestEventType": "PULL_REQUEST_CREATED",
                "actorArn": self.author_arn,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "pullRequestId": self.pull_request_id,
            "title": self.title,
            "description": self.description,
            "pullRequestStatus": self.pull_request_status,
            "creationDate": self.creation_date,
            "lastActivityDate": self.last_activity_date,
            "authorArn": self.author_arn,
            "pullRequestTargets": self.pull_request_targets,
            "approvalRules": [r.to_dict() for r in self.approval_rules.values()],
        }


class ApprovalRuleTemplate(BaseModel):
    def __init__(
        self,
        template_name: str,
        template_content: str,
        template_description: str,
    ):
        self.approval_rule_template_id = str(mock_random.uuid4())
        self.approval_rule_template_name = template_name
        self.approval_rule_template_content = template_content
        self.approval_rule_template_description = template_description
        self.creation_date = iso_8601_datetime_with_milliseconds()
        self.last_modified_date = self.creation_date
        self.last_modified_user = ""
        self.rule_content_sha256 = hashlib.sha256(
            template_content.encode()
        ).hexdigest()
        self.associated_repositories: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "approvalRuleTemplateId": self.approval_rule_template_id,
            "approvalRuleTemplateName": self.approval_rule_template_name,
            "approvalRuleTemplateContent": self.approval_rule_template_content,
            "approvalRuleTemplateDescription": self.approval_rule_template_description,
            "ruleContentSha256": self.rule_content_sha256,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
            "lastModifiedUser": self.last_modified_user,
        }


class CodeCommit(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        repository_description: str,
        repository_name: str,
        tags: Optional[dict[str, str]] = None,
        kms_key_id: Optional[str] = None,
    ):
        current_date = iso_8601_datetime_with_milliseconds()
        self.repository_name = repository_name
        self.repository_metadata: dict[str, Any] = {}
        self.repository_metadata["repositoryName"] = repository_name
        self.repository_metadata["cloneUrlSsh"] = (
            f"ssh://git-codecommit.{region}.amazonaws.com/v1/repos/{repository_name}"
        )
        self.repository_metadata["cloneUrlHttp"] = (
            f"https://git-codecommit.{region}.amazonaws.com/v1/repos/{repository_name}"
        )
        self.repository_metadata["creationDate"] = current_date
        self.repository_metadata["lastModifiedDate"] = current_date
        self.repository_metadata["repositoryDescription"] = repository_description
        self.repository_metadata["repositoryId"] = str(mock_random.uuid4())
        self.repository_metadata["Arn"] = (
            f"arn:{get_partition(region)}:codecommit:{region}:{account_id}:{repository_name}"
        )
        self.repository_metadata["accountId"] = account_id
        if kms_key_id:
            self.repository_metadata["kmsKeyId"] = kms_key_id
        self.repository_metadata["defaultBranch"] = "main"

        self.branches: dict[str, Branch] = {}
        self.commits: dict[str, Commit] = {}
        self.files: dict[str, FileEntry] = {}
        self.tags: dict[str, str] = tags or {}
        self.triggers: list[dict[str, Any]] = []

        # Create initial commit and main branch
        initial_commit_id = str(mock_random.uuid4()).replace("-", "")[:40]
        tree_id = str(mock_random.uuid4()).replace("-", "")[:40]
        initial_commit = Commit(
            commit_id=initial_commit_id,
            tree_id=tree_id,
            parents=[],
            message="Initial commit",
            author_name="CodeCommit",
            author_email="codecommit@amazon.com",
            committer_name="CodeCommit",
            committer_email="codecommit@amazon.com",
        )
        self.commits[initial_commit_id] = initial_commit
        self.branches["main"] = Branch("main", initial_commit_id)


class CodeCommitBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.repositories: dict[str, CodeCommit] = {}
        self.pull_requests: dict[str, PullRequest] = {}
        self.comments: dict[str, Comment] = {}
        self.approval_rule_templates: dict[str, ApprovalRuleTemplate] = {}
        self._pull_request_counter = 0

    def _get_repo(self, repository_name: str) -> CodeCommit:
        repo = self.repositories.get(repository_name)
        if not repo:
            raise RepositoryDoesNotExistException(repository_name)
        return repo

    def _caller_arn(self) -> str:
        return f"arn:{get_partition(self.region_name)}:iam::{self.account_id}:root"

    # ── Repository operations ──

    def create_repository(
        self,
        repository_name: str,
        repository_description: str,
        tags: Optional[dict[str, str]] = None,
        kms_key_id: Optional[str] = None,
    ) -> dict[str, Any]:
        repository = self.repositories.get(repository_name)
        if repository:
            raise RepositoryNameExistsException(repository_name)

        self.repositories[repository_name] = CodeCommit(
            self.account_id,
            self.region_name,
            repository_description,
            repository_name,
            tags=tags,
            kms_key_id=kms_key_id,
        )

        return self.repositories[repository_name].repository_metadata

    def get_repository(self, repository_name: str) -> dict[str, Any]:
        repo = self._get_repo(repository_name)
        return repo.repository_metadata

    def delete_repository(self, repository_name: str) -> Optional[str]:
        repository = self.repositories.get(repository_name)
        if repository:
            self.repositories.pop(repository_name)
            return repository.repository_metadata.get("repositoryId")
        return None

    def batch_get_repositories(
        self, repository_names: list[str]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        repositories = []
        not_found = []
        for name in repository_names:
            repo = self.repositories.get(name)
            if repo:
                repositories.append(repo.repository_metadata)
            else:
                not_found.append(name)
        return repositories, not_found

    def list_repositories(
        self,
        sort_by: str = "repositoryName",
        order: str = "ascending",
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, str]], Optional[str]]:
        repos = []
        for name, repo in self.repositories.items():
            repos.append(
                {
                    "repositoryName": name,
                    "repositoryId": repo.repository_metadata["repositoryId"],
                }
            )
        if sort_by == "lastModifiedDate":
            repos.sort(
                key=lambda r: r.get("repositoryName", ""),
                reverse=(order == "descending"),
            )
        else:
            repos.sort(
                key=lambda r: r.get("repositoryName", ""),
                reverse=(order == "descending"),
            )
        return repos, None

    def update_repository_description(
        self, repository_name: str, repository_description: str
    ) -> None:
        repo = self._get_repo(repository_name)
        repo.repository_metadata["repositoryDescription"] = repository_description
        repo.repository_metadata["lastModifiedDate"] = (
            iso_8601_datetime_with_milliseconds()
        )

    def update_repository_name(
        self, old_name: str, new_name: str
    ) -> None:
        repo = self._get_repo(old_name)
        if new_name in self.repositories:
            raise RepositoryNameExistsException(new_name)
        self.repositories.pop(old_name)
        repo.repository_metadata["repositoryName"] = new_name
        repo.repository_name = new_name
        repo.repository_metadata["lastModifiedDate"] = (
            iso_8601_datetime_with_milliseconds()
        )
        self.repositories[new_name] = repo

    def update_repository_encryption_key(
        self, repository_name: str, kms_key_id: str
    ) -> dict[str, Any]:
        repo = self._get_repo(repository_name)
        repo.repository_metadata["kmsKeyId"] = kms_key_id
        repo.repository_metadata["lastModifiedDate"] = (
            iso_8601_datetime_with_milliseconds()
        )
        return {
            "repositoryId": repo.repository_metadata["repositoryId"],
            "kmsKeyId": kms_key_id,
            "originalKmsKeyId": repo.repository_metadata.get("kmsKeyId", ""),
        }

    # ── Branch operations ──

    def create_branch(
        self, repository_name: str, branch_name: str, commit_id: str
    ) -> None:
        repo = self._get_repo(repository_name)
        if branch_name in repo.branches:
            raise BranchNameExistsException(branch_name)
        repo.branches[branch_name] = Branch(branch_name, commit_id)

    def get_branch(
        self, repository_name: str, branch_name: str
    ) -> dict[str, str]:
        repo = self._get_repo(repository_name)
        branch = repo.branches.get(branch_name)
        if not branch:
            raise BranchDoesNotExistException(branch_name)
        return branch.to_dict()

    def delete_branch(
        self, repository_name: str, branch_name: str
    ) -> dict[str, str]:
        repo = self._get_repo(repository_name)
        branch = repo.branches.get(branch_name)
        if not branch:
            raise BranchDoesNotExistException(branch_name)
        default_branch = repo.repository_metadata.get("defaultBranch")
        if branch_name == default_branch:
            raise DefaultBranchCannotBeDeletedException()
        del repo.branches[branch_name]
        return branch.to_dict()

    def list_branches(
        self,
        repository_name: str,
        next_token: Optional[str] = None,
    ) -> tuple[list[str], Optional[str]]:
        repo = self._get_repo(repository_name)
        return list(repo.branches.keys()), None

    def update_default_branch(
        self, repository_name: str, default_branch_name: str
    ) -> None:
        repo = self._get_repo(repository_name)
        if default_branch_name not in repo.branches:
            raise BranchDoesNotExistException(default_branch_name)
        repo.repository_metadata["defaultBranch"] = default_branch_name

    # ── Commit operations ──

    def create_commit(
        self,
        repository_name: str,
        branch_name: str,
        parent_commit_id: Optional[str],
        author_name: str,
        email: str,
        commit_message: str,
        put_files: Optional[list[dict[str, Any]]] = None,
        delete_files: Optional[list[dict[str, str]]] = None,
        set_file_modes: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        repo = self._get_repo(repository_name)

        commit_id = str(mock_random.uuid4()).replace("-", "")[:40]
        tree_id = str(mock_random.uuid4()).replace("-", "")[:40]
        parents = [parent_commit_id] if parent_commit_id else []

        commit = Commit(
            commit_id=commit_id,
            tree_id=tree_id,
            parents=parents,
            message=commit_message,
            author_name=author_name or "Author",
            author_email=email or "author@example.com",
            committer_name=author_name or "Author",
            committer_email=email or "author@example.com",
        )
        repo.commits[commit_id] = commit

        files_added = []
        files_updated = []
        files_deleted = []

        if put_files:
            for pf in put_files:
                file_path = pf.get("filePath", "")
                file_content = pf.get("fileContent", "")
                if isinstance(file_content, str):
                    file_content = file_content.encode()
                file_mode = pf.get("fileMode", "NORMAL")
                was_update = file_path in repo.files
                entry = FileEntry(file_path, file_content, file_mode)
                repo.files[file_path] = entry
                if was_update:
                    files_updated.append(entry.to_dict())
                else:
                    files_added.append(entry.to_dict())

        if delete_files:
            for df in delete_files:
                file_path = df.get("filePath", "")
                if file_path in repo.files:
                    files_deleted.append({"absolutePath": file_path, "blobId": "", "fileMode": "NORMAL"})
                    del repo.files[file_path]

        # Update branch to point to new commit
        if branch_name in repo.branches:
            repo.branches[branch_name].commit_id = commit_id
        else:
            repo.branches[branch_name] = Branch(branch_name, commit_id)

        return {
            "commitId": commit_id,
            "treeId": tree_id,
            "filesAdded": files_added,
            "filesUpdated": files_updated,
            "filesDeleted": files_deleted,
        }

    def get_commit(
        self, repository_name: str, commit_id: str
    ) -> dict[str, Any]:
        repo = self._get_repo(repository_name)
        commit = repo.commits.get(commit_id)
        if commit:
            return commit.to_dict()
        # Return a stub commit for unknown commit IDs
        return Commit(
            commit_id=commit_id,
            tree_id=str(mock_random.uuid4()).replace("-", "")[:40],
            parents=[],
            message="",
            author_name="Unknown",
            author_email="unknown@example.com",
            committer_name="Unknown",
            committer_email="unknown@example.com",
        ).to_dict()

    def batch_get_commits(
        self, repository_name: str, commit_ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        repo = self._get_repo(repository_name)
        commits = []
        errors = []
        for cid in commit_ids:
            commit = repo.commits.get(cid)
            if commit:
                commits.append(commit.to_dict())
            else:
                errors.append(
                    {
                        "commitId": cid,
                        "errorCode": "CommitDoesNotExistException",
                        "errorMessage": f"Commit '{cid}' does not exist.",
                    }
                )
        return commits, errors

    # ── File/Tree operations (stubs) ──

    def get_file(
        self,
        repository_name: str,
        commit_specifier: Optional[str],
        file_path: str,
    ) -> dict[str, Any]:
        repo = self._get_repo(repository_name)
        entry = repo.files.get(file_path)
        if not entry:
            raise FileDoesNotExistException(file_path)
        commit_id = ""
        if commit_specifier and commit_specifier in repo.branches:
            commit_id = repo.branches[commit_specifier].commit_id
        elif commit_specifier:
            commit_id = commit_specifier
        else:
            default_branch = repo.repository_metadata.get("defaultBranch", "main")
            if default_branch in repo.branches:
                commit_id = repo.branches[default_branch].commit_id

        return {
            "commitId": commit_id,
            "blobId": entry.blob_id,
            "filePath": file_path,
            "fileMode": entry.file_mode,
            "fileSize": len(entry.content),
            "fileContent": base64.b64encode(entry.content).decode(),
        }

    def get_folder(
        self,
        repository_name: str,
        commit_specifier: Optional[str],
        folder_path: str,
    ) -> dict[str, Any]:
        repo = self._get_repo(repository_name)
        commit_id = ""
        if commit_specifier and commit_specifier in repo.branches:
            commit_id = repo.branches[commit_specifier].commit_id
        elif commit_specifier:
            commit_id = commit_specifier
        else:
            default_branch = repo.repository_metadata.get("defaultBranch", "main")
            if default_branch in repo.branches:
                commit_id = repo.branches[default_branch].commit_id

        # Collect files under the folder path
        prefix = folder_path.rstrip("/") + "/" if folder_path != "/" else "/"
        files = []
        sub_folders: set[str] = set()
        for fp, entry in repo.files.items():
            if folder_path == "/" or fp.startswith(prefix):
                relative = fp[len(prefix):] if folder_path != "/" else fp
                if "/" in relative:
                    sub_folder_name = relative.split("/")[0]
                    sub_folders.add(prefix + sub_folder_name if folder_path != "/" else sub_folder_name)
                else:
                    files.append(entry.to_dict())

        return {
            "commitId": commit_id,
            "folderPath": folder_path,
            "files": files,
            "subFolders": [
                {"absolutePath": sf, "relativePath": sf.split("/")[-1], "treeId": str(mock_random.uuid4()).replace("-", "")[:40]}
                for sf in sorted(sub_folders)
            ],
            "symbolicLinks": [],
            "subModules": [],
            "treeId": str(mock_random.uuid4()).replace("-", "")[:40],
        }

    def get_blob(
        self, repository_name: str, blob_id: str
    ) -> dict[str, str]:
        self._get_repo(repository_name)
        # Return stub content for any blob ID
        return {
            "blobId": blob_id,
            "content": base64.b64encode(b"").decode(),
        }

    def put_file(
        self,
        repository_name: str,
        branch_name: str,
        file_content: bytes,
        file_path: str,
        file_mode: str = "NORMAL",
        parent_commit_id: Optional[str] = None,
        commit_message: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict[str, Any]:
        repo = self._get_repo(repository_name)
        entry = FileEntry(file_path, file_content, file_mode)
        repo.files[file_path] = entry

        # Create a commit for the file put
        commit_id = str(mock_random.uuid4()).replace("-", "")[:40]
        tree_id = str(mock_random.uuid4()).replace("-", "")[:40]
        parents = [parent_commit_id] if parent_commit_id else []
        commit = Commit(
            commit_id=commit_id,
            tree_id=tree_id,
            parents=parents,
            message=commit_message or f"Add {file_path}",
            author_name=name or "Author",
            author_email=email or "author@example.com",
            committer_name=name or "Author",
            committer_email=email or "author@example.com",
        )
        repo.commits[commit_id] = commit
        if branch_name in repo.branches:
            repo.branches[branch_name].commit_id = commit_id

        return {
            "commitId": commit_id,
            "blobId": entry.blob_id,
            "treeId": tree_id,
        }

    def delete_file(
        self,
        repository_name: str,
        branch_name: str,
        file_path: str,
        parent_commit_id: str,
        keep_empty_folders: bool = False,
        commit_message: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict[str, Any]:
        repo = self._get_repo(repository_name)
        if file_path in repo.files:
            blob_id = repo.files[file_path].blob_id
            del repo.files[file_path]
        else:
            blob_id = ""

        commit_id = str(mock_random.uuid4()).replace("-", "")[:40]
        tree_id = str(mock_random.uuid4()).replace("-", "")[:40]
        commit = Commit(
            commit_id=commit_id,
            tree_id=tree_id,
            parents=[parent_commit_id] if parent_commit_id else [],
            message=commit_message or f"Delete {file_path}",
            author_name=name or "Author",
            author_email=email or "author@example.com",
            committer_name=name or "Author",
            committer_email=email or "author@example.com",
        )
        repo.commits[commit_id] = commit
        if branch_name in repo.branches:
            repo.branches[branch_name].commit_id = commit_id

        return {
            "commitId": commit_id,
            "blobId": blob_id,
            "treeId": tree_id,
            "filePath": file_path,
        }

    def get_differences(
        self,
        repository_name: str,
        before_commit_specifier: Optional[str],
        after_commit_specifier: str,
        before_path: Optional[str] = None,
        after_path: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        self._get_repo(repository_name)
        # Return empty differences as a stub
        return [], None

    def list_file_commit_history(
        self,
        repository_name: str,
        commit_specifier: Optional[str],
        file_path: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        self._get_repo(repository_name)
        return [], None

    # ── Pull Request operations ──

    def create_pull_request(
        self,
        title: str,
        description: str,
        targets: list[dict[str, str]],
    ) -> dict[str, Any]:
        self._pull_request_counter += 1
        pr_id = str(self._pull_request_counter)
        pr = PullRequest(
            pull_request_id=pr_id,
            title=title,
            description=description or "",
            targets=targets,
            author_arn=self._caller_arn(),
        )
        self.pull_requests[pr_id] = pr
        return pr.to_dict()

    def get_pull_request(self, pull_request_id: str) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        return pr.to_dict()

    def list_pull_requests(
        self,
        repository_name: str,
        author_arn: Optional[str] = None,
        pull_request_status: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[str], Optional[str]]:
        self._get_repo(repository_name)
        pr_ids = []
        for pr_id, pr in self.pull_requests.items():
            match = True
            if author_arn and pr.author_arn != author_arn:
                match = False
            if pull_request_status and pr.pull_request_status != pull_request_status:
                match = False
            # Check if PR targets this repo
            targets_repo = any(
                t.get("repositoryName") == repository_name
                for t in pr.pull_request_targets
            )
            if not targets_repo:
                match = False
            if match:
                pr_ids.append(pr_id)
        return pr_ids, None

    def update_pull_request_title(
        self, pull_request_id: str, title: str
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        pr.title = title
        pr.last_activity_date = iso_8601_datetime_with_milliseconds()
        return pr.to_dict()

    def update_pull_request_description(
        self, pull_request_id: str, description: str
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        pr.description = description
        pr.last_activity_date = iso_8601_datetime_with_milliseconds()
        return pr.to_dict()

    def update_pull_request_status(
        self, pull_request_id: str, pull_request_status: str
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        if pr.pull_request_status == "CLOSED":
            raise PullRequestAlreadyClosedException(pull_request_id)
        pr.pull_request_status = pull_request_status
        pr.last_activity_date = iso_8601_datetime_with_milliseconds()
        pr.events.append(
            {
                "pullRequestId": pull_request_id,
                "eventDate": pr.last_activity_date,
                "pullRequestEventType": "PULL_REQUEST_STATUS_CHANGED",
                "pullRequestStatusChangedEventMetadata": {
                    "pullRequestStatus": pull_request_status
                },
            }
        )
        return pr.to_dict()

    def describe_pull_request_events(
        self,
        pull_request_id: str,
        pull_request_event_type: Optional[str] = None,
        actor_arn: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        events = pr.events
        if pull_request_event_type:
            events = [e for e in events if e.get("pullRequestEventType") == pull_request_event_type]
        if actor_arn:
            events = [e for e in events if e.get("actorArn") == actor_arn]
        return events, None

    # ── Merge operations (stubs) ──

    def merge_branches_by_fast_forward(
        self,
        repository_name: str,
        source_commit_specifier: str,
        destination_commit_specifier: str,
        target_branch: Optional[str] = None,
    ) -> dict[str, str]:
        repo = self._get_repo(repository_name)
        # Resolve source to a commit ID
        if source_commit_specifier in repo.branches:
            source_commit_id = repo.branches[source_commit_specifier].commit_id
        else:
            source_commit_id = source_commit_specifier
        # Update destination branch to point to source commit (fast-forward)
        dest_branch_name = target_branch or destination_commit_specifier
        if dest_branch_name in repo.branches:
            repo.branches[dest_branch_name].commit_id = source_commit_id
        # Return the resulting commit ID and its tree ID
        commit = repo.commits.get(source_commit_id)
        tree_id = commit.tree_id if commit else str(mock_random.uuid4()).replace("-", "")[:40]
        return {"commitId": source_commit_id, "treeId": tree_id}

    def merge_branches_by_squash(
        self,
        repository_name: str,
        source_commit_specifier: str,
        destination_commit_specifier: str,
        target_branch: Optional[str] = None,
        commit_message: Optional[str] = None,
        author_name: Optional[str] = None,
        email: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
        conflict_resolution: Optional[dict[str, Any]] = None,
        keep_empty_folders: bool = False,
    ) -> dict[str, str]:
        self._get_repo(repository_name)
        commit_id = str(mock_random.uuid4()).replace("-", "")[:40]
        tree_id = str(mock_random.uuid4()).replace("-", "")[:40]
        return {"commitId": commit_id, "treeId": tree_id}

    def merge_branches_by_three_way(
        self,
        repository_name: str,
        source_commit_specifier: str,
        destination_commit_specifier: str,
        target_branch: Optional[str] = None,
        commit_message: Optional[str] = None,
        author_name: Optional[str] = None,
        email: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
        conflict_resolution: Optional[dict[str, Any]] = None,
        keep_empty_folders: bool = False,
    ) -> dict[str, str]:
        self._get_repo(repository_name)
        commit_id = str(mock_random.uuid4()).replace("-", "")[:40]
        tree_id = str(mock_random.uuid4()).replace("-", "")[:40]
        return {"commitId": commit_id, "treeId": tree_id}

    def merge_pull_request_by_fast_forward(
        self,
        pull_request_id: str,
        repository_name: str,
        source_commit_id: Optional[str] = None,
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        if pr.pull_request_status == "CLOSED":
            raise PullRequestAlreadyClosedException(pull_request_id)
        pr.pull_request_status = "CLOSED"
        pr.last_activity_date = iso_8601_datetime_with_milliseconds()
        for target in pr.pull_request_targets:
            target["mergeMetadata"] = {"isMerged": True, "mergeCommitId": str(mock_random.uuid4()).replace("-", "")[:40]}
        return pr.to_dict()

    def merge_pull_request_by_squash(
        self,
        pull_request_id: str,
        repository_name: str,
        source_commit_id: Optional[str] = None,
        commit_message: Optional[str] = None,
        author_name: Optional[str] = None,
        email: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
        conflict_resolution: Optional[dict[str, Any]] = None,
        keep_empty_folders: bool = False,
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        if pr.pull_request_status == "CLOSED":
            raise PullRequestAlreadyClosedException(pull_request_id)
        pr.pull_request_status = "CLOSED"
        pr.last_activity_date = iso_8601_datetime_with_milliseconds()
        for target in pr.pull_request_targets:
            target["mergeMetadata"] = {"isMerged": True, "mergeCommitId": str(mock_random.uuid4()).replace("-", "")[:40]}
        return pr.to_dict()

    def merge_pull_request_by_three_way(
        self,
        pull_request_id: str,
        repository_name: str,
        source_commit_id: Optional[str] = None,
        commit_message: Optional[str] = None,
        author_name: Optional[str] = None,
        email: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
        conflict_resolution: Optional[dict[str, Any]] = None,
        keep_empty_folders: bool = False,
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        if pr.pull_request_status == "CLOSED":
            raise PullRequestAlreadyClosedException(pull_request_id)
        pr.pull_request_status = "CLOSED"
        pr.last_activity_date = iso_8601_datetime_with_milliseconds()
        for target in pr.pull_request_targets:
            target["mergeMetadata"] = {"isMerged": True, "mergeCommitId": str(mock_random.uuid4()).replace("-", "")[:40]}
        return pr.to_dict()

    def get_merge_options(
        self,
        repository_name: str,
        source_commit_specifier: str,
        destination_commit_specifier: str,
        conflict_detail_level: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
    ) -> dict[str, Any]:
        self._get_repo(repository_name)
        return {
            "mergeOptions": ["FAST_FORWARD_MERGE", "SQUASH_MERGE", "THREE_WAY_MERGE"],
            "sourceCommitId": source_commit_specifier,
            "destinationCommitId": destination_commit_specifier,
            "baseCommitId": str(mock_random.uuid4()).replace("-", "")[:40],
        }

    def get_merge_commit(
        self,
        repository_name: str,
        source_commit_specifier: str,
        destination_commit_specifier: str,
        conflict_detail_level: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
    ) -> dict[str, str]:
        self._get_repo(repository_name)
        return {
            "sourceCommitId": source_commit_specifier,
            "destinationCommitId": destination_commit_specifier,
            "baseCommitId": str(mock_random.uuid4()).replace("-", "")[:40],
            "mergedCommitId": str(mock_random.uuid4()).replace("-", "")[:40],
        }

    def get_merge_conflicts(
        self,
        repository_name: str,
        destination_commit_specifier: str,
        source_commit_specifier: str,
        merge_option: str,
        conflict_detail_level: Optional[str] = None,
        max_conflict_files: Optional[int] = None,
        conflict_resolution_strategy: Optional[str] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        self._get_repo(repository_name)
        return {
            "mergeable": True,
            "destinationCommitId": destination_commit_specifier,
            "sourceCommitId": source_commit_specifier,
            "baseCommitId": str(mock_random.uuid4()).replace("-", "")[:40],
            "conflictMetadataList": [],
        }

    def batch_describe_merge_conflicts(
        self,
        repository_name: str,
        destination_commit_specifier: str,
        source_commit_specifier: str,
        merge_option: str,
        max_merge_hunks: Optional[int] = None,
        max_conflict_files: Optional[int] = None,
        file_paths: Optional[list[str]] = None,
        conflict_detail_level: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        self._get_repo(repository_name)
        return {
            "conflicts": [],
            "destinationCommitId": destination_commit_specifier,
            "sourceCommitId": source_commit_specifier,
            "baseCommitId": str(mock_random.uuid4()).replace("-", "")[:40],
            "errors": [],
        }

    def describe_merge_conflicts(
        self,
        repository_name: str,
        destination_commit_specifier: str,
        source_commit_specifier: str,
        merge_option: str,
        file_path: str,
        max_merge_hunks: Optional[int] = None,
        conflict_detail_level: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        self._get_repo(repository_name)
        return {
            "conflictMetadata": {
                "filePath": file_path,
                "fileSizes": {"source": 0, "destination": 0, "base": 0},
                "fileModes": {"source": "NORMAL", "destination": "NORMAL", "base": "NORMAL"},
                "objectTypes": {"source": "FILE", "destination": "FILE", "base": "FILE"},
                "numberOfConflicts": 0,
                "isBinaryFile": {"source": False, "destination": False, "base": False},
                "contentConflict": False,
                "fileModeConflict": False,
                "objectTypeConflict": False,
                "mergeOperations": {"source": "A", "destination": "A"},
            },
            "mergeHunks": [],
            "destinationCommitId": destination_commit_specifier,
            "sourceCommitId": source_commit_specifier,
            "baseCommitId": str(mock_random.uuid4()).replace("-", "")[:40],
        }

    def create_unreferenced_merge_commit(
        self,
        repository_name: str,
        source_commit_specifier: str,
        destination_commit_specifier: str,
        merge_option: str,
        conflict_detail_level: Optional[str] = None,
        conflict_resolution_strategy: Optional[str] = None,
        author_name: Optional[str] = None,
        email: Optional[str] = None,
        commit_message: Optional[str] = None,
        keep_empty_folders: bool = False,
        conflict_resolution: Optional[dict[str, Any]] = None,
    ) -> dict[str, str]:
        self._get_repo(repository_name)
        return {
            "commitId": str(mock_random.uuid4()).replace("-", "")[:40],
            "treeId": str(mock_random.uuid4()).replace("-", "")[:40],
        }

    # ── Comment operations ──

    def post_comment_for_compared_commit(
        self,
        repository_name: str,
        before_commit_id: Optional[str],
        after_commit_id: str,
        content: str,
        location: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        self._get_repo(repository_name)
        comment_id = str(mock_random.uuid4())
        comment = Comment(
            comment_id=comment_id,
            content=content,
            author_arn=self._caller_arn(),
        )
        self.comments[comment_id] = comment
        return {
            "repositoryName": repository_name,
            "beforeCommitId": before_commit_id or "",
            "afterCommitId": after_commit_id,
            "beforeBlobId": "",
            "afterBlobId": "",
            "location": location or {},
            "comment": comment.to_dict(),
        }

    def post_comment_for_pull_request(
        self,
        pull_request_id: str,
        repository_name: str,
        before_commit_id: str,
        after_commit_id: str,
        content: str,
        location: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        self._get_repo(repository_name)
        comment_id = str(mock_random.uuid4())
        comment = Comment(
            comment_id=comment_id,
            content=content,
            author_arn=self._caller_arn(),
        )
        self.comments[comment_id] = comment
        pr.comments.append(comment)
        return {
            "repositoryName": repository_name,
            "pullRequestId": pull_request_id,
            "beforeCommitId": before_commit_id,
            "afterCommitId": after_commit_id,
            "beforeBlobId": "",
            "afterBlobId": "",
            "location": location or {},
            "comment": comment.to_dict(),
        }

    def post_comment_reply(
        self,
        in_reply_to: str,
        content: str,
    ) -> dict[str, Any]:
        parent = self.comments.get(in_reply_to)
        if not parent:
            raise CommentDoesNotExistException(in_reply_to)
        comment_id = str(mock_random.uuid4())
        comment = Comment(
            comment_id=comment_id,
            content=content,
            author_arn=self._caller_arn(),
            in_reply_to=in_reply_to,
        )
        self.comments[comment_id] = comment
        return {"comment": comment.to_dict()}

    def get_comment(self, comment_id: str) -> dict[str, Any]:
        comment = self.comments.get(comment_id)
        if not comment:
            raise CommentDoesNotExistException(comment_id)
        return comment.to_dict()

    def update_comment(
        self, comment_id: str, content: str
    ) -> dict[str, Any]:
        comment = self.comments.get(comment_id)
        if not comment:
            raise CommentDoesNotExistException(comment_id)
        comment.content = content
        comment.last_modified_date = iso_8601_datetime_with_milliseconds()
        return comment.to_dict()

    def delete_comment_content(self, comment_id: str) -> dict[str, Any]:
        comment = self.comments.get(comment_id)
        if not comment:
            raise CommentDoesNotExistException(comment_id)
        comment.content = ""
        comment.deleted = True
        return comment.to_dict()

    def get_comments_for_compared_commit(
        self,
        repository_name: str,
        before_commit_id: Optional[str],
        after_commit_id: str,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        self._get_repo(repository_name)
        # Return all comments as a simplified approach
        comments = [c.to_dict() for c in self.comments.values()]
        return comments, None

    def get_comments_for_pull_request(
        self,
        pull_request_id: str,
        repository_name: Optional[str] = None,
        before_commit_id: Optional[str] = None,
        after_commit_id: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        comments_for_pr = []
        for comment in pr.comments:
            comments_for_pr.append(
                {
                    "repositoryName": repository_name or "",
                    "pullRequestId": pull_request_id,
                    "beforeCommitId": before_commit_id or "",
                    "afterCommitId": after_commit_id or "",
                    "beforeBlobId": "",
                    "afterBlobId": "",
                    "location": {},
                    "comments": [comment.to_dict()],
                }
            )
        return comments_for_pr, None

    def put_comment_reaction(
        self, comment_id: str, reaction_value: str
    ) -> None:
        comment = self.comments.get(comment_id)
        if not comment:
            raise CommentDoesNotExistException(comment_id)
        comment.reaction_counts[reaction_value] = (
            comment.reaction_counts.get(reaction_value, 0) + 1
        )
        if reaction_value not in comment.caller_reactions:
            comment.caller_reactions.append(reaction_value)

    def get_comment_reactions(
        self,
        comment_id: str,
        reaction_user_arn: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        comment = self.comments.get(comment_id)
        if not comment:
            raise CommentDoesNotExistException(comment_id)
        reactions = []
        for emoji, count in comment.reaction_counts.items():
            reactions.append(
                {
                    "reaction": {"emoji": emoji, "shortCode": emoji, "unicode": emoji},
                    "reactionUsers": [self._caller_arn()],
                    "reactionsFromDeletedUsersCount": 0,
                }
            )
        return reactions, None

    # ── Approval Rule operations ──

    def create_pull_request_approval_rule(
        self,
        pull_request_id: str,
        approval_rule_name: str,
        approval_rule_content: str,
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        rule_id = str(mock_random.uuid4())
        rule = ApprovalRule(rule_id, approval_rule_name, approval_rule_content)
        pr.approval_rules[approval_rule_name] = rule
        return rule.to_dict()

    def delete_pull_request_approval_rule(
        self, pull_request_id: str, approval_rule_name: str
    ) -> dict[str, str]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        rule = pr.approval_rules.get(approval_rule_name)
        if not rule:
            raise ApprovalRuleDoesNotExistException(approval_rule_name)
        del pr.approval_rules[approval_rule_name]
        return {"approvalRuleId": rule.approval_rule_id}

    def update_pull_request_approval_rule_content(
        self,
        pull_request_id: str,
        approval_rule_name: str,
        new_rule_content: str,
        existing_rule_content_sha256: Optional[str] = None,
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        rule = pr.approval_rules.get(approval_rule_name)
        if not rule:
            raise ApprovalRuleDoesNotExistException(approval_rule_name)
        rule.approval_rule_content = new_rule_content
        rule.rule_content_sha256 = hashlib.sha256(new_rule_content.encode()).hexdigest()
        rule.last_modified_date = iso_8601_datetime_with_milliseconds()
        return rule.to_dict()

    def update_pull_request_approval_state(
        self,
        pull_request_id: str,
        revision_id: str,
        approval_state: str,
    ) -> None:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        # Update or add approval state
        caller_arn = self._caller_arn()
        for state in pr.approval_states:
            if state.get("userArn") == caller_arn:
                state["approvalState"] = approval_state
                return
        pr.approval_states.append(
            {"approvalState": approval_state, "userArn": caller_arn}
        )

    def get_pull_request_approval_states(
        self, pull_request_id: str, revision_id: str
    ) -> list[dict[str, str]]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        return pr.approval_states

    def evaluate_pull_request_approval_rules(
        self,
        pull_request_id: str,
        revision_id: str,
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        import json as _json

        num_approvals = len(pr.approval_states)
        satisfied = []
        not_satisfied = []
        for r in pr.approval_rules.values():
            # Parse NumberOfApprovalsNeeded from rule content if present
            needed = 1
            try:
                content = _json.loads(r.approval_rule_content)
                for stmt in content.get("Statements", []):
                    if "NumberOfApprovalsNeeded" in stmt:
                        needed = int(stmt["NumberOfApprovalsNeeded"])
                        break
            except Exception:
                pass
            if num_approvals >= needed:
                satisfied.append(r.approval_rule_name)
            else:
                not_satisfied.append(r.approval_rule_name)
        all_rules_satisfied = len(not_satisfied) == 0
        return {
            "evaluation": {
                "approved": all_rules_satisfied or pr.override_status == "OVERRIDE",
                "overridden": pr.override_status == "OVERRIDE",
                "approvalRulesSatisfied": satisfied,
                "approvalRulesNotSatisfied": not_satisfied,
            }
        }

    def override_pull_request_approval_rules(
        self,
        pull_request_id: str,
        revision_id: str,
        override_status: str,
    ) -> None:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        pr.override_status = override_status
        pr.override_user = self._caller_arn()

    def get_pull_request_override_state(
        self, pull_request_id: str, revision_id: str
    ) -> dict[str, Any]:
        pr = self.pull_requests.get(pull_request_id)
        if not pr:
            raise PullRequestDoesNotExistException(pull_request_id)
        return {
            "overridden": pr.override_status == "OVERRIDE",
            "overrider": pr.override_user,
        }

    # ── Approval Rule Template operations ──

    def create_approval_rule_template(
        self,
        approval_rule_template_name: str,
        approval_rule_template_content: str,
        approval_rule_template_description: str = "",
    ) -> dict[str, Any]:
        if approval_rule_template_name in self.approval_rule_templates:
            raise ApprovalRuleTemplateNameAlreadyExistsException(
                approval_rule_template_name
            )
        template = ApprovalRuleTemplate(
            approval_rule_template_name,
            approval_rule_template_content,
            approval_rule_template_description,
        )
        self.approval_rule_templates[approval_rule_template_name] = template
        return template.to_dict()

    def get_approval_rule_template(
        self, approval_rule_template_name: str
    ) -> dict[str, Any]:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        return template.to_dict()

    def delete_approval_rule_template(
        self, approval_rule_template_name: str
    ) -> str:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        del self.approval_rule_templates[approval_rule_template_name]
        return template.approval_rule_template_id

    def list_approval_rule_templates(
        self,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[str], Optional[str]]:
        return list(self.approval_rule_templates.keys()), None

    def update_approval_rule_template_name(
        self, old_name: str, new_name: str
    ) -> dict[str, Any]:
        template = self.approval_rule_templates.get(old_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(old_name)
        if new_name in self.approval_rule_templates:
            raise ApprovalRuleTemplateNameAlreadyExistsException(new_name)
        del self.approval_rule_templates[old_name]
        template.approval_rule_template_name = new_name
        template.last_modified_date = iso_8601_datetime_with_milliseconds()
        self.approval_rule_templates[new_name] = template
        return template.to_dict()

    def update_approval_rule_template_content(
        self,
        approval_rule_template_name: str,
        new_rule_content: str,
        existing_rule_content_sha256: Optional[str] = None,
    ) -> dict[str, Any]:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        template.approval_rule_template_content = new_rule_content
        template.rule_content_sha256 = hashlib.sha256(
            new_rule_content.encode()
        ).hexdigest()
        template.last_modified_date = iso_8601_datetime_with_milliseconds()
        return template.to_dict()

    def update_approval_rule_template_description(
        self,
        approval_rule_template_name: str,
        approval_rule_template_description: str,
    ) -> dict[str, Any]:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        template.approval_rule_template_description = (
            approval_rule_template_description
        )
        template.last_modified_date = iso_8601_datetime_with_milliseconds()
        return template.to_dict()

    def associate_approval_rule_template_with_repository(
        self, approval_rule_template_name: str, repository_name: str
    ) -> None:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        self._get_repo(repository_name)
        if repository_name not in template.associated_repositories:
            template.associated_repositories.append(repository_name)

    def disassociate_approval_rule_template_from_repository(
        self, approval_rule_template_name: str, repository_name: str
    ) -> None:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        if repository_name in template.associated_repositories:
            template.associated_repositories.remove(repository_name)

    def batch_associate_approval_rule_template_with_repositories(
        self,
        approval_rule_template_name: str,
        repository_names: list[str],
    ) -> tuple[list[str], list[dict[str, str]]]:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        associated = []
        errors = []
        for name in repository_names:
            if name in self.repositories:
                if name not in template.associated_repositories:
                    template.associated_repositories.append(name)
                associated.append(name)
            else:
                errors.append(
                    {
                        "repositoryName": name,
                        "errorCode": "RepositoryDoesNotExistException",
                        "errorMessage": f"{name} does not exist",
                    }
                )
        return associated, errors

    def batch_disassociate_approval_rule_template_from_repositories(
        self,
        approval_rule_template_name: str,
        repository_names: list[str],
    ) -> tuple[list[str], list[dict[str, str]]]:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        disassociated = []
        errors = []
        for name in repository_names:
            if name in template.associated_repositories:
                template.associated_repositories.remove(name)
                disassociated.append(name)
            else:
                disassociated.append(name)
        return disassociated, errors

    def list_associated_approval_rule_templates_for_repository(
        self,
        repository_name: str,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[str], Optional[str]]:
        self._get_repo(repository_name)
        templates = []
        for name, template in self.approval_rule_templates.items():
            if repository_name in template.associated_repositories:
                templates.append(name)
        return templates, None

    def list_repositories_for_approval_rule_template(
        self,
        approval_rule_template_name: str,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> tuple[list[str], Optional[str]]:
        template = self.approval_rule_templates.get(approval_rule_template_name)
        if not template:
            raise ApprovalRuleTemplateDoesNotExistException(
                approval_rule_template_name
            )
        return template.associated_repositories[:], None

    # ── Trigger operations ──

    def get_repository_triggers(
        self, repository_name: str
    ) -> dict[str, Any]:
        repo = self._get_repo(repository_name)
        return {
            "repositoryName": repository_name,
            "triggers": repo.triggers,
            "configurationId": str(mock_random.uuid4()),
        }

    def put_repository_triggers(
        self, repository_name: str, triggers: list[dict[str, Any]]
    ) -> str:
        repo = self._get_repo(repository_name)
        repo.triggers = triggers
        return str(mock_random.uuid4())

    def test_repository_triggers(
        self, repository_name: str, triggers: list[dict[str, Any]]
    ) -> tuple[list[str], list[dict[str, str]]]:
        self._get_repo(repository_name)
        successful = [t.get("name", "") for t in triggers]
        return successful, []

    # ── Tag operations ──

    def tag_resource(
        self, resource_arn: str, tags: dict[str, str]
    ) -> None:
        # Find the resource by ARN
        for repo in self.repositories.values():
            if repo.repository_metadata.get("Arn") == resource_arn:
                repo.tags.update(tags)
                return

    def untag_resource(
        self, resource_arn: str, tag_keys: list[str]
    ) -> None:
        for repo in self.repositories.values():
            if repo.repository_metadata.get("Arn") == resource_arn:
                for key in tag_keys:
                    repo.tags.pop(key, None)
                return

    def list_tags_for_resource(
        self, resource_arn: str, next_token: Optional[str] = None
    ) -> tuple[dict[str, str], Optional[str]]:
        for repo in self.repositories.values():
            if repo.repository_metadata.get("Arn") == resource_arn:
                return repo.tags, None
        return {}, None


codecommit_backends = BackendDict(CodeCommitBackend, "codecommit")
