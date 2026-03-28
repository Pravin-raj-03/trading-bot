# Binance Futures Trading Bot

A professional command-line interface (CLI) for placing orders on the Binance Futures Testnet (USDT-M). This project demonstrates a structured approach to API integration, including secure signing, input validation, and comprehensive logging.

## Key Features

- **Multi-Order Support**: Execute MARKET, LIMIT, and STOP-LIMIT orders.
- **Secure Client**: Implements HMAC-SHA256 request signing and server clock synchronization.
- **Input Validation**: Rigorous parameter checking for trading symbols, sides, quantities, and prices.
- **Simulation Mode**: A full `--mock` mode for status checks and order placement without network activity.
- **Professional Logging**: Records all interactions in structured, timestamped log files.
- **Automated Testing**: Includes a pytest suite for core logic and validation verification.

## Prerequisites

- Python 3.8 or higher.
- A Binance Futures Testnet account with API Key and Secret.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Pravin-raj-03/trading-bot.git
   cd trading-bot
   ```

2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your credentials in a `.env` file:
   ```bash
   BINANCE_TESTNET_API_KEY=your_api_key_here
   BINANCE_TESTNET_API_SECRET=your_api_secret_here
   ```

## Usage

### Account Status Check
Verify your connection and account balance:
```bash
python cli.py check
```

### Market Order
Place a market buy order for BTC/USDT:
```bash
python cli.py order BTCUSDT BUY MARKET 0.001
```

### Limit Order
Place a limit sell order for ETH/USDT:
```bash
python cli.py order ETHUSDT SELL LIMIT 0.01 --price 3500
```

### Stop-Limit Order
Place a stop-limit buy order for BTC/USDT:
```bash
python cli.py order BTCUSDT BUY STOP_LIMIT 0.001 --price 95000 --stop-price 94500
```

## Professional Polish and Conventions

This project adheres to the **Google Python Style Guide** for documentation and code structure. 

### Simulation Mode (Testing)
You can run the application in simulation mode to explore the features safely without providing API credentials or impacting your testnet balance:

```bash
# Check simulated account
python cli.py --mock check

# Place simulated orders
python cli.py --mock order BTCUSDT BUY MARKET 0.001
```

## Automated Testing

To run the full test suite and verify the integrity of the application:
```bash
python -m pytest -v
```

## Project Directory Structure

```
tradebot/
├── bot/
│   ├── client.py          # API Client with secure signing
│   ├── orders.py          # High-level order functions
│   ├── validators.py      # Input validation logic
│   └── logging_config.py  # Centralized log setup
├── tests/                 # Automated pytest suite
├── cli.py                 # Primary CLI entry point
├── logs/                  # Directory for generated log files
├── .env.example           # Template for environment variables
├── README.md              # Documentation
├── requirements.txt       # Project dependencies
└── pytest.ini             # Test configuration
```
