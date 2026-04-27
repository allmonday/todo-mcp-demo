"""SQLModel entity definitions for the todo application."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, select

from sqlmodel_graphql import mutation, query


class BaseEntity(SQLModel):
    """Base class for all todo entities."""

    pass


class Comment(BaseEntity, table=True):
    """Comment entity."""

    id: int | None = Field(default=None, primary_key=True)
    todo_id: int = Field(foreign_key="todo.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationship: Comment belongs to Todo
    todo: Optional["Todo"] = Relationship(back_populates="comments")


    @query
    async def get_comments(cls, limit: int = 100) -> list["Comment"]:
        """Get all comments with optional limit."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = select(cls).order_by(cls.created_at.desc()).limit(limit)
            result = await session.exec(stmt)
            return list(result.all())

    @query
    async def get_comment(cls, id: int) -> Optional["Comment"]:
        """Get a comment by ID."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = select(cls).where(cls.id == id)
            result = await session.exec(stmt)
            return result.first()

    @query
    async def get_comments_by_todo(
        cls, todo_id: int, limit: int = 100
    ) -> list["Comment"]:
        """Get comments by todo ID."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = (
                select(cls)
                .where(cls.todo_id == todo_id)
                .order_by(cls.created_at.desc())
                .limit(limit)
            )
            result = await session.exec(stmt)
            return list(result.all())

    @mutation
    async def create_comment(cls, todo_id: int, content: str) -> "Comment":
        """Add a comment to a todo."""
        from todo.database import async_session

        async with async_session() as session:
            # Check if todo exists
            todo_result = await session.exec(select(Todo).where(Todo.id == todo_id))
            todo = todo_result.first()
            if not todo:
                raise ValueError(f"Todo with id {todo_id} not found")

            comment = cls(todo_id=todo_id, content=content)
            session.add(comment)
            await session.commit()
            await session.refresh(comment)
            return comment

    @mutation
    async def delete_comment(cls, id: int) -> bool:
        """Delete a comment by ID."""
        from todo.database import async_session

        async with async_session() as session:
            existing = await session.exec(select(cls).where(cls.id == id))
            comment = existing.first()
            if comment:
                await session.delete(comment)
                await session.commit()
                return True
            return False


class Todo(BaseEntity, table=True):
    """Todo entity."""

    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationship: Todo has many comments
    comments: list["Comment"] = Relationship(
        back_populates="todo",
        cascade_delete=True,
        sa_relationship_kwargs={"order_by": "Comment.created_at.desc()"},
    )

    @query
    async def get_todos(
        cls, limit: int = 100, done: bool | None = None
    ) -> list["Todo"]:
        """Get all todos with optional limit and done status filter."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = select(cls).order_by(cls.created_at.desc()).limit(limit)
            if done is not None:
                stmt = stmt.where(cls.done == done)
            result = await session.exec(stmt)
            return list(result.all())

    @query
    async def get_todo(cls, id: int) -> Optional["Todo"]:
        """Get a todo by ID."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = select(cls).where(cls.id == id)
            result = await session.exec(stmt)
            return result.first()

    @mutation
    async def create_todo(cls, title: str) -> "Todo":
        """Add a new todo."""
        from todo.database import async_session

        async with async_session() as session:
            todo = cls(title=title)
            session.add(todo)
            await session.commit()
            await session.refresh(todo)
            return todo

    @mutation
    async def create_todo_with_comments(
        cls, title: str, comments: list[str] = []
    ) -> "Todo":
        """Add a new todo with optional comments."""
        from todo.database import async_session

        async with async_session() as session:
            # Create todo
            todo = cls(title=title)
            session.add(todo)
            await session.commit()
            await session.refresh(todo)

            # Create comments
            for content in comments:
                comment = Comment(todo_id=todo.id, content=content)
                session.add(comment)
            await session.commit()
            await session.refresh(todo)
            return todo

    @mutation
    async def delete_todo(cls, id: int) -> bool:
        """Delete a todo by ID (cascades to comments)."""
        from todo.database import async_session

        async with async_session() as session:
            existing = await session.exec(select(cls).where(cls.id == id))
            todo = existing.first()
            if todo:
                await session.delete(todo)
                await session.commit()
                return True
            return False

    @mutation
    async def set_todo_done(cls, id: int, done: bool) -> "Todo":
        """Mark a todo as done or undone."""
        from todo.database import async_session

        async with async_session() as session:
            existing = await session.exec(select(cls).where(cls.id == id))
            todo = existing.first()
            if not todo:
                raise ValueError(f"Todo with id {id} not found")

            todo.done = done
            session.add(todo)
            await session.commit()
            await session.refresh(todo)
            return todo
