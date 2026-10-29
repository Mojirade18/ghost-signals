# test_ghost.py - checks for the AI ghost that never call the real AI.

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import ghost


def test_passing_report_skips_the_ai():
    # A passing design has nothing to explain, so no AI call is made.
    explanation, error = ghost.ask_ghost({"verdict": "PASS"})
    assert error is None
    assert "passed" in explanation.lower()


def test_missing_settings_gives_clear_error(monkeypatch):
    monkeypatch.delenv("AI_BASE_URL", raising=False)
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.delenv("AI_MODEL", raising=False)
    explanation, error = ghost.ask_ghost({"verdict": "FAIL"})
    assert explanation is None
    assert ".env" in error


def test_messages_contain_the_evidence():
    report = {"verdict": "FAIL", "failures": [{"test_id": "SUB_EQUAL"}]}
    messages = ghost.build_messages(report)
    assert messages[0]["role"] == "system"
    assert "SUB_EQUAL" in messages[1]["content"]