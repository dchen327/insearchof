from fastapi import APIRouter
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


router = APIRouter(
    prefix='/catalog',
    tags=['catalog'],
)


class ListingsFilters(BaseModel):
    search: str = Field(
        default='', description="The search query: searches item names and descriptions.")
    sort: str = Field(
        default='relevance', description="Options for sorting (ascending/descending): relevance, upload date, price")
    listing_types: List[str] = Field(
        ['buy', 'rent', 'request'], description="The types of listing to return (buy, rent, or request)")
    min_price: float = Field(
        0, description="Minimum price of returned items. Must be a non-negative float with max 2 decimal places.")
    max_price: float = Field(
        None, description="Maximum price of returned items. Must at least the minimum price, and be a non-negative float with max 2 decimal places.")
    categories: List[str] = Field(
        None, description="Categories to filter by (e.g. electronics, furniture, clothing)")


class Listing(BaseModel):
    pass


class ListingsResponse(BaseModel):
    listings: List[Listing] = Field(
        ..., description="The list of item listings based on search parameters")


class PurchaseRequest(BaseModel):
    item_id: str = Field(...,
                         description="The ID of the item being purchased.")
    buyer_id: str = Field(..., description="The buyer's email.")
    seller_id: str = Field(..., description="The seller's email.")


class PurchaseResponse(BaseModel):
    seller_email: str = Field(
        ..., description="The seller's email address.")


@router.get("/listings")
def get_listings(filters: ListingsFilters) -> ListingsResponse:
    ''' Get item listings based on search parameters. '''
    return {"listings": []}


@router.get("/purchase")
def purchase_item(purchase_request: PurchaseRequest) -> PurchaseResponse:
    ''' A buyer indicates to a seller that they'd want to purchase an item. Query profiles backend for seller\'s contact information and return for the frontend. '''
    return {"message": "Seller notified"}


def get_image(img_id):
    ''' Retrive image from Cloud Storage based on ID. '''
    return {"image": "image"}
