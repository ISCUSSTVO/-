from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime,  Text, func

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default = func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default = func.now() , onupdate= func.now())

##################Дтаблица админов################################################################
class Admins(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    usernameadm: Mapped[str] = mapped_column(String)


##################таблица аккаунтов################################################################
class Accounts(Base):
    __tablename__ = 'allacc'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    description: Mapped[str] = mapped_column(String)
    gamesonaacaunt: Mapped[str] = mapped_column(String)
    categories: Mapped[str] = mapped_column(String)
    price: Mapped[int]  = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String)
    acclog: Mapped[str] = mapped_column(String)
    accpass: Mapped[str] = mapped_column(String)
    accmail: Mapped[str] = mapped_column(String)
    imap: Mapped[str] = mapped_column(String)

##################таблица банеры ################################################################
class Banner(Base):
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)