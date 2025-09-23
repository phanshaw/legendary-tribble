from sqlmodel import SQLModel, Field, Column
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy import JSON as SQLAlchemyJSON, String


class UserBase(SQLModel):
    name: str
    email: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    user_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(SQLAlchemyJSON))


class UserCreate(UserBase):
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str
    user: User


class FileRecord(SQLModel, table=True):
    __tablename__ = "files"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    path: str
    size: int
    user_id: int = Field(foreign_key="user.id")
    uploaded_at: datetime = Field(default_factory=datetime.now)
    file_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(SQLAlchemyJSON))