#!/usr/bin/env python3
"""
sim.py — Agentic trading SIMULATION. Mock data only.

Runs a simple strategy over a scripted mock price path and narrates the agent's decisions plus a
simulated PnL. This is a pure simulation: it touches no real account, no API, no keys, no network,
and places no real orders. It exists to *show* an agent trading a strategy, risk-free.

    python sim.py --mode sim_run --strategy dip --scenario dip --budget 1000
    python sim.py --mode sim_run --scenario bull
    python sim.py --mode sim_run --scenario choppy --slice-usd 150 --take-profit 4

Everything below is fabricated mock data for demonstration. None of it is market reality.
"""

import argparse
import json

# Scripted mock scenarios: per-step % move for each asset. Deterministic, for clean demos.
SCENARIOS = {
    "dip":    {"BTC": [0.5, -2, -3, -2, 1, 3, 2, 1, 2, 1],
               "ETH": [0.3, -2.5, -3.5, -1, 2, 3, 1, 2, 1, 1]},
    "bull":   {"BTC": [1, 2, 1, 3, 1, 2, 1, 2, 1, 2],
               "ETH": [1, 1, 2, 2, 1, 3, 1, 1, 2, 1]},
    "choppy": {"BTC": [2, -2, 1, -1, 2, -2, 1, -1, 2, -1],
               "ETH": [-1, 2, -2, 1, -1, 2, -1, 1, -2, 1]},
}
START = {"BTC": 65000.0, "ETH": 1850.0}


def run(strategy="dip", scenario="dip", budget=1000.0,
        dip_threshold=3.0, take_profit=5.0, slice_usd=100.0):
    moves = SCENARIOS.get(scenario, SCENARIOS["dip"])
    steps = len(next(iter(moves.values())))
    price = dict(START)
    high = dict(START)
    cash = budget
    pos = {a: {"qty": 0.0, "cost": 0.0} for a in START}
    log = []

    for i in range(steps):
        for a in price:
            price[a] *= (1 + moves[a][i] / 100.0)
            high[a] = max(high[a], price[a])

        actions = []
        for a in price:
            p = price[a]
            drawdown = (high[a] - p) / high[a] * 100 if high[a] else 0
            # Dip-buy: bought once when price has fallen dip_threshold% off its rolling high.
            if strategy == "dip" and drawdown >= dip_threshold and cash >= slice_usd and pos[a]["qty"] == 0:
                qty = slice_usd / p
                cash -= slice_usd
                pos[a] = {"qty": qty, "cost": p}
                actions.append(f"bought ${slice_usd:.0f} {a} @ ${p:,.0f}")
            # Take profit when up take_profit% from the simulated entry.
            elif pos[a]["qty"] > 0 and (p - pos[a]["cost"]) / pos[a]["cost"] * 100 >= take_profit:
                proceeds = pos[a]["qty"] * p
                gain = proceeds - pos[a]["qty"] * pos[a]["cost"]
                cash += proceeds
                actions.append(f"sold {a} @ ${p:,.0f}, +${gain:.2f}")
                pos[a] = {"qty": 0.0, "cost": 0.0}

        log.append({"step": i + 1,
                    "prices": {a: round(price[a], 2) for a in price},
                    "actions": actions})

    holdings_value = sum(pos[a]["qty"] * price[a] for a in price)
    final = cash + holdings_value
    return {
        "mock": True, "disclaimer": "simulated mock data, no real orders",
        "scenario": scenario, "strategy": strategy, "start_budget": budget,
        "steps": log,
        "final_cash": round(cash, 2), "holdings_value": round(holdings_value, 2),
        "final_value": round(final, 2),
        "pnl": round(final - budget, 2),
        "pnl_pct": round((final - budget) / budget * 100, 2),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="sim_run")
    ap.add_argument("--strategy", default="dip")
    ap.add_argument("--scenario", default="dip", help="dip | bull | choppy")
    ap.add_argument("--budget", type=float, default=1000.0)
    ap.add_argument("--dip-threshold", dest="dip", type=float, default=3.0)
    ap.add_argument("--take-profit", dest="tp", type=float, default=5.0)
    ap.add_argument("--slice-usd", dest="slice", type=float, default=100.0)
    a = ap.parse_args()
    print(json.dumps(run(a.strategy, a.scenario, a.budget, a.dip, a.tp, a.slice), indent=2))


if __name__ == "__main__":
    main()
