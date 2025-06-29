from flask import request,json
import jwt
from config import User, contract_name, contract_address, contract_abi
#from utils import common_utils
import common_utils
from  results import *

# 创建设备 - 目前只搞了设备名称，设备id，设备功率，（设备所在地址_equ_local）
def create_equipment_impl(data):
    # data = request.get_json()
    equ_name = data.get("equ_name")
    equ_power = data.get("equ_power")
    equ_local = data.get("equ_local")
    addTime = data.get("addTime")
    price = 0   #设备金额默认等于0
    # 通过请求头 token解码获得用户名
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    # 从用户名查找数据库中用户的地址  ： user.address
    user = User.query.filter_by(username=username).first()
    # 调用函数开始请求
    res = common_utils.common_bc_req(user.address, contract_name, "createItem", [
                                     equ_name, equ_power, user.address, equ_local, price, addTime], contract_address, contract_abi)
    # 修改文档7中的校验逻辑
    if res.status_code == 200:
        res_json = json.loads(res.text)
        # 检查交易回执状态
        if res_json.get('status') == '0x0' and res_json.get('output') == '0x':
            return success_result
        else:
            return gen_result(500, "Transaction failed on blockchain")
    else:
        return gen_result(res.status_code, res.text)



