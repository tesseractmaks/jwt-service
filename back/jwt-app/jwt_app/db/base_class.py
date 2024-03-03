import typing as T

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls):
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    async def get_or_create(
        cls, session: AsyncSession, defaults=None, commit=True, **kwargs
    ) -> T.Tuple[T.AnyStr, bool]:
        predicates = [getattr(cls, k) == v for k, v in kwargs.items()]
        instance = await session.scalar(sa.select(cls).where(*predicates))
        if instance:
            return instance, False
        defaults = defaults or {}
        instance_kwargs = kwargs | defaults
        instance = cls(**instance_kwargs)
        session.add(instance)
        if commit:
            await session.commit()
        return instance, True
