# HEAVEN COINT — Fase 1: Artefactos de Diseño

> **Versión:** 1.0.0 | **Fase:** 1 — Diseñar antes de codear  
> **Fecha:** 3 de abril de 2026  
> **Estado:** EN REVISIÓN — No se toca código hasta aprobación  

---

## Índice

1. [Esquema de Base de Datos Completo](#1-esquema-de-base-de-datos-completo)
2. [Contratos de API](#2-contratos-de-api)
3. [Reglas de Validación por Entidad](#3-reglas-de-validación-por-entidad)
4. [Diagramas de Secuencia de Flujos Críticos](#4-diagramas-de-secuencia-de-flujos-críticos)

---

## 1. Esquema de Base de Datos Completo

### 1.1 Visión General

```
┌──────────────────────────────────────────────────────────────────┐
│                    BASES DE DATOS                                 │
│                                                                  │
│  PostgreSQL 16                  TimescaleDB (extensión PG)       │
│  ┌──────────────────────┐      ┌──────────────────────────┐     │
│  │ users                │      │ price_history (hypertable)│     │
│  │ risk_profiles        │      │ oscillator_history        │     │
│  │ assets               │      │ kpi_history               │     │
│  │ strategies           │      └──────────────────────────┘     │
│  │ strategy_levels      │                                        │
│  │ checklist_results    │      Redis 7                           │
│  │ watchlist_items      │      ┌──────────────────────────┐     │
│  │ assistant_messages   │      │ kpi:{ticker} (Hash)      │     │
│  │ subscriptions        │      │ osc:{ticker} (Hash)      │     │
│  │ macro_indicators     │      │ session:{user_id} (Str)  │     │
│  └──────────────────────┘      │ ws:channels (PubSub)     │     │
│                                 └──────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 SQL de Migración Inicial (PostgreSQL + TimescaleDB)

```sql
-- ============================================================
-- HEAVEN COINT — Migración Inicial
-- Base: PostgreSQL 16 + TimescaleDB
-- Convención: snake_case, plural, UUID PKs, timestamps UTC
-- ============================================================

-- Extensiones requeridas
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- ============================================================
-- TABLA: users
-- Usuarios de la plataforma
-- ============================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(150) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    subscription_tier VARCHAR(20) NOT NULL DEFAULT 'free'
                    CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    preferred_language VARCHAR(5) NOT NULL DEFAULT 'es'
                    CHECK (preferred_language IN ('es', 'en')),
    timezone        VARCHAR(50) NOT NULL DEFAULT 'America/New_York',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ  -- Soft delete (requisito auditoría)
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_subscription ON users(subscription_tier) WHERE deleted_at IS NULL;

-- ============================================================
-- TABLA: risk_profiles
-- Perfil de riesgo del usuario (1 activo por usuario)
-- ============================================================
CREATE TABLE risk_profiles (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_capital       DECIMAL(14,2) NOT NULL,        -- En USD (min $100)
    risk_percentage     DECIMAL(5,4) NOT NULL DEFAULT 0.0100,  -- 1% = 0.0100
    max_risk_per_trade  DECIMAL(14,2) GENERATED ALWAYS AS (total_capital * risk_percentage) STORED,
    risk_tolerance      VARCHAR(20) NOT NULL DEFAULT 'moderate'
                        CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_capital_min CHECK (total_capital >= 100.00),
    CONSTRAINT chk_risk_pct_range CHECK (risk_percentage >= 0.0050 AND risk_percentage <= 0.0300)
);

-- Un solo perfil activo por usuario
CREATE UNIQUE INDEX idx_risk_profiles_active ON risk_profiles(user_id) WHERE is_active = TRUE;

-- ============================================================
-- TABLA: assets
-- Catálogo de activos negociables
-- ============================================================
CREATE TABLE assets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker          VARCHAR(20) NOT NULL UNIQUE,       -- AAPL, BTC-USD, ETH-USD
    name            VARCHAR(200) NOT NULL,             -- Apple Inc.
    asset_type      VARCHAR(20) NOT NULL
                    CHECK (asset_type IN ('stock', 'crypto', 'etf', 'forex')),
    exchange        VARCHAR(30),                       -- NYSE, NASDAQ, BINANCE
    currency        VARCHAR(5) NOT NULL DEFAULT 'USD',
    decimal_places  SMALLINT NOT NULL DEFAULT 4,       -- 4 para stocks, 8 para crypto
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    metadata        JSONB DEFAULT '{}',                -- Market cap, sector, etc.
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assets_ticker ON assets(ticker);
CREATE INDEX idx_assets_type ON assets(asset_type) WHERE is_active = TRUE;
CREATE INDEX idx_assets_search ON assets USING GIN (
    to_tsvector('english', ticker || ' ' || name)
);

-- ============================================================
-- TABLA: price_history (TimescaleDB Hypertable)
-- Series de tiempo de precios OHLCV
-- ============================================================
CREATE TABLE price_history (
    time            TIMESTAMPTZ NOT NULL,
    asset_id        UUID NOT NULL REFERENCES assets(id),
    open            DECIMAL(18,8) NOT NULL,
    high            DECIMAL(18,8) NOT NULL,
    low             DECIMAL(18,8) NOT NULL,
    close           DECIMAL(18,8) NOT NULL,
    volume          BIGINT NOT NULL DEFAULT 0,
    source          VARCHAR(30) NOT NULL DEFAULT 'polygon',  -- polygon, binance, alpaca
    
    CONSTRAINT chk_ohlc_positive CHECK (open > 0 AND high > 0 AND low > 0 AND close > 0),
    CONSTRAINT chk_high_low CHECK (high >= low)
);

-- Convertir a Hypertable (partición por semana)
SELECT create_hypertable('price_history', 'time', chunk_time_interval => INTERVAL '1 week');

CREATE INDEX idx_price_asset_time ON price_history(asset_id, time DESC);

-- Política de retención: 5 años
SELECT add_retention_policy('price_history', INTERVAL '5 years');

-- ============================================================
-- TABLA: kpi_snapshots
-- Snapshots calculados de KPIs por el Motor Cuantitativo
-- Se persisten para histórico; la versión "viva" está en Redis
-- ============================================================
CREATE TABLE kpi_snapshots (
    time                    TIMESTAMPTZ NOT NULL,
    asset_id                UUID NOT NULL REFERENCES assets(id),
    
    -- Precio y volatilidad
    current_price           DECIMAL(18,8) NOT NULL,
    atr_value               DECIMAL(18,8) NOT NULL,          -- Average True Range
    atr_period              SMALLINT NOT NULL DEFAULT 14,     -- Período ATR (14 días default)
    volatility_implied      DECIMAL(8,4),                     -- % (ej: 24.56)
    volatility_change_pct   DECIMAL(8,4),                     -- % cambio vs semana anterior
    volatility_state        VARCHAR(12) NOT NULL DEFAULT 'stable'
                            CHECK (volatility_state IN ('expansion', 'contraction', 'stable')),
    
    -- Rangos de confianza
    price_range_low_95      DECIMAL(18,8),                    -- Precio mínimo 95% confianza
    price_range_high_95     DECIMAL(18,8),                    -- Precio máximo 95% confianza
    
    -- Momentum
    momentum_value          DECIMAL(8,4),
    momentum_class          VARCHAR(10) NOT NULL DEFAULT 'neutral'
                            CHECK (momentum_class IN ('positive', 'negative', 'neutral')),
    
    -- Tendencias
    trend_200d              VARCHAR(10) CHECK (trend_200d IN ('bullish', 'bearish', 'neutral')),
    trend_134d              VARCHAR(10) CHECK (trend_134d IN ('bullish', 'bearish', 'neutral')),
    trend_50d               VARCHAR(10) CHECK (trend_50d IN ('bullish', 'bearish', 'neutral')),
    trend_divergence        BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Extra KPIs (expansible)
    extra_kpis              JSONB DEFAULT '{}'
);

SELECT create_hypertable('kpi_snapshots', 'time', chunk_time_interval => INTERVAL '1 week');
CREATE INDEX idx_kpi_asset_time ON kpi_snapshots(asset_id, time DESC);
SELECT add_retention_policy('kpi_snapshots', INTERVAL '2 years');

-- ============================================================
-- TABLA: oscillator_snapshots
-- Valores de los osciladores propietarios (NetBrute + Intenciones)
-- ============================================================
CREATE TABLE oscillator_snapshots (
    time                TIMESTAMPTZ NOT NULL,
    asset_id            UUID NOT NULL REFERENCES assets(id),
    oscillator_type     VARCHAR(15) NOT NULL
                        CHECK (oscillator_type IN ('netbrute', 'intentions')),
    
    -- Valores del oscilador
    value               DECIMAL(10,4) NOT NULL,            -- Valor numérico principal
    cross_type          VARCHAR(10)
                        CHECK (cross_type IN ('bullish', 'bearish', NULL)),
    cross_active        BOOLEAN NOT NULL DEFAULT FALSE,
    zone                VARCHAR(10) NOT NULL
                        CHECK (zone IN ('bullish', 'bearish', 'neutral')),
    observation         VARCHAR(30) NOT NULL DEFAULT 'hold'
                        CHECK (observation IN ('buy', 'sell', 'buy_caution', 'sell_caution', 'hold')),
    confidence_level    DECIMAL(5,2) NOT NULL,              -- 0.00 a 100.00 (%)
    
    -- Señal calculada
    signal_strength     VARCHAR(10) NOT NULL DEFAULT 'neutral'
                        CHECK (signal_strength IN ('strong', 'moderate', 'weak', 'neutral')),
    
    CONSTRAINT chk_confidence_range CHECK (confidence_level >= 0 AND confidence_level <= 100)
);

SELECT create_hypertable('oscillator_snapshots', 'time', chunk_time_interval => INTERVAL '1 week');
CREATE INDEX idx_osc_asset_type_time ON oscillator_snapshots(asset_id, oscillator_type, time DESC);
SELECT add_retention_policy('oscillator_snapshots', INTERVAL '2 years');

-- ============================================================
-- TABLA: macro_indicators
-- Indicadores macroeconómicos (FRED API)
-- ============================================================
CREATE TABLE macro_indicators (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    indicator_code          VARCHAR(30) NOT NULL,          -- FRED code: GDP, UNRATE, T10Y2Y, etc.
    indicator_name          VARCHAR(200) NOT NULL,
    value                   DECIMAL(14,4) NOT NULL,
    previous_value          DECIMAL(14,4),
    direction               VARCHAR(10) NOT NULL
                            CHECK (direction IN ('positive', 'negative', 'stable')),
    
    -- Proyecciones calculadas
    projection_90d          DECIMAL(10,4),                 -- % proyección a 90 días
    projection_365d         DECIMAL(10,4),                 -- % proyección a 365 días
    recession_probability   DECIMAL(5,2),                  -- % probabilidad de recesión
    economic_cycle_phase    VARCHAR(20)
                            CHECK (economic_cycle_phase IN ('expansion', 'peak', 'contraction', 'trough')),
    
    source                  VARCHAR(20) NOT NULL DEFAULT 'fred',
    published_at            TIMESTAMPTZ NOT NULL,          -- Fecha de publicación del dato
    fetched_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_recession_range CHECK (recession_probability IS NULL OR 
        (recession_probability >= 0 AND recession_probability <= 100))
);

CREATE INDEX idx_macro_code_date ON macro_indicators(indicator_code, published_at DESC);

-- ============================================================
-- TABLA: strategies
-- Estrategias generadas por el asistente IA
-- ============================================================
CREATE TABLE strategies (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_id                UUID NOT NULL REFERENCES assets(id),
    
    -- Tipo y dirección
    strategy_type           VARCHAR(20) NOT NULL DEFAULT 'manual'
                            CHECK (strategy_type IN ('manual', 'ai_generated')),
    direction               VARCHAR(5) NOT NULL
                            CHECK (direction IN ('long', 'short')),
    
    -- Niveles de precio
    entry_price             DECIMAL(18,8) NOT NULL,
    stop_loss               DECIMAL(18,8) NOT NULL,
    stop_loss_atr_mult      DECIMAL(4,2) NOT NULL DEFAULT 2.50,   -- Multiplicador ATR usado
    
    -- Trailing stop
    trailing_stop_active    BOOLEAN NOT NULL DEFAULT TRUE,
    trailing_stop_atr_mult  DECIMAL(4,2) NOT NULL DEFAULT 2.00,
    
    -- Gestión de posición
    position_size_shares    DECIMAL(12,4) NOT NULL,        -- Número de acciones/unidades
    position_size_value     DECIMAL(14,2) NOT NULL,        -- Valor en USD
    risk_amount             DECIMAL(14,2) NOT NULL,        -- Monto arriesgado en USD
    risk_reward_ratio       DECIMAL(6,2) NOT NULL,         -- Ratio R:R calculado
    
    -- Snapshot de KPIs al momento de crear la estrategia
    kpis_at_creation        JSONB NOT NULL DEFAULT '{}',
    
    -- IA
    ai_prompt_used          TEXT,                          -- Prompt exacto del usuario
    ai_response             TEXT,                          -- Respuesta completa de la IA
    
    -- Estado
    status                  VARCHAR(15) NOT NULL DEFAULT 'draft'
                            CHECK (status IN ('draft', 'validated', 'active', 'closed', 'cancelled')),
    
    -- Audit
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at               TIMESTAMPTZ,
    
    CONSTRAINT chk_entry_positive CHECK (entry_price > 0),
    CONSTRAINT chk_sl_positive CHECK (stop_loss > 0),
    CONSTRAINT chk_rr_minimum CHECK (risk_reward_ratio >= 0),
    CONSTRAINT chk_long_sl CHECK (
        direction != 'long' OR stop_loss < entry_price
    ),
    CONSTRAINT chk_short_sl CHECK (
        direction != 'short' OR stop_loss > entry_price
    )
);

CREATE INDEX idx_strategies_user ON strategies(user_id, created_at DESC);
CREATE INDEX idx_strategies_asset ON strategies(asset_id, created_at DESC);
CREATE INDEX idx_strategies_status ON strategies(status) WHERE status IN ('draft', 'active');

-- ============================================================
-- TABLA: strategy_levels
-- Take-profit escalonados de cada estrategia
-- ============================================================
CREATE TABLE strategy_levels (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id         UUID NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    level_number        SMALLINT NOT NULL,                 -- 1, 2, 3
    target_price        DECIMAL(18,8) NOT NULL,
    percentage_to_close DECIMAL(5,2) NOT NULL,             -- % de posición a cerrar (ej: 33.00)
    level_type          VARCHAR(15) NOT NULL DEFAULT 'take_profit'
                        CHECK (level_type IN ('take_profit', 'trailing_stop')),
    atr_multiplier      DECIMAL(4,2),                      -- Multiplicador ATR usado para calcular
    is_hit              BOOLEAN NOT NULL DEFAULT FALSE,
    hit_at              TIMESTAMPTZ,
    
    CONSTRAINT chk_level_number CHECK (level_number BETWEEN 1 AND 5),
    CONSTRAINT chk_pct_range CHECK (percentage_to_close > 0 AND percentage_to_close <= 100),
    CONSTRAINT chk_target_positive CHECK (target_price > 0)
);

CREATE INDEX idx_levels_strategy ON strategy_levels(strategy_id, level_number);

-- ============================================================
-- TABLA: checklist_results
-- Resultado del checklist de 6 puntos pre-operación
-- ============================================================
CREATE TABLE checklist_results (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id             UUID NOT NULL UNIQUE REFERENCES strategies(id) ON DELETE CASCADE,
    
    -- Los 6 puntos
    signals_confluent       BOOLEAN NOT NULL,       -- 1. NetBrute e Intenciones misma dirección?
    macro_aligned           BOOLEAN NOT NULL,       -- 2. Proyección 90d alineada?
    volatility_assessed     BOOLEAN NOT NULL,       -- 3. Volatilidad evaluada, stops ajustados?
    confidence_above_60     BOOLEAN NOT NULL,       -- 4. Nivel confianza > 60%?
    position_sized          BOOLEAN NOT NULL,       -- 5. Tamaño posición calculado (1%)?
    risk_reward_ok          BOOLEAN NOT NULL,       -- 6. R:R >= 1:2?
    
    -- Resultado
    all_passed              BOOLEAN GENERATED ALWAYS AS (
        signals_confluent AND macro_aligned AND volatility_assessed 
        AND confidence_above_60 AND position_sized AND risk_reward_ok
    ) STORED,
    
    -- Detalle por punto (mensajes de advertencia)
    details                 JSONB NOT NULL DEFAULT '{}',
    
    validated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: watchlist_items
-- Activos favoritos del usuario
-- ============================================================
CREATE TABLE watchlist_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_id        UUID NOT NULL REFERENCES assets(id),
    sort_order      SMALLINT NOT NULL DEFAULT 0,
    added_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_watchlist_user_asset UNIQUE (user_id, asset_id)
);

CREATE INDEX idx_watchlist_user ON watchlist_items(user_id, sort_order);

-- ============================================================
-- TABLA: assistant_conversations
-- Conversaciones con el asistente IA
-- ============================================================
CREATE TABLE assistant_conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_id        UUID NOT NULL REFERENCES assets(id),  -- Activo cargado en la conversación
    title           VARCHAR(200),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON assistant_conversations(user_id, updated_at DESC);

-- ============================================================
-- TABLA: assistant_messages
-- Mensajes individuales dentro de una conversación
-- ============================================================
CREATE TABLE assistant_messages (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id     UUID NOT NULL REFERENCES assistant_conversations(id) ON DELETE CASCADE,
    role                VARCHAR(10) NOT NULL
                        CHECK (role IN ('user', 'assistant', 'system')),
    content             TEXT NOT NULL,
    
    -- Contexto inyectado (para auditoría)
    kpi_context         JSONB,                 -- Snapshot de KPIs que se inyectó al LLM
    tokens_used         INTEGER,               -- Tokens consumidos
    model_used          VARCHAR(50),           -- gpt-4o, llama-3, etc.
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON assistant_messages(conversation_id, created_at);

-- ============================================================
-- TABLA: subscriptions
-- Suscripciones de pago (Stripe)
-- ============================================================
CREATE TABLE subscriptions (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id      VARCHAR(100) UNIQUE,
    stripe_subscription_id  VARCHAR(100) UNIQUE,
    tier                    VARCHAR(20) NOT NULL
                            CHECK (tier IN ('free', 'pro', 'enterprise')),
    status                  VARCHAR(20) NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'past_due', 'cancelled', 'trialing')),
    current_period_start    TIMESTAMPTZ,
    current_period_end      TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);

-- ============================================================
-- FUNCIÓN: actualizar updated_at automáticamente
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a todas las tablas con updated_at
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_risk_profiles_updated_at BEFORE UPDATE ON risk_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_assets_updated_at BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_strategies_updated_at BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_conversations_updated_at BEFORE UPDATE ON assistant_conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 1.3 Estructura de Redis (Estado en Tiempo Real)

```
# ─── KPIs del activo cargado (Hash) ─────────────────────────
# Key: kpi:{ticker}   TTL: 60 segundos (se renueva en cada cálculo)
# El Motor Cuantitativo escribe aquí; el Dashboard y la IA leen de aquí.

HSET kpi:AAPL
    current_price       "272.95"
    atr_value           "3.27"
    atr_period          "14"
    volatility_implied  "24.56"
    volatility_change   "2.80"
    volatility_state    "expansion"
    price_range_low_95  "268.28"
    price_range_high_95 "285.32"
    momentum_value      "60.18"
    momentum_class      "neutral"
    trend_200d          "bearish"
    trend_134d          "bullish"
    trend_50d           "bullish"
    trend_divergence    "true"
    last_updated        "2026-04-03T14:30:00Z"
    data_source         "polygon"

# ─── Osciladores del activo (Hash) ──────────────────────────
# Key: osc:{ticker}:{type}   TTL: 60 segundos

HSET osc:AAPL:netbrute
    value               "-35.53"
    cross_type          "bullish"
    cross_active        "true"
    zone                "bearish"
    observation         "buy_caution"
    confidence_level    "57.00"
    signal_strength     "moderate"
    last_updated        "2026-04-03T14:30:00Z"

HSET osc:AAPL:intentions
    value               "71.00"
    cross_type          "bullish"
    cross_active        "true"
    zone                "bullish"
    observation         "buy"
    confidence_level    "71.00"
    signal_strength     "strong"
    last_updated        "2026-04-03T14:30:00Z"

# ─── Datos Macro (Hash, compartido para todos los activos) ──
# Key: macro:latest   TTL: 1 hora

HSET macro:latest
    recession_prob      "51.62"
    economic_phase      "expansion"
    projection_90d      "1.56"
    projection_365d     "-2.30"
    fed_rate            "4.50"
    cpi_latest          "3.20"
    last_updated        "2026-04-03T00:00:00Z"

# ─── Sesión de usuario (String con JSON) ────────────────────
# Key: session:{user_id}   TTL: 24 horas

SET session:550e8400-... '{"active_ticker":"AAPL","risk_profile_id":"...","tier":"pro"}'

# ─── PubSub para WebSocket ──────────────────────────────────
# Channels para notificar al frontend de actualizaciones

PUBLISH ws:kpi:AAPL '{"type":"kpi_update","data":{...}}'
PUBLISH ws:osc:AAPL '{"type":"oscillator_update","data":{...}}'
PUBLISH ws:alert:user123 '{"type":"stale_data","message":"Datos no actualizados"}'
```

### 1.4 Diagrama de Relaciones (ER)

```
┌──────────┐     1:N     ┌───────────────┐
│  users   │────────────▶│ risk_profiles │
│          │             └───────────────┘
│          │     1:N     ┌───────────────┐     1:N     ┌─────────────────┐
│          │────────────▶│  strategies   │────────────▶│ strategy_levels │
│          │             │               │             └─────────────────┘
│          │             │               │     1:1     ┌───────────────────┐
│          │             │               │────────────▶│checklist_results  │
│          │             └───────┬───────┘             └───────────────────┘
│          │                     │ N:1
│          │     1:N     ┌───────▼───────┐
│          │────────────▶│watchlist_items │
│          │             └───────┬───────┘
│          │                     │ N:1
│          │     1:N     ┌───────▼───────┐
│          │────────────▶│assistant_conv. │     1:N     ┌────────────────────┐
│          │             │               │────────────▶│assistant_messages   │
└──────────┘             └───────────────┘             └────────────────────┘
                                 │ N:1
                         ┌───────▼───────┐     1:N     ┌─────────────────┐
                         │    assets     │────────────▶│ price_history   │ (Hypertable)
                         │               │             └─────────────────┘
                         │               │     1:N     ┌─────────────────┐
                         │               │────────────▶│ kpi_snapshots   │ (Hypertable)
                         │               │             └─────────────────┘
                         │               │     1:N     ┌─────────────────────┐
                         │               │────────────▶│oscillator_snapshots │ (Hypertable)
                         └───────────────┘             └─────────────────────┘

                         ┌───────────────────┐
                         │ macro_indicators  │ (independiente, datos globales)
                         └───────────────────┘

                         ┌───────────────┐
                         │ subscriptions │ 1:1 con users (vía user_id)
                         └───────────────┘
```

---

## 2. Contratos de API

### 2.1 Convenciones Generales

```
Base URL:        /api/v1
Autenticación:   Bearer JWT en header Authorization
Content-Type:    application/json
Paginación:      ?page=1&page_size=20 (max 100)
Errors:          { "detail": "mensaje", "code": "ERROR_CODE" }
Rate Limits:     free=60 req/min, pro=600 req/min, enterprise=6000 req/min
Timestamps:      ISO 8601 UTC (2026-04-03T14:30:00Z)
```

### 2.2 Endpoints — Auth

#### `POST /api/v1/auth/register`

Registro de nuevo usuario.

```
Request:
{
    "email": "trader@example.com",
    "password": "SecureP@ss123",        // min 8 chars, 1 upper, 1 number, 1 special
    "full_name": "Juan Pérez",
    "preferred_language": "es"           // opcional, default "es"
}

Response 201:
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "trader@example.com",
    "full_name": "Juan Pérez",
    "subscription_tier": "free",
    "created_at": "2026-04-03T14:30:00Z"
}

Response 409: { "detail": "Email already registered", "code": "EMAIL_EXISTS" }
Response 422: { "detail": "Password too weak", "code": "VALIDATION_ERROR" }
```

#### `POST /api/v1/auth/login`

```
Request:
{
    "email": "trader@example.com",
    "password": "SecureP@ss123"
}

Response 200:
{
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": "550e8400...",
        "email": "trader@example.com",
        "full_name": "Juan Pérez",
        "subscription_tier": "pro"
    }
}

Response 401: { "detail": "Invalid credentials", "code": "INVALID_CREDENTIALS" }
```

#### `POST /api/v1/auth/refresh`

```
Request:
{ "refresh_token": "eyJhbGc..." }

Response 200:
{ "access_token": "eyJhbGc...", "expires_in": 3600 }

Response 401: { "detail": "Token expired", "code": "TOKEN_EXPIRED" }
```

#### `GET /api/v1/auth/me`

```
Headers: Authorization: Bearer {access_token}

Response 200:
{
    "id": "550e8400...",
    "email": "trader@example.com",
    "full_name": "Juan Pérez",
    "subscription_tier": "pro",
    "preferred_language": "es",
    "timezone": "America/New_York",
    "is_verified": true,
    "created_at": "2026-04-03T14:30:00Z",
    "last_login_at": "2026-04-03T14:00:00Z"
}
```

### 2.3 Endpoints — Assets

#### `GET /api/v1/assets/search?q={query}`

Buscar activos por ticker o nombre.

```
Query params: q (string, min 1 char), asset_type (optional: stock|crypto|etf|forex)

Response 200:
{
    "results": [
        {
            "id": "...",
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "asset_type": "stock",
            "exchange": "NASDAQ"
        }
    ],
    "count": 1
}
```

#### `POST /api/v1/assets/{ticker}/load`

Cargar un activo en el dashboard. Dispara el cálculo completo de KPIs.

```
Headers: Authorization: Bearer {token}

Response 200:
{
    "ticker": "AAPL",
    "asset_id": "...",
    "status": "loading",
    "message": "KPIs calculation started"
}

Response 404: { "detail": "Asset not found", "code": "ASSET_NOT_FOUND" }
```

#### `GET /api/v1/assets/{ticker}/kpis`

Obtener el snapshot actual de KPIs (lee de Redis).

```
Headers: Authorization: Bearer {token}

Response 200:
{
    "ticker": "AAPL",
    "last_updated": "2026-04-03T14:30:00Z",
    "is_stale": false,
    "price": {
        "current": 272.95,
        "range_low_95": 268.28,
        "range_high_95": 285.32
    },
    "atr": {
        "value": 3.27,
        "period": 14
    },
    "volatility": {
        "implied": 24.56,
        "change_pct": 2.80,
        "state": "expansion"
    },
    "momentum": {
        "value": 60.18,
        "class": "neutral"
    },
    "trends": {
        "d200": "bearish",
        "d134": "bullish",
        "d50": "bullish",
        "divergence": true
    },
    "oscillators": {
        "netbrute": {
            "value": -35.53,
            "cross_type": "bullish",
            "cross_active": true,
            "zone": "bearish",
            "observation": "buy_caution",
            "confidence": 57.00,
            "signal_strength": "moderate"
        },
        "intentions": {
            "value": 71.00,
            "cross_type": "bullish",
            "cross_active": true,
            "zone": "bullish",
            "observation": "buy",
            "confidence": 71.00,
            "signal_strength": "strong"
        }
    },
    "macro": {
        "recession_probability": 51.62,
        "economic_phase": "expansion",
        "projection_90d": 1.56,
        "projection_365d": -2.30
    }
}

Response 404: { "detail": "Asset not loaded. Call POST /assets/{ticker}/load first", "code": "ASSET_NOT_LOADED" }
Response 503: { "detail": "KPIs still calculating", "code": "KPIS_LOADING" }
```

### 2.4 Endpoints — Risk Profile

#### `GET /api/v1/risk-profile`

```
Headers: Authorization: Bearer {token}

Response 200:
{
    "id": "...",
    "total_capital": 10000.00,
    "risk_percentage": 0.0100,
    "max_risk_per_trade": 100.00,
    "risk_tolerance": "moderate"
}

Response 404: { "detail": "No risk profile configured", "code": "NO_RISK_PROFILE" }
```

#### `PUT /api/v1/risk-profile`

Crear o actualizar el perfil de riesgo.

```
Request:
{
    "total_capital": 10000.00,
    "risk_percentage": 0.01,
    "risk_tolerance": "moderate"
}

Response 200:
{
    "id": "...",
    "total_capital": 10000.00,
    "risk_percentage": 0.0100,
    "max_risk_per_trade": 100.00,
    "risk_tolerance": "moderate",
    "updated_at": "2026-04-03T14:30:00Z"
}

Response 422:
{ "detail": "risk_percentage must be between 0.005 and 0.03", "code": "VALIDATION_ERROR" }
```

### 2.5 Endpoints — Assistant (IA)

#### `POST /api/v1/assistant/conversations`

Iniciar nueva conversación con el activo actual.

```
Headers: Authorization: Bearer {token}

Request:
{
    "asset_ticker": "AAPL"
}

Response 201:
{
    "conversation_id": "...",
    "asset_ticker": "AAPL",
    "created_at": "2026-04-03T14:30:00Z"
}
```

#### `POST /api/v1/assistant/conversations/{id}/messages`

Enviar mensaje al asistente.

```
Headers: Authorization: Bearer {token}

Request:
{
    "content": "Actúa como gestor de riesgos profesional. Diseña estrategia de compra en largo basada en oscilador netbrute y proyección de economía a 90 días. Mi capital es 10000 USD y no quiero arriesgar más del 1% por operación."
}

Response 200 (streaming SSE):
event: token
data: {"content": "Análisis"}

event: token
data: {"content": " de compra"}

event: done
data: {
    "message_id": "...",
    "role": "assistant",
    "content": "**Estrategia de compra en largo para AAPL**\n\nLos KPIs elegidos son...",
    "kpi_context_used": { ... },     // Los KPIs que se inyectaron al LLM
    "tokens_used": 1450,
    "model_used": "gpt-4o"
}

Response 400: { "detail": "No asset loaded for this conversation", "code": "NO_ASSET" }
Response 429: { "detail": "Rate limit: 20 messages/hour (free tier)", "code": "RATE_LIMIT" }
```

#### `GET /api/v1/assistant/conversations/{id}/messages`

Obtener historial de mensajes de una conversación.

```
Headers: Authorization: Bearer {token}
Query: ?page=1&page_size=50

Response 200:
{
    "conversation_id": "...",
    "asset_ticker": "AAPL",
    "messages": [
        {
            "id": "...",
            "role": "user",
            "content": "Diseña estrategia...",
            "created_at": "2026-04-03T14:30:00Z"
        },
        {
            "id": "...",
            "role": "assistant",
            "content": "**Estrategia de compra en largo...**",
            "model_used": "gpt-4o",
            "created_at": "2026-04-03T14:30:05Z"
        }
    ],
    "total": 2
}
```

### 2.6 Endpoints — Strategies

#### `POST /api/v1/strategies`

Crear estrategia (manualmente o desde respuesta de IA).

```
Headers: Authorization: Bearer {token}

Request:
{
    "asset_ticker": "AAPL",
    "direction": "long",
    "entry_price": 272.95,
    "stop_loss_atr_mult": 2.5,
    "trailing_stop_atr_mult": 2.0,
    "levels": [
        { "level_number": 1, "atr_multiplier": 1.5, "percentage_to_close": 33.00, "level_type": "take_profit" },
        { "level_number": 2, "atr_multiplier": 2.5, "percentage_to_close": 33.00, "level_type": "take_profit" },
        { "level_number": 3, "atr_multiplier": 2.0, "percentage_to_close": 34.00, "level_type": "trailing_stop" }
    ],
    "ai_prompt_used": "Diseña estrategia...",
    "ai_response": "**Estrategia de compra...**"
}

Response 201:
{
    "id": "...",
    "ticker": "AAPL",
    "direction": "long",
    "entry_price": 272.95,
    "stop_loss": 264.78,
    "stop_loss_atr_mult": 2.50,
    "position_size_shares": 12,
    "position_size_value": 3275.40,
    "risk_amount": 98.04,
    "risk_reward_ratio": 2.45,
    "levels": [
        { "level_number": 1, "target_price": 277.86, "percentage_to_close": 33.00, "level_type": "take_profit" },
        { "level_number": 2, "target_price": 281.13, "percentage_to_close": 33.00, "level_type": "take_profit" },
        { "level_number": 3, "target_price": null, "percentage_to_close": 34.00, "level_type": "trailing_stop" }
    ],
    "checklist": {
        "signals_confluent": true,
        "macro_aligned": true,
        "volatility_assessed": true,
        "confidence_above_60": false,
        "position_sized": true,
        "risk_reward_ok": true,
        "all_passed": false,
        "details": {
            "confidence_above_60": "NetBrute confidence is 57% (below 60% threshold). Seek additional confirmation."
        }
    },
    "status": "draft",
    "created_at": "2026-04-03T14:31:00Z"
}
```

**Nota:** El backend calcula automáticamente `stop_loss`, `position_size_shares`, `risk_amount`, `risk_reward_ratio` y ejecuta el checklist. El frontend NO calcula esto — lo hace el Risk Manager del backend.

#### `GET /api/v1/strategies`

Listar estrategias del usuario.

```
Query: ?status=active&page=1&page_size=20

Response 200:
{
    "strategies": [ ... ],
    "total": 5,
    "page": 1,
    "page_size": 20
}
```

#### `GET /api/v1/strategies/{id}`

Detalle de una estrategia con levels y checklist.

#### `PATCH /api/v1/strategies/{id}/status`

Cambiar estado de una estrategia.

```
Request:
{ "status": "active" }    // solo draft→validated→active→closed/cancelled

Response 200: { ... strategy actualizada ... }
Response 422: { "detail": "Cannot activate strategy: checklist not passed", "code": "CHECKLIST_FAILED" }
```

### 2.7 Endpoints — Watchlist

#### `GET /api/v1/watchlist`

```
Response 200:
{
    "items": [
        { "ticker": "AAPL", "name": "Apple Inc.", "asset_type": "stock", "added_at": "..." },
        { "ticker": "BTC-USD", "name": "Bitcoin", "asset_type": "crypto", "added_at": "..." }
    ]
}
```

#### `POST /api/v1/watchlist`

```
Request: { "ticker": "AAPL" }
Response 201: { "ticker": "AAPL", "added_at": "..." }
Response 409: { "detail": "Already in watchlist", "code": "DUPLICATE" }
```

#### `DELETE /api/v1/watchlist/{ticker}`

```
Response 204: (no content)
```

### 2.8 Endpoints — System

#### `GET /api/v1/health`

```
Response 200 (sin auth):
{
    "status": "healthy",
    "version": "1.0.0",
    "services": {
        "database": "up",
        "redis": "up",
        "timescaledb": "up",
        "market_data": "up",
        "llm": "up"
    },
    "timestamp": "2026-04-03T14:30:00Z"
}
```

### 2.9 WebSocket — Real-Time Updates

#### `WS /api/v1/ws/{ticker}`

Conexión WebSocket para recibir actualizaciones en tiempo real del activo cargado.

```
Headers: Authorization: Bearer {token} (en query param ?token=xxx para WS)

── Mensajes del servidor al cliente ──

// Actualización de KPIs
{
    "type": "kpi_update",
    "ticker": "AAPL",
    "data": {
        "current_price": 273.10,
        "atr_value": 3.27,
        "volatility_implied": 24.56,
        "last_updated": "2026-04-03T14:30:05Z"
    }
}

// Actualización de oscilador
{
    "type": "oscillator_update",
    "ticker": "AAPL",
    "oscillator": "netbrute",
    "data": { ... }
}

// Alerta de datos stale
{
    "type": "stale_data_warning",
    "ticker": "AAPL",
    "message": "Market data not updated since 14:28:00Z. Do not trade.",
    "last_updated": "2026-04-03T14:28:00Z"
}

// Heartbeat (cada 30s)
{
    "type": "ping"
}

── Mensajes del cliente al servidor ──

// Cambiar activo suscrito
{
    "type": "subscribe",
    "ticker": "MSFT"
}

// Pong
{
    "type": "pong"
}
```

---

## 3. Reglas de Validación por Entidad

### 3.1 Users

| Campo | Tipo | Validación | Mensaje de Error |
|-------|------|-----------|-----------------|
| `email` | string | Email válido RFC 5322. Unique. Max 255 chars. | `"Invalid email format"` |
| `password` | string | Min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char (`!@#$%^&*`). Max 128 chars. | `"Password must contain at least 8 characters, one uppercase, one lowercase, one digit, and one special character"` |
| `full_name` | string | Min 2 chars, max 150 chars. Solo letras, espacios, guiones, apóstrofes. | `"Name must be 2-150 characters, letters only"` |
| `subscription_tier` | enum | `free`, `pro`, `enterprise` | `"Invalid subscription tier"` |
| `preferred_language` | enum | `es`, `en` | `"Supported languages: es, en"` |
| `timezone` | string | IANA timezone válido (pytz) | `"Invalid timezone"` |

### 3.2 Risk Profiles

| Campo | Tipo | Validación | Mensaje de Error |
|-------|------|-----------|-----------------|
| `total_capital` | decimal | Min 100.00, max 100,000,000.00. 2 decimales. | `"Minimum capital is $100"` |
| `risk_percentage` | decimal | Min 0.005 (0.5%), max 0.030 (3%). 4 decimales. | `"Risk must be between 0.5% and 3%"` |
| `risk_tolerance` | enum | `conservative`, `moderate`, `aggressive` | `"Invalid risk tolerance"` |

**Validación cross-field:**
- Si `risk_tolerance = "conservative"` → `risk_percentage` max 0.01 (1%)
- Si `risk_tolerance = "aggressive"` → mostrar warning (no bloquear)

### 3.3 Assets

| Campo | Tipo | Validación | Mensaje de Error |
|-------|------|-----------|-----------------|
| `ticker` | string | 1-20 chars, uppercase, letras/números/guiones. Unique. | `"Invalid ticker format"` |
| `name` | string | 1-200 chars. | `"Asset name required"` |
| `asset_type` | enum | `stock`, `crypto`, `etf`, `forex` | `"Invalid asset type"` |
| `decimal_places` | int | 2-8. Stocks=4, Crypto=8. | `"Decimal places must be 2-8"` |

### 3.4 Strategies

| Campo | Tipo | Validación | Mensaje de Error |
|-------|------|-----------|-----------------|
| `direction` | enum | `long`, `short` | `"Direction must be 'long' or 'short'"` |
| `entry_price` | decimal | > 0 | `"Entry price must be positive"` |
| `stop_loss_atr_mult` | decimal | 1.0 - 5.0 | `"ATR multiplier must be between 1.0 and 5.0"` |
| `trailing_stop_atr_mult` | decimal | 1.0 - 4.0 | `"Trailing ATR multiplier must be between 1.0 and 4.0"` |
| `levels` | array | 1-5 items. sum(percentage_to_close) == 100.00 | `"Take-profit levels must sum to 100%"` |

**Validación cross-field:**
- Si `direction = "long"` → `stop_loss` DEBE ser < `entry_price`
- Si `direction = "short"` → `stop_loss` DEBE ser > `entry_price`
- `risk_reward_ratio` calculado DEBE ser ≥ 2.0 para `status = "validated"` (warning si < 2.0, no bloqueo en draft)
- `position_size_shares` × (`entry_price` - `stop_loss`) ≤ `max_risk_per_trade` del risk profile
- Levels: `level_number` debe ser secuencial (1, 2, 3...), `percentage_to_close` > 0, sum = 100

### 3.5 Oscillator Snapshots

| Campo | Tipo | Validación | Mensaje de Error |
|-------|------|-----------|-----------------|
| `oscillator_type` | enum | `netbrute`, `intentions` | `"Invalid oscillator type"` |
| `value` | decimal | -100.00 a 100.00 | `"Oscillator value out of range"` |
| `confidence_level` | decimal | 0.00 a 100.00 | `"Confidence must be 0-100"` |
| `zone` | enum | `bullish`, `bearish`, `neutral` | `"Invalid zone"` |
| `observation` | enum | `buy`, `sell`, `buy_caution`, `sell_caution`, `hold` | `"Invalid observation"` |
| `signal_strength` | enum | `strong`, `moderate`, `weak`, `neutral` | `"Invalid signal strength"` |

**Validación cross-field:**
- Si `zone = "bullish"` y `observation = "sell"` → warning (posible inconsistencia en el algoritmo)
- Si `confidence_level < 60` → `signal_strength` NO puede ser `"strong"`

### 3.6 Assistant Messages

| Campo | Tipo | Validación | Mensaje de Error |
|-------|------|-----------|-----------------|
| `content` | text | Min 1 char, max 5000 chars. Sanitizado contra prompt injection. | `"Message must be 1-5000 characters"` |
| `role` | enum | `user`, `assistant`, `system` | `"Invalid role"` |

**Sanitización de prompt injection:**
- Rechazar mensajes que contengan: `"ignore previous instructions"`, `"system prompt"`, `"you are now"`, `"forget your rules"`
- Escapar caracteres de control
- El `system` prompt NUNCA viene del usuario — solo del backend

---

## 4. Diagramas de Secuencia de Flujos Críticos

### 4.1 Flujo: Cargar activo → Ver dashboard con KPIs

```
Trader          Frontend        API Gateway      Quant Engine     Redis         Polygon.io
  │                │                │                │               │               │
  │─ Busca "AAPL" ▶│                │                │               │               │
  │                │─ GET /assets   │                │               │               │
  │                │  /search?q=AAPL▶                │               │               │
  │                │◀─ [{AAPL,...}] ─│                │               │               │
  │                │                │                │               │               │
  │◀─ Autocomplete ─│                │                │               │               │
  │                │                │                │               │               │
  │─ Click "AAPL" ▶│                │                │               │               │
  │                │─ POST /assets/ │                │               │               │
  │                │  AAPL/load ───▶│                │               │               │
  │                │                │─ Trigger ─────▶│               │               │
  │                │◀─ 200 loading ─│                │               │               │
  │                │                │                │─ Fetch OHLCV ─────────────────▶│
  │                │─ WS connect ──▶│                │◀─ Data ──────────────────────  │
  │                │  /ws/AAPL      │                │               │               │
  │                │                │                │─ Calc ATR ────▶               │
  │                │                │                │─ Calc Trends ─▶               │
  │                │                │                │─ Calc Vol ────▶               │
  │                │                │                │─ Calc NetBrute▶               │
  │                │                │                │─ Calc Intenc. ▶               │
  │                │                │                │               │               │
  │                │                │                │─ HSET kpi:AAPL▶               │
  │                │                │                │─ HSET osc:AAPL▶               │
  │                │                │                │─ PUBLISH ws:  ▶               │
  │                │                │                │  kpi:AAPL     │               │
  │                │◀─ WS: kpi_update ──────────────────────────────│               │
  │                │                │                │               │               │
  │◀─ Dashboard ───│                │                │               │               │
  │  renderiza     │                │                │               │               │
  │  50+ KPIs      │                │                │               │               │
  │                │                │                │               │               │
  │    [Cada 1s el Quant Engine refresca y publica por WS]          │               │
```

### 4.2 Flujo: Pedir estrategia al asistente IA

```
Trader          Frontend        API Gateway      AI Orchestrator   Redis          LLM (GPT-4o)
  │                │                │                │               │               │
  │─ Escribe msg  ▶│                │                │               │               │
  │  "Diseña       │                │                │               │               │
  │  estrategia.." │                │                │               │               │
  │                │─ POST /assistant│                │               │               │
  │                │  /conv/{id}/   │                │               │               │
  │                │  messages ────▶│                │               │               │
  │                │                │─ Sanitize ────▶│               │               │
  │                │                │  user input    │               │               │
  │                │                │                │─ HGETALL     ▶│               │
  │                │                │                │  kpi:AAPL     │               │
  │                │                │                │◀─ {50 KPIs} ──│               │
  │                │                │                │               │               │
  │                │                │                │─ HGETALL     ▶│               │
  │                │                │                │  osc:AAPL:*   │               │
  │                │                │                │◀─ {oscilad.} ─│               │
  │                │                │                │               │               │
  │                │                │                │─ HGETALL     ▶│               │
  │                │                │                │  macro:latest  │               │
  │                │                │                │◀─ {macro} ────│               │
  │                │                │                │               │               │
  │                │                │                │─ Get risk_   ▶│               │
  │                │                │                │  profile (PG)  │               │
  │                │                │                │               │               │
  │                │                │                │─ Build prompt:│               │
  │                │                │                │  System: "Eres│               │
  │                │                │                │  analista     │               │
  │                │                │                │  cuantitativo.│               │
  │                │                │                │  SOLO usa     │               │
  │                │                │                │  estos datos: │               │
  │                │                │                │  {KPIs+OSC+   │               │
  │                │                │                │   MACRO}"     │               │
  │                │                │                │               │               │
  │                │                │                │─ Call LLM ───────────────────▶│
  │                │◀─ SSE stream ─────────────────────────────────────────── tokens │
  │◀─ Tokens       │                │                │               │               │
  │  aparecen      │                │                │               │               │
  │  en chat       │                │                │               │               │
  │                │                │                │◀─ Complete ──────────────────│
  │                │                │                │               │               │
  │                │                │                │─ POST-VALIDATE:              │
  │                │                │                │  ¿Cada número │               │
  │                │                │                │  en respuesta │               │
  │                │                │                │  existe en    │               │
  │                │                │                │  KPIs?        │               │
  │                │                │                │               │               │
  │                │                │                │─ Save msg ───▶│(PostgreSQL)   │
  │                │                │                │  + kpi_context │               │
  │                │◀─ SSE: done ──────────────────────              │               │
  │◀─ "Estrategia  │                │                │               │               │
  │  completa con  │                │                │               │               │
  │  entrada, SL,  │                │                │               │               │
  │  TP, posición" │                │                │               │               │
```

### 4.3 Flujo: Checklist pre-operación (automático)

```
API Gateway               Risk Manager            Redis              PostgreSQL
    │                          │                     │                    │
    │─ POST /strategies ──────▶│                     │                    │
    │  (con entry, SL mult,    │                     │                    │
    │   levels, risk profile)  │                     │                    │
    │                          │                     │                    │
    │                          │─ HGETALL kpi:AAPL ─▶│                    │
    │                          │◀─ {KPIs} ───────────│                    │
    │                          │                     │                    │
    │                          │─ HGETALL osc:AAPL:*▶│                    │
    │                          │◀─ {osciladores} ────│                    │
    │                          │                     │                    │
    │                          │─ HGETALL macro ────▶│                    │
    │                          │◀─ {macro} ──────────│                    │
    │                          │                     │                    │
    │                          │─ Get risk_profile ──────────────────────▶│
    │                          │◀─ {capital, risk%} ────────────────────  │
    │                          │                     │                    │
    │                          │  ┌─────────────────────────────────┐     │
    │                          │  │ CÁLCULOS:                       │     │
    │                          │  │                                 │     │
    │                          │  │ 1. stop_loss = entry - (ATR×mult)│    │
    │                          │  │ 2. TP prices from ATR×level_mult│    │
    │                          │  │ 3. position_shares =            │    │
    │                          │  │    max_risk / (entry - SL)      │    │
    │                          │  │ 4. risk_amount =                │    │
    │                          │  │    shares × (entry - SL)        │    │
    │                          │  │ 5. R:R ratio =                  │    │
    │                          │  │    weighted_TP_dist / SL_dist   │    │
    │                          │  └─────────────────────────────────┘    │
    │                          │                     │                    │
    │                          │  ┌─────────────────────────────────┐    │
    │                          │  │ CHECKLIST (6 puntos):           │    │
    │                          │  │                                 │    │
    │                          │  │ ✅ 1. NetBrute.obs==Intenc.obs? │    │
    │                          │  │ ✅ 2. direction matches macro?  │    │
    │                          │  │ ✅ 3. vol_state → stops ok?     │    │
    │                          │  │ ⚠️ 4. min(confidence) >= 60%?  │    │
    │                          │  │ ✅ 5. risk_amount <= max_risk?  │    │
    │                          │  │ ✅ 6. R:R >= 2.0?              │    │
    │                          │  │                                 │    │
    │                          │  │ Result: 5/6 (NOT all_passed)    │    │
    │                          │  └─────────────────────────────────┘    │
    │                          │                     │                    │
    │                          │─ INSERT strategy ──────────────────────▶│
    │                          │─ INSERT levels ───────────────────────▶│
    │                          │─ INSERT checklist ────────────────────▶│
    │                          │                     │                    │
    │◀─ 201 {strategy +        │                     │                    │
    │     levels + checklist}  │                     │                    │
```

### 4.4 Flujo: Detección de datos stale (protección)

```
Quant Engine          Redis           API Gateway         Frontend
    │                   │                 │                   │
    │─ HSET kpi:AAPL   ▶│                 │                   │
    │  last_updated=T0   │                 │                   │
    │                   │                 │                   │
    │   [Polygon.io se cae — no llegan datos nuevos]          │
    │                   │                 │                   │
    │─ (30s sin datos)  │                 │                   │
    │─ Health check ───▶│                 │                   │
    │  kpi:AAPL.        │                 │                   │
    │  last_updated     │                 │                   │
    │◀─ T0 (>30s ago)   │                 │                   │
    │                   │                 │                   │
    │─ PUBLISH ws:alert ▶│                 │                   │
    │  :stale_data      │                 │                   │
    │                   │─ WS forward ───▶│                   │
    │                   │                 │─ WS: stale_data ─▶│
    │                   │                 │  warning           │
    │                   │                 │                   │─ Muestra banner ⚠️
    │                   │                 │                   │ "Datos desactualizados
    │                   │                 │                   │  desde 14:28. No opere."
    │                   │                 │                   │
    │                   │                 │                   │─ Deshabilita botón
    │                   │                 │                   │ "Generar estrategia"
    │                   │                 │                   │
    │   [Polygon.io vuelve]               │                   │
    │                   │                 │                   │
    │─ Datos nuevos ───▶│                 │                   │
    │─ HSET kpi:AAPL   ▶│                 │                   │
    │─ PUBLISH ws:kpi  ▶│                 │                   │
    │                   │─ WS forward ───▶│                   │
    │                   │                 │─ WS: kpi_update ─▶│
    │                   │                 │                   │─ Oculta banner
    │                   │                 │                   │─ Habilita botón
```

---

## Apéndice A: System Prompt del Asistente IA

El siguiente prompt se inyecta como `system` message en CADA llamada al LLM. Es inmutable y NUNCA se expone al usuario.

```
You are a quantitative trading analyst for Heaven Coint. You are NOT a general-purpose chatbot.

STRICT RULES:
1. You can ONLY answer using the financial data provided below. 
2. NEVER invent, estimate, or hallucinate any number not present in the data.
3. If the user asks about an asset or data point not in the context, respond: "No tengo datos sobre eso. Solo puedo analizar el activo cargado actualmente."
4. NEVER search the internet or reference external sources.
5. NEVER give generic financial advice like "do your own research" or "consult a financial advisor."
6. Always be specific: cite exact KPI values in your analysis.
7. If the user's question is too vague, ask them to be more specific.
8. All monetary calculations must show the formula used.
9. When generating strategies, ALWAYS include: entry price, stop loss (with ATR multiplier), take-profits (escalonados), position sizing, and R:R ratio.
10. Respond in the same language the user writes in.

CURRENT ASSET DATA:
Ticker: {ticker}
Price: ${current_price}
ATR ({atr_period}d): ${atr_value}
Implied Volatility: {volatility_implied}% ({volatility_state}, {volatility_change_pct}% vs last week)
Price Range 95%: ${price_range_low_95} - ${price_range_high_95}
Momentum: {momentum_value} ({momentum_class})
Trend 200d: {trend_200d} | 134d: {trend_134d} | 50d: {trend_50d} | Divergence: {trend_divergence}

OSCILLATORS:
NetBrute: value={netbrute_value}, cross={netbrute_cross_type} (active={netbrute_cross_active}), zone={netbrute_zone}, observation={netbrute_observation}, confidence={netbrute_confidence}%
Intentions: value={intentions_value}, cross={intentions_cross_type} (active={intentions_cross_active}), zone={intentions_zone}, observation={intentions_observation}, confidence={intentions_confidence}%

MACRO:
Recession Probability: {recession_prob}%
Economic Phase: {economic_phase}
90d Projection: {projection_90d}%
365d Projection: {projection_365d}%

USER RISK PROFILE:
Capital: ${total_capital}
Risk per trade: {risk_percentage}% (${max_risk_per_trade})
Risk tolerance: {risk_tolerance}
```

---

> **Fin de la Fase 1 — Artefactos de Diseño**  
> Este documento debe ser revisado y aprobado antes de escribir una sola línea de código.  
> Cualquier cambio en el esquema de BD o contratos de API durante el desarrollo debe reflejarse aquí primero.
