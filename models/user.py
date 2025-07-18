from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    characters: Mapped[list["Character"]] = relationship(back_populates="user")
    messages: Mapped[list["Message"]] = relationship(back_populates="user") 