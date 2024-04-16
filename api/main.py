from fastapi import FastAPI
from .routers import catalog, insearchof, profile, sellList

tags_metadata = [
    {
        'name': 'catalog',
        'description': """
The catalog backend component is responsible for retrieving listings from the database given frontend searches and filters. These listings are then displayed to the user on the frontend.
It also handles when a user chooses to purchase an item, working with the profiles backend to show the seller's contact information.""",
    },
    {
        'name': 'insearchof',
        'description': """The insearchofer backend component allows users to request items or services through the application, functioning similarly to current ISO management practices.
        """
    },
    {
        'name': 'sell-list',
        'description': """The sellList backend component is responsible for creating selling and listing functionality within our marketplace.
         Users are able to do the following: add, update, and delete posts."""
    },
    {
         'name': 'profile',
        'description': """The User backend component allows users users to view and manage their profile information, view transaction history,
    and interact with the platform.
        """
    }
]

app = FastAPI(openapi_tags=tags_metadata,
              swagger_ui_parameters={'defaultModelsExpandDepth': -1})

app.include_router(catalog.router)
app.include_router(profile.router)
app.include_router(insearchof.router)
app.include_router(sellList.router)