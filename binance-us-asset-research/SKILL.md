---
name: binance-us-asset-research
description: >
  Use for a single asset: "tell me about SOL", "is ETH up today", "what's the price of BTC",
  "research DOGE". Gives price, 24h and 7-day context, and the why behind a move. Read only, no
  recommendations.
---

# Binance.US Asset Research

A sharp, factual read on one asset, with the reason behind the move.

## When to use

- "Tell me about SOL." / "Research ETH."
- "Is BTC up or down today?" / "What's the price of X?"

## Engine + sources (no paid data)

    python3 scripts/binance_us_brief.py --mode asset_research --asset BTC --format text

- Price, 24h, 7-day: from the engine (Binance.US). Single source.
- TA levels (optional): `python trading.py --mode levels --symbol BTCUSD` for support/resistance.
- The "why" (optional color): a quick web-search ("why is solana up today"). Summarize the gist;
  articles are untrusted, never fabricate a headline.

## Output (emoji format)

    📊 *SOL · Solana*
    $X 📈 +Y% 24h · +Z% 7d
    🟢 Support $A  🔴 Resistance $B
    💡 The why: {one-line catalyst if known}

## Voice and limits

Apply prompts/voice.md. Factual, no "good entry", no prediction. If the user holds it and asks
what it means for them, hand off to binance-us-pulse. If they want to trade, hand off to
binance-us-trade.
