import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Config:
    db_path: str = "runtime/lanes_ceo.sqlite3"
    timezone: str = "Asia/Shanghai"
    artifact_dir: str = "runtime/artifacts"
    log_level: str = "INFO"
    log_file: str = "runtime/lanes_ceo.log"

    feishu_enabled: bool = False
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    feishu_webhook_host: str = ""
    feishu_webhook_port: int = 0

    weixin_enabled: bool = False
    qq_enabled: bool = False

    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""

    deepseek_balance_threshold: float = 10.0
    deepseek_api_key: str = ""

    email_enabled: bool = False
    email_address: str = ""
    email_password: str = ""
    email_imap_server: str = ""
    email_smtp_server: str = ""

    notification_default_channel: str = "cli"

    @classmethod
    def from_env(cls) -> "Config":
        _load_dotenv()
        return cls(
            db_path=os.getenv("LANES_CEO_DB_PATH", "runtime/lanes_ceo.sqlite3"),
            timezone=os.getenv("LANES_CEO_TIMEZONE", "Asia/Shanghai"),
            artifact_dir=os.getenv("LANES_CEO_ARTIFACT_DIR", "runtime/artifacts"),
            log_level=os.getenv("LANES_CEO_LOG_LEVEL", "INFO"),
            log_file=os.getenv("LANES_CEO_LOG_FILE", "runtime/lanes_ceo.log"),
            feishu_enabled=_bool_env("LANES_CEO_FEISHU_ENABLED"),
            feishu_app_id=os.getenv("LANES_CEO_FEISHU_APP_ID", ""),
            feishu_app_secret=os.getenv("LANES_CEO_FEISHU_APP_SECRET", ""),
            feishu_webhook_host=os.getenv("LANES_CEO_FEISHU_WEBHOOK_HOST", "127.0.0.1"),
            feishu_webhook_port=int(os.getenv("LANES_CEO_FEISHU_WEBHOOK_PORT", "8080")),
            weixin_enabled=_bool_env("LANES_CEO_WEIXIN_ENABLED"),
            qq_enabled=_bool_env("LANES_CEO_QQ_ENABLED"),
            llm_provider=os.getenv("LANES_CEO_LLM_PROVIDER", "openai"),
            llm_api_key=os.getenv("LANES_CEO_LLM_API_KEY", ""),
            llm_base_url=os.getenv("LANES_CEO_LLM_BASE_URL", ""),
            llm_model=os.getenv("LANES_CEO_LLM_MODEL", ""),
            deepseek_balance_threshold=float(
                os.getenv("LANES_CEO_DEEPSEEK_BALANCE_THRESHOLD", "10.0")
            ),
            deepseek_api_key=os.getenv("LANES_CEO_DEEPSEEK_API_KEY", ""),
            email_enabled=_bool_env("LANES_CEO_EMAIL_ENABLED"),
            email_address=os.getenv("LANES_CEO_EMAIL_ADDRESS", ""),
            email_password=os.getenv("LANES_CEO_EMAIL_PASSWORD", ""),
            email_imap_server=os.getenv("LANES_CEO_EMAIL_IMAP_SERVER", ""),
            email_smtp_server=os.getenv("LANES_CEO_EMAIL_SMTP_SERVER", ""),
            notification_default_channel=os.getenv(
                "LANES_CEO_NOTIFICATION_CHANNEL", "cli"
            ),
        )

    def ensure_dirs(self) -> None:
        for d in [self.db_path, self.artifact_dir, self.log_file]:
            Path(d).parent.mkdir(parents=True, exist_ok=True)


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv as _load
        _load(Path(__file__).parent.parent.parent / ".env")
    except Exception:
        pass


def _bool_env(key: str) -> bool:
    return os.getenv(key, "").strip().lower() in ("1", "true", "yes", "on")
