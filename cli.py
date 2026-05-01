#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Supports two modes:
  1. Command-line arguments  – ideal for scripting / CI
  2. Interactive mode         – guided prompts with rich formatting

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py --interactive
"""

from __future__ import annotations

import argparse
import os
import sys

# Force UTF-8 output on Windows to avoid encoding errors with Rich
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

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

console = Console(force_terminal=True)
logger = setup_logging()


# ── Argument parsing ─────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot – place Market, Limit, and Stop-Limit orders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001\n"
            "  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.05 --price 3500\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 90000 --stop-price 91000\n"
            "  python cli.py --interactive\n"
        ),
    )
    parser.add_argument("--symbol", type=str, help="Trading pair (e.g. BTCUSDT)")
    parser.add_argument("--side", type=str, help="Order side: BUY or SELL")
    parser.add_argument("--type", dest="order_type", type=str, help="Order type: MARKET, LIMIT, or STOP_LIMIT")
    parser.add_argument("--quantity", type=str, help="Order quantity")
    parser.add_argument("--price", type=str, default=None, help="Limit price (required for LIMIT & STOP_LIMIT)")
    parser.add_argument("--stop-price", type=str, default=None, help="Stop price (required for STOP_LIMIT)")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive mode with guided prompts")
    return parser


# ── Interactive mode ─────────────────────────────────────────────────


def interactive_mode() -> dict:
    """Collect order parameters interactively using rich prompts."""
    console.print(
        Panel.fit(
            "[bold cyan]Binance Futures Testnet Trading Bot[/bold cyan]\n"
            "[dim]Interactive Order Placement[/dim]",
            border_style="cyan",
        )
    )

    symbol = Prompt.ask("[bold yellow]Symbol[/bold yellow]", default="BTCUSDT")
    side = Prompt.ask("[bold yellow]Side[/bold yellow]  (BUY / SELL)", choices=["BUY", "SELL", "buy", "sell"])
    order_type = Prompt.ask(
        "[bold yellow]Order type[/bold yellow]  (MARKET / LIMIT / STOP_LIMIT)",
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
    )

    quantity = Prompt.ask("[bold yellow]Quantity[/bold yellow]")

    price = None
    stop_price = None
    order_type_upper = order_type.upper()

    if order_type_upper in ("LIMIT", "STOP_LIMIT"):
        price = Prompt.ask("[bold yellow]Price[/bold yellow]")
    if order_type_upper == "STOP_LIMIT":
        stop_price = Prompt.ask("[bold yellow]Stop price[/bold yellow]")

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price,
    }


# ── Display helpers ──────────────────────────────────────────────────


def print_order_summary(symbol: str, side: str, order_type: str, quantity: float,
                        price: float | None, stop_price: float | None) -> None:
    """Print a formatted summary of the order about to be placed."""
    table = Table(title="Order Request Summary", show_header=False, border_style="cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Symbol", symbol)
    table.add_row("Side", f"[green]{side}[/green]" if side == "BUY" else f"[red]{side}[/red]")
    table.add_row("Type", order_type)
    table.add_row("Quantity", str(quantity))
    if price is not None:
        table.add_row("Price", str(price))
    if stop_price is not None:
        table.add_row("Stop Price", str(stop_price))
    console.print(table)


def print_order_response(data: dict) -> None:
    """Print a formatted table of the order response details."""
    table = Table(title="Order Response", show_header=False, border_style="green")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for key, value in data.items():
        table.add_row(key, str(value))
    console.print(table)


# ── Core execution ───────────────────────────────────────────────────


def execute_order(client: BinanceClient, symbol: str, side: str,
                  order_type: str, quantity: float,
                  price: float | None, stop_price: float | None) -> None:
    """Validate, place, and display an order."""
    # Print order summary
    print_order_summary(symbol, side, order_type, quantity, price, stop_price)
    console.print()

    # Place order
    try:
        if order_type == "MARKET":
            response = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            response = place_limit_order(client, symbol, side, quantity, price)
        elif order_type == "STOP_LIMIT":
            response = place_stop_limit_order(client, symbol, side, quantity, price, stop_price)
        else:
            raise ValueError(f"Unexpected order type: {order_type}")
    except BinanceClientError as exc:
        console.print(f"[bold red][X] Order failed:[/bold red] {exc}")
        logger.error("Order failed: %s", exc)
        return
    except (ConnectionError, TimeoutError) as exc:
        console.print(f"[bold red][X] Network error:[/bold red] {exc}")
        logger.error("Network error: %s", exc)
        return

    # Format and display response
    formatted = format_order_response(response)
    logger.info("Order response: %s", formatted)
    print_order_response(formatted)
    console.print("[bold green][OK] Order placed successfully![/bold green]")


# ── Main ─────────────────────────────────────────────────────────────


def main() -> None:
    """Entry point – parse args or launch interactive mode, then execute."""
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    # ── Load credentials ─────────────────────────────────────────────
    api_key = os.environ.get("BINANCE_TESTNET_API_KEY")
    api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET")

    if not api_key or not api_secret:
        console.print(
            "[bold red][X] Missing API credentials.[/bold red]\n"
            "Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET\n"
            "in your environment or in a .env file.\n"
            "See .env.example for reference.",
        )
        sys.exit(1)

    client = BinanceClient(api_key, api_secret)

    # ── Gather parameters ────────────────────────────────────────────
    if args.interactive:
        params = interactive_mode()
    else:
        # Validate that required args are present
        if not all([args.symbol, args.side, args.order_type, args.quantity]):
            parser.error(
                "The following arguments are required: --symbol, --side, --type, --quantity\n"
                "Or use --interactive for guided prompts."
            )
        params = {
            "symbol": args.symbol,
            "side": args.side,
            "order_type": args.order_type,
            "quantity": args.quantity,
            "price": args.price,
            "stop_price": args.stop_price,
        }

    # ── Validate inputs ──────────────────────────────────────────────
    try:
        symbol = validate_symbol(params["symbol"])
        side = validate_side(params["side"])
        order_type = validate_order_type(params["order_type"])
        quantity = validate_quantity(params["quantity"])
        price = validate_price(params["price"], order_type)
        stop_price = validate_stop_price(params.get("stop_price"), order_type)
    except ValueError as exc:
        console.print(f"[bold red][X] Validation error:[/bold red] {exc}")
        logger.error("Validation error: %s", exc)
        sys.exit(1)

    # ── Execute ──────────────────────────────────────────────────────
    execute_order(client, symbol, side, order_type, quantity, price, stop_price)


if __name__ == "__main__":
    main()
