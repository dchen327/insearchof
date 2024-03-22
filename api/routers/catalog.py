from fastapi import APIRouter
from typing import Optional, List
from pydantic import BaseModel, Field


router = APIRouter(
    prefix='/catalog',
    tags=['catalog'],
)


class ListingsFilters(BaseModel):
    search: Optional[str] = Field(None, description="The search query")
    type_: Optional[str] = Field(
        None, description="The type of listing (buy, rent, or request)")
    min_price: Optional[float] = Field(
        None, description="Minimum price of returned items")
    max_price: Optional[float] = Field(
        None, description="Maximum price of returned items")
    categories: Optional[List[str]] = Field(
        None, description="Categories to filter by")


@router.get("/listings")
def get_listings(filters: ListingsFilters):
    ''' Get item listings based on search parameters '''
    return {"listings": []}


@router.get("/purchase")
def purchase_item():
    ''' A buyer indicates to a seller that they'd want to purchase an item'''
    return {"message": "Seller notified"}


def get_image(img_id):
    ''' Retrive image from Cloud Storage based on ID '''
    return {"image": "image"}
