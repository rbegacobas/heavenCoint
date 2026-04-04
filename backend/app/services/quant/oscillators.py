"""Oscillator Engine — NetBrute (CMF-14) and Intenciones (RSI-14 + Momentum).

NetBrute:
    Based on Chaikin Money Flow (CMF) x 100.
    Formula: sum((2C-H-L)/(H-L) x V, N) / sum(V, N)
    Range: -100 to +100
    Zones: <-25 oversold, -25-0 bearish, 0-25 bullish, >25 overbought

Intenciones:
    Based on RSI(14) combined with sign of Momentum(14).
    RSI range: 0-100. Normalized and classified.
    States: BUY (RSI<30), SELL (RSI>70), HOLD (30-70)
    Confidence: distance from center (50) normalized to 0-100
"""

from dataclasses import dataclass


@dataclass
class OscillatorResult:
    value: float           # CMF x 100 for NetBrute; RSI for Intenciones
    cross_type: str        # "BULLISH" | "BEARISH" | "NONE"
    zone: str              # zone label
    observation: str       # deterministic text, no LLM
    confidence_level: float  # 0.0 - 100.0


# ── NetBrute (Chaikin Money Flow x 100) ──────────────────────────────────────


def calculate_netbrute(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float],
    period: int = 14,
) -> OscillatorResult:
    """Calculate NetBrute oscillator using CMF-14.

    Requires at least `period` bars.
    """
    if len(closes) < period:
        return OscillatorResult(
            value=0.0,
            cross_type="NONE",
            zone="BEARISH",
            observation="Datos insuficientes para calcular NetBrute.",
            confidence_level=0.0,
        )

    # Current window CMF
    cmf_current = _cmf(highs, lows, closes, volumes, period)

    # Previous window CMF (shift back 1 bar)
    cmf_prev = None
    if len(closes) >= period + 1:
        cmf_prev = _cmf(highs[:-1], lows[:-1], closes[:-1], volumes[:-1], period)

    value = cmf_current * 100  # scale to -100..+100

    # Detect cross
    cross_type = "NONE"
    if cmf_prev is not None:
        prev_val = cmf_prev * 100
        if prev_val < 0 and value >= 0:
            cross_type = "BULLISH"
        elif prev_val >= 0 and value < 0:
            cross_type = "BEARISH"

    zone = _netbrute_zone(value)
    confidence_level = _netbrute_confidence(value)
    observation = _netbrute_observation(value, zone, cross_type)

    return OscillatorResult(
        value=round(value, 4),
        cross_type=cross_type,
        zone=zone,
        observation=observation,
        confidence_level=round(confidence_level, 2),
    )


def _cmf(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float],
    period: int,
) -> float:
    """Chaikin Money Flow for the last `period` bars."""
    mf_volume_sum = 0.0
    volume_sum = 0.0

    for i in range(-period, 0):
        h, lo, c, v = highs[i], lows[i], closes[i], volumes[i]
        hl_range = h - lo
        if hl_range == 0:
            # No range bar — skip (flat candle)
            continue
        mf_multiplier = (2 * c - h - lo) / hl_range
        mf_volume_sum += mf_multiplier * v
        volume_sum += v

    if volume_sum == 0:
        return 0.0
    return mf_volume_sum / volume_sum


def _netbrute_zone(value: float) -> str:
    if value > 25:
        return "OVERBOUGHT"
    elif value >= 0:
        return "BULLISH"
    elif value >= -25:
        return "BEARISH"
    return "OVERSOLD"


def _netbrute_confidence(value: float) -> float:
    """Confidence = min(100, abs(value) * 2 + 25)."""
    return min(100.0, abs(value) * 2 + 25)


def _netbrute_observation(value: float, zone: str, cross_type: str) -> str:
    base = {
        "OVERBOUGHT": "Flujo institucional muy positivo. Presión compradora intensa.",
        "BULLISH": "Flujo de dinero neto positivo. Compradores dominan el mercado.",
        "BEARISH": "Flujo de dinero neto negativo. Vendedores presentes en el mercado.",
        "OVERSOLD": "Flujo institucional muy negativo. Presión vendedora intensa.",
    }[zone]

    if cross_type == "BULLISH":
        base += " Cruce alcista activo: dinero institucional entrando."
    elif cross_type == "BEARISH":
        base += " Cruce bajista activo: dinero institucional saliendo."

    return base


# ── Intenciones (RSI-14 + Momentum sign) ─────────────────────────────────────


def calculate_intentions(
    closes: list[float],
    rsi_period: int = 14,
    momentum_period: int = 14,
) -> OscillatorResult:
    """Calculate Intenciones oscillator using RSI(14) + sign of Momentum(14).

    Requires at least `rsi_period + 1` closes.
    """
    if len(closes) < rsi_period + 1:
        return OscillatorResult(
            value=50.0,
            cross_type="NONE",
            zone="HOLD",
            observation="Datos insuficientes para calcular Intenciones.",
            confidence_level=0.0,
        )

    rsi = _rsi_wilder(closes, rsi_period)
    momentum_sign = _momentum_sign(closes, momentum_period)

    # RSI-based state
    if rsi < 30:
        state = "BUY"
    elif rsi > 70:
        state = "SELL"
    else:
        state = "HOLD"

    # Cross detection: RSI crossed 30 or 70 boundary
    cross_type = "NONE"
    if len(closes) >= rsi_period + 2:
        prev_rsi = _rsi_wilder(closes[:-1], rsi_period)
        if prev_rsi >= 30 and rsi < 30:
            cross_type = "BULLISH"   # Entering oversold = potential reversal buy
        elif prev_rsi <= 70 and rsi > 70:
            cross_type = "BEARISH"   # Entering overbought = potential reversal sell
        # Exit signals (stronger confirmation)
        elif prev_rsi < 30 and rsi >= 30:
            cross_type = "BULLISH"   # Exiting oversold = confirmed buy
        elif prev_rsi > 70 and rsi <= 70:
            cross_type = "BEARISH"   # Exiting overbought = confirmed sell

    # Adjust state with momentum sign
    if state == "HOLD" and momentum_sign > 0:
        zone = "BULLISH"
    elif state == "HOLD" and momentum_sign < 0:
        zone = "BEARISH"
    else:
        zone = state  # BUY / SELL maps to their own zones

    confidence_level = _intentions_confidence(rsi, state)
    observation = _intentions_observation(rsi, state, momentum_sign, cross_type)

    return OscillatorResult(
        value=round(rsi, 4),
        cross_type=cross_type,
        zone=zone,
        observation=observation,
        confidence_level=round(confidence_level, 2),
    )


def _rsi_wilder(closes: list[float], period: int = 14) -> float:
    """RSI using Wilder's exponential smoothing (industry standard)."""
    if len(closes) < period + 1:
        return 50.0

    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    # Seed with simple average
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # Wilder smoothing for remaining bars
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _momentum_sign(closes: list[float], period: int = 14) -> int:
    """Returns +1, -1, or 0 based on N-period rate of change sign."""
    if len(closes) < period + 1:
        return 0
    delta = closes[-1] - closes[-(period + 1)]
    if delta > 0:
        return 1
    elif delta < 0:
        return -1
    return 0


def _intentions_confidence(rsi: float, state: str) -> float:
    """Confidence = distance from neutral (50), scaled 0-100."""
    distance = abs(rsi - 50)
    return min(100.0, distance * 2)


def _intentions_observation(
    rsi: float, state: str, momentum_sign: int, cross_type: str
) -> str:
    momentum_text = {1: "positivo", -1: "negativo", 0: "neutral"}[momentum_sign]

    if state == "BUY":
        base = f"RSI en zona de pánico extremo ({rsi:.1f}). Alta probabilidad de rebote."
    elif state == "SELL":
        base = f"RSI en zona de sobrecompra ({rsi:.1f}). Presión vendedora psicológica."
    else:
        base = f"RSI en zona neutral ({rsi:.1f}). Momentum {momentum_text}."

    if cross_type == "BULLISH":
        base += " Señal de compra confirmada por cruce de RSI."
    elif cross_type == "BEARISH":
        base += " Señal de venta confirmada por cruce de RSI."

    return base


# ── Divergence detection ──────────────────────────────────────────────────────


def detect_divergence(netbrute: OscillatorResult, intentions: OscillatorResult) -> bool:
    """Returns True when NetBrute and Intenciones signal opposite directions.

    Divergence = opportunity only the 'smart money' spots.
    """
    nb_bullish = netbrute.zone in ("BULLISH", "OVERBOUGHT") or netbrute.cross_type == "BULLISH"
    nb_bearish = netbrute.zone in ("BEARISH", "OVERSOLD") or netbrute.cross_type == "BEARISH"
    it_bullish = intentions.zone in ("BUY", "BULLISH") or intentions.cross_type == "BULLISH"
    it_bearish = intentions.zone in ("SELL", "BEARISH") or intentions.cross_type == "BEARISH"

    return (nb_bullish and it_bearish) or (nb_bearish and it_bullish)
