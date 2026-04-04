---
name: Decisiones de algoritmos para osciladores
description: Qué implementar para NetBrute e Intenciones, y por qué — no cambiar sin consenso
type: project
---

## Decisiones tomadas (2026-04-03)

### NetBrute = Chaikin Money Flow (CMF-14) × 100
- Rango: -100 a +100
- Fórmula: `sum((2C-H-L)/(H-L) × V, 14) / sum(V, 14)` × 100
- Cruce alcista: CMF cruza de negativo a positivo
- Zonas: <-25=sobreventa, -25 a 0=bajista, 0 a 25=alcista, >25=sobrecompra
- Confianza: `min(100, abs(cmf) × 2 + 25)`

**Why:** El video nunca revela el algoritmo real de Orion One. CMF mide flujo real de dinero institucional desde OHLCV+Volume — exactamente lo que Fernando describe como "flujo institucional de órdenes". Open source, verificable, computacionalmente barato.

### Intenciones = RSI(14) + signo Momentum(14)
- RSI Wilder clásico
- Estado: RSI<30=BUY (pánico extremo), RSI>70=SELL, 30-70=HOLD
- Confianza: distancia al centro (50) normalizada × 2

**Why:** Fernando describe Intenciones como "psicología de masa anticipada". RSI es la métrica estándar de sentimiento y sobre-extensión. Momentum confirma dirección del cambio.

## Regla fundamental del LLM
**Python calcula, el LLM narra.** El asistente NUNCA hace matemáticas. El backend calcula SL/TP/position sizing y el LLM solo explica los resultados en lenguaje natural. Esto previene alucinaciones matemáticas.

**How to apply:** En el AI Orchestrator (M6), el system prompt incluye los valores ya calculados por Python. El LLM solo formatea la respuesta.
