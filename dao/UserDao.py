import math

from sqlalchemy import create_engine, func, true, false
from sqlalchemy.orm import sessionmaker
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


# 创建新用户
def create_user(new_user):
    session = get_session()
    try:
        # 检查用户名是否已存在
        existing_user = session.query(SysUser).filter_by(username=new_user.username, telephone=new_user.telephone).first()
        if existing_user:
            return False, f"用户已存在", True
            # 如果不存在，则添加新用户
        new_user.password = hash_password(new_user.password)
        session.add(new_user)
        session.flush()
        user_id = new_user.id
        new_user_role = SysUserRole(user_id=user_id, role_id=3)
        session.add(new_user_role)
        session.flush()
        session.commit()
        return True, f"用户 {new_user.username} 成功创建", True
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}", False
    finally:
        session.close()


# 用户登录
def login(user):
    session = get_session()
    try:
        # 检查用户是否已存在
        existing_user = session.query(SysUser).filter_by(username=user.username, telephone=user.telephone).first()
        if existing_user:
            # 对比数据库中的密码
            hash_pwd = existing_user.password
            if verify_password(user.password, hash_pwd.encode('utf-8')):
                return True, f"登录成功"
            else:
                return False, f"密码错误"
        else:
            return False, f"用户不存在"
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}"
    finally:
        session.close()


# 修改密码
def change_password(user, new_password):
    session = get_session()
    try:
        # 检查用户是否已存在
        existing_user = session.query(SysUser).filter_by(username=user.username, telephone=user.telephone).first()
        if existing_user:
            # 使用新密码生成哈希值
            hashed_password = hash_password(new_password)
            # 更新用户的密码字段
            existing_user.password = hashed_password
            session.flush()
            session.commit()
            return True, f"用户 {existing_user.username} 密码已修改", True
        else:
            return False, f"用户不存在", True
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}", False
    finally:
        session.close()


# 修改用户信息
def user_change(user, new_telephone):
    session = get_session()
    try:
        # 检查用户是否已存在
        existing_user = session.query(SysUser).filter_by(username=user.username, telephone=user.telephone).first()
        if existing_user:
            existing_user.telephone = new_telephone
            session.flush()
            session.commit()
            return True, f"用户 {existing_user.username} 信息已修改", True
        else:
            return False, f"用户不存在", True
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}", False
    finally:
        session.close()


# 分页查询用户
def user_list(user, page):
    total_pages = 0
    user_list = []
    page_size = 5
    flag, mes = login(user)
    if flag:
        try:
            session = get_session()
            existing_user = session.query(SysUser).filter_by(username=user.username).first()
            user_id = existing_user.id
            # 鉴权
            role = session.query(SysUserRole).filter_by(user_id=user_id).first()
            if role.role_id == 1:
                # 分页查询用户列表
                total_count = session.query(SysUser).count()
                offset = (page - 1) * page_size
                users = session.query(SysUser)
                user_list = users.offset(offset).limit(page_size).all()
                # 计算总页数
                total_pages = math.ceil(total_count / page_size)
                user_dict_list = [
                    {
                        "id": user.id,
                        "user_name": user.username,
                        "tel": user.tel,
                        "role_id": session.query(SysUserRole).filter_by(user_id=user.id).first().role_id
                    } for user in user_list
                ]
                return True, f"成功", total_pages, user_dict_list, True
            else:
                return False, f"用户权限不足", total_pages, user_list, True
        except Exception as e:
            session.rollback()
            return False, f"错误: {e}", total_pages, user_list, False
        finally:
            session.close()

    else:
        return False, f"系统内部错误", total_pages, user_list, False


# 删除用户
def user_delete(user, target_id):
    try:
        session = get_session()
        existing_user = session.query(SysUser).filter_by(username=user.username).first()
        if existing_user:
            # 鉴权
            user_id = existing_user.id
            role = session.query(SysUserRole).filter_by(user_id=user_id).first()
            if role.role_id == 1:
                if user_id == target_id:
                    return False, f"不能删除自己", True
                else:
                    target_user = session.query(SysUser).filter_by(id=target_id).first()
                    if target_user:
                        target_role = session.query(SysUserRole).filter_by(user_id=target_id).first()
                        session.flush()
                        session.delete(target_role)
                        session.flush()
                        session.delete(target_user)
                        session.commit()
                        return True, f"成功", False
                    else:
                        return False, f"用户不存在", True
            else:
                return False, f"用户权限不足", True
        else:
            return False, f"用户不存在", True
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}", False
    finally:
        session.close()


def getUserByPassword(user):
    session = get_session()
    try:
        # 检查用户是否已存在
        existing_user = session.query(SysUser).filter_by(username=user.username).first()
        if existing_user:
            sys_user = existing_user
            return sys_user
        else:
            return None
    except Exception as e:
        session.rollback()
        print(e)
        return None
    finally:
        session.close()


def getUserIdByName(username, telephone):
    session = get_session()
    try:
        # 检查用户是否已存在
        existing_user = session.query(SysUser).filter_by(username=username, telephone=telephone).first()
        if existing_user:
            return existing_user.id
        else:
            return None
    except Exception as e:
        session.rollback()
        print(e)
        return None
    finally:
        session.close()
