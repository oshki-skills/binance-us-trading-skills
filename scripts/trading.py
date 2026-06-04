#!/usr/bin/env python3
"""
trading.py — Execution graft for the Binance.US skills repo.

Self-contained: signs its own requests, independent of the read engine. Handles single orders
(market or limit) and multi-leg LIMIT plans (e.g. "split $15 across BTC and ETH as limit orders").

Single order:
    python trading.py --mode preview_order --symbol BTCUSD --side BUY  --type MARKET --quote-usd 10
    python trading.py --mode place_order   --symbol BTCUSD --side BUY  --type LIMIT  --quote-usd 10 --price 64000
    python trading.py --mode place_order   --symbol SOLUSD --side SELL --type MARKET --pct 50

Multi-leg LIMIT plan (legs are JSON; each leg is its own validated order):
    python trading.py --mode preview_multi --legs '[
      {"symbol":"BTCUSD","side":"BUY","type":"LIMIT","quote_usd":7.5,"price":64000},
      {"symbol":"ETHUSD","side":"BUY","type":"LIMIT","quote_usd":7.5,"price":1800}]'
    python trading.py --mode place_multi   --legs '[ ... same shape ... ]'

Dry-run is the default. place_order / place_multi refuse unless LIVE_TRADING_ENABLED is true.
Open knobs (cap, allowlist, order types) live in config.py. Two things are NOT configurable and
enforced here: no withdrawal/transfer/key endpoints, and your keys only.

Env: BINANCE_US_API_KEY, BINANCE_US_SECRET_KEY.
"""

from __future__ import annotations
import os, sys, time, json, hmac, hashlib, argparse
from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(os.path.expanduser("~/.openclaw/secrets.env"))
except Exception:
    pass

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import config

BASE_URL = "https://api.binance.us"
API_KEY = os.getenv("BINANCE_US_API_KEY", "")
SECRET = os.getenv("BINANCE_US_SECRET_KEY", "")
TIMEOUT = 15


# --- Non-negotiable guards (NOT in config on purpose) -----------------------------------------
class SafetyError(Exception):
    pass

_ALLOWED_SIGNED = {"/api/v3/account", "/api/v3/myTrades", "/api/v3/openOrders",
                   "/api/v3/order", "/api/v3/order/test"}
_FORBIDDEN_FRAGMENTS = ("withdraw", "transfer", "apikey", "/sapi/", "/wapi/")


def _assert_endpoint_allowed(path: str) -> None:
    low = path.lower()
    for frag in _FORBIDDEN_FRAGMENTS:
        if frag in low:
            raise SafetyError(f"Blocked endpoint (moves funds / manages keys): {path}")
    if path not in _ALLOWED_SIGNED:
        raise SafetyError(f"Signed endpoint not allowed: {path}")


# --- HTTP -------------------------------------------------------------------------------------
def _public_get(path, params=None):
    r = requests.get(BASE_URL + path, params=params or {}, timeout=TIMEOUT)
    r.raise_for_status(); return r.json()


def _signed(method, path, params=None):
    _assert_endpoint_allowed(path)
    if not API_KEY or not SECRET:
        raise RuntimeError("Missing BINANCE_US_API_KEY / BINANCE_US_SECRET_KEY in env.")
    params = dict(params or {}); params["timestamp"] = int(time.time()*1000); params["recvWindow"] = 5000
    query = urlencode(params)
    sig = hmac.new(SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    r = requests.request(method, f"{BASE_URL}{path}?{query}&signature={sig}",
                         headers={"X-MBX-APIKEY": API_KEY}, timeout=TIMEOUT)
    if r.status_code >= 400:
        raise RuntimeError(f"Binance.US error {r.status_code}: {r.text}")
    return r.json()


def _sym(asset):
    a = asset.upper()
    return a if a.endswith(config.QUOTE_ASSET) else f"{a}{config.QUOTE_ASSET}"


# --- Market data + account ---------------------------------------------------------------------
def get_price(symbol):
    return Decimal(str(_public_get("/api/v3/ticker/price", {"symbol": _sym(symbol)})["price"]))


def get_filters(symbol):
    info = _public_get("/api/v3/exchangeInfo", {"symbol": _sym(symbol)})
    s = info["symbols"][0]
    out = {"minNotional": "0", "stepSize": "0", "minQty": "0", "tickSize": "0"}
    for f in s["filters"]:
        t = f["filterType"]
        if t in ("MIN_NOTIONAL", "NOTIONAL"):
            out["minNotional"] = f.get("minNotional", out["minNotional"])
        elif t == "LOT_SIZE":
            out["stepSize"] = f.get("stepSize", out["stepSize"]); out["minQty"] = f.get("minQty", out["minQty"])
        elif t == "PRICE_FILTER":
            out["tickSize"] = f.get("tickSize", out["tickSize"])
    return out


def free_balance(asset):
    for b in _signed("GET", "/api/v3/account")["balances"]:
        if b["asset"].upper() == asset.upper():
            return Decimal(b["free"])
    return Decimal("0")


# --- Validation (config-driven) ----------------------------------------------------------------
def _validate(symbol, side, order_type, filters, last_price, quote_usd, quantity, price):
    side, order_type = side.upper(), order_type.upper()
    if config.SYMBOL_ALLOWLIST is not None and symbol not in config.SYMBOL_ALLOWLIST:
        raise SafetyError(f"{symbol} not in allowlist. Set SYMBOL_ALLOWLIST=None to allow any.")
    if order_type not in config.ALLOWED_ORDER_TYPES:
        raise SafetyError(f"{order_type} not in ALLOWED_ORDER_TYPES {config.ALLOWED_ORDER_TYPES}.")
    if side not in {"BUY", "SELL"}:
        raise SafetyError(f"Invalid side: {side}.")
    if order_type == "LIMIT" and not price:
        raise SafetyError("LIMIT orders need a price.")

    ref = Decimal(str(price)) if (order_type == "LIMIT" and price) else last_price
    if quote_usd is not None:
        notional = Decimal(str(quote_usd)); qty = notional / ref
    elif quantity is not None:
        qty = Decimal(str(quantity)); notional = qty * ref
    else:
        raise SafetyError("Need quote_usd (buy) or quantity/pct (sell).")

    if config.MAX_ORDER_USD is not None and notional > Decimal(str(config.MAX_ORDER_USD)):
        raise SafetyError(f"~${notional:.2f} exceeds cap ${config.MAX_ORDER_USD}. "
                          f"Raise/remove MAX_ORDER_USD in config.py.")
    min_notional = Decimal(str(filters.get("minNotional", "0")))
    if min_notional and notional < min_notional:
        raise SafetyError(f"~${notional:.2f} is below the exchange minimum ${min_notional}.")
    step = Decimal(str(filters.get("stepSize", "0"))); min_qty = Decimal(str(filters.get("minQty", "0")))
    if step > 0:
        qty = (qty // step) * step
    if min_qty and qty < min_qty:
        raise SafetyError(f"Quantity {qty} below exchange minimum lot {min_qty}.")
    if qty <= 0:
        raise SafetyError("Quantity rounds to zero at the exchange lot size.")
    norm_price = None
    if order_type == "LIMIT":
        tick = Decimal(str(filters.get("tickSize", "0"))); p = Decimal(str(price))
        norm_price = (p / tick).to_integral_value(ROUND_DOWN) * tick if tick > 0 else p
    return {"symbol": symbol, "side": side, "type": order_type, "quantity": qty,
            "price": norm_price, "ref_price": ref, "est_notional_usd": notional}


def _resolve_sell_qty(symbol, side, quantity, pct):
    if side.upper() == "SELL" and pct is not None and quantity is None:
        base = _sym(symbol)[:-len(config.QUOTE_ASSET)]
        return free_balance(base) * Decimal(str(pct)) / Decimal("100")
    return Decimal(str(quantity)) if quantity is not None else None


def _params(symbol, n, quote_usd):
    p = {"symbol": symbol, "side": n["side"], "type": n["type"]}
    if n["type"] == "MARKET" and n["side"] == "BUY" and quote_usd is not None:
        p["quoteOrderQty"] = str(Decimal(str(quote_usd)))
    else:
        p["quantity"] = str(n["quantity"])
    if n["type"] == "LIMIT":
        p["price"] = str(n["price"]); p["timeInForce"] = "GTC"
    return p


def _preview_dict(n):
    return {"symbol": n["symbol"], "side": n["side"], "type": n["type"],
            "quantity": str(n["quantity"]), "price": (str(n["price"]) if n["price"] else None),
            "ref_price": str(n["ref_price"]), "est_notional_usd": float(n["est_notional_usd"])}


# --- Single order ------------------------------------------------------------------------------
def preview_order(symbol, side, order_type, quote_usd=None, quantity=None, pct=None, price=None):
    symbol = _sym(symbol)
    quantity = _resolve_sell_qty(symbol, side, quantity, pct)
    n = _validate(symbol, side, order_type, get_filters(symbol), get_price(symbol), quote_usd, quantity, price)
    _signed("POST", "/api/v3/order/test", _params(symbol, n, quote_usd))
    return {"ok": True, "dry_run": True, "preview": _preview_dict(n)}


def place_order(symbol, side, order_type, quote_usd=None, quantity=None, pct=None, price=None):
    if not config.LIVE_TRADING_ENABLED:
        raise SafetyError("LIVE_TRADING_ENABLED is false, so this stayed a dry-run. "
                          "Set it true in config.py (or env) to place real orders.")
    symbol = _sym(symbol)
    quantity = _resolve_sell_qty(symbol, side, quantity, pct)
    n = _validate(symbol, side, order_type, get_filters(symbol), get_price(symbol), quote_usd, quantity, price)
    return {"ok": True, "dry_run": False, "order": _signed("POST", "/api/v3/order", _params(symbol, n, quote_usd))}


# --- Multi-leg LIMIT plan ----------------------------------------------------------------------
def _prep_leg(leg):
    symbol = _sym(leg["symbol"])
    qty = _resolve_sell_qty(symbol, leg["side"], leg.get("quantity"), leg.get("pct"))
    n = _validate(symbol, leg["side"], leg.get("type", "LIMIT"), get_filters(symbol),
                  get_price(symbol), leg.get("quote_usd"), qty, leg.get("price"))
    return symbol, n, leg.get("quote_usd")


def preview_multi(legs):
    previews, total = [], Decimal("0")
    for leg in legs:
        symbol, n, q = _prep_leg(leg)
        _signed("POST", "/api/v3/order/test", _params(symbol, n, q))  # validate each, no execution
        total += n["est_notional_usd"]; previews.append(_preview_dict(n))
    return {"ok": True, "dry_run": True, "legs": previews, "total_usd": float(total)}


def place_multi(legs):
    if not config.LIVE_TRADING_ENABLED:
        raise SafetyError("LIVE_TRADING_ENABLED is false, so this stayed a dry-run. No legs placed.")
    prepared = [_prep_leg(leg) for leg in legs]  # validate ALL before placing ANY
    results = []
    for symbol, n, q in prepared:
        try:
            results.append({"symbol": symbol, "ok": True, "order": _signed("POST", "/api/v3/order", _params(symbol, n, q))})
        except Exception as e:
            results.append({"symbol": symbol, "ok": False, "error": str(e)})
    return {"ok": True, "dry_run": False, "legs": results}


def open_orders(symbol):
    return _signed("GET", "/api/v3/openOrders", {"symbol": _sym(symbol)})


def cancel_order(symbol, order_id):
    return _signed("DELETE", "/api/v3/order", {"symbol": _sym(symbol), "orderId": order_id})


# --- Strategy scan: support/resistance from candles (clear source, no mystery) -----------------
def levels(symbol, interval="1d", lookback=14):
    """
    Simple, transparent levels from Binance.US candles:
      support    = lowest low over the lookback window
      resistance = highest high over the lookback window
      suggested_limit_buy = support (a 'buy near recent support' level)
    Observational only. Not a prediction.
    """
    kl = _public_get("/api/v3/klines", {"symbol": _sym(symbol), "interval": interval, "limit": lookback})
    highs = [Decimal(str(k[2])) for k in kl]
    lows = [Decimal(str(k[3])) for k in kl]
    closes = [Decimal(str(k[4])) for k in kl]
    support, resistance = min(lows), max(highs)
    current = get_price(symbol)
    span = (resistance - support)
    pos_pct = float((current - support) / span * 100) if span > 0 else None
    first, last = closes[0], closes[-1]
    trend = "up" if last > first else ("down" if last < first else "flat")
    change_pct = float((last - first) / first * 100) if first else None
    dist_support = float((current - support) / current * 100) if current else None
    dist_resist = float((resistance - current) / current * 100) if current else None
    return {
        "symbol": _sym(symbol), "lookback_days": lookback,
        "current": str(current), "support": str(support), "resistance": str(resistance),
        "trend": trend, "window_change_pct": (round(change_pct, 1) if change_pct is not None else None),
        "position_in_range_pct": (round(pos_pct, 1) if pos_pct is not None else None),
        "pct_above_support": (round(dist_support, 1) if dist_support is not None else None),
        "pct_below_resistance": (round(dist_resist, 1) if dist_resist is not None else None),
        "suggested_limit_buy": str(support),
    }


# --- CLI --------------------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True)
    p.add_argument("--symbol"); p.add_argument("--side")
    p.add_argument("--type", dest="order_type", default="MARKET")
    p.add_argument("--quote-usd", dest="quote_usd", type=float)
    p.add_argument("--quantity", type=float); p.add_argument("--pct", type=float)
    p.add_argument("--price", type=float); p.add_argument("--order-id", dest="order_id", type=int)
    p.add_argument("--legs")
    p.add_argument("--interval", default="1d"); p.add_argument("--limit", type=int, default=14)
    a = p.parse_args()
    try:
        if a.mode == "preview_order":
            out = preview_order(a.symbol, a.side, a.order_type, a.quote_usd, a.quantity, a.pct, a.price)
        elif a.mode == "place_order":
            out = place_order(a.symbol, a.side, a.order_type, a.quote_usd, a.quantity, a.pct, a.price)
        elif a.mode == "preview_multi":
            out = preview_multi(json.loads(a.legs))
        elif a.mode == "place_multi":
            out = place_multi(json.loads(a.legs))
        elif a.mode == "levels":
            out = levels(a.symbol, a.interval, a.limit)
        elif a.mode == "open_orders":
            out = open_orders(a.symbol)
        elif a.mode == "cancel_order":
            out = cancel_order(a.symbol, a.order_id)
        else:
            out = {"error": f"unknown mode {a.mode}"}
    except (SafetyError, RuntimeError, ValueError, requests.RequestException) as e:
        out = {"error": str(e)}
    print(json.dumps(out, default=str, indent=2))


if __name__ == "__main__":
    main()
