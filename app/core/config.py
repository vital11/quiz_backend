from typing import Any, Annotated, Literal
from pathlib import Path

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, AnyUrl, BeforeValidator, BaseModel, EmailStr

BASE_DIR = Path(__file__).parent.parent.parent


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_ignore_empty=True,
        extra="ignore",
    )


class Run(Config):
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000


class ApiV1Prefix(BaseModel):
    PREFIX: str = "/v1"
    USERS: str = "/users"
    LOGIN: str = "/login"


class ApiPrefix(BaseModel):
    PREFIX: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @computed_field
    @property
    def BEARER_TOKEN_URL(self) -> str:
        return str(self.PREFIX + self.v1.PREFIX + self.v1.LOGIN + "/access-token")


class Logger(BaseModel):
    PATH: Path = BASE_DIR / "app" / "core" / "log.json"
    FORMAT: str = "{time} {level} {message}"
    LEVEL: Literal["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    ROTATION: str = "1 MB"
    COMPRESSION: str = "zip"
    SERIALIZE: bool = True

    @computed_field
    @property
    def RECORD_DICT(self) -> dict:
        return dict(
            sink=self.PATH,
            format=self.FORMAT,
            level=self.LEVEL,
            rotation=self.ROTATION,
            compression=self.COMPRESSION,
            serialize=self.SERIALIZE,
        )


class Database(Config):
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    ECHO: bool = True
    ECHO_POOL: bool = False
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10

    NAMING_CONVENTION: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AuthJWT(Config):
    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-public.pem"
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class Auth0JWT(Config):
    DOMAIN: str = ""
    API_AUDIENCE: str = ""
    ALGORITHMS: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ISSUER(self) -> str:
        return str("https://" + self.DOMAIN + "/")


class CrossOrigin(Config):
    FRONTEND_HOST: str = ""

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]


class Settings(Config):
    APP_NAME: str = "Quiz AI"

    run: Run = Run()
    api: ApiPrefix = ApiPrefix()
    log: Logger = Logger()
    db: Database = Database()
    jwt: AuthJWT = AuthJWT()
    auth0: Auth0JWT = Auth0JWT()
    cors: CrossOrigin = CrossOrigin()


settings = Settings()
