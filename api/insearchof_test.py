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


def create_test_image():
    # Create an image for testing
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr


class InSearchOfTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        clear_db()
        pass

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

    def create_initial_request(self):
        # This function simulates adding an initial entry to the database
        test_request = RequestInformation(
            title="Initial Title",
            description="Initial Description",
            price=50.0,
            image_url="",
            user_id="initialuserid",
            display_name="initialuser",
            email="initialuser@gmail.com",
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Home"]
        )
        response = requests.post(
            "http://localhost:8000/api/insearchof/upload", json=test_request.model_dump())
        return response.json()['request_id']

    # async def test_upload_request_with_image(self):
    #     # First, upload an image and get the URL
    #     img_byte_arr = create_test_image()
    #     user_id = "testuserid"
    #     file = UploadFile(filename="test.jpg", file=io.BytesIO(img_byte_arr.getvalue()))
    #     image_response = await upload_image(user_id, file)

    #     # Extract the content from the JSONResponse
    #     image_response_content = image_response.body.decode('utf-8')
    #     image_response_dict = json.loads(image_response_content)

    #     # Assert based on the dictionary content
    #     self.assertEqual(image_response_dict['message'], "Image uploaded successfully")

    #     # Now, use the returned image URL in the request information
    #     test_request = RequestInformation(
    #         title="Test Title",
    #         description="Test Description",
    #         price=25.0,
    #         image_url=image_response_dict['image_url'],
    #         user_id="testuserid",
    #         display_name="testuser",
    #         email="testemail@gmail.com",
    #         type="request",
    #         trans_comp=False,
    #         urgent=False,
    #         categories=["Electronics"]
    #     )
    #     response = await upload_request(test_request)
    #     response_content = response.body.decode('utf-8')
    #     response_dict = json.loads(response_content)

    #     self.assertEqual(response_dict['message'], "Request uploaded successfully")
    #     self.assertIn("request_id", response_dict)


if __name__ == '__main__':
    unittest.main()
