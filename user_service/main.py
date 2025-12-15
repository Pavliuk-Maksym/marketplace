from fastapi import FastAPI, APIRouter
from typing import List, Dict

app = FastAPI()
router = APIRouter(prefix="/user")

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
