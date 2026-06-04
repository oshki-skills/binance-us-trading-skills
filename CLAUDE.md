# CLAUDE.md — Project rules (read first, every session)

Signal: a Binance.US spot trading assistant built as skills. The differentiator is the closed
loop, your words and real portfolio in, a feasible previewed trade out, placed only on your
confirm. Demoed by talking to Claude Code directly.

## Architecture
- The read engine (scripts/binance_us_brief.py) and trading.py are the only callers of external
  APIs. Skills invoke them as a CLI and read JSON. Skills never call an API directly.
- One source of truth: Binance.US for price, portfolio, candles, orders. Web-search is optional
  color only. No paid data (no CoinDesk, no LunarCrush).
- config.py holds the open knobs. safety logic in trading.py holds the non-negotiables.

## Skills
- Read: briefing-engine, asset-research, account-status, fund-account (inherited, tightened).
- binance-us-trade: intent-to-trade, single market/limit + multi-leg LIMIT. Preview then confirm.
- binance-us-strategy: candle support/resistance scan, multi-leg LIMIT buy plan.
- binance-us-pulse: cross-context synthesis (why + what-it-means), price + TA + holdings.
- binance-us-news: portfolio-aware news, ranked by holdings with dollar impact.
- binance-us-scenario: deterministic what-if math on the real portfolio (no predictions).
- binance-us-sim: agentic trading SIMULATION on mock data (sim.py). No real orders, no keys.
- binance-us-learn: beginner concept explainer.
- Retire the old binance-us-spot-trade (review-only); binance-us-trade replaces it.

## Hard lines (enforced in code / kept in voice; not optional)
1. Dry-run default. Live only when LIVE_TRADING_ENABLED=true.
2. Every order passes validation: allowlist, cap, exchange filters (in config.py / trading.py).
3. No withdrawal, transfer, or key endpoint, ever (blocked in trading.py).
4. Your keys only.
5. Voice keeps the seed-phrase/PII refusal and the 988 distress line.

## Voice
Use prompts/voice.md: sharp, plain, fun, emoji-led. Lead with one read, one reason, one number.
Trades preview-then-confirm. TA and web context are observational, never "so buy", never promise
gains. The user states intent and amount; you translate and execute mechanics.

## Build conventions
- Plan before coding for execution, signing, or the levels math. Just write for formatting/glue.
- After every change, run it and show the result. Fix errors in place.
- Keep scope tight. Don't add features beyond what's in the skills above.
