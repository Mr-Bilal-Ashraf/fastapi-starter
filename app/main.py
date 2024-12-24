from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI, staticfiles

from app.dependencies import engine
from app.models.base import Base
from app.config import settings


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    summary=settings.APP_SUMMARY,
    version=settings.APP_VERSION,
    terms_of_service=settings.APP_TERM_OF_SERVICE,
    contact={
        "name": settings.APP_CONTACT_NAME,
        "url": settings.APP_CONTACT_URL,
        "email": settings.APP_CONTACT_EMAIL,
    },
    license_info={
        "name": settings.APP_LICENSE_NAME,
        "identifier": settings.APP_LICENSE_IDENTIFIER,
    },
)


# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware)  # Compress responses


# Include API routes
def configure_routing():
    from app.api.v1 import user

    app.mount("/app/static", staticfiles.StaticFiles(directory="app/static"), name="static")
    # app.include_router(base.router, prefix="/base", tags=["base"])
    app.include_router(user.router, prefix="/api", tags=["user"])

@app.on_event("startup")
def startup_event():
    from app.models.base import OTP
    from app.models.user import User
    Base.metadata.create_all(engine)
    configure_routing()


@app.get("/ping")
async def ping():
    return {"status": "pong"}
