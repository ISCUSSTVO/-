from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Float, func

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default = func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default = func.now() , onupdate= func.now())

class Admlist(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    usernameadm: Mapped[str] = mapped_column(String)

class Accounts(Base):
    __tablename__ = 'allacc'

    name: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String)
    gamesonaacaunt: Mapped[str] = mapped_column(String)
    categories: Mapped[str] = mapped_column(String)
    price: Mapped[int]  = mapped_column(Float(500))
    image: Mapped[str] = mapped_column(String)
    acclog: Mapped[str] = mapped_column(String)
    accpass: Mapped[str] = mapped_column(String)
    accmail: Mapped[str] = mapped_column(String)
    im4p: Mapped[str] = mapped_column(String)

class Backet(Base):
    __tablename__ = 'chumbacket'
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    username: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    infoacc: Mapped[str] = mapped_column(String)
