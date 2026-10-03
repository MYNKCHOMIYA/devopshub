import uuid
import pytest

from sqlalchemy import delete,select

from app.core.security import hash_password
from app.crud.comment import (
    create_comment,
    get_comment_by_id,
    get_comments_for_task,
    delete_comment,
)

from app.db.session import SessionLocal
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate
from app.crud.activity import get_activities_for_task
from app.models.activity import Activity
from app.models.comment import Comment


def test_create_comment():
    db = SessionLocal()

    user = User(
        username=f"comment_{uuid.uuid4().hex[:8]}",
        email=f"comment_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Comment User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Comment Project",
        description="Project for comment CRUD testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    project_id = project.id

    task = Task(
        project_id=project_id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment Task",
        description="Task for comment CRUD testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    comment_data = CommentCreate(
        task_id=task_id,
        author_id=user_id,
        content="This is the first DevOpsHub comment.",
    )

    comment = create_comment(db, comment_data)

    assert comment.id is not None
    assert comment.task_id == task_id
    assert comment.author_id == user_id
    assert comment.content == "This is the first DevOpsHub comment."
    assert comment.created_at is not None
    assert comment.updated_at is not None

    db.close()

def test_get_comment_by_id():
    db = SessionLocal()

    user = User(
        username=f"commentget_{uuid.uuid4().hex[:8]}",
        email=f"commentget_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Comment Get User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Comment Get Project",
        description="Project for comment get testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment Get Task",
        description="Task for comment get testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    comment = create_comment(
        db,
        CommentCreate(
            task_id=task.id,
            author_id=user_id,
            content="Find this comment.",
        ),
    )

    found_comment = get_comment_by_id(db, comment.id)

    assert found_comment is not None
    assert found_comment.id == comment.id
    assert found_comment.task_id == task.id
    assert found_comment.author_id == user_id
    assert found_comment.content == "Find this comment."

    db.close()


def test_get_comments_for_task():
    db = SessionLocal()

    user = User(
        username=f"commentlist_{uuid.uuid4().hex[:8]}",
        email=f"commentlist_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Comment List User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Comment List Project",
        description="Project for comment list testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task_1 = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment List Task One",
        description="First task.",
        status="TODO",
        priority="MEDIUM",
    )

    task_2 = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment List Task Two",
        description="Second task.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add_all([task_1, task_2])
    db.commit()
    db.refresh(task_1)
    db.refresh(task_2)

    comment_1 = create_comment(
        db,
        CommentCreate(
            task_id=task_1.id,
            author_id=user_id,
            content="First comment.",
        ),
    )

    comment_2 = create_comment(
        db,
        CommentCreate(
            task_id=task_1.id,
            author_id=user_id,
            content="Second comment.",
        ),
    )

    comment_3 = create_comment(
        db,
        CommentCreate(
            task_id=task_2.id,
            author_id=user_id,
            content="Comment for another task.",
        ),
    )

    comments = get_comments_for_task(db, task_1.id)

    assert len(comments) == 2

    comment_ids = {comment.id for comment in comments}

    assert comment_1.id in comment_ids
    assert comment_2.id in comment_ids
    assert comment_3.id not in comment_ids

    assert comments[0].content == "First comment."
    assert comments[1].content == "Second comment."

    db.close()



def test_delete_comment():
    db = SessionLocal()

    user = User(
        username=f"commentdelete_{uuid.uuid4().hex[:8]}",
        email=f"commentdelete_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Comment Delete User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Comment Delete Project",
        description="Project for comment delete testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment Delete Task",
        description="Task for comment delete testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    comment = create_comment(
        db,
        CommentCreate(
            task_id=task.id,
            author_id=user_id,
            content="This comment will be deleted.",
        ),
    )

    comment_id = comment.id

    delete_comment(db, comment)

    deleted_comment = get_comment_by_id(db, comment_id)

    assert deleted_comment is None

    db.close()


def test_create_comment_records_activity():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None
    comment = None

    try:
        user = User(
            username=f"comment_activity_{unique_value}",
            email=f"comment_activity_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Comment Activity User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = Project(
            owner_id=user.id,
            name="Comment Activity Project",
            description="Project for COMMENT_CREATED audit testing.",
            status="TODO",
            priority="MEDIUM",
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        task = Task(
            project_id=project.id,
            created_by_id=user.id,
            assignee_id=user.id,
            title="Comment Activity Task",
            description="Task for COMMENT_CREATED audit testing.",
            status="TODO",
            priority="MEDIUM",
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        comment = create_comment(
            db,
            CommentCreate(
                task_id=task.id,
                author_id=user.id,
                content="Audit test comment.",
            ),
        )

        activities = get_activities_for_task(
            db,
            task.id,
        )

        assert len(activities) == 1

        activity = activities[0]

        assert activity.project_id == project.id
        assert activity.task_id == task.id
        assert activity.actor_id == user.id
        assert activity.action == "COMMENT_CREATED"
        assert activity.activity_metadata == {
            "content": "Audit test comment.",
        }
        assert activity.created_at is not None

    finally:
        if comment is not None:
            db.delete(comment)
            db.commit()

        if task is not None:
            db.execute(
        delete(Activity).where(
            Activity.task_id == task.id
        )
        )
        db.delete(task)
        db.commit()

        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)
            db.commit()

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_create_comment_rolls_back_when_activity_fails(monkeypatch):
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None
    captured = {}

    try:
        user = User(
            username=f"comment_rollback_{unique_value}",
            email=f"comment_rollback_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Comment Rollback User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Create test project directly so this test only focuses
        # on the Comment transaction.
        project = Project(
            owner_id=user.id,
            name="Comment Rollback Project",
            status="TODO",
            priority="MEDIUM",
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        task = Task(
            project_id=project.id,
            created_by_id=user.id,
            assignee_id=user.id,
            title="Comment Rollback Task",
            status="TODO",
            priority="MEDIUM",
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        def fail_record_activity(db, activity_data):
            # create_comment() has already flushed the Comment.
            # Querying here lets us capture the uncommitted Comment ID.
            comment_row = db.scalar(
                select(Comment).where(
                    Comment.task_id == activity_data.task_id,
                    Comment.author_id == activity_data.actor_id,
                    Comment.content == "Rollback Test Comment",
                )
            )

            assert comment_row is not None

            captured["comment_id"] = comment_row.id

            raise RuntimeError("Simulated comment activity failure")

        monkeypatch.setattr(
            "app.crud.activity.record_activity",
            fail_record_activity,
        )

        comment_data = CommentCreate(
            task_id=task.id,
            author_id=user.id,
            content="Rollback Test Comment",
        )

        with pytest.raises(
            RuntimeError,
            match="Simulated comment activity failure",
        ):
            create_comment(db, comment_data)

        # The Comment was flushed but never committed.
        db.rollback()

        comment_id = captured["comment_id"]

        # The Comment must not exist after rollback.
        assert db.get(Comment, comment_id) is None

        # No COMMENT_CREATED Activity should exist.
        activities = get_activities_for_task(
            db,
            task.id,
        )

        assert activities == []



    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)
            db.commit()

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()
