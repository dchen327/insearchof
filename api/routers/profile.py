from fastapi import APIRouter
from typing import Optional, List
from pydantic import BaseModel, Field

router = APIRouter(
    prefix='/profile',
    tags=['profile'],
)

class UserProfile(BaseModel):
    """
    The UserProfile class allows users to manage their profile information, view transaction history,
    and interact with the platform. It also provides a user's location to pick up the item they want to buy. 

    Attributes:
        email (str): The user's email.
        name (str): The user's name.
        profile_picture (str, optional): A profile picture representing the user.
        location (str): The user's location on campus specifically.
        phone_number (str, optional): The user's phone number (not necessary; can be optional).

    Methods:
        upload_contact_info(): Uploads the users contact information to the database.
        get_list_of_items(): Provides a list of items associated with a given user.
        get_transaction_history(): Provides users with a list of recent transaction history including
        buys, sells, and ISOs.
    """

    email: str = Field(None, description="The user's email.")
    name: str = Field(None, description="The user's name.")
    profile_picture: Optional[str] = Field(None, description="A profile picture representing the user.")
    location: str = Field(None, description="The user's location on campus specifically")
    phone_number: Optional[str] = Field(None, description="The user's phone number")
    
    def __init__(self, email, name, profile_picture=None, location=None, phone_number=0):
        """
        Initializes a new User Profile instance with the given parameters.

        Parameters:
            email (str): The user's email.
            name (str): The user's name.
            profile_picture (Image, optional): A profile picture representing the user.
            location (str): The user's location on campus specifically).
            phone_number (int, optional): The user's phone number (not necessary; can be optional).
        """
    class ISOrequester(BaseModel):
        pass


    class UploadContactInfoResponse(BaseModel):
        """
        Response model for uploading one's contact info to the database.
        """

        message: str = Field(
            ..., description="Response message confirming the user's contact info has been uploaded.")


    class GetListOfItemsRequest(BaseModel):
        """
        Model for getting a list of items from the database.
        """

        user_id: str = Field(...,
                         description="The ID of the user whose list of items is being requested.")
        requester_id: str = Field(..., description="The requester's email.")
        # seller_id: str = Field(..., description="The seller's email.")


    class GetListOfItemsResponse(BaseModel):
        """
        Response model for getting a list of items from the database.    
        """

        message: str = Field(
            ..., description="Response message confirming the user's list of items has been requested.")

    class GetTransactionHistoryRequest(BaseModel):
        """
        Model for getting a user's transaction history from the database.
        """

        user_id: str = Field(...,
                         description="The ID of the user whose transaction history is being requested.")
        # requester_id: str = Field(..., description="The requester's email.")
        # seller_id: str = Field(..., description="The seller's email.")


    class GetTransactionHistoryResponse(BaseModel):
        """
        Response model for getting a user's transaction history in the database.    
        """

        message: str = Field(
            ..., description="Response message confirming the user's transaction history been requested.")


    @router.put("/upload_contact_info")
    def upload_contact_info() -> UploadContactInfoResponse:
        """
        Uploads a users contact information, including their name, email, profile picture, optional
        phone number, to the user database, making it visible to buyers.
        """
        return {"message": "Uploads users contact info successfully"}

    @router.get("/get_list_of_items/{user_id}")
    def get_list_of_items(get_list: GetListOfItemsRequest, user_id: str) -> GetListOfItemsResponse:
        """
        Retrieves a list of items associated with a given user from the itemsForSale and itemsForRent 
        database and stores it within the user database, making it visible to buyers. 
        This allows potential buyers to view items listed by the user.

        Parameters:
            user_id (str): The unique identifier of the user whose items are to be retrieved.
        
        Returns:
            list: A list of items associated with the specified user.
        """
        return {"message": "List of items shown successfully", "list": []}

    @router.get("/get_transaction_history/{user_id}")
    def get_transaction_history(get_transactions: GetTransactionHistoryRequest, user_id: str) -> GetTransactionHistoryResponse:
        """
        Retrieves a list of the user's transaction history and stores it within the user database. This includes 
        recent transactions such as buys, sells, and ISOs. Users can use this method to review their own 
        transaction history and other users' transaction history.
        
        Parameters:
        user_id (str): The unique identifier of the user whose transaction history is to be retrieved.
        
        Returns:
            list: A list of the user's transaction history, including buys, sells, and ISOs.
        """
        return {"message": "Transaction history shown successfully", "list": []}

# # This is a sample GET request. Add others based on your functions!
# @router.get("/api/profile")
# def get_profile():
#     '''  '''
#     return {"listings": []}