from internish.security import require_auth

from institution_app.views import institution_interact
from institution_app.schemas import Institution

from fastapi import APIRouter, Depends, HTTPException, Query

print("Loading institution_app.urls module")

institution_router_public = APIRouter(prefix="/institutions", tags=["institutions"])
institution_router_private = APIRouter(
    prefix="/institutions",
    tags=["institutions"],
    dependencies=[Depends(require_auth)],
)

@institution_router_public.get("/")
def list_institutions(
    q: str | None = Query(None, description="Search"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Skip N items"),
):
    return institution_interact.list(q=q, limit=limit, offset=offset)

@institution_router_public.get("/{institution_id}")
def get_institution(institution_id: int):
    data = institution_interact.detail(institution_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return data

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
            "status": False, "message": f"Validation error: {str(ve)}",
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            "status": False, "message": f"Error: {str(e)}",
        })

    return {"status_code": 200, "detail": {
        "status": result, "message": "Institution created successfully",
    }}

@institution_router_private.put("/{institution_id}")
def update_institution(institution_id: int, institution: Institution):
    try:
        result = institution_interact.v_update(
            institution_id=institution_id,
            institution=institution,
            institution_contacts=institution.institution_contacts_.model_dump() if institution.institution_contacts_ else None,
            institution_quotas=institution.institution_quotas_.model_dump() if institution.institution_quotas_ else None,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail={
            "status": False, "message": f"Validation error: {str(ve)}",
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            "status": False, "message": f"Error: {str(e)}",
        })

    if not result:
        raise HTTPException(status_code=404, detail="Institution not found")

    return {"status_code": 200, "detail": {
        "status": True, "message": "Institution updated successfully",
    }}

@institution_router_private.delete("/{institution_id}")
def delete_institution(institution_id: int):
    result = institution_interact.v_delete(institution_id)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": False, "message": "Institution not found",
        })
    return {"status_code": 200, "detail": {
        "status": True, "message": "Institution deleted successfully",
    }}

