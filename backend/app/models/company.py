from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)

    roles = relationship("Role", back_populates="company", cascade="all, delete-orphan")

    def to_dict(self, include_roles=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "logo_url": self.logo_url,
        }
        if include_roles:
            data["roles"] = [r.to_dict() for r in self.roles]
        return data
