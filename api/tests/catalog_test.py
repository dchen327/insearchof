import os
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client

os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'
cred = AnonymousCredentials()

db = Client(project='insearchof-1fb7a', credentials=cred)


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
