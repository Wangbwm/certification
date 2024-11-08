from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SysRoom(Base):
    __tablename__ = 'sys_room'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    manager_id = Column(Integer, nullable=False)
    def __repr__(self):
        return (f"<SysRoom(id={self.id}, "  
                f"address='{self.address if self.address else 'None'}', "
                f"name='{self.name}', "  
                f"manager_id='{self.manager_id}', "    
                f"...)>")
