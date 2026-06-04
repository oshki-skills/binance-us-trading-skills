---
name: binance-us-fund-account
description: >
  Use when the user asks how to add money or deposit: "how do I fund my account", "add cash",
  "deposit USD". Plain step-by-step guidance. No engine call, no moving funds.
---

# Binance.US Fund Account

Friendly, plain guidance for getting cash into the account. This skill explains; it never moves
funds (that's blocked, and it's the user's action in the app).

## When to use

- "How do I add money / fund my account?"
- "How do I deposit USD / crypto?"

## How to answer

- Walk the deposit options plainly (bank transfer / ACH, wire, crypto deposit), short and clear.
- Point the user to the in-app deposit flow to actually do it.
- If they ask what they can do once funded, hand off to binance-us-account-status or
  binance-us-trade.

## Output (emoji format)

    💵 *Adding funds*
    1. App → Deposit
    2. Pick USD (bank/ACH) or a crypto deposit
    3. Funds land, then you're ready to trade.

## Voice and limits

Apply prompts/voice.md. Guidance only. Never asks for or handles credentials. For account
problems (login, verification), point to Binance.US Support.
