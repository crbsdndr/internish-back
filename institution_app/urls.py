from internish.security import require_auth

from institution_app.views import institution_interact
from institution_app.schemas import Institution

from fastapi import APIRouter, Depends

print("Loading institution_app.urls module")

institution_router_public = APIRouter(prefix="/institutions", tags=["institutions"])
institution_router_private = APIRouter(
    prefix="/institutions",
    tags=["institutions"],
    dependencies=[Depends(require_auth)],
)

@institution_router_public.get("/")
def status():
    return {"message": "Hallo, this is from microsoft. I want to tell that your bank account is in danger"}

@institution_router_public.post("/create/")
def create_institution(institution: Institution):
    result = institution_interact.v_create(institution)
    return result