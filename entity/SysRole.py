from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SysRole(Base):
    __tablename__ = 'sys_role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow)

