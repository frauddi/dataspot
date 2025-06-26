"""Preprocessing functionality for Dataspot.

This module handles all data preprocessing including email patterns,
custom preprocessors, and other field transformations.
"""

import re
from typing import Any, Callable, Dict, List


def email_preprocessor(value: Any) -> Any:
    """Extract alphabetic parts from email addresses.

    Args:
        value: Email address string

    Returns:
        List of alphabetic parts from email local part, or original value

    """
    # Handle None values
    if value is None:
        return ""

    if isinstance(value, str) and "@" in value:
        # Extract local part (before @)
        email_local = value[: value.index("@")]
        # Extract all alphabetic sequences
        return re.findall(r"[a-zA-Z]+", email_local)

    return value


class Preprocessor:
    """Manages all preprocessing functionality for Dataspot.

    This class handles email pattern extraction, custom preprocessors,
    and other field transformations in a centralized way.
    """

    def __init__(self):
        """Initialize the preprocessor manager."""
        self.email_fields = ["email", "email_pattern"]
        self.custom_preprocessors: Dict[str, Callable] = {}

    def add_custom_preprocessor(
        self, field_name: str, preprocessor: Callable[[Any], Any]
    ) -> None:
        """Add a custom preprocessor for a specific field.

        Args:
            field_name: Name of the field to preprocess
            preprocessor: Function to apply to field values

        """
        self.custom_preprocessors[field_name] = preprocessor

    def add_email_field(self, field_name: str) -> None:
        """Add a field to be treated as email for preprocessing.

        Args:
            field_name: Name of the field containing emails

        """
        if field_name not in self.email_fields:
            self.email_fields.append(field_name)

    def remove_email_field(self, field_name: str) -> None:
        """Remove a field from email preprocessing.

        Args:
            field_name: Name of the field to stop treating as email

        """
        if field_name in self.email_fields:
            self.email_fields.remove(field_name)

    def set_email_fields(self, field_names: List[str]) -> None:
        """Set the complete list of email fields.

        Args:
            field_names: List of field names to treat as emails

        """
        self.email_fields = field_names.copy()

    def get_email_fields(self) -> List[str]:
        """Get the current list of email fields.

        Returns:
            List of field names treated as emails

        """
        return self.email_fields.copy()

    def preprocess_value(self, field: str, value: Any, record: Dict[str, Any]) -> Any:
        """Preprocess field values based on type and custom preprocessors.

        Args:
            field: Field name
            value: Field value
            record: Complete record for context

        Returns:
            Preprocessed value

        """
        # Apply custom preprocessor if available
        if field in self.custom_preprocessors:
            return self.custom_preprocessors[field](value)

        # Handle email patterns
        if field in self.email_fields:
            return self._preprocess_email(field, value, record)

        # Handle None values
        if value is None:
            return ""

        return value

    def _preprocess_email(self, field: str, value: Any, record: Dict[str, Any]) -> Any:
        """Preprocess email field values to extract patterns.

        Args:
            field: Field name
            value: Field value
            record: Complete record for context

        Returns:
            List of alphabetic parts from email local part, or original value

        """
        # Use 'email' field if available, otherwise use the provided value
        email_value = record.get("email", value)
        return email_preprocessor(email_value)
