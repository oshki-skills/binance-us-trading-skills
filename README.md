# Binance.US Trading Skills

Natural-language spot trading and portfolio insight for **Binance.US**, packaged as agent skills.
Say what you want in plain English — your agent reasons over your real portfolio and live market
data, previews every trade, and places it **only after you confirm**.

Works in **Claude Code**, **OpenAI Codex**, **OpenClaw**, and any agent runtime that can read a
`SKILL.md` and run a Python CLI.

```
You:   How's my portfolio doing today?
Agent: 📊 Your bag today — up ~2% 📈, BTC carrying it. ~60% BTC, 25% ETH.

You:   Put $10 into BTC.
Agent: BUY 0.00015 BTC @ ~$64,960 · spending $10 · MARKET. Place it?
You:   yes
Agent: ✅ Filled. 0.00015 BTC @ $64,953, fee 6¢.
```

> ⚠️ **This software can place real trades with real money.** It ships in dry-run mode and stays
> there until you explicitly enable live trading. Read [Safety](#safety) before you flip the switch.

---

## What's inside

**Read & insight** (no orders, read-only):
| Skill | Use it for |
| --- | --- |
| `binance-us-briefing-engine` | "How's my portfolio?", "What's moving?", daily/watchlist brief |
| `binance-us-asset-research` | "Tell me about SOL" — price, 24h/7d context, the why |
| `binance-us-account-status` | "What's my balance?", "Am I ready to trade?" |
| `binance-us-pulse` | "Why is BTC moving and what does it mean for me?" |
| `binance-us-news` | Headlines ranked by what you actually hold, with dollar impact |
| `binance-us-scenario` | "What's my portfolio worth if BTC hits $100k?" — deterministic math |
| `binance-us-fund-account` | Step-by-step deposit guidance |
| `binance-us-learn` | Plain-English explainer ("what is staking?", "explain RSI") |

**Trade & strategy** (preview → confirm → place):
| Skill | Use it for |
| --- | --- |
| `binance-us-trade` | "Put $10 into BTC", "sell half my SOL", multi-leg limit plans |
| `binance-us-strategy` | "Scan BTC and ETH" — support/resistance from candles + a limit buy plan |

**Simulation** (no keys, no real orders):
| Skill | Use it for |
| --- | --- |
| `binance-us-sim` | "Run an agentic trading sim" — paper-trade a strategy on mock data |

---

## Quick start

```bash
git clone https://github.com/oshki-skills/binance-us-trading-skills
cd binance-us-trading-skills
pip install requests python-dotenv
```

Create a `.env` in the repo root with your [Binance.US API keys](#getting-api-keys):

```
BINANCE_US_API_KEY=your_key
BINANCE_US_SECRET_KEY=your_secret
LIVE_TRADING_ENABLED=false
```

Then open the folder in your agent and just chat. Full per-platform steps — Claude Code, Codex,
OpenClaw — are in **[INSTALL.md](INSTALL.md)**.

> The simulation skill (`binance-us-sim`) needs **no keys** and places **no real orders** — a safe
> way to try the project before connecting an account.

---

## How you use it

**Just chat.** Each skill carries a `description`; your agent reads them and triggers the right one
automatically. You don't have to name skills.

- *"How's my portfolio?"* → briefing-engine
- *"Tell me about SOL"* → asset-research
- *"Scan BTC and ETH"* → strategy
- *"Put $10 into BTC"* → trade (previews, waits for your confirm)
- *"Run an agentic sim"* → sim

**Or pick one by hand.** In Claude Code, type `/` to list skills and choose, e.g. `/binance-us-sim`.

The trade flow is always the same: the agent translates your words into a concrete order, shows you
a preview card, and places nothing until you clearly confirm.

---

## Safety

Safety is layered, and the strongest guarantees are enforced in code — not configurable.

**On by default:**
- **Dry-run.** Orders are validated but not placed until `LIVE_TRADING_ENABLED=true`.
- **Preview + explicit confirm** on every trade. No order is placed without your go-ahead.

**Tunable guardrails** (`config.py` — loosen or tighten as you like):
- Per-order USD cap
- Symbol allowlist
- Allowed order types
- Quote asset (USD vs USDT)

**Hard limits — enforced in `trading.py`, not configurable:**
- **No withdrawals, transfers, or API-key management.** Those endpoints are blocked and cannot be
  called, by any skill, ever.
- **Your keys only.** The code reads your credentials from your environment and nothing else.

**Your keys never leave your machine.** `.env` is gitignored. Use an API key scoped to **spot
trading only** — never enable withdrawals on the key you use here.

> This project does not provide financial advice. Skills describe markets factually and never tell
> you to buy or sell. You are responsible for every order you confirm.

---

## Getting API keys

1. Sign in to Binance.US → **API Management**.
2. Create an API key. **Enable only "Spot Trading."** Leave withdrawals disabled.
3. (Optional) Restrict the key to your IP for an extra layer.
4. Copy the key and secret into your `.env`. The secret is shown once — grab it immediately.

For read-only briefings you can use a key with no trading permission at all. The simulation skill
needs no key.

---

## Architecture

A simple, auditable design — skills are thin; all market access goes through two Python entrypoints.

```
scripts/binance_us_brief.py   Read engine — market data, balances, briefings
trading.py                    Execution — signs orders, candle levels, hard safety limits
sim.py                        Simulation — mock data only, no keys, no network
config.py                     Tunable knobs (cap, allowlist, order types, quote asset)
prompts/voice.md              Shared response voice
skills/                       One SKILL.md per workflow
.claude/skills/               Read skills, discovered automatically by Claude Code
CLAUDE.md / AGENTS.md         Runtime rules for agents
```

- **Skills never call an exchange API directly.** They shell out to the Python entrypoints and read
  JSON. That keeps every network call in one auditable place.
- **One source of truth:** Binance.US for price, portfolio, candles, and orders. Optional web
  search adds context/color only and never sets an order price. No third-party paid data feeds.

---

## Credits & license

Built on top of [`cmeiliu/binance-us-skills`](https://github.com/cmeiliu/binance-us-skills) — the
read-only briefing engine — and extended with an execution layer, strategy/insight/simulation
skills, and a sharper voice. See [LICENSE](LICENSE) for terms.
