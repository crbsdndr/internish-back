from fastapi import APIRouter, HTTPException, Depends, Query

from internish.security import require_auth
from user_app.schemas import UserUpdate
from user_app.utils import user_utils
from user_app.views import user_interact

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_auth)],
)


@router.get("/")
def list_users(
    q: str | None = Query(None, description="Search"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Skip N items"),
):
    return user_interact.list(q=q, limit=limit, offset=offset)

@router.get("/me")
def get_current_user(current=Depends(require_auth)):
    return current

@router.get("/{id}")
def get_user_detail(id: int):
    data = user_interact.detail(id=id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return data


@router.put("/{user_id}")
def update_user(user: UserUpdate, current=Depends(require_auth)):
    if current["role"] == "student":
        raise HTTPException(status_code=403, detail="Your role can't update users")
    elif current["role"] == "supervisor" and user.role_ != "student":
        raise HTTPException(status_code=403, detail="Your role can only update student users")

    if user.password_:
        user.password_ = user_utils.password_hash(user.password_)

    try:
        result = user_interact.v_update(
            user_item=user,
            student=user.student_.model_dump() if user.student_ else None,
            supervisor=user.supervisor_.model_dump() if user.supervisor_ else None,
        )

        if result:
            return {"detail": {"status": True, "message": "User updated successfully"}}
        return {"detail": {"status": False, "message": "Apalagi sih ya ampun"}}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail={"status": False, "message": str(ve)})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"DB error: {str(e)}"})
