#!/bin/bash
# Start script — applies migrations then starts uvicorn.
# Usage: bash start.sh
# This ensures the DB schema is always up to date before the server accepts requests.

set -e

echo "⏳ Waiting for database..."
python3 -c "
import asyncio, sys
async def wait():
    import asyncpg
    for i in range(30):
        try:
            conn = await asyncpg.connect(
                host='localhost', port=5432,
                user='heavencoint', password='heavencoint_dev_2026', database='heavencoint'
            )
            await conn.close()
            print('✅ Database ready')
            return
        except Exception:
            print(f'  Attempt {i+1}/30 — retrying...')
            await asyncio.sleep(1)
    print('❌ Database not ready after 30s')
    sys.exit(1)
asyncio.run(wait())
" 2>/dev/null || echo "DB check skipped (asyncpg not installed in env)"

echo "🔄 Applying migrations..."
alembic upgrade head

echo "👤 Ensuring admin user exists..."
python3 << 'PYEOF'
import asyncio
from app.core.database import engine
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def ensure_admin():
    async with AsyncSession(engine) as db:
        result = await db.execute(select(User).where(User.email == "admin@heavencoint.com"))
        if result.scalar_one_or_none() is None:
            db.add(User(
                email="admin@heavencoint.com",
                password_hash=get_password_hash("Admin1234!"),
                full_name="Admin",
                is_active=True,
                is_verified=True,
            ))
            await db.commit()
            print("✅ Admin user created")
        else:
            print("✅ Admin user already exists")

asyncio.run(ensure_admin())
PYEOF

echo "🚀 Starting server..."
uvicorn app.main:app --reload --port 8000
