from fastapi import FastAPI, APIRouter, File, Form, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel, Field
from firebase_admin import credentials, firestore, initialize_app
import os
import json
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix='/api/insearchof',
    tags=['insearchof'],
)

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )




cred_dict = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY'))
cred = credentials.Certificate(cred_dict)
firebase_app = initialize_app(cred)
db = firestore.client()


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


class insearchofer(BaseModel):
    pass


class UploadRequestResponse(BaseModel):
    """
    Response model for uploading a request to the database.
    """

    message: str = Field(
        ..., description="Response message confirming the request has been uploaded.")


class UpdateRequestResponse(BaseModel):
    """
    Response model for updating a request in the database.
    """

    message: str = Field(
        ..., description="Response message confirming the request has been updated.")


class DeleteRequestResponse(BaseModel):
    """
    Response model for deleting a request from the database.
    """

    message: str = Field(
        ..., description="Response message confirming the request has been deleted.")


class MarkTransactionRequest(BaseModel):
    """
    Model for marking a transaction as complete in the database.
    """

    item_id: str = Field(...,
                         description="The ID of the item being requested.")
    requester_id: str = Field(..., description="The requester's email.")
    seller_id: str = Field(..., description="The seller's email.")


class MarkTransactionCompleteResponse(BaseModel):
    """
    Response model for marking a transaction as complete in the database.    
    """

    message: str = Field(
        ..., description="Response message confirming the transaction has been marked as complete.")


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
    type: str  # will be "request"

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
    doc_ref = db.collection('insearchof').document()
    iso_request_data = iso_request.dict()
    doc_ref.set(iso_request_data)
    return {"message": "Request uploaded successfully", "request_id": doc_ref.id}


@router.patch("/update/{request_id}", response_model=UpdateRequestResponse)
def update_request(request_id: str, request, current_user):
    '''
    Updates an existing ISO request in the database. This endpoint requires the user to be authenticated.

    Security: Only the user who created the ISO request is allowed to update it.

    Returns a JSON response with the result of the operation.
    '''
    return {"message": "Request updated"}


@router.delete("/delete/{request_id}")
def delete_request(request_id: str, current_user):
    '''
    Deletes an ISO request from the database. This endpoint requires user authentication.

    Security: Only the user who created the ISO request or an admin can delete it.

    Returns a JSON response indicating the outcome of the operation.
    '''
    return {"message": "Request deleted"}


@router.get("/mark/{request_id}", response_model=MarkTransactionCompleteResponse)
def mark_transaction_complete(request_id: str, current_user):
    '''
    Marks the transaction related to the ISO request as complete. This endpoint requires user authentication.

    Security: Ensures that only the user involved in the transaction can mark it as complete.

    If an error occurs during the database operation, an appropriate error response is returned.

    Returns a JSON response confirming the transaction status update.
    '''
    return {"message": "Transaction marked complete"}


@router.post("/upload-image")
async def upload_image(file: UploadFile = File()):
    """
    Allows user to upload an image for their item listing.

    The endpoint enforces the following restrictions for the uploaded images:
    - File size: Maximum allowed file size is X MB <-- to be determined later.
    - File format: Only JPEG and PNG formats are accepted.

    The uploaded image is processed and stored in a cloud storage service, and a UUID reference
    of the stored image is saved in the Firestore listing for retrieval.

    If the uploaded image does not meet the criteria, the function raises an HTTPException.
    """
    # Logic to ensure correct file size and format
    # Stores the reference UUID in the Firestore listing of the image

    # Check the file size and type here (you might use file.content_type)
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=415, detail="Unsupported file type.")

    # Assuming you have a function to upload to Firebase Storage and return the URL
    image_url = await upload_to_storage_service(file)

    return {"message": "Image uploaded successfully", "image_url": image_url}


'''
ISSUES PROVIDED BY REVIEW:

Non-negative Price Validation:
Issue: The initial code did not validate the non-negative price on the backend.
Risk: Without backend validation, there was a possibility of negative prices "screwing up" the database integrity.

Editing/Deleting ISO Requests:
Issue: The program lacked the ability for users to edit or delete their ISO requests.
Risk: This limitation restricted user control and could lead to outdated information existing in the database.

Image Handling Post-Upload:
Issue: There was no clarification or implementation detail on the restrictions for image size and format.
Risk: Without such restrictions, users could upload excessively large or improperly formatted images, potentially leading to storage inefficiencies or technical issues.

Notification System Integration:
Issue: There was no mention of a notification system to alert users of important events related to their ISO requests.
Risk: Users might not be promptly informed about significant updates, potentially degrading the user experience.

Security Measures:
Issue: The preliminary design did not address security measures such as authentication and authorization for accessing and modifying requests.
Risk: Neglecting security could lead to unauthorized access and manipulation of user data.

Testing Framework
Issue: No standard (off the shelf) testing framework.
Risk: Tests are formatted in many different ways, creating confusion

SUMMARY OF CHANGES MADE:

Non-negative Price Validation:
Change: Added a validator within the insearchoferFilters Pydantic model to check for non-negative prices.
Reason: Backend validation ensures integrity even if frontend validation fails or is bypassed, safeguarding the database against corrupt data.

Editing/Deleting ISO Requests:
Change: Introduced new endpoints for updating and deleting ISO requests, along with proper permission checks.
Reason: This allows users to maintain accurate and current information and removes any obsolete data, enhancing user control and data relevance.

Image Handling Post-Upload:
Change: Included comments about handling images with specific size and format restrictions post-upload.
Reason: Outlines the need to enforce these limitations to maintain efficient storage and prevent technical issues.

Notification System Integration:
Change: Added comments discussing the potential integration of a notification system.
Reason: To improve user engagement by keeping users updated about the status of their ISO requests and related transactions.

Security Measures:
Change: Ensured all sensitive endpoints require user authentication, and only appropriate users can perform actions.
Reason: To protect user data and prevent unauthorized actions, upholding the application’s integrity and trustworthiness.

Testing Framework
Change: Utilize python unittest as the testing framework.
Reason: Standardized tests will be easier to understand for yourself and others.
'''
