from fastapi import APIRouter
from apis.endpoint import  food

api_router = APIRouter()

api_router.include_router(food.router, prefix="/food", tags=["food"])