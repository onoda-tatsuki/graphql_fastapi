import uuid

import strawberry
from strawberry.types import Info

from src.core.dependencies import AppContext
from src.core.schemas.graphql.pages.schemas import PageQueryInput
from src.core.schemas.pydantic.paginate import PageQuery
from src.errors.exception import AppException
from src.errors.messages.error_message import ErrorMessage
from src.todos.graphql.schemas import TodoSortQueryInput
from src.todos.graphql.types import PagedTodoType, TodoType
from src.todos.repositories.todo import TodoRepository
from src.todos.schemas.todo import TodoSortQuery


@strawberry.type
class TodoQuery:
    @strawberry.field(name="todos")
    async def get_todos(
        self,
        info: Info[AppContext[TodoRepository]],
        page_query: PageQueryInput | None = None,
        sort_query: TodoSortQueryInput | None = None,
    ) -> PagedTodoType:
        todo_repo = info.context.repository
        paged_query = (
            page_query.to_pydantic() if page_query is not None else PageQuery()
        )
        sorted_query = (
            sort_query.to_pydantic() if sort_query is not None else TodoSortQuery()
        )

        todos, page_mage = await todo_repo.get_paged_context(
            page_query=paged_query, sort_query=sorted_query
        )

        return PagedTodoType.from_model(todos, page_mage)

    @strawberry.field(name="todo")
    async def get_todo_by_id(
        self, info: Info[AppContext[TodoRepository]], id: uuid.UUID
    ) -> TodoType:
        todo_repo: TodoRepository = info.context.repository
        todo = await todo_repo.get_context_by_id(id)

        if todo is None:
            raise AppException(error=ErrorMessage.NOT_FOUND("TODO"))

        return TodoType.from_model(todo)
