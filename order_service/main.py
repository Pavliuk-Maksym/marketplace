from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter(prefix="/order")


@router.get("/user/{user_id}")
def getAllUserOrders(user_id: int):
    pass


@router.get("/{id}")
def findOrderById(id: int):
    pass


@router.post("/")
def createOrder(order: dict):
    pass


@router.put("/{id}/status")
def updateOrderStatus(id: int, status: str):
    pass


@router.delete("/{id}")
def cancelOrder(id: int):
    pass


app.include_router(router)
