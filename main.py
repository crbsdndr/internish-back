from fastapi import FastAPI
from internish import urls

app = FastAPI()

app.include_router(urls.router)
