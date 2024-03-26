from fastapi import FastAPI
from .routers import catalog, profiles, ISOrequest, sellList

tags_metadata = [
    {
        'name': 'catalog',
        'description': """
The catalog backend component is responsible for retrieving listings from the database given frontend searches and filters. These listings are then displayed to the user on the frontend.

It also handles when a user chooses to purchase an item, working with the profiles backend to show the seller's contact information.""",
    },
    {
        'name': 'ISOrequest',
        'description': """The ISORequester backend component allows users to request items or services through the application, functioning similarly to current ISO management practices.
        """
    },
    {
        'name': 'sellList',
        'description': """The sellList backend component is responsible for creating selling and listing functionality within our marketplace.
         Users are able to do the following: add, update, and delete posts."""
    }
]

app = FastAPI(openapi_tags=tags_metadata,
              swagger_ui_parameters={'defaultModelsExpandDepth': -1})

app.include_router(catalog.router)
app.include_router(profiles.router)
app.include_router(ISOrequest.router)
app.include_router(sellList.router)
