from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SysUserRole(Base):
    __tablename__ = 'sys_user_role'  # 数据库中的表名
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    role_id = Column(Integer)
