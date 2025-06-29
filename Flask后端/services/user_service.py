import requests
from config import *
import jwt
from  results import *
from flask import request, jsonify
from config import User, db, contract_address, contract_abi, admin_address, contract_name, webase_host
import hashlib
#from utils import common_utils
import common_utils
# 登录
def login_impl(data):
    username = data.get('username')  # 用户名
    password = data.get('password')  # 密码
    print(username, password)
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        payload = {'user_id': user.id, 'username': user.username}
        token = jwt.encode(payload, 'secret_key',algorithm='HS256')   # 生成 JWT token
            # 这里的密钥 'secret_key' 应该是一个随机的字符串，用于保护 JWT Token 的安全性
        print(f"用户{user}登录成功")
        return jsonify({"code": 200, "message": "success", "data": {'token': token}})
    else:
        return jsonify({"code": 501, "message": "登陆失败", "data": {"username": username, "password": password}})
# 注册
def register_impl(data):
    username = data.get('username')
    password = data.get('password')
      # 验证是否已经存在该用户
    user = User.query.filter_by(username=username).first()
    if user:
        return exists_result
     # 通过用户名在webase中生成一个测试用户，并获得地址,创建测试用户
        url = f"http://{webase_host}:5002/WeBASE-Front/privateKey?type=0&userName={username}&groupId=group0"
    try:
        response = requests.get(url)
        response_data = response.json()
        if response.status_code == 200 and response_data.get("code") == 0:
            address = response_data.get("address")
        else:
            print(f"WeBASE地址生成失败: {response_data}")
            # 如果WeBASE服务不可用，使用临时地址或返回错误
            address = None
    except Exception as e:
        print(f"调用WeBASE服务异常: {e}")
        address = None
    # 创建新用户
    new_user = User(username=username, address=address)
    new_user.set_password(password)  # 将明文密码转换成哈希值并存储到数据库中
    db.session.add(new_user)
    db.session.commit()
    return success_result
    



# 更改密码
def change_password_impl(data):
    username = data.get('username')
    new_password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user :
        # 对密码进行加密
        m = hashlib.sha256()
        m.update(new_password.encode('utf-8'))
        password_hash = m.hexdigest()

        user.password = password_hash
        db.session.commit()
        return success_result
    else:
        return empty_result


# 更改权限
def chang_user_power_impl(data):
    username = data.get('username')  # 用户昵称
    address = data.get("address")  # 用户地址
    role = data.get("role")    # 用户需要修改后的权限
    user = User.query.filter_by(username=username).first()
    if user and address:
        user.role = role
        db.session.commit()
        return success_result
    else:
        return empty_result

