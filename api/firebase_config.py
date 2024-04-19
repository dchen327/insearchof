# firebase_config.py
import os
import json
from firebase_admin import credentials, initialize_app, firestore
from dotenv import load_dotenv

load_dotenv()

cred_dict = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY'))
cred = credentials.Certificate(cred_dict)
firebase_app = initialize_app(cred, {
    'storageBucket': os.getenv('NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET')
})
db = firestore.client()
