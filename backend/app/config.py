from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VERITAS_", env_file=".env", extra="ignore")

    app_name: str = "Veritas Evidentiary Collection Engine"
    database_url: str = f"sqlite:///{DATA_DIR / 'veritas.db'}"
    # Content-addressed object store: files saved under store/<sha256[:2]>/<sha256>
    storage_dir: Path = DATA_DIR / "store"
    # OpenTimestamps detached signatures: one .ots file per evidence hash
    timestamp_dir: Path = DATA_DIR / "timestamps"
    # Comma-friendly CORS origins. Add your Vercel frontend URL via
    # VERITAS_CORS_ORIGINS env var (JSON array format).
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    max_upload_mb: int = 512
    # External timestamp anchoring (OpenTimestamps)
    timestamp_enabled: bool = True
    timestamp_calendars: list[str] = [
        "https://alice.btc.calendar.opentimestamps.org",
        "https://bob.btc.calendar.opentimestamps.org",
        "https://finney.calendar.eternitywall.com",
    ]
    timestamp_bitcoin_url: str = "https://blockstream.info/api"
    # RFC 3161 timestamp authority (FreeTSA by default)
    rfc3161_enabled: bool = True
    rfc3161_tsa_url: str = "https://freetsa.org/tsr"
    rfc3161_tsa_cert_url: str = "https://freetsa.org/files/tsa.crt"
    # URL collector
    collect_timeout_seconds: float = 30.0
    collect_max_redirects: int = 5
    # Allow fetching private/loopback addresses (SSRF guard off). Keep False
    # in any networked/public deployment.
    allow_private_collect: bool = False
    # Batch/crawl collection limits
    collect_batch_limit: int = 50
    default_collector: str | None = None


settings = Settings()

DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.storage_dir.mkdir(parents=True, exist_ok=True)
settings.timestamp_dir.mkdir(parents=True, exist_ok=True)
