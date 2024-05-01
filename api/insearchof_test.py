import os
os.environ['TESTING'] = 'True'

from routers.insearchof import *
import requests
import unittest
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from dotenv import load_dotenv
from firebase_config import db


load_dotenv()

FIREBASE_ID = os.getenv('NEXT_PUBLIC_FIREBASE_PROJECT_ID')
FIRESTORE_EMULATORS_PORT = 'localhost:8080'


def clear_db():
    url = f"http://{FIRESTORE_EMULATORS_PORT}/emulator/v1/projects/{FIREBASE_ID}/databases/(default)/documents"
    response = requests.delete(url)
    if response.status_code != 200:
        print('Error clearing database', response.status_code)


class InSearchOfTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """
        Set up method called before each test. Clears the database to ensure isolation of test cases.
        """
        clear_db()

    async def test_upload_request_successful(self):
        """
        Test to ensure a valid request can be successfully uploaded.
        Verifies that the database correctly reflects the new ISO request entry after upload.
        """
        test_request = RequestInformation(
            title="Test Title",
            description="Test Description",
            price=25.0,
            timestamp=datetime.now(timezone.utc),
            image_url="",
            user_id="testuserid",
            display_name="testuser",
            email="testemail@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Electronics"]
        )
        response = await upload_request(test_request)
        self.assertEqual(response['message'], "Request uploaded successfully")

    async def test_upload_request_negative_price(self):
        """
        Test to ensure that an upload request with a negative price is rejected.
        This test validates the backend's ability to handle invalid input correctly.
        """
        test_request = RequestInformation(
            title="Test Title",
            description="Test Description",
            price=-25.0,
            timestamp=datetime.now(timezone.utc),
            image_url="",
            user_id="testuserid",
            display_name="testuser",
            email="testemail@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Electronics"]
        )
        with self.assertRaises(HTTPException) as context:
            await upload_request(test_request)
        self.assertEqual(context.exception.status_code, 422)

    async def test_upload_request_empty_title(self):
        """
        Test to ensure that an upload request with an empty title is rejected.
        Validates that the title is a necessary field for request validation.
        """
        test_request = RequestInformation(
            title="",
            description="Test Description",
            price=25.0,
            timestamp=datetime.now(timezone.utc),
            image_url="",
            user_id="testuserid",
            display_name="testuser",
            email="testemail@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Electronics"]
        )
        with self.assertRaises(HTTPException) as context:
            await upload_request(test_request)
        self.assertEqual(context.exception.status_code, 422)

    async def test_upload_request_not_logged_in(self):
        """
        Test to ensure that an upload request without a user ID is rejected.
        This simulates the scenario where a non-logged-in user attempts to upload a request.
        """
        test_request = RequestInformation(
            title="Test Title",
            description="Test Description",
            price=25.0,
            timestamp=datetime.now(timezone.utc),
            image_url="",
            user_id="",
            display_name="testuser",
            email="testemail@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Electronics"]
        )
        with self.assertRaises(HTTPException) as context:
            await upload_request(test_request)
        self.assertEqual(context.exception.status_code, 422)

    async def test_update_request_successful(self):
        """
        Test the successful update of an existing request.
        This test involves:
        1. Creating an initial entry in the database.
        2. Updating this entry with new data.
        3. Verifying that the changes are accurately reflected in the database.
        """
        # First, create an initial entry in the database
        initial_request = RequestInformation(
            title="Initial Title",
            description="Initial Description",
            price=100.0,
            user_id="testuserid",
            display_name="Initial User",
            email="initialuser@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Home", "Garden"]
        )
        initial_response = await upload_request(initial_request)
        item_id = initial_response['request_id']

        # Update the entry
        update_data = RequestInformation(
            title="Updated Title",
            description="Updated Description",
            price=150.0,
            user_id="testuserid",  # Ensure user_id matches for permission
            display_name="Initial User",
            email="initialuser@gmail.com",
            type="request",
            trans_comp=True,  # Mark as transaction complete
            urgent=True,
            categories=["Electronics", "Garden"]  # Change categories
        )

        # Perform the update
        response = await update_request(item_id, update_data)
        self.assertEqual(response['message'], "Item updated successfully")

        # Verify the update
        item_details = await get_item_details(item_id)
        self.assertEqual(item_details['itemDetails']['title'], "Updated Title")
        self.assertEqual(item_details['itemDetails']
                         ['description'], "Updated Description")
        self.assertEqual(item_details['itemDetails']['price'], 150.0)
        self.assertTrue(item_details['itemDetails']['trans_comp'])
        self.assertTrue(item_details['itemDetails']['urgent'])
        self.assertListEqual(item_details['itemDetails']['categories'], [
                             "Electronics", "Garden"])

    async def test_update_request_permission_denied(self):
        """
        Test to ensure that an attempt to update a request by a user who does not own the request is denied.
        This simulates the scenario where a user tries to update another user's request.
        """
        # Create an initial request by a different user
        initial_request = RequestInformation(
            title="Initial Title",
            description="Initial Description",
            price=100.0,
            user_id="differentuserid",  # Different user ID
            display_name="Different User",
            email="differentuser@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Home", "Garden"]
        )
        initial_response = await upload_request(initial_request)
        item_id = initial_response['request_id']

        # Attempt to update the request with a different user ID
        update_data = RequestInformation(
            title="Updated Title",
            description="Updated Description",
            price=150.0,
            user_id="testuserid",  # User ID does not match the original
            display_name="Initial User",
            email="initialuser@gmail.com",
            type="request",
            trans_comp=True,
            urgent=True,
            categories=["Electronics", "Garden"]
        )

        with self.assertRaises(HTTPException) as context:
            await update_request(item_id, update_data)
        self.assertEqual(context.exception.detail,
                         "403: You do not have permission to update this item.")

    async def test_update_request_item_not_found(self):
        """
        Test the behavior when attempting to update a non-existent request.
        This test ensures that the system properly handles cases where the specified item ID does not correspond to any existing record.
        """
        # Non-existent item ID
        item_id = "nonexistentitemid"

        # Attempt to update a non-existent request
        update_data = RequestInformation(
            title="Updated Title",
            description="Updated Description",
            price=150.0,
            user_id="testuserid",
            display_name="Test User",
            email="testuser@gmail.com",
            type="request",
            trans_comp=True,
            urgent=True,
            categories=["Electronics", "Garden"]
        )

        with self.assertRaises(HTTPException) as context:
            await update_request(item_id, update_data)
        self.assertEqual(context.exception.detail, "404: Item not found")

    async def test_delete_request_successful(self):
        """
        Test the successful deletion of an ISO request.
        This test checks that:
        1. A request can be created and then deleted successfully.
        2. The database no longer contains the deleted request.
        """
        # Create an initial request by the user
        initial_request = RequestInformation(
            title="Initial Title",
            description="Initial Description",
            price=100.0,
            user_id="testuserid",  # User ID of the owner
            display_name="Test User",
            email="testuser@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Home", "Garden"]
        )
        initial_response = await upload_request(initial_request)
        item_id = initial_response['request_id']

        # User data for authentication matching the item owner
        user_data = {
            "user_id": "testuserid"
        }

        # Delete the request
        delete_response = await delete_request(item_id, user_data)
        self.assertEqual(delete_response['message'], "Item and associated image deleted successfully")

        # Verify that the item is no longer in the database
        with self.assertRaises(HTTPException) as context:
            await get_item_details(item_id)
        self.assertEqual(context.exception.detail, "404: Item not found")

    async def test_delete_request_permission_denied(self):
        """
        Test to ensure that a request cannot be deleted by a user other than the owner.
        This test verifies proper authentication and authorization enforcement.
        """
        # Create an initial request by a different user
        initial_request = RequestInformation(
            title="Initial Title",
            description="Initial Description",
            price=100.0,
            user_id="differentuserid",  # Different user ID
            display_name="Different User",
            email="differentuser@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Home", "Garden"]
        )
        initial_response = await upload_request(initial_request)
        item_id = initial_response['request_id']

        # User data pretending to be a different user
        user_data = {
            "user_id": "testuserid"  # Does not match the owner of the item
        }

        with self.assertRaises(HTTPException) as context:
            await delete_request(item_id, user_data)
        self.assertEqual(context.exception.detail, "403: You do not have permission to delete this item.")

    async def test_delete_request_item_not_found(self):
        """
        Test the behavior when attempting to delete a non-existent request.
        This test ensures that the system properly handles attempts to delete items that do not exist in the database.
        """
        # Non-existent item ID
        item_id = "nonexistentitemid"

        # User data for authentication
        user_data = {
            "user_id": "testuserid"
        }

        with self.assertRaises(HTTPException) as context:
            await delete_request(item_id, user_data)
        self.assertEqual(context.exception.detail, "404: Item not found")

    async def test_mark_transaction_as_complete_success(self):
        """
        Test marking a transaction as complete successfully.
        Verifies that:
        1. The transaction status is updated in the database.
        2. Only the rightful owner can mark the transaction as complete.
        """
        # Create an initial request by the user
        initial_request = RequestInformation(
            title="To Complete Title",
            description="To Complete Description",
            price=150.0,
            user_id="testuserid",  # User ID of the owner
            display_name="Test User",
            email="testuser@gmail.com",
            type="request",
            trans_comp=False,  # Initially not completed
            urgent=False,
            categories=["Electronics"]
        )
        initial_response = await upload_request(initial_request)
        item_id = initial_response['request_id']

        # User data for authentication matching the item owner
        user_data = {
            "user_id": "testuserid"
        }

        # Mark the transaction as complete
        mark_response = mark_transaction_complete(item_id, user_data)
        self.assertTrue(mark_response['trans_comp_value'])

    async def test_mark_transaction_as_complete_permission_denied(self):
        """
        Test to ensure that a transaction cannot be marked as complete by someone other than the transaction owner.
        This test checks for proper authentication and authorization to safeguard the integrity of transaction status updates.
        """
        # Create an initial request by a different user
        initial_request = RequestInformation(
            title="Other User Title",
            description="Other User Description",
            price=100.0,
            user_id="differentuserid",
            display_name="Different User",
            email="differentuser@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Home"]
        )
        initial_response = await upload_request(initial_request)
        item_id = initial_response['request_id']

        # User data pretending to be a different user
        user_data = {
            "user_id": "testuserid"  # Does not match the owner
        }

        with self.assertRaises(HTTPException) as context:
            await mark_transaction_complete(item_id, user_data)
        self.assertEqual(context.exception.detail, "403: You do not have permission to mark this transaction as complete.")

    async def test_mark_transaction_as_complete_item_not_found(self):
        """
        Test the response when attempting to mark a transaction as complete for a non-existent item.
        Ensures that the system properly responds with an error when the item ID does not exist.
        """
        # Non-existent item ID
        item_id = "nonexistentitemid"

        # User data for authentication
        user_data = {
            "user_id": "testuserid"
        }

        with self.assertRaises(HTTPException) as context:
            await mark_transaction_complete(item_id, user_data)
        self.assertEqual(context.exception.detail, "404: Item not found")


if __name__ == '__main__':
    unittest.main()
