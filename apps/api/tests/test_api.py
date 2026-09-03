"""API foundation tests for Phase 4.

Uses FastAPI TestClient with the real app and in-memory SQLite for isolation.
No external services, no LLM, no real banking data.

IMPORTANT: These tests use SQLite (file::memory:?cache=shared) ONLY for test
isolation. PostgreSQL remains the production source of truth. Tests explicitly
verify the API contract boundary — not intelligence logic.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models import domain  # ensure all models are registered


# ── Test DB setup (SQLite in-memory, test-only) ───────────────────────────────

TEST_DATABASE_URL = "sqlite:///:memory:?cache=shared"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# SQLite does not enforce FK constraints by default — enable them
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helper: seed data ─────────────────────────────────────────────────────────

def _seed(db_session):
    from app.models.domain import User, Recipient, ScenarioDefinition
    user = User()
    recipient = Recipient()
    db_session.add_all([user, recipient])
    db_session.flush()

    scenario = ScenarioDefinition(name="BANK_IMPERSONATION", description="Simulates a bank impersonation call.")
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(recipient)
    db_session.refresh(scenario)
    return user, recipient, scenario


# ── 1. Root / health ──────────────────────────────────────────────────────────

def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "raksha-api"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── 2. Transaction endpoint: availability + validation ────────────────────────

def test_transaction_analyze_missing_fields(client):
    resp = client.post("/api/v1/transactions/analyze", json={})
    assert resp.status_code == 422


def test_transaction_analyze_invalid_user(client, db_session):
    resp = client.post(
        "/api/v1/transactions/analyze",
        json={
            "user_id": "99999",
            "recipient_id": "1",
            "amount": 1000,
            "currency": "INR",
        },
    )
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "USER_NOT_FOUND"


def test_transaction_analyze_invalid_recipient(client, db_session):
    user, _, _ = _seed(db_session)
    resp = client.post(
        "/api/v1/transactions/analyze",
        json={
            "user_id": str(user.id),
            "recipient_id": "99999",
            "amount": 1000,
            "currency": "INR",
        },
    )
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "RECIPIENT_NOT_FOUND"


def test_transaction_analyze_valid(client, db_session):
    user, recipient, _ = _seed(db_session)
    resp = client.post(
        "/api/v1/transactions/analyze",
        json={
            "user_id": str(user.id),
            "recipient_id": str(recipient.id),
            "amount": 50000,
            "currency": "INR",
            "reason": "Bank officer told me to verify my account",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "transaction_id" in body
    assert "behavior" in body
    assert "recipient" in body
    assert "intent" in body
    assert "risk" in body
    assert "friction" in body


# ── 3. Users ──────────────────────────────────────────────────────────────────

def test_get_user_not_found(client, db_session):
    resp = client.get("/api/v1/users/99999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "USER_NOT_FOUND"


def test_get_user_found(client, db_session):
    user, _, _ = _seed(db_session)
    resp = client.get(f"/api/v1/users/{user.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == user.id


# ── 4. Recipients ─────────────────────────────────────────────────────────────

def test_get_recipient_not_found(client, db_session):
    resp = client.get("/api/v1/recipients/99999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "RECIPIENT_NOT_FOUND"


def test_get_recipient_found(client, db_session):
    _, recipient, _ = _seed(db_session)
    resp = client.get(f"/api/v1/recipients/{recipient.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == recipient.id


def test_recipient_graph(client, db_session):
    _, recipient, _ = _seed(db_session)
    resp = client.get(f"/api/v1/recipients/{recipient.id}/graph")
    assert resp.status_code == 200
    body = resp.json()
    assert "score" in body
    assert "model_version" in body


def test_recipient_graph_not_found(client, db_session):
    resp = client.get("/api/v1/recipients/99999/graph")
    assert resp.status_code == 404


# ── 5. Scenarios ──────────────────────────────────────────────────────────────

def test_list_scenarios(client, db_session):
    _seed(db_session)
    resp = client.get("/api/v1/scenarios")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_scenario_found(client, db_session):
    _, _, scenario = _seed(db_session)
    resp = client.get(f"/api/v1/scenarios/{scenario.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == scenario.name


def test_get_scenario_not_found(client, db_session):
    resp = client.get("/api/v1/scenarios/99999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "SCENARIO_NOT_FOUND"


def test_run_scenario_not_found(client, db_session):
    resp = client.post("/api/v1/scenarios/99999/run")
    assert resp.status_code == 404


def test_run_scenario_found(client, db_session):
    _, _, scenario = _seed(db_session)
    resp = client.post(f"/api/v1/scenarios/{scenario.id}/run")
    assert resp.status_code == 200
    body = resp.json()
    assert body["scenario_id"] == scenario.id
    assert "status" in body


# ── 6. Dashboard ──────────────────────────────────────────────────────────────

def test_dashboard_summary(client, db_session):
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_transactions" in body
    assert "flagged_transactions" in body
    assert "active_clusters" in body


def test_dashboard_transactions(client, db_session):
    resp = client.get("/api/v1/dashboard/transactions")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_dashboard_clusters(client, db_session):
    resp = client.get("/api/v1/dashboard/clusters")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ── 7. Behavior adapter integration boundary ──────────────────────────────────

def test_behavior_adapter_stub(client, db_session):
    """Verify the behavior adapter returns a contract-compliant result
    even when P2's engine is not yet merged."""
    from app.services.behavior.adapter import run_behavior_analysis
    from app.schemas.transaction import TransactionContext

    ctx = TransactionContext(user_id="1", recipient_id="1", amount=1000, currency="INR")
    result = run_behavior_analysis(ctx, db_session)

    assert "score" in result
    assert "signals" in result
    assert "features" in result
    assert result["model_version"] == "behavior-v1"
    assert 0 <= result["score"] <= 100


# ── 8. Recipient adapter integration boundary ─────────────────────────────────

def test_recipient_adapter_stub(client, db_session):
    """Verify the recipient adapter returns a contract-compliant result
    even when P3's engine is not yet merged."""
    from app.services.recipient.adapter import run_recipient_analysis

    _, recipient, _ = _seed(db_session)
    result = run_recipient_analysis(str(recipient.id), db_session)

    assert "score" in result
    assert "signals" in result
    assert "recipient_profile" in result
    assert "network" in result
    assert result["model_version"] == "recipient-v1"
    assert 0 <= result["score"] <= 100
