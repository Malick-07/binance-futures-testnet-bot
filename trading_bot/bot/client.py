from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any
from urllib.parse import urlencode

import requests


LOGGER = logging.getLogger(__name__)


class BinanceClientError(Exception):
    """Raised when Binance API communication or response handling fails."""


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout: int = 10,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": api_key})

    def place_order(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._signed_request("POST", "/fapi/v1/order", params)

    def _signed_request(
        self, method: str, path: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        payload = dict(params)
        payload["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(payload, doseq=True)
        payload["signature"] = self._sign(query_string)

        safe_payload = self._sanitize_params(payload)
        LOGGER.info("API request method=%s path=%s params=%s", method, path, safe_payload)

        try:
            response = self.session.request(
                method=method,
                url=f"{self.base_url}{path}",
                params=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            LOGGER.exception("Network error while calling Binance API")
            raise BinanceClientError(f"network error: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            LOGGER.error(
                "Non-JSON API response status=%s body=%s",
                response.status_code,
                response.text,
            )
            raise BinanceClientError("Binance returned a non-JSON response") from exc

        LOGGER.info("API response status=%s body=%s", response.status_code, data)

        if response.status_code >= 400:
            message = data.get("msg", "unknown Binance API error")
            code = data.get("code", response.status_code)
            raise BinanceClientError(f"Binance API error {code}: {message}")

        return data

    def _sign(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _sanitize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        sanitized = dict(params)
        sanitized.pop("signature", None)
        if self.api_key:
            sanitized["apiKey"] = f"{self.api_key[:4]}...{self.api_key[-4:]}"
        return sanitized
