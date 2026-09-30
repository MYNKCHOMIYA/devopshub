# DevOpsHub v0.1 Data Model

## 1. Data Model

### User

- id
- username
- email
- password_hash
- name
- phone
- created_at
- updated_at
- deleted_at

### Project

- id
- owner_id
- name
- description
- status
- priority
- start_date
- due_date
- created_at
- updated_at
- deleted_at

### Task

- id
- project_id
- created_by_id
- assignee_id
- title
- description
- status
- priority
- due_date
- created_at
- updated_at
- deleted_at

### Comment

- id
- task_id
- author_id
- content
- created_at
- updated_at

### Activity

- id
- project_id
- task_id
- actor_id
- action
- metadata
- created_at


## 2. Model Decisions

### Project Owner

Exactly one owner in v0.1.

`owner_id` is required.

### Task Assignee

Every task has an assignee in v0.1.

`assignee_id` is required.

### Task Creator

Every task has a creator.

`created_by_id` is required because the creator and assignee can be different users.

### Task Status

Allowed values:

- TODO
- IN_PROGRESS
- DONE

### Project Status

Allowed values:

- TODO
- IN_PROGRESS
- DONE

### Priority

Allowed values:

- LOW
- MEDIUM
- HIGH

Priority applies to both Projects and Tasks.

### Activity

`project_id` is required.

`task_id` is nullable because project-level events can exist without a specific task.

### Activity Metadata

Activity metadata uses structured JSONB data.


## 3. Relationship Decisions

### 3.1 User → Project

One user can own many projects.

Every project has exactly one owner.

### 3.2 Project → Task

One project can have many tasks.

Every task belongs to exactly one project.

### 3.3 User → Task

A user can create many tasks.

A user can be assigned many tasks.

Every task has one creator and one assignee.

### 3.4 Task → Comment

A task can have many comments.

Every comment belongs to exactly one task and one author.

### 3.5 Project → Activity

A project can have many activities.

Every activity belongs to exactly one project.

### 3.6 Task → Activity

A task can have many activities.

An activity may belong to a specific task or may be a project-level activity.

`Activity.task_id` is nullable.

### 3.7 User → Activity

A user can generate many activities.

Every activity has one actor.

The actor is the user who performed the action.


## 4. Delete Behavior

### Project Deletion

Decision:

Projects are soft deleted using `deleted_at`.

Tasks, comments, and activities are preserved.

Reason:

Activity history must remain available for auditing and historical tracking.

Soft deletion also preserves the relationships between projects, tasks, and activities.

### Task Deletion

Decision:

Tasks are soft deleted using `deleted_at`.

Comments and activities are preserved.

Reason:

Activity history must remain available for auditing and historical tracking.

Soft deletion preserves the task relationship referenced by activity records.

### User Deletion

Decision:

Users are soft deleted using `deleted_at`.

The user record and historical relationships are preserved.

Reason:

Users are referenced by projects, tasks, comments, and activities.

Soft deletion preserves historical integrity and audit history.

Soft-deleted users cannot:

- authenticate
- be assigned new tasks
- create new projects

Existing historical relationships remain intact.


## 5. Database Constraints

### 5.1 Primary Keys

All tables use UUID primary keys.

Every primary key must be:

- unique
- NOT NULL

### 5.2 Foreign Keys

- Project.owner_id → User.id
- Task.project_id → Project.id
- Task.created_by_id → User.id
- Task.assignee_id → User.id
- Comment.task_id → Task.id
- Comment.author_id → User.id
- Activity.project_id → Project.id
- Activity.task_id → Task.id
- Activity.actor_id → User.id

Foreign keys enforce referential integrity.


## 6. Required Fields

### User

Required:

- id
- username
- email
- password_hash
- name
- created_at
- updated_at

Nullable:

- phone
- deleted_at

### Project

Required:

- id
- owner_id
- name
- status
- priority
- created_at
- updated_at

Nullable:

- description
- start_date
- due_date
- deleted_at

### Task

Required:

- id
- project_id
- created_by_id
- assignee_id
- title
- status
- priority
- created_at
- updated_at

Nullable:

- description
- due_date
- deleted_at

### Comment

Required:

- id
- task_id
- author_id
- content
- created_at
- updated_at

### Activity

Required:

- id
- project_id
- actor_id
- action
- metadata
- created_at

Nullable:

- task_id


## 7. Unique Constraints

The following fields must be unique:

- User.username
- User.email

Both fields are required.

Deleted users retain their username and email.

A new account cannot reuse the username or email of a soft-deleted account in v0.1.


## 8. Status Constraints

### Project Status

Allowed values:

- TODO
- IN_PROGRESS
- DONE

### Task Status

Allowed values:

- TODO
- IN_PROGRESS
- DONE

The database/application must reject values outside these allowed states.


## 9. Priority Constraints

### Project Priority

Allowed values:

- LOW
- MEDIUM
- HIGH

### Task Priority

Allowed values:

- LOW
- MEDIUM
- HIGH

The database/application must reject values outside these allowed priorities.


## 10. Activity

### Activity Action

`action` is required.

Activity actions represent meaningful events performed by users or generated by the system.

Examples:

- USER_CREATED
- PROJECT_CREATED
- PROJECT_UPDATED
- PROJECT_DELETED
- TASK_CREATED
- TASK_UPDATED
- TASK_STATUS_CHANGED
- TASK_ASSIGNED
- TASK_COMPLETED
- TASK_DELETED
- COMMENT_CREATED
- COMMENT_UPDATED
- COMMENT_DELETED

The exact action vocabulary will be centralized in the application layer.

### Activity Metadata

`metadata` uses PostgreSQL JSONB.

Example:

```json
{
  "old_status": "TODO",
  "new_status": "IN_PROGRESS"
}

The metadata structure can vary depending on the activity type.

## 11. Indexes

Indexes will be created for frequently queried relationship and lookup fields.

### User

- username
- email

`username` and `email` are already indexed by their UNIQUE constraints in PostgreSQL.

### Project

- owner_id

### Task

- project_id
- created_by_id
- assignee_id

### Comment

- task_id
- author_id

### Activity

- project_id
- task_id
- actor_id
- created_at

### Composite Activity Index

- Activity(project_id, created_at)

This supports common queries such as retrieving a project's activity history ordered by newest activity first.

## 12. Delete Policy

### User

Soft delete using `deleted_at`.

Historical relationships are preserved.

### Project

Soft delete using `deleted_at`.

Tasks, comments, and activities are preserved.

### Task

Soft delete using `deleted_at`.

Comments and activities are preserved.

### Comment

Hard delete.

Deleting a comment does not delete the associated task or activity records.

### Activity

Activity records are preserved as audit/history records.

Activity records are not deleted when their related User, Project, or Task is soft deleted.

## 13. Soft Delete Rules

The following entities support soft deletion:

- User
- Project
- Task

They use:

`deleted_at`

Behavior:

- `deleted_at = NULL` → Active
- `deleted_at = timestamp` → Soft deleted

Normal application queries should only return records where:

`deleted_at IS NULL`

Historical and administrative queries may explicitly include soft-deleted records.

## 14. Timestamp Rules

All entities use timestamps to track lifecycle changes.

### Creation

`created_at`

### Last Modification

`updated_at`

### Soft Deletion

`deleted_at`

`deleted_at` is only populated when the entity is soft deleted.

## 15. v0.1 Design Principles

The v0.1 database design follows these principles:

1. Referential integrity is enforced through foreign keys.
2. Required business data uses NOT NULL constraints.
3. Usernames and email addresses are unique.
4. Project and task status values are controlled.
5. Project and task priority values are controlled.
6. Activity metadata uses PostgreSQL JSONB.
7. Frequently queried relationships are indexed.
8. Users, projects, and tasks use soft deletion.
9. Activity history is preserved.
10. Derived values such as project progress are calculated from task data instead of being stored redundantly.
11. Passwords are never stored directly; only password hashes are stored.
12. The v0.1 model favors simplicity while leaving room for future production features such as project membership, role-based access control, immutable audit storage, and advanced ownership management.
