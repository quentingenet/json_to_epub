import logging
from fastapi import FastAPI

from core.security import configure_cors
from endpoints import converter


app = FastAPI()

configure_cors(app)

logger = logging.getLogger("app")

app.include_router(converter.router, prefix="/api")



