import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Identidad Global. No sujeta a RLS directamente."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Roles del Sistema y Custom. Sujetos a RLS."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    # Si organization_id es NULL, es un "System Role" creado por ti.
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    # Permisos en formato JSON para máxima flexibilidad inicial
    permissions: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, server_default="{}"
    )


class Member(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Vínculo Persona <-> Organización. Sujeto a RLS."""

    __tablename__ = "members"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    # Perfil específico del usuario en esta Organización
    profile_data: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, server_default="{}"
    )
