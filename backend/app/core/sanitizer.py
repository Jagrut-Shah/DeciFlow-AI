"""
Input Sanitization Utilities
----------------------------
Provides sanitize_string, sanitize_dict, and InputSanitizationMixin (Pydantic).
Use InputSanitizationMixin on any Request schema to guard against:
  - HTML/JS injection (strips tags)
  - Excessively long inputs (truncates)
  - Leading/trailing whitespace
"""

import re
from typing import Any, Dict
from pydantic import model_validator

_SCRIPT_TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_JS_PROTOCOL_RE = re.compile(r"javascript:", re.IGNORECASE)
_MAX_STRING_LENGTH = 2000


def sanitize_string(value: str, max_length: int = _MAX_STRING_LENGTH) -> str:
    """
    Sanitize a single string value:
      1. Strip surrounding whitespace
      2. Remove <script> and <style> tags and their contents
      3. Remove all other HTML tags
      4. Remove javascript: protocol strings
      5. Truncate to max_length
    """
    value = value.strip()
    value = _SCRIPT_TAG_RE.sub("", value)
    value = _HTML_TAG_RE.sub("", value)
    value = _JS_PROTOCOL_RE.sub("", value)
    return value[:max_length]


def sanitize_dict(data: Dict[str, Any], max_length: int = _MAX_STRING_LENGTH) -> Dict[str, Any]:
    """
    Recursively sanitize all string values inside a dict.
    Non-string values are left untouched.
    """
    result: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = sanitize_string(value, max_length)
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value, max_length)
        elif isinstance(value, list):
            result[key] = [
                sanitize_string(item, max_length) if isinstance(item, str)
                else sanitize_dict(item, max_length) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


class InputSanitizationMixin:
    """
    Pydantic model mixin that auto-sanitizes all str fields before validation.

    Usage:
        class MyRequest(InputSanitizationMixin, BaseModel):
            name: str
            description: str
    """

    @model_validator(mode="before")
    @classmethod
    def sanitize_inputs(cls, values: Any) -> Any:
        if isinstance(values, dict):
            return sanitize_dict(values)
        return values
