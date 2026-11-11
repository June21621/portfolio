# syntax=docker/dockerfile:1

# 1단계: uv로 uv.lock에 고정된 의존성과 앱을 가상환경에 설치
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS build
COPY --from=ghcr.io/astral-sh/uv:0.12.23@sha256:61d393e44e249f2e4b526b6c7ddcecce245946826e608e11c93ad4f5bba55b21 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
# 의존성 층을 먼저 만들어 두면 코드만 바뀐 빌드는 캐시를 쓴다
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

# 2단계: 가상환경만 옮긴 런타임 (uv·빌드 도구 없음)
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
LABEL org.opencontainers.image.source=https://github.com/June21621/portfolio
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
COPY --from=build /app/.venv /app/.venv
# 빌드마다 바뀌는 값은 마지막에 둬서 위 층의 캐시를 깨지 않는다
ARG GIT_SHA=dev
ARG BUILD_TIME=
ENV APP_VERSION=${GIT_SHA} \
    BUILD_TIME=${BUILD_TIME} \
    PATH=/app/.venv/bin:${PATH} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
USER 10001
EXPOSE 8000
CMD ["uvicorn", "portfolio.app:app", "--host", "0.0.0.0", "--port", "8000"]
