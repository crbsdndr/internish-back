from internish.security import require_auth

from institution_app.views import institution_interact
from institution_app.schemas import Institution

from fastapi import APIRouter, Depends, HTTPException

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
    try:
        result = institution_interact.v_create(
            institution=institution,
            institution_contacts=institution.institution_contacts_.model_dump() if institution.institution_contacts_ else None,
            institution_quotas=institution.institution_quotas_.model_dump() if institution.institution_quotas_ else None,
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail={
            "status": False, "message": f"Validation error: {str(ve)}"
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail={
            "status": False, "message": f"Error: {str(e)}"
        })

    return {"status_code": 200, "detail": {
        "status": result, "message": "Institution created successfully"
    }}