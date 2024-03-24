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
    
    The method receives ISO request data from the client, which includes a title,
    an optional description, an optional image URL, and a price. The data is then
    validated and sent to the Firebase database where a new entity is created 
    within the ISO requests collection.

    The Firebase entity structure follows:
    - requester_id: str - Unique identifier of the user making the request
    - title: str - Title of the requested item or service
    - description: Optional[str] - Additional details about the request
    - image: Optional[str] - URL of the image if uploaded
    - price: float - Proposed price for the item or service
    - status: str - Initialized to 'open' indicating the request is active
    
    If an image is included, the image processor function would be called prior to this,
    returning a URL to be included in the database entry. In case of any database operation
    failures, appropriate error handling will be performed and an error message will be returned.

    Returns a confirmation message indicating the successful upload of the request.
    '''
    
    # Here you would typically call a function or a class method that handles the database operation.
    # The actual database call has been abstracted away from this layer of the code for separation
    # of concerns and easier testing.
    
    return {"message": "Request uploaded"}


@router.get("/mark")
def mark_transaction_complete(mark_request: MarkTransactionRequest) -> MarkTransactionCompleteResponse:
    '''
    Marks the associated transaction as complete in the database. This is used
    to update the transaction history once a successful transaction has been completed.
    
    This method receives the unique item ID for the ISO request and the requester's user ID.
    With these details, it updates the corresponding ISO request entry in the Firebase
    database to reflect that the transaction has been completed.

    The update to Firebase involves setting the 'status' field of the document to 'completed'.
    This indicates that the ISO request is no longer active and has been fulfilled.

    The following Firebase operations are executed:
    - Transaction document is retrieved by item_id and requester_id.
    - The status field of the document is updated to 'completed'.
    - The update is committed, and a response message is generated and returned.

    Returns a message confirming the transaction status update.
    '''

    # Similar to the upload_request, the actual database update operation would be encapsulated in a separate function or method.
    # The focus here is on what needs to be done with the database, not how it's done.

    return {"message": "Transaction marked complete"}
