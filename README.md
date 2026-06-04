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

**Hard limits — enforced in `scripts/trading.py`, not configurable:**
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
scripts/trading.py            Execution — signs orders, candle levels, hard safety limits
scripts/sim.py                Simulation — mock data only, no keys, no network
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

## Building your own strategy

Strategies are portable JSON files — no code required. Drop one in `strategies/` and run it with
`strategy.py`. The engine reads the spec, scans candle-derived support/resistance for each coin,
and builds a multi-leg limit order plan priced to your budget.

### Anatomy of a strategy file

```json
{
  "name": "My Strategy",
  "description": "One line on what this does.",
  "author": "you",
  "universe": ["BTC", "ETH", "SOL"],
  "budget_usd": 50,
  "entry": {
    "side": "BUY",
    "type": "LIMIT",
    "anchor": "support",
    "legs_per_asset": 2,
    "spacing_pct": 1.5
  },
  "exit": {
    "take_profit_pct": 6,
    "note": "Informational — place as a TAKE_PROFIT_LIMIT sell if you hold the asset."
  },
  "spot_only": true
}
```

| Field | What it does |
| --- | --- |
| `universe` | Coins to trade. Any Binance.US-listed symbol. |
| `budget_usd` | Default budget. Override at runtime with `--budget`. |
| `entry.anchor` | `"support"` prices legs at candle-derived support; `"current"` prices from the live price. |
| `entry.legs_per_asset` | How many limit orders per coin. Budget splits evenly across all legs. |
| `entry.spacing_pct` | % gap between each ladder step (leg 2 = leg 1 price × (1 − spacing_pct/100)). |
| `exit.take_profit_pct` | Target gain shown in the plan card. Not placed automatically — shown as a level. |

### Running a strategy

```bash
# Preview — scan levels, build the plan, validate against exchange filters. Nothing places.
python strategy.py --mode strategy_preview --spec strategies/dip-and-ladder.json --budget 20

# Filter to a subset of the universe
python strategy.py --mode strategy_preview --spec strategies/dip-and-ladder.json --coins BTC

# Place — sends all legs as live limit orders (requires LIVE_TRADING_ENABLED=true)
python strategy.py --mode strategy_place --spec strategies/dip-and-ladder.json --budget 20
```

Or just chat: *"Run the Dip & Ladder strategy on BTC and ETH with $20"* — the
`binance-us-strategy-market` skill handles the whole flow.

### The included strategy

**`strategies/dip-and-ladder.json`** — Dip & Ladder  
Ladders two limit buy orders per coin near recent candle support, spaced 1.5% apart. Default
universe: BTC + ETH. Default budget: $30. Take-profit target: +6%. A straightforward starting
point you can copy and modify.

### Tips for writing your own

- Keep `legs_per_asset × len(universe) × per-leg size` within your `MAX_ORDER_USD` cap in
  `config.py`, or raise the cap first.
- `spacing_pct: 0` gives you a single entry per coin at the anchor price (no ladder).
- Add more coins to `universe` freely — the budget splits automatically across all legs.
- The spec is untrusted input: only the documented fields above are read by `strategy.py`.
  Anything else is ignored, so extra notes or metadata in the file are safe.
- Strategies are read-only descriptions of intent. The safety limits in `scripts/trading.py`
  (cap, allowlist, no withdrawals) apply to every leg regardless of what the spec says.

---

## Credits & license

Built on top of [`cmeiliu/binance-us-skills`](https://github.com/cmeiliu/binance-us-skills) — the
read-only briefing engine — and extended with an execution layer, strategy/insight/simulation
skills, and a sharper voice. See [LICENSE](LICENSE) for terms.
