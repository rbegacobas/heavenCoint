---
name: Estado del proyecto Heaven Coint
description: Qué módulos están hechos, qué está en progreso, qué sigue — referencia rápida de arranque
type: project
---

## Producto
Heaven Coint = clon mejorado de "Orion One" (transcripción en docs/heavenCoint.md). Plataforma cuantitativa de trading con osciladores propietarios, IA determinista, gestión de riesgo matemática.

## Stack
Backend: Python 3.12 + FastAPI + SQLAlchemy + Alembic + Redis + TimescaleDB/PostgreSQL  
Frontend: Next.js 16 + React + TypeScript strict + TailwindCSS + shadcn/ui  
Puertos: Backend:8000, Frontend:3000, PostgreSQL:5432, Redis:6379

## Estado por módulo (2026-04-03)
- M1 Data Ingestion ✅ — Polygon, Binance, FRED, 6 tests
- M2 Quant Engine ✅ — ATR, SMA, volatilidad, momentum, 10 tests  
- M4 Dashboard UI ✅ — 5 componentes desde diseño Penpot (disenoDashboard.pen), datos HARDCODEADOS
- **FASE B EN PROGRESO** — conectar frontend con backend (prioridad actual)
- M3 Oscillator Engine 🔲 — después de B
- M5 Risk Manager 🔲
- M6 AI Orchestrator 🔲
- M8 Strategy Builder + Checklist 🔲
- M9 User Management 🔲
- M10 Stripe 🔲

## Tests
21 backend + 1 frontend = 22 totales, todos pasando.

## Problema raíz resuelto en M4
`<main>` en dashboard/layout.tsx no era flex → todo el dashboard era una captura estática desalineada.

## Próxima tarea concreta
Fase B, empezar por B1: crear `frontend/src/lib/api.ts` + `frontend/src/types/api.ts`

**Why:** El frontend tiene UI pero no llama ningún endpoint. El backend calcula KPIs reales pero nadie los muestra.

**How to apply:** Antes de tocar código, verificar que el backend está corriendo: `curl http://localhost:8000/api/v1/health`
