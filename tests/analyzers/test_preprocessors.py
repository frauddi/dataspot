"""Unit tests for the Preprocessor class and email preprocessing.

This module tests the preprocessing functionality in isolation, focusing on
email pattern extraction, custom preprocessors, and field transformations.
"""

import pytest

from dataspot.analyzers.preprocessors import Preprocessor, email_preprocessor


class TestEmailPreprocessor:
    """Test cases for the email_preprocessor function."""

    def test_email_preprocessor_with_valid_email(self):
        """Test email preprocessing with valid email addresses."""
        # Basic email
        result = email_preprocessor("john.doe@example.com")
        assert result == ["john", "doe"]

        # Email with numbers (should extract only alphabetic parts)
        result = email_preprocessor("user123@domain.com")
        assert result == ["user"]

        # Email with underscores and dots
        result = email_preprocessor("first.last_name@company.org")
        assert result == ["first", "last", "name"]

    def test_email_preprocessor_with_complex_emails(self):
        """Test email preprocessing with complex email formats."""
        # Multiple dots and underscores
        result = email_preprocessor("john.doe.smith_jr@example.com")
        assert result == ["john", "doe", "smith", "jr"]

        # Mixed case
        result = email_preprocessor("JohnDoe@Example.COM")
        assert result == ["JohnDoe"]

        # Single character parts
        result = email_preprocessor("a.b.c@test.com")
        assert result == ["a", "b", "c"]

    def test_email_preprocessor_with_special_cases(self):
        """Test email preprocessing with special cases."""
        # Email with only numbers in local part
        result = email_preprocessor("123456@domain.com")
        assert result == []

        # Email with mixed alphanumeric
        result = email_preprocessor("abc123def456@domain.com")
        assert result == ["abc", "def"]

        # Email with special characters
        result = email_preprocessor("user+tag@domain.com")
        assert result == ["user", "tag"]

    def test_email_preprocessor_with_invalid_input(self):
        """Test email preprocessing with invalid input."""
        # No @ symbol
        result = email_preprocessor("notanemail")
        assert result == "notanemail"

        # Empty string
        result = email_preprocessor("")
        assert result == ""

        # None value
        result = email_preprocessor(None)
        assert result == ""

        # Non-string value
        result = email_preprocessor(123)
        assert result == 123

    def test_email_preprocessor_edge_cases(self):
        """Test email preprocessing edge cases."""
        # Email with @ at the beginning
        result = email_preprocessor("@domain.com")
        assert result == []

        # Email with multiple @ symbols (invalid but should handle gracefully)
        result = email_preprocessor("user@domain@extra.com")
        assert result == ["user"]

        # Empty local part
        result = email_preprocessor("@domain.com")
        assert result == []


class TestPreprocessorInitialization:
    """Test cases for Preprocessor class initialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = Preprocessor()

    def test_initialization(self):
        """Test that Preprocessor initializes correctly."""
        assert isinstance(self.preprocessor, Preprocessor)
        assert self.preprocessor.email_fields == ["email", "email_pattern"]
        assert self.preprocessor.custom_preprocessors == {}

    def test_initial_email_fields(self):
        """Test initial email fields configuration."""
        email_fields = self.preprocessor.get_email_fields()
        assert "email" in email_fields
        assert "email_pattern" in email_fields
        assert len(email_fields) == 2


class TestPreprocessorEmailFields:
    """Test cases for email field management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = Preprocessor()

    def test_add_email_field(self):
        """Test adding email fields."""
        self.preprocessor.add_email_field("user_email")

        email_fields = self.preprocessor.get_email_fields()
        assert "user_email" in email_fields
        assert len(email_fields) == 3

    def test_add_duplicate_email_field(self):
        """Test adding duplicate email field."""
        initial_count = len(self.preprocessor.get_email_fields())

        # Add existing field
        self.preprocessor.add_email_field("email")

        # Should not duplicate
        email_fields = self.preprocessor.get_email_fields()
        assert len(email_fields) == initial_count
        assert email_fields.count("email") == 1

    def test_remove_email_field(self):
        """Test removing email fields."""
        # Remove existing field
        self.preprocessor.remove_email_field("email_pattern")

        email_fields = self.preprocessor.get_email_fields()
        assert "email_pattern" not in email_fields
        assert "email" in email_fields

    def test_remove_nonexistent_email_field(self):
        """Test removing non-existent email field."""
        initial_fields = self.preprocessor.get_email_fields()

        # Remove non-existent field
        self.preprocessor.remove_email_field("nonexistent")

        # Should not change anything
        assert self.preprocessor.get_email_fields() == initial_fields

    def test_set_email_fields(self):
        """Test setting complete email fields list."""
        new_fields = ["contact_email", "billing_email", "support_email"]
        self.preprocessor.set_email_fields(new_fields)

        email_fields = self.preprocessor.get_email_fields()
        assert email_fields == new_fields
        assert "email" not in email_fields  # Original fields should be replaced

    def test_set_email_fields_creates_copy(self):
        """Test that set_email_fields creates a copy."""
        original_list = ["test1", "test2"]
        self.preprocessor.set_email_fields(original_list)

        # Modify original list
        original_list.append("test3")

        # Internal list should not be affected
        email_fields = self.preprocessor.get_email_fields()
        assert "test3" not in email_fields
        assert len(email_fields) == 2

    def test_get_email_fields_returns_copy(self):
        """Test that get_email_fields returns a copy."""
        email_fields = self.preprocessor.get_email_fields()
        original_length = len(email_fields)

        # Modify returned list
        email_fields.append("modified")

        # Internal list should not be affected
        new_fields = self.preprocessor.get_email_fields()
        assert len(new_fields) == original_length
        assert "modified" not in new_fields


class TestPreprocessorCustomPreprocessors:
    """Test cases for custom preprocessor management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = Preprocessor()

    def test_add_custom_preprocessor(self):
        """Test adding custom preprocessors."""

        def upper_preprocessor(value):
            return str(value).upper() if value is not None else ""

        self.preprocessor.add_custom_preprocessor("name", upper_preprocessor)

        assert "name" in self.preprocessor.custom_preprocessors
        assert self.preprocessor.custom_preprocessors["name"] == upper_preprocessor

    def test_add_multiple_custom_preprocessors(self):
        """Test adding multiple custom preprocessors."""

        def upper_preprocessor(value):
            return str(value).upper()

        def lower_preprocessor(value):
            return str(value).lower()

        self.preprocessor.add_custom_preprocessor("field1", upper_preprocessor)
        self.preprocessor.add_custom_preprocessor("field2", lower_preprocessor)

        assert len(self.preprocessor.custom_preprocessors) == 2
        assert "field1" in self.preprocessor.custom_preprocessors
        assert "field2" in self.preprocessor.custom_preprocessors

    def test_replace_custom_preprocessor(self):
        """Test replacing existing custom preprocessor."""

        def first_preprocessor(value):
            return f"first_{value}"

        def second_preprocessor(value):
            return f"second_{value}"

        # Add first preprocessor
        self.preprocessor.add_custom_preprocessor("test_field", first_preprocessor)

        # Replace with second preprocessor
        self.preprocessor.add_custom_preprocessor("test_field", second_preprocessor)

        assert len(self.preprocessor.custom_preprocessors) == 1
        assert (
            self.preprocessor.custom_preprocessors["test_field"] == second_preprocessor
        )


class TestPreprocessorValueProcessing:
    """Test cases for value preprocessing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = Preprocessor()

    def test_preprocess_value_with_custom_preprocessor(self):
        """Test preprocessing with custom preprocessor."""

        def custom_preprocessor(value):
            return f"processed_{value}"

        self.preprocessor.add_custom_preprocessor("test_field", custom_preprocessor)

        record = {"test_field": "value"}
        result = self.preprocessor.preprocess_value("test_field", "value", record)

        assert result == "processed_value"

    def test_preprocess_value_with_email_field(self):
        """Test preprocessing with email field."""
        record = {"email": "john.doe@example.com"}
        result = self.preprocessor.preprocess_value(
            "email", "john.doe@example.com", record
        )

        assert result == ["john", "doe"]

    def test_preprocess_value_with_custom_email_field(self):
        """Test preprocessing with custom email field."""
        self.preprocessor.add_email_field("user_email")

        record = {"email": "john.doe@example.com", "user_email": "jane.smith@test.com"}
        result = self.preprocessor.preprocess_value(
            "user_email", "jane.smith@test.com", record
        )

        # Should use the record's email field if available
        assert result == ["john", "doe"]

    def test_preprocess_value_email_field_without_record_email(self):
        """Test email preprocessing when record has no email field."""
        self.preprocessor.add_email_field("contact_email")

        record = {"contact_email": "user@domain.com"}
        result = self.preprocessor.preprocess_value(
            "contact_email", "user@domain.com", record
        )

        # Should use the provided value since no 'email' field in record
        assert result == ["user"]

    def test_preprocess_value_with_none(self):
        """Test preprocessing with None value."""
        record = {"field": None}
        result = self.preprocessor.preprocess_value("field", None, record)

        assert result == ""

    def test_preprocess_value_default_behavior(self):
        """Test preprocessing default behavior (no custom processor, not email)."""
        record = {"field": "value"}
        result = self.preprocessor.preprocess_value("field", "value", record)

        assert result == "value"

    def test_preprocess_value_priority_custom_over_email(self):
        """Test that custom preprocessors have priority over email processing."""

        def custom_preprocessor(value):
            return f"custom_{value}"

        # Add custom preprocessor for an email field
        self.preprocessor.add_custom_preprocessor("email", custom_preprocessor)

        record = {"email": "john.doe@example.com"}
        result = self.preprocessor.preprocess_value(
            "email", "john.doe@example.com", record
        )

        # Should use custom preprocessor, not email processing
        assert result == "custom_john.doe@example.com"


class TestPreprocessorEmailProcessing:
    """Test cases for internal email processing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = Preprocessor()

    def test_preprocess_email_with_record_email(self):
        """Test email preprocessing with email in record."""
        record = {"email": "john.doe@example.com", "other": "value"}
        result = self.preprocessor._preprocess_email(
            "other", "different@test.com", record
        )

        # Should use record's email field
        assert result == ["john", "doe"]

    def test_preprocess_email_without_record_email(self):
        """Test email preprocessing without email in record."""
        record = {"other": "value"}
        result = self.preprocessor._preprocess_email(
            "email_field", "user@domain.com", record
        )

        # Should use provided value
        assert result == ["user"]

    def test_preprocess_email_with_none_value(self):
        """Test email preprocessing with None value."""
        record = {}
        result = self.preprocessor._preprocess_email("email", None, record)

        assert result == ""


class TestPreprocessorEdgeCases:
    """Test edge cases and error conditions for Preprocessor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = Preprocessor()

    def test_custom_preprocessor_with_exception(self):
        """Test behavior when custom preprocessor raises exception."""

        def failing_preprocessor(value):
            raise ValueError("Preprocessor error")

        self.preprocessor.add_custom_preprocessor("test_field", failing_preprocessor)

        # Should raise the exception
        record = {"test_field": "value"}
        with pytest.raises(ValueError, match="Preprocessor error"):
            self.preprocessor.preprocess_value("test_field", "value", record)

    def test_custom_preprocessor_with_none_return(self):
        """Test custom preprocessor that returns None."""

        def none_preprocessor(value):
            return None

        self.preprocessor.add_custom_preprocessor("test_field", none_preprocessor)

        record = {"test_field": "value"}
        result = self.preprocessor.preprocess_value("test_field", "value", record)

        assert result is None

    def test_email_field_with_complex_record(self):
        """Test email processing with complex record structure."""
        record = {
            "email": "primary@example.com",
            "secondary_email": "secondary@test.com",
            "user": {"nested": "data"},
            "list_field": [1, 2, 3],
        }

        result = self.preprocessor.preprocess_value(
            "email", "primary@example.com", record
        )
        assert result == ["primary"]

        # Test with non-email field
        result = self.preprocessor.preprocess_value("user", record["user"], record)
        assert result == record["user"]

    def test_large_email_list(self):
        """Test performance with large email field list."""
        # Add many email fields
        for i in range(100):
            self.preprocessor.add_email_field(f"email_{i}")

        # Should still work efficiently
        email_fields = self.preprocessor.get_email_fields()
        assert len(email_fields) == 102  # 2 initial + 100 added

        # Test processing
        record = {"email_50": "test@example.com"}
        result = self.preprocessor.preprocess_value(
            "email_50", "test@example.com", record
        )
        assert result == ["test"]

    def test_unicode_email_processing(self):
        """Test email processing with unicode characters."""
        record = {"email": "josé.maría@dominio.com"}
        result = self.preprocessor.preprocess_value(
            "email", "josé.maría@dominio.com", record
        )

        # The regex [a-zA-Z]+ only extracts ASCII alphabetic parts
        # Unicode characters like é, í are not included in the basic ASCII range
        assert "jos" in result  # é is stripped, leaving jos
        assert "mar" in result  # í is stripped, leaving mar
        assert "a" in result  # ía becomes just a
