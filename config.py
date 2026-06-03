"""
config.py — Open knobs for your prototype. This is YOUR account; tune freely.

Everything here is meant to be loosened. The two things that are NOT here, and are not
configurable on purpose, live in trading.py: the block on withdrawal/transfer/key endpoints,
and the use of your own keys only. Those stay regardless.
"""

import os

# Live trading. Dry-run (/order/test) until this is true. Flip via env or here.
LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"

# Max USD per order. Set to None to remove the cap entirely.
MAX_ORDER_USD = 15          # or None for no cap

# Which symbols may trade. Set to None to allow ANY Binance.US-listed pair.
SYMBOL_ALLOWLIST = None     # or e.g. {"BTCUSD", "ETHUSD", "SOLUSD"}

# Order types you allow. Add STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT, etc. if you want them.
ALLOWED_ORDER_TYPES = {"MARKET", "LIMIT"}

# Binance.US USD pairs by default (BTCUSD). Change to "USDT" if your account uses USDT pairs.
QUOTE_ASSET = "USD"
