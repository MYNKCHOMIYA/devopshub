from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.task import Task
from app.schemas.activity import ActivityCreate
from app.schemas.comment import CommentCreate


def create_comment(
    db: Session,
    comment_data: CommentCreate,
) -> Comment:
    comment = Comment(
        task_id=comment_data.task_id,
        author_id=comment_data.author_id,
        content=comment_data.content,
    )

    db.add(comment)

    # Flush the Comment INSERT without committing.
    # This makes the comment UUID available inside the transaction.
    db.flush()

    # Activity requires project_id, but Comment only stores task_id.
    # Resolve the parent project through the Task.
    task = db.get(Task, comment.task_id)

    if task is None:
        raise ValueError("Task not found for comment.")

    from app.crud.activity import record_activity

    record_activity(
        db,
        ActivityCreate(
            project_id=task.project_id,
            task_id=comment.task_id,
            actor_id=comment.author_id,
            action="COMMENT_CREATED",
            metadata={
                "content": comment.content,
            },
        ),
    )

    db.commit()
    db.refresh(comment)

    return comment




def get_comment_by_id(
    db: Session,
    comment_id: UUID,
) -> Comment | None:
    statement = select(Comment).where(
        Comment.id == comment_id,
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def get_comments_for_task(
    db: Session,
    task_id: UUID,
) -> list[Comment]:
    statement = (
        select(Comment)
        .where(Comment.task_id == task_id)
        .order_by(Comment.created_at)
    )

    result = db.execute(statement)

    return list(result.scalars().all())


def delete_comment(
    db: Session,
    comment: Comment,
) -> None:
    db.delete(comment)
    db.commit()
