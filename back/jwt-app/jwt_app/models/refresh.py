from datetime import datetime

from db import Base
from sqlalchemy.orm import Mapped


class RefreshKey(Base):
    exp: Mapped[datetime]
    refresh: Mapped[str]
    sub: Mapped[str]

    def __str__(self):
        return f"{self.__class__.__name__}, id={self.id}, exp={self.exp}, refresh={self.exp}, sub={self.sub}"

    def __repr__(self):
        return str(self)
