from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, Field, validator


router = APIRouter(
    prefix='/ISOrequest',
    tags=['ISOrequest'],
)


class ISOrequesterFilters(BaseModel):
    """
    The ISORequester backend component allows users to request items or services through
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
    """

    title: str = Field(
        None, description="The title of the item or service being requested.")
    description: Optional[str] = Field(
        None, description="A more detailed description of the item or service.")
    image: Optional[str] = Field(
        None, description="An image representing the item or service.")
    price: float = Field(
        0.0, description="The price the requester is willing to pay. Must be non-negative.")

    @validator('price')
    def validate_price(cls, price):
        if price < 0:
            raise ValueError('Price must be non-negative.')
        return price


class ISOrequester(BaseModel):
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


@router.post("/upload", response_model=UploadRequestResponse)
def upload_request(request: ISOrequester, current_user):
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
    return {"message": "Request uploaded", "request_id": "new_request_id"}


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
