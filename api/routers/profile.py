from fastapi import FastAPI, APIRouter, File, Form, UploadFile, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel, Field
from firebase_admin import auth
<<<<<<< HEAD
from ..firebase_config import db
=======
from api.firebase_config import db
>>>>>>> 113ee4eb2eeac41b0e6866367de36b574e58e64e
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4

load_dotenv()

router = APIRouter(
    prefix='/api/profile',
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

    name: str = Field(None, description="The user's name.")
    profile_picture: Optional[str] = Field(
        None, description="An image of the profile picture representing the user.")
    location: str = Field(
        None, description="The user's location on campus specifically")
    # phone_number: Optional[constr(regex=r'^\(\d{3}\)\s\d{3}-\d{4}$')]  = Field(None, description="The user's phone number") # type: ignore

    class UploadContactInformation(BaseModel):
        user_uid: str
        location: str
        phone_number: str

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

        user_id: str = Field(..., description="The requester's uid.")

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

    @router.post("/upload_contact_info", response_model=dict)
    def upload_contact_info(user_profile: UploadContactInformation):
        """
        Uploads a users contact information, including their name, email, profile picture, optional
        phone number, to the user database, making it visible to buyers.
        """
        doc_ref = db.collection('users').document()
        user_profile_data = user_profile.dict()
        doc_ref.set(user_profile_data)
        return {"message": "Uploads users contact info successfully"}

        # user_query = db.collection('users').where('user_id', '==', requester_id)
    
        # # If user doesn't exist, show blanks
        # if not user_query.exists:
        #     return {"message": "User not found", "phone_number": "", "location": ""}
        
        # # Update user's contact information
        # user_data = user_query.to_dict()
        # user_data['phone_number'] = user_profile.phone_number
        # user_data['location'] = user_profile.location
        # user_query.set(user_data)
        
        # return {"message": "Uploaded user's contact info successfully"}


    @router.get("/get_list_of_items")
    def get_list_of_items(requester_id: str = Query(description="The requester's uid")) -> GetListOfItemsResponse:
        """
        Retrieves a list of items associated with a given user from the itemsForSale and itemsForRent 
        database and stores it within the user database, making it visible to buyers. 
        This allows potential buyers to view items listed by the user.

        """
        query = db.collection('items').where('user_id', '==', requester_id)
        items = []
        for doc in query.stream():
            items.append(doc.to_dict())

        return {"listingOfItems": items}


    @router.get("/get_transaction_history")
    def get_transaction_history(requester_id: str = Query(description="The requester's uid")) -> GetTransactionHistoryResponse:
        """
        Retrieves a list of the user's transaction history and stores it within the user database. This includes 
        recent transactions such as buys, sells, and ISOs. Users can use this method to review their own 
        transaction history and other users' transaction history.

        """

        query = db.collection('listings').where('user_id', '==', requester_id)
        listings = []
        for doc in query.stream():
            listings.append(doc.to_dict())

        return {"listingOfTransactionHistory": listings}
    

    # @router.delete("/delete/{item_id}", response_model=dict)
    # def delete_request(item_id: str, user_data: dict):
    
    #     try:
    #         item_ref = db.collection('items').document(item_id)
    #         item = item_ref.get()
    #         if item.exists:
    #             item_data = item.to_dict()
    #             # Check if the item's user_id matches the logged-in user's uid
    #             if item_data['user_id'] != user_data['user_id']:
    #                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                                     detail="You do not have permission to delete this item.")
                
    #             # Attempt to delete the image first, if it exists
    #             if item_data.get('image_url'):
    #                 image_filename = item_data['image_url'].split('/')[-1]  # Extracting filename from URL
    #                 # await delete_image(image_filename, user_data['user_id'])
                                
    #             # Proceed with the deletion of the database entry
    #             item_ref.delete()
    #             return {"message": "Item and associated image deleted successfully"}
    #         else:
    #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
