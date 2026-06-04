---
name: binance-us-account-status
description: >
  Use for account state: "what's my balance", "what cash do I have", "am I ready to trade",
  "what's blocking my deposit". Reports balances and trade-readiness plainly. Read only.
---

# Binance.US Account Status

Balances and readiness, no fluff.

## When to use

- "What's my balance / buying power?"
- "Am I ready to trade?" / "What's blocking me?"

## Engine

    python3 scripts/binance_us_brief.py --mode capital_readiness --format text
    python3 scripts/binance_us_brief.py --mode portfolio_brief --format text

(If the engine exposes a dedicated account/status mode, prefer it; otherwise these cover balances
and readiness.)

## Output (emoji format)

    💼 *Account status*
    💵 Cash available: $X
    🟢 Holdings: BTC, ETH, SOL (~$Y total)
    ✅ Ready to trade — or — ⚠️ {what's blocking}

Surface trade/deposit readiness plainly. Don't dump every tiny balance.

## Voice and limits

Apply prompts/voice.md. Factual. For how to add money, hand off to binance-us-fund-account. To
trade, hand off to binance-us-trade.
