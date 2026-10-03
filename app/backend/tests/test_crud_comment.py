import uuid

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
