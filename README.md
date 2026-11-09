# portfolio

[homelab](https://github.com/June21621/homelab) k3s 클러스터에 GitOps로 배포되는 FastAPI 앱.
지금은 배포 파이프라인 확인용 최소 페이지이고, 내용은 나중에 채운다.

배포: main push → GitHub Actions가 테스트·이미지 빌드(태그 = 커밋 SHA) → homelab `gitops/apps/portfolio/overlays/*`의 `newTag` 변경 → ArgoCD 반영.

## 엔드포인트

| 경로 | 설명 |
|---|---|
| `GET /` | 버전(git SHA)·빌드 시각·파드 이름 |
| `GET /healthz`, `GET /readyz` | liveness·readiness 프로브 |
| `GET /metrics` | Prometheus 지표 (`http_requests_total`, `http_request_duration_seconds`) |
| `POST /chaos/memory?mb=N` | 메모리 N MiB를 잡고 놓지 않음 (OOM 실험) |
| `POST /chaos/crash` | 응답 후 프로세스 종료 (재시작 실험) |

`/chaos/*`는 `CHAOS_ENABLED=true`일 때만 생긴다. 운영(prod)에서는 꺼져 있고 실험용(lab)에서만 켠다.

## 환경 변수

| 이름 | 기본값 | 설명 |
|---|---|---|
| `APP_VERSION` | `dev` | 이미지 빌드 인자 `GIT_SHA` |
| `BUILD_TIME` | (빈 값) | 이미지 빌드 인자 `BUILD_TIME` |
| `POD_NAME` | (빈 값) | downward API로 주입 |
| `CHAOS_ENABLED` | `false` | 정확히 `true`일 때만 켜짐 |

## 개발

```bash
uv sync
uv run pytest
uv run uvicorn portfolio.app:app --reload
```
