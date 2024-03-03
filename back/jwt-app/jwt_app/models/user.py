from db import Base
from sqlalchemy.orm import Mapped


class User(Base):
    email: Mapped[str]
    password: Mapped[str]
    is_active: Mapped[bool]

    def __str__(self):
        return f"{self.email}"

    def __repr__(self):
        return str(self)
