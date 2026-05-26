from __future__ import annotations

import argparse
import logging
import os
import sys

from trading_bot.bot.client import BinanceClientError, BinanceFuturesClient
from trading_bot.bot.logging_config import configure_logging
from trading_bot.bot.orders import OrderService
from trading_bot.bot.validators import ValidationError, validate_order_input


LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET and LIMIT orders on Binance USDT-M Futures Testnet."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="Order side: BUY or SELL")
    parser.add_argument("--type", required=True, help="Order type: MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Positive order quantity")
    parser.add_argument("--price", help="Positive price, required for LIMIT orders")
    parser.add_argument(
        "--time-in-force",
        default="GTC",
        choices=["GTC", "IOC", "FOK"],
        help="Time in force for LIMIT orders. Default: GTC",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the order request without sending it.",
    )
    return parser


def print_request_summary(order_request: dict[str, str]) -> None:
    print("\nOrder Request Summary")
    print("---------------------")
    for key in ("symbol", "side", "type", "quantity", "price", "timeInForce"):
        if key in order_request:
            print(f"{key}: {order_request[key]}")


def print_order_response(response: dict[str, object]) -> None:
    print("\nOrder Response Details")
    print("----------------------")
    for key in ("orderId", "status", "executedQty", "avgPrice"):
        print(f"{key}: {response.get(key, 'N/A')}")


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        order_input = validate_order_input(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            time_in_force=args.time_in_force,
        )
    except ValidationError as exc:
        LOGGER.error("Validation failed: %s", exc)
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 2

    service = OrderService()
    order_request = service.build_order_request(order_input)
    print_request_summary(order_request)

    if args.dry_run:
        print("\nSuccess: dry run completed. No order was sent.")
        return 0

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        LOGGER.error("Configuration failed: missing Binance API credentials")
        print(
            "Configuration failed: set BINANCE_API_KEY and BINANCE_API_SECRET.",
            file=sys.stderr,
        )
        return 2

    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
        response = service.place_order(client, order_input)
    except BinanceClientError as exc:
        LOGGER.error("Order placement failed: %s", exc)
        print(f"\nFailure: order was not placed. {exc}", file=sys.stderr)
        return 1

    print_order_response(response)
    print("\nSuccess: order placed on Binance Futures Testnet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
