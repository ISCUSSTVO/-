from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Float

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default =func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default =func.now(), onupdate=func.now())

class admlist(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    usernameadm: Mapped[str] = mapped_column(String)

class accounts(Base):
    __tablename__ = 'allacc'

    description: Mapped[str] = mapped_column(String)
    gamesonaacaunt: Mapped[str] = mapped_column(primary_key = True)
    categories: Mapped[str] = mapped_column(String)
    price: Mapped[int]  = mapped_column(Float)
    acclog: Mapped[str] = mapped_column(String)
    accpass: Mapped[str] = mapped_column(String)

class backet(Base):
    __tablename__ = 'chumbacket'

    username: Mapped[str] = mapped_column(primary_key=True)
    infoacc: Mapped[str] = mapped_column(String)
