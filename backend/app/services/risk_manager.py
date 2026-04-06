"""Risk Manager — pure mathematical position sizing and strategy calculation.

Rules implemented (from CLAUDE.md business rules):
  RN-1: max risk per trade = 1% of capital (configurable up to 3%, NEVER more)
  RN-2: position_size = (capital × risk_pct) / (entry - stop_loss)
  RN-3: stop_loss = entry - (ATR × 2.5)  [dynamic, ATR-based]
  RN-4: TP1 = entry + ATR×1.5 → sell 33%
         TP2 = entry + ATR×2.5 → sell 33%
         TP3 = trailing stop at max_price - ATR×2.0 → hold 34%
  RN-5: R:R ratio must be ≥ 2.0 or strategy is marked not recommended

Python calculates everything. The LLM only narrates results.
"""

from __future__ import annotations

from dataclasses import dataclass

MAX_RISK_PCT = 0.03  # 3% hard cap (RN-1)
MIN_RR_RATIO = 2.0   # Minimum recommended R:R (RN-5)


@dataclass
class StrategyResult:
    ticker: str
    direction: str          # "LONG" | "SHORT"
    entry_price: float
    stop_loss: float
    tp1: float
    tp2: float
    tp3_trailing_atr_mult: float   # TP3 = max_price - (ATR × this)
    n_shares: float                # fractional allowed for forex/crypto
    risk_amount: float             # dollars at risk
    rr_ratio: float
    is_recommended: bool
    atr_used: float
    sl_atr_mult: float
    tp1_pct: float                 # 33%
    tp2_pct: float                 # 33%
    tp3_pct: float                 # 34%
    warning: str | None = None


class RiskManager:
    """Calculates position sizing, stops, and take-profits for a given asset."""

    def calculate_strategy(
        self,
        ticker: str,
        direction: str,
        capital: float,
        risk_pct: float,
        entry_price: float,
        atr_value: float,
        sl_atr_mult: float = 2.5,
    ) -> StrategyResult:
        """Calculate a complete strategy for the given parameters.

        Args:
            ticker:       Asset symbol (e.g. "AAPL", "BTC-USD")
            direction:    "LONG" or "SHORT"
            capital:      Total account capital in USD
            risk_pct:     Fraction of capital to risk (0.01 = 1%)
            entry_price:  Planned entry price
            atr_value:    Current ATR-14 value for the asset
            sl_atr_mult:  ATR multiplier for stop loss (default 2.5)
        """
        direction = direction.upper()
        warning: str | None = None

        # ── Validate inputs ──────────────────────────────────────────────────
        if capital <= 0:
            raise ValueError("Capital must be positive")
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        if risk_pct > MAX_RISK_PCT:
            risk_pct = MAX_RISK_PCT
            warning = f"Risk % capped at {MAX_RISK_PCT*100:.0f}% (RN-1)"
        if risk_pct <= 0:
            raise ValueError("risk_pct must be positive")
        if atr_value <= 0:
            # Fallback: use 1% of price as ATR if unavailable
            atr_value = entry_price * 0.01
            warning = "ATR was 0 — used 1% of price as fallback"

        # ── Stop Loss (RN-3) ─────────────────────────────────────────────────
        if direction == "LONG":
            stop_loss = entry_price - (atr_value * sl_atr_mult)
            sl_distance = entry_price - stop_loss
        else:  # SHORT
            stop_loss = entry_price + (atr_value * sl_atr_mult)
            sl_distance = stop_loss - entry_price

        if sl_distance <= 0:
            raise ValueError("Stop loss distance must be positive")

        # ── Position Sizing (RN-2) ───────────────────────────────────────────
        risk_amount = capital * risk_pct
        n_shares = risk_amount / sl_distance

        # ── Take Profits (RN-4) ──────────────────────────────────────────────
        if direction == "LONG":
            tp1 = entry_price + (atr_value * 1.5)
            tp2 = entry_price + (atr_value * 2.5)
        else:  # SHORT
            tp1 = entry_price - (atr_value * 1.5)
            tp2 = entry_price - (atr_value * 2.5)

        tp3_trailing_mult = 2.0  # TP3 = max_price - ATR × 2.0 (trailing)

        # ── R:R Ratio (RN-5) ────────────────────────────────────────────────
        tp2_distance = abs(tp2 - entry_price)
        rr_ratio = tp2_distance / sl_distance

        is_recommended = rr_ratio >= MIN_RR_RATIO

        return StrategyResult(
            ticker=ticker,
            direction=direction,
            entry_price=round(entry_price, 8),
            stop_loss=round(stop_loss, 8),
            tp1=round(tp1, 8),
            tp2=round(tp2, 8),
            tp3_trailing_atr_mult=tp3_trailing_mult,
            n_shares=round(n_shares, 4),
            risk_amount=round(risk_amount, 2),
            rr_ratio=round(rr_ratio, 4),
            is_recommended=is_recommended,
            atr_used=round(atr_value, 8),
            sl_atr_mult=sl_atr_mult,
            tp1_pct=33.0,
            tp2_pct=33.0,
            tp3_pct=34.0,
            warning=warning,
        )
