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
    """
    The SellListTests class contains integration tests designed to validate the functionality
    of the Selling/Listing system within our application. The tests ensure that the endpoints 
    responsible for handling the creation, updating, deletion, and querying of listings perform 
    correctly, as defined in sellList.py. 

    The focus of these tests is to verify that the system handles:
    - The creation of new listings with complete and partial data.
    - The updating of existing listings both validly and invalidly (e.g., with unauthorized access or nonexistent IDs).
    - The deletion of listings, ensuring that only valid, existing listings can be deleted and proper errors are returned otherwise.
    - Error handling to ensure the system robustly manages incorrect inputs and system failures.
    """
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
            type="buy",
            user_id="testuserid",
            timestamp=datetime.now(timezone.utc)
        )
        response = await upload_listing(listing)
        self.assertEqual(response['message'], "Listing uploaded successfully")
        self.assertIsNotNone(response['listing_id'])

    async def test_upload_listing(self):
        # valid listing upload
        listing_data = {
            "title": "Gaming Console",
            "description": "Brand new gaming console for sale.",
            "price": 299.99,
            "display_name": "Henry Gamer",
            "email": "henry@gamer.com",
            "category": "Electronics",
            "type": "sale",
            "user_id": "user123"
        }
        response = requests.post('http://localhost:8000/api/sell-list/upload', json=listing_data)
        self.assertEqual(response.status_code, 200)  # Updated to expect 200 instead of 201
        self.assertEqual(response.json()['message'], "Listing uploaded successfully")

        # missing required fields
        incomplete_listing_data = {
            "title": "Gaming Console",
            "price": 299.99,
            "user_id": "user123"
        }
        response = requests.post('http://localhost:8000/api/sell-list/upload', json=incomplete_listing_data)
        self.assertEqual(response.status_code, 422) # missing fields = unprocessable entity
        self.assertIn("detail", response.json())

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
            type="buy",
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
            type="buy",
            user_id="user123",
            display_name="John Doe",
            email="johndoe@example.com"
        )
        with self.assertRaises(HTTPException) as context:
            await update_listing("nonexistentid", update_data)
        self.assertEqual(context.exception.status_code, 404)

    async def test_unauthorized_update(self):
        """
        Test updating a listing with an unauthorized user ID.
        """
        original_listing = ListingInformation(
            title="Original Title",
            description="Original description",
            price=200.0,
            image_url="",
            display_name="originaluser",
            email="originaluser@example.com",
            category="Electronics",
            type="buy",
            user_id="originaluserid",
        )
        response = await upload_listing(original_listing)
        listing_id = response['listing_id']
        update_data = original_listing.copy(update={"user_id": "unauthorizeduserid"})
        with self.assertRaises(HTTPException) as context:
            await update_listing(listing_id, update_data)
        self.assertEqual(context.exception.status_code, 403)

    async def test_delete_nonexistent_listing_route(self):
        response = requests.delete('http://localhost:8000/api/sell-list/delete/nonexistentid?user_id=testuserid')
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()['detail'], "Listing not found")
        
    async def test_delete_non_existent_listing(self):
        """
        Test deletion of a non-existent listing.
        """
        with self.assertRaises(HTTPException) as context:
            await delete_listing("nonexistentid", "someuserid")
        self.assertEqual(context.exception.status_code, 404)

    async def test_update_non_existent_listing(self):
        """
        Test updating a non-existent listing.
        """
        update_data = ListingInformation(
            title="Non-Existent Update",
            description="Update attempt on a non-existent listing.",
            price=50.0,
            image_url="",
            display_name="nonexistentuser",
            email="nonexistentuser@example.com",
            category="Electronics",
            availability_dates="",
            type="buy",
            user_id="nonexistentuserid",
        )
        with self.assertRaises(HTTPException) as context:
            await update_listing("nonexistentid", update_data)
        self.assertEqual(context.exception.status_code, 404)

    async def test_partial_update_listing(self):
        """
        Test updating a listing with partial data.
        """
        original_listing = ListingInformation(
            title="Partial Update Test",
            description="Original description for partial update test.",
            price=300.0,
            image_url="",
            display_name="partialupdateuser",
            email="partialupdateuser@example.com",
            category="Gadgets",
            availability_dates="6/1/2024 to 6/10/2024",
            type="rent",
            user_id="partialupdateuserid",
        )
        response = await upload_listing(original_listing)
        listing_id = response['listing_id']

        update_data = ListingInformation(
            title="Updated Partial Title",
            user_id="partialupdateuserid",
            price=250.0,
            category="Gadgets",
            type="rent",
            display_name="partialupdateuser",
            email="partialupdateuser@example.com"
        )
        response = await update_listing(listing_id, update_data)
        self.assertEqual(response['message'], "Listing updated successfully")

    async def test_fetch_listing_details_non_existent(self):
        """
        Test fetching details of a non-existent listing.
        """
        with self.assertRaises(HTTPException) as context:
            await get_listing_details("nonexistentid")
        self.assertEqual(context.exception.status_code, 404)

    async def test_update_listing_unauthorized_user(self):
        """
        Test updating a listing with a different, unauthorized user ID.
        """
        original_listing = ListingInformation(
            title="Unauthorized Update",
            description="Test unauthorized update attempt.",
            price=100.0,
            image_url="",
            display_name="authorizeduser",
            email="authorizeduser@example.com",
            category="Miscellaneous",
            availability_dates="",
            type="buy",
            user_id="authorizeduserid"
        )
        response = await upload_listing(original_listing)
        listing_id = response['listing_id']

        update_data = ListingInformation(
            title="Unauthorized Update Attempt",
            description="Trying to update with a different user ID.",
            price=120.0,
            image_url="",
            display_name="unauthorizeduser",
            email="unauthorizeduser@example.com",
            category="Miscellaneous",
            availability_dates="",
            type="buy",
            user_id="unauthorizeduserid"
        )
        with self.assertRaises(HTTPException) as context:
            await update_listing(listing_id, update_data)
        self.assertEqual(context.exception.status_code, 403)

    """By using input validation from Pydantic and not using known
    HTTP status codes within some elements of the listings page, 
    I am unable to test for specific conditions such as negative prices.
    If a negative input is found for the price, for instance, I will receive
    an error in my test (which passes, as an error was expected). Upon
    researching how to explicitly write this test to get it to work (and
    not fail the emulator test), it seems that this cannot be done — the test
    will fail and there will always be an error message from the Validator, as
    expected.
    """

if __name__ == '__main__':
    unittest.main()
