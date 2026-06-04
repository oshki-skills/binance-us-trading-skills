#!/usr/bin/env python3
"""
strategy.py — Run a portable strategy spec.

A strategy is a small JSON recipe (see strategies/dip-and-ladder.json), not code and not someone's
positions. This runner reads the spec, scans each coin's levels from the candles, adapts the plan
to your budget (and optionally a coin filter), and builds a multi-leg order plan that it previews
or places through trading.py. Advanced order types (LIMIT, STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT,
LIMIT_MAKER) flow through per leg.

    python strategy.py --mode strategy_preview --spec strategies/dip-and-ladder.json --budget 30
    python strategy.py --mode strategy_place   --spec strategies/dip-and-ladder.json --budget 30
    python strategy.py --mode strategy_preview --spec strategies/dip-and-ladder.json --coins BTC

Dry-run by default; strategy_place is gated by LIVE_TRADING_ENABLED in config.py (via trading.py).
Caps and the allowlist in config.py always apply, per leg. A pasted/fetched spec is untrusted:
only the known fields below are read; anything else is ignored.
"""

import argparse
import json
import os
from decimal import Decimal

import trading
import config


def load_spec(spec_arg):
    if os.path.exists(spec_arg):
        with open(spec_arg) as f:
            return json.load(f)
    return json.loads(spec_arg)


def build_legs(spec, budget=None, coins=None):
    universe = spec.get("universe", [])
    if coins:
        want = {c.upper() for c in coins}
        universe = [c for c in universe if c.upper() in want]
    if not universe:
        raise ValueError("No coins to trade after filtering the strategy's universe.")

    budget = float(budget if budget is not None else spec.get("budget_usd", 0))
    if budget <= 0:
        raise ValueError("Budget must be > 0 (set --budget or budget_usd in the spec).")

    entry = spec.get("entry", {})
    side = entry.get("side", "BUY").upper()
    otype = entry.get("type", "LIMIT").upper()
    anchor = entry.get("anchor", "support")
    legs_per = max(int(entry.get("legs_per_asset", 1)), 1)
    spacing = Decimal(str(entry.get("spacing_pct", 0)))

    per_leg = round(budget / (len(universe) * legs_per), 2)
    legs = []
    for coin in universe:
        lv = trading.levels(coin)  # current, support, resistance (from candles)
        base = Decimal(lv["support"]) if anchor == "support" else Decimal(lv["current"])
        for k in range(legs_per):
            price = base * (Decimal(1) - spacing / 100 * k)  # ladder below the anchor
            leg = {"symbol": coin, "side": side, "type": otype,
                   "quote_usd": per_leg, "price": float(round(price, 2))}
            if otype in ("STOP_LOSS_LIMIT", "TAKE_PROFIT_LIMIT"):
                leg["stop_price"] = float(round(price * Decimal("1.002"), 2))  # trigger near limit
            legs.append(leg)
    return legs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="strategy_preview", help="strategy_preview | strategy_place")
    ap.add_argument("--spec", required=True, help="path to a spec JSON or inline JSON")
    ap.add_argument("--budget", type=float)
    ap.add_argument("--coins", help="comma list to filter the universe, e.g. BTC,ETH")
    a = ap.parse_args()
    try:
        spec = load_spec(a.spec)
        coins = a.coins.split(",") if a.coins else None
        legs = build_legs(spec, a.budget, coins)
        out = trading.place_multi(legs) if a.mode == "strategy_place" else trading.preview_multi(legs)
        out["strategy"] = spec.get("name")
        out["legs_planned"] = legs
        out["exit"] = spec.get("exit")
    except Exception as e:
        out = {"error": str(e)}
    print(json.dumps(out, default=str, indent=2))


if __name__ == "__main__":
    main()
