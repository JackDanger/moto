"""Static conformance checks between moto's response handlers and botocore's models.

Moto serializes a handler's ``ActionResult`` against the operation's botocore
output shape. A key that the shape does not recognise is silently dropped, and a
handler that returns nothing yields an empty body. Neither failure raises, so
they surface far away from the cause -- typically as a ``KeyError`` in a caller,
or a response that is simply missing a field.

These tests read the handlers rather than invoking them, so they cover every
operation regardless of how hard it is to set up.
"""

import ast
import json
import pathlib
import re
from collections import defaultdict
from typing import Any

import botocore.session
import pytest
from botocore import xform_name
from botocore.model import OperationModel, ServiceModel

MOTO_ROOT = pathlib.Path(__file__).parent.parent.parent / "moto"
BASELINE_PATH = pathlib.Path(__file__).parent / "response_shape_baseline.json"

# Directory name in moto/ -> botocore service name, where they differ.
SERVICE_DIR_ALIASES = {"awslambda": "lambda"}

RESULT_WRAPPERS = {"ActionResult", "PaginatedResult"}


def _snake(name: str) -> str:
    intermediate = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", intermediate).lower()


def _accepted_keys(operation: OperationModel) -> set[str]:
    """Keys the serializer will recognise for this operation's output.

    Mirrors moto.core.serialize's alias providers: the member name itself, the
    ``locationName`` used on the wire, the name of the member's own shape (see
    ``ShapeNameAlias``), and the snake_case form of each.
    """
    shape = operation.output_shape
    if shape is None:
        return set()
    keys: set[str] = set()
    for member_name, member_shape in shape.members.items():
        candidates = {member_name, member_shape.serialization.get("name", member_name)}
        if member_shape.type_name in ("list", "structure"):
            shape_name = getattr(member_shape, "name", None)
            if shape_name:
                candidates.add(shape_name)
        for candidate in list(candidates):
            candidates.add(xform_name(candidate))
        keys |= candidates
    return keys


def _iter_services() -> Any:
    session = botocore.session.get_session()
    for directory in sorted(MOTO_ROOT.iterdir()):
        if not directory.is_dir():
            continue
        service_name = SERVICE_DIR_ALIASES.get(directory.name, directory.name)
        try:
            model = session.get_service_model(service_name)
        except Exception:
            # Not an AWS service directory (moto_api, core, utilities, ...)
            continue
        yield directory, model


def _response_files(directory: pathlib.Path) -> list[pathlib.Path]:
    return sorted(
        [*directory.rglob("responses.py"), *directory.rglob("responses/*.py")]
    )


def _operations_by_handler_name(model: ServiceModel) -> dict[str, OperationModel]:
    return {_snake(name): model.operation_model(name) for name in model.operation_names}


def _returns_empty_body(func: ast.FunctionDef) -> bool:
    """True when the handler's final statement returns an empty response."""
    body = [
        stmt
        for stmt in func.body
        if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
    ]
    if not body:
        return False
    last = body[-1]
    if not isinstance(last, ast.Return) or last.value is None:
        return False
    dumped = ast.dump(last.value)
    return "EmptyResult" in dumped or "Dict(keys=[], values=[])" in dumped


def _literal_result_keys(func: ast.FunctionDef) -> list[tuple[str, int]]:
    """Top-level string keys of literal dicts passed to ActionResult/PaginatedResult."""
    found: list[tuple[str, int]] = []
    for node in ast.walk(func):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "id", None) not in RESULT_WRAPPERS:
            continue
        if not node.args or not isinstance(node.args[0], ast.Dict):
            continue
        for key in node.args[0].keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                found.append((key.value, node.lineno))
    return found


def _walk_handlers() -> Any:
    """Yield (service_dir_name, file, handler_ast, operation) for every handler
    whose name matches a real botocore operation."""
    for directory, model in _iter_services():
        operations = _operations_by_handler_name(model)
        for file in _response_files(directory):
            try:
                tree = ast.parse(file.read_text())
            except SyntaxError:  # pragma: no cover - caught by other tests
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for member in node.body:
                    if not isinstance(member, ast.FunctionDef):
                        continue
                    operation = operations.get(member.name)
                    if operation is not None:
                        yield directory.name, file, member, operation


def test_response_keys_are_recognised_by_the_output_shape() -> None:
    """Every literal key a handler returns must be one the serializer accepts.

    An unrecognised key is dropped silently, so the field never reaches the
    caller. ``PutScalingPolicy`` returning ``PolicyArn`` where the shape declares
    ``PolicyARN`` produced an empty response for exactly this reason.
    """
    violations = []
    for service, file, handler, operation in _walk_handlers():
        accepted = _accepted_keys(operation)
        if not accepted:
            continue
        for key, lineno in _literal_result_keys(handler):
            if key not in accepted:
                violations.append(
                    f"{file}:{lineno} {service}.{handler.name} "
                    f"({operation.name}) returns {key!r}, which the output shape "
                    f"does not accept. Valid members: "
                    f"{sorted(operation.output_shape.members)}"
                )
    assert not violations, "Unrecognised response keys:\n" + "\n".join(violations)


def test_acknowledgement_operations_report_their_result() -> None:
    """Operations whose entire output is boolean flags must return them.

    These are the ``{"Return": true}`` style acknowledgements. There is exactly
    one correct response, so an empty body is unambiguously wrong --
    ``CancelCapacityReservation`` returned nothing and broke clients that read
    ``Return``.
    """
    violations = []
    for service, file, handler, operation in _walk_handlers():
        shape = operation.output_shape
        if shape is None or not shape.members:
            continue
        if not all(m.type_name == "boolean" for m in shape.members.values()):
            continue
        if _returns_empty_body(handler):
            violations.append(
                f"{file}:{handler.lineno} {service}.{handler.name} "
                f"({operation.name}) returns an empty body but AWS returns "
                f"{sorted(shape.members)}"
            )
    assert not violations, "Missing acknowledgement fields:\n" + "\n".join(violations)


def _current_empty_body_handlers() -> dict[str, list[str]]:
    found: dict[str, list[str]] = defaultdict(list)
    for service, _file, handler, operation in _walk_handlers():
        shape = operation.output_shape
        if shape is None or not shape.members:
            continue
        if _returns_empty_body(handler):
            found[service].append(handler.name)
    return {service: sorted(names) for service, names in sorted(found.items())}


def test_empty_body_handlers_do_not_increase() -> None:
    """Guard the wider class of handlers that answer with an empty body.

    Some of these are deliberate placeholders for unimplemented operations, so
    this is a ratchet rather than a hard zero: the recorded baseline may shrink
    freely, but a new one has to be added deliberately.
    """
    baseline = json.loads(BASELINE_PATH.read_text())
    current = _current_empty_body_handlers()

    added = []
    for service, names in current.items():
        new_names = set(names) - set(baseline.get(service, []))
        added += [f"{service}.{name}" for name in sorted(new_names)]

    assert not added, (
        "These handlers newly return an empty body despite a modelled output "
        "shape. Return the modelled fields, or add them to "
        f"{BASELINE_PATH.name} with a reason:\n  " + "\n  ".join(added)
    )


@pytest.mark.parametrize("service", ["ec2", "autoscaling", "ecs", "rds"])
def test_baseline_is_not_stale(service: str) -> None:
    """Entries that have since been fixed should be removed from the baseline."""
    baseline = json.loads(BASELINE_PATH.read_text())
    current = _current_empty_body_handlers()
    stale = sorted(set(baseline.get(service, [])) - set(current.get(service, [])))
    assert not stale, (
        f"{service}: these baseline entries no longer return an empty body and "
        f"should be dropped from {BASELINE_PATH.name}:\n  " + "\n  ".join(stale)
    )
