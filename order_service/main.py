from fastapi import FastAPI, APIRouter
import requests

app = FastAPI()
router = APIRouter(prefix="/orders")

# Test data
orders = [
    {
        "id": 1,
        "buyerId": 1,
        "productId": 1,
        "status": "pending",
    },
    {
        "id": 6,
        "buyerId": 1,
        "productId": 2,
        "status": "pending",
    },
    {
        "id": 2,
        "buyerId": 2,
        "productId": 2,
        "status": "delivered",
    },
    {
        "id": 3,
        "buyerId": 3,
        "productId": 3,
        "status": "shipped",
    },
    {
        "id": 4,
        "buyerId": 4,
        "productId": 4,
        "status": "cancele",
    },
    {
        "id": 5,
        "buyerId": 5,
        "productId": 5,
        "status": "payed",
    },
]


@router.get("/users/{user_id}")
def get_all_user_orders(user_id: int):
    user_orders = [order for order in orders if order["buyerId"] == user_id]
    return user_orders if len(user_orders) != 0 else {"error": "OrdersNotFound"}


@router.get("/{id}")
def find_order_by_id(id: int):
    for order in orders:
        if order["id"] == id:
            return order
    return {"error": "OrderNotFound"}


@router.post("")
def create_order(order: dict):
    new_id = max([o["id"] for o in orders], default=0) + 1

    new_order = {
        "id": new_id,
        "buyerId": order.get("buyerId"),
        "productId": order.get("productId"),
        "status": "pending",
    }

    orders.append(new_order)

    return new_order


@router.put("/{id}/{status}")
def update_order_status(id: int, status: str):
    for order in orders:
        if order["id"] == id:
            order["status"] = status
            return order
    return {"error": "OrderNotFound"}


@router.delete("/{id}")
def cancel_order(id: int):
    for i, order in enumerate(orders):
        if order["id"] == id:
            return orders.pop(i)
    return {"error": "OrderNotFound"}


app.include_router(router)
