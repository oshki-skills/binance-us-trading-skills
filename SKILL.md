---
name: binance-us-briefing-engine
description: >
  Use for portfolio and market briefings: "how's my portfolio today", "what's moving", "daily
  brief", "recap my watchlist", "am I ready to trade". Pulls balances, PnL, and live market
  context and gives a sharp, position-aware read. Read only.
---

# Binance.US Briefing Engine

Sharp daily/portfolio/market briefings. Lead with the takeaway, tie market moves to the user's
actual position, keep it short.

## When to use

- "How's my portfolio doing today?" / "How am I doing?"
- "What's moving in crypto?" / "Daily brief."
- "Recap my watchlist." / "Am I ready to trade?"

## Engine (read layer, the only API caller for this skill)

    python3 scripts/binance_us_brief.py --mode daily_brief --format text
    python3 scripts/binance_us_brief.py --mode portfolio_brief --format text
    python3 scripts/binance_us_brief.py --mode watchlist_brief --watchlist BTC,ETH,SOL
    python3 scripts/binance_us_brief.py --mode capital_readiness --format text

## Fetch discipline

- Pull the brief, then focus on the top 1-3 holdings by weight. Don't narrate every small bag.
- One market signal max (overall tone), unless the user asks for a full rundown.

## Cross-context bridge (the differentiator)

Always connect the market to the user's money. Not "BTC +3%" but "BTC +3%, and since you're ~60%
BTC that added ~$X to your position." Quantify in dollars when you can.

## Output (emoji format from prompts/voice.md)

    📊 *Your portfolio today*
    Up ~2% 📈 — BTC's carrying it.
    🟢 ~60% BTC, 25% ETH.
    💡 Today's BTC move added ~$X to your bag.

## Voice and limits

Apply prompts/voice.md: sharp, plain, fun. Describe the portfolio factually; no "too
concentrated", no "so buy", no predictions. If the user wants to act, hand off to binance-us-trade.
