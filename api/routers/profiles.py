from fastapi import APIRouter
from typing import Optional, List
from pydantic import BaseModel, Field


router = APIRouter(
    prefix='/profile',
    tags=['profile'],
    
)


@router.get("/api/profile")
def get_profile():
    '''  '''
    return {"listings": []}
