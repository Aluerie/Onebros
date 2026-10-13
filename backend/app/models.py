import datetime as dt
import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

#############################################################################################################################
# SOME UTILS
#############################################################################################################################


def get_datetime_utc() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


#############################################################################################################################
# SOME MODEL CONSTANTS
#############################################################################################################################


TEXT_MIN_LENGTH = 1
SHORT_TEXT_MAX_LENGTH = 255  # email, username, full name, short description
LONG_TEXT_MAX_LENGTH = 2000  # long description
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


#############################################################################################################################
# TEMPLATE MODELS
#############################################################################################################################


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=SHORT_TEXT_MAX_LENGTH)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=SHORT_TEXT_MAX_LENGTH)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=SHORT_TEXT_MAX_LENGTH)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    full_name: str | None = Field(default=None, max_length=SHORT_TEXT_MAX_LENGTH)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=SHORT_TEXT_MAX_LENGTH)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=SHORT_TEXT_MAX_LENGTH)
    password: str | None = Field(default=None, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=SHORT_TEXT_MAX_LENGTH)
    email: EmailStr | None = Field(default=None, max_length=SHORT_TEXT_MAX_LENGTH)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: dt.datetime | None = Field(default_factory=get_datetime_utc)
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: dt.datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=TEXT_MIN_LENGTH, max_length=SHORT_TEXT_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=SHORT_TEXT_MAX_LENGTH)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=TEXT_MIN_LENGTH, max_length=SHORT_TEXT_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=SHORT_TEXT_MAX_LENGTH)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: dt.datetime | None = Field(default_factory=get_datetime_utc)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: dt.datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"  # ruff: ignore[hardcoded-password-string]


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
