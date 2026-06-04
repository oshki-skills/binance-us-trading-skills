---
name: binance-us-scenario
description: >
  Use for what-if math on the user's own portfolio: "what's my portfolio worth if BTC hits 100k",
  "what if I'd put 500 into SOL last month", "how much is my ETH worth at 3000". Deterministic
  math on real holdings and live prices. No predictions, no advice.
---

# Binance.US Scenario (what-if on your real portfolio)

Personalized what-if math. A general chatbot can't do this, it doesn't know the user's holdings.
This is arithmetic on their real position, not a forecast.

## When to use

- "What's my portfolio worth if BTC hits $100k?"
- "What if I'd bought $500 of SOL a month ago?"
- "How much is my ETH worth at $3,000?"

## Inputs

- Holdings + quantities: `python3 scripts/binance_us_brief.py --mode portfolio_brief --format text`.
- Live price for the math: from the engine.
- The user's hypothetical (a target price, a past date, an amount).

## How to answer (deterministic only)

- Forward price scenario: hold quantities fixed, recompute value at the hypothetical price.
  "At BTC $100k, your 0.0X BTC is worth $Y, and your total is $Z (up $W from now)."
- Past what-if: use the amount and the historical price if available; if not, say what you'd need.
- Show the math plainly. No projection of whether it will happen, no probability, no advice.

## Output (emoji format)

    🔮 *What-if: BTC at $100k*
    Your 0.0X BTC → $Y (now $A)
    💵 Portfolio total → $Z (+$W)
    Just the math — not a prediction.

## Voice and limits

Apply prompts/voice.md. Deterministic math only. Never imply it will happen, never recommend. If
the user wants to act on it, hand off to binance-us-trade.
