from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    city = Column(String(100))
    state = Column(String(100))

    users = relationship("User", back_populates="college")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "city": self.city, "state": self.state}
