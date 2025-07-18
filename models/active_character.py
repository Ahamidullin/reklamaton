from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class ActiveCharacter(Base):
    __tablename__ = 'active_characters'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'))

    user: Mapped["User"] = relationship()
    character: Mapped["Character"] = relationship() 