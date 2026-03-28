"""Binance Futures Testnet Client.

This module provides a professional-standard low-level HTTP client to interact
with the Binance Futures Testnet REST API. It handles clock synchronization,
HMAC-SHA256 request signing, and secure logging.
"""

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

# Binance Futures Testnet base configurations
BASE_URL = "https://testnet.binancefuture.com"
REQUEST_TIMEOUT = 15

# API Endpoint paths
ENDPOINTS = {
    "order": "/fapi/v1/order",
    "exchange_info": "/fapi/v1/exchangeInfo",
    "account": "/fapi/v2/account",
    "ticker_price": "/fapi/v1/ticker/price",
}


class BinanceAPIError(Exception):
    """Exception raised for errors returned from the Binance API.

    Attributes:
        status_code: The HTTP status code of the response.
        code: The error code returned in the API response.
        message: The descriptive error message from the API.
    """

    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(
            f"Binance API Error [{code}]: {message} (HTTP {status_code})"
        )


class BinanceClient:
    """A client for interacting with the Binance Futures Testnet API.

    Attributes:
        api_key: The API key for authentication.
        api_secret: The API secret for signing requests.
        base_url: The root URL for all API calls.
        mock: Whether to simulate API calls without network activity.
        time_offset: Synchronized difference between server and local clock.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = BASE_URL,
        mock: bool = False,
    ):
        """Initializes the Binance client.

        Args:
            api_key: The API key string.
            api_secret: The API secret string.
            base_url: The base URL for the exchange.
            mock: If True, simulate network actions with mock responses.

        Raises:
            ValueError: If credentials are missing and mock mode is False.
        """
        self.mock = mock
        if not self.mock and (not api_key or not api_secret):
            raise ValueError(
                "API credentials are required unless in mock mode."
            )

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

        # Initialize session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key if not self.mock else "MOCK_KEY",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

        self.time_offset = 0
        if not self.mock:
            try:
                self.time_offset = self._calculate_time_offset()
                logger.info(
                    "Clock offset synchronized: %dms", self.time_offset
                )
            except Exception as e:
                logger.warning("Clock synchronization failed: %s", e)

        logger.info(
            "Client initialized (URL: %s, Mock: %s)",
            self.base_url,
            self.mock,
        )

    def _calculate_time_offset(self) -> int:
        """Calculates the difference between the server and the local clock.

        Returns:
            The offset in milliseconds (Server Time - Local Time).
        """
        response = self.session.get(
            f"{self.base_url}/fapi/v1/time", timeout=5
        )
        response.raise_for_status()
        server_time = response.json()["serverTime"]
        local_time = int(time.time() * 1000)
        return server_time - local_time

    def _get_timestamp(self) -> int:
        """Generates a synchronized timestamp for requests.

        Returns:
            The current synchronized timestamp in milliseconds.
        """
        return int(time.time() * 1000) + self.time_offset

    def _generate_signature(self, query_string: str) -> str:
        """Signs a query string using HMAC-SHA256.

        Args:
            query_string: The string to be signed.

        Returns:
            The HMAC-SHA256 hex digest of the signature.
        """
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _signed_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Makes a signed request to a private API endpoint.

        Args:
            method: The HTTP method (GET/POST/DELETE).
            endpoint: The API endpoint path.
            params: The parameters to be included in the request.

        Returns:
            The JSON-parsed response dictionary.

        Raises:
            BinanceAPIError: If the API returns a non-200 status code.
        """
        if params is None:
            params = {}

        params["timestamp"] = self._get_timestamp()

        # Build query string in consistent alphabetical order for signing
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])

        signature = self._generate_signature(query_string)
        payload = f"{query_string}&signature={signature}"

        url = f"{self.base_url}{endpoint}"

        # Mask signatures in logs for security
        masked_payload = f"{query_string}&signature=[MASKED]"
        logger.debug("Request: %s %s | Payload: %s", method, endpoint, masked_payload)

        try:
            # For futures testnet, appending parameters to URL is recommended
            request_url = f"{url}?{payload}"
            response = self.session.request(
                method=method,
                url=request_url,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as e:
            logger.error("Network communication error: %s", e)
            raise

        logger.debug("Response: HTTP %d", response.status_code)

        if response.status_code != 200:
            try:
                err = response.json()
                raise BinanceAPIError(
                    status_code=response.status_code,
                    code=err.get("code", -1),
                    message=err.get("msg", "Unknown API error"),
                )
            except ValueError:
                response.raise_for_status()

        return response.json()

    def get_exchange_info(self) -> Dict[str, Any]:
        """Retrieves exchange trading rules and symbol details.

        Returns:
            Dictionary containing symbols and their trading filters.
        """
        url = f"{self.base_url}{ENDPOINTS['exchange_info']}"
        response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get_account(self) -> Dict[str, Any]:
        """Retrieves account balance and status.

        Returns:
            Dictionary with account details (balances, assets).
        """
        if self.mock:
            return {
                "accountAlias": "MOCK_USER",
                "totalWalletBalance": "1000.00",
                "availableBalance": "1000.00",
            }
        return self._signed_request("GET", ENDPOINTS["account"])

    def place_order(self, **params: Any) -> Dict[str, Any]:
        """Submits a new order to the exchange.

        Returns:
            The order response received from the API.
        """
        if self.mock:
            logger.info("Simulation: Order processed successfully.")
            return {
                "orderId": 12345678,
                "symbol": params.get("symbol", "N/A"),
                "status": "FILLED",
                "executedQty": params.get("quantity", "0.0"),
                "avgPrice": params.get("price") or "95000.0",
                "type": params.get("type", "MARKET"),
                "side": params.get("side", "BUY"),
                "updateTime": int(time.time() * 1000),
            }

        logger.info(
            "Submitting order: %s %s %s",
            params.get("type"),
            params.get("side"),
            params.get("symbol"),
        )
        return self._signed_request("POST", ENDPOINTS["order"], params)
