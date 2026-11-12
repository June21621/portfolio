import os
from html import escape

from fastapi import BackgroundTasks, FastAPI, Query
from fastapi.responses import HTMLResponse

from portfolio import metrics
from portfolio.settings import Settings

PAGE = """<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><title>portfolio</title></head>
<body>
<h1>portfolio</h1>
<dl>
<dt>version</dt><dd>{version}</dd>
<dt>build time</dt><dd>{build_time}</dd>
<dt>pod</dt><dd>{pod_name}</dd>
</dl>
</body>
</html>
"""


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="portfolio", docs_url=None, redoc_url=None, openapi_url=None)
    app.middleware("http")(metrics.record)
    app.add_api_route(metrics.METRICS_PATH, metrics.metrics_endpoint, methods=["GET"])

    page = PAGE.format(
        version=escape(settings.version),
        build_time=escape(settings.build_time),
        pod_name=escape(settings.pod_name),
    )

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return page

    build_info = {
        "version": settings.version,
        "build_time": settings.build_time,
        "pod": settings.pod_name,
    }

    @app.get("/version")
    def version() -> dict:
        return build_info

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> dict:
        return {"status": "ok"}

    if settings.chaos_enabled:
        add_chaos_routes(app)
    return app


def add_chaos_routes(app: FastAPI) -> None:
    """lab에서만 켜는 실험용 엔드포인트. 꺼져 있으면 라우트 자체가 없어 404"""
    held: list[bytearray] = []

    @app.post("/chaos/memory", status_code=202)
    def chaos_memory(mb: int = Query(ge=1, le=4096)) -> dict:
        # 0으로 채워 실제 메모리를 차지하게 하고, 리스트에 쥐고 있어 해제되지 않는다
        held.append(bytearray(mb * 2**20))
        return {"held_mb": sum(len(b) for b in held) // 2**20}

    @app.post("/chaos/crash", status_code=202)
    def chaos_crash(tasks: BackgroundTasks) -> dict:
        # 응답을 보낸 뒤 비정상 종료 → 컨테이너 재시작
        tasks.add_task(os._exit, 1)
        return {"crashing": True}


app = create_app(Settings.from_env())
