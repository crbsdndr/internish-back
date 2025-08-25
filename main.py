from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from internish.urls import router
from internish.settings import config_frontend

app = FastAPI(debug=True)

app.include_router(router)

origins = [
    config_frontend.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

