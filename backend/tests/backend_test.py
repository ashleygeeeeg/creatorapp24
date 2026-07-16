"""Regression tests for maligeeAi backend - all /api endpoints."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://genesis-clone-1.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"

# Generate unique test user per run
UNIQUE = uuid.uuid4().hex[:8]
TEST_EMAIL = f"testuser_e2e_{UNIQUE}@maligee.ai"
TEST_PASSWORD = "TestPass123!"
TEST_NAME = "E2E Tester"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def auth_ctx(session):
    """Signup then reuse token+user across tests."""
    r = session.post(f"{API}/auth/signup", json={
        "email": TEST_EMAIL, "password": TEST_PASSWORD, "name": TEST_NAME
    })
    assert r.status_code == 200, f"signup failed: {r.status_code} {r.text}"
    d = r.json()
    return {"token": d["token"], "user": d["user"], "headers": {"Authorization": f"Bearer {d['token']}"}}


# ─── Root / Health ───
def test_root(session):
    r = session.get(f"{API}/")
    assert r.status_code == 200
    assert "maligeeAi" in r.json().get("message", "")


# ─── Auth ───
class TestAuth:
    def test_signup_creates_user(self, auth_ctx):
        assert auth_ctx["user"]["email"] == TEST_EMAIL
        assert auth_ctx["user"]["has_free_build"] is True
        assert len(auth_ctx["token"]) > 20

    def test_signup_duplicate_email(self, session):
        r = session.post(f"{API}/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
        assert r.status_code == 409

    def test_login_success(self, session):
        r = session.post(f"{API}/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
        assert r.status_code == 200
        assert "token" in r.json()

    def test_login_wrong_password(self, session):
        r = session.post(f"{API}/auth/login", json={"email": TEST_EMAIL, "password": "wrong"})
        assert r.status_code == 401

    def test_me_returns_user(self, session, auth_ctx):
        r = session.get(f"{API}/auth/me", headers=auth_ctx["headers"])
        assert r.status_code == 200
        d = r.json()
        assert d["email"] == TEST_EMAIL
        assert "build_count" in d

    def test_me_requires_auth(self, session):
        r = session.get(f"{API}/auth/me")
        assert r.status_code == 401


# ─── Builds & Mock Payment ───
class TestBuilds:
    def test_first_build_is_free(self, session, auth_ctx):
        r = session.post(f"{API}/builds", json={"name": "TEST_First Build", "description": "free one"},
                         headers=auth_ctx["headers"])
        assert r.status_code == 200
        d = r.json()
        assert d["is_free"] is True
        assert d["payment_status"] == "free"
        auth_ctx["free_build_id"] = d["id"]

    def test_second_build_requires_payment(self, session, auth_ctx):
        r = session.post(f"{API}/builds", json={"name": "TEST_Second Build"}, headers=auth_ctx["headers"])
        assert r.status_code == 200
        d = r.json()
        assert d["is_free"] is False
        assert d["payment_status"] == "pending"
        assert d["price"] == 10.0
        auth_ctx["paid_build_id"] = d["id"]

    def test_list_builds(self, session, auth_ctx):
        r = session.get(f"{API}/builds", headers=auth_ctx["headers"])
        assert r.status_code == 200
        builds = r.json()
        assert isinstance(builds, list)
        assert len(builds) >= 2

    def test_edit_build_free(self, session, auth_ctx):
        bid = auth_ctx["free_build_id"]
        r = session.put(f"{API}/builds/{bid}", json={"name": "TEST_Renamed"}, headers=auth_ctx["headers"])
        assert r.status_code == 200
        assert r.json()["name"] == "TEST_Renamed"

    def test_mock_payment_for_second_build(self, session, auth_ctx):
        bid = auth_ctx["paid_build_id"]
        r = session.post(f"{API}/builds/{bid}/pay", headers=auth_ctx["headers"])
        assert r.status_code == 200
        d = r.json()
        assert d["payment_status"] in ("mock_paid", "paid")

        # Verify persistence
        r2 = session.get(f"{API}/builds", headers=auth_ctx["headers"])
        paid = [b for b in r2.json() if b["id"] == bid][0]
        assert paid["payment_status"] == "mock_paid"

    def test_deploy_paid_build(self, session, auth_ctx):
        bid = auth_ctx["paid_build_id"]
        r = session.post(f"{API}/builds/{bid}/deploy", headers=auth_ctx["headers"])
        assert r.status_code == 200
        assert r.json()["status"] == "deployed"

    def test_builds_require_auth(self, session):
        r = session.get(f"{API}/builds")
        assert r.status_code == 401


# ─── Landing/Public ───
class TestLanding:
    def test_showcase(self, session):
        r = session.get(f"{API}/showcase")
        assert r.status_code == 200
        assert len(r.json()) > 0

    def test_features(self, session):
        r = session.get(f"{API}/features")
        assert r.status_code == 200
        assert len(r.json()) > 0

    def test_stats(self, session):
        r = session.get(f"{API}/stats")
        assert r.status_code == 200
        assert "users_count" in r.json()

    def test_pricing(self, session):
        r = session.get(f"{API}/pricing")
        assert r.status_code == 200
        assert len(r.json()["plans"]) >= 2

    def test_waitlist_signup(self, session):
        email = f"waitlist_{UNIQUE}@example.com"
        r = session.post(f"{API}/waitlist", json={"email": email, "name": "WL Test"})
        assert r.status_code == 200
        assert r.json()["email"] == email

    def test_waitlist_duplicate(self, session):
        email = f"waitlist_{UNIQUE}@example.com"
        r = session.post(f"{API}/waitlist", json={"email": email})
        assert r.status_code == 409

    def test_waitlist_count(self, session):
        r = session.get(f"{API}/waitlist/count")
        assert r.status_code == 200
        assert isinstance(r.json()["count"], int)


# ─── AI Chat (Emergent LLM) ───
class TestChat:
    def test_chat_with_ai(self, session, auth_ctx):
        r = session.post(f"{API}/chat", json={"message": "Hi! Reply with just: pong"},
                         headers=auth_ctx["headers"], timeout=60)
        assert r.status_code == 200, f"chat failed: {r.text}"
        d = r.json()
        assert "response" in d
        assert len(d["response"]) > 0
        assert "session_id" in d
        auth_ctx["chat_session"] = d["session_id"]

    def test_chat_history(self, session, auth_ctx):
        sid = auth_ctx.get("chat_session")
        if not sid:
            pytest.skip("no chat session")
        r = session.get(f"{API}/chat/history/{sid}", headers=auth_ctx["headers"])
        assert r.status_code == 200
        hist = r.json()
        assert len(hist) >= 2  # user + assistant

    def test_chat_sessions_list(self, session, auth_ctx):
        r = session.get(f"{API}/chat/sessions", headers=auth_ctx["headers"])
        assert r.status_code == 200


# ─── Share Links ───
class TestShare:
    def test_share_non_deployed_returns_400(self, session, auth_ctx):
        # free build was renamed but not deployed
        bid = auth_ctx["free_build_id"]
        r = session.post(f"{API}/builds/{bid}/share", headers=auth_ctx["headers"])
        assert r.status_code == 400

    def test_share_deployed_returns_slug(self, session, auth_ctx):
        bid = auth_ctx["paid_build_id"]  # deployed in TestBuilds
        r = session.post(f"{API}/builds/{bid}/share", headers=auth_ctx["headers"])
        assert r.status_code == 200
        slug = r.json()["share_slug"]
        assert isinstance(slug, str) and len(slug) >= 6
        auth_ctx["share_slug"] = slug

    def test_share_slug_is_stable(self, session, auth_ctx):
        bid = auth_ctx["paid_build_id"]
        r1 = session.post(f"{API}/builds/{bid}/share", headers=auth_ctx["headers"])
        r2 = session.post(f"{API}/builds/{bid}/share", headers=auth_ctx["headers"])
        assert r1.json()["share_slug"] == r2.json()["share_slug"]

    def test_public_get_share_no_auth(self, session, auth_ctx):
        slug = auth_ctx["share_slug"]
        # no auth header
        r = requests.get(f"{API}/share/{slug}")
        assert r.status_code == 200
        d = r.json()
        assert d["name"] and d["status"] == "deployed"
        assert "owner_name" in d

    def test_public_get_bad_slug_404(self, session):
        r = requests.get(f"{API}/share/badslug_zzz_nope")
        assert r.status_code == 404

    def test_share_others_build_404(self, session, auth_ctx):
        # create a second user and try to share the first user's build
        email2 = f"other_{UNIQUE}@maligee.ai"
        r = session.post(f"{API}/auth/signup", json={"email": email2, "password": TEST_PASSWORD})
        assert r.status_code == 200
        headers2 = {"Authorization": f"Bearer {r.json()['token']}"}
        r = session.post(f"{API}/builds/{auth_ctx['paid_build_id']}/share", headers=headers2)
        assert r.status_code == 404

    def test_share_requires_auth(self, session, auth_ctx):
        r = requests.post(f"{API}/builds/{auth_ctx['paid_build_id']}/share")
        assert r.status_code == 401
