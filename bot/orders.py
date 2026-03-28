"""Order placement functions.

This module provides high-level functions to place market, limit, and
stop-limit orders using a provided BinanceClient instance. It handles
formatting and output reporting for the order execution results.
"""

import logging
import time
from typing import Any, Dict, Optional

from bot.client import BinanceClient
from bot.validators import validate_order_params

logger = logging.getLogger("trading_bot.orders")


def report_order_result(order_type: str, result: Dict[str, Any]) -> None:
    """Prints a professional summary of the order execution result.

    Args:
        order_type: The execution type string (e.g., 'MARKET', 'LIMIT').
        result: The API response dictionary of the successful order.
    """
    print(f"\n[ORDER PLACED] {order_type} execution confirmed.")
    print("-" * 35)
    print(f"ID:           {result.get('orderId', 'N/A')}")
    print(f"Symbol:       {result.get('symbol', 'N/A')}")
    print(f"Side:         {result.get('side', 'N/A')}")
    print(f"Quantity:     {result.get('executedQty', result.get('origQty', '0.0'))}")
    print(f"Price:        {result.get('avgPrice', result.get('price', '0.0'))} USDT")
    print(f"Time:         {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    print("-" * 35)


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> Dict[str, Any]:
    """Places a market order on the exchange.

    Args:
        client: The initialized BinanceClient instance.
        symbol: The trading pair symbol (e.g., 'BTCUSDT').
        side: The order side ('BUY' or 'SELL').
        quantity: The quantity to trade.

    Returns:
        The API response for the placed order.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="MARKET",
        quantity=quantity,
    )

    result = client.place_order(
        symbol=params["symbol"],
        side=params["side"],
        type=params["order_type"],
        quantity=params["quantity"],
    )

    report_order_result("MARKET", result)
    return result


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """Places a limit order on the exchange.

    Args:
        client: The initialized BinanceClient instance.
        symbol: The trading pair symbol.
        side: The order side.
        quantity: The quantity to trade.
        price: The limit price as a float.
        time_in_force: The time-in-force strategy ('GTC', 'IOC', 'FOK').

    Returns:
        The API response for the placed order.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="LIMIT",
        quantity=quantity,
        price=price,
        time_in_force=time_in_force,
    )

    result = client.place_order(
        symbol=params["symbol"],
        side=params["side"],
        type=params["order_type"],
        quantity=params["quantity"],
        price=params["price"],
        timeInForce=params["time_in_force"],
    )

    report_order_result("LIMIT", result)
    return result


def place_stop_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """Places a stop-limit order on the exchange.

    Args:
        client: The initialized BinanceClient instance.
        symbol: The trading pair symbol.
        side: The order side.
        quantity: The quantity to trade.
        price: The limit price to execute at after trigger.
        stop_price: The trigger price (stop price).
        time_in_force: The time-in-force strategy.

    Returns:
        The API response for the placed order.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="STOP_LIMIT",
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        time_in_force=time_in_force,
    )

    result = client.place_order(
        symbol=params["symbol"],
        side=params["side"],
        type=params["order_type"],
        quantity=params["quantity"],
        price=params["price"],
        stopPrice=params["stop_price"],
        timeInForce=params["time_in_force"],
    )

    report_order_result("STOP-LIMIT", result)
    return result
