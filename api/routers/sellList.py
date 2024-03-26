from fastapi import APIRouter, UploadFile, File
from typing import Optional
from pydantic import BaseModel, Field

router = APIRouter(
    prefix='/sell-list',
    tags=['sell-list'],
)

class SellList(BaseModel):
    """
    The SellList class allows users to list items or services for sale or rent 
    on the application. It provides the functionality to input details about the item 
    or service, including categorization, pricing, and availability for rentable items.

    Attributes:
        title (str): The title of the item or service being sold or rented.
        description (str, optional): A detailed description of the item or service.
        category (str): The category under which the item or service falls.
        price (float): The asking price for the item or service. Must be non-negative.
        image (str, optional): An image represented by its unique id. Image not explicitly passed through backend.
        availability_dates (str, optional): A tuple containing start and end dates for the availability of a rentable item.

    Methods:
        list_item(item): Uploads the item or service details to the database, making it available in the marketplace.
        update_listing(listing_id, item): Updates the status of an existing listing.
        upload_image(UploadFile)
    """
    title: str = Field(None, description="The title of the item or service being listed.")
    description: Optional[str] = Field(None, description="A detailed description of the item or service.")
    category: str = Field(None, description="The category of the item or service.")
    price: float = Field(0.0, description="The price of the item or service. Must be non-negative.")
    image: Optional[str] = Field(None, description="An image based on ID")
    availability_dates: Optional[str] = Field(None, description="Start and end dates for rentable item availability.")

@router.post("/list-item")
def list_item(item: SellList):
    """ 
    Allows users to list a new item for sale or rent. It receives the listing
    details as input, validates them, and then uploads the information to the Firebase database.
    Regarding the validation mechanism, we will check to make sure that the price is not negative.
    """
    # We can call a timestamp here, either using Timestamp from Firebase, or by creating
    # a datetime element (which we would also need to import). We would then add the listing
    # to our database (collection)
    return {"message": "Listing added successfully", "item": item}

@router.put("/update-listing/{listing_id}")
def update_listing(listing_id: str, item: SellList):
    """ Updates an existing listing with new information based on listing_id. """
    # Connect to Firestore and update the db with listing_id in the respective collection
    # Ensure to validate the listing_id exists and the user performing the update is the owner of the listing
    # We can use this to also allow for the re-listing of items. Here, we would create
    # an updated_at field that gets the current timestamp and update the listing using its id.
    return {"message": "Listing updated successfully", "listing_id": listing_id, "item": item}

@router.post("/upload-image")
async def upload_image(file: UploadFile = File()):
    """ Allows user to upload an image for their item listing. """
    # Stores the reference UUID in the Firestore listing of the image
    return {"message": "Image uploaded successfully"}