"""Tests for health check and auth endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["redis"] == "ok"


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient) -> None:
    # Register
    register_body = {
        "email": "test@heaven.com",
        "password": "Test@1234",
        "full_name": "Test User",
        "preferred_language": "es",
    }
    resp = await client.post("/api/v1/auth/register", json=register_body)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@heaven.com"
    assert data["subscription_tier"] == "free"

    # Login
    login_body = {"email": "test@heaven.com", "password": "Test@1234"}
    resp = await client.post("/api/v1/auth/login", json=login_body)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@heaven.com"

    # Me
    token = data["access_token"]
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@heaven.com"

    # Refresh
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": data["refresh_token"]})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    body = {
        "email": "dup@heaven.com",
        "password": "Test@1234",
        "full_name": "Dup User",
    }
    resp = await client.post("/api/v1/auth/register", json=body)
    assert resp.status_code == 201

    resp = await client.post("/api/v1/auth/register", json=body)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@heaven.com", "password": "Wrong@123"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@heaven.com", "password": "short", "full_name": "Weak"},
    )
    assert resp.status_code == 422
