"""Tests for email preprocessing functionality in Dataspot.

This module tests the email pattern extraction and preprocessing capabilities,
including edge cases and various email formats.
"""

from dataspot import Dataspot
from dataspot.analyzers.base import Base
from dataspot.models.finder import FindInput, FindOptions


class TestEmailPreprocessing:
    """Test cases for email preprocessing functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataspot = Dataspot()
        self.base = Base()

    def test_basic_email_extraction(self):
        """Test basic email extraction from records."""
        test_data = [
            {"user": "john@example.com", "category": "A"},
            {"user": "jane@company.org", "category": "B"},
            {"user": "mike@example.com", "category": "A"},
        ]

        find_input = FindInput(data=test_data, fields=["user", "category"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should find email domain patterns
        email_patterns = [p for p in result.patterns if "@" in p.path]
        assert len(email_patterns) > 0

        # Should extract domain information
        domain_patterns = [p for p in result.patterns if "example.com" in p.path]
        assert len(domain_patterns) > 0

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
            processed = self.base._preprocess_value("email", email, test_record)
            assert processed == expected, f"Failed for email: {email}"

    def test_emails_with_no_alphabetic_characters(self):
        """Test handling of emails with numeric domains or special characters."""
        test_data = [
            {"email": "user@123.com", "type": "numeric"},
            {"email": "admin@test-site.org", "type": "hyphen"},
            {"email": "support@test.co.uk", "type": "multi"},
        ]

        find_input = FindInput(data=test_data, fields=["email", "type"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle special domain formats and extract alphabetic parts
        assert len(result.patterns) > 0

        # Should find patterns with extracted alphabetic parts (not @ symbol)
        # Since email preprocessing extracts only alphabetic parts from local part
        email_patterns = [p for p in result.patterns if "email=" in p.path]
        assert len(email_patterns) > 0

        # Should find specific extracted terms
        user_patterns = [p for p in result.patterns if "email=user" in p.path]
        admin_patterns = [p for p in result.patterns if "email=admin" in p.path]
        support_patterns = [p for p in result.patterns if "email=support" in p.path]

        assert len(user_patterns) > 0
        assert len(admin_patterns) > 0
        assert len(support_patterns) > 0

    def test_malformed_emails_no_at_symbol(self):
        """Test emails without @ symbol (not processed as emails)."""
        test_cases = [
            ("no_at_symbol", "no_at_symbol"),
            ("", ""),
            ("user.name", "user.name"),
        ]

        for email, expected in test_cases:
            test_record = {"email": email}
            processed = self.base._preprocess_value("email", email, test_record)
            assert processed == expected, f"Failed for malformed email: {email}"

    def test_email_pattern_field(self):
        """Test email preprocessing creates appropriate pattern fields."""
        test_data = [
            {"contact": "sales@company.com", "role": "sales"},
            {"contact": "support@company.com", "role": "support"},
            {"contact": "info@partner.org", "role": "info"},
        ]

        find_input = FindInput(data=test_data, fields=["contact", "role"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should find domain-based patterns
        company_patterns = [p for p in result.patterns if "company.com" in p.path]
        assert len(company_patterns) > 0

        # Should categorize by domain
        domain_concentration = len(
            [p for p in result.patterns if "company.com" in p.path]
        )
        assert domain_concentration > 0

    def test_email_field_priority(self):
        """Test that 'email' field takes precedence for email_pattern preprocessing."""
        test_record = {
            "email": "real.email@domain.com",
            "email_pattern": "fake.pattern@domain.com",
        }

        # When processing email_pattern field but email field exists, use email field
        processed = self.base._preprocess_value(
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
            processed = self.base._preprocess_value("email", email, test_record)
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
            processed = self.base._preprocess_value("email", email, test_record)
            assert processed == expected, f"Failed for Unicode email: {email}"

    def test_non_email_fields_not_processed(self):
        """Test that non-email fields are not preprocessed as emails."""
        test_record = {"text": "user@domain.com"}
        processed = self.base._preprocess_value("text", "user@domain.com", test_record)

        # Should return the value as-is, not preprocessed as email
        assert processed == "user@domain.com"

    def test_custom_preprocessor_override(self):
        """Test that custom preprocessors override email preprocessing."""

        def custom_email_processor(value):
            return f"custom_{value}"

        self.base.add_preprocessor("email", custom_email_processor)

        test_record = {"email": "test@domain.com"}
        processed = self.base._preprocess_value("email", "test@domain.com", test_record)

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
            processed = self.base._preprocess_value("email", value, test_record)
            assert processed == expected, f"Failed for value: {value}"


class TestEmailPreprocessorConfiguration:
    """Test cases for email preprocessor configuration using the new API."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.base = Base()

    def test_default_email_preprocessing(self):
        """Test that default email fields are correctly preprocessed."""
        # Test that 'email' field gets preprocessed by default
        test_record = {"email": "test.user@domain.com"}
        processed = self.base._preprocess_value(
            "email", "test.user@domain.com", test_record
        )
        assert processed == ["test", "user"]

        # Test that 'email_pattern' field gets preprocessed by default
        test_record = {"email_pattern": "admin.support@domain.com"}
        processed = self.base._preprocess_value(
            "email_pattern", "admin.support@domain.com", test_record
        )
        assert processed == ["admin", "support"]

    def test_add_custom_email_field(self):
        """Test adding custom email field using preprocessor API."""
        from dataspot.analyzers.preprocessors import email_preprocessor

        # Add custom email field using the preprocessor API
        self.base.add_preprocessor("contact_email", email_preprocessor)

        test_record = {"contact_email": "contact.support@domain.com"}
        processed = self.base._preprocess_value(
            "contact_email", "contact.support@domain.com", test_record
        )

        # Should apply email preprocessing to custom field
        assert processed == ["contact", "support"]

    def test_override_default_email_field(self):
        """Test overriding default email field behavior."""

        # Override the default email preprocessor with a custom one
        def custom_email_processor(value):
            return f"custom_{value}"

        self.base.add_preprocessor("email", custom_email_processor)

        test_record = {"email": "test.user@domain.com"}
        processed = self.base._preprocess_value(
            "email", "test.user@domain.com", test_record
        )

        # Should use custom preprocessor instead of default email preprocessing
        assert processed == "custom_test.user@domain.com"

    def test_non_email_field_not_preprocessed(self):
        """Test that fields without email preprocessor are not processed as emails."""
        # Custom field without email preprocessor should not be processed as email
        test_record = {"custom_field": "test.user@domain.com"}
        processed = self.base._preprocess_value(
            "custom_field", "test.user@domain.com", test_record
        )

        # Should NOT apply email preprocessing
        assert processed == "test.user@domain.com"


class TestEmailIntegrationWithPatterns:
    """Test cases for email preprocessing integration with pattern detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_email_list_expansion_in_patterns(self):
        """Test that email lists are properly expanded in pattern detection."""
        test_data = [
            {
                "recipients": ["john@company.com", "jane@company.com"],
                "department": "sales",
            },
            {
                "recipients": ["mike@company.com", "sarah@partner.org"],
                "department": "marketing",
            },
        ]

        find_input = FindInput(data=test_data, fields=["recipients", "department"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should expand email lists and find domain patterns
        company_patterns = [p for p in result.patterns if "company.com" in p.path]
        assert len(company_patterns) > 0

    def test_email_with_pattern_filtering(self):
        """Test email analysis with pattern filtering options."""
        test_data = [
            {"sender": "user1@domain1.com", "status": "sent"},
            {"sender": "user2@domain1.com", "status": "sent"},
            {"sender": "user3@domain2.com", "status": "failed"},
        ] * 10  # Scale up for percentage calculations

        find_input = FindInput(data=test_data, fields=["sender", "status"])
        find_options = FindOptions(min_percentage=20.0)
        result = self.dataspot.find(find_input, find_options)

        # Should filter out low-concentration patterns
        for pattern in result.patterns:
            assert pattern.percentage >= 20.0

    def test_performance_with_many_emails(self):
        """Test performance with large number of email addresses."""
        # Generate large dataset with emails
        test_data = []
        for i in range(1000):
            test_data.append(
                {
                    "email": f"user{i}@domain{i % 10}.com",
                    "category": f"cat_{i % 5}",
                }
            )

        find_input = FindInput(data=test_data, fields=["email", "category"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should complete efficiently
        assert len(result.patterns) > 0
        assert result.total_records == 1000
