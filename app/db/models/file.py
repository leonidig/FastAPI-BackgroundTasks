from .. import Base

from sqlalchemy.orm import Mapped, mapped_column


class File(Base):
    __tablename__ = "files"

    filename: Mapped[str]
    progress: Mapped[int] = mapped_column(default = 0)