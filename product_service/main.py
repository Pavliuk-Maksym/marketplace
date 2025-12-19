from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import httpx

app = FastAPI()


class ProductBase(BaseModel):
    ownerId: int
    title: str
    description: str
    price: float
    category: str
    status: str
    quantity: int


class Product(ProductBase):
    id: int


fake_products_db: List[Product] = [
    Product(
        id=1,
        ownerId=1,
        title="В'язаний шарф",
        description="Теплий вовняний шарф ручної роботи",
        price=350.0,
        category="Одяг",
        status="active",
        quantity=5,
    ),
    Product(
        id=2,
        ownerId=2,
        title="Глиняна чашка",
        description="Керамічна чашка з розписом",
        price=150.0,
        category="Посуд",
        status="active",
        quantity=1,
    ),
]


@app.get("/products", response_model=List[Product])
def get_products(ownerId: Optional[int] = None):
    if ownerId:
        return [p for p in fake_products_db if p.ownerId == ownerId]
    return fake_products_db


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for product in fake_products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", response_model=Product)
def create_product(product: ProductBase):
    new_id = len(fake_products_db) + 1 if fake_products_db else 1
    new_product = Product(id=new_id, **product.dict())
    fake_products_db.append(new_product)
    return new_product


@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_data: ProductBase):
    for index, product in enumerate(fake_products_db):
        if product.id == product_id:
            updated_product = Product(id=product_id, **updated_data.dict())
            fake_products_db[index] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for index, product in enumerate(fake_products_db):
        if product.id == product_id:
            del fake_products_db[index]
            return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")


SERVICE_NAME = "products"
SERVICE_HOST = "localhost"
SERVICE_PORT = 8001
DISCOVERY_URL = "http://localhost:8000"


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


@app.get("/health")
def health():
    return {"status": "ok"}


async def call_service(
    service_name: str, path: str, method="GET", json=None, params=None
):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DISCOVERY_URL}/services/{service_name}")
        resp.raise_for_status()
        instances = resp.json()
        if not instances:
            raise Exception(f"No alive instances for service {service_name}")
        instance = instances[0]
        url = f"http://{instance['host']}:{instance['port']}/{service_name}/{path}"
        response = await client.request(method, url, json=json, params=params)
        response.raise_for_status()
        return response.json()
