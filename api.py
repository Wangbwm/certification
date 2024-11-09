from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Body, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from dao import UserDao, RoleDao, ManagerDao, RoomDao, ApproveDao
from entity.SysManager import SysManager
from entity.SysRoom import SysRoom
from entity.SysUser import SysUser

# 创建FastAPI应用
app = FastAPI()

# 定义密钥和算法
SECRET_KEY = "CMCCMY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60
# 初始密码
INIT_PASSWORD = "password"

# OAuth2PasswordBearer会创建一个依赖项来验证令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 扩展 OAuth2PasswordRequestForm，使其支持 telephone 字段
class ExtendedOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(self, username: str = Form(...), password: str = Form(...), telephone: str = Form(...)):
        super().__init__(username=username, password=password)
        self.telephone = telephone


# 验证用户是否有效
def authenticate_user(username: str, password: str, telephone: str):
    user = SysUser(username=username, password=password, telephone=telephone)
    if UserDao.login(user)[0]:
        return user
    else:
        return None


# 生成访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 登录并获取Token的路由
@app.post("/token", response_model=dict)
async def login_for_access_token(form_data: ExtendedOAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, form_data.telephone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/password/telephone",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "username": user.username,
            "password": user.password,
            "telephone": user.telephone
        }, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 依赖项，通过Token获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        password: str = payload.get("password")
        telephone: str = payload.get("telephone")
        if username is None or password is None or telephone is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = SysUser(username=username, password=password, telephone=telephone)
    if UserDao.login(user)[0]:
        sys_user = UserDao.getUserByPassword(user)
        return sys_user
    else:
        raise credentials_exception


# 受保护的路由
@app.get("/users/me")
async def read_users_me(current_user: SysUser = Depends(get_current_user)):
    return current_user


# 管理员获取用户信息
@app.get("/users/list", response_model=dict)
async def user_list(page: int = 1, current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    else:
        res = UserDao.user_list(page)
        if res[0]:
            return {
                "total_pages": res[2],
                "users": res[3]
            }
        return {
            "details": res[1],
            "total_pages": res[2],
            "users": res[3]
        }


# 修改用户信息
@app.post("/users/change", response_model=dict)
async def change(username: str = Body(required=True), password: str = Body(required=True),
                 telephone: str = Body(required=True), new_telephone: str = Body(required=True),
                 current_user: SysUser = Depends(get_current_user)):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="username not match")
    sys_user = SysUser(id=current_user.id, username=username, password=password, telephone=telephone)
    res = UserDao.user_change(sys_user, new_telephone)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 修改密码
@app.post("/users/change/password", response_model=dict)
async def change_password(username: str = Body(required=True), password: str = Body(required=True),
                          telephone: str = Body(required=True), current_user: SysUser = Depends(get_current_user)):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="username not match")
    sys_user = SysUser(id=current_user.id, username=username, password=password, telephone=telephone)
    res = UserDao.change_password(sys_user, password)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 管理员重置用户密码
@app.post("/users/reset/password", response_model=dict)
async def reset_password(username: str = Body(required=True),
                         telephone: str = Body(required=True),
                         current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    else:
        target_user = SysUser(username=username, telephone=telephone)
        res = UserDao.change_password(target_user, INIT_PASSWORD)
        if res[0]:
            return {"detail": res[1]}
        else:
            raise HTTPException(status_code=403, detail=res[1])


# 新建用户
@app.post("/users/create", response_model=dict)
async def create_user(username: str = Body(required=True), password: str = Body(required=True),
                      telephone: str = Body(required=True)):
    sys_user = SysUser(username=username, password=password, telephone=telephone)
    res = UserDao.create_user(sys_user)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 用户删除
@app.delete("/users/delete", response_model=dict)
async def delete_user(username: str = Body(required=True),
                      telephone: str = Body(required=True),
                      current_user: SysUser = Depends(get_current_user)):
    target_id = UserDao.getUserIdByName(username, telephone)
    if target_id is None:
        raise HTTPException(status_code=403, detail="User not found")
    res = UserDao.user_delete(current_user, target_id)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 获取用户角色
@app.get("/users/me/role", response_model=dict)
async def read_users_role(current_user: SysUser = Depends(get_current_user)):
    role = RoleDao.get_role_by_user(current_user.id)[0]
    if role is None:
        raise HTTPException(status_code=403, detail="Role not found")
    else:
        role_dict = {"id": role.id, "name": role.name}
        return role_dict


# 管理员获得用户角色
@app.get("/users/role/get", response_model=dict)
async def get_role(username: str = Body(required=True),
                   telephone: str = Body(required=True),
                   current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    target_user = SysUser(username=username, telephone=telephone)
    role = RoleDao.get_role_by_user(target_user.id)[0]
    if role is None:
        raise HTTPException(status_code=403, detail="Role not found")
    else:
        role_dict = {
            "username": target_user.username,
            "telephone": target_user.telephone,
            "id": role.id,
            "name": role.name
        }
        return role_dict


# 用户角色修改
@app.post("/users/change/role", response_model=dict)
async def change_role(username: str = Body(required=True),
                      telephone: str = Body(required=True),
                      role_id: int = Body(required=True),
                      current_user: SysUser = Depends(get_current_user)):
    target_id = UserDao.getUserIdByName(username, telephone)
    res = RoleDao.role_change(current_user, target_id, role_id)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 机房长信息
@app.get("/manager/me")
async def manager_me(current_user: SysUser = Depends(get_current_user)):
    res = ManagerDao.get_manager(current_user)
    if res[0]:
        return res[1]
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 查询指定机房长信息
@app.get("/manager/get", response_model=dict)
async def get_manager(username: str = Body(required=True),
                      telephone: str = Body(required=True),
                      current_user: SysUser = Depends(get_current_user)):
    target_user = UserDao.getUserByName(username, telephone)
    res = ManagerDao.get_manager(target_user)
    if res[0]:
        return res[1]
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 查询机房长列表
@app.get("/manager/list", response_model=dict)
async def get_manager_list(page: int = 1, current_user: SysUser = Depends(get_current_user)):
    res = ManagerDao.get_manager_list(page)
    if res[0]:
        return {
            "total_pages": res[2],
            "managers": res[3]
        }
    return {
        "details": res[1],
        "total_pages": res[2],
        "managers": res[3]
    }


# 新增机房长
@app.post("/manager/create", response_model=dict)
async def create_manager(username: str = Body(required=True),
                         telephone: str = Body(required=True),
                         address: str = Body(required=True),
                         current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    sys_user = UserDao.getUserIdByName(username, telephone)
    sys_manager = SysManager(user_id=sys_user.id, address=address, telephone=telephone)
    res = ManagerDao.create_manager(sys_manager)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 删除机房长
@app.delete("/manager/delete", response_model=dict)
async def delete_manager(username: str = Body(required=True),
                         telephone: str = Body(required=True),
                         current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    target_id = UserDao.getUserIdByName(username, telephone)
    res = ManagerDao.delete_manager(target_id)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 修改机房长信息
@app.post("/manager/change", response_model=dict)
async def change_manager(address: str = Body(required=True),
                         current_user: SysUser = Depends(get_current_user)):
    res = ManagerDao.user_change(current_user, address)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 管理员修改机房长信息
@app.post("/manager/admin/change/", response_model=dict)
async def admin_change_manager(username: str = Body(required=True),
                               telephone: str = Body(required=True),
                               address: str = Body(required=True),
                               current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    target_user = UserDao.getUserIdByName(username, telephone)
    res = ManagerDao.user_change(target_user, address)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 机房信息列表查询
@app.get("/room/list", response_model=dict)
async def get_room_list(page: int = 1, current_user: SysUser = Depends(get_current_user)):
    res = RoomDao.get_room_list(page)
    if res[0]:
        return {
            "total_pages": res[2],
            "rooms": res[3]
        }
    return {
        "details": res[1],
        "total_pages": res[2],
        "rooms": res[3]
    }


# 查询指定机房信息
@app.get("/room/get")
async def get_room(name: str, current_user: SysUser = Depends(get_current_user)):
    res = RoomDao.get_room_by_name(name)
    if res[0]:
        return res[1]
    else:
        raise HTTPException()


# 管理员增加机房
@app.post("/room/create", response_model=dict)
async def create_room(name: str = Body(required=True),
                      address: str = Body(required=True),
                      manager_id: int = Body(required=True),
                      current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    sys_room = SysRoom(name=name, address=address, manager_id=manager_id)
    res = RoomDao.create_room(sys_room)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 管理员删除机房
@app.delete("/room/delete", response_model=dict)
async def delete_room(name: str = Body(required=True),
                      current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    res = RoomDao.delete_room_by_name(name)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 管理员和机房长修改机房信息
@app.post("/room/change", response_model=dict)
async def change_room(name: str = Body(required=True),
                      address: str = Body(required=True),
                      manager_id: int = Body(required=True),
                      current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    user = ManagerDao.get_user_by_id(manager_id)
    if role_id[0].id != 1 and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission")
    sys_room = SysRoom(name=name, address=address, manager_id=manager_id)
    res = RoomDao.change_room(sys_room)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 发起机房开门请求
@app.post("/approve/open", response_model=dict)
async def approve_open(room_id: int = Body(required=True),
                       notes: Optional[str] = Body(None),
                       current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id)
    if role_id[0].id != 3:
        res = ApproveDao.direct_open(current_user, room_id, notes)
        if res[0]:
            return {"detail": res[1]}
        else:
            raise HTTPException(status_code=403, detail=res[1])
    res = ApproveDao.approve_open(current_user, room_id, notes)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])


# 获得审批工单
@app.get("/approve/list", response_model=dict)
async def get_approve_list(pro_status: bool,
                           page: int = 1,
                           current_user: SysUser = Depends(get_current_user)):
    res = ApproveDao.get_approve_list(page, pro_status, current_user)
    if res[0]:
        return {
            "total_pages": res[2],
            "approves": res[3]
        }
    else:
        raise HTTPException(status_code=403, detail=res[1])

# 审批开门请求
@app.post("/approve/approve", response_model=dict)
async def approve_approve(approve_id: int = Body(required=True),
                          approve_status: bool = Body(required=True),
                          current_user: SysUser = Depends(get_current_user)):
    res = ApproveDao.approve_approve(approve_id, approve_status, current_user)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])

# 管理员删除审批工单
@app.delete("/approve/delete", response_model=dict)
async def delete_approve(approve_id: int = Body(required=True),
                         current_user: SysUser = Depends(get_current_user)):
    role_id = RoleDao.get_role_by_user(current_user.id).id
    if role_id != 1:
        raise HTTPException(status_code=403, detail="No permission")
    res = ApproveDao.delete_approve(approve_id)
    if res[0]:
        return {"detail": res[1]}
    else:
        raise HTTPException(status_code=403, detail=res[1])

@app.get("/index")
async def index(current_user: SysUser = Depends(get_current_user)):
    return "hello world"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8081)
