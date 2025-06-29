from flask import request,  json
import jwt
from config import User, contract_name, contract_address, contract_abi
#from utils import common_utils
import common_utils
from results import *
from blockchain_cache import cached_blockchain_call



# /////////////////////////////////////////////////////////////////////////////////
# 函数的调用，根据id获取设备详细信息
def get_equipment_impl(id):
    equ_id = id
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    user = User.query.filter_by(username=username).first()
    res = cached_blockchain_call(user.address, contract_name, "getItem", [
                                 equ_id], contract_address, contract_abi)
    result = res.text.strip('[]')
    result = result.strip('"')
    # print(result)
    # print(list(result.split(",")))
    # result = list(result.split(","))
    return result
# /////////////////////////////////////////////////////////////////////////////////


# 获取用户设备列表 (根据用户地址，获取用户所有的设备id)
def get_equipment_id_impl(token):
    # token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    # 从用户名查找数据库中用户的地址  ： user.address
    user = User.query.filter_by(username=username).first()
    res = cached_blockchain_call(user.address, contract_name, "getUserItems", [
                                 user.address], contract_address, contract_abi)
    if res.status_code == 200:
        # 将返回的字符串转为列表
        # return json.loads(json.loads(res.text)[0])
        
        # 获取所有正在出售的商品id列表
        id_list = json.loads(json.loads(res.text)[0])
        # print(id_list)
        items = []
        for item_id in id_list:
            # 获取商品详细信息
            result = get_equipment_impl(item_id)
            result = result.strip('"')
            result_str = result.replace("\\\"", "\"")  # 将转义的双引号替换为普通的双引号
            result_list = json.loads(result_str)
            # result_list = json.loads(result)
            result_dict = {
                "id": str(result_list[0]),
                "name": result_list[1],
                "power": str(result_list[2]),
                "address": result_list[3],
                "equ_local": result_list[4],
                "price": result_list[5],
                "addTime": result_list[6],
            }
            items.append(result_dict)
        return items
    else:
        return gen_result(res.status_code, res.text)


# 查看正在出售商品列表,返回的商品id列表
def get_id_list_impl(token):
    # token = request.headers.get('Authorization')
    # 根据token,解码出用户名
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    # 从数据库中查到用户地址
    user = User.query.filter_by(username=username).first()
    res = cached_blockchain_call(user.address,
                                 contract_name,
                                 'getIdList',
                                 [],
                                 contract_address,
                                 contract_abi)
    # print("打印值------------------------------",res.text)
    result = res.text.strip('[]')
    result = result.strip('"')
    return result
    """返回的格式：[ 1, 2 ]
    """
