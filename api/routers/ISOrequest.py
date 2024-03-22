from fastapi import APIRouter
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


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
    

class ISOrequester(BaseModel):
    pass


class UploadRequestResponse(BaseModel):
    """
    Response model for uploading a request to the database.
    """

    message: str = Field(
        ..., description="Response message confirming the request has been uploaded.")
    

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


@router.get("/upload")
def upload_request(filters: ISOrequesterFilters) -> UploadRequestResponse:
    ''' 
    Uploads the request to the database, making it visible to other users 
    and recording the details for transaction history. 
    '''
    
    return {"message": "Request uploaded"}


@router.get("/mark")
def mark_transaction_complete(mark_request: MarkTransactionRequest) -> MarkTransactionCompleteResponse:
    '''
    Marks the associated transaction as complete in the database. This is used
    to update the transaction history once a successful transaction has been completed.
    '''
    
    return {"message": "Transaction marked complete"}
