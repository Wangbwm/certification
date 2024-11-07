from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from dao import UserDao, RoleDao
from entity.SysUser import SysUser


# 创建FastAPI应用
app = FastAPI()

# 定义密钥和算法
SECRET_KEY = "CMCCMY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer会创建一个依赖项来验证令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 验证用户是否有效
def authenticate_user(username: str, password: str):
    user = SysUser(username=username, password=password)
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
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "username": user.username,
            "password": user.password
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
        if username is None or password is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = SysUser(username=username, password=password)
    if UserDao.login(user)[0]:
        sys_user = UserDao.getUserByPassword(user)
        # 转为字典
        user_dict = {"id": sys_user.id, "username": sys_user.username, "password": sys_user.password, "telephone": sys_user.telephone}
        return user_dict
    else:
        raise credentials_exception


# 受保护的路由
@app.get("/users/me", response_model=dict)
async def read_users_me(current_user: SysUser = Depends(get_current_user)):
    return current_user

@app.get("/users/me/role", response_model=dict)
async def read_users_role(current_user: SysUser = Depends(get_current_user)):
    role = RoleDao.get_role_by_user(current_user["id"])[0]
    if role is None:
        raise HTTPException(status_code=200, detail="Role not found")
    else:
        role_dict = {"id": role.id, "name": role.name}
        return role_dict

@app.get("/index")
async def index(current_user: SysUser = Depends(get_current_user)):
    return "hello world"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8081)
