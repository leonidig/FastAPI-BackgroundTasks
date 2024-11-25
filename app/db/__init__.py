from sqlalchemy.orm import (sessionmaker,
                            Mapped,
                            mapped_column,
                            DeclarativeBase)
from sqlalchemy import create_engine


ENGINE = create_engine("sqlite:///files.db")
SESSION = sessionmaker(bind=ENGINE)


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True)


def up():
    Base.metadata.create_all(ENGINE)


def drop():
    Base.metadata.drop_all(ENGINE)


def migrate():
    drop()
    up()


def get_session():
    with SESSION.begin() as session:
        yield session


from .models import File

migrate()