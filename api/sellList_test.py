# sellList_test.py
import os
os.environ['TESTING'] = 'True'

from routers.sellList import *
import requests
import unittest
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from dotenv import load_dotenv
from firebase_config import db
from pydantic import ValidationError

load_dotenv()

FIREBASE_ID = os.getenv('NEXT_PUBLIC_FIREBASE_PROJECT_ID')
FIRESTORE_EMULATORS_PORT = 'localhost:8080'

def clear_db():
    url = f"http://{FIRESTORE_EMULATORS_PORT}/emulator/v1/projects/{FIREBASE_ID}/databases/(default)/documents"
    response = requests.delete(url)
    if response.status_code != 200:
        print('Error clearing database', response.status_code)

class SellListTests(unittest.IsolatedAsyncioTestCase):
    async def setUp(self):
        """
        Setup method to initialize the database or clear it before each test.
        """
        clear_db()

    async def test_valid_listing_creation(self):
        """
        Test the successful creation of a listing.
        """
        listing = ListingInformation(
            title="Vintage Camera",
            description="A fully functional vintage camera.",
            price=120.0,
            image_url="",
            display_name="testuser",
            email="testemail@gmail.com",
            category="Electronics",
            availability_dates="",
            type="sale",
            user_id="testuserid",
            timestamp=datetime.now(timezone.utc)
        )
        response = await upload_listing(listing)
        self.assertEqual(response['message'], "Listing uploaded successfully")
        self.assertIsNotNone(response['listing_id'])

    async def test_valid_listing_creation_with_opt_info(self):
        """
        Test the successful creation of a listing with the minimum requirements.
        All optional fields will be left as optional
        """
        listing = ListingInformation(
            title="iPhone 10 (Used)",
            description="",
            price=120.0,
            image_url="",
            display_name="testuser",
            email="testemail@gmail.com",
            category="All",
            availability_dates="",
            type="sale",
            user_id="testuserid",
            timestamp=datetime.now(timezone.utc)
        )
        response = await upload_listing(listing)
        self.assertEqual(response['message'], "Listing uploaded successfully")
        self.assertIsNotNone(response['listing_id'])

    async def test_valid_rental_creation(self):
        """
        Test the successful creation of a rental listing.
        """
        listing = ListingInformation(
            title="iPhone 10 (Used)",
            description="",
            price=120.0,
            image_url="",
            display_name="testuser",
            email="testemail@gmail.com",
            category="All",
            availability_dates="7/8/2024 to 7/15/2024",
            type="rent",
            user_id="testuserid",
            timestamp=datetime.now(timezone.utc)
        )
        response = await upload_listing(listing)
        self.assertEqual(response['message'], "Listing uploaded successfully")
        self.assertIsNotNone(response['listing_id'])

    async def test_update_listing_non_existent_id(self):
        """
        Test updating a listing with an ID that does not exist.
        """
        update_data = ListingInformation(
            title="Updated Vintage Camera",
            price=150.0,
            category="Electronics",
            type="sale",
            user_id="user123",
            display_name="John Doe",
            email="johndoe@example.com"
        )
        with self.assertRaises(HTTPException) as context:
            await update_listing("nonexistentid", update_data)
        self.assertEqual(context.exception.status_code, 404)

    # async def test_upload_request_negative_price(self):
    #     """
    #     Test with negative price (invalid).
    #     """
    #     test_request = ListingInformation(
    #         title="Hungarian Candy",
    #         description="Study Abroad food!",
    #         price=-120.0,
    #         image_url="",
    #         display_name="testuser",
    #         email="testemail@gmail.com",
    #         category="All",
    #         availability_dates="",
    #         type="sale",
    #         user_id="testuserid",
    #         timestamp=datetime.now(timezone.utc)
    #     )
    #     with self.assertRaises(ValueError) as context:
    #         await upload_listing(test_request)
    #     self.assertEqual("Price must be non-negative", str(context.exception))

if __name__ == '__main__':
    unittest.main()
