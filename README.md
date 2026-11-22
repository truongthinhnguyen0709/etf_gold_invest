# ETF & Gold Drawdown Alert

A small Python script that tracks how far Vietnamese ETFs and gold have fallen from their peak, and sends a Telegram alert for each one.

## What it does

For each ticker, the script:

1. Downloads daily closing prices.
2. Calculates the running peak and the **drawdown** from that peak (in %).
3. Ranks today's drawdown against its own history to get a **percentile**.
4. Assigns a **zone** from the percentile.
5. Computes a **benchmark price**: the price at which the drawdown would equal its 25th percentile (`peak × (1 + p25 drawdown / 100)`).
6. Sends the result to a Telegram chat.

A 50-day rolling z-score of price is also calculated, but it is not currently used in the alert.

### Tracked tickers

| Source | Tickers |
|---|---|
| `yfinance` (10 years) | `FUEVFVND.VN`, `E1VFVN30.VN`, `FUEVN100.VN`, `FUESSVFL.VN` |
| `yfinance` (10 years) | `XAUT-USD` |

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
1. Ticker: E1VFVN30
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

Main dependencies: `polars`, `pandas`, `numpy`, `httpx`, `yfinance`.

## Setup

```bash
uv sync
```

> **Note:** the API keys and Telegram credentials are currently hardcoded in `main.py`. Move them to environment variables before committing or sharing the code, and revoke any token that has already been exposed.

## Usage

Run once:

```bash
uv run main.py
```

Run on a schedule with cron, for example every weekday at 15:30 and logging to `cron.log`:

```cron
30 15 * * 1-5 cd /home/thinh/VS_CODE/etf_gold_invest && uv run main.py >> cron.log 2>&1
```

To change the tickers, edit the `source_data` dictionary at the bottom of `main.py`.

## Project structure

```
.
├── main.py          # data fetching, metrics, Telegram alert
├── pyproject.toml   # project metadata and dependencies
├── uv.lock          # locked dependency versions
└── cron.log         # output from scheduled runs
```

## Known limitations

- Errors are only printed, so a failed ticker produces no alert and no notification.
- The peak is the maximum within the downloaded window (8 or 10 years), so the zones for VN tickers and gold are not strictly comparable.

## Disclaimer

This tool is for personal monitoring only and is not investment advice.
