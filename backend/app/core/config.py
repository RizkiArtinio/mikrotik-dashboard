from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Database ---
    database_url: str = "postgresql+asyncpg://mikrotik_app:change_me@postgres:5432/mikrotik_dashboard"

    # --- Auth / Security ---
    jwt_secret_key: str = "insecure-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    fernet_key: str = ""

    # --- Seed super admin ---
    seed_admin_email: str = "admin@example.com"
    seed_admin_password: str = "change_me"

    # --- Default / seed router ---
    seed_default_router: bool = False
    default_router_name: str = "RB4011-Main"
    default_router_ip: str = "192.0.2.1"
    default_router_api_port: int = 8728
    default_router_username: str = "admin"
    default_router_password: str = "change_me"

    # --- SNMP (reserved) ---
    snmp_enabled: bool = False
    snmp_community: str = ""

    # --- Polling / Scheduler ---
    dashboard_poll_interval_seconds: int = 5
    traffic_snapshot_interval_minutes: int = 5
    backup_daily_hour: int = 2
    backup_daily_minute: int = 0
    alert_cooldown_minutes_default: int = 15
    cpu_alert_threshold: float = 90
    mem_alert_threshold: float = 90
    isp_ping_targets: str = "8.8.8.8,1.1.1.1"

    # --- Telegram ---
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # --- SMTP / Email ---
    email_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_address: str = ""
    smtp_use_tls: bool = True
    alert_email_recipients: str = ""

    # --- Backups ---
    backup_storage_dir: str = "/app/backups"

    # --- Domain / TLS ---
    domain: str = "dashboard.example.com"
    certbot_email: str = "admin@example.com"

    # --- CORS ---
    cors_allowed_origins: str = "http://localhost:5173"

    @property
    def isp_ping_target_list(self) -> list[str]:
        return [t.strip() for t in self.isp_ping_targets.split(",") if t.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def alert_email_recipient_list(self) -> list[str]:
        return [e.strip() for e in self.alert_email_recipients.split(",") if e.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
