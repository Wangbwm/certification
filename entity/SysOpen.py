from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SysOpen(Base):
    __tablename__ = 'sys_open'
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, nullable=False)
    room_name = Column(String(255), nullable=False)
    pro_status = Column(Boolean, nullable=False)
    open_status = Column(Boolean, nullable=False)
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return "<SysOpen(id='%s', room_id='%s', room_name='%s', pro_status='%s', open_status='%s', create_time='%s')>" % (
            self.id, self.room_id, self.room_name, self.pro_status, self.open_status, self.create_time)
