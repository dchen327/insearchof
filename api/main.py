from fastapi import FastAPI
from .routers import catalog, profiles

tags_metadata = [
    {
        'name': 'Profiles',
        'description': """The User backend component allows users users to view and manage their profile information, view transaction history,
    and interact with the platform.
        """
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(catalog.router)
app.include_router(profiles.router)
