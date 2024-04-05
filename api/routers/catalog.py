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
        0, description="Minimum price of returned items. Must be at most the maximum price, and be a non-negative float with max 2 decimal places. ")
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
    buyer_id: str = Field(...,
                          description="The buyer's email, must be validated.")
    seller_id: str = Field(...,
                           description="The seller's email, must be validated.")


class PurchaseResponse(BaseModel):
    seller_email: str = Field(
        ..., description="The seller's email address.")
    seller_phone: Optional[str] = Field(
        None, description="The seller's phone number.")
    seller_discord: Optional[str] = Field(
        None, description="The seller's Discord username.")
    seller_messenger: Optional[str] = Field(
        None, description="The seller's Facebook Messenger profile.")


@router.get("/listings")
def get_listings(filters: ListingsFilters) -> ListingsResponse:
    ''' Get item listings based on search parameters. '''
    # First check that input is valid, then query the database for items that match the search parameters
    # For the default blank search, we return all items and sort by most recent
    # Check that max_price >= min_price
    # Firebase docs: https://firebase.google.com/docs/firestore/query-data/queries#python
    # - sorting: if provided by the user, sort the items based on the specified criteria (indexes are already created for these types of queries)
    # - types: based on listing type (buy, rent, request), query the respective collections in the database (ItemsForSale, ItemsForRent, Requests)
    # - price: filter the items based on the price range (assume 0 and infinity as the default values for min and max prices)
    # - categories: filter the items based on the categories provided
    # If any of the searching/sorting/filtering can't be done in the query itself, can also run one more Python iteration below to filter/sort the results

    # Return: a list of objects that represent a listing, corresponds to the database schema
    # Has fields like Title, Description, Price, Image, Seller, etc.

    return {"listings": []}


@router.get("/purchase")
def purchase_item(purchase_request: PurchaseRequest) -> PurchaseResponse:
    ''' A buyer indicates to a seller that they'd want to purchase an item. Query profiles backend for seller\'s contact information and return for the frontend. '''
    # First validates inputs
    # Query the profiles backend to get the seller's contact information from the User collection
    # Use the seller's email to find their profile and any other contact information (e.g. phone number, Discord, Messenger)

    return {"seller_email": "email@email.com", "seller_phone": "123-456-7890", "seller_discord": "username#1234", "seller_messenger": "profile"}
