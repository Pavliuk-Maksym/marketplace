from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio

app = FastAPI(title="Service Discovery")

# ====== CONFIG ======
HEARTBEAT_TIMEOUT = 15  # seconds
CLEANUP_INTERVAL = 5  # seconds

# ====== REGISTRY ======
# {
#   "users": [
#       {"host": "localhost", "port": 8001, "last_heartbeat": datetime}
#   ]
# }
registry: Dict[str, List[dict]] = {}


# ====== MODELS (internal) ======
def is_alive(service: dict) -> bool:
    return datetime.utcnow() - service["last_heartbeat"] < timedelta(
        seconds=HEARTBEAT_TIMEOUT
    )


# ====== API ======
@app.post("/register")
def register(name: str, host: str, port: int):
    services = registry.setdefault(name, [])

    # не регистрируем дубликаты
    for s in services:
        if s["host"] == host and s["port"] == port:
            s["last_heartbeat"] = datetime.utcnow()
            return {"status": "updated"}

    services.append({"host": host, "port": port, "last_heartbeat": datetime.utcnow()})

    return {"status": "registered"}


@app.post("/heartbeat/{name}")
def heartbeat(name: str, host: str, port: int):
    services = registry.get(name)
    if not services:
        raise HTTPException(404, "Service not found")

    for s in services:
        if s["host"] == host and s["port"] == port:
            s["last_heartbeat"] = datetime.utcnow()
            return {"status": "alive"}

    raise HTTPException(404, "Instance not found")


@app.get("/services/{name}")
def get_service(name: str):
    services = registry.get(name)
    if not services:
        raise HTTPException(404, "Service not found")

    alive = [s for s in services if is_alive(s)]
    if not alive:
        raise HTTPException(503, "No alive instances")

    return alive


@app.get("/services")
def list_services():
    return registry


# ====== BACKGROUND CLEANUP ======
async def cleanup_task():
    while True:
        for name in list(registry.keys()):
            registry[name] = [s for s in registry[name] if is_alive(s)]
            if not registry[name]:
                del registry[name]
        await asyncio.sleep(CLEANUP_INTERVAL)


@app.on_event("startup")
async def startup():
    asyncio.create_task(cleanup_task())
