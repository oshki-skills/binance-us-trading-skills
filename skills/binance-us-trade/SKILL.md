---
name: binance-us-trade
description: >
  Use when the user wants to buy or sell a specific asset on Binance.US in plain words
  (for example "put 10 dollars into BTC", "sell half my SOL"). Turns the words into a feasible
  spot order, previews it as a dry-run, and places it only after the user confirms. Spot only.
  Replaces the review-only spot-trade skill.
---

# Binance.US Trade Skill

## Overview

This skill turns natural-language intent into a real spot order on Binance.US:

- Interpret what the user asked for (asset, side, amount)
- Preview the order as a dry-run, validated against the configured limits
- Show the user the order, then place it only on explicit confirmation
- Report the actual fill (price and fee) after placing

There is no strategy to invent. The user's words are the instruction.

## Engine

This skill calls `trading.py` (not the read engine). Commands:

    python trading.py --mode preview_order --symbol BTCUSD --side BUY  --type MARKET --quote-usd 10
    python trading.py --mode place_order   --symbol BTCUSD --side BUY  --type MARKET --quote-usd 10
    python trading.py --mode place_order   --symbol SOLUSD --side SELL --type MARKET --pct 50
    python trading.py --mode open_orders   --symbol BTCUSD
    python trading.py --mode cancel_order  --symbol BTCUSD --order-id 12345

Buys use `--quote-usd` (dollars to spend). Sells use `--pct` (percent of holding) or `--quantity`.

## Interpreting the words

- "Put 10 dollars into BTC" -> BUY BTCUSD MARKET, --quote-usd 10
- "Buy 15 of ETH"           -> BUY ETHUSD MARKET, --quote-usd 15
- "Sell half my SOL"        -> SELL SOLUSD MARKET, --pct 50
- "Sell all my BTC"         -> SELL BTCUSD MARKET, --pct 100
- Default type is MARKET unless the user gives a limit price. Ask at most one short question, and
  only if the asset or amount is genuinely missing.

## The flow (always, in this order)

1. Preview (dry-run): run `preview_order`.
2. If it returns an error, explain it plainly and offer the nearest feasible option (for example
   "the minimum is about $X" or "that's above the $15 cap, want $15?"). Do not place anything.
3. If it succeeds, show the preview: asset, side, type, quantity, estimated price, estimated
   total. For market orders, note the price is an estimate.
4. Ask the user to confirm. They must clearly say to place it.
5. Place: run `place_order`. If live trading is off, say it stayed a dry-run. If it placed, read
   the FULL response `fills` and report the actual average fill price and total fee.

## Response fields (place_order, FULL response)

| Field | Meaning |
| --- | --- |
| status | FILLED, PARTIALLY_FILLED, etc. |
| executedQty | base asset filled |
| cummulativeQuoteQty | total quote (USD) spent or received |
| fills[] | each fill: price, qty, commission, commissionAsset |

## Use cases

1. Buy a fixed dollar amount of an asset
2. Sell a percentage of a holding
3. Place a limit order at a price the user names
4. Check and cancel open orders

## Notes

- Always preview before placing. Never place without explicit confirmation.
- Limits (cap, allowlist, order types, live flag) live in config.py. The skill respects whatever
  is set there.
- This skill never moves funds off the platform; withdrawal and transfer endpoints are blocked
  in trading.py and cannot be called.
- Apply the voice in prompts/voice.md.
