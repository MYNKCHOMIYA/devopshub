from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.comment import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_comments_for_task,
)
from app.db.session import get_db
from app.schemas.comment import CommentCreate, CommentResponse


router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)


@router.post(
    "",
    response_model=CommentResponse,
    status_code=201,
)
def create_comment_endpoint(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
):
    return create_comment(db, comment_data)


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
def get_comment_endpoint(
    comment_id: UUID,
    db: Session = Depends(get_db),
):
    comment = get_comment_by_id(db, comment_id)

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found.",
        )

    return comment


@router.get(
    "/task/{task_id}",
    response_model=list[CommentResponse],
)
def get_task_comments_endpoint(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    return get_comments_for_task(db, task_id)


@router.delete(
    "/{comment_id}",
    status_code=204,
)
def delete_comment_endpoint(
    comment_id: UUID,
    db: Session = Depends(get_db),
):
    comment = get_comment_by_id(db, comment_id)

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found.",
        )

    delete_comment(db, comment)

    return None
