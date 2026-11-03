import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    version: str
    build_time: str
    pod_name: str
    chaos_enabled: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            version=os.environ.get("APP_VERSION", "dev"),
            build_time=os.environ.get("BUILD_TIME", ""),
            pod_name=os.environ.get("POD_NAME", ""),
            # 오타("True", "1")로 운영에서 실험 기능이 켜지지 않도록 정확히 "true"만 인정
            chaos_enabled=os.environ.get("CHAOS_ENABLED") == "true",
        )
