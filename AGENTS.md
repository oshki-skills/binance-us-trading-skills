# AGENTS.md

This repo is also runnable by Codex, OpenClaw, and other agent runtimes. The full project rules
live in CLAUDE.md; follow them. Summary:

- Skills call the engines (scripts/binance_us_brief.py for reads, trading.py for execution and
  levels) as a CLI and read the JSON. Never call an API directly from a skill.
- Binance.US is the only source for price, portfolio, candles, and orders. Web-search is optional
  color. No paid data feeds.
- Trading is dry-run by default; place_order / place_multi require LIVE_TRADING_ENABLED=true.
  Always preview, always confirm. Never call withdrawal/transfer/key endpoints. Your keys only.
- Voice: prompts/voice.md (sharp, plain, emoji-led, no profit promises, no "so buy").
- Credentials: a `.env` in the repo root (BINANCE_US_API_KEY, BINANCE_US_SECRET_KEY,
  LIVE_TRADING_ENABLED). Keep it gitignored.

See README.md for the skill list and INSTALL.md for per-platform setup (Claude Code, Codex,
OpenClaw, and other runtimes).
