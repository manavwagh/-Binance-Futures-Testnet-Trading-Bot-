"""
Input validators for trading bot CLI arguments.

Each function raises ``ValueError`` with a descriptive message on failure
and returns the sanitised value on success.
"""

from __future__ import annotations

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_LIMIT")


def validate_symbol(symbol: str) -> str:
    """Validate and normalise a trading symbol (e.g. BTCUSDT)."""
    if not symbol or not symbol.strip():
        raise ValueError("Symbol must not be empty.")
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValueError(f"Symbol must be alphanumeric, got: '{symbol}'")
    return symbol


def validate_side(side: str) -> str:
    """Validate order side – must be BUY or SELL."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Side must be one of {VALID_SIDES}, got: '{side}'")
    return side


def validate_order_type(order_type: str) -> str:
    """Validate order type – MARKET, LIMIT, or STOP_LIMIT."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Order type must be one of {VALID_ORDER_TYPES}, got: '{order_type}'"
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
    """Validate quantity – must be a positive number."""
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Quantity must be a number, got: '{quantity}'")
    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got: {qty}")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    """Validate price – required for LIMIT and STOP_LIMIT orders."""
    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None:
            raise ValueError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValueError(f"Price must be a number, got: '{price}'")
        if p <= 0:
            raise ValueError(f"Price must be positive, got: {p}")
        return p
    return None  # price not needed for MARKET


def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    """Validate stop price – required only for STOP_LIMIT orders."""
    if order_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValueError("Stop price is required for STOP_LIMIT orders.")
        try:
            sp = float(stop_price)
        except (TypeError, ValueError):
            raise ValueError(f"Stop price must be a number, got: '{stop_price}'")
        if sp <= 0:
            raise ValueError(f"Stop price must be positive, got: {sp}")
        return sp
    return None
