import os
os.environ['TESTING'] = 'True'
from routers.profile import UserProfile
from routers.insearchof import upload_request, RequestInformation
import requests
import unittest
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from dotenv import load_dotenv
from firebase_config import db
from pydantic.error_wrappers import ValidationError


load_dotenv()

FIREBASE_ID = os.getenv('NEXT_PUBLIC_FIREBASE_PROJECT_ID')
FIRESTORE_EMULATORS_PORT = 'localhost:8080'


def clear_db():
    url = f"http://{FIRESTORE_EMULATORS_PORT}/emulator/v1/projects/{FIREBASE_ID}/databases/(default)/documents"
    response = requests.delete(url)
    if response.status_code != 200:
        print('Error clearing database', response.status_code)

class ProfileTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        clear_db()
        pass

    async def test_upload_user_info_successful(self):
        # Test case for successful upload of user info  
        test_info = UserProfile.UploadContactInformation(
            phoneNumber="1234567890",
            location="Test Location",
            userID="test_user_id"
        )
        response = UserProfile.upload_contact_info(test_info)
        self.assertEqual(response['message'], "Uploaded user's contact info successfully")


    async def test_upload_user_info_invalid_data(self):
        # Test case for uploading user info with invalid data
        with self.assertRaises(ValidationError):
            test_info = UserProfile.UploadContactInformation(
                phone_number="Invalid Phone Number",  # Invalid format
                location="Test Location",
                userID="test_user_id"
            )

            response = await UserProfile.upload_contact_info(test_info)


    async def test_get_list_of_items(self):
        # Test case for getting list of items associated with a user
        requester_id = "test_user_id"
        response = UserProfile.get_list_of_items(requester_id)
        self.assertEqual(response['listingOfItems'], [])


    async def test_get_transaction_history(self):
        # Test case for getting transaction history of a user
        requester_id = "test_user_id"
        response = UserProfile.get_transaction_history(requester_id)
        self.assertEqual(response['listingOfTransactionHistory'], [])


    async def test_upload_request_empty_location(self):
        # Test case for uploading user info without a location
        with self.assertRaises(ValidationError):
            test_info = UserProfile.UploadContactInformation(
                phoneNumber="Invalid Phone Number",  
                location=""
            )

            await upload_request(test_info)


    async def test_update_profile(self):
        # Test case for updating profile
        test_info = UserProfile.UploadContactInformation(
            phoneNumber="1234567890",
            location="Test Location",
            userID="test_user_id"
        )
        UserProfile.upload_contact_info(test_info)
        updated_info = UserProfile.UploadContactInformation(
            phoneNumber="0987654321",
            location="Updated Location",
            userID="test_user_id"
        )
        UserProfile.upload_contact_info(updated_info)

        response = UserProfile.get_user_info(updated_info.userID)
        self.assertEqual(response['phoneNumber'], updated_info.phoneNumber)
        self.assertEqual(response['location'], updated_info.location)


    async def test_get_user_info_non_existing_user(self):
        # Test case for getting user info of a non-existing user
        requester_id = "non_existing_user_id"
        response = UserProfile.get_user_info(requester_id)
        self.assertEqual(response['userID'], '')
        self.assertEqual(response['location'], '')
        self.assertEqual(response['phoneNumber'], '')


if __name__ == '__main__':
    unittest.main()