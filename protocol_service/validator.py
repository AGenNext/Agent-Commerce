from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

FORMAT_CHECKER = FormatChecker()


def validate_payload(schema: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    return [error.message for error in errors]
