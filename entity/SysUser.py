from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SysUser(Base):
    __tablename__ = 'sys_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    telephone = Column(String(20))
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return (f"<SysUser(id={self.id}, "  
                f"user_name='{self.user_name}', "  
                f"tel='{self.tel if self.tel else 'None'}', "  
                f"create_time='{self.create_time.isoformat() if self.create_time else 'None'}', "  
                f"...)>")
