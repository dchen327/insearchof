import os
import requests
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from dotenv import load_dotenv

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


doc_ref = db.collection("users").document("alovelace")
doc_ref.set({"first": "Ada", "last": "Lovelace", "born": 1815})

doc_ref = db.collection("users").document("aturing")
doc_ref.set({"first": "Alan", "middle": "Mathison",
            "last": "Turing", "born": 1912})

users_ref = db.collection("users")
docs = users_ref.stream()

for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")

print('hi')
clear_db()
