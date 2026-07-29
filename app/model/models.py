import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.core.database import Base


class UserJWT(Base):
    __tablename__:ClassVar[str] = "users"
    __table_args__:ClassVar[dict] = {"schema": "course"}
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("uuid_generate_v4()")
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    

class PostJWT(Base):  
    __tablename__:ClassVar[str] = "posts"
    __table_args__:ClassVar[dict] = {"schema": "course"}

    id = Column(BigInteger, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
        )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "course.users.id",
            ondelete="CASCADE"),
        nullable=False
        )

    owner = relationship("UserJWT")


class VoteJWT(Base):
    __tablename__:ClassVar[str] = "votes"
    __table_args__:ClassVar[dict] = {"schema": "course"}

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "course.users.id",
            ondelete="CASCADE"),
        primary_key=True
        )
    post_id = Column(
        BigInteger,
        ForeignKey(
            "course.posts.id",
            ondelete="CASCADE"),
        primary_key=True
        )
    