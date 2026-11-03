import os

import pytest
from fastapi.testclient import TestClient

from portfolio import app as app_module
from portfolio.app import create_app
from portfolio.settings import Settings


def make_client(**overrides) -> TestClient:
    fields = {"version": "dev", "build_time": "", "pod_name": "", "chaos_enabled": False}
    return TestClient(create_app(Settings(**(fields | overrides))))


def test_index_shows_version_and_pod():
    res = make_client(version="abc123", pod_name="p-1").get("/")
    assert res.status_code == 200
    assert "abc123" in res.text
    assert "p-1" in res.text


def test_healthz_and_readyz():
    client = make_client()
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 200


def test_metrics_exposes_request_counter():
    client = make_client()
    client.get("/")
    body = client.get("/metrics").text
    assert "http_requests_total" in body
    assert 'path="/"' in body


def test_chaos_hidden_when_disabled():
    client = make_client(chaos_enabled=False)
    assert client.post("/chaos/memory?mb=1").status_code == 404
    assert client.post("/chaos/crash").status_code == 404


def test_chaos_memory_allocates():
    res = make_client(chaos_enabled=True).post("/chaos/memory?mb=5")
    assert res.status_code == 202
    assert res.json()["held_mb"] >= 5


def rss_mb() -> float:
    """현재 프로세스가 실제로 차지한 물리 메모리 (Linux /proc)"""
    with open("/proc/self/statm") as f:
        pages = int(f.read().split()[1])
    return pages * os.sysconf("SC_PAGE_SIZE") / 2**20


def test_chaos_memory_is_resident():
    # 잡기만 하고 쓰지 않은 메모리는 Linux가 물리 메모리를 안 줘서 OOM 실험이 안 된다
    client = make_client(chaos_enabled=True)
    before = rss_mb()
    client.post("/chaos/memory?mb=64")
    assert rss_mb() - before >= 60


@pytest.mark.parametrize("mb", [0, 4097])
def test_chaos_memory_rejects_bad_size(mb):
    assert make_client(chaos_enabled=True).post(f"/chaos/memory?mb={mb}").status_code == 422


def test_chaos_crash_schedules_exit(monkeypatch):
    calls = []
    monkeypatch.setattr(app_module.os, "_exit", calls.append)
    res = make_client(chaos_enabled=True).post("/chaos/crash")
    assert res.status_code == 202
    assert calls == [1]


@pytest.mark.parametrize(("value", "expected"), [("1", False), ("yes", False), (None, False), ("true", True)])
def test_settings_chaos_only_true_string(monkeypatch, value, expected):
    if value is None:
        monkeypatch.delenv("CHAOS_ENABLED", raising=False)
    else:
        monkeypatch.setenv("CHAOS_ENABLED", value)
    assert Settings.from_env().chaos_enabled is expected
