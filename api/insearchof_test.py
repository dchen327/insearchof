from datetime import datetime, timezone
from dotenv import load_dotenv
from google.cloud.firestore import Client
from google.auth.credentials import AnonymousCredentials
import unittest
import requests
from routers.insearchof import *
import os
from fastapi import UploadFile
import io
from PIL import Image

os.environ['TESTING'] = 'True'


load_dotenv()

FIREBASE_ID = os.getenv('NEXT_PUBLIC_FIREBASE_PROJECT_ID')
FIRESTORE_EMULATORS_PORT = 'localhost:8080'

os.environ['FIRESTORE_EMULATOR_HOST'] = FIRESTORE_EMULATORS_PORT
cred = AnonymousCredentials()
db = Client(project=FIREBASE_ID, credentials=cred)


def clear_db():
    url = f"http://{FIRESTORE_EMULATORS_PORT}/emulator/v1/projects/{FIREBASE_ID}/databases/(default)/documents"
    response = requests.delete(url)
    if response.status_code != 200:
        print('Error clearing database', response.status_code)


class InSearchOfTests(unittest.IsolatedAsyncioTestCase):
    # def setUp(self):
    #     clear_db()

    async def test_upload_request_successful(self):
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

    async def test_upload_image_success(self):
        # Create an in-memory image
        image = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        # Create an UploadFile object
        upload_file = UploadFile(filename="test_image.jpg", file=img_byte_arr)

        # Use the upload_image function directly
        response = await upload_image(user_id="testuserid", file=upload_file)
        
        # Assert the upload was successful
        self.assertIn('image_url', response)


if __name__ == '__main__':
    unittest.main()
