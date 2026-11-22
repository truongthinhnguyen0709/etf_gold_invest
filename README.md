# ETF & Gold Drawdown Alert

A small Python script that tracks how far Vietnamese ETFs and gold have fallen from their peak, and sends a Telegram alert for each one.

## What it does

For each ticker, the script:

1. Downloads 10 years of daily closing prices from Yahoo Finance (`yfinance`).
2. Calculates the running peak and the **drawdown** from that peak (in %).
3. Ranks today's drawdown against its own history to get a **percentile**.
4. Assigns a **zone** from the percentile.
5. Computes a **benchmark price**: the price at which the drawdown would equal its 25th percentile (`peak × (1 + p25 drawdown / 100)`).
6. Sends the result to a Telegram chat.

If any ticker fails (no data from Yahoo, network error, Telegram rejecting a message), the script finishes the other tickers, then sends one error report to the same chat and exits with code 1:

```
⚠️ ETF alert errors (2026-11-22 15:30)
1/5 tickers failed:
- FUEVN100.VN: ValueError: no price data returned from Yahoo Finance
```

A 50-day rolling z-score of price is also calculated, but it is not currently used in the alert.

### Tracked tickers

| Ticker | Asset |
|---|---|
| `FUEVFVND.VN` | DCVFMVN Diamond ETF |
| `E1VFVN30.VN` | DCVFMVN30 ETF |
| `FUEVN100.VN` | VinaCapital VN100 ETF |
| `FUESSVFL.VN` | SSIAM VNFIN LEAD ETF |
| `XAUT-USD` | Tether Gold (gold proxy) |

### Zones

| Drawdown percentile | Zone |
|---|---|
| >= 75 | Floor_4 |
| >= 50 | Floor_3 |
| >= 25 | Floor_2 |
| < 25 | Floor_1 |

Drawdowns are negative, so a low percentile means a deeper drawdown than usual.

### Example alert

```
🚀 Stock Alert
------------------
1. Ticker: E1VFVN30.VN
2. Price: 25.40
3. Peak: 28.10
4. Zone: Floor_2
5. Benchmark: 24.90
6. Percentile: 31.50
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (the project uses `pyproject.toml` and `uv.lock`)
- A Telegram bot token and chat ID

Main dependencies: `polars`, `pandas`, `numpy`, `httpx`, `yfinance`, `python-dotenv`.

## Setup

```bash
uv sync
cp .env.example .env
```

Then fill in your Telegram credentials in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

`.env` is listed in `.gitignore`, so it is never committed.

## Usage

Run once:

```bash
uv run main.py
```

Run on a schedule with cron, for example every weekday at 15:30, logging to `cron.log`:

```cron
30 15 * * 1-5 cd /path/to/etf_gold_invest && uv run main.py >> cron.log 2>&1
```

Log files (`*.log`) are ignored by git.

To change the tickers, edit the `tickers` list at the bottom of `main.py`. Any symbol Yahoo Finance supports will work (Vietnamese stocks use the `.VN` suffix).

## Project structure

```
.
├── main.py          # data fetching, metrics, Telegram alert
├── .env.example     # template for Telegram credentials
├── pyproject.toml   # project metadata and dependencies
└── uv.lock          # locked dependency versions
```

## Known limitations

- If Telegram itself is unreachable or misconfigured (wrong token or chat ID), the error report cannot be delivered and is only printed to the log.
- The peak and percentiles only use the downloaded history. Tickers with less than 10 years of data (such as `XAUT-USD` and the newer ETFs) have a shorter baseline, so their zones are not strictly comparable.

## Disclaimer

This tool is for personal monitoring only and is not investment advice.
