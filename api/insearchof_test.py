import os
os.environ['TESTING'] = 'True'
from routers.catalog import *
import requests
import unittest
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from main import app  # Ensure your FastAPI app is imported correctly


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


client = TestClient(app)

class TestUploadRequest(unittest.TestCase):

    def test_upload_valid_request(self):
        request_data = {
            "title": "Test Item",
            "description": "A test item description",
            "price": 100.0,
            "user_id": "user123",
            "type": "request",
            "urgent": False,
            "categories": ["Electronics", "Gadgets"]
        }
        response = client.post("/api/insearchof/upload", json=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertIn("Request uploaded successfully", response.json()['message'])


if __name__ == '__main__':
    unittest.main()
