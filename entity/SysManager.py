from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SysManager(Base):
    __tablename__ = 'sys_manager'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    telephone = Column(String(50))
    address = Column(String(255), nullable=False)
    def __repr__(self):
        return (f"<SysManager(id={self.id}, "  
                f"user_id='{self.user_id}', "  
                f"telephone='{self.telephone if self.telephone else 'None'}', "  
                f"address='{self.address if self.address else 'None'}', "  
                f"...)>")
