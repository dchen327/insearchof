import os
os.environ['TESTING'] = 'True'
from routers.insearchof import *
import requests
import unittest
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from dotenv import load_dotenv
from datetime import datetime, timezone


load_dotenv()

FIREBASE_ID = os.getenv('NEXT_PUBLIC_FIREBASE_PROJECT_ID')
FIRESTORE_EMULATORS_PORT = 'localhost:8080'

os.environ['FIRESTORE_EMULATOR_HOST'] = FIRESTORE_EMULATORS_PORT
cred = AnonymousCredentials()
db = Client(project=FIREBASE_ID, credentials=cred)


def clear_db():
    url = f"http://{FIRESTORE_EMULATORS_PORT}/emulator/v1/projects/{FIREBASE_ID}/databases/(default)/documents"
    response = requests.delete(url)
    if response.status_code == 200:
        print('Database cleared')
    else:
        print('Error clearing database', response.status_code)


class InSearchOfTests(unittest.IsolatedAsyncioTestCase):
    # async def test_upload_request_successful(self):
    #     test_request = RequestInformation(
    #         title="Test Title",
    #         description="Test Description",
    #         price=25.0,  
    #         timestamp=datetime.now(timezone.utc),
    #         image_url="",
    #         user_id="testuserid",
    #         type="request",
    #         trans_comp=False,
    #         urgent=False,
    #         categories=["Electronics"]
    #     )
    #     response = await upload_request(test_request)
    #     self.assertEqual(response['message'], "Request uploaded successfully")

    # async def test_upload_request_negative_price(self):
    #     test_request = RequestInformation(
    #         title="Test Title",
    #         description="Test Description",
    #         price=-25.0,  
    #         timestamp=datetime.now(timezone.utc),
    #         image_url="",
    #         user_id="testuserid",
    #         type="request",
    #         trans_comp=False,
    #         urgent=False,
    #         categories=["Electronics"]
    #     )
    #     with self.assertRaises(HTTPException) as context:
    #         await upload_request(test_request)
    #     self.assertEqual(context.exception.status_code, 422)
        
    # async def test_upload_request_empty_title(self):
    #     test_request = RequestInformation(
    #         title="",
    #         description="Test Description",
    #         price=25.0,  
    #         timestamp=datetime.now(timezone.utc),
    #         image_url="",
    #         user_id="testuserid",
    #         type="request",
    #         trans_comp=False,
    #         urgent=False,
    #         categories=["Electronics"]
    #     )
    #     with self.assertRaises(HTTPException) as context:
    #         await upload_request(test_request)
    #     self.assertEqual(context.exception.status_code, 422)
        
    # async def test_upload_request_not_logged_in(self):
    #     test_request = RequestInformation(
    #         title="Test Title",
    #         description="Test Description",
    #         price=25.0,  
    #         timestamp=datetime.now(timezone.utc),
    #         image_url="",
    #         user_id="",
    #         type="request",
    #         trans_comp=False,
    #         urgent=False,
    #         categories=["Electronics"]
    #     )
    #     with self.assertRaises(HTTPException) as context:
    #         await upload_request(test_request)
    #     self.assertEqual(context.exception.status_code, 422)
        
    async def asyncSetUp(self):
        self.test_item_id = "fixed_test_item_id"
        self.user_id = "testuserid"
        item_ref = db.collection('items').document(self.test_item_id)
        item_ref.delete()  # Notice `await` is removed if it's not an async call
        
        initial_data = RequestInformation(
            title="Initial Title",
            description="Initial Description",
            price=100.0,
            image_url="",
            user_id=self.user_id,
            type="request",
            trans_comp=False,
            urgent=False,
            categories=["Books"]
        )
        
        item_ref.set(jsonable_encoder(initial_data))  # Same here, `await` is removed if not needed

    async def test_update_request_successful(self):
        update_data = RequestInformation(
            title="Updated Title",
            description="Updated Description",
            price=120.0,
            timestamp=datetime.now(timezone.utc),
            image_url="",
            user_id=self.user_id,
            type="request",
            trans_comp=False,
            urgent=True,
            categories=["Books", "Education"]
        )
        print(self.test_item_id)
        response = await update_request(self.test_item_id, update_data)
        self.assertEqual(response['message'], "Item updated successfully")


if __name__ == '__main__':
    unittest.main()
