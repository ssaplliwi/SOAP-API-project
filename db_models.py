from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    accounts = relationship("Account", back_populates="owner")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    account_id = Column(String, index=True, nullable=False)   # <-- bỏ unique=True
    balance = Column(Integer, default=0, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    owner = relationship("User", back_populates="accounts")

    __table_args__ = (
        UniqueConstraint('owner_id', 'account_id', name='uq_owner_account'),
    )

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    session_key = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
