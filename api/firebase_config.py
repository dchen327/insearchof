# firebase_config.py
import os
import json
from firebase_admin import credentials, initialize_app, firestore
from dotenv import load_dotenv
from google.cloud.firestore import Client
from google.auth.credentials import AnonymousCredentials

load_dotenv()

if os.getenv('TESTING'):
    FIREBASE_ID = os.getenv('NEXT_PUBLIC_FIREBASE_PROJECT_ID')
    FIRESTORE_EMULATORS_PORT = 'localhost:8080'
    FIREBASE_STORAGE_EMULATOR_HOST = 'localhost:9199'

    os.environ['FIRESTORE_EMULATOR_HOST'] = FIRESTORE_EMULATORS_PORT
    os.environ['STORAGE_EMULATOR_HOST'] = FIREBASE_STORAGE_EMULATOR_HOST
    cred = AnonymousCredentials()
    db = Client(project=FIREBASE_ID, credentials=cred)
else:
    cred_dict = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY'))
    cred = credentials.Certificate(cred_dict)
    firebase_app = initialize_app(cred, {
        'storageBucket': os.getenv('NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET')
    })
    db = firestore.client()
