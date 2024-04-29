import os
os.environ['TESTING'] = 'True'

from firebase_config import db
from dotenv import load_dotenv
from google.cloud.firestore import Client
from google.auth.credentials import AnonymousCredentials
import unittest
import requests
from routers.insearchof import *
from PIL import Image
from fastapi import UploadFile
import json


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
        clear_db()
        pass

    async def test_upload_user_info_successful(self):
        # Test case for successful upload of user info  
        test_info = RequestInformation(
            phone_number="1234567890",
            location="Test Location"
        )
        response = await upload_request(test_info)
        self.assertEqual(response['message'], "User info uploaded successfully")


    async def test_upload_user_info_invalid_data(self):
        # Test case for uploading user info with invalid data
        test_info = RequestInformation(
            phone_number="Invalid Phone Number",  # Invalid format
            location="Test Location"
        )

        response = await upload_request(test_info)

        with self.assertRaises(HTTPException) as context:
            await upload_request(test_info)
        self.assertEqual(context.exception.status_code, 422)

    async def test_upload_request_empty_location(self):
        # Test case for uploading user info without a location
        test_info = RequestInformation(
            phone_number="Invalid Phone Number",  
            location=""
        )

        response = await upload_request(test_info)

        with self.assertRaises(HTTPException) as context:
            await upload_request(test_info)
        self.assertEqual(context.exception.status_code, 422)