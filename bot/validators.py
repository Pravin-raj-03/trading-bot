"""Input validation for Binance Futures orders.

This module provides utility functions to validate and normalize parameters
for market, limit, and stop-limit orders on the Binance Futures Testnet.
All functions raise a ValidationError if the input does not meet the
required criteria.
"""

import re
from typing import Any, Dict, Optional


class ValidationError(Exception):
    """Specific error raised when order parameters fail validation."""
    pass


def validate_symbol(symbol: str) -> str:
    """Validates the trading pair symbol format.

    Args:
        symbol: The trading pair string (e.g., 'BTCUSDT').

    Returns:
        The normalized (uppercase and stripped) symbol string.

    Raises:
        ValidationError: If the symbol is empty or not in the correct format.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValidationError("Symbol is required and must be a non-empty string.")

    symbol = symbol.upper().strip()
    if not re.match(r"^[A-Z]{2,20}$", symbol):
        raise ValidationError(
            f"'{symbol}' is not a valid symbol format. Use 2-20 uppercase "
            "letters (e.g., BTCUSDT)."
        )

    return symbol


def validate_side(side: str) -> str:
    """Validates the order side.

    Args:
        side: The order side string ('BUY' or 'SELL').

    Returns:
        The normalized (uppercase and stripped) side string.

    Raises:
        ValidationError: If the side is not 'BUY' or 'SELL'.
    """
    if not isinstance(side, str):
        raise ValidationError("Order side is required.")

    side = side.upper().strip()
    if side not in ("BUY", "SELL"):
        raise ValidationError(
            f"Invalid side '{side}'. Must be either 'BUY' or 'SELL'."
        )

    return side


def validate_order_type(order_type: str) -> str:
    """Validates the order execution type.

    Args:
        order_type: The type string (e.g., 'MARKET', 'LIMIT', 'STOP_LIMIT').

    Returns:
        The normalized order type string.

    Raises:
        ValidationError: If the order type is not supported.
    """
    if not isinstance(order_type, str):
        raise ValidationError("Order type is required.")

    order_type = order_type.upper().strip().replace("-", "_")
    if order_type not in ("MARKET", "LIMIT", "STOP_LIMIT"):
        raise ValidationError(
            f"Unsupported order type '{order_type}'. Use MARKET, LIMIT, "
            "or STOP_LIMIT."
        )

    return order_type


def validate_quantity(quantity: Any) -> float:
    """Validates and converts the order quantity.

    Args:
        quantity: The quantity value (string, int, or float).

    Returns:
        The validated quantity as a float.

    Raises:
        ValidationError: If the quantity is not a positive number.
    """
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(
            f"Invalid quantity '{quantity}'. Please provide a numeric value."
        )

    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than zero. Got: {qty}")

    return qty


def validate_price(price: Optional[Any], required: bool = False) -> Optional[float]:
    """Validates and converts the order price.

    Args:
        price: The price value (string, int, or float).
        required: Whether the price is mandatory for the current order type.

    Returns:
        The validated price as a float, or None if not provided and not required.

    Raises:
        ValidationError: If the price is required but missing, or not a positive number.
    """
    if price is None:
        if required:
            raise ValidationError("A price is required for this order type.")
        return None

    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(
            f"Invalid price '{price}'. Please provide a numeric value."
        )

    if p <= 0:
        raise ValidationError(f"Price must be greater than zero. Got: {p}")

    return p


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Any,
    price: Optional[Any] = None,
    stop_price: Optional[Any] = None,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """Validates and normalizes all parameters for an order request.

    Args:
        symbol: The trading pair symbol.
        side: The order side (BUY/SELL).
        order_type: The order type (MARKET/LIMIT/STOP_LIMIT).
        quantity: The order quantity.
        price: The limit price (required for LIMIT/STOP_LIMIT).
        stop_price: The trigger price (required for STOP_LIMIT).
        time_in_force: The time-in-force policy (default: GTC).

    Returns:
        A dictionary containing the validated and cleaned order parameters.

    Raises:
        ValidationError: If any of the provided parameters fail validation.
    """
    cleaned_type = validate_order_type(order_type)

    requires_price = cleaned_type in ("LIMIT", "STOP_LIMIT")
    requires_stop = cleaned_type == "STOP_LIMIT"

    params = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": cleaned_type,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, required=requires_price),
        "stop_price": validate_price(stop_price, required=requires_stop),
    }

    if requires_price:
        tif = time_in_force.upper().strip()
        if tif not in ("GTC", "IOC", "FOK"):
            raise ValidationError(
                f"Invalid time-in-force '{tif}'. Use GTC, IOC, or FOK."
            )
        params["time_in_force"] = tif

    return params
