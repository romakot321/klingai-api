from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class TaskDB(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str | None]
    status: Mapped[str | None]
    user_id: Mapped[str]
    app_id: Mapped[str]
    prompt: Mapped[str | None]
    webhook_url: Mapped[str | None]
    result: Mapped[str | None]
    error: Mapped[str | None]
