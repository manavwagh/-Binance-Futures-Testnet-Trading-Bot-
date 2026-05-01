"""
Binance Futures Testnet API client.

Handles request signing (HMAC-SHA256), HTTP communication,
automatic retries on transient errors, and structured logging.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("trading_bot.client")

DEFAULT_BASE_URL = "https://testnet.binancefuture.com"
REQUEST_TIMEOUT = 10  # seconds


class BinanceClientError(Exception):
    """Raised when the Binance API returns a non-2xx response."""

    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"HTTP {status_code} – Binance error {code}: {message}")


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

        # Session with automatic retries on 5xx / connection errors
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "DELETE"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.debug("BinanceClient initialised – base_url=%s", self.base_url)

    # ── Signing ──────────────────────────────────────────────────────

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add timestamp and HMAC-SHA256 signature to *params*."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    # ── HTTP helpers ─────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True,
    ) -> Dict[str, Any]:
        """Send a request to the Binance API and return the JSON body."""
        params = params or {}
        if signed:
            params = self._sign(params)

        url = f"{self.base_url}{endpoint}"
        logger.debug("API request  : %s %s  params=%s", method.upper(), url, params)

        try:
            resp = self.session.request(
                method,
                url,
                params=params if method.upper() == "GET" else None,
                data=params if method.upper() != "GET" else None,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError(
                "Unable to reach Binance testnet. Check your internet connection."
            ) from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise TimeoutError("Request to Binance timed out.") from exc

        logger.debug("API response : HTTP %s  body=%s", resp.status_code, resp.text)

        if resp.status_code >= 400:
            try:
                body = resp.json()
                code = body.get("code", -1)
                msg = body.get("msg", resp.text)
            except ValueError:
                code, msg = -1, resp.text
            logger.error("API error    : HTTP %s – %s (code %s)", resp.status_code, msg, code)
            raise BinanceClientError(resp.status_code, code, msg)

        return resp.json()

    # ── Public API methods ───────────────────────────────────────────

    def place_order(self, **kwargs: Any) -> Dict[str, Any]:
        """Place a new order on Binance Futures (POST /fapi/v1/order)."""
        return self._request("POST", "/fapi/v1/order", params=kwargs)

    def get_exchange_info(self) -> Dict[str, Any]:
        """Retrieve exchange info (GET /fapi/v1/exchangeInfo)."""
        return self._request("GET", "/fapi/v1/exchangeInfo", signed=False)
