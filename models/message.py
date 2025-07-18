import datetime
from sqlalchemy import Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'))
    
    role: Mapped[str] = mapped_column(Text)  # "user" or "model"
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="messages")
    character: Mapped["Character"] = relationship(back_populates="messages") 