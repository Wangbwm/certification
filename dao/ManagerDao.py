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


def create_manager(sys_manager):
    session = get_session()
    try:
        existing_manager = session.query(SysManager).filter_by(user_id=sys_manager.user_id)
        if existing_manager.first():
            return False, "用户已绑定机房长"
        session.add(sys_manager)
        session.flush()
        session.commit()
        return True, f"用户{sys_manager.user_id}绑定机房长成功"
    except Exception as e:
        session.rollback()
        print(e)
        return False, "服务器内部错误"
    finally:
        session.close()


def delete_manager(target_id):
    session = get_session()
    try:
        existing_manager = session.query(SysManager).filter_by(user_id=target_id)
        if existing_manager.first():
            existing_manager.delete()
            session.flush()
            session.commit()
            return True, f"用户{target_id}解绑机房长成功"
        else:
            return False, "用户未绑定机房长"
    except Exception as e:
        session.rollback()
        print(e)
        return False, "服务器内部错误"
    finally:
        session.close()


def user_change(current_user, address):
    session = get_session()
    try:
        # 检查用户是否已存在
        existing_user = session.query(SysManager).filter_by(user_id=current_user.id).first()
        if existing_user:
            existing_user.address = address
            session.flush()
            session.commit()
            return True, f"用户{current_user.username}修改地址成功"
        else:
            return False, "用户未绑定机房长"
    except Exception as e:
        session.rollback()
        print(e)
        return False, "服务器内部错误"
    finally:
        session.close()


def get_manager_list(page):
    total_pages = 0
    all_managers_list = []
    managers_dict_list = {}
    page_size = 5
    session = get_session()
    try:
        # 分页查询列表
        total_count = session.query(SysManager).count()
        offset = (page - 1) * page_size
        managers = session.query(SysManager)
        all_managers_list = managers.offset(offset).limit(page_size).all()
        # 计算总页数
        total_pages = math.ceil(total_count / page_size)

        managers_dict_list = [
            {
                "id": manager.id,
                "manager_name": session.query(SysUser)
                .filter_by(id=manager.user_id).first().username,
                "manager_telephone": session.query(SysUser)
                .filter_by(id=manager.user_id).first().telephone,
                "manager_address": manager.address
            } for manager in all_managers_list
        ]
        return True, f"成功", total_pages, managers_dict_list
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}", total_pages, managers_dict_list
    finally:
        session.close()


def get_user_by_id(manager_id):
    session = get_session()
    try:
        user = session.query(SysUser)\
            .filter_by(id=session.query(SysManager).filter_by(manager_id=manager_id).first().user_id).first()
        return True, f"成功", user
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}", None
    finally:
        session.close()