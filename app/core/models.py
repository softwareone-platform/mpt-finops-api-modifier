import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import text
from sqlmodel import Field, SQLModel


class UUIDModel(SQLModel):
    """
    A base model to include a universally unique identifier (UUID) as the primary key.
    """
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "unique": True
        },
        description="Universally unique identifier for the record."
    )


class TimestampModel(SQLModel):
    """
    A base model to add automatic timestamp fields for creation and updates.
    """
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)") # Server-side default timestamp
        },
        description="Timestamp indicating when the record was created."
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"), # Server-side default timestamp
            "onupdate": text("current_timestamp(0)"),  # noqa Automatically updates on modification
        },
        description="Timestamp indicating when the record was last updated."
    )
