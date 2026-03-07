from pydantic import BaseModel, ConfigDict, EmailStr, Field

from curso_dunossauro.models import TodoState


class Message(BaseModel):
    message: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int
    model_config = ConfigDict(from_attributes=True)  # chave padrão do pydantic


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserDB(UserSchema):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    # ge = greater equal (>=)
    limit: int = Field(ge=0, default=10)
    offset: int = Field(ge=0, default=0)


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState = Field(default=TodoState.TODO)


class TodoPublic(TodoSchema):
    id: int


class FilterTodo(FilterPage):
    title: str | None = Field(default=None, min_length=3, max_length=15)
    description: str | None = None
    state: TodoState | None = None


class TodoList(BaseModel):
    list[TodoPublic]