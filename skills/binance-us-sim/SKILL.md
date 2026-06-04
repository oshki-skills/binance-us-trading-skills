---
name: binance-us-sim
description: >
  Use when the user wants to simulate or backtest a strategy with no real money: "simulate the dip
  strategy", "run an agentic trading sim", "what would this strategy have done", "paper trade
  this". Runs a mock simulation and narrates the agent's decisions and simulated PnL. No real
  orders, no account, no keys. Everything is mock data.
---

# Binance.US Agentic Trading Simulation (mock)

Show an agent trading a strategy over a mock price path, risk-free. Nothing here is real: no
account, no API, no orders. Always say it's a simulation on mock data.

## When to use

- "Run an agentic trading simulation."
- "Simulate the dip-buy strategy." / "Paper trade this."
- "What would buying dips have done?"

## Engine (sim.py — pure mock, no network, no keys)

    python sim.py --mode sim_run --strategy dip --scenario dip --budget 1000
    python sim.py --mode sim_run --scenario bull
    python sim.py --mode sim_run --scenario choppy --take-profit 4 --slice-usd 150

Scenarios are scripted mock paths (dip / bull / choppy). The strategy buys when price drops off
its rolling high and takes profit at a set gain. All fills are simulated.

## How to narrate it

Walk the run as if you're watching the agent work, then give the simulated result. Emoji format:

    🤖 *Agentic sim — dip strategy* (mock data)
    Step 3 📉 BTC $62,098 → 🟢 agent buys $100 (sim)
    Step 3 📉 ETH $1,746 → 🟢 agent buys $100 (sim)
    Step 7 📈 ETH $1,834 → 🔴 takes profit +$5.05 (sim)
    Step 8 📈 BTC $65,220 → 🔴 takes profit +$5.03 (sim)
    💵 Final: $1,010 · PnL +$10 (+1%) — simulated, mock data

## Hard rule

Say "simulation" and "mock data" clearly. This skill never places a real order and never touches
a real account. If the user then wants to do it for real, hand off to binance-us-trade (which
previews and confirms on their actual account). Apply prompts/voice.md.
