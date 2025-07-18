from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Character(Base):
    __tablename__ = 'characters'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    avatar_file_id: Mapped[str] = mapped_column(String, nullable=True)
    is_premade: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    user: Mapped["User"] = relationship(back_populates="characters")
    messages: Mapped[list["Message"]] = relationship(back_populates="character")

    # For constructor-based creation
    archetype: Mapped[str] = mapped_column(String, nullable=True)
    communication_style: Mapped[str] = mapped_column(String, nullable=True)
    sarcasm_level: Mapped[int] = mapped_column(Integer, nullable=True)
    humor_level: Mapped[int] = mapped_column(Integer, nullable=True)
    flirt_level: Mapped[int] = mapped_column(Integer, nullable=True)
    unpredictability_level: Mapped[int] = mapped_column(Integer, nullable=True)
    has_black_humor: Mapped[bool] = mapped_column(Boolean, nullable=True) 