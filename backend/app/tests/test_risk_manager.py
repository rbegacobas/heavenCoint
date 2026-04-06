"""Unit tests for the RiskManager service."""

import pytest
from app.services.risk_manager import MAX_RISK_PCT, RiskManager, StrategyResult

rm = RiskManager()


def _calc(
    ticker="AAPL",
    direction="LONG",
    capital=10_000.0,
    risk_pct=0.01,
    entry_price=200.0,
    atr_value=5.0,
) -> StrategyResult:
    return rm.calculate_strategy(
        ticker=ticker,
        direction=direction,
        capital=capital,
        risk_pct=risk_pct,
        entry_price=entry_price,
        atr_value=atr_value,
    )


# ── LONG strategy ─────────────────────────────────────────────────────────────

def test_long_stop_loss():
    s = _calc()
    # SL = entry - ATR × 2.5 = 200 - 12.5 = 187.5
    assert s.stop_loss == pytest.approx(187.5)


def test_long_tp1():
    s = _calc()
    # TP1 = entry + ATR × 1.5 = 200 + 7.5 = 207.5
    assert s.tp1 == pytest.approx(207.5)


def test_long_tp2():
    s = _calc()
    # TP2 = entry + ATR × 2.5 = 200 + 12.5 = 212.5
    assert s.tp2 == pytest.approx(212.5)


def test_position_sizing():
    s = _calc()
    # N = (capital × risk_pct) / (entry - SL) = (10000 × 0.01) / 12.5 = 8
    assert s.n_shares == pytest.approx(8.0)
    assert s.risk_amount == pytest.approx(100.0)


def test_rr_ratio_long():
    s = _calc()
    # RR = (TP2 - entry) / (entry - SL) = 12.5 / 12.5 = 1.0... wait
    # Actually ATR=5, so SL dist = 5×2.5 = 12.5, TP2 dist = 5×2.5 = 12.5 → RR = 1.0
    # That means is_recommended = False (< 2.0)
    assert s.rr_ratio == pytest.approx(1.0)
    assert s.is_recommended is False


def test_rr_recommended_when_gte_2():
    # Use ATR=5, sl_mult=1.0 → SL dist=5, TP2 dist=5×2.5=12.5 → RR=2.5
    s = rm.calculate_strategy(
        ticker="AAPL", direction="LONG", capital=10_000, risk_pct=0.01,
        entry_price=200.0, atr_value=5.0, sl_atr_mult=1.0,
    )
    assert s.rr_ratio == pytest.approx(2.5)
    assert s.is_recommended is True


# ── SHORT strategy ────────────────────────────────────────────────────────────

def test_short_stop_loss():
    s = _calc(direction="SHORT")
    # SL = entry + ATR × 2.5 = 200 + 12.5 = 212.5
    assert s.stop_loss == pytest.approx(212.5)


def test_short_tp1():
    s = _calc(direction="SHORT")
    # TP1 = entry - ATR × 1.5 = 200 - 7.5 = 192.5
    assert s.tp1 == pytest.approx(192.5)


# ── Risk cap (RN-1) ───────────────────────────────────────────────────────────

def test_risk_pct_capped_at_3pct():
    s = rm.calculate_strategy(
        ticker="X", direction="LONG", capital=10_000, risk_pct=0.99,
        entry_price=100.0, atr_value=2.0,
    )
    assert s.risk_amount == pytest.approx(10_000 * MAX_RISK_PCT)
    assert s.warning is not None
    assert "capped" in s.warning.lower()


# ── Edge case: ATR = 0 ────────────────────────────────────────────────────────

def test_atr_zero_fallback():
    s = rm.calculate_strategy(
        ticker="X", direction="LONG", capital=10_000, risk_pct=0.01,
        entry_price=100.0, atr_value=0.0,
    )
    # Should fallback to 1% of price = 1.0
    assert s.atr_used == pytest.approx(1.0)
    assert s.warning is not None


# ── TP percentages always sum to 100 ─────────────────────────────────────────

def test_tp_percentages_sum_to_100():
    s = _calc()
    assert s.tp1_pct + s.tp2_pct + s.tp3_pct == pytest.approx(100.0)
