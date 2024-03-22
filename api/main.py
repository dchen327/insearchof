from fastapi import FastAPI
from .routers import catalog, profiles

tags_metadata = [
    {
        'name': 'catalog',
        'description': '''
These are items ''',
    }
]

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(catalog.router)
app.include_router(profiles.router)
