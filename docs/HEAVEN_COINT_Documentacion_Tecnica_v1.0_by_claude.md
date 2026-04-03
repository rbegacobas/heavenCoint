# ORION ONE — Documentación Técnica Exhaustiva

> **Versión:** 1.0.0 | **Clasificación:** Confidencial | **Fecha:** Abril 2026

---

## Índice

1. [Análisis Profundo del Producto](#1-análisis-profundo-del-producto)
2. [Ciclo de Vida del Diseño del Software (SDLC)](#2-ciclo-de-vida-del-diseño-del-software-sdlc)
3. [Stack Tecnológico Recomendado](#3-stack-tecnológico-recomendado)
4. [Arquitectura de Módulos](#4-arquitectura-de-módulos)
5. [Modelo de Datos](#5-modelo-de-datos)
6. [Flujos de Trabajo Clave](#6-flujos-de-trabajo-clave)
7. [Requisitos No Funcionales](#7-requisitos-no-funcionales)
8. [Recomendaciones Estratégicas](#8-recomendaciones-estratégicas)

---

## 1. Análisis Profundo del Producto

### 1.1 Propósito Central

ORION ONE es un sistema cuantitativo profesional de análisis de mercados financieros diseñado para democratizar el acceso a herramientas de nivel institucional. A diferencia de los modelos de lenguaje generativo (ChatGPT, Gemini, Claude) que generan texto convincente pero carecen de acceso a datos financieros estructurados en tiempo real, ORION ONE procesa exclusivamente datos cuantitativos reales: volatilidad implícita, flujo de órdenes institucionales, indicadores macroeconómicos y osciladores propietarios.

El sistema se fundamenta en **cuatro pilares interconectados** que proporcionan una cadena completa desde el análisis hasta la ejecución de estrategias con esperanza matemática positiva:

- **Pilar 1:** Análisis de datos macroeconómicos actualizados constantemente (probabilidad de recesión, fase del ciclo económico, proyecciones hasta 365 días, volatilidad implícita diaria).
- **Pilar 2:** Osciladores propietarios que miden presión real del mercado (NetBrute para flujo institucional de órdenes, Intenciones para psicología de masa).
- **Pilar 3:** Asistente IA especializado que jamás improvisa (cada respuesta calculada con los KPIs del activo analizado, con miles de datos reales).
- **Pilar 4:** Sistema completo de construcción de estrategias (confluencia de señales, gestión de riesgo cuantitativa, stops dinámicos basados en ATR, take-profits escalonados).

### 1.2 Problema que Resuelve

El ecosistema de trading retail enfrenta una crisis silenciosa: la adopción masiva de IAs generativas como herramientas de análisis financiero. El documento fuente documenta explícitamente este problema:

- **Ausencia de datos reales:** Los LLMs no conocen el precio actual, la volatilidad implícita semanal ni el flujo de órdenes institucionales de ningún activo.
- **Respuestas genéricas:** Ante preguntas como «¿es buen momento para comprar Apple?», los chatbots producen texto que suena profesional pero no contiene análisis cuantitativo alguno. Ejemplo: "Apple es una empresa sólida con buenos fundamentos. El sector tecnológico muestra fortaleza. Podría ser buen momento para considerar una posición."
- **Pérdida de capital verificada:** Experimentos institucionales con capital real demostraron que todas las IAs generativas perdieron dinero operando mercados sin excepción.
- **Brecha institucional-retail:** Los traders profesionales que gestionan millones usan sistemas cuantitativos especializados con una sola función: analizar mercados con datos reales. Estos sistemas eran inaccesibles para el retail hasta ORION ONE.

### 1.3 Usuarios Objetivo

| Segmento | Perfil | Necesidad Principal |
|----------|--------|---------------------|
| **Trader Retail Intermedio** | 1-5 años de experiencia, conoce análisis técnico básico | Acceso a datos institucionales y estrategias con esperanza matemática positiva |
| **Trader Retail Avanzado** | Opera activamente, busca edge cuantitativo | Osciladores propietarios, gestión de riesgo matemática, confluencia de señales |
| **Trader en Formación** | Aprende trading, vulnerable a malas herramientas | Sistema que le enseñe a operar profesionalmente sin improvisar |
| **Inversor Swing/Posición** | Opera en timeframes de días a semanas | Proyecciones macro a 90-365 días, probabilidad de recesión |

### 1.4 Valor Diferencial

La ventaja competitiva de ORION ONE se articula en cuatro dimensiones exclusivas:

1. **Osciladores Propietarios (NetBrute + Intenciones):** Algoritmos no disponibles en ninguna otra plataforma que miden flujo institucional real y psicología de masa. El oscilador NetBrute mide flujo institucional de órdenes (dinero entrando o saliendo), nada de opiniones, solo matemática pura. El oscilador de Intenciones anticipa movimientos antes de que sucedan midiendo psicología de masa.
2. **Asistente IA que jamás improvisa:** Entrenado exclusivamente con los KPIs del activo cargado, no busca en internet ni genera texto genérico. Cada respuesta está calculada con los KPIs del activo que se analiza, con miles de datos reales.
3. **Más de 50 KPIs profesionales por activo:** Desde volatilidad implícita hasta probabilidad de recesión con modelos estadísticos. En 3 segundos el usuario tiene acceso a más de 50 KPIs profesionales.
4. **Sistema de construcción de estrategias completo:** Confluencia de señales para aumentar probabilidad, gestión de riesgo cuantitativa que calcula tamaño exacto de posición, stops dinámicos basados en ATR que se ajustan a volatilidad, take-profits escalonados que maximizan esperanza matemática.

### 1.5 Alcance y Potencial de Crecimiento

| Fase | Alcance | Activos Soportados |
|------|---------|---------------------|
| **MVP (Actual)** | Dashboard + Asistente IA + Estrategias para activos individuales | Acciones US + Criptomonedas principales |
| **Fase 2** | Portfolio multi-activo, backtesting histórico, alertas en tiempo real | + Forex, ETFs, Commodities |
| **Fase 3** | API para brokers, ejecución semi-automática, marketplace de estrategias | + Futuros, Opciones, Mercados emergentes |

---

## 2. Ciclo de Vida del Diseño del Software (SDLC)

### 2.1 Fase de Requerimientos

Del análisis del documento fuente se extraen los siguientes requerimientos:

#### 2.1.1 Requerimientos Funcionales (RF)

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| RF-001 | Dashboard con +50 KPIs profesionales por activo cargado | CRÍTICA |
| RF-002 | Oscilador NetBrute: valor numérico, tipo de cruce (alcista/bajista), zona (alcista/bajista/neutral), nivel de confianza (%) | CRÍTICA |
| RF-003 | Oscilador de Intenciones: estado (BUY/SELL/HOLD), zona, nivel de confianza (%) | CRÍTICA |
| RF-004 | Proyección económica a 90 y 365 días con modelos estadísticos, incluyendo dirección (positiva/negativa) y porcentaje | ALTA |
| RF-005 | Volatilidad implícita actualizada diariamente con variación porcentual respecto a semana anterior y estado (expansión/contracción) | CRÍTICA |
| RF-006 | ATR actual y rango de precios esperado con 95% de confianza (precio mínimo y máximo estimados) | ALTA |
| RF-007 | Asistente IA exclusivo que analiza solo los KPIs del activo cargado en el dashboard. No busca en internet. No improvisa. | CRÍTICA |
| RF-008 | Constructor de estrategias completo: precio de entrada, stop loss dinámico basado en ATR (default 2.5x ATR), take-profits escalonados (50%, 30%, 20%), trailing stop (2x ATR bajo precio máximo) | CRÍTICA |
| RF-009 | Gestión de riesgo cuantitativa: regla del 1% de capital máximo por operación, cálculo exacto de tamaño de posición (capital × riesgo% / stop_distance), ratio riesgo/beneficio mínimo 1:2 | CRÍTICA |
| RF-010 | Checklist pre-operación de 6 puntos de verificación obligatorios: (1) confluencia de señales, (2) proyección economía alineada, (3) volatilidad evaluada, (4) nivel confianza > 60%, (5) tamaño posición calculado, (6) ratio R:R ≥ 1:2 | ALTA |
| RF-011 | Probabilidad de recesión calculada con modelos estadísticos, expresada en porcentaje | ALTA |
| RF-012 | Tendencias múltiples: 200 días, 134 días y 50 días, con detección automática de divergencia entre ellas | ALTA |
| RF-013 | Momentum: valor numérico con clasificación (positivo > 60, negativo < 40, neutral entre ambos) | MEDIA |
| RF-014 | Restricción de activo único: el sistema solo analiza un activo a la vez. No permite comparar dos mercados simultáneamente | CRÍTICA (restricción de diseño) |
| RF-015 | El asistente debe solicitar mayor especificidad cuando las preguntas son ambiguas, en lugar de dar respuestas generalistas | ALTA |
| RF-016 | Explicación de conceptos financieros avanzados bajo demanda: esperanza matemática, riesgo de ruina, drawdown, simulación de escenarios | MEDIA |

#### 2.1.2 Requerimientos No Funcionales (RNF)

| ID | Requerimiento | Fuente |
|----|---------------|--------|
| RNF-001 | Dashboard debe cargar KPIs en menos de 3 segundos | Mencionado explícitamente: "en tres segundos tienes más de 50 KPIs profesionales delante" |
| RNF-002 | Volatilidad implícita actualizada diariamente; osciladores actualizados en tiempo real durante horas de mercado | Inferido del comportamiento descrito |
| RNF-003 | Cálculos financieros con precisión mínima de 2 decimales para precios y porcentajes; dimensionamiento de posición con redondeo a unidades enteras | Extraído de los ejemplos: "12.24 acciones ≈ 12 acciones" |
| RNF-004 | El asistente IA opera en aislamiento total: no accede a internet, solo procesa datos del activo seleccionado en el dashboard | Mencionado explícitamente como advertencia crítica |
| RNF-005 | Revisión trimestral obligatoria de estrategias por cambios en volatilidad y contexto macroeconómico | Advertencia #4 del documento fuente |

### 2.2 Fase de Diseño (Arquitectura Propuesta)

Se recomienda una **arquitectura de microservicios event-driven** con las siguientes capas:

```
Capa de Presentación (Frontend SPA)
        │
        ▼
    API Gateway (autenticación, rate limiting, caché)
        │
        ▼
Microservicios de Dominio
   ├── Asset Service (gestión de activos)
   ├── Data Engine Service (ingesta + cálculos)
   ├── Oscillator Service (NetBrute, Intenciones, Momentum)
   ├── AI Assistant Service (LLM + contexto restringido)
   ├── Strategy Service (construcción + risk management)
   └── User Service (autenticación, suscripciones)
        │
        ▼
    Event Bus (Apache Kafka)
        │
        ▼
    Data Pipeline (ingesta de datos de mercado)
        │
        ▼
    Almacén de Datos (PostgreSQL + TimescaleDB + Redis)
```

**Justificación de la arquitectura event-driven:** Los datos financieros llegan como streams continuos (precios, volúmenes, órdenes) y los osciladores propietarios deben recalcularse en cascada cuando cambian los inputs. La separación en microservicios permite escalar independientemente el servicio de cálculo de osciladores (CPU-intensivo) del servicio de chat IA (GPU-intensivo).

### 2.3 Fase de Desarrollo

**Metodología:** Scrum con sprints de 2 semanas, complementado con Kanban para el pipeline de datos financieros que requiere flujo continuo.

**Equipo mínimo recomendado:**
- 2 Frontend Engineers (React/Next.js + TradingView Charts)
- 2 Backend Engineers (Node.js + Python)
- 1 ML/Data Engineer (pipeline de datos + asistente IA)
- 1 Quant Developer (algoritmos propietarios de osciladores)
- 1 DevOps Engineer (Kubernetes, CI/CD, monitoring)
- 1 QA Engineer especializado en finanzas

**Estrategia de desarrollo:** Feature flags para habilitar progresivamente los cuatro pilares:
1. Sprint 1-4: Dashboard de KPIs (Pilar 1)
2. Sprint 5-8: Osciladores propietarios (Pilar 2)
3. Sprint 9-12: Asistente IA especializado (Pilar 3)
4. Sprint 13-16: Constructor de estrategias + checklist (Pilar 4)

### 2.4 Fase de Pruebas

| Tipo de Test | Alcance | Herramientas |
|-------------|---------|--------------|
| **Unitarios** | Cálculos financieros: ATR, position sizing, esperanza matemática, trailing stops, ratios R:R | Jest, Pytest, verificación con datos históricos reales |
| **Integración** | Pipeline completo: datos de mercado → osciladores → KPIs → dashboard | Testcontainers, datos de mercado sandbox |
| **E2E** | Flujo completo: cargar activo → ver KPIs → pedir estrategia al asistente → verificar checklist | Cypress / Playwright |
| **Precisión Financiera** | Backtesting de estrategias generadas contra datos históricos. Validar que stops ATR-based y TP escalonados producen esperanza matemática positiva | Python + datasets históricos (Yahoo Finance, Polygon) |
| **Carga** | 1,000+ usuarios concurrentes consultando KPIs en horas pico de mercado | k6, Locust |
| **AI Quality (Evals)** | Evaluación sistemática de respuestas del asistente: ¿cita datos reales del activo? ¿rechaza preguntas ambiguas? ¿nunca improvisa? | Framework de evals custom + human review |

### 2.5 Fase de Despliegue

**Estrategia:** Blue-Green Deployment con canary releases para cambios en algoritmos de osciladores.

- **Staging:** Conectado a datos de mercado reales con delay de 15 minutos. Smoke tests automáticos.
- **Producción:** Datos en tiempo real, auto-scaling basado en horas de mercado (NYSE 9:30-16:00 ET, crypto 24/7).
- **DR (Disaster Recovery):** RPO < 1 hora, RTO < 15 minutos. Los datos de mercado son efímeros pero las estrategias del usuario son críticas.
- **Rollback:** Automático si métricas de precisión de osciladores caen por debajo del umbral tras deploy.

### 2.6 Fase de Mantenimiento

- **Recalibración trimestral** de modelos de osciladores (mencionada explícitamente como advertencia crítica #4 en el documento fuente: "Los mercados cambian, la volatilidad cambia, contexto macro cambia, debe revisar estrategias trimestralmente").
- **Actualización de modelos** de probabilidad de recesión según nuevos indicadores macroeconómicos.
- **Monitoreo continuo de drift** en las predicciones del asistente IA (alertas si calidad de respuestas degrada).
- **Auditoría de precisión:** Comparar recomendaciones históricas del sistema vs resultados reales del mercado.
- **Actualización de proveedores de datos:** Mantener contratos vigentes con Polygon.io, CBOE, FRED API.

---

## 3. Stack Tecnológico Recomendado

### 3.1 Frontend

| Componente | Tecnología | Justificación |
|-----------|------------|---------------|
| **Framework** | Next.js 15 (App Router) | SSR para SEO del landing page. React Server Components para dashboard pesado con +50 KPIs. Streaming para carga progresiva. |
| **Estado Global** | Zustand + TanStack Query | Zustand para estado de UI (activo seleccionado, tab activo). TanStack Query para caché de datos financieros con invalidación automática por WebSocket. |
| **Gráficos** | TradingView Lightweight Charts + D3.js | Lightweight Charts es el estándar de la industria para candlesticks profesionales. D3.js para gauges y osciladores custom (NetBrute, Intenciones). |
| **Estilos** | Tailwind CSS + CSS Modules | Dark theme nativo del ecosistema trading. Tailwind para utilidades rápidas, CSS Modules para componentes complejos del dashboard. |
| **Tiempo Real** | WebSocket (socket.io) + SSE | WebSocket para precios y osciladores en tiempo real. Server-Sent Events para streaming de respuestas del asistente IA. |
| **UI Components** | Radix UI + shadcn/ui | Componentes accesibles y personalizables. shadcn para inputs, modales, dropdowns y tooltips del constructor de estrategias. |
| **Tipografía Monoespaciada** | JetBrains Mono | Estándar en dashboards financieros para alineación numérica precisa en KPIs y precios. |

### 3.2 Backend

| Componente | Tecnología | Justificación |
|-----------|------------|---------------|
| **API Principal** | Node.js + Fastify | Alto throughput para WebSocket connections masivas. TypeScript end-to-end con el frontend. JSON Schema validation nativo. |
| **Motor Cuantitativo** | Python 3.12 + FastAPI | Ecosistema científico (NumPy, Pandas, SciPy, statsmodels) para cálculo de osciladores, ATR, volatilidad implícita, modelos estadísticos de probabilidad de recesión. |
| **Asistente IA** | Python + LangChain + Anthropic Claude API | LLM con contexto restringido exclusivamente a KPIs del activo cargado. RAG sobre documentación financiera para conceptos avanzados. Prompt engineering especializado que impide respuestas genéricas. |
| **Data Pipeline** | Apache Kafka + Apache Flink | Kafka para ingesta desacoplada de datos de mercado en streaming. Flink para cálculos en ventana temporal (volatilidad rolling, ATR, medias móviles). |
| **API Gateway** | Kong / AWS API Gateway | Rate limiting por tier de suscripción. Autenticación centralizada. Caché de KPIs frecuentemente consultados. Anti-scraping de datos propietarios. |
| **Scheduler** | Temporal.io | Orquestación de jobs: recalibración de osciladores, actualización de volatilidad diaria, limpieza de caché, generación de alertas. |

### 3.3 Base de Datos

| Tipo | Tecnología | Uso |
|------|------------|-----|
| **Relacional** | PostgreSQL 16 | Usuarios, suscripciones, estrategias guardadas, historial de análisis, configuración de activos. |
| **Time-Series** | TimescaleDB (extensión PostgreSQL) | Precios históricos, valores de osciladores en el tiempo, volatilidad histórica, ATR diario. Compresión nativa y queries temporales optimizados. |
| **Cache** | Redis Cluster | KPIs precalculados por activo, sesión de activo cargado, rate limiting, pub/sub para distribución de WebSocket a múltiples nodos. |
| **Vectorial** | pgvector (extensión PostgreSQL) | Embeddings de documentación financiera para RAG del asistente IA (explicaciones de esperanza matemática, riesgo de ruina, drawdown, etc.). |

### 3.4 Infraestructura

| Componente | Tecnología | Justificación |
|-----------|------------|---------------|
| **Cloud** | AWS (primario) | Multi-region: us-east-1 (proximidad a NYSE para mínima latencia) + eu-west-1 (usuarios europeos). |
| **Contenedores** | Kubernetes (EKS) | Auto-scaling basado en horas de mercado. Pod priority para servicios críticos (Data Engine > AI Assistant > Dashboard). |
| **CI/CD** | GitHub Actions + ArgoCD | GitOps workflow: lint → test → build → security scan → staging → canary → production. Rollback automático por métricas. |
| **Monitoring** | Datadog + PagerDuty | Métricas de infraestructura + custom dashboards para precisión de osciladores. Alertas por degradación de calidad de datos. |
| **CDN** | CloudFront | Assets estáticos del dashboard, librerías de gráficos, fuentes tipográficas. |
| **Secrets** | AWS Secrets Manager | API keys de proveedores de datos financieros, credenciales de base de datos, tokens de autenticación. |

### 3.5 Servicios Externos

| Servicio | Proveedor | Propósito |
|----------|-----------|-----------|
| **Datos de Mercado (Stocks)** | Polygon.io (primario) / Alpha Vantage (failover) | Precios en tiempo real y históricos, datos fundamentales, WebSocket de precios. |
| **Datos de Mercado (Crypto)** | Binance API / CoinGecko | Precios 24/7, volúmenes, order book para cálculo de NetBrute en crypto. |
| **Volatilidad / Opciones** | CBOE / IVolatility | Volatilidad implícita semanal, skew de volatilidad, superficie de volatilidad por activo. |
| **Datos Macroeconómicos** | FRED API (Federal Reserve) | Indicadores macroeconómicos, curva de rendimientos, tasa de desempleo, datos para modelos de probabilidad de recesión y proyecciones económicas a 90-365 días. |
| **Autenticación** | Auth0 / Clerk | OAuth2, MFA, gestión de sesiones, roles por tier de suscripción. |
| **Pagos** | Stripe | Suscripciones recurrentes con múltiples planes (Free, Pro, Institucional). |
| **LLM** | Anthropic Claude API | Motor del asistente IA con contexto restringido a KPIs. Claude seleccionado por capacidad de seguir instrucciones estrictas y no improvisar. |
| **Email transaccional** | Resend / SendGrid | Alertas de osciladores, confirmaciones de suscripción, reportes periódicos. |

---

## 4. Arquitectura de Módulos

### 4.1 Diagrama de Módulos (Jerárquico)

```
ORION ONE
│
├── M1: Asset Manager (Gestión de Activos)
│   ├── Selección y carga de activos desde sidebar
│   ├── Caché de KPIs por activo en Redis
│   ├── Restricción: solo 1 activo activo simultáneamente
│   └── Emisión de evento asset:selected al cambiar activo
│
├── M2: Data Engine (Motor de Datos — Pilar 1)
│   ├── Ingesta de precios en tiempo real vía WebSocket
│   ├── Cálculo de ATR (Average True Range) actual
│   ├── Rango de precios esperado con 95% de confianza
│   ├── Tendencias múltiples (200d, 134d, 50d) con detección de divergencia
│   ├── Volatilidad implícita semanal + variación vs semana anterior
│   ├── Proyecciones macroeconómicas (90 días, 365 días)
│   ├── Probabilidad de recesión con modelos estadísticos
│   └── Fase exacta del ciclo económico
│
├── M3: Oscillator Engine (Motor de Osciladores — Pilar 2)
│   ├── NetBrute: flujo institucional de órdenes
│   │   ├── Valor numérico (-100 a +100)
│   │   ├── Tipo de cruce (alcista/bajista)
│   │   ├── Zona (alcista/bajista/neutral)
│   │   └── Nivel de confianza (0-100%)
│   ├── Intenciones: psicología de masa
│   │   ├── Estado (BUY/SELL/HOLD)
│   │   ├── Zona (alcista/bajista/neutral)
│   │   └── Nivel de confianza (0-100%)
│   └── Momentum: presión compradora/vendedora
│       ├── Valor numérico (0-100)
│       └── Clasificación (Positivo >60, Negativo <40, Neutral)
│
├── M4: AI Assistant (Asistente IA Especializado — Pilar 3)
│   ├── Contexto exclusivo: KPIs del activo cargado (NUNCA internet)
│   ├── Generación de estrategias basadas en datos reales
│   ├── Análisis técnico completo bajo demanda
│   ├── Explicación de conceptos financieros avanzados
│   │   ├── Esperanza matemática
│   │   ├── Riesgo de ruina
│   │   ├── Drawdown
│   │   └── Simulación de escenarios
│   └── Solicitud de mayor especificidad ante preguntas ambiguas
│
├── M5: Strategy Builder (Constructor de Estrategias — Pilar 4)
│   ├── Confluencia de señales (NetBrute + Intenciones + Macro = 0-3)
│   ├── Precio de entrada (precio actual al momento de generación)
│   ├── Stop Loss dinámico basado en ATR
│   │   ├── Default: 2.5x ATR por debajo de entrada (long)
│   │   ├── Se ajusta automáticamente a volatilidad del mercado
│   │   └── Trailing stop: 2x ATR bajo precio máximo alcanzado
│   ├── Take Profits escalonados
│   │   ├── TP1: 50% de la posición a 2x distancia del stop
│   │   ├── TP2: 30% de la posición a 3x distancia del stop
│   │   └── TP3: 20% de la posición a 4x distancia del stop
│   └── Cálculo de esperanza matemática y ratio R:R
│
├── M6: Risk Manager (Gestión de Riesgo)
│   ├── Regla del 1%: riesgo máximo = capital × 1%
│   ├── Tamaño de posición = riesgo_por_operación / stop_distance
│   ├── Ratio riesgo/beneficio (mínimo aceptable: 1:2)
│   ├── Esperanza matemática: (Win% × Ganancia_Media) - (Loss% × Pérdida_Media)
│   └── Validación: si salta el stop, la pérdida = exactamente 1% del capital
│
├── M7: Pre-Trade Checklist (Checklist Pre-Operación)
│   ├── ✓ Verificación 1: Confluencia de señales (NetBrute + Intenciones misma dirección)
│   ├── ✓ Verificación 2: Proyección economía 90d alineada con dirección
│   ├── ✓ Verificación 3: Volatilidad evaluada (expansión → ampliar stops; contracción → ajustar)
│   ├── ✓ Verificación 4: Nivel de confianza > 60% (si <60%, buscar confirmación adicional)
│   ├── ✓ Verificación 5: Tamaño de posición calculado correctamente (regla del 1%)
│   └── ✓ Verificación 6: Ratio riesgo/beneficio ≥ 1:2
│
└── M8: Dashboard UI (Interfaz de Usuario)
    ├── Sidebar: lista de activos con sparklines y precios
    ├── Panel principal: +50 KPIs organizados en cards
    ├── Panel de osciladores: gauges visuales con estados
    ├── Panel de tendencias: 200d, 134d, 50d con divergencia
    ├── Gráfico de precio (90 días)
    ├── Chat del asistente IA
    ├── Panel de estrategia con inputs y resultados
    └── Panel de checklist con semáforo visual
```

### 4.2 Dependencias entre Módulos

```
M1 (Asset Manager) ──▶ M2 (Data Engine) ──▶ M3 (Oscillator Engine)
       │                         │                        │
       └─────────────────────────▼────────────────────────┘
                              M4 (AI Assistant)
                              M5 (Strategy Builder) ─▶ M6 (Risk Manager)
                                     │
                              M7 (Checklist) ──▶ M8 (Dashboard UI)
```

**Flujo de datos:**
1. M1 emite `asset:selected` → M2 carga datos del activo
2. M2 emite `data:updated` → M3 recalcula osciladores
3. M2 + M3 proveen contexto → M4 (AI Assistant) responde preguntas
4. M2 + M3 proveen datos → M5 genera estrategia → M6 valida riesgo
5. M5 + M6 → M7 evalúa checklist → M8 renderiza todo

**Patrón clave:** M4 (AI Assistant) depende de M2 y M3 pero NUNCA accede directamente a fuentes externas. Su contexto está completamente contenido por los KPIs calculados.

### 4.3 Patrones de Diseño Aplicables

| Patrón | Aplicación en ORION ONE |
|--------|------------------------|
| **Observer** | Osciladores (M3) se recalculan automáticamente cuando cambian datos del Data Engine (M2). Dashboard (M8) se actualiza al cambiar cualquier KPI. |
| **Strategy Pattern** | Diferentes algoritmos de cálculo de stop loss intercambiables: ATR-based (default 2.5x), porcentaje fijo, trailing (2x ATR). |
| **Chain of Responsibility** | Checklist pre-operación (M7) como cadena de 6 validadores independientes que se ejecutan en secuencia. |
| **Mediator** | Asset Manager (M1) como mediador que coordina qué datos fluyen al AI Assistant (M4). Evita acoplamiento directo entre fuentes de datos y el LLM. |
| **CQRS** | Separar lectura de KPIs (alta frecuencia, miles de lecturas/segundo) de escritura de estrategias (baja frecuencia, acciones explícitas del usuario). |
| **Event Sourcing** | Pipeline de datos financieros: cada tick de precio es un evento inmutable que alimenta los cálculos downstream. |

---

## 5. Modelo de Datos

### 5.1 Entidades Principales

#### Entity: Asset (Activo Financiero)

| Atributo | Tipo | Ejemplo | Regla de Negocio |
|----------|------|---------|------------------|
| `symbol` | VARCHAR(10) PK | AAPL | Único, inmutable |
| `name` | VARCHAR(100) | Apple Inc. | NOT NULL |
| `type` | ENUM('Stock','Crypto') | Stock | Determina proveedores de datos y horarios de mercado |
| `exchange` | VARCHAR(50) | NASDAQ | Exchange principal del activo |
| `sector` | VARCHAR(100) | Technology | Sector para futuro análisis sectorial |
| `current_price` | DECIMAL(18,8) | 272.95000000 | Precisión de 8 decimales para crypto |
| `atr` | DECIMAL(12,4) | 3.2700 | Recalculado cada cierre de mercado |
| `implied_volatility` | DECIMAL(8,4) | 24.5600 | Actualizado diariamente |
| `vol_weekly_change` | DECIMAL(8,4) | 2.8000 | Variación porcentual vs semana anterior |
| `vol_status` | ENUM('expansion','contraction') | expansion | Derivado de vol_weekly_change |
| `momentum` | DECIMAL(8,4) | 64.2000 | 0-100, recalculado con cada tick |
| `recession_probability` | DECIMAL(5,2) | 28.40 | 0-100%, modelo estadístico macro |
| `economy_projection_90d` | DECIMAL(8,4) | 1.5600 | Proyección a 90 días, positiva o negativa |
| `economy_projection_365d` | DECIMAL(8,4) | 3.2100 | Proyección a 365 días |
| `range_high_95` | DECIMAL(18,8) | 285.32 | Precio máximo esperado (95% confianza) |
| `range_low_95` | DECIMAL(18,8) | 268.28 | Precio mínimo esperado (95% confianza) |
| `trend_200d` | ENUM('bullish','bearish','neutral') | bullish | Tendencia a 200 días |
| `trend_134d` | ENUM('bullish','bearish','neutral') | bullish | Tendencia a 134 días |
| `trend_50d` | ENUM('bullish','bearish','neutral') | bullish | Tendencia a 50 días |
| `trend_divergence` | BOOLEAN | false | true si trend_200d ≠ trend_50d |
| `updated_at` | TIMESTAMPTZ | 2026-04-01T14:30:00Z | Timestamp de última actualización |

#### Entity: OscillatorReading (Lectura de Oscilador)

| Atributo | Tipo | Ejemplo | Regla de Negocio |
|----------|------|---------|------------------|
| `id` | UUID PK | uuid-v4 | Autogenerado |
| `asset_symbol` | VARCHAR(10) FK | AAPL | Referencia a Asset |
| `oscillator_type` | ENUM('NETBRUTE','INTENTIONS','MOMENTUM') | NETBRUTE | Tipo de oscilador propietario |
| `value` | DECIMAL(10,4) | -35.5300 | Rango [-100, 100] para NetBrute; [0, 100] para Momentum |
| `cross_type` | ENUM('bullish','bearish','none') | bullish | Cruce detectado por algoritmo propietario |
| `zone` | ENUM('bullish','bearish','neutral') | bearish | Zona calculada del oscilador |
| `state` | ENUM('BUY','SELL','HOLD') | BUY | Solo para Intenciones; NULL para otros |
| `confidence_level` | DECIMAL(5,2) | 57.00 | 0-100%. Umbral crítico: 60% (checklist punto 4) |
| `timestamp` | TIMESTAMPTZ | 2026-04-01T14:30:00Z | Momento exacto del cálculo |

#### Entity: Strategy (Estrategia Generada)

| Atributo | Tipo | Ejemplo | Regla de Negocio |
|----------|------|---------|------------------|
| `id` | UUID PK | uuid-v4 | Autogenerado |
| `user_id` | UUID FK | uuid-v4 | Referencia a User |
| `asset_symbol` | VARCHAR(10) FK | AAPL | Activo sobre el que se genera la estrategia |
| `direction` | ENUM('LONG','SHORT') | LONG | Debe alinearse con confluencia de señales |
| `entry_price` | DECIMAL(18,8) | 272.95 | Precio del activo al momento de generación |
| `stop_loss` | DECIMAL(18,8) | 264.78 | Calculado: entry ± (ATR × atr_multiplier) |
| `stop_distance` | DECIMAL(18,8) | 8.17 | ATR × atr_multiplier en unidades monetarias |
| `atr_multiplier` | DECIMAL(4,2) | 2.50 | Default 2.5, ajustable por volatilidad |
| `trailing_stop_atr` | DECIMAL(4,2) | 2.00 | Multiplicador ATR para trailing stop (default 2x) |
| `tp_levels` | JSONB | [{"pct":50,"price":289.29},{"pct":30,"price":297.46},{"pct":20,"price":305.63}] | Take profits escalonados |
| `position_size` | INTEGER | 12 | Unidades/acciones según regla del 1% |
| `capital` | DECIMAL(12,2) | 10000.00 | Capital total del trader |
| `risk_pct` | DECIMAL(4,2) | 1.00 | Porcentaje de riesgo por operación |
| `risk_amount` | DECIMAL(12,2) | 100.00 | capital × risk_pct |
| `total_investment` | DECIMAL(12,2) | 3275.40 | position_size × entry_price |
| `confluence_score` | INTEGER | 3 | 0-3 señales alineadas |
| `signal_netbrute` | BOOLEAN | true | NetBrute alineado con dirección |
| `signal_intentions` | BOOLEAN | true | Intenciones alineadas con dirección |
| `signal_macro` | BOOLEAN | true | Proyección macro alineada con dirección |
| `win_rate_est` | DECIMAL(5,4) | 0.6200 | Win rate estimado según confluencia |
| `expectancy` | DECIMAL(10,4) | 1.8700 | (WinRate × AvgWin) - (LossRate × AvgLoss) |
| `risk_reward_ratio` | DECIMAL(4,2) | 2.50 | Ratio R:R. Mínimo aceptable: 2.0 |
| `checklist_passed` | INTEGER | 6 | Puntos del checklist superados (0-6) |
| `created_at` | TIMESTAMPTZ | 2026-04-01T14:35:00Z | Momento de generación |

#### Entity: User (Usuario)

| Atributo | Tipo | Ejemplo | Regla de Negocio |
|----------|------|---------|------------------|
| `id` | UUID PK | uuid-v4 | Autogenerado |
| `email` | VARCHAR(255) UNIQUE | trader@email.com | Único, validado |
| `subscription_tier` | ENUM('free','pro','institutional') | pro | Determina rate limits y features |
| `default_capital` | DECIMAL(12,2) | 10000.00 | Capital default para cálculos |
| `default_risk_pct` | DECIMAL(4,2) | 1.00 | Riesgo default por operación |
| `created_at` | TIMESTAMPTZ | 2026-01-15T10:00:00Z | Registro |

#### Entity: ChatMessage (Mensajes del Asistente)

| Atributo | Tipo | Ejemplo | Regla de Negocio |
|----------|------|---------|------------------|
| `id` | UUID PK | uuid-v4 | Autogenerado |
| `user_id` | UUID FK | uuid-v4 | Referencia a User |
| `asset_symbol` | VARCHAR(10) | AAPL | Activo cargado al momento del mensaje |
| `role` | ENUM('user','assistant') | user | Quién envía el mensaje |
| `content` | TEXT | "Diseña estrategia..." | Texto del mensaje |
| `kpi_context_snapshot` | JSONB | {...todos los KPIs...} | Snapshot de KPIs al momento (auditoría) |
| `created_at` | TIMESTAMPTZ | 2026-04-01T14:32:00Z | Timestamp |

#### Entity: PriceHistory (Serie Temporal — TimescaleDB Hypertable)

| Atributo | Tipo | Ejemplo | Regla de Negocio |
|----------|------|---------|------------------|
| `time` | TIMESTAMPTZ PK | 2026-04-01T14:30:00Z | Partition key de TimescaleDB |
| `asset_symbol` | VARCHAR(10) FK | AAPL | Referencia a Asset |
| `price` | DECIMAL(18,8) | 272.95 | Precio en ese instante |
| `volume` | BIGINT | 1523400 | Volumen acumulado |
| `atr_snapshot` | DECIMAL(12,4) | 3.27 | ATR al momento |

### 5.2 Relaciones Clave

```
User 1──N Strategy          (un usuario genera múltiples estrategias)
User 1──N ChatMessage       (un usuario tiene múltiples conversaciones)
Asset 1──N OscillatorReading (un activo tiene lecturas históricas de osciladores)
Asset 1──N PriceHistory      (un activo tiene serie temporal de precios — hypertable)
Asset 1──N Strategy          (múltiples estrategias por activo)
Asset 1──N ChatMessage       (mensajes vinculados al activo cargado)
Strategy 1──1 ChecklistResult (cada estrategia tiene resultado de checklist embebido)
User 1──1 Subscription       (un usuario tiene una suscripción activa)
```

### 5.3 Consideraciones de Validación

- **Precio:** DECIMAL(18,8) para soportar criptomonedas con hasta 8 decimales (BTC satoshis).
- **ATR Multiplier:** Validar rango [1.0, 5.0]. Default 2.5 según documento fuente.
- **Risk Percentage:** Validar rango [0.5, 5.0]. Default 1.0 (regla del 1% del documento).
- **Confluence Score:** Calculado automáticamente, no editable por usuario.
- **Position Size:** Siempre redondeado hacia abajo (12.24 → 12 acciones, mencionado explícitamente).
- **Stop Loss:** Debe ser siempre menor que entry_price en LONG, mayor en SHORT.
- **Take Profits:** TP1 > TP2 > TP3 en LONG; invertido en SHORT. Mínimo TP1 a 2x stop distance.
- **Confidence Level:** Si < 60%, checklist marca fallo en punto 4.

---

## 6. Flujos de Trabajo Clave

### 6.1 Flujo Principal: Cargar Activo y Ver Dashboard

```
1. Usuario selecciona activo en el sidebar (ej: AAPL)
2. Asset Manager (M1) emite evento asset:selected con el símbolo
3. Data Engine (M2) carga +50 KPIs del activo:
   ├── Precio actual: $272.95
   ├── ATR: $3.27
   ├── Volatilidad implícita: 24.56% (expansión +2.8%)
   ├── Rango 95% confianza: $268.28 — $285.32
   ├── Proyección economía 90d: +1.56% (positiva)
   ├── Probabilidad recesión: 28.4%
   ├── Tendencias: 200d bullish, 134d bullish, 50d bullish
   └── Momentum: 64.2 (Positivo)
4. Oscillator Engine (M3) calcula osciladores:
   ├── NetBrute: -35.53, cruce alcista, zona bajista, confianza 57%
   └── Intenciones: BUY, zona alcista, confianza 71%
5. Dashboard (M8) renderiza todo en < 3 segundos
6. AI Assistant (M4) recibe contexto restringido al activo cargado
7. WebSocket mantiene actualización continua de precio y osciladores
```

### 6.2 Flujo: Generar Estrategia Profesional

```
1. Usuario navega al Constructor de Estrategias con activo cargado (AAPL)
2. Introduce parámetros:
   ├── Capital total: €10,000
   ├── Porcentaje de riesgo: 1% (default, regla de oro)
   └── Dirección: LONG (compra en largo)
3. Strategy Builder (M5) calcula:
   ├── Entrada: $272.95 (precio actual)
   ├── Riesgo por operación: €100 (10,000 × 1%)
   ├── Stop distance: $8.17 (ATR $3.27 × 2.5)
   ├── Stop Loss: $264.78 (272.95 - 8.17)
   ├── Trailing Stop: 2x ATR bajo precio máximo alcanzado
   ├── TP1 (50%): $289.29 (entrada + 2×stop_distance)
   ├── TP2 (30%): $297.46 (entrada + 3×stop_distance)
   └── TP3 (20%): $305.63 (entrada + 4×stop_distance)
4. Risk Manager (M6) computa:
   ├── Tamaño posición: 100/8.17 = 12.24 → 12 acciones
   ├── Inversión total: 12 × $272.95 = $3,275.40
   └── Ratio R:R: 1:2.5
5. Se evalúa confluencia (3 señales):
   ├── ✅ NetBrute: cruce alcista → alineado con LONG
   ├── ✅ Intenciones: BUY → alineado con LONG
   └── ✅ Macro: proyección 90d positiva → alineado con LONG
6. Esperanza matemática calculada: positiva
7. Checklist automático: 6/6 verificaciones superadas
8. Resultado completo mostrado en dashboard con todos los detalles
```

### 6.3 Flujo: Consulta al Asistente IA

```
1. Usuario escribe en el chat:
   "Actúa como gestor de riesgos profesional, diseña estrategia robusta
    de compra en largo basado en oscilador NetBrute y proyección de
    economía a 90 días. Quiero esperanza matemática positiva."

2. Sistema inyecta como contexto EXCLUSIVAMENTE los KPIs del activo cargado:
   {
     symbol: "AAPL", price: 272.95, atr: 3.27,
     netbrute: {value: -35.53, cross: "bullish", confidence: 57},
     intentions: {state: "BUY", zone: "bullish", confidence: 71},
     economy90: {projection: 1.56, direction: "positive"},
     volatility: {implied: 24.56, change: 2.8, status: "expansion"},
     momentum: 64.2, recession_prob: 28.4,
     trends: {d200: "bullish", d134: "bullish", d50: "bullish"}
   }

3. LLM procesa con prompt especializado:
   - REGLA: Solo usar datos del contexto proporcionado
   - REGLA: Nunca improvisar ni buscar en internet
   - REGLA: Si datos insuficientes, solicitar más especificidad
   - REGLA: Citar valores exactos de KPIs en la respuesta

4. Respuesta incluye datos específicos:
   - "NetBrute en -35.53 con cruce alcista activo, confianza 57%"
   - "Proyección economía 90d positiva (+1.56%)"
   - "ATR actual: $3.27, stop recomendado: 2.5×ATR = $8.17"
   - Estrategia completa con entrada, stops, TPs, position sizing

5. Si la pregunta es ambigua ("¿Es buen momento para comprar?"):
   - El asistente responde con sugerencias de prompts más específicos
   - Según advertencia explícita del documento fuente
```

### 6.4 Flujo: Ejemplo Ethereum (Señales Contradictorias)

```
1. Usuario carga ETH en el dashboard
2. KPIs muestran situación compleja:
   ├── Precio: $2,660.88
   ├── Tendencia 200d: BAJISTA
   ├── Tendencia 134d: ALCISTA
   ├── Tendencia 50d: ALCISTA
   ├── ⚠️ DIVERGENCIA DETECTADA entre tendencias
   ├── NetBrute: cruce BAJISTA, vender con precaución
   ├── Momentum: 60.18 (neutral)
   ├── Volatilidad: 48.69% (alta, pero disminuyendo)
   ├── Probabilidad recesión: 51.62% (riesgo significativo)
   └── Proyección 90d: -19.17% (NEGATIVA)

3. Asistente IA genera análisis:
   - "Existe divergencia en tendencias: largo plazo bajista, corto/medio alcista"
   - "NetBrute muestra cruce bajista: presión vendedora a corto plazo"
   - "RECOMENDACIÓN: PRECAUCIÓN. Esperar confirmación."
   - "Escenario alcista: si supera resistencia en $2,814 con volumen"
   - "Escenario bajista: si no supera resistencia y NetBrute continúa bajista"

4. Checklist falla en múltiples puntos:
   ├── ❌ Confluencia: señales divergentes
   ├── ❌ Proyección negativa para compras
   ├── ⚠️ Volatilidad alta (requiere stops amplios)
   └── ❌ Confianza NetBrute < 60%

5. Sistema protege al trader: NO recomienda entrar
```

### 6.5 Casos de Borde Identificados

| Caso de Borde | Comportamiento del Sistema |
|---------------|---------------------------|
| **Divergencia de tendencias** | El sistema detecta cuando tendencia 200d ≠ 50d (caso ETH) y recomienda esperar confirmación con ruptura clara de soporte/resistencia |
| **Confianza < 60%** | Checklist marca fallo en punto 4. El sistema recomienda buscar confirmación adicional en otros KPIs antes de operar |
| **Volatilidad extrema (expansión)** | ATR se dispara → stops se amplían automáticamente → position size se reduce → el sistema alerta sobre mercado volátil |
| **Solicitud de comparar activos** | El sistema rechaza explícitamente: "Solo puedo analizar el activo cargado actualmente ({symbol}). Seleccione otro activo para analizarlo." |
| **Pregunta ambigua al asistente** | Respuesta genérica con sugerencias de cómo formular mejores preguntas (según advertencia #2 del documento) |
| **Capital insuficiente** | Si cálculo de posición resulta en 0 unidades (capital × risk% / stop_distance < 1), el sistema alerta: "Capital insuficiente para este nivel de riesgo y activo." |
| **Todas las señales en contra** | Confluencia 0/3: el sistema desaconseja explícitamente la operación y sugiere esperar |
| **Mercado cerrado (stocks)** | KPIs muestran último cierre con timestamp. Osciladores congelados hasta próxima apertura. Crypto opera 24/7. |

---

## 7. Requisitos No Funcionales

### 7.1 Escalabilidad

- **Horizontal scaling** del Data Engine durante horas pico de mercado (apertura NYSE 9:30 ET, cierre europeo 17:30 CET, crypto 24/7).
- **Auto-scaling de pods** del AI Assistant basado en cola de mensajes (GPU-bound, escala independiente).
- **Cache distribuido de KPIs:** La misma consulta de AAPL por 10,000 usuarios sirve datos del mismo cache Redis. Invalidación por WebSocket cuando cambian los datos.
- **Objetivo:** Soportar 50,000 usuarios concurrentes en peak con p99 latencia < 500ms para KPIs.
- **Particionamiento de datos:** TimescaleDB hypertables particionadas por tiempo para queries eficientes sobre series históricas.

### 7.2 Seguridad

- **Datos financieros:** Encriptación en tránsito (TLS 1.3) y en reposo (AES-256). Los algoritmos de osciladores propietarios (NetBrute, Intenciones) son propiedad intelectual crítica.
- **AI Sandboxing:** El asistente IA opera en un sandbox sin acceso a red externa. Solo recibe KPIs pre-calculados como contexto. Nunca accede a internet.
- **Rate limiting:** Por tier de suscripción. Anti-scraping agresivo de datos de osciladores propietarios. Watermarking de datos para detectar filtración.
- **Compliance:** GDPR para usuarios europeos. MiFID II disclaimer obligatorio: "No constituye asesoramiento financiero." SOC 2 Type II para datos de usuario.
- **Audit trail:** Registro inmutable de todas las estrategias generadas y recomendaciones del asistente (entidad ChatMessage con kpi_context_snapshot).
- **Autenticación:** OAuth2 + MFA obligatorio para tier institucional. Rotación de API keys de proveedores de datos cada 90 días.

### 7.3 Rendimiento

| Métrica | Objetivo | Fuente del Requisito |
|---------|----------|---------------------|
| Carga de dashboard (KPIs) | < 3 segundos | Explícitamente mencionado: "en tres segundos tienes más de 50 KPIs" |
| Cálculo de estrategia completa | < 500ms | Inferido de UX fluido |
| Respuesta del asistente IA (first token) | < 1 segundo | Best practice de streaming LLM |
| Respuesta del asistente IA (completa) | < 8 segundos | Respuestas complejas con múltiples KPIs |
| Recálculo de osciladores tras cambio de precio | < 200ms | Tiempo real durante horas de mercado |
| WebSocket heartbeat (precios) | < 100ms latencia | Estándar de plataformas trading |
| Time-to-interactive del dashboard | < 2 segundos | Renderizado progresivo con SSR + streaming |

### 7.4 Usabilidad

- **Dark theme exclusivo** (estándar de la industria trading). Sin opción light theme en MVP.
- **Un solo activo cargado simultáneamente** (restricción de diseño explícita que simplifica UX y contexto del asistente).
- **KPIs organizados jerárquicamente:** resumen (precio, ATR) → osciladores (NetBrute, Intenciones, Momentum) → tendencias (200d, 134d, 50d) → volatilidad → macro (proyecciones, recesión).
- **Checklist visual con semáforo** (✅/❌) para decisión rápida pre-operación.
- **Asistente con sugerencias de prompts** para guiar al usuario hacia preguntas específicas (según advertencia #2).
- **Gauges visuales** para osciladores: representación intuitiva de valores y zonas.
- **Sparklines** en sidebar para visualización rápida de tendencia de precio por activo.
- **Responsive:** Optimizado para desktop (pantalla principal de operación) con soporte tablet. Mobile como consulta rápida de KPIs.

### 7.5 Disponibilidad

- **SLA objetivo:** 99.9% durante horas de mercado (NYSE: L-V 9:30-16:00 ET). 99.5% fuera de horario.
- **Crypto 24/7:** Los activos crypto requieren disponibilidad continua. Se toleran ventanas de mantenimiento de < 5 minutos entre 02:00-04:00 UTC (menor volumen global).
- **Graceful degradation:** Si el Data Engine falla, mostrar últimos KPIs conocidos con timestamp y alerta visual prominente: "Datos de hace X minutos. Verificar antes de operar."
- **RPO/RTO:** RPO < 1 hora (pérdida de datos aceptable: datos de mercado son efímeros), RTO < 15 minutos (las estrategias del usuario son críticas).
- **Multi-region:** us-east-1 (NYSE) + eu-west-1 (usuarios europeos) con failover automático.

---

## 8. Recomendaciones Estratégicas

### 8.1 Mejoras Futuras Priorizadas

| Prioridad | Mejora | Impacto | Esfuerzo |
|-----------|--------|---------|----------|
| **P0** | **Backtesting histórico:** Validar estrategias generadas contra datos pasados. Sin esto, las estrategias son teóricas sin validación empírica. | CRÍTICO | 3-4 sprints |
| **P1** | **Alertas push:** Notificaciones cuando osciladores cruzan umbrales configurados por el usuario (ej: NetBrute cruza a alcista) | ALTO | 2 sprints |
| **P1** | **Portfolio view:** Visualizar múltiples activos con correlación entre ellos y exposición sectorial | ALTO | 4 sprints |
| **P2** | **Journal de trading:** Registro automático de operaciones ejecutadas con análisis post-mortem vs lo que predijo el sistema | MEDIO | 2 sprints |
| **P2** | **Simulador Monte Carlo:** Simulación de escenarios para calcular probabilidad de ruina según parámetros del trader (mencionado en el documento fuente como capacidad del asistente) | MEDIO | 3 sprints |
| **P3** | **API para brokers:** Integración con Interactive Brokers, Binance para ejecución directa de estrategias desde ORION ONE | ALTO | 6+ sprints |
| **P3** | **Marketplace de estrategias:** Los usuarios pueden compartir/vender estrategias validadas por backtesting | MEDIO | 8+ sprints |

### 8.2 Riesgos Técnicos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| **Drift de osciladores propietarios** | ALTA | Los algoritmos de NetBrute e Intenciones pueden perder precisión con cambios estructurales del mercado | Recalibración trimestral automática (advertencia #4 del documento) + monitoring continuo de precisión con métricas de backtesting |
| **Dependencia de proveedores de datos** | MEDIA | Si Polygon.io tiene downtime, todo el sistema se degrada | Multi-provider con failover automático: Polygon → Alpha Vantage → Yahoo Finance. Health checks cada 30 segundos |
| **Alucinación del asistente IA** | MEDIA | El LLM podría generar datos que no están en el contexto proporcionado | Sandbox estricto: solo KPIs como input. Validación post-generación: verificar que cada número citado existe en el contexto. Logging de kpi_context_snapshot para auditoría |
| **Latencia en horas pico** | ALTA | Miles de usuarios cargando KPIs simultáneamente durante apertura de NYSE | Pre-computing de KPIs, cache agresivo en Redis con TTL de 1 segundo para precios, CDN para assets estáticos, auto-scaling predictivo |
| **Riesgo regulatorio** | ALTA | El sistema podría clasificarse como "asesoría financiera" en ciertas jurisdicciones | Disclaimers legales permanentes. Clasificación como "herramienta informativa". Revisión legal por jurisdicción antes de lanzamiento en cada mercado. Nunca usar lenguaje imperativo ("debes comprar") sino informativo ("las señales sugieren") |
| **Scraping de algoritmos propietarios** | MEDIA | Competidores podrían reverse-engineer los osciladores analizando las respuestas | Rate limiting agresivo, ofuscación de valores exactos en API pública (redondeo), watermarking de datos (variaciones microscópicas por usuario), detección de patrones de scraping |

### 8.3 Deuda Técnica Potencial

1. **Restricción de activo único hardcodeada:** Si se implementa como constraint fuerte en toda la arquitectura (base de datos, API, cache), migrar a multi-activo (portfolio view, Fase 2) requerirá refactorización significativa. **Recomendación:** Diseñar internamente para multi-activo desde el día uno (arrays de activos, sesiones independientes), pero restringir en la capa de UI con un simple `activeAsset.length === 1`.

2. **Osciladores acoplados al Data Engine:** Si NetBrute e Intenciones se calculan dentro del mismo servicio que ingesta datos de mercado, desacoplarlos posteriormente será costoso. **Recomendación:** Microservicio separado (M3) desde el inicio con interfaz clara: recibe datos → emite lecturas de osciladores.

3. **AI Assistant sin evaluación sistemática:** Sin un framework de evals automatizados que valide calidad de respuestas del asistente, la calidad puede degradarse silenciosamente con actualizaciones del modelo LLM. **Recomendación:** Implementar suite de evals desde MVP: 50+ test cases con respuestas esperadas, ejecutados en CI/CD antes de cada deploy.

4. **Ausencia de backtesting en MVP:** Generar estrategias sin validación histórica reduce la credibilidad del sistema y expone a riesgo reputacional. **Recomendación:** Priorizar como P0. Incluso un backtesting simplificado (últimos 6 meses) agrega valor enorme y permite al sistema mostrar "esta estrategia habría producido X% de retorno histórico".

5. **Chat sin memoria entre sesiones:** Si el asistente IA no mantiene historial de conversaciones previas, el usuario pierde contexto al recargar. **Recomendación:** Persistir ChatMessages en PostgreSQL y cargar últimos N mensajes como contexto del LLM al reabrir sesión.

### 8.4 Arquitecturas Alternativas Según Escenario

| Escenario | Arquitectura | Ventajas | Trade-offs |
|-----------|-------------|----------|------------|
| **Startup bootstrap (bajo presupuesto)** | Monolito modular: Next.js (full-stack) + Supabase (PostgreSQL managed + auth) + Python sidecar (cálculos) en Railway/Render | Rápido de lanzar (4-8 semanas). Costo < $200/mes. Un solo deploy. | Difícil escalar osciladores independientemente. Límite ~5,000 usuarios concurrentes. Python sidecar como bottleneck. |
| **Escala institucional** | Microservicios completos: Kubernetes + Kafka + Flink + GPU cluster para IA + TimescaleDB cluster + Redis Sentinel | Máximo rendimiento y escalabilidad. Cada pilar escala independiente. SLA 99.99%. | Costo $5,000-20,000/mes. Equipo mínimo de 8-10 personas. 6-9 meses hasta MVP. Complejidad operacional alta. |
| **Serverless-first** | Vercel (Next.js) + AWS Lambda (Python cálculos) + DynamoDB + Amazon Bedrock (IA) + EventBridge | Cero gestión de infraestructura. Pay-per-use. Escala automática. | Cold starts problemáticos para WebSocket real-time. DynamoDB no ideal para time-series. Vendor lock-in fuerte. |
| **Híbrido (RECOMENDADO)** | Next.js en Vercel (frontend) + Python FastAPI en ECS/EKS (backend/cálculos/osciladores) + PostgreSQL + TimescaleDB en RDS + Redis ElastiCache + Claude API | Balance óptimo: frontend managed sin preocupaciones, backend escalable con control total, costos controlados ($500-2,000/mes), time-to-market 3-4 meses. | Requiere gestión de ECS/EKS. Dos lenguajes (TypeScript + Python). Necesita DevOps competente. |

---

## Apéndice A: Datos de Referencia del Documento Fuente

### Ejemplo Apple (AAPL) — Valores Exactos Documentados

```yaml
Precio actual: $272.95
ATR actual: $3.27
Volatilidad implícita semanal: 24.56%
Variación volatilidad: +2.8% (expansión)
Rango 95% confianza: $268.28 — $285.32

Oscilador NetBrute:
  valor: -35.53
  cruce: alcista activo
  zona: bajista
  confianza: 57%

Oscilador Intenciones:
  estado: COMPRA
  zona: alcista
  confianza: 71%

Proyección economía 90 días: +1.56% (positiva)

Estrategia generada:
  dirección: LONG
  entrada: $272.95
  stop loss: $264.78 (2.5x ATR = $8.17)
  trailing stop: 2x ATR bajo precio máximo
  TP1 (50%): $289.29
  TP2 (30%): $297.46
  TP3 (20%): trailing stop
  capital: €10,000
  riesgo: 1% = €100
  posición: 100/8.17 = 12.24 → 12 acciones
```

### Ejemplo Ethereum (ETH) — Valores Exactos Documentados

```yaml
Precio actual: $2,660.88
Tendencia general: bajista
Momentum: 60.18 (neutral)
Volatilidad: 48.69% (alta, disminuyendo)
Probabilidad recesión: 51.62%
Proyección economía 90 días: -19.17% (negativa)

Oscilador NetBrute:
  cruce: bajista activo
  observación: vender con precaución

Tendencias múltiples:
  200 días: bajista
  134 días: alcista
  50 días: alcista
  DIVERGENCIA DETECTADA

Resistencia clave: $2,814

Recomendación: PRECAUCIÓN — esperar confirmación
```

### Checklist Pre-Operación (6 Verificaciones)

```
1. CONFLUENCIA: ¿NetBrute e Intenciones apuntan en misma dirección?
   → Si divergencia: actuar con precaución, esperar confirmación

2. PROYECCIÓN MACRO: ¿Proyección 90d alineada con dirección?
   → Positiva para compras, negativa para ventas

3. VOLATILIDAD: ¿Expansión o contracción?
   → Expansión: ampliar stops y TP en proporción
   → Contracción: stops más ajustados

4. CONFIANZA: ¿Nivel > 60%?
   → Si < 60%: buscar confirmación adicional en otros KPIs

5. POSICIÓN: ¿Tamaño calculado correctamente?
   → Regla del 1%: pérdida si salta stop = exactamente 1% del capital

6. RATIO R:R: ¿TP al menos 2x más lejos que SL?
   → Mínimo ratio 1:2
```

---

> **ORION ONE** | Documentación Técnica v1.0 | Abril 2026 | Confidencial
