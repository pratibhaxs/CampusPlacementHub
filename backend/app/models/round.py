from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

VALID_DIFFICULTIES = ("easy", "medium", "hard")


class RecruitmentRound(Base):
    __tablename__ = "recruitment_rounds"

    id = Column(Integer, primary_key=True)
    experience_id = Column(Integer, ForeignKey("experiences.id"), nullable=False)

    round_number = Column(Integer, nullable=False)
    round_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), nullable=True)

    experience = relationship("Experience", back_populates="rounds")
    questions = relationship("Question", back_populates="round", cascade="all, delete-orphan")

    def to_dict(self, include_questions=False):
        data = {
            "id": self.id,
            "experience_id": self.experience_id,
            "round_number": self.round_number,
            "round_type": self.round_type,
            "description": self.description,
            "difficulty": self.difficulty,
        }
        if include_questions:
            data["questions"] = [q.to_dict() for q in self.questions]
        return data
