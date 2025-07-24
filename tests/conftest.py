"""Pytest configuration and fixtures for dataspot tests."""

import json
import os
from typing import Any, Dict, List

import pytest


@pytest.fixture
def fake_transactions_data() -> List[Dict[str, Any]]:
    """Load fake transaction data from database.json.

    Returns:
        List of fake transaction dictionaries for testing.

    """
    data_file = os.path.join(os.path.dirname(__file__), "data/transactions.json")
    with open(data_file, "r") as f:
        return json.load(f)


@pytest.fixture
def identical_dataset_small(fake_transactions_data) -> List[Dict[str, Any]]:
    """Get a small dataset for identical comparison tests.

    Args:
        fake_transactions_data: The fake transaction data fixture.

    Returns:
        All fake transactions for identical comparison.

    """
    return fake_transactions_data.copy()


@pytest.fixture
def baseline_dataset_small(fake_transactions_data) -> List[Dict[str, Any]]:
    """Get baseline dataset for comparison tests.

    Args:
        fake_transactions_data: The fake transaction data fixture.

    Returns:
        First 3 transactions as baseline data.

    """
    return fake_transactions_data[:3].copy()


@pytest.fixture
def modified_current_dataset(fake_transactions_data) -> List[Dict[str, Any]]:
    """Get modified current dataset for comparison tests.

    Args:
        fake_transactions_data: The fake transaction data fixture.

    Returns:
        Last 3 transactions with modifications to guarantee differences.

    """
    current_data = fake_transactions_data[2:5].copy()

    current_data[0]["brand"] = "mastercard"
    current_data[1]["currency"] = "jpy"
    current_data[2]["status"] = "failed"

    current_data[0]["amount"] = 999.0
    current_data[1]["amount"] = 1000.0
    current_data[2]["amount"] = 1000.0

    return current_data


@pytest.fixture
def compare_fields() -> List[str]:
    """Define fields for comparison tests.

    Returns:
        List of field names commonly used in comparison tests.

    """
    return ["brand", "currency", "status", "amount"]


@pytest.fixture
def sample_transaction() -> Dict[str, Any]:
    """Get a single sample transaction for unit tests.

    Returns:
        A single fake transaction record.

    """
    return {
        "amount": 100.0,
        "brand": "visa",
        "currency": "usd",
        "status": "paid",
        "id": 1,
        "full_name": "John Doe",
        "email": "john.doe@example.com",
    }


@pytest.fixture
def diverse_transaction_data() -> List[Dict[str, Any]]:
    """Get diverse transaction data for pattern discovery tests.

    Returns:
        List of transactions with diverse patterns for testing pattern discovery.

    """
    return [
        {"country": "US", "payment_method": "card", "risk_level": "low"},
        {"country": "US", "payment_method": "card", "risk_level": "low"},
        {"country": "UK", "payment_method": "bank", "risk_level": "medium"},
        {"country": "FR", "payment_method": "crypto", "risk_level": "high"},
        {"country": "FR", "payment_method": "crypto", "risk_level": "high"},
    ]
