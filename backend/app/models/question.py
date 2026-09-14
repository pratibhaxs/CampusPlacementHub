from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

VALID_CATEGORIES = (
    "Aptitude", "Coding", "DSA", "OOP", "DBMS",
    "Operating Systems", "Computer Networks",
    "Python", "Java", "JavaScript", "HR", "Behavioral", "Other",
)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey("recruitment_rounds.id"), nullable=False)

    question_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=True)

    round = relationship("RecruitmentRound", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "round_id": self.round_id,
            "question_text": self.question_text,
            "category": self.category,
            "topic": self.topic,
            "difficulty": self.difficulty,
        }
