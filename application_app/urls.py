from fastapi import APIRouter, Depends, HTTPException, Query

from internish.security import require_auth
from application_app.schemas import Application
from application_app.views import application_interact

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/")
def list_applications(
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Skip N items"),
    current=Depends(require_auth),
):
    student_id = None
    if current["role"] == "student":
        student_id = application_interact.get_student_id_by_email(current["email"])
    return application_interact.list(student_id=student_id, limit=limit, offset=offset)


@router.get("/{application_id}")
def get_application(application_id: int, current=Depends(require_auth)):
    student_id = None
    if current["role"] == "student":
        student_id = application_interact.get_student_id_by_email(current["email"])
    data = application_interact.detail(application_id, student_id=student_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return data


@router.post("/")
def create_application(application: Application, current=Depends(require_auth)):
    if current["role"] == "student":
        student_id = application_interact.get_student_id_by_email(current["email"])
        if student_id is None:
            raise HTTPException(status_code=404, detail="Student not found")
        application.student_id_ = student_id
        application.status_ = "under_review"
    else:
        if application.student_id_ is None:
            raise HTTPException(status_code=400, detail="student_id_ is required")
        if application.status_ is None:
            application.status_ = "pending"
    try:
        result = application_interact.v_create(application)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Error: {str(e)}"})
    return {"status_code": 200, "detail": {"status": result, "message": "Application created successfully"}}


@router.put("/{application_id}")
def update_application(application_id: int, application: Application, current=Depends(require_auth)):
    student_id = None
    if current["role"] == "student":
        student_id = application_interact.get_student_id_by_email(current["email"])
        application.status_ = None
    else:
        if application.status_ is None:
            application.status_ = "pending"
    try:
        result = application_interact.v_update(application_id, application, student_id=student_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Error: {str(e)}"})
    if not result:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"status_code": 200, "detail": {"status": True, "message": "Application updated successfully"}}


@router.delete("/{application_id}")
def delete_application(application_id: int, current=Depends(require_auth)):
    student_id = None
    if current["role"] == "student":
        student_id = application_interact.get_student_id_by_email(current["email"])
    result = application_interact.v_delete(application_id, student_id=student_id)
    if not result:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"status_code": 200, "detail": {"status": True, "message": "Application deleted successfully"}}
