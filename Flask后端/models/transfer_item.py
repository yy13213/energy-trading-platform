from flask import request, json
import jwt
from config import User, contract_name, contract_address, contract_abi
#from utils import common_utils
import common_utils
from results import *


# 创建出售订单信息---卖  （把solidity中调用一个把这个商品id放到正在出售的列表中）
# 加这个方法就会需要在请求头部的Authorization中加入token值，
def create_production_order_impl(data):
    # 这里前端的json可以只传2个数值，<用户地址><调用参数>,
    # 其他的可以直接在代码中写死，<合约名称><调用的功能><合约地址><合约abi>
    get_json = request.get_json()
    # print(get_json["sb"])
    # 将用户传入的token解码成用户名
    token = request.headers.get('Authorization')
    # 根据token,解码出用户名
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    # 从数据库中查到用户地址
    user = User.query.filter_by(username=username).first()
    print(user.address)
    # 传入添加到出售列表中的商品 id
    id = get_json["id"]
    price = get_json["price"]
    """
    sub_no 可能是用于标识某个子订单的唯一标识符。
    假设在一个在线餐厅订餐系统中，用户下了一个订单，并选择了两个不同的食品，
    此时系统会自动生成一个主订单号和两个子订单号，用于标识这个订单和每个子订单
    """
    # 调用智能合约Produces接口，创建订单
    res = common_utils.common_bc_req(user.address,
                                     contract_name,
                                     'addItemToSaleList',
                                     [id, price],
                                     contract_address,
                                     contract_abi)
    if res.status_code == 200:
        res_json = json.loads(res.text)
        """" status": "0x0" 表示成功 """
        if res_json['status'] == '0x0':
            return success_result
        else:
            return gen_result(500, res_json['message'])
    else:
        return gen_result(res.status_code, res.text)


# 创建购买订单信息---买  （把solidity中调用转移函数和将id从正在出售的列表中删除）
"""
前端在json中出传入from_address ，
这个购买的商品的卖方地址（  from_address   ），和购买的商品的id（ itemId ）
因为买方已经在json传入的headers 中token中得出地址了
"""
def create_buy_order_impl(data):
    # 这里前端的json可以只传2个数值，<用户地址><调用参数>,（前端只需要传入token和itemid即可）
    # 其他的可以直接在代码中写死，<合约名称><调用的功能><合约地址><合约abi>
    # data = request.get_json()
    # 将用户传入的token解码成用户名
    token = request.headers.get('Authorization')
    # 根据token,解码出用户名
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    # 从数据库中查到用户地址
    user = User.query.filter_by(username=username).first()
    # print(user.address)

    to_address = user.address
    # to_address = get_json["to_address"]
    itemId = data["itemId"]
    # 调用智能合约Produces接口，进行买（转移商品拥有人地址）
    res = common_utils.common_bc_req(user.address,
                                     contract_name,
                                     'transferItem',
                                     [to_address, itemId],
                                     contract_address,
                                     contract_abi)
    if res.status_code == 200:
        res_json = json.loads(res.text)
        """" status": "0x0" 表示成功 """
        if res_json['status'] == '0x0':
            return success_result
        else:
            return gen_result(500, res_json['message'])
    else:
        return gen_result(res.status_code, res.text)
