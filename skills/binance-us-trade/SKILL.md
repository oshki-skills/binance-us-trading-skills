---
name: binance-us-trade
description: >
  Use when the user wants to buy or sell on Binance.US in plain words: a single order ("put 10
  dollars into BTC", "sell half my SOL"), a limit order at a price they name, or a multi-leg
  split ("split 15 dollars across BTC and ETH as limit orders"). Always previews as a dry-run and
  places only after the user confirms. Spot only.
---

# Binance.US Trade Skill

## Overview

Turns natural-language intent into real spot orders, single or multi-leg, market or limit:

- Interpret what the user asked for
- Preview as a dry-run, validated against the configured limits
- Place only on explicit confirmation
- Report the actual fills (price and fee) after placing

## Engine (trading.py)

Single order:

    python trading.py --mode preview_order --symbol BTCUSD --side BUY  --type MARKET --quote-usd 10
    python trading.py --mode place_order   --symbol BTCUSD --side BUY  --type LIMIT  --quote-usd 10 --price 64000
    python trading.py --mode place_order   --symbol SOLUSD --side SELL --type MARKET --pct 50

Multi-leg LIMIT plan (legs are JSON; each leg is its own validated limit order):

    python trading.py --mode preview_multi --legs '[
      {"symbol":"BTCUSD","side":"BUY","type":"LIMIT","quote_usd":7.5,"price":64000},
      {"symbol":"ETHUSD","side":"BUY","type":"LIMIT","quote_usd":7.5,"price":1800}]'
    python trading.py --mode place_multi   --legs '[ ...same shape... ]'

Buys use --quote-usd. Sells use --pct or --quantity. LIMIT legs require a price.

## Interpreting the words

- "Put 10 dollars into BTC"                 -> single MARKET BUY, --quote-usd 10
- "Buy 10 of ETH at 1800"                   -> single LIMIT BUY, --quote-usd 10 --price 1800
- "Sell half my SOL"                        -> single MARKET SELL, --pct 50
- "Split 15 dollars across BTC and ETH as limit orders" -> multi-leg: two LIMIT BUY legs, ~7.5
  each. If the user didn't give prices, use the current price for each leg as the limit (fetch via
  the engine) and tell them that's what you used. Ask at most one short question.

## The flow (always, in this order)

1. Preview (dry-run): preview_order or preview_multi.
2. On error, explain it plainly and offer the nearest feasible option (cap, exchange minimum,
   balance). Place nothing.
3. On success, show the preview. Single: asset, side, type, quantity, est. price, est. total.
   Multi: each leg's asset/side/price/quantity/est. total, plus the combined total.
4. Ask the user to confirm. They must clearly say to place it.
5. Place: place_order / place_multi. If live is off, say it stayed a dry-run. If it placed, read
   the FULL response fills and report the actual average price and fee per order. For a multi-leg,
   report each leg and note any leg that failed.

## Response fields (place, FULL response)

| Field | Meaning |
| --- | --- |
| status | FILLED, PARTIALLY_FILLED, NEW (resting limit), etc. |
| executedQty | base asset filled |
| cummulativeQuoteQty | total quote (USD) |
| fills[] | price, qty, commission, commissionAsset |

Note: a LIMIT order may rest as NEW instead of filling immediately. Say so plainly ("placed,
resting at your price") rather than implying it filled.

## Use cases

1. Buy a fixed dollar amount (market)
2. Limit order at a user-named price
3. Sell a percentage of a holding
4. Multi-leg limit split across two or more assets in one previewed plan

## Notes

- Always preview before placing. Never place without explicit confirmation.
- Limits (cap, allowlist, order types, live flag) live in config.py; respect whatever is set.
- Never moves funds off the platform; withdrawal/transfer endpoints are blocked in trading.py.
- Apply the voice in prompts/voice.md.
