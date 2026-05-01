"""
Order placement logic for the trading bot.

Provides helper functions that build order payloads, invoke the Binance client,
and format the API response into human-readable output.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from bot.client import BinanceClient

logger = logging.getLogger("trading_bot.orders")


# ── Order builders ───────────────────────────────────────────────────


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> Dict[str, Any]:
    """Place a MARKET order and return the raw API response."""
    logger.info("Placing MARKET %s order: %s qty=%s", side, symbol, quantity)
    return client.place_order(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
    )


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """Place a LIMIT order and return the raw API response."""
    logger.info(
        "Placing LIMIT %s order: %s qty=%s price=%s tif=%s",
        side, symbol, quantity, price, time_in_force,
    )
    return client.place_order(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce=time_in_force,
    )


def place_stop_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """Place a STOP (stop-limit) order and return the raw API response."""
    logger.info(
        "Placing STOP_LIMIT %s order: %s qty=%s price=%s stopPrice=%s tif=%s",
        side, symbol, quantity, price, stop_price, time_in_force,
    )
    return client.place_order(
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce=time_in_force,
    )


# ── Response formatting ─────────────────────────────────────────────


def format_order_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the most relevant fields from a raw order response."""
    return {
        "orderId": response.get("orderId"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
        "status": response.get("status"),
        "origQty": response.get("origQty"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice", "N/A"),
        "price": response.get("price", "N/A"),
        "stopPrice": response.get("stopPrice", "N/A"),
        "timeInForce": response.get("timeInForce", "N/A"),
    }
