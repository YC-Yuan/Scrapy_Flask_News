import db.db_base as db
import hashlib
import random
from global_var import SNOW_USER


# 新建用户
def insert(email, password):
    table = db.get_db().yanfuNewsDB.userTable
    salt = str(random.randint(0, 100000))
    password = str.encode(password + salt, encoding='utf-8')
    password = hashlib.md5(password).hexdigest()

    user_id = int(SNOW_USER.get_id())

    user = {
        '_id': user_id,
        'email': email,
        'password': password,
        'salt': salt,
        'permission': 1
    }
    table.insert(user)


# 判断用户是否存在
def exist(email):
    table = db.get_db().yanfuNewsDB.userTable
    user = table.find_one({'email': email})
    return user is not None


# 登陆检测
def login_check(email, password):
    table = db.get_db().yanfuNewsDB.userTable

    # 根本没这用户
    user = table.find_one({'email': email})
    if not user:
        return False

    salt = user['salt']
    password = str.encode(password + salt, encoding='utf-8')
    password = hashlib.md5(password).hexdigest()

    if password == user['password']:
        return user['_id']
    # 用户名存在，但密码错误
    else:
        return False


# 检测权限
def permission_check(user_id):
    table = db.get_db().yanfuNewsDB.userTable

    user = table.find_one({'_id': user_id})
    if user:
        return user['permission']
    else:
        return 0
