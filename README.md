# portfolio

[homelab](https://github.com/June21621/homelab) k3s 클러스터에 GitOps로 배포되는 FastAPI 앱.
지금은 배포 파이프라인 확인용 최소 페이지이고, 내용은 나중에 채운다.

## 배포 흐름

main에 병합하면 사람 손 없이 homelab 클러스터까지 간다(병합 → prod 반영 약 8분).

1. 이 repo의 Actions: 테스트 → homelab의 재사용 워크플로(`build-and-bump.yaml`)로 이미지 빌드 →
   GHCR push(태그 = 커밋 SHA) → 빌드 증명서(attestation)
2. 태그 갱신 GitHub App이 homelab에 PR을 연다. 바뀌는 건 overlay의 `newTag`·`digest` 두 줄뿐
3. homelab의 필수 검사(`tag-pr-guard`)가 그 두 줄만 바뀌었는지, 새 커밋이 지금 배포본보다 앞서는지,
   그 다이제스트가 이 repo main의 그 커밋에서 homelab main의 워크플로로 빌드됐는지 확인 → 통과하면 자동 병합
4. 클러스터 안 ArgoCD가 homelab main을 읽어 반영. 이미지는 다이제스트로 받으므로 태그를 덮어써도 영향이 없다

이 repo는 클러스터에 접근할 권한이 없다. 할 수 있는 일은 homelab에 태그 PR을 여는 것까지다.

## 엔드포인트

| 경로 | 설명 |
|---|---|
| `GET /` | 버전(git SHA)·빌드 시각·파드 이름 |
| `GET /version` | 같은 정보를 JSON으로 (`version`, `build_time`, `pod`) |
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
