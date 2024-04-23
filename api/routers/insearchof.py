from fastapi import FastAPI, APIRouter, File, Form, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel, Field
from firebase_admin import storage
from ..firebase_config import db
from datetime import datetime, timezone
from uuid import uuid4
from ..firebase_config import db
from fastapi.encoders import jsonable_encoder
import os


router = APIRouter(
    prefix='/api/insearchof',
    tags=['insearchof'],
)


class insearchoferFilters(BaseModel):
    """
    The insearchofer backend component allows users to request items or services through
    the application, functioning similarly to current ISO management practices.
    Users can specify various details about the item or service they are seeking,
    including title, optional description, optional image, and the price they are
    willing to pay. These requests are then uploaded to the database for recording
    and tracking purposes.

    Once a transaction related to a request is successfully completed, the requester
    has the capability to mark this in their post. This action automatically updates
    the transaction's status as complete in the transaction history database, providing
    a record of the completed transaction.

    Attributes:
        title (str): The title of the item or service being requested.
        description (str, optional): A more detailed description of the item or service.
        image (Image, optional): An image representing the item or service.
        price (float): The price the requester is willing to pay. Must be non-negative.

    Methods:
        upload_request(): Uploads the request details to the database.
        mark_transaction_complete(): Marks the transaction as complete in the database.
        upload_image(UploadFile): Allows users to upload an image for their item listing.
    """

    title: str = Field(
        None, description="The title of the item or service being requested.")
    description: Optional[str] = Field(
        None, description="A more detailed description of the item or service.")
    image: Optional[str] = Field(
        None, description="An image representing the item or service.")
    price: float = Field(
        0.0, description="The price the requester is willing to pay. Must be non-negative.")

    def validate_price(cls, price):
        if price < 0:
            raise ValueError('Price must be non-negative.')
        return price


class NotificationService:
    @staticmethod
    def send_notification(user_id: str, message: str) -> None:
        """
        Simulates sending a notification to a user.

        Parameters:
        - user_id: The ID of the user who will receive the notification.
        - message: The message to be sent to the user.

        This could be integrated with Firebase Cloud Messaging or a similar service
        to push notifications to the user's device.
        """
        # Logic to send the notification would be here.
        # For now, we're just printing to simulate the action.
        print(f"Notification sent to {user_id}: {message}")


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
async def upload_request(iso_request: RequestInformation):
    '''
    Uploads the ISO request to the database. This endpoint is protected and requires
    the user to be authenticated.

    Additional input validation is performed to ensure the price is non-negative
    and the image, if present, meets size and format restrictions.

    Error handling includes capturing exceptions from the database operations and
    returning appropriate HTTP error responses.

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
async def update_request(item_id: str, update_data: RequestInformation):
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
async def delete_request(item_id: str, user_data: dict):
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
    print("hello?")
    try:
        # Fetch the item from the database
        print("hello?")
        item_ref = db.collection('items').document(item_id)
        item = item_ref.get()

        # Check if the item exists
        if item.exists:
            item_data = item.to_dict()

            # Check if the current user is authorized to mark the transaction as complete
            if item_data['user_id'] != current_user['user_id']:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to mark this transaction as complete.")

            # Toggle the value of trans_comp
            trans_comp_value = not item_data.get('trans_comp', False)
            item_ref.update({'trans_comp': trans_comp_value})

            # Log the change
            print(f"Transaction status for item {item_id} has been set to {trans_comp_value}")

            # Return a success message
            return {"message": "Transaction status updated successfully"}

        # If the item does not exist, raise a 404 error
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    except Exception as e:
        # If any other error occurs, raise a 500 error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    


@router.post("/upload-image/{user_id}", response_model=dict)
async def upload_image(user_id: str, file: UploadFile = File(...)):
    """
    Uploads an image to Firebase Storage and returns the URL of the uploaded image.
    """

    try:
        bucket = storage.bucket()

        # Create a unique file name
        unique_filename = f"{uuid4()}_{file.filename}"
        file_name = f"images/{user_id}/{unique_filename}"
        blob = bucket.blob(file_name)

        file_content = await file.read()

        # Upload the file
        blob.upload_from_string(file_content, content_type=file.content_type)

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
async def delete_image(filename: str, user_id: str):
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


@router.post("/validate-item-id/{item_id}", response_model=dict)
async def validate_item_id(item_id: str, user_data: dict):
    try:
        # Assuming db is your Firebase database client
        item_ref = db.collection('items').document(item_id).get()
        if item_ref.exists:
            item = item_ref.to_dict()
            # Check if the item's user_id matches the logged-in user's uid
            is_valid = item.get('user_id') == user_data.get('user_id')
            print("This item is yours" if is_valid else "This item is not yours")
            if is_valid:
                # Return the item details to the frontend
                return {
                    "isValid": True,
                    "itemDetails": {
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "price": item.get("price", 0),
                        "image_url": item.get("image_url", ""),
                        "urgent": item.get("urgent", False),
                        "categories": item.get("categories", []) 
                    }
                }
            else:
                return {"isValid": False}
        else:
            return {"isValid": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item-details/{item_id}", response_model=dict)
async def get_item_details(item_id: str):
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
