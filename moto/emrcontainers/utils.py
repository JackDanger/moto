import string
from typing import Any

from moto.moto_api._internal import mock_random as random


def paginated_list(
    full_list: list[dict[str, Any]],
    sort_key: str,
    max_results: int | None,
    next_token: str | None,
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Returns a tuple containing a slice of the full list, ordered by sort_key,
    starting at next_token and containing at most max_results elements, and
    the new next_token to pass back for the following page (None on the last
    page).
    """
    sorted_list = sorted(full_list, key=lambda item: item[sort_key])
    limit = max_results or len(sorted_list)

    start = 0
    if next_token:
        start = next(
            (i for i, item in enumerate(sorted_list) if item[sort_key] == next_token),
            0,
        )
    end = min(start + limit, len(sorted_list))
    new_next = sorted_list[end][sort_key] if end < len(sorted_list) else None

    return sorted_list[start:end], new_next


def random_id(size: int = 13) -> str:
    chars = list(range(10)) + list(string.ascii_lowercase)
    return "".join(str(random.choice(chars)) for x in range(size))


def random_cluster_id() -> str:
    return random_id(size=25)


def random_job_id() -> str:
    return random_id(size=19)
