from moto.core.exceptions import JsonRESTError


class RepositoryNameExistsException(JsonRESTError):
    code = 400

    def __init__(self, repository_name: str):
        super().__init__(
            "RepositoryNameExistsException",
            f"Repository named {repository_name} already exists",
        )


class RepositoryDoesNotExistException(JsonRESTError):
    code = 400

    def __init__(self, repository_name: str):
        super().__init__(
            "RepositoryDoesNotExistException", f"{repository_name} does not exist"
        )


class InvalidRepositoryNameException(JsonRESTError):
    code = 400

    def __init__(self) -> None:
        super().__init__(
            "InvalidRepositoryNameException",
            "The repository name is not valid. Repository names can be any valid "
            "combination of letters, numbers, "
            "periods, underscores, and dashes between 1 and 100 characters in "
            "length. Names are case sensitive. "
            "For more information, see Limits in the AWS CodeCommit User Guide. ",
        )


class BranchDoesNotExistException(JsonRESTError):
    code = 400

    def __init__(self, branch_name: str):
        super().__init__(
            "BranchDoesNotExistException",
            f"Branch named {branch_name} does not exist",
        )


class BranchNameExistsException(JsonRESTError):
    code = 400

    def __init__(self, branch_name: str):
        super().__init__(
            "BranchNameExistsException",
            f"Branch named {branch_name} already exists",
        )


class PullRequestDoesNotExistException(JsonRESTError):
    code = 400

    def __init__(self, pull_request_id: str):
        super().__init__(
            "PullRequestDoesNotExistException",
            f"Pull request {pull_request_id} does not exist",
        )


class CommentDoesNotExistException(JsonRESTError):
    code = 400

    def __init__(self, comment_id: str):
        super().__init__(
            "CommentDoesNotExistException",
            f"Comment {comment_id} does not exist",
        )


class ApprovalRuleTemplateDoesNotExistException(JsonRESTError):
    code = 400

    def __init__(self, template_name: str):
        super().__init__(
            "ApprovalRuleTemplateDoesNotExistException",
            f"Approval rule template named {template_name} does not exist",
        )


class ApprovalRuleTemplateNameAlreadyExistsException(JsonRESTError):
    code = 400

    def __init__(self, template_name: str):
        super().__init__(
            "ApprovalRuleTemplateNameAlreadyExistsException",
            f"Approval rule template named {template_name} already exists",
        )


class FileDoesNotExistException(JsonRESTError):
    code = 400

    def __init__(self, file_path: str):
        super().__init__(
            "FileDoesNotExistException",
            f"File {file_path} does not exist",
        )


class PullRequestAlreadyClosedException(JsonRESTError):
    code = 400

    def __init__(self, pull_request_id: str):
        super().__init__(
            "PullRequestAlreadyClosedException",
            f"Pull request {pull_request_id} is already closed",
        )


class ApprovalRuleDoesNotExistException(JsonRESTError):
    code = 400

    def __init__(self, rule_name: str):
        super().__init__(
            "ApprovalRuleDoesNotExistException",
            f"Approval rule named {rule_name} does not exist",
        )


class DefaultBranchCannotBeDeletedException(JsonRESTError):
    code = 400

    def __init__(self) -> None:
        super().__init__(
            "DefaultBranchCannotBeDeletedException",
            "The default branch cannot be deleted.",
        )
