from fastapi import FastAPI
from .routers import catalog, insearchof, profile, sellList

tags_metadata = [
    {
        'name': 'Profiles',
        'description': """The User backend component allows users users to view and manage their profile information, view transaction history,
    and interact with the platform.
        """
    },
]

app = FastAPI(openapi_tags=tags_metadata,
              swagger_ui_parameters={'defaultModelsExpandDepth': -1})

app.include_router(catalog.router)
app.include_router(profile.router)
app.include_router(insearchof.router)
app.include_router(sellList.router)