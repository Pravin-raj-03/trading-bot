"""Unit tests for order parameter validation logic.

This module provides test cases to verify the performance and accuracy
of the input validation functions defined in bot/validators.py.
"""

import pytest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_quantity,
    validate_price,
    ValidationError,
)

def test_validate_symbol_correct_normalization():
    """Verify that symbols are correctly uppercased and stripped."""
    assert validate_symbol("btcusdt") == "BTCUSDT"
    assert validate_symbol("ETHUSDT ") == "ETHUSDT"

def test_validate_symbol_rejection_criteria():
    """Verify that invalid symbol formats are correctly caught."""
    # Invalid character format
    with pytest.raises(ValidationError, match="not a valid symbol format"):
        validate_symbol("123")
    # Missing input
    with pytest.raises(ValidationError, match="Symbol is required"):
        validate_symbol("")

def test_validate_side_correct_normalization():
    """Verify that order side is correctly normalized to uppercase."""
    assert validate_side("buy") == "BUY"
    assert validate_side("SELL") == "SELL"

def test_validate_side_rejection_criteria():
    """Verify that unsupported order sides are rejected."""
    with pytest.raises(ValidationError, match="Invalid side"):
        validate_side("HOLD")

def test_validate_quantity_data_conversion():
    """Verify that quantities are converted to float accurately."""
    assert validate_quantity("0.001") == 0.001
    assert validate_quantity(1.5) == 1.5

def test_validate_quantity_rejection_criteria():
    """Verify that negative or non-numeric quantities are rejected."""
    # Negative quantity
    with pytest.raises(ValidationError, match="must be greater than zero"):
        validate_quantity("-1")
    # Non-numeric string
    with pytest.raises(ValidationError, match="Please provide a numeric value"):
        validate_quantity("abc")

def test_validate_price_optional_behavior():
    """Verify that prices are optional when appropriate."""
    assert validate_price("50000.5") == 50000.5
    assert validate_price(None, required=False) is None

def test_validate_price_rejection_criteria():
    """Verify that required prices and zero values are correctly handled."""
    # Required but missing
    with pytest.raises(ValidationError, match="A price is required"):
        validate_price(None, required=True)
    # Zero value
    with pytest.raises(ValidationError, match="Price must be greater than zero"):
        validate_price("0")
