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


class CatalogTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        clear_db()

    def test_black_box(self):
        response = requests.get('http://localhost:8000/api/catalog/listings')
        self.assertEqual(response.status_code, 200)

        # negative price
        response = requests.get('http://localhost:8000/api/catalog/listings?min_price=-10')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "Minimum price must be a non-negative value.")

        # min price > max price
        response = requests.get('http://localhost:8000/api/catalog/listings?min_price=10&max_price=5')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "Maximum price must be greater than or equal to minimum price.")

        # invalid sort
        response = requests.get('http://localhost:8000/api/catalog/listings?sort=invalid')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "Invalid sort option.")

        # valid sort
        response = requests.get('http://localhost:8000/api/catalog/listings?sort=uploadDateAsc')
        self.assertEqual(response.status_code, 200)

        # invalid type
        response = requests.get('http://localhost:8000/api/catalog/listings?listing_types=invalid')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "Invalid listing type.")

        # valid type
        response = requests.get('http://localhost:8000/api/catalog/listings?listing_types=buy')
        self.assertEqual(response.status_code, 200)


    def test_query_empty_db(self):
        listings = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['All'])
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
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['All'])
        self.assertEqual(len(request_listings['listings']), 1)
        self.assertEqual(request_listings['listings'][0]['type'], 'request')

        other_listings = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent'], min_price=0, max_price=0, categories=['All'])
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
                                'buy', 'rent', 'request'], min_price=0, max_price=10, categories=['All'])    
        self.assertEqual(len(listings_under_10['listings']), 0)

        listings_over_100 = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=100, max_price=0, categories=['All'])
        self.assertEqual(len(listings_over_100['listings']), 0)

        listings_50 = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=50, max_price=50, categories=['All'])
        self.assertEqual(len(listings_50['listings']), 1)
    
    async def test_sort(self):
        ''' Check sorting options '''
        test_request1 = RequestInformation(
            title="Test title 1",
            description="Test description",
            price=50,
            user_id="userid",
            type="request",
            urgent=False,
            categories=["Test category"],
            display_name='test user',
            email='testemail@gmail.com'
        )

        test_request2 = RequestInformation(
            title="Test title 2",
            description="Test description",
            price=100,
            user_id="userid",
            type="request",
            urgent=False,
            categories=["Test category"],
            display_name='test user',
            email='testemail@gmail.com'
        )

        await upload_request(test_request1)
        await upload_request(test_request2)

        listings_upload_desc = get_listings(search='', sort='uploadDateDesc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['All'])
        self.assertEqual(len(listings_upload_desc['listings']), 2)
        self.assertEqual(listings_upload_desc['listings'][0]['title'], 'Test title 2')
        self.assertEqual(listings_upload_desc['listings'][1]['title'], 'Test title 1')

        listings_price_desc = get_listings(search='', sort='priceDesc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['All'])
        self.assertEqual(len(listings_price_desc['listings']), 2)
        self.assertEqual(listings_price_desc['listings'][0]['price'], 100)
        self.assertEqual(listings_price_desc['listings'][1]['price'], 50)
    
    async def test_categories(self):
        ''' Check categories filter '''
        test_request1 = RequestInformation(
            title="Test title 1",
            description="Test description",
            price=50,
            user_id="userid",
            type="request",
            urgent=False,
            categories=["Clothing"],
            display_name='test user',
            email='testemail@gmail.com'
        )

        test_request2 = RequestInformation(
            title="Test title 2",
            description="Test description",
            price=100,
            user_id="userid",
            type="request",
            urgent=False,
            categories=["Electronics"],
            display_name='test user',
            email='testemail@gmail.com'
        )

        await upload_request(test_request1)
        await upload_request(test_request2)

        listings_clothing = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['Clothing'])
        
        self.assertEqual(len(listings_clothing['listings']), 1)
        self.assertEqual(listings_clothing['listings'][0]['categories'], ['Clothing'])

        listings_food = get_listings(search='', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['Food'])
        self.assertEqual(len(listings_food['listings']), 0)

    async def test_search(self):
        ''' Check search query '''
        test_request = RequestInformation(
            title="microwave",
            description="the description has the word heat in it",
            price=50,
            user_id="userid",
            type="request",
            urgent=False,
            categories=["Clothing"],
            display_name='test user',
            email='test@gmail.com'
        )

        await upload_request(test_request)

        # search title
        listings_title = get_listings(search='wave', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['All'])
        self.assertEqual(len(listings_title['listings']), 1)
        self.assertEqual(listings_title['listings'][0]['title'], 'microwave')

        # search description
        listings_desc = get_listings(search='heat', sort='uploadDateAsc', listing_types=[
                                'buy', 'rent', 'request'], min_price=0, max_price=0, categories=['All'])
        self.assertEqual(len(listings_desc['listings']), 1)
        self.assertEqual(listings_desc['listings'][0]['description'], 'the description has the word heat in it')
        

    

if __name__ == '__main__':
    unittest.main()
