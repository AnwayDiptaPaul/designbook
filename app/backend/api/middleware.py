# pyre-ignore-all-errors
"""Rate-limiting middleware for DesignBook API.

Implements fix.md §Circuit Breakers:
  - Limits concurrent analysis requests to prevent CPU thrashing
  - Returns 429 Too Many Requests when limit is exceeded
  - Tracks active requests per-endpoint category
"""

import asyncio
import logging
import time
from typing import Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("designbook.middleware")


class AnalysisRateLimiter(BaseHTTPMiddleware):
    """Circuit-breaker middleware that limits concurrent analysis requests.

    Prevents the server from being overwhelmed by simultaneous OpenSees
    analysis calls, which are CPU-intensive and can exhaust system memory.
    """

    def __init__(self, app, max_concurrent_analysis: int = 5, max_concurrent_design: int = 20):
        super().__init__(app)
        self.max_concurrent_analysis = max_concurrent_analysis
        self.max_concurrent_design = max_concurrent_design
        self._analysis_semaphore = asyncio.Semaphore(max_concurrent_analysis)
        self._design_semaphore = asyncio.Semaphore(max_concurrent_design)
        self._request_count: Dict[str, int] = {"analysis": 0, "design": 0, "other": 0}
        self._lock = asyncio.Lock()

    def _classify_request(self, path: str, method: str) -> str:
        """Classify the request into a rate-limit category."""
        if "analysis" in path.lower() and method.upper() == "POST":
            return "analysis"
        if "design" in path.lower() and method.upper() == "POST":
            return "design"
        return "other"

    async def dispatch(self, request: Request, call_next):
        category = self._classify_request(str(request.url.path), request.method)

        if category == "analysis":
            if self._analysis_semaphore.locked() and self._request_count["analysis"] >= self.max_concurrent_analysis:
                logger.warning(
                    f"Rate limit exceeded: {self._request_count['analysis']} concurrent analysis requests"
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many concurrent analysis requests. Please wait.",
                        "active_requests": self._request_count["analysis"],
                        "max_allowed": self.max_concurrent_analysis,
                    },
                )
            async with self._analysis_semaphore:
                async with self._lock:
                    self._request_count["analysis"] += 1
                try:
                    t_start = time.perf_counter()
                    response = await call_next(request)
                    dt = time.perf_counter() - t_start
                    logger.info(f"Analysis request completed in {dt:.3f}s")
                    return response
                finally:
                    async with self._lock:
                        self._request_count["analysis"] -= 1

        elif category == "design":
            if self._design_semaphore.locked() and self._request_count["design"] >= self.max_concurrent_design:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many concurrent design requests.",
                        "active_requests": self._request_count["design"],
                        "max_allowed": self.max_concurrent_design,
                    },
                )
            async with self._design_semaphore:
                async with self._lock:
                    self._request_count["design"] += 1
                try:
                    response = await call_next(request)
                    return response
                finally:
                    async with self._lock:
                        self._request_count["design"] -= 1

        # Non-rate-limited paths pass through directly
        return await call_next(request)
