
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class MCQAttempt(Base):
    __tablename__ = "mcq_attempts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    
    skill: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    total_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    correct_answers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    incorrect_answers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unanswered: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    score_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
