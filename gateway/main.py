from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
import httpx
import itertools

app = FastAPI()
DISCOVERY_URL = "http://localhost:8000"
rr_counters = {}


def pick_instance(service: str, instances: list) -> dict:
    counter = rr_counters.setdefault(service, itertools.cycle(instances))
    return next(counter)


@app.api_route(
    "/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy(service: str, path: str, request: Request):
    async with httpx.AsyncClient(timeout=3.0) as client:
        resp = await client.get(f"{DISCOVERY_URL}/services/{service}")
    if resp.status_code != 200:
        raise HTTPException(503, "Service unavailable")
    instances = resp.json()
    instance = pick_instance(service, instances)

    # Правильная сборка URL
    target_url = f"http://{instance['host']}:{instance['port']}/{service}"
    if path:
        target_url += f"/{path}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            content=await request.body(),
            params=request.query_params,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response.headers,
    )
