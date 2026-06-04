---
name: binance-us-strategy
description: >
  Use when the user wants to scan a setup and act on it: "scan BTC and ETH", "find me levels and
  set up buys", "run the dip strategy". Reads trend + support/resistance from the candles,
  presents a sharp emoji scan card, and proposes a multi-leg LIMIT buy at support for BTC and ETH.
  Preview first, place only on confirm. Spot only. Observational, not a prediction.
---

# Binance.US Strategy Scan

The agentic beat: scan levels, present a setup, place limit orders the user confirms. Simple and
transparent on purpose: buy near recent support. Keep responses sharp.

## When to use

- "Scan BTC and ETH and find me levels."
- "Set up dip buys near support."
- "Run the strategy scan."

## Engine + sources (no paid data)

- Levels (the numbers the orders use): `python trading.py --mode levels --symbol BTCUSD` and
  `--symbol ETHUSD`. Returns trend, support (recent low), resistance (recent high), where price
  sits, and a suggested limit-buy at support. From the candles. This is the source of the order
  prices.
- Optional color: a quick web-search for context. Never sets the order price; that comes from
  `levels`. Never fabricate a number.

## The flow

1. Run `levels` for BTC and ETH.
2. Show the scan card per asset (format below).
3. Propose a multi-leg LIMIT buy: split the budget across BTC and ETH, each a LIMIT BUY at that
   asset's support. Build the legs JSON, run `preview_multi`.
4. Show the combined plan + total. Ask to confirm.
5. On confirm, `place_multi`. A limit usually rests (⏳ "resting at your level"), don't fake a
   fill. If live is off, say it stayed a dry-run.

## Output format (sharp, with emojis)

Scan card per asset:

    📊 *{ASSET}* · {trend} this week ({window_change_pct}%)
    Price ${current} · 📍 {position_in_range_pct}% up from support
    🟢 Support ${support}  🔴 Resistance ${resistance}

Proposed plan:

    🎯 *Dip buys* (limit, at support)
    • BTC ${leg} @ ${btc_support}
    • ETH ${leg} @ ${eth_support}
    💵 Total ${total} — confirm to place?

Placed:

    ✅ *Placed*
    • BTC ⏳ resting @ ${btc_support}
    • ETH ⏳ resting @ ${eth_support}
    📈 Two limits live. Fills if price taps your levels.

## Limits

Apply prompts/voice.md. Levels are observational areas from recent candles, not a prediction. A
light "levels, not promises" is fine; no "this will pump", no guaranteed gains. Always preview,
always confirm, respect config.py. Never moves funds off the platform.
