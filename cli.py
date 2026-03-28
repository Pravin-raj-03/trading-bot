#!/usr/bin/env python3
"""Trading Bot Command-Line Interface.

This module provides the main entry point for the Binance Futures Testnet
Trading Bot terminal application. It allows users to check account status,
verify credentials, and submit market, limit, or stop-limit orders.
"""

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging
from bot.orders import (
    place_market_order,
    place_limit_order,
    place_stop_limit_order,
)
from bot.validators import ValidationError


def create_parser() -> argparse.ArgumentParser:
    """Configures the command-line argument parser.

    Returns:
        An configured ArgumentParser instance for the trading bot.
    """
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Binance Futures Trading Bot terminal application.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  %(prog)s --mock check
  %(prog)s order BTCUSDT BUY MARKET 0.001
  %(prog)s order ETHUSDT SELL LIMIT 0.01 --price 3500
        """,
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in simulation mode (no network activity).",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: check
    subparsers.add_parser(
        "check",
        help="Check account status and credentials.",
    )

    # Command: order
    order_parser = subparsers.add_parser(
        "order",
        help="Place a new order on the exchange.",
    )

    order_parser.add_argument(
        "symbol",
        type=str,
        help="Trading pair symbol (e.g., BTCUSDT).",
    )
    order_parser.add_argument(
        "side",
        type=str,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order execution side.",
    )
    order_parser.add_argument(
        "order_type",
        type=str,
        choices=[
            "MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"
        ],
        help="Execution strategy type.",
    )
    order_parser.add_argument(
        "quantity",
        type=float,
        help="Order execution quantity.",
    )
    order_parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Limit execution price.",
    )
    order_parser.add_argument(
        "--stop-price",
        type=float,
        default=None,
        dest="stop_price",
        help="Order trigger price (stop price).",
    )
    order_parser.add_argument(
        "--time-in-force",
        type=str,
        default="GTC",
        choices=["GTC", "IOC", "FOK"],
        dest="time_in_force",
        help="Time-in-force policy (default: GTC).",
    )

    return parser


def initialize_client(mock: bool = False) -> BinanceClient:
    """Creates a BinanceClient instance using environment credentials.

    Args:
        mock: If True, uses simulation mode.

    Returns:
        The initialized BinanceClient instance.

    Raises:
        SystemExit: If credentials are missing in non-mock mode.
    """
    if mock:
        return BinanceClient(
            api_key="MOCK_EY", api_secret="MOCK_SECRET", mock=True
        )

    load_dotenv()
    api_key = os.getenv("BINANCE_TESTNET_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print("\n[ERROR] API credentials not found.")
        print("Please configure your .env file with:")
        print("  BINANCE_TESTNET_API_KEY=your_key")
        print("  BINANCE_TESTNET_API_SECRET=your_secret")
        print("\nAlternatively, run in mock mode: python cli.py --mock check\n")
        sys.exit(1)

    # Validate credential length
    if len(api_key) < 32 or len(api_secret) < 32:
        print("\n[ERROR] Provided API key or secret format is invalid.")
        sys.exit(1)

    return BinanceClient(api_key=api_key, api_secret=api_secret)


def handle_check(args: argparse.Namespace) -> None:
    """Executes the status check logic.

    Args:
        args: Command-line arguments.
    """
    logger = setup_logging()
    client = initialize_client(mock=args.mock)

    prefix = "(MOCK) " if args.mock else ""
    try:
        account = client.get_account()
        print(f"\n[INFO] {prefix}Account Connectivity Verified")
        print(f"Alias:      {account.get('accountAlias', 'N/A')}")
        print(f"Balance:    {account.get('totalWalletBalance', 'N/A')} USDT")
        logger.info("Credentials check successful.")
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}\n")
        logger.error("Credential check failed: %s", e)


def handle_order(args: argparse.Namespace) -> None:
    """Executes the order placement logic based on subcommand arguments.

    Args:
        args: Command-line arguments.
    """
    logger = setup_logging()
    client = initialize_client(mock=args.mock)

    otype = args.order_type.upper()
    sym = args.symbol.upper()
    sd = args.side.upper()

    try:
        if otype == "MARKET":
            place_market_order(client, sym, sd, args.quantity)

        elif otype == "LIMIT":
            if args.price is None:
                print("\n[ERROR] --price is mandatory for LIMIT orders.\n")
                sys.exit(1)
            place_limit_order(
                client, sym, sd, args.quantity, args.price, args.time_in_force
            )

        elif otype == "STOP_LIMIT":
            if args.price is None or args.stop_price is None:
                print(
                    "\n[ERROR] --price and --stop-price are mandatory for "
                    "STOP_LIMIT.\n"
                )
                sys.exit(1)
            place_stop_limit_order(
                client,
                sym,
                sd,
                args.quantity,
                args.price,
                args.stop_price,
                args.time_in_force,
            )

    except ValidationError as e:
        print(f"\n[VALIDATION ERROR] {e}\n")
        logger.error("Order submission failed validation: %s", e)
        sys.exit(1)

    except BinanceAPIError as e:
        print(f"\n[EXCHANGE ERROR] {e}\n")
        logger.error("API call failed: %s", e)
        sys.exit(1)

    except Exception as e:
        print(f"\n[SYSTEM ERROR] {e}\n")
        logger.exception("Unexpected operational failure.")
        sys.exit(1)


def main() -> None:
    """Main application loop."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "check":
        handle_check(args)
    elif args.command == "order":
        handle_order(args)


if __name__ == "__main__":
    main()
