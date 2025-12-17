import httpx
from src.config import settings


class HttpClient:

    _instance = None
    _client: httpx.AsyncClient | None = None

    def __new__(cls: type["HttpClient"]) -> "HttpClient":
        if cls._instance is None:
            cls._instance = super(HttpClient, cls).__new__(cls)  # noqa
        return cls._instance

    def init(self) -> None:
        auth = httpx.BasicAuth(
            username=settings.prefect.basic_auth_username,
            password=settings.prefect.basic_auth_password,
        )
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10, auth=auth)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()

    def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client is not initialized")
        return self._client


http_client = HttpClient()
