from fastapi import FastAPI, APIRouter, File, Form, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel, Field
from firebase_admin import storage
from api.firebase_config import db
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
import os
from PIL import Image
import io


router = APIRouter(
    prefix='/api/insearchof',
    tags=['insearchof'],
)


class NotificationService:
    pass


class RequestInformation(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    user_id: str
    type: str  # will be "request"
    trans_comp: bool = False  # will be False
    urgent: bool
    categories: List[str]  # Add categories field

    def validate_price(cls, value):
        if value < 0:
            raise ValueError("Price must be non-negative")
        return value


@router.post("/upload", response_model=dict)
def upload_request(iso_request: RequestInformation):
    '''
    Uploads the ISO request to the database. 

    Security: This endpoint requires authentication. The current user's ID is used to
    link the ISO request to the user creating it.

    Returns a JSON response with the result of the operation.
    '''
    doc_ref = db.collection('items').document()
    iso_request_data = iso_request.dict()
    iso_request_data["timestamp"] = datetime.now(timezone.utc)
    doc_ref.set(iso_request_data)
    return {"message": "Request uploaded successfully", "request_id": doc_ref.id}


@router.put("/update/{item_id}", response_model=dict)
def update_request(item_id: str, update_data: RequestInformation):
    """
    Updates an existing ISO request in the database using the item ID.
    Parameters:
    - item_id: The unique ID of the item to update.
    - update_data: Data to update the item with.
    Returns a JSON response with the result of the operation.
    """
    try:
        item_ref = db.collection('items').document(item_id)
        item = item_ref.get()
        if item.exists:
            item_data = item.to_dict()

            if item_data['user_id'] != update_data.user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You do not have permission to update this item.")

            # Proceed with the update
            item_data.update(update_data.dict(exclude_unset=True))
            item_ref.set(item_data)
            return {"message": "Item updated successfully"}

        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{item_id}", response_model=dict)
def delete_request(item_id: str, user_data: dict):
    """
    Deletes an ISO request from the database. This endpoint requires user authentication.
    Security: Only the user who created the ISO request or an admin can delete it.
    Parameters:
    - item_id: The unique ID of the item to delete.
    - user_data: Authentication information of the current user, typically provided from a security dependency.
    Returns a JSON response indicating the outcome of the operation.
    """
    try:
        item_ref = db.collection('items').document(item_id)
        item = item_ref.get()
        if item.exists:
            item_data = item.to_dict()
            # Check if the item's user_id matches the logged-in user's uid
            if item_data['user_id'] != user_data['user_id']:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You do not have permission to delete this item.")
            
            # Attempt to delete the image first, if it exists
            if item_data.get('image_url'):
                image_filename = item_data['image_url'].split('/')[-1]  # Extracting filename from URL
                await delete_image(image_filename, user_data['user_id'])
                            
            # Proceed with the deletion of the database entry
            item_ref.delete()
            return {"message": "Item and associated image deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/mark/{item_id}", response_model=dict)
def mark_transaction_complete(item_id: str, current_user: dict):
    """
    Marks the transaction related to the ISO request as complete. This endpoint requires user authentication.
    Security: Ensures that only the user involved in the transaction can mark it as complete.
    If an error occurs during the database operation, an appropriate error response is returned.
    Returns a JSON response confirming the transaction status update.
    """
    try:
        # Fetch the item from the database
        item_ref = db.collection('items').document(item_id)
        item = item_ref.get()

        # Check if the item exists
        if item.exists:
            item_data = item.to_dict()

            # Check if the current user is authorized to mark the transaction as complete
            if item_data['user_id'] != current_user['user_id']:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to mark this transaction as complete.")

            trans_comp_value = not item_data.get('trans_comp', False)
            item_ref.update({'trans_comp': trans_comp_value})

            return {"trans_comp_value": trans_comp_value}

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/upload-image/{user_id}", response_model=dict)
def upload_image(user_id: str, file: UploadFile = File(...)):
    """
    Uploads an image to Firebase Storage after resizing and compressing it if necessary.
    """
    try:
        # Read the image data
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convert the image to RGB if not already
        # Prevents errors when converting to JPEG
        if image.mode != 'RGB':
            image = image.convert('RGB')
            print('converted to RGB')

        # Resize the image if it is larger than 1080px in height or width
        max_size = 1080
        if image.height > max_size or image.width > max_size:
            scale_ratio = min(max_size / image.height, max_size / image.width)
            new_size = (int(image.width * scale_ratio), int(image.height * scale_ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            print('scaled')

        # Compress the image to ensure the size is under 1MB with decent quality
        img_byte_arr = io.BytesIO()
        quality = 90
        while True:
            image.save(img_byte_arr, format='JPEG', quality=quality)
            if img_byte_arr.tell() <= 1_000_000 or quality <= 10:  # Stop if size is under 1MB or quality too low
                break
            quality -= 10
            img_byte_arr.seek(0) 
            print('compressed')

        img_byte_arr.seek(0)

        # Configure Firebase Storage
        bucket = storage.bucket()
        unique_filename = f"{uuid4()}_{file.filename}"
        file_name = f"images/{user_id}/{unique_filename}"
        blob = bucket.blob(file_name)

        # Upload the compressed image
        blob.upload_from_string(img_byte_arr.getvalue(), content_type='image/jpeg')

        # Make the blob publicly viewable
        blob.make_public()

        return {"image_url": blob.public_url}
    except Exception as e:
        print(f"Failed to upload image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to upload image", "error": str(e)}
        )
                

@router.delete("/delete-image/{filename}/{user_id}", response_model=dict)
def delete_image(filename: str, user_id: str):
    """
    Deletes an image from Firebase Storage.

    Parameters:
    - filename: The filename of the image to delete.

    Returns a JSON response indicating the outcome of the operation.
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(f"images/{user_id}/{filename}")

        # Delete the image from Firebase Storage
        blob.delete()

        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )

# In your FastAPI backend...


@router.post("/validate-item-id/{item_id}/{user_id}", response_model=dict)
def validate_item_id(item_id: str, user_id: str):
    try:
        item_details_response = await get_item_details(item_id)        
        item = item_details_response['itemDetails']
        print(item)

        is_valid = item['user_id'] == user_id
        print("This item is yours" if is_valid else "This item is not yours")
        
        if is_valid:
            return {
                "isValid": True,
                "itemDetails": item
            }
        else:
            return {"isValid": False}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item-details/{item_id}", response_model=dict)
def get_item_details(item_id: str):
    """
    Retrieves the details of a specific item by its ID.

    Parameters:
    - item_id: The unique identifier of the item.

    Returns:
    - A JSON response containing the item details or an error message.
    """
    try:
        # Fetch the document from Firestore
        item_ref = db.collection('items').document(item_id)
        item_doc = item_ref.get()

        if item_doc.exists:
            item_data = item_doc.to_dict()
            return {
                "message": "Item details fetched successfully",
                "itemDetails": item_data
            }
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    except Exception as e:
        print(f"Error fetching item details: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
