import bcrypt


# 生成一个随机的盐（salt），用于增加密码哈希的安全性
def generate_salt():
    return bcrypt.gensalt()


# 对密码进行哈希处理
def hash_password(password):
    salt = bcrypt.gensalt()  # 生成新的盐
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)  # 使用盐对密码进行哈希处理
    hashed = hashed.decode('utf-8')
    return hashed  # 返回哈希值


# 验证密码
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)