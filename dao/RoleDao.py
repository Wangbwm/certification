import yaml
from sqlalchemy import create_engine, func, true, false
from sqlalchemy.orm import sessionmaker

from entity.SysRole import SysRole
from entity.SysUser import SysUser
from entity.SysUserRole import SysUserRole

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


def get_role_by_user(user_id):
    session = get_session()
    try:
        role_id = session.query(SysUserRole).filter(SysUserRole.user_id == user_id).first()
        if role_id:
            sys_role = session.query(SysRole).filter(SysRole.id == role_id.role_id).first()
            return sys_role, None, True
    except Exception as e:
        session.rollback()
        return None, f"错误: {e}", False
    finally:
        session.close()


# 修改用户权限
def role_change(user, tag_user_id, role_id):
    try:
        session = get_session()
        existing_user = session.query(SysUser).filter_by(username=user.username, telephone=user.telephone).first()
        user_id = existing_user.id
        # 鉴权
        role = session.query(SysUserRole).filter_by(user_id=user_id).first()
        if tag_user_id == user_id:
            return False, f"无法操作本人权限", True
        else:
            if role.role_id == 1:
                existing_user_target = session.query(SysUser).filter_by(id=tag_user_id).first()
                if existing_user_target:
                    target_user_id = existing_user_target.id
                    target_role = session.query(SysUserRole).filter_by(user_id=target_user_id).first()
                    target_role.role_id = role_id
                    session.flush()
                    session.commit()
                    return True, f"用户身份已修改", True
                else:
                    return False, f"目标用户不存在", True
            else:
                return False, f"用户权限不足", True

    except Exception as e:
        session.rollback()
        return False, f"错误: {e}", False
    finally:
        session.close()
