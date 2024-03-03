from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    password: str
    is_active: bool


class UserProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    id: int


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str


class UserCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    password: str
    is_active: bool


class UserUpdateSchema(UserSchema): ...


class UserUpdatePartialSchema(UserSchema):
    model_config = ConfigDict(from_attributes=True)
    email: str | None = None
    password: str | None = None
    is_active: bool | None = None
    id: int | None = None


class UserInDB(UserSchema):
    model_config = ConfigDict(from_attributes=True)
    password: str
