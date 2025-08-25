from fastapi import APIRouter, Depends, HTTPException, Query

from internish.security import require_auth, require_role
from internship_app.schemas import Internship
from internship_app.views import internship_interact

router = APIRouter(prefix="/internships", tags=["internships"])


@router.get("/")
def list_internships(
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Skip N items"),
    current=Depends(require_auth),
):
    try:
        student_id = None
        if current["role"] == "student":
            student_id = internship_interact.get_student_id_by_email(current["email"])
        return internship_interact.list(student_id=student_id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Error: {str(e)}"})


@router.get("/{internship_id}")
def get_internship(internship_id: int, current=Depends(require_auth)):
    try:
        student_id = None
        if current["role"] == "student":
            student_id = internship_interact.get_student_id_by_email(current["email"])
        data = internship_interact.detail(internship_id, student_id=student_id)
        if data is None:
            raise HTTPException(status_code=404, detail="Internship not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Error: {str(e)}"})

@router.post("/")
def create_internship(internship: Internship, current=Depends(require_role)):
    try:
        result = internship_interact.v_create(internship, student_id=None)
        return {"status_code": 200, "detail": {"status": result, "message": "Internship created successfully"}}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Error: {str(e)}"})


@router.put("/{internship_id}")
def update_internship(internship_id: int, internship: Internship, current=Depends(require_role)):
    try:
        result = internship_interact.v_update(internship_id, internship, student_id=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Error: {str(e)}"})
    if not result:
        raise HTTPException(status_code=404, detail="Internship not found")
    return {"status_code": 200, "detail": {"status": True, "message": "Internship updated successfully"}}


@router.delete("/{internship_id}")
def delete_internship(internship_id: int, current=Depends(require_role)):
    try:
        result = internship_interact.v_delete(internship_id, student_id=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Error: {str(e)}"})
    if not result:
        raise HTTPException(status_code=404, detail="Internship not found")
    return {"status_code": 200, "detail": {"status": True, "message": "Internship deleted successfully"}}
