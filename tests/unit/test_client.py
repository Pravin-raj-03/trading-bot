"""Unit tests for the Binance API client.

This module provides test cases to verify the signing logic, mock response
handling, and error reporting of the BinanceClient class.
"""

import hmac
import hashlib
import pytest
from bot.client import BinanceClient, BinanceAPIError

@pytest.fixture
def mock_client():
    """Provides a BinanceClient instance initialized in mock mode."""
    return BinanceClient(
        api_key="TEST_API_KEY", api_secret="TEST_API_SECRET", mock=True
    )

def test_mock_client_initialization_state(mock_client):
    """Verify that mock client state is correctly set."""
    assert mock_client.mock is True
    assert mock_client.api_key == "TEST_API_KEY"

def test_mock_account_data_retrieval(mock_client):
    """Verify that get_account returns mock user data."""
    account = mock_client.get_account()
    assert account["accountAlias"] == "MOCK_USER"
    assert "totalWalletBalance" in account

def test_mock_order_placement_simulation(mock_client):
    """Verify that place_order returns a simulated successful order."""
    order = mock_client.place_order(
        symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.001
    )
    assert order["symbol"] == "BTCUSDT"
    assert order["status"] == "FILLED"
    assert order["orderId"] == 12345678

def test_hmac_signature_generation_accuracy(mock_client):
    """Verify that the internal signing logic matches standard HMAC-SHA256."""
    query_string = (
        "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1499827319559"
    )
    expected = hmac.new(
        "TEST_API_SECRET".encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    
    assert mock_client._generate_signature(query_string) == expected

def test_api_error_exception_formatting():
    """Verify that BinanceAPIError produces a clear, descriptive message."""
    error = BinanceAPIError(
        status_code=400, code=-1102, message="Mandatory parameter not sent."
    )
    assert "Binance API Error [-1102]" in str(error)
    assert "Mandatory parameter not sent" in str(error)
