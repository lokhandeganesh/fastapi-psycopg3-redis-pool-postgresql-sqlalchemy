from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database Parameters
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USERNAME: str

    # # JWT Settings
    # SECRET_KEY: str
    # ALGORITHM: str
    # ACCESS_TOKEN_EXPIRE_MINUTES: int
    # REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # PRE_AUTH_TOKEN_EXPIRE_MINUTES: int = 5  # Temporary token for 2FA step

    # # 2FA / TOTP Security
    # TOTP_ENCRYPTION_KEY: str  # Used to encrypt stored Base32 OTP secrets
    # PROJECT_NAME: str  # This will use in TOTP provisioning URI

    # Swagger / Docs security
    DOCSHIELD_ADMIN_PASS: str
    DOCSHIELD_DEVELOPER_PASS: str
    DOCSHIELD_VIEWER_PASS: str

    # # Docker Configuration
    # DEV_DOCKER_PORT: str
    # PROD_DOCKER_PORT: str

    model_config = SettingsConfigDict(
        env_file=".env",
        # Optional: Instead of adding fields,
        # you can tell Pydantic to ignore extras
        extra="ignore")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOSTNAME}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


settings = Settings()
