#!/usr/bin/env python3
"""
Flask web UI for the Binance Futures Testnet Trading Bot.

Provides a sleek, modern single-page interface for placing
Market, Limit, and Stop-Limit orders.
"""

from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logging
from bot.orders import (
    format_order_response,
    place_limit_order,
    place_market_order,
    place_stop_limit_order,
)
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

load_dotenv()
logger = setup_logging()

app = Flask(__name__)


def _get_client() -> BinanceClient:
    """Build a BinanceClient from env vars or raise."""
    api_key = os.environ.get("BINANCE_TESTNET_API_KEY", "")
    api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET", "")
    if not api_key or not api_secret:
        raise ValueError(
            "Missing API credentials. Set BINANCE_TESTNET_API_KEY and "
            "BINANCE_TESTNET_API_SECRET in your .env file."
        )
    return BinanceClient(api_key, api_secret)


# ── Routes ───────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Serve the main UI."""
    return render_template("index.html")


@app.route("/api/place-order", methods=["POST"])
def place_order():
    """Validate and place an order, returning JSON result."""
    data = request.get_json(force=True)

    # ── Validate ─────────────────────────────────────────────────────
    try:
        symbol = validate_symbol(data.get("symbol", ""))
        side = validate_side(data.get("side", ""))
        order_type = validate_order_type(data.get("orderType", ""))
        quantity = validate_quantity(data.get("quantity", ""))
        price = validate_price(data.get("price") or None, order_type)
        stop_price = validate_stop_price(data.get("stopPrice") or None, order_type)
    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 400

    # ── Build client ─────────────────────────────────────────────────
    try:
        client = _get_client()
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

    # ── Place order ──────────────────────────────────────────────────
    try:
        if order_type == "MARKET":
            raw = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            raw = place_limit_order(client, symbol, side, quantity, price)
        elif order_type == "STOP_LIMIT":
            raw = place_stop_limit_order(client, symbol, side, quantity, price, stop_price)
        else:
            return jsonify({"success": False, "error": f"Unknown order type: {order_type}"}), 400
    except BinanceClientError as exc:
        logger.error("Binance API error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 502
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 503

    formatted = format_order_response(raw)
    logger.info("Order placed via web UI: %s", formatted)
    return jsonify({"success": True, "order": formatted})


@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Return the last N lines of the log file."""
    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logs", "trading_bot.log"
    )
    lines_count = int(request.args.get("lines", 50))
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        return jsonify({"lines": all_lines[-lines_count:]})
    except FileNotFoundError:
        return jsonify({"lines": ["No log file found yet. Place an order to generate logs."]})


# ── Entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Trading Bot Web UI running at http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
