from flask import  request, jsonify
from flask_cors import CORS
import jwt
from functools import wraps
from config import User, app
from config import *
#from utils import common_utils
import common_utils
from results import *
from services.user_service import *
from services.token_service import *
from models.equipment import *
from models.transfer_item import *
from models.get_item import *
from models.get_energy import *
from models.energy import *
from models.transfer_energy import *
from models.add_user_balance import *
from models.get_user_balance import *
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)
@app.route('/')
def hello_index():
    return 'Hello, World!'
# 刷新token
@app.route('/refresh_token', methods=['POST'])
def refresh_token():
    # 从请求体中获取 token
    token = request.json.get('token')
    return refresh_token_impl(token)
# 必须头部使用token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer_token = request.headers.get('Authorization')
            token = bearer_token
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, 'secret_key',
                              algorithms='HS256')
            print(data)
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated
# 登录
@app.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    return login_impl(data)
# 注册
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return register_impl(data)
# 修改密码
@app.route('/change_password',methods=["POST"])
@token_required
def change_password():
    data = request.get_json()
    return change_password_impl(data)
# 修改用户权限
@app.route('/chang_user_power', methods=["POST"])
@token_required
def chang_user_power():
    data = request.get_json()
    return chang_user_power_impl(data)

# 创建设备
@app.route('/create_equipment',methods=["POST"])
@token_required
def create_equipment():
    data = request.get_json()
    return create_equipment_impl(data)
        
# 根据设备id获取设备详细信息
@token_required
@app.route('/get_equipment', methods=["POST"])
def get_equipment():
    data = request.get_json()
    return get_equipment_impl(data['id'])

# 获取用户设备列表 (根据用户地址，获取用户所有的设备id)
@app.route('/get_equipment_id',methods=["POST","GET"])
@token_required
def get_equipment_id():
    token = request.headers.get('Authorization')
    return (get_equipment_id_impl(token))

# 创建出售订单信息---卖  （把solidity中调用一个把这个商品id放到正在出售的列表中）
@app.route('/create_production_order',methods=["POST"])
@token_required
# 加这个方法就会需要在请求头部的Authorization中加入token值，
def create_production_order():
    data = request.get_json()
    return create_production_order_impl(data)

# 查看正在出售商品列表,返回的商品id列表 
@app.route('/get_id_list',methods=["POST"])
@token_required
def get_id_list():
    token = request.headers.get('Authorization')
    return get_id_list_impl(token)
# 可以直接返回正在出售的商品详细信息，【用于做区块链浏览器】
@app.route('/get_items', methods=["POST"])
def get_items():
    # 获取所有正在出售的商品id列表
    id_list = json.loads(get_id_list())
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


# 创建购买订单信息
@app.route('/create_buy_order',methods=["POST"])
@token_required
def create_buy_order():
    data = request.get_json()
    return create_buy_order_impl(data)

# 获取用户剩余能源
@app.route('/get_user_energy', methods=["POST"])
@token_required
def get_user_energy():
    token = request.headers.get('Authorization')
    return get_user_energy_impl(token)
#  出售能源
@app.route('/sell_energy', methods=["POST"])
def sell_energy():
    data = request.get_json()
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    amount = data["amount"]
    price = data["price"]
    user = User.query.filter_by(username=username).first()
    res = common_utils.common_bc_req(user.address,
                                     contract_name,
                                     'sellEnergy',
                                     [amount,price],
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

# 获取用户正在出售中的能源数量
@app.route('/get_user_sell_energy', methods=["POST"])
def get_user_sell_energy():
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    user = User.query.filter_by(username=username).first()
    res = common_utils.common_bc_req(user.address,
                                     contract_name,
                                     'getUserAvailableEnergy',
                                     [user.address],
                                     contract_address,
                                     contract_abi)
    output_list = [eval(item) for item in eval(res.text)]
    
    return [str(sum(output_list[2]))]

# 获取用户正在出售中的能源数量__列表
@app.route('/getUserAvailableEnergy', methods=["POST"])
def getUserAvailableEnergy():
    # data = request.get_json()
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    user = User.query.filter_by(username=username).first()
    res = common_utils.common_bc_req(user.address,
                                     contract_name,
                                     'getUserAvailableEnergy',
                                     [user.address],
                                     contract_address,
                                     contract_abi)
    output_list = [eval(item) for item in eval(res.text)]
    dict_avilable = {}
    for i in output_list[0]:
        id = i
        index = output_list[0].index(id)
        price = output_list[1][index]
        amount = output_list[2][index]
        dict_avilable[id] = {"amount": amount, "price": price}
    return dict_avilable
# 获取所有正在出售中的能源数量
@app.route('/getAvailableEnergy', methods=["POST"])
def getAvailableEnergy():
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    user = User.query.filter_by(username=username).first()
    res = common_utils.common_bc_req(user.address,
                                     contract_name,
                                     'getAvailableEnergy',
                                     [],
                                     contract_address,
                                     contract_abi)
    output_list = [eval(item) for item in eval(res.text)]
    # print(output_list)
    dict_avilable = {}
    for i in output_list[0]:
        id = i
        index = output_list[0].index(id)
        address = output_list[1][index]
        price = output_list[2][index]
        amount = output_list[3][index]
        dict_avilable[id] = {"amount": amount, "price": price,"address":address}
        # print
    return dict_avilable

# 添加能源
@app.route('/add_user_energy', methods=["POST"])
def add_user_energy():
    data = request.get_json()
    return add_user_energy_impl(data)

# 用户购买能源
@app.route('/transfer_energy', methods=["POST"])
@token_required
def transfer_energy():
    data = request.get_json()
    return transfer_energy_impl(data)

# 取消出售能源
@app.route('/cancel_energy_sale', methods=["POST"])
def cance_energy_sale():
    data = request.get_json()
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    id = data["id"]
    user = User.query.filter_by(username=username).first()
    res = common_utils.common_bc_req(user.address,
                                     contract_name,
                                     'cancelEnergySale',
                                     [id],
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
    
#  添加用户余额
@app.route('/add_user_balance', methods=['POST'])
def add_user_balance():
   data = request.get_json()
   return add_user_balance_impl(data)
#  查询自己当前余额
@app.route('/get_user_balance', methods=["POST"])
@token_required
def get_user_balance():
    token = request.headers.get('Authorization')
    return get_user_balance_impl(token)

# 进行交易时对余额进行操作  【为后面购买设备做准备
@app.route('/transfer_balance', methods=['POST'])
def transfer():
    user_id = request.json.get('user_id')
    target_id = request.json.get('target_id')
    amount = request.json.get('amount')
    # 传入用户地址交易
    user = User.query.filter_by(address=user_id).first()
    
    target_user = User.query.filter_by(
        address=target_id).first()
    if user is None or target_user is None:
        return jsonify({"message": "User not found"}), 404
    if user.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400
    user.balance -= amount
    target_user.balance += amount
    db.session.commit()
    return jsonify({"message": "Transfer completed successfully", "balance": user.balance})
# 获取用户名和地址
@app.route('/getusername' , methods=["POST"])
def getusername():
    token = request.headers.get('Authorization')
    datasss = jwt.decode(token, 'secret_key', algorithms=['HS256'])
    username = datasss["username"]
    user = User.query.filter_by(username=username).first()
    
    return jsonify({"username": username,
                    "address": user.address
                    })
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)