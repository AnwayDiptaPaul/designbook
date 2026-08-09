"""Dependency-aware smoke check for a running DesignBook API."""

from __future__ import annotations

import json
import os
import sys
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


BASE_URL = os.environ.get("DESIGNBOOK_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def get_json(path: str) -> tuple[int, dict]:
    request = Request(BASE_URL + path, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{path} returned HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"cannot connect to {BASE_URL}: {exc.reason}") from exc


def main() -> int:
    try:
        health_status, health = get_json("/api/health")
        ready_status, ready = get_json("/api/ready")
        capability_status, capabilities = get_json("/api/capabilities")
    except RuntimeError as exc:
        print(f"RUNTIME SMOKE FAILED: {exc}", file=sys.stderr)
        return 2
    if health_status != 200 or health.get("status") != "healthy":
        print(f"RUNTIME SMOKE FAILED: unhealthy API response: {health}", file=sys.stderr)
        return 1
    if ready_status != 200 or ready.get("status") != "ready":
        print(f"RUNTIME SMOKE FAILED: dependencies are not ready: {ready}", file=sys.stderr)
        return 1
    if capability_status != 200 or capabilities.get("status") != "prototype":
        print(f"RUNTIME SMOKE FAILED: unexpected capability response: {capabilities}", file=sys.stderr)
        return 1
    print("RUNTIME SMOKE PASSED: API, database readiness, and capability boundary are healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())