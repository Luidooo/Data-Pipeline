import asyncio
from typing import AsyncIterator
import httpx
from fastapi import HTTPException

from api.config import settings
from api import schemas


class ObrasGovClient:
    def __init__(self):
        self.base_url = settings.OBRASGOV_API_BASE_URL
        self.timeout = settings.OBRASGOV_API_TIMEOUT
        self.max_retries = settings.OBRASGOV_API_MAX_RETRIES
        self.backoff_factor = settings.OBRASGOV_RETRY_BACKOFF_FACTOR
        self.delay = settings.OBRASGOV_DELAY_BETWEEN_REQUESTS

    async def fetch_page(self, uf: str, page: int, page_size: int = 100) -> schemas.APIResponse:
        url = f"{self.base_url}/projeto-investimento"
        params = {
            "uf": uf,
            "pagina": page,
            "tamanhoDaPagina": page_size
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()

                    await asyncio.sleep(self.delay)

                    return schemas.APIResponse(**response.json())

                except httpx.HTTPStatusError as e:
                    if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                        wait_time = self.backoff_factor ** attempt
                        await asyncio.sleep(wait_time)
                        continue
                    raise HTTPException(
                        status_code=e.response.status_code,
                        detail=f"Erro ao buscar dados: {str(e)}"
                    )

                except httpx.TimeoutException:
                    if attempt < self.max_retries - 1:
                        continue
                    raise HTTPException(status_code=504, detail="Timeout ao buscar dados da API")

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    async def fetch_all(self, uf: str, page_size: int = 100) -> AsyncIterator[schemas.APIResponse]:
        page = 0
        while True:
            response = await self.fetch_page(uf, page, page_size)

            if not response.content:
                break

            yield response

            if response.last:
                break

            page += 1
