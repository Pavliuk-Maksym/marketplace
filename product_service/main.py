from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- 1. Опис структури даних (Pydantic Models) ---

# Базова модель (те, що ми відправляємо при створенні)
class ProductBase(BaseModel):
    ownerId: int          # ID користувача (власника)
    title: str            # Назва товару
    description: str      # Опис
    price: float          # Ціна (number)
    category: str         # Категорія (string у вашому описі Product)
    status: str           # Наприклад: "available", "sold", "hidden"
    quantity: int         # Кількість (number -> int)
    imageUrl: str         # Посилання на фото

# Повна модель (те, що віддає база даних - з ID)
class Product(ProductBase):
    id: int

# --- 2. Імітація Бази Даних ---
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
        imageUrl="http://img.com/scarf.jpg"
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
        imageUrl="http://img.com/cup.jpg"
    )
]

# --- 3. API Endpoints ---

# Отримати всі товари або товари конкретного юзера (ownerId)
@app.get("/products", response_model=List[Product])
def get_products(ownerId: Optional[int] = None):
    if ownerId:
        return [p for p in fake_products_db if p.ownerId == ownerId]
    return fake_products_db

# Знайти товар за ID
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for product in fake_products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# Створити новий товар
@app.post("/products", response_model=Product)
def create_product(product: ProductBase):
    new_id = len(fake_products_db) + 1 if fake_products_db else 1
    # Створюємо новий об'єкт Product, додаючи ID до отриманих даних
    new_product = Product(id=new_id, **product.dict())
    fake_products_db.append(new_product)
    return new_product

# Оновити товар
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_data: ProductBase):
    for index, product in enumerate(fake_products_db):
        if product.id == product_id:
            updated_product = Product(id=product_id, **updated_data.dict())
            fake_products_db[index] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")

# Видалити товар
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for index, product in enumerate(fake_products_db):
        if product.id == product_id:
            del fake_products_db[index]
            return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")


# --- Запуск сервера (щоб можна було запускати кнопкою Play у PyCharm) ---
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)