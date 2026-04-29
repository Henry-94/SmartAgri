from sqlalchemy import Column, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    # Database has only username and password columns; use username as primary key
    username = Column(String, primary_key=True, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
