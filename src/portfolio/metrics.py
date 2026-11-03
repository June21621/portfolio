import time

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest

# 앱을 여러 번 만들어도(테스트) 지표가 중복 등록되지 않게 모듈에서 한 번만 만든다
REGISTRY = CollectorRegistry()
REQUESTS = Counter(
    "http_requests_total", "HTTP 요청 수", ["method", "path", "status"], registry=REGISTRY
)
LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP 요청 처리 시간", ["path"], registry=REGISTRY
)

METRICS_PATH = "/metrics"


def route_template(request: Request) -> str:
    """경로 라벨은 실제 URL이 아니라 라우트 템플릿. 없는 경로는 하나로 묶어 라벨 수 폭증을 막는다"""
    route = request.scope.get("route")
    return getattr(route, "path", "<unmatched>")


async def record(request: Request, call_next) -> Response:
    if request.url.path == METRICS_PATH:
        return await call_next(request)
    start = time.perf_counter()
    response = await call_next(request)
    path = route_template(request)
    REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    LATENCY.labels(path).observe(time.perf_counter() - start)
    return response


def metrics_endpoint() -> Response:
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
