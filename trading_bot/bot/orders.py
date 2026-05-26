from __future__ import annotations

import logging
from typing import Any, Protocol

from trading_bot.bot.validators import OrderInput


LOGGER = logging.getLogger(__name__)


class OrderClient(Protocol):
    def place_order(self, params: dict[str, Any]) -> dict[str, Any]:
        ...


class OrderService:
    def build_order_request(self, order: OrderInput) -> dict[str, str]:
        request = {
            "symbol": order.symbol,
            "side": order.side,
            "type": order.order_type,
            "quantity": str(order.quantity),
        }

        if order.order_type == "LIMIT":
            request["price"] = str(order.price)
            request["timeInForce"] = order.time_in_force

        return request

    def place_order(
        self, client: OrderClient, order: OrderInput
    ) -> dict[str, Any]:
        request = self.build_order_request(order)
        LOGGER.info(
            "Placing order symbol=%s side=%s type=%s quantity=%s",
            order.symbol,
            order.side,
            order.order_type,
            order.quantity,
        )
        return client.place_order(request)
