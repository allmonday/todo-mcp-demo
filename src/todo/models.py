"""SQLModel entity definitions for the todo application."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel, select

from sqlmodel_graphql import QueryMeta, mutation, query

if TYPE_CHECKING:
    pass


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

    @query(name="comments", description="Get all comments with optional limit")
    async def get_all(
        cls, limit: int = 100, query_meta: QueryMeta | None = None
    ) -> list["Comment"]:
        """Get all comments with optional limit."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = select(cls).order_by(cls.created_at.desc()).limit(limit)
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return list(result.all())

    @query(name="comment", description="Get a comment by ID")
    async def get_by_id(
        cls, id: int, query_meta: QueryMeta | None = None
    ) -> Optional["Comment"]:
        """Get a comment by ID."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = select(cls).where(cls.id == id)
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return result.first()

    @query(name="comments_by_todo", description="Get comments by todo ID")
    async def get_by_todo(
        cls, todo_id: int, limit: int = 100, query_meta: QueryMeta | None = None
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
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return list(result.all())

    @mutation(name="comment_add", description="Add a comment to a todo")
    async def create(
        cls, todo_id: int, content: str, query_meta: QueryMeta | None = None
    ) -> "Comment":
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

            # Re-query with query_meta to load relationships
            stmt = select(cls).where(cls.id == comment.id)
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return result.first()

    @mutation(name="comment_delete", description="Delete a comment")
    async def delete(cls, id: int) -> bool:
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
        back_populates="todo", cascade_delete=True
    )

    @query(name="todos", description="Get all todos with optional limit")
    async def get_all(
        cls, limit: int = 100, query_meta: QueryMeta | None = None
    ) -> list["Todo"]:
        """Get all todos with optional limit."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = select(cls).order_by(cls.created_at.desc()).limit(limit)
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return list(result.all())

    @query(name="todo", description="Get a todo by ID")
    async def get_by_id(
        cls, id: int, query_meta: QueryMeta | None = None
    ) -> Optional["Todo"]:
        """Get a todo by ID."""
        from todo.database import async_session

        async with async_session() as session:
            stmt = select(cls).where(cls.id == id)
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return result.first()

    @mutation(name="todo_add", description="Add a new todo")
    async def create(cls, title: str, query_meta: QueryMeta | None = None) -> "Todo":
        """Add a new todo."""
        from todo.database import async_session

        async with async_session() as session:
            todo = cls(title=title)
            session.add(todo)
            await session.commit()
            await session.refresh(todo)

            # Re-query with query_meta to load relationships
            stmt = select(cls).where(cls.id == todo.id)
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return result.first()

    @mutation(name="todo_add_with_comments", description="Add a new todo with comments")
    async def create_with_comments(
        cls, title: str, query_meta: QueryMeta | None = None, comments: list[str] = []
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

            # Re-query with query_meta to load relationships
            stmt = select(cls).where(cls.id == todo.id)
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return result.first()

    @mutation(name="todo_delete", description="Delete a todo")
    async def delete(cls, id: int) -> bool:
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

    @mutation(name="todo_done", description="Mark a todo as done/undone")
    async def set_done(cls, id: int, done: bool, query_meta: QueryMeta | None = None) -> "Todo":
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

            # Re-query with query_meta to load relationships
            stmt = select(cls).where(cls.id == todo.id)
            if query_meta:
                stmt = stmt.options(*query_meta.to_options(cls))
            result = await session.exec(stmt)
            return result.first()
