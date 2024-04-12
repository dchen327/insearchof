###### ALL FIREBASE CODE TO BE UNCOMMENTED IN THE NEXT REVISION ######

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from pydantic import BaseModel, Field, validator
# from firebase_admin import firestore


router = APIRouter(
    prefix='/sell-list',
    tags=['sell-list'],
)

# # Initialize Firebase Admin SDK here
# db = firestore.client()

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
    price: float = Field(0.00, description="The price of the item or service. Must be non-negative.")
    image: Optional[str] = Field(None, description="An image based on ID")
    availability_dates: Optional[str] = Field(None, description="Start and end dates for rentable item availability.")

    @validator('price')
    def non_neg_price(cls, v):
        if v < 0:
            raise ValueError('Price must be non-negative')
        return v

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

    # In the future, we could add a file of constants for status codes to make it more readable.
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Negative prices are not allowed")
    
    # Including Firebase serverTimestamp for sorting by recent in the catalog/profile.
    # --- This code will be uncommented when we finalize our Firebase collections ---
    # item_dict = item.dict()
    # item_dict["created_at"] = firestore.SERVER_TIMESTAMP
    # db.collection('listings').add(item_dict)
    # return {"message": "Listing added successfully", "item": item.dict()}
    return {"message": "Listing added successfully", "item": item}

@router.patch("/update-listing/{listing_id}")
def update_listing(listing_id: str, item: SellList):
    """ Updates an existing listing with new information based on listing_id. """
    # Connect to Firestore and update the db with listing_id in the respective collection
    # Ensure to validate the listing_id exists and the user performing the update is the owner of the listing
    # We can use this to also allow for the re-listing of items. Here, we would create
    # an updated_at field that gets the current timestamp and update the listing using its id.

    # --- This code will be uncommented when we finalize our Firebase collections ---
    # listing_ref = db.collection('listings').document(listing_id)
    # if not listing_ref.get().exists:
    #     raise HTTPException(status_code=404, detail="Listing not found.")
    # listing_ref.update(item.dict())
    return {"message": "Listing updated successfully", "listing_id": listing_id, "item": item}

@router.post("/upload-image")
async def upload_image(file: UploadFile = File()):
    """ Allows user to upload an image for their item listing. """
    # Stores the reference UUID in the Firestore listing of the image
    return {"message": "Image uploaded successfully"}

@router.delete("/delete-listing/{listing_id}")
def delete_listing(listing_id: str):
    """
    Deletes a listing based on the provided listing ID.
    @Param: listing_id (str): The unique identifier for the listing to be deleted.
    @Return: A message indicating the outcome of the delete operation.
    """
    # Delete from firebase db; uncomment when fully implemented
    # doc_ref = db.collection('listings').document(listing_id)
    # doc_ref.delete()
    
    # For robustness, we will handle cases where the listing does not exist or the user does not have permission to delete it.
    return {"message": "Listing deleted successfully"}