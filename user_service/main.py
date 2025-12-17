from fastapi import FastAPI, APIRouter
import asyncio
import httpx
from typing import List, Dict

app = FastAPI()
router = APIRouter(prefix="/users")

# ====== BUSINESS LOGIC (оставлено без изменений) ======
users: List[Dict] = [
    {
        "id": 1,
        "username": "alice",
        "password": "12345",
        "email": "alice@example.com",
        "fullName": "Alice A.",
    },
    {
        "id": 2,
        "username": "bob",
        "password": "12345",
        "email": "bob@example.com",
        "fullName": "Bob B.",
    },
]


@router.get("")
def list_users():
    return users


@router.get("/{id}")
def find_user_by_id(id: int):
    for u in users:
        if u["id"] == id:
            return u
    return {"error": "UserNotFound"}


@router.post("")
def create_user(user: dict):
    new_id = (max([u["id"] for u in users]) + 1) if users else 1
    user["id"] = new_id
    users.append(user)
    return user


@router.put("/{id}")
def update_user(id: int, user_update: dict):
    for u in users:
        if u["id"] == id:
            u.update(user_update)
            u["id"] = id
            return u
    return {"error": "UserNotFound"}


@router.delete("/{id}")
def delete_user(id: int):
    for i, u in enumerate(users):
        if u["id"] == id:
            return users.pop(i)
    return {"error": "UserNotFound"}


app.include_router(router)

# ====== DISCOVERY CONFIG ======
SERVICE_NAME = "users"
SERVICE_HOST = "localhost"
SERVICE_PORT = 8003
DISCOVERY_URL = "http://localhost:8000"


# ====== REGISTRATION И HEARTBEAT ======
async def register():
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{DISCOVERY_URL}/register",
            params={"name": SERVICE_NAME, "host": SERVICE_HOST, "port": SERVICE_PORT},
        )


async def heartbeat():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{DISCOVERY_URL}/heartbeat/{SERVICE_NAME}",
                    params={"host": SERVICE_HOST, "port": SERVICE_PORT},
                )
        except Exception:
            pass
        await asyncio.sleep(5)


@app.on_event("startup")
async def startup():
    await register()
    asyncio.create_task(heartbeat())


# ====== HEALTHCHECK ======
@app.get("/health")
def health():
    return {"status": "ok"}


# ====== HELPER ДЛЯ ВЫЗОВА ДРУГИХ СЕРВИСОВ ПО ЛОГИЧЕСКОМУ ИМЕНИ ======
async def call_service(
    service_name: str, path: str, method="GET", json=None, params=None
):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DISCOVERY_URL}/services/{service_name}")
        resp.raise_for_status()
        instances = resp.json()
        if not instances:
            raise Exception(f"No alive instances for service {service_name}")
        instance = instances[0]  # round-robin можно улучшить
        url = f"http://{instance['host']}:{instance['port']}/{service_name}/{path}"
        response = await client.request(method, url, json=json, params=params)
        response.raise_for_status()
        return response.json()
