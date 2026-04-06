# HeavenCoint v2.0

**Plataforma cuantitativa de trading profesional** — herramientas de nivel institucional para el trader retail.

Sin improvisar. Con matemática pura.

---

## ¿Qué es HeavenCoint?

HeavenCoint democratiza el acceso a herramientas que normalmente solo usan fondos de inversión y mesas institucionales de Wall Street. El sistema calcula todo por Python — el asistente IA solo narra los resultados, nunca improvisa.

### Características principales

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| **Data Ingestion** | ✅ | Datos de Binance (crypto), yfinance (acciones/forex gratis), FRED (macro) |
| **Quant Engine** | ✅ | ATR-14, SMA 50/134/200, volatilidad anualizada, momentum, rangos de confianza 95% |
| **Oscillator Engine** | ✅ | NetBrute (CMF-14) + Intenciones (RSI-14 + Momentum) |
| **Dashboard** | ✅ | +50 KPIs en tiempo real, 11 cards de análisis |
| **Risk Manager** | ✅ | Position sizing, SL dinámico ATR, TP1/TP2/TP3 escalonados, ratio R:R |
| **Autenticación** | ✅ | JWT, rutas protegidas, registro/login |
| **AI Assistant** | 🔲 | Próximamente — responde solo con datos del activo cargado |
| **Pagos (Stripe)** | 🔲 | Próximamente |

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | Next.js 15 + React 19 + TypeScript strict |
| UI | TailwindCSS + shadcn/ui |
| Estado frontend | Zustand + TanStack Query |
| Backend | Python 3.12 + FastAPI (async) |
| Base de datos | PostgreSQL 16 + TimescaleDB |
| Cache | Redis 7 |
| ORM | SQLAlchemy 2.0 + Alembic |
| Market data (gratis) | yfinance (acciones, forex, ETFs) + Binance API (crypto) |
| Market data (producción) | Polygon.io |
| Datos macro | FRED API (Federal Reserve, gratuito) |

---

## Requisitos previos

- **Docker + Docker Compose** — para PostgreSQL/TimescaleDB y Redis
- **Python 3.12+**
- **Node.js 20+ + pnpm**
- **Git**

---

## Cómo levantar el proyecto (desarrollo)

### 1. Clonar el repositorio

```bash
git clone https://github.com/rbegacobas/heavenCoint.git
cd heavenCoint
```

### 2. Levantar bases de datos

```bash
docker compose up -d
```

Esto levanta:
- PostgreSQL + TimescaleDB en `localhost:5432`
- Redis en `localhost:6379`

Verificar que estén corriendo:

```bash
docker compose ps
# Ambos contenedores deben estar "healthy"
```

### 3. Configurar el backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Crear el archivo de variables de entorno:

```bash
cp .env.example .env
```

Editar `.env` con tus valores (mínimo para desarrollo local ya funciona sin cambios):

```env
DATABASE_URL=postgresql+asyncpg://heavencoint:heavencoint_dev@localhost:5432/heavencoint_db
REDIS_URL=redis://localhost:6379

# Opcional — sin esto usa yfinance gratis para acciones
POLYGON_API_KEY=

# Recomendado — gratis en https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=tu_clave_aqui

SECRET_KEY=cambia_esto_en_produccion
```

Aplicar migraciones de base de datos:

```bash
alembic upgrade head
```

Iniciar el servidor:

```bash
uvicorn app.main:app --reload --port 8000
```

Verificar que funciona:

```bash
curl http://localhost:8000/api/v1/health
# {"status":"healthy","checks":{"database":"ok","redis":"ok"}}
```

### 4. Crear el primer usuario

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@email.com","password":"TuPassword123!","full_name":"Tu Nombre"}'
```

### 5. Configurar el frontend

En otra terminal:

```bash
cd frontend
pnpm install
```

Crear el archivo de variables de entorno:

```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

Iniciar el servidor de desarrollo:

```bash
pnpm dev
```

Abrir en el navegador: **http://localhost:3000**

---

## Puertos en uso

| Servicio | Puerto |
|----------|--------|
| Next.js frontend | 3000 |
| FastAPI backend | 8000 |
| PostgreSQL + TimescaleDB | 5432 |
| Redis | 6379 |

---

## Activos soportados

| Tipo | Ejemplos | Fuente de datos |
|------|----------|-----------------|
| Acciones US | AAPL, MSFT, NVDA, PLTR | yfinance (gratis) / Polygon.io |
| Criptomonedas | BTC-USD, ETH-USD, SOL-USD | Binance API |
| Forex | EURUSD, GBPJPY, USDJPY | yfinance (gratis) |
| ETFs | SPY, QQQ, VTI | yfinance (gratis) |

---

## Comandos útiles

### Backend

```bash
# Tests
pytest                                    # todos los tests
pytest -v                                 # verbose
pytest --cov=app --cov-report=term-missing  # con cobertura

# Linting
ruff check .                              # lint
ruff format .                             # formateo

# Migraciones
alembic revision --autogenerate -m "descripción"   # nueva migración
alembic upgrade head                               # aplicar migraciones
alembic downgrade -1                               # revertir última migración
```

### Frontend

```bash
pnpm type-check    # verificar tipos TypeScript
pnpm lint          # ESLint
pnpm test          # Vitest
pnpm build         # build de producción
```

### Docker

```bash
docker compose up -d        # levantar todo
docker compose down         # apagar todo
docker compose logs -f      # ver logs en tiempo real
docker compose ps           # estado de contenedores
```

---

## Reglas de negocio críticas

El sistema está construido sobre estas reglas matemáticas que **nunca se violan**:

| Regla | Descripción |
|-------|-------------|
| **Riesgo máximo 1%** | Configurable hasta 3%, nunca más. Protege el capital. |
| **Position Sizing** | `N = (Capital × Riesgo%) / (Entrada - StopLoss)` — siempre calculado, nunca manual. |
| **Stop Loss dinámico** | Basado en ATR × 2.5 (no porcentaje fijo). Se adapta a la volatilidad real del activo. |
| **Take-Profits escalonados** | TP1 (33%) en ATR×1.5, TP2 (33%) en ATR×2.5, TP3 (34%) trailing 2×ATR. |
| **R:R mínimo 1:2** | Si el ratio Riesgo:Recompensa es menor a 2, la estrategia se marca "no recomendada". |
| **IA determinista** | El asistente responde solo con datos del activo cargado en Redis. Nunca improvisa. |

---

## Estructura del proyecto

```
heavenCoint/
├── frontend/                  # Next.js 15
│   └── src/
│       ├── app/               # Páginas (login, register, dashboard)
│       ├── components/        # UI components
│       │   └── dashboard/     # TickerBar, TopNav, Sidebars, MainContent
│       ├── hooks/             # useKpiSnapshot, useAssetSearch
│       ├── lib/               # API client (api.ts)
│       ├── stores/            # Zustand (asset-store.ts)
│       └── types/             # TypeScript types (api.ts)
├── backend/                   # FastAPI + Python
│   ├── app/
│   │   ├── api/v1/            # Endpoints REST
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── market_data/   # Binance, yfinance, FRED clients
│   │   │   ├── quant/         # KPI engine + oscillators
│   │   │   └── risk_manager.py  # Position sizing + strategy
│   │   └── tests/             # 46 tests
│   └── alembic/               # 5 migraciones aplicadas
├── infrastructure/
│   └── docker-compose.yml     # PostgreSQL + TimescaleDB + Redis
└── docs/                      # Documentación técnica
```

---

## Tests

```
46 tests pasando (backend) + 1 test frontend
```

```bash
cd backend && pytest -v
```

---

## Variables de entorno — referencia completa

Ver [`.env.example`](backend/.env.example) para la lista completa documentada.

Variables mínimas para desarrollo:

```env
DATABASE_URL=postgresql+asyncpg://heavencoint:heavencoint_dev@localhost:5432/heavencoint_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev-secret-key-change-in-production
FRED_API_KEY=           # opcional pero recomendado (gratis)
POLYGON_API_KEY=        # opcional — sin esto usa yfinance gratis
```

---

## Contribuir

Este proyecto sigue **Conventional Commits**:

```
feat:     nueva funcionalidad
fix:      corrección de bug
docs:     cambios en documentación
test:     añadir o corregir tests
refactor: refactoring sin cambio de funcionalidad
chore:    cambios de build, dependencias, etc.
```

---

## Disclaimer legal

HeavenCoint es una herramienta de análisis cuantitativo. **No constituye asesoramiento financiero.** Toda operación en mercados financieros conlleva riesgo de pérdida de capital. Úsalo bajo tu propio criterio y responsabilidad.

---

*Construido con Python + FastAPI + Next.js. Documentación técnica completa en [`docs/`](docs/).*
