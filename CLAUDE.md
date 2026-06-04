# CLAUDE.md — Runtime rules for this project

A Binance.US spot-trading assistant built as skills. The core loop: the user's words plus their
real portfolio go in; a feasible, previewed order comes out; it's placed only on the user's
explicit confirm.

## Architecture
- The read engine (`scripts/binance_us_brief.py`) and `scripts/trading.py` are the only callers of external
  APIs. Skills invoke them as a CLI and read JSON. Skills never call an API directly.
- One source of truth: Binance.US for price, portfolio, candles, orders. Web search is optional
  context/color only and never sets an order price. No third-party paid data feeds.
- `config.py` holds the tunable knobs. The safety logic in `scripts/trading.py` holds the non-negotiables.

## Skills
- Read: `binance-us-briefing-engine`, `binance-us-asset-research`, `binance-us-account-status`,
  `binance-us-fund-account`.
- `binance-us-trade`: intent-to-trade, single market/limit + multi-leg LIMIT. Preview then confirm.
- `binance-us-strategy`: candle support/resistance scan, multi-leg LIMIT buy plan.
- `binance-us-pulse`: cross-context synthesis (why + what-it-means), price + TA + holdings.
- `binance-us-news`: portfolio-aware news, ranked by holdings with dollar impact.
- `binance-us-scenario`: deterministic what-if math on the real portfolio (no predictions).
- `binance-us-sim`: agentic trading SIMULATION on mock data (`scripts/sim.py`). No real orders, no keys.
- `binance-us-learn`: beginner concept explainer.
- `binance-us-spot-trade` is deprecated (review-only); route trade intent to `binance-us-trade`.

## Hard lines (enforced in code / kept in voice; not optional)
1. Dry-run default. Live only when `LIVE_TRADING_ENABLED=true`.
2. Every order passes validation: allowlist, cap, exchange filters (`config.py` / `scripts/trading.py`).
3. No withdrawal, transfer, or key endpoint, ever (blocked in `scripts/trading.py`).
4. Your keys only.
5. Voice keeps the seed-phrase/PII refusal and the 988 distress line.

## Voice
Use `prompts/voice.md`: sharp, plain, emoji-led. Lead with one read, one reason, one number. Trades
are preview-then-confirm. TA and web context are observational — never "so buy", never promise
gains. The user states intent and amount; you translate and execute the mechanics.
