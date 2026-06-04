# Signal — a Binance.US trading assistant (skills for Claude Code)

Natural-language spot trading and portfolio insight on Binance.US, built as agent skills you run
in Claude Code. Say what you want; it reasons over your real portfolio and live market data,
previews trades, and places them only after you confirm.

Forked from and built on top of cmeiliu/binance-us-skills (the read-only briefing engine). This
project adds an execution layer, a cross-context synthesis skill, a candle-based strategy scan,
a beginner concept skill, and a sharper, emoji-led voice. See LICENSE for the original terms.

## What it does

Read skills (inherited, tightened):
- briefing-engine — daily brief, watchlist, portfolio brief, capital-readiness
- asset-research — deep single-asset read
- account-status — balances, readiness, blockers
- fund-account — deposit guidance

New skills:
- binance-us-trade — intent-to-trade: plain words to a single market/limit order or a multi-leg
  LIMIT plan. Preview, confirm, place. Reports real fills.
- binance-us-strategy — scan support/resistance from the candles, propose a multi-leg LIMIT buy
  at support, preview and confirm.
- binance-us-pulse — cross-context synthesis: why an asset is moving and what it means for your
  position (price + candle TA + holdings; web-search for color).
- binance-us-news — portfolio-aware news: headlines ranked by what you hold, with dollar impact.
- binance-us-scenario — what-if math on your real portfolio ("if BTC hits $100k, you're worth $Y").
- binance-us-sim — agentic trading simulation on mock data. No real orders, no keys. Demo-safe.
- binance-us-learn — plain-English concept explainer for beginners.

## Architecture

- engine (scripts/binance_us_brief.py) — the inherited read engine. Public market data + balances.
- trading.py — the execution layer. Signs its own requests. Single + multi-leg orders, plus a
  `levels` mode for candle-based support/resistance. Independent of the read engine.
- config.py — open knobs: cap, allowlist, order types, live flag, quote asset.
- skills/ — one SKILL.md per workflow. Behavior + voice. Skills call the engines as a CLI.
- prompts/voice.md — the shared voice (sharp, emoji-led, plain).

One source of truth: Binance.US for price, portfolio, candles, and orders. Web-search is optional
color only. No paid data feeds (no CoinDesk, no LunarCrush).

## Setup

1. Clone, then `pip install requests python-dotenv`.
2. Create `.env` in the repo root:
   ```
   BINANCE_US_API_KEY=...
   BINANCE_US_SECRET_KEY=...
   LIVE_TRADING_ENABLED=false
   ```
3. Confirm `.env` is gitignored.
4. Read WALKTHROUGH.md (build) or INSTALL.md (install for anyone) and follow it.

## Safety

- Dry-run is the default. Live orders only when LIVE_TRADING_ENABLED=true.
- Per-order cap, symbol allowlist, exchange-filter validation — all in config.py, all loosenable.
- Not configurable, enforced in trading.py: no withdrawal/transfer/key endpoints, and your keys
  only. The voice keeps a PII refusal and a distress (988) line.
- This is a prototype for your own account. Production would need the no-financial-advice framing
  added back; that is a compliance requirement, not a style choice.

## Files

```
scripts/binance_us_brief.py   read engine (inherited)
trading.py                    execution + levels
config.py                     open knobs
prompts/voice.md              shared voice
skills/                       trade, strategy, pulse, learn (+ inherited read skills)
CLAUDE.md                     project rules (Claude Code reads this)
AGENTS.md                     same rules for other agent runtimes
WALKTHROUGH.md                download-to-demo steps
DEMO_SCRIPT.md                the rehearsed demo
SKILLS_ANALYSIS.md            what each skill does
SKILLS_UPGRADE.md             how the inherited skills were tightened
```
