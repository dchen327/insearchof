import os
os.environ['TESTING'] = 'True'
from routers.catalog import get_listings
from routers.insearchof import upload_request, RequestInformation
import requests
import unittest
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from dotenv import load_dotenv
from firebase_config import db

load_dotenv()

FIREBASE_ID = os.getenv('NEXT_PUBLIC_FIREBASE_PROJECT_ID')
FIRESTORE_EMULATORS_PORT = 'localhost:8080'

# os.environ['FIRESTORE_EMULATOR_HOST'] = FIRESTORE_EMULATORS_PORT
# cred = AnonymousCredentials()
# db = Client(project=FIREBASE_ID, credentials=cred)


def clear_db():
    url = f"http://{FIRESTORE_EMULATORS_PORT}/emulator/v1/projects/{FIREBASE_ID}/databases/(default)/documents"
    response = requests.delete(url)
    if response.status_code != 200:
        print('Error clearing database', response.status_code)


# doc_ref = db.collection("users").document("alovelace")
# doc_ref.set({"first": "Ada", "last": "Lovelace", "born": 1815})

# doc_ref = db.collection("users").document("aturing")
# doc_ref.set({"first": "Alan", "middle": "Mathison",
#             "last": "Turing", "born": 1912})

# users_ref = db.collection("users")
# docs = users_ref.stream()

# for doc in docs:
#     print(f"{doc.id} => {doc.to_dict()}")

# print('hi')
# clear_db()

class CatalogTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        clear_db()
        pass

    def test_query_empty_db(self):
        listings = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['None'])
        self.assertEqual(listings, {"listings": []})

    async def test_type(self):
        ''' Ensure the correct type is returned '''
        test_request = RequestInformation(
            title="Test title 2",
            description="Test description",
            price=50,
            user_id="userid",
            type="request",
            urgent=False,
            categories=["Test category"],
            display_name='test user',
            email='test_email@gmail.com'
        )
        await upload_request(test_request)

        request_listings = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['None'])
        self.assertEqual(len(request_listings['listings']), 1)
        self.assertEqual(request_listings['listings'][0]['type'], 'request')

        other_listings = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent'], min_price=0, max_price=0, categories=['None'])
        self.assertEqual(len(other_listings['listings']), 0)

    async def test_price(self):
        ''' Check price filters (min/max) '''
        test_request = RequestInformation(
            title="Test title 2",
            description="Test description",
            price=50,
            user_id="userid",
            type="request",
            urgent=False,
            categories=["Test category"],
            display_name='test user',
            email='testemail@gmail.com'
        )
        await upload_request(test_request)

        listings_under_10 = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=10, categories=['None'])    
        self.assertEqual(len(listings_under_10['listings']), 0)

        listings_over_100 = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=100, max_price=0, categories=['None'])
        self.assertEqual(len(listings_over_100['listings']), 0)

        listings_50 = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=50, max_price=50, categories=['None'])
        self.assertEqual(len(listings_50['listings']), 1)

    

if __name__ == '__main__':
    unittest.main()
