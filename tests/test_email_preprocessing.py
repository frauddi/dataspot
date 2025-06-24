"""Tests for email preprocessing functionality in Dataspot.

This module tests the email pattern extraction and preprocessing capabilities,
including edge cases and various email formats.
"""

from dataspot import Dataspot


class TestEmailPreprocessing:
    """Test cases for email preprocessing functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataspot = Dataspot()

    def test_basic_email_extraction(self):
        """Test basic email pattern extraction."""
        email_data = [
            {"email": "john.doe@company.com", "department": "tech"},
            {"email": "jane.smith@company.com", "department": "sales"},
            {"email": "admin@company.com", "department": "ops"},
        ]

        patterns = self.dataspot.find(email_data, ["email", "department"])
        assert len(patterns) > 0

        # Should find email patterns with extracted words
        email_patterns = [p for p in patterns if "email=" in p.path]
        assert len(email_patterns) > 0

    def test_email_local_part_extraction(self):
        """Test extraction of alphabetic parts from email local part."""
        test_cases = [
            ("john.doe@company.com", ["john", "doe"]),
            ("admin@company.com", ["admin"]),
            ("user123.test456@domain.com", ["user", "test"]),
            ("admin_support_2023@domain.com", ["admin", "support"]),
            ("sales-team-01@domain.com", ["sales", "team"]),
        ]

        for email, expected in test_cases:
            test_record = {"email": email}
            processed = self.dataspot._preprocess_value("email", email, test_record)
            assert processed == expected, f"Failed for email: {email}"

    def test_emails_with_no_alphabetic_characters(self):
        """Test email preprocessing with no alphabetic characters in local part."""
        # These emails have @ so they get processed, but local part has no letters
        test_cases = [
            ("123456@company.com", []),
            ("___@company.com", []),
            ("123.456@company.com", []),
            ("@company.com", []),  # Empty local part
        ]

        for email, expected in test_cases:
            test_record = {"email": email}
            processed = self.dataspot._preprocess_value("email", email, test_record)
            assert processed == expected, f"Failed for email: {email}"

        # When email preprocessing returns empty lists, no paths are generated at all
        # So we need at least one field that generates non-empty values
        numeric_emails = [
            {"email": "123456@company.com", "type": "numeric"},
            {
                "email": "valid@company.com",
                "type": "mixed",
            },  # This will generate patterns
        ]

        patterns = self.dataspot.find(numeric_emails, ["email", "type"])
        assert len(patterns) > 0

        # Should find patterns for valid email
        valid_email_patterns = [p for p in patterns if "email=valid" in p.path]
        assert len(valid_email_patterns) > 0

        # Should find type patterns
        type_patterns = [p for p in patterns if "type=" in p.path]
        assert len(type_patterns) > 0

    def test_malformed_emails_no_at_symbol(self):
        """Test emails without @ symbol (not processed as emails)."""
        test_cases = [
            ("no_at_symbol", "no_at_symbol"),
            ("", ""),
            ("user.name", "user.name"),
        ]

        for email, expected in test_cases:
            test_record = {"email": email}
            processed = self.dataspot._preprocess_value("email", email, test_record)
            assert processed == expected, f"Failed for malformed email: {email}"

    def test_email_pattern_field(self):
        """Test email preprocessing with email_pattern field."""
        email_pattern_data = [
            {"email_pattern": "test.user@domain.com", "type": "test"},
            {"email_pattern": "admin.support@domain.com", "type": "admin"},
        ]

        patterns = self.dataspot.find(email_pattern_data, ["email_pattern", "type"])
        assert len(patterns) > 0

        # Should process email_pattern field the same way as email field
        email_patterns = [p for p in patterns if "email_pattern=" in p.path]
        assert len(email_patterns) > 0

    def test_email_field_priority(self):
        """Test that 'email' field takes precedence for email_pattern preprocessing."""
        test_record = {
            "email": "real.email@domain.com",
            "email_pattern": "fake.pattern@domain.com",
        }

        # When processing email_pattern field but email field exists, use email field
        processed = self.dataspot._preprocess_value(
            "email_pattern", "fake.pattern@domain.com", test_record
        )

        # Should use the 'email' field value instead
        expected = ["real", "email"]  # From real.email@domain.com
        assert processed == expected

    def test_special_characters_in_emails(self):
        """Test emails with special characters."""
        test_cases = [
            ("user+tag@domain.com", ["user", "tag"]),
            ("john.doe+newsletter@domain.com", ["john", "doe", "newsletter"]),
            ("user..double.dot@domain.com", ["user", "double", "dot"]),
            ("user--double.dash@domain.com", ["user", "double", "dash"]),
            (".user.name@domain.com", ["user", "name"]),  # Leading dot
            ("user.name.@domain.com", ["user", "name"]),  # Trailing dot
        ]

        for email, expected in test_cases:
            test_record = {"email": email}
            processed = self.dataspot._preprocess_value("email", email, test_record)
            assert processed == expected, f"Failed for email: {email}"

    def test_unicode_emails(self):
        """Test email preprocessing with Unicode characters."""
        # Note: The regex [a-zA-Z]+ extracts ASCII parts from Unicode characters
        test_cases = [
            ("josé.garcía@empresa.com", ["jos", "garc", "a"]),  # ASCII parts extracted
            ("francois.dubois@société.fr", ["francois", "dubois"]),  # Pure ASCII works
            ("test.müller@firma.de", ["test", "m", "ller"]),  # ASCII parts extracted
        ]

        for email, expected in test_cases:
            test_record = {"email": email}
            processed = self.dataspot._preprocess_value("email", email, test_record)
            assert processed == expected, f"Failed for Unicode email: {email}"

    def test_non_email_fields_not_processed(self):
        """Test that non-email fields are not preprocessed as emails."""
        test_record = {"text": "user@domain.com"}
        processed = self.dataspot._preprocess_value(
            "text", "user@domain.com", test_record
        )

        # Should return the value as-is, not preprocessed as email
        assert processed == "user@domain.com"

    def test_custom_preprocessor_override(self):
        """Test that custom preprocessors override email preprocessing."""

        def custom_email_processor(value):
            return f"custom_{value}"

        self.dataspot.add_preprocessor("email", custom_email_processor)

        test_record = {"email": "test@domain.com"}
        processed = self.dataspot._preprocess_value(
            "email", "test@domain.com", test_record
        )

        # Should use custom preprocessor instead of email preprocessing
        assert processed == "custom_test@domain.com"

    def test_none_and_non_string_values(self):
        """Test email preprocessing with None and non-string values."""
        test_cases = [
            (None, ""),  # None becomes empty string
            (123, 123),  # Numbers returned as-is
            ([], []),  # Lists returned as-is
            ({}, {}),  # Dicts returned as-is
        ]

        for value, expected in test_cases:
            test_record = {"email": value}
            processed = self.dataspot._preprocess_value("email", value, test_record)
            assert processed == expected, f"Failed for value: {value}"


class TestEmailFieldConfiguration:
    """Test cases for email field configuration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_default_email_fields(self):
        """Test that default email fields are correctly configured."""
        expected_defaults = ["email", "email_pattern"]
        assert set(self.dataspot.email_patterns) == set(expected_defaults)

    def test_modify_email_fields(self):
        """Test modifying email field configuration."""
        # Add custom email field
        self.dataspot.email_patterns.append("contact_email")

        test_record = {"contact_email": "contact.support@domain.com"}
        processed = self.dataspot._preprocess_value(
            "contact_email", "contact.support@domain.com", test_record
        )

        # Should apply email preprocessing to custom field
        assert processed == ["contact", "support"]

    def test_remove_email_field(self):
        """Test removing email field from configuration."""
        # Remove 'email' from email patterns
        self.dataspot.email_patterns = ["email_pattern"]  # Remove 'email'

        test_record = {"email": "test.user@domain.com"}
        processed = self.dataspot._preprocess_value(
            "email", "test.user@domain.com", test_record
        )

        # Should NOT apply email preprocessing
        assert processed == "test.user@domain.com"

    def test_empty_email_fields_list(self):
        """Test behavior with empty email fields list."""
        # Clear all email patterns
        self.dataspot.email_patterns = []

        test_record = {"email": "test.user@domain.com"}
        processed = self.dataspot._preprocess_value(
            "email", "test.user@domain.com", test_record
        )

        # Should NOT apply email preprocessing
        assert processed == "test.user@domain.com"


class TestEmailIntegrationWithPatterns:
    """Test cases for email preprocessing integration with pattern detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_email_list_expansion_in_patterns(self):
        """Test how email preprocessing creates multiple paths."""
        email_data = [
            {
                "email": "john.doe@company.com",
                "department": "tech",
            },  # Creates 2 email paths
            {"email": "admin@company.com", "department": "ops"},  # Creates 1 email path
        ]

        patterns = self.dataspot.find(email_data, ["email", "department"])
        assert len(patterns) > 0

        # Should find patterns for individual email parts
        john_patterns = [p for p in patterns if "email=john" in p.path]
        assert len(john_patterns) > 0

        doe_patterns = [p for p in patterns if "email=doe" in p.path]
        assert len(doe_patterns) > 0

        admin_patterns = [p for p in patterns if "email=admin" in p.path]
        assert len(admin_patterns) > 0

    def test_email_with_pattern_filtering(self):
        """Test email preprocessing with pattern filtering."""
        # Create data where some emails appear frequently
        email_data = []
        for i in range(10):
            email_data.append(
                {
                    "email": "admin@company.com" if i < 7 else "user@company.com",
                    "type": "test",
                }
            )

        patterns = self.dataspot.find(email_data, ["email", "type"], min_percentage=50)

        # Should find high-percentage patterns
        admin_patterns = [
            p for p in patterns if "email=admin" in p.path and p.percentage >= 50
        ]
        assert len(admin_patterns) > 0

    def test_performance_with_many_emails(self):
        """Test performance with many email records."""
        large_data = []
        for i in range(100):
            large_data.append(
                {"email": f"user{i % 10}.test@domain.com", "category": f"cat_{i % 5}"}
            )

        patterns = self.dataspot.find(large_data, ["email", "category"])

        # Should complete efficiently and find patterns
        assert len(patterns) > 0
        assert isinstance(patterns, list)
