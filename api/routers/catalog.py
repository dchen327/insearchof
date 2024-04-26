import os
import firebase_admin
import json
from fastapi import APIRouter, Query, Depends
from typing import Annotated, Optional, List
from pydantic import BaseModel, Field
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv
from api.firebase_config import db
from datetime import datetime, timezone
from google.cloud.firestore_v1 import FieldFilter

load_dotenv()


router = APIRouter(
    prefix='/api/catalog',
    tags=['catalog'],
)

sort_options = {
    "uploadDateAsc": ("timestamp", "ASCENDING"),
    "uploadDateDesc": ("timestamp", "DESCENDING"),
    "priceAsc": ("price", "ASCENDING"),
    "priceDesc": ("price", "DESCENDING"),
}


class ListingsFilters(BaseModel):
    search: str = Field(
        default='', description="The search query: searches item names and descriptions.")
    sort: str = Field(
        default='uploadDateAsc', description="Options for sorting (ascending/descending): upload date, price")
    listing_types: Annotated[list[str], Query()] = Field(
        description="The types of listing to return (buy, rent, or request)")
    min_price: float = Field(
        0, description="Minimum price of returned items. Must be at most the maximum price, and be a non-negative float with max 2 decimal places. ")
    max_price: float = Field(
        0, description="Maximum price of returned items. Must at least the minimum price, and be a non-negative float with max 2 decimal places.")
    categories: List[str] = Field(
        ['None'], description="Categories to filter by (e.g. electronics, furniture, clothing)")
    user_name: Optional[str] = Field(None, description='User display name')
    email: Optional[str] = Field(None, description='User email')


class Listing(BaseModel):
    description: str
    image_url: str
    price: float
    timestamp: datetime
    time_since_listing: str
    title: str
    trans_comp: bool
    type: str
    user_id: str
    user_name: str
    email: str


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


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    periods = [
        ('y', 60*60*24*365),
        ('mo', 60*60*24*30),
        ('w', 60*60*24*7),
        ('d', 60*60*24),
        ('h', 60*60),
        ('m', 60),
        ('s', 1)
    ]

    for period_name, period_seconds in periods:
        if total_seconds >= period_seconds:
            period_value, total_seconds = divmod(total_seconds, period_seconds)
            return "%s%s" % (period_value, period_name)

    return "0s"


@router.get("/listings")
def get_listings(
    search: str = Query(
        default='', description="The search query: searches item names and descriptions."),
    sort: str = Query(default='uploadDateAsc',
                      description="Options for sorting (ascending/descending): upload date, price"),
    listing_types: List[str] = Query(
        default=['buy', 'rent', 'request'], description="The types of listing to return (buy, rent, or request)"),
    min_price: float = Query(
        default=0, description="Minimum price of returned items. Must be at most the maximum price, and be a non-negative float with max 2 decimal places."),
    max_price: float = Query(
        default=0, description="Maximum price of returned items. Must at least the minimum price, and be a non-negative float with max 2 decimal places."),
    categories: List[str] = Query(default=[
                                  'None'], description="Categories to filter by (e.g. electronics, furniture, clothing)")

) -> ListingsResponse:
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

    # If there are errors in the input, generates a descriptive error message and fails the API call
    # This allows the frontend to display the error to the users
    # query from database items collection, filter and order correctly
    # print items in db.items collection
    for item in db.collection('items').stream():
        print(item.to_dict())

    if max_price == 0:
        max_price = float('inf')

    field, direction = sort_options[sort]

    # Create FieldFilter objects
    type_filter = FieldFilter(
        field_path='type', op_string='in', value=listing_types)

    min_price_filter = FieldFilter(
        field_path='price', op_string='>=', value=min_price)

    max_price_filter = FieldFilter(
        field_path='price', op_string='<=', value=max_price)

    # Use FieldFilter objects with where method
    query = db.collection('items').where(filter=type_filter).where(
        filter=min_price_filter).where(filter=max_price_filter)

    docs = query.order_by(field, direction=direction).stream()

    items = []
    for doc in docs:
        items.append(doc.to_dict())

    if search:
        items = [item for item in items if search.lower() in item['title'].lower(
        ) or search.lower() in item['description'].lower()]

    # convert timestamp to string (e.g. 5m, 1h, 1d, 1w, 1mo, 1y)
    now = datetime.now(timezone.utc)
    for item in items:
        # calculate difference from current time
        timestamp = item['timestamp']
        diff = now - timestamp
        item['time_since_listing'] = format_timedelta(diff)

    # print all
    # print(search, sort, listing_types, min_price, max_price, categories)
    # print(items)

    return {"listings": items}


@router.get("/purchase")
def purchase_item(purchase_request: PurchaseRequest) -> PurchaseResponse:
    ''' A buyer indicates to a seller that they'd want to purchase an item. Query profiles backend for seller\'s contact information and return for the frontend. '''
    # First validates inputs
    # Query the profiles backend to get the seller's contact information from the User collection
    # Use the seller's email to find their profile and any other contact information (e.g. phone number, Discord, Messenger)

    return {"seller_email": "email@email.com", "seller_phone": "123-456-7890", "seller_discord": "username#1234", "seller_messenger": "profile"}