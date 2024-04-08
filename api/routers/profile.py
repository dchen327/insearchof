from fastapi import APIRouter
from typing import Optional, List 
from pydantic import BaseModel, Field, constr

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
        profile_picture (str, optional): An image of a profile picture representing the user.
        location (str): The user's location on campus specifically.
        phone_number (regex, optional): The user's phone number (not necessary; can be optional).

    Methods:
        upload_contact_info(): Uploads the users contact information to the database.
        get_list_of_items(): Provides a list of items associated with a given user.
        get_transaction_history(): Provides users with a list of recent transaction history including
        buys, sells, and ISOs.
    """

    email: str = Field(None, description="The user's email.")
    name: str = Field(None, description="The user's name.")
    profile_picture: Optional[str] = Field(None, description="An image of the profile picture representing the user.")
    location: str = Field(None, description="The user's location on campus specifically")
    phone_number: Optional[constr(regex=r'^\(\d{3}\)\s\d{3}-\d{4}$')] = Field(None, description="The user's phone number")
    

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

        requester_id: str = Field(..., description="The requester's email.")


    class GetListOfItemsResponse(BaseModel):
        """
        Response model for getting a list of items from the database.    
        """

        listingOfItems: List[dict] = Field(
            ..., description="List of items associated with the user.")


    class GetTransactionHistoryRequest(BaseModel):
        pass

    class GetTransactionHistoryResponse(BaseModel):
        """
        Response model for getting a user's transaction history in the database.    
        """

        listingOfTransactionHistory: List[dict] = Field(
            ..., description="User's transaction history.")


    @router.put("/upload_contact_info")
    def upload_contact_info(user_profile: UserProfile) -> UploadContactInfoResponse:
        """
        Uploads a users contact information, including their name, email, profile picture, optional
        phone number, to the user database, making it visible to buyers.
        """
        return {"message": "Uploads users contact info successfully"}


    @router.get("/get_list_of_items")
    def get_list_of_items(get_list: GetListOfItemsRequest) -> GetListOfItemsResponse:
        """
        Retrieves a list of items associated with a given user from the itemsForSale and itemsForRent 
        database and stores it within the user database, making it visible to buyers. 
        This allows potential buyers to view items listed by the user.

        """
        return {"listingOfItems": []}

    @router.get("/get_transaction_history")
    def get_transaction_history(get_transactions: GetTransactionHistoryRequest) -> GetTransactionHistoryResponse:
        """
        Retrieves a list of the user's transaction history and stores it within the user database. This includes 
        recent transactions such as buys, sells, and ISOs. Users can use this method to review their own 
        transaction history and other users' transaction history.
        
        """
        return {"listingOfTransactionHistory": []}