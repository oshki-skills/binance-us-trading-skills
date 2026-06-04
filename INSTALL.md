# Install guide

These skills shell out to Python (the read engine, `scripts/trading.py`, `scripts/sim.py`), so installing them is
more than dropping in a `SKILL.md`. You need the repo's scripts, a couple of Python packages, and
your own Binance.US keys. The reliable setup on every platform is the same: **clone the repo and
work inside it** so the skills' relative paths (`python3 scripts/...`) resolve correctly.

## Contents
- [Prerequisites](#prerequisites)
- [Step 1 — Clone & install dependencies](#step-1--clone--install-dependencies)
- [Step 2 — Add your keys](#step-2--add-your-keys)
- [Step 3 — Connect your agent](#step-3--connect-your-agent)
  - [Claude Code](#claude-code)
  - [OpenAI Codex](#openai-codex)
  - [OpenClaw](#openclaw)
  - [Other runtimes](#other-runtimes)
- [Step 4 — Try it](#step-4--try-it)
- [Going live](#going-live)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.9+** and `pip`
- **Git**
- An agent runtime (Claude Code, Codex, OpenClaw, or similar)
- A **Binance.US** account and an API key — only needed for the trading and portfolio skills. The
  simulation skill (`binance-us-sim`) needs none.

---

## Step 1 — Clone & install dependencies

```bash
git clone https://github.com/oshki-skills/binance-us-trading-skills
cd binance-us-trading-skills
pip install requests python-dotenv
```

Confirm the two packages import:

```bash
python3 -c "import requests, dotenv; print('deps OK')"
```

---

## Step 2 — Add your keys

Create a file named `.env` in the repo root:

```
BINANCE_US_API_KEY=your_key
BINANCE_US_SECRET_KEY=your_secret
LIVE_TRADING_ENABLED=false
```

- Keep `LIVE_TRADING_ENABLED=false` to start. Everything runs as a dry-run until you change it.
- Create the API key in **Binance.US → API Management** with **Spot Trading enabled** and
  **withdrawals disabled**.
- `.env` is already gitignored. Confirm it:

```bash
git check-ignore .env    # prints ".env" → you're safe
```

> Read-only briefings work with a key that has no trading permission at all.

---

## Step 3 — Connect your agent

### Claude Code

The skills are discovered automatically when you open the folder.

1. Open the cloned folder in Claude Code (the desktop **Code** tab, or run `claude` in the repo
   from your terminal).
2. The read skills in `.claude/skills/` and the skill folders under `skills/` are picked up on
   their own. Claude Code also reads `CLAUDE.md` for runtime rules.
3. Start chatting (see [Step 4](#step-4--try-it)).

**Optional — install globally** so the family is available outside this folder. Use
`--full-depth` because this is a skill family with nested skills:

```bash
npx skills add oshki-skills/binance-us-trading-skills -g --agent claude --yes --full-depth --copy
```

A global install can break the relative `scripts/...` paths the skills call. If a skill errors
running Python, fall back to the clone-and-run setup above. Refresh later with `npx skills update`.

### OpenAI Codex

Codex reads **`AGENTS.md`** at the repo root automatically and follows it.

1. Open the cloned folder as your Codex working directory.
2. `AGENTS.md` tells Codex how the skills, engines, and safety rules fit together; the individual
   `SKILL.md` files under `skills/` describe each workflow and the exact CLI commands to run.
3. Ask in plain English ("how's my portfolio?", "preview $10 into BTC"). Codex will run the Python
   entrypoints and read their JSON output.

Because Codex executes shell commands, keep the working directory at the repo root so
`python3 scripts/...` and `python3 scripts/trading.py ...` resolve.

### OpenClaw

OpenClaw discovers the skills from the repo and supports a shared secrets file.

1. Open the cloned folder in OpenClaw.
2. Provide keys one of two ways:
   - the repo-root `.env` from [Step 2](#step-2--add-your-keys), **or**
   - the OpenClaw convention `~/.openclaw/secrets.env` with the same three variables
     (`BINANCE_US_API_KEY`, `BINANCE_US_SECRET_KEY`, `LIVE_TRADING_ENABLED`). The trading engine
     loads this path automatically.
3. Chat as usual; OpenClaw follows the same `AGENTS.md` runtime rules.

### Other runtimes

Any agent that can (a) read a `SKILL.md` description and (b) run a shell command will work. Point it
at the repo, have it read `AGENTS.md` for the rules, and let it call:

```bash
python3 scripts/binance_us_brief.py --mode daily_brief --format text   # reads
python3 scripts/trading.py --mode preview_order --symbol BTCUSD --side BUY --type MARKET --quote-usd 10
python3 scripts/sim.py --mode sim_run --strategy dip --scenario dip            # simulation, no keys
```

---

## Step 4 — Try it

Start with something that needs no keys and places nothing:

> **"Run an agentic trading simulation of the dip strategy."**

Then, once your keys are in, try the read layer:

> **"How's my portfolio doing today?"**

And a dry-run trade (still nothing placed while `LIVE_TRADING_ENABLED=false`):

> **"Put $10 into BTC."**

You'll get a preview card and a confirm prompt. Confirming while live trading is off simply tells
you it stayed a dry-run.

---

## Going live

When you're ready to place real orders:

1. Set `LIVE_TRADING_ENABLED=true` in your `.env`.
2. Optionally tune the guardrails in `config.py` (the per-order cap defaults to a small amount on
   purpose — raise it deliberately).
3. Run a small preview, confirm, and verify the fill before sizing up.

The hard limits in `scripts/trading.py` (no withdrawals/transfers/key management, your keys only) stay in
force regardless of any setting.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `Missing BINANCE_US_API_KEY / BINANCE_US_SECRET_KEY` | `.env` not found or wrong variable names. Confirm it's in the repo root and uses `BINANCE_US_SECRET_KEY` (with `_KEY`). |
| `401 ... Invalid API-key, IP, or permissions` | Enable **Spot Trading** on the key; if you set an IP allowlist, add your current IP (or make the key unrestricted). |
| A skill errors trying to run Python | You're likely outside the repo (global install). Run from inside the cloned folder so relative paths resolve. |
| Order rejected for size | It's below the exchange minimum or above your `config.py` cap. The error states which; adjust the amount or the cap. |
| Wrong skill triggers | Two descriptions overlap — sharpen the `description` line in the relevant `SKILL.md`. |
