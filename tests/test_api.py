# test_api.py - checks for the web API. The AI is faked, so no internet needed.

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient

import api
import ghost

client = TestClient(api.app)


def fake_ghost(report):
    return "fake explanation", None


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_cases_are_listed():
    response = client.get("/cases")
    assert response.status_code == 200
    assert "sub_carry_bug" in response.json()["cases"]
    assert "good_alu" in response.json()["cases"]


def test_unknown_case_is_rejected():
    response = client.post("/investigate/../../secret")
    assert response.status_code in (404, 405)
    response = client.post("/investigate/not_a_real_case")
    assert response.status_code == 404


def test_buggy_case_is_caught(monkeypatch):
    monkeypatch.setattr(ghost, "ask_ghost", fake_ghost)
    response = client.post("/investigate/sub_carry_bug")
    assert response.status_code == 200
    body = response.json()
    assert body["report"]["verdict"] == "FAIL"
    assert body["report"]["failures"][0]["test_id"] == "SUB_EQUAL"
    assert body["ghost"] == "fake explanation"


def test_good_case_passes(monkeypatch):
    monkeypatch.setattr(ghost, "ask_ghost", fake_ghost)
    response = client.post("/investigate/good_alu")
    assert response.status_code == 200
    assert response.json()["report"]["verdict"] == "PASS"