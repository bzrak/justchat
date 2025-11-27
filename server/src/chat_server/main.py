from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from chat_server.settings import get_settings

settings = get_settings()

# Create FastAPI app with settings
app = FastAPI(
    title="Chat Server API",
    version="0.1.0",
    debug=settings.is_development,
)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Chat Server API",
        "environment": settings.ENVIRONMENT,
    }


# async_engine = create_async_engine(
#     settings.async_database_url,
#     pool_size=settings.DB_POOL_SIZE,
#     max_overflow=settings.DB_MAX_OVERFLOW,
# )
async_engine = create_async_engine(settings.async_database_url)
