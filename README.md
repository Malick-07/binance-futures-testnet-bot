# Binance Futures Testnet Trading Bot

A small Python CLI application for placing Binance USDT-M Futures Testnet orders.

The bot uses direct REST calls against:

```text
https://testnet.binancefuture.com
```

It supports:

- MARKET and LIMIT orders
- BUY and SELL sides
- CLI validation for symbol, side, order type, quantity, and limit price
- Structured request/response/error logging
- Clear console output for order summaries and API responses

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py
    logging_config.py
    orders.py
    validators.py
  cli.py
logs/
  sample_market_order.log
  sample_limit_order.log
requirements.txt
README.md
```

## Setup

1. Create and activate a Binance Futures Testnet account.
2. Generate API credentials from the Futures Testnet dashboard.
3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate it.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Set API credentials as environment variables.

Windows PowerShell:

```powershell
$env:BINANCE_API_KEY="your_testnet_api_key"
$env:BINANCE_API_SECRET="your_testnet_api_secret"
```

macOS/Linux:

```bash
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

## Usage

Run the CLI as a module from the repository root.

### MARKET Order

```bash
python -m trading_bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT Order

```bash
python -m trading_bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000 --time-in-force GTC
```

### Dry Run

Use `--dry-run` to validate input and inspect the request without sending it to Binance.

```bash
python -m trading_bot.cli --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 90000 --dry-run
```

## CLI Options

```text
--symbol          Trading pair, for example BTCUSDT
--side            BUY or SELL
--type            MARKET or LIMIT
--quantity        Positive order quantity
--price           Positive limit price, required for LIMIT orders
--time-in-force   Time in force for LIMIT orders, default: GTC
--dry-run         Validate and print the request without placing an order
```

## Logging

Runtime logs are written to:

```text
logs/trading_bot.log
```

The application logs:

- outgoing API request method, URL path, and sanitized parameters
- API response status and body
- validation errors
- network/API errors

API secrets are never logged. API keys are masked.

Sample logs are included for one MARKET order and one LIMIT order:

```text
logs/sample_market_order.log
logs/sample_limit_order.log
```

## Assumptions

- This project targets Binance USDT-M Futures Testnet only.
- The account already has testnet funds available.
- The submitted order quantity and price must satisfy Binance symbol filters.
- `avgPrice` may be `0.00000` for some order responses, especially immediately after order placement or for unfilled LIMIT orders.
- LIMIT orders use `GTC` by default.
