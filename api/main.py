from fastapi import FastAPI
from .routers import catalog, profiles

tags_metadata = [
    {
        'name': 'catalog',
        'description': """
The catalog backend component is responsible for retrieving listings from the database given frontend searches and filters. These listings are then displayed to the user on the frontend.

It also handles when a user chooses to purchase an item, working with the profiles backend to show the seller's contact information.""",
    }
]

app = FastAPI(openapi_tags=tags_metadata,
              swagger_ui_parameters={'tryItOutEnabled': False})

app.include_router(catalog.router)
app.include_router(profiles.router)
