import math

import yaml
from sqlalchemy import create_engine, func, true, false
from sqlalchemy.orm import sessionmaker

from entity.SysManager import SysManager
from entity.SysRole import SysRole
from entity.SysRoom import SysRoom
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


def get_room_list(page):
    total_pages = 0
    all_rooms_list = []
    rooms_dict_list = {}
    page_size = 5
    session = get_session()
    try:
        # 分页查询列表
        total_count = session.query(SysRoom).count()
        offset = (page - 1) * page_size
        rooms = session.query(SysRoom)
        all_rooms_list = rooms.offset(offset).limit(page_size).all()
        # 计算总页数
        total_pages = math.ceil(total_count / page_size)

        rooms_dict_list = [
            {
                "id": room.id,
                "address": room.address,
                "name": room.name,
                "manager_name": session.query(SysUser)
                .filter_by(id=session.query(SysManager).filter_by(id=room.manager_id).first().user_id).first().username,
                "manager_telephone": session.query(SysUser)
                .filter_by(id=session.query(SysManager).filter_by(id=room.manager_id).first().user_id).first().telephone,
            } for room in all_rooms_list
        ]
        return True, f"成功", total_pages, rooms_dict_list
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}", total_pages, rooms_dict_list
    finally:
        session.close()


def get_room_by_name(name):
    session = get_session()
    try:
        # 根据name模糊搜索
        room = session.query(SysRoom).filter(SysRoom.name.like(f"%{name}%")).all()
        if room:
            return True, room
        return False, "未找到该机房"
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}"
    finally:
        session.close()


def create_room(sys_room):
    session = get_session()
    try:
        exiting_room = session.query(SysRoom).filter_by(name=sys_room.name)
        if exiting_room.first():
            return False, "该机房已存在"
        session.add(sys_room)
        session.flush()
        session.commit()
        return True, f"机房：{sys_room.name}添加成功"
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}"
    finally:
        session.close()


def delete_room_by_name(name):
    session = get_session()
    try:
        room = session.query(SysRoom).filter_by(name=name).first()
        if not room:
            return False, "未找到该机房"
        session.delete(room)
        session.flush()
        session.commit()
        return True, f"已删除该机房：{room.name}"
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}"
    finally:
        session.close()


def change_room(sys_room):
    session = get_session()
    try:
        room = session.query(SysRoom).filter_by(name=sys_room.name).first()
        if not room:
            return False, "未找到该机房"
        room.address = sys_room.address
        room.manager_id = sys_room.manager_id
        session.flush()
        session.commit()
        return True, f"已修改该机房：{room.name}"
    except Exception as e:
        session.rollback()
        return False, f"错误: {e}"
    finally:
        session.close()