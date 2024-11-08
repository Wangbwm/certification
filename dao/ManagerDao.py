import math

from sqlalchemy import create_engine, func, true, false
from sqlalchemy.orm import sessionmaker

from entity.SysManager import SysManager
from entity.SysUserRole import SysUserRole
from entity.SysUser import SysUser
from Utils.hash import *
import yaml

# 读取YAML配置文件
with open('config/database.yaml', 'r') as file:
    db_config = yaml.safe_load(file)
default_db_config = db_config['mysql']

# 创建SQLAlchemy引擎
engine = create_engine(
    f"mysql+pymysql://{default_db_config['user']}:{default_db_config['password']}@{default_db_config['host']}:{default_db_config['port']}/{default_db_config['database']}?charset=utf8")

# 创建会话类型
Session = sessionmaker(bind=engine)


# 创建会话实例
def get_session():
    return Session()


def get_manager(user):
    session = get_session()
    try:
        # 检查用户是否已存在
        existing_user = session.query(SysUser).filter_by(username=user.username, telephone=user.telephone).first()
        if existing_user:
            user_id = user.id
            existing_user = session.query(SysManager).filter_by(user_id=user_id).first()
            if existing_user:
                return True, existing_user
            else:
                return False, "用户未绑定机房长"
        else:
            return False, "用户不存在"
    except Exception as e:
        session.rollback()
        print(e)
        return False, "服务器内部错误"
    finally:
        session.close()