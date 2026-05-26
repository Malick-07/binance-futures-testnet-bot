from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(Exception):
    """Raised when CLI input is invalid."""


@dataclass(frozen=True)
class OrderInput:
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal | None = None
    time_in_force: str = "GTC"


def validate_order_input(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None,
    time_in_force: str,
) -> OrderInput:
    normalized_symbol = symbol.strip().upper()
    normalized_side = side.strip().upper()
    normalized_order_type = order_type.strip().upper()
    normalized_time_in_force = time_in_force.strip().upper()

    if not normalized_symbol:
        raise ValidationError("symbol is required")
    if not normalized_symbol.isalnum():
        raise ValidationError("symbol must contain only letters and numbers")
    if normalized_side not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL")
    if normalized_order_type not in VALID_ORDER_TYPES:
        raise ValidationError("type must be MARKET or LIMIT")

    parsed_quantity = _positive_decimal(quantity, "quantity")
    parsed_price = None

    if normalized_order_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders")
        parsed_price = _positive_decimal(price, "price")
    elif price is not None:
        raise ValidationError("price is only valid for LIMIT orders")

    return OrderInput(
        symbol=normalized_symbol,
        side=normalized_side,
        order_type=normalized_order_type,
        quantity=parsed_quantity,
        price=parsed_price,
        time_in_force=normalized_time_in_force,
    )


def _positive_decimal(raw_value: str, field_name: str) -> Decimal:
    try:
        value = Decimal(raw_value)
    except (InvalidOperation, TypeError) as exc:
        raise ValidationError(f"{field_name} must be a number") from exc

    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0")
    return value
