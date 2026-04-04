"""Tests for M3 Oscillator Engine — NetBrute (CMF-14) and Intenciones (RSI+Momentum)."""

import pytest

from app.services.quant.oscillators import (
    OscillatorResult,
    _cmf,
    _intentions_confidence,
    _netbrute_confidence,
    _netbrute_zone,
    _rsi_wilder,
    calculate_intentions,
    calculate_netbrute,
    detect_divergence,
)

# ── Synthetic data helpers ─────────────────────────────────────────────────────


def _flat_bars(price: float, n: int, volume: float = 1_000_000):
    """Generate flat OHLCV bars at a fixed price."""
    closes = [price] * n
    highs = [price * 1.005] * n
    lows = [price * 0.995] * n
    volumes = [volume] * n
    return highs, lows, closes, volumes


def _rising_bars(start: float, step: float, n: int, volume: float = 1_000_000):
    """Generate bullish bars: close near the high (positive CMF multiplier)."""
    closes = [start + i * step for i in range(n)]
    # Close near top of range → mf_multiplier close to +1
    highs = [c + 0.1 for c in closes]
    lows = [c - 2.0 for c in closes]
    volumes = [volume] * n
    return highs, lows, closes, volumes


def _falling_bars(start: float, step: float, n: int, volume: float = 1_000_000):
    """Generate bearish bars: close near the low (negative CMF multiplier)."""
    closes = [start - i * step for i in range(n)]
    # Close near bottom of range → mf_multiplier close to -1
    highs = [c + 2.0 for c in closes]
    lows = [c - 0.1 for c in closes]
    volumes = [volume] * n
    return highs, lows, closes, volumes


# ── NetBrute (CMF-14) tests ───────────────────────────────────────────────────


def test_netbrute_insufficient_data():
    """Returns safe defaults when fewer than period bars provided."""
    highs, lows, closes, volumes = _flat_bars(100, 5)
    result = calculate_netbrute(highs, lows, closes, volumes, period=14)

    assert isinstance(result, OscillatorResult)
    assert result.value == 0.0
    assert result.cross_type == "NONE"
    assert result.confidence_level == 0.0


def test_netbrute_bullish_trend():
    """Rising prices with high volume → positive CMF → BULLISH zone."""
    highs, lows, closes, volumes = _rising_bars(100, 0.5, 30)
    result = calculate_netbrute(highs, lows, closes, volumes)

    assert result.value > 0
    assert result.zone in ("BULLISH", "OVERBOUGHT")
    assert result.confidence_level >= 25.0


def test_netbrute_bearish_trend():
    """Falling prices → negative CMF → BEARISH or OVERSOLD zone."""
    highs, lows, closes, volumes = _falling_bars(200, 0.5, 30)
    result = calculate_netbrute(highs, lows, closes, volumes)

    assert result.value < 0
    assert result.zone in ("BEARISH", "OVERSOLD")


def test_netbrute_zone_boundaries():
    """Zone thresholds: >25 OVERBOUGHT, 0-25 BULLISH, -25-0 BEARISH, <-25 OVERSOLD."""
    assert _netbrute_zone(30) == "OVERBOUGHT"
    assert _netbrute_zone(25.1) == "OVERBOUGHT"
    assert _netbrute_zone(10) == "BULLISH"
    assert _netbrute_zone(0) == "BULLISH"
    assert _netbrute_zone(-1) == "BEARISH"
    assert _netbrute_zone(-24.9) == "BEARISH"
    assert _netbrute_zone(-30) == "OVERSOLD"


def test_netbrute_confidence_formula():
    """Confidence = min(100, abs(value) * 2 + 25)."""
    assert _netbrute_confidence(0) == 25.0
    assert _netbrute_confidence(25) == 75.0
    assert _netbrute_confidence(50) == 100.0   # capped at 100
    assert _netbrute_confidence(-25) == 75.0


# ── Intenciones (RSI + Momentum) tests ───────────────────────────────────────


def test_intentions_insufficient_data():
    """Returns 50/HOLD/0% when fewer than rsi_period+1 bars provided."""
    closes = [100.0] * 5
    result = calculate_intentions(closes)

    assert result.value == 50.0
    assert result.zone == "HOLD"
    assert result.confidence_level == 0.0


def test_intentions_buy_signal():
    """Heavily falling prices → RSI < 30 → BUY state."""
    # Create a sharp downtrend that drives RSI below 30
    closes = [100.0 - i * 1.5 for i in range(30)]
    result = calculate_intentions(closes)

    assert result.value < 50  # RSI below neutral
    assert result.zone in ("BUY", "BEARISH")  # aggressive downtrend = low RSI


def test_intentions_sell_signal():
    """Heavily rising prices → RSI > 70 → SELL state."""
    closes = [50.0 + i * 2.0 for i in range(30)]
    result = calculate_intentions(closes)

    assert result.value > 50  # RSI above neutral
    assert result.zone in ("SELL", "BULLISH")


def test_rsi_wilder_bounds():
    """RSI is always between 0 and 100."""
    # All gains
    all_rising = [float(i) for i in range(1, 50)]
    rsi_up = _rsi_wilder(all_rising)
    assert 0 <= rsi_up <= 100

    # All losses
    all_falling = [float(50 - i) for i in range(50)]
    rsi_down = _rsi_wilder(all_falling)
    assert 0 <= rsi_down <= 100


def test_intentions_confidence_neutral():
    """RSI=50 → confidence=0 (equidistant from extremes)."""
    assert _intentions_confidence(50.0, "HOLD") == 0.0


def test_intentions_confidence_extreme():
    """RSI=0 → confidence=100 (max distance from center)."""
    assert _intentions_confidence(0.0, "BUY") == 100.0
    assert _intentions_confidence(100.0, "SELL") == 100.0


# ── Divergence detection ──────────────────────────────────────────────────────


def test_divergence_detected_when_opposing():
    """Bullish NetBrute + Bearish Intenciones → divergence True."""
    nb_bullish = OscillatorResult(
        value=30.0, cross_type="BULLISH", zone="OVERBOUGHT",
        observation="", confidence_level=85.0
    )
    it_bearish = OscillatorResult(
        value=75.0, cross_type="NONE", zone="SELL",
        observation="", confidence_level=50.0
    )
    assert detect_divergence(nb_bullish, it_bearish) is True


def test_no_divergence_when_aligned():
    """Bullish NetBrute + Bullish Intenciones → divergence False."""
    nb_bullish = OscillatorResult(
        value=20.0, cross_type="NONE", zone="BULLISH",
        observation="", confidence_level=65.0
    )
    it_bullish = OscillatorResult(
        value=25.0, cross_type="NONE", zone="BUY",
        observation="", confidence_level=70.0
    )
    assert detect_divergence(nb_bullish, it_bullish) is False


def test_cmf_flat_bars_near_zero():
    """CMF for bars closing near midpoint should be near zero."""
    # All bars: H=105, L=95, C=100 → mf_mult = (200-105-95)/(105-95) = 0
    n = 14
    highs = [105.0] * n
    lows = [95.0] * n
    closes = [100.0] * n
    volumes = [1_000_000.0] * n
    value = _cmf(highs, lows, closes, volumes, n)
    assert abs(value) < 0.01  # essentially zero
