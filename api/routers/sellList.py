# sellList.py
import os
from firebase_admin import firestore, storage
from api.firebase_config import db
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
from datetime import datetime, timezone
from dotenv import load_dotenv
from uuid import uuid4
import io
from PIL import Image
from pydantic import ValidationError


load_dotenv()

router = APIRouter(
    prefix='/api/sell-list',
    tags=['sell-list'],
)

class ListingInformation(BaseModel):
    """
    The SellList class allows users to list items or services for sale or rent 
    on the application. It provides the functionality to input details about the item 
    or service, including categorization, pricing, and availability for rentable items.

    Attributes:
        title (str): The title of the item or service being sold or rented.
        description (str, optional): A detailed description of the item or service.
        category (str): The category under which the item or service falls.
        price (float): The asking price for the item or service. Must be non-negative.
        image (str, optional): An image represented by its unique id.
        availability_dates (str, optional): Start and end dates for the availability of a rentable item.
    """
    title: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    display_name: str
    email: str
    category: str
    availability_dates: Optional[str] = None
    type: str  # "sale" or "rent"
    user_id: str
    trans_comp: bool = False  # Transaction complete status

    @validator('price')
    def validate_price(cls, value):
        if value < 0:
            raise ValueError("Price must be non-negative")
        return value

@router.post("/upload", response_model=dict)
async def upload_listing(listing: ListingInformation):
    """
    Uploads a new listing to the database.
    """
    try:
        doc_ref = db.collection('items').document()
        listing_data = listing.model_dump()
        listing_data["timestamp"] = datetime.now(timezone.utc)
        doc_ref.set(listing_data)
        return {"message": "Listing uploaded successfully", "listing_id": doc_ref.id}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.put("/update/{listing_id}", response_model=dict)
async def update_listing(listing_id: str, update_data: ListingInformation):
    """
    Updates an existing listing in the database.
    """
    item_ref = db.collection('items').document(listing_id)
    item = item_ref.get()
    if item.exists:
        item_data = item.to_dict()
        if item_data['user_id'] != update_data.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized to update this listing.")
        item_data.update(update_data.dict(exclude_unset=True))
        item_ref.set(item_data)
        return {"message": "Listing updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Listing not found")

@router.delete("/delete/{listing_id}", response_model=dict)
async def delete_listing(listing_id: str, user_id: str):
    """
    Deletes a listing from the database.
    """
    item_ref = db.collection('items').document(listing_id)
    item = item_ref.get()
    if item.exists:
        item_data = item.to_dict()
        # if item_data['user_id'] != user_id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to delete this listing.")
        item_ref.delete()
        return {"message": "Listing deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

# Utility function to sanitize strings (e.g., filenames, user IDs)
def sanitize(input_string):
    """
    Sanitizes input string by removing newline characters and other disallowed characters.
    This enables our images to post successfully on Firebase.
    """
    # Remove any newline characters or other unwanted characters
    sanitized_string = input_string.replace('\n', '').replace('\r', '')
    return sanitized_string

@router.post("/upload-image/{user_id}", response_model=dict)
async def upload_image(user_id: str, file: UploadFile = File(...)):
    """
    Handles image uploads for listings, with added error handling.
    """
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        max_size = 1080
        if image.height > max_size or image.width > max_size:
            scale_ratio = min(max_size / image.height, max_size / image.width)
            new_size = (int(image.width * scale_ratio), int(image.height * scale_ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        img_byte_arr = io.BytesIO()
        quality = 90
        while True:
            image.save(img_byte_arr, format='JPEG', quality=quality)
            if img_byte_arr.tell() <= 1_000_000 or quality <= 10:
                break
            quality -= 10
            img_byte_arr.seek(0)

        img_byte_arr.seek(0)

        # Sanitize the user_id and filename
        sanitized_user_id = sanitize(user_id)
        sanitized_filename = sanitize(file.filename)

        # Configure Firebase Storage
        bucket = storage.bucket()
        unique_filename = f"{uuid4()}_{sanitized_filename}"
        file_name = f"images/{sanitized_user_id}/{unique_filename}"
        blob = bucket.blob(file_name)
        blob.upload_from_string(img_byte_arr.getvalue(), content_type='image/jpeg')
        blob.make_public()

        return {"message": "Image uploaded successfully", "image_url": blob.public_url}
    
    except Exception as e:
        print(f"Failed to upload image: {str(e)}")  # This will log the error
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
@router.delete("/delete-image/{filename}/{user_id}", response_model=dict)
async def delete_image(filename: str, user_id: str):
    """
    Deletes an image from Firebase Storage.
    """
    bucket = storage.bucket()
    blob = bucket.blob(f"images/{user_id}/{filename}")
    blob.delete()
    return {"message": "Image deleted successfully"}

@router.get("/listing-details/{listing_id}", response_model=dict)
async def get_listing_details(listing_id: str):
    """
    Retrieves the details of a specific listing by its ID.
    """
    listing_ref = db.collection('items').document(listing_id)
    listing_doc = listing_ref.get()
    if listing_doc.exists:
        listing_data = listing_doc.to_dict()
        return {"message": "Listing details fetched successfully", "listingDetails": listing_data}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

@router.get("/user-listings/{user_id}", response_model=List[dict])
async def get_user_listings(user_id: str):
    """
    Retrieves all listings associated with a specific user.
    """
    query = db.collection('items').where('user_id', '==', user_id).stream()
    listings = [{"title": doc.to_dict().get("title", ""), "listing_id": doc.id} for doc in query]
    return listings
