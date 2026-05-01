# 🤖 Binance Futures Testnet Trading Bot

A simplified Python trading bot that places **Market**, **Limit**, and **Stop-Limit** orders on [Binance Futures Testnet (USDT-M)](https://testnet.binancefuture.com).

Built with clean, layered architecture, structured logging, robust input validation, and an enhanced CLI experience using [Rich](https://github.com/Textualize/rich).

---

## ✨ Features

| Feature | Description |
|---|---|
| **Market Orders** | Place instant buy/sell orders at current market price |
| **Limit Orders** | Place buy/sell orders at a specified price |
| **Stop-Limit Orders** | *(Bonus)* Conditional orders that trigger at a stop price |
| **Interactive Mode** | *(Bonus)* Guided prompts with colourful, formatted output |
| **Structured Logging** | Dual handlers – console (INFO) + rotating file (DEBUG) |
| **Input Validation** | Comprehensive validation with descriptive error messages |
| **Error Handling** | Graceful handling of API errors, network failures, invalid input |
| **Auto-Retry** | Automatic retry on 5xx / transient errors (3 attempts with backoff) |

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package init
│   ├── client.py            # Binance API client (signing, HTTP, retries)
│   ├── orders.py            # Order placement logic + response formatting
│   ├── validators.py        # Input validation functions
│   └── logging_config.py    # Dual-handler logging configuration
├── logs/                     # Auto-created log directory
│   └── trading_bot.log      # Rotating log file (DEBUG-level)
├── cli.py                    # CLI entry point (argparse + interactive)
├── .env.example              # Template for API credentials
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🚀 Setup

### Prerequisites

- **Python 3.9+** installed
- **Binance Futures Testnet account** – [register here](https://testnet.binancefuture.com)
- **API Key & Secret** – generate from the testnet dashboard

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/trading-bot.git
cd trading-bot/trading_bot
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Credentials

Copy the example env file and add your testnet credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BINANCE_TESTNET_API_KEY=your_actual_api_key
BINANCE_TESTNET_API_SECRET=your_actual_api_secret
```

> ⚠️ **Never commit your `.env` file.** It is already in `.gitignore`.

---

## 📖 How to Run

### Command-Line Mode

**Market Order (BUY):**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Limit Order (SELL):**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000
```

**Stop-Limit Order (SELL):**
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 90000 --stop-price 91000
```

### Interactive Mode

```bash
python cli.py --interactive
```

You will be guided through each parameter with clear prompts and validation.

### Help

```bash
python cli.py --help
```

---

## 📋 Output Example

### Order Request Summary

```
┌────────────────────────────┐
│   Order Request Summary    │
├──────────┬─────────────────┤
│ Symbol   │ BTCUSDT         │
│ Side     │ BUY             │
│ Type     │ MARKET          │
│ Quantity │ 0.001           │
└──────────┴─────────────────┘
```

### Order Response

```
┌────────────────────────────┐
│      Order Response        │
├─────────────┬──────────────┤
│ orderId     │ 123456789    │
│ symbol      │ BTCUSDT      │
│ side        │ BUY          │
│ type        │ MARKET       │
│ status      │ FILLED       │
│ origQty     │ 0.001        │
│ executedQty │ 0.001        │
│ avgPrice    │ 97234.50     │
└─────────────┴──────────────┘
✓ Order placed successfully!
```

---

## 📊 Logging

Logs are written to **`logs/trading_bot.log`** with full DEBUG-level detail including:

- API request parameters (URL, method, signed params)
- API response bodies
- Errors and exceptions with stack traces

The log file rotates at **5 MB** with **3 backups** to prevent disk usage issues.

**Sample log entry:**
```
2026-05-01 12:30:00 | DEBUG    | trading_bot.client | API request  : POST https://testnet.binancefuture.com/fapi/v1/order  params={...}
2026-05-01 12:30:01 | DEBUG    | trading_bot.client | API response : HTTP 200  body={...}
2026-05-01 12:30:01 | INFO     | trading_bot.orders | Order response: {'orderId': 123456, 'status': 'FILLED', ...}
```

---

## 🧪 Testing Scenarios

| Scenario | Command |
|---|---|
| Market BUY | `python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001` |
| Limit SELL | `python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000` |
| Stop-Limit SELL | `python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 90000 --stop-price 91000` |
| Missing price (error) | `python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001` |
| Invalid side (error) | `python cli.py --symbol BTCUSDT --side HOLD --type MARKET --quantity 0.001` |
| Interactive mode | `python cli.py --interactive` |

---

## 🔧 Assumptions

1. **Testnet only** – this bot is designed exclusively for the Binance Futures Testnet. Do NOT use with real credentials.
2. **USDT-M futures** – all orders are placed on USDT-margined futures contracts.
3. **Direct REST** – uses `requests` library with HMAC-SHA256 signing instead of `python-binance` for full transparency.
4. **Time-in-force** – defaults to `GTC` (Good Till Cancelled) for Limit and Stop-Limit orders.
5. **No position management** – this bot places individual orders; it does not manage open positions or implement strategies.
6. **Symbol validation** – validates format only (alphanumeric); does not check against exchange info by default.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP client for Binance API calls |
| `python-dotenv` | Load `.env` file for API credentials |
| `rich` | Enhanced CLI output (tables, panels, coloured text) |

---

## 📄 License

This project is provided as-is for evaluation purposes.
