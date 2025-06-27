from flask import  request, jsonify
from flask_cors import CORS
import jwt
import json
import time
from datetime import datetime
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
from blockchain_cache import cached_blockchain_call, auto_cleanup_cache
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)

# 添加响应时间统计中间件
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = round((time.time() - request.start_time) * 1000, 2)
        endpoint = request.endpoint or 'unknown'
        method = request.method
        path = request.path
        
        # 只记录API接口的时间，过滤掉静态文件
        if path.startswith('/') and not path.startswith('/static'):
            print(f"⏱️ {method} {path} - {response.status_code} - {duration}ms")
            
            # 标记慢请求（超过1000ms）
            if duration > 1000:
                print(f"🐌 慢请求警告: {path} 耗时 {duration}ms")
    
    return response

# 函数级时间统计装饰器
def timing_decorator(func_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)
            
            print(f"📊 {func_name} 执行时间: {duration}ms")
            
            if duration > 500:
                print(f"🚨 {func_name} 执行慢: {duration}ms")
            
            return result
        return wrapper
    return decorator

# 验证token的辅助函数
def verify_token_from_request():
    """从请求中验证token并返回用户信息"""
    try:
        token = request.headers.get('Authorization')
        if not token:
            return None
        
        decoded_data = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        username = decoded_data.get("username")
        
        if not username:
            return None
            
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
            
        return {
            'user_id': user.id,
            'username': username,
            'address': user.address
        }
    except Exception as e:
        print(f"Token验证失败: {e}")
        return None

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

# 获取用户正在出售的设备列表
@app.route('/get_user_selling_equipment', methods=["POST"])
@token_required
@timing_decorator("get_user_selling_equipment")
def get_user_selling_equipment():
    try:
        token = request.headers.get('Authorization')
        username = jwt.decode(token, 'secret_key', algorithms=['HS256'])["username"]
        user = User.query.filter_by(username=username).first()
        
        # 获取所有正在出售的设备ID
        id_list_result = get_id_list()
        if isinstance(id_list_result, str):
            selling_ids = json.loads(id_list_result)
        else:
            selling_ids = id_list_result
        
        # 获取用户拥有的设备ID
        user_equipment_result = get_equipment_id_impl(token)
        if isinstance(user_equipment_result, str):
            user_ids_data = json.loads(user_equipment_result)
        else:
            user_ids_data = user_equipment_result
        
        # 从设备详情中提取ID
        if isinstance(user_ids_data, list) and len(user_ids_data) > 0:
            if isinstance(user_ids_data[0], dict):
                # 如果是字典列表，提取ID
                user_ids = [int(item['id']) for item in user_ids_data]
            else:
                # 如果已经是ID列表
                user_ids = [int(item) for item in user_ids_data]
        else:
            user_ids = []
        
        # 找出用户正在出售的设备（两个列表的交集）
        user_selling_ids = [id for id in selling_ids if int(id) in user_ids]
        
        # 并发获取每个设备的详细信息 - 大幅提升性能
        selling_equipment = []
        if user_selling_ids:
            # 使用线程池并发调用区块链接口
            import concurrent.futures
            import threading
            
            def get_equipment_details(equipment_id):
                try:
                    # 直接调用区块链缓存，避免Flask request上下文问题
                    res = cached_blockchain_call(user.address, contract_name, "getItem", [
                                                 equipment_id], contract_address, contract_abi)
                    result = res.text.strip('[]')
                    result = result.strip('"')
                    
                    if result:
                        result_str = result.replace("\\\"", "\"")
                        result_list = json.loads(result_str)
                        
                        # 处理不同的数据格式
                        if isinstance(result_list, list) and len(result_list) >= 7:
                            equipment_info = {
                                "id": str(result_list[0]),
                                "name": result_list[1],
                                "power": str(result_list[2]),
                                "address": result_list[3],
                                "equ_local": result_list[4],
                                "price": result_list[5],
                                "addTime": result_list[6],
                            }
                            return equipment_info
                except Exception as e:
                    print(f"  ❌ 获取设备{equipment_id}详情失败: {e}")
                return None
            
            # 并发执行，最多5个线程
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(user_selling_ids))) as executor:
                futures = {executor.submit(get_equipment_details, equipment_id): equipment_id 
                          for equipment_id in user_selling_ids}
                
                for future in concurrent.futures.as_completed(futures):
                    equipment_info = future.result()
                    if equipment_info:
                        selling_equipment.append(equipment_info)
        
        print(f"  ✅ 返回{len(selling_equipment)}个正在出售的设备")
        return selling_equipment
        
    except Exception as e:
        print(f"❌ 获取用户出售设备失败: {e}")
        return gen_result(500, f"获取用户出售设备失败: {str(e)}")

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
    try:
        # 获取所有正在出售的商品id列表
        id_list_result = get_id_list()
        if isinstance(id_list_result, str):
            id_list = json.loads(id_list_result)
        else:
            id_list = id_list_result
        
        # print(id_list)
        items = []
        for item_id in id_list:
            try:
                # 获取商品详细信息
                result = get_equipment_impl(item_id)
                if isinstance(result, str):
                    result = result.strip('"')
                    result_str = result.replace("\\\"", "\"")  # 将转义的双引号替换为普通的双引号
                    result_list = json.loads(result_str)
                else:
                    result_list = result
                
                # 处理不同的数据格式
                if isinstance(result_list, list) and len(result_list) >= 7:
                    # 如果是列表格式
                    result_dict = {
                        "id": str(result_list[0]),
                        "name": result_list[1],
                        "power": str(result_list[2]),
                        "address": result_list[3],
                        "equ_local": result_list[4],
                        "price": result_list[5],
                        "addTime": result_list[6],
                    }
                elif isinstance(result_list, dict):
                    # 如果是字典格式
                    result_dict = {
                        "id": str(result_list.get("id", "")),
                        "name": result_list.get("name", ""),
                        "power": str(result_list.get("power", "")),
                        "address": result_list.get("owner", ""),
                        "equ_local": result_list.get("equ_address", ""),
                        "price": result_list.get("price", ""),
                        "addTime": result_list.get("addTime", ""),
                    }
                else:
                    # 数据格式不正确，跳过
                    continue
                    
                items.append(result_dict)
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"处理商品 {item_id} 时出错: {e}")
                continue
                
        return items
    except Exception as e:
        print(f"获取商品列表时出错: {e}")
        return gen_result(500, "获取商品列表失败")


# 创建购买订单信息
@app.route('/create_buy_order',methods=["POST"])
@token_required
def create_buy_order():
    data = request.get_json()
    return create_buy_order_impl(data)

# 获取用户剩余能源
@app.route('/get_user_energy', methods=["POST"])
@token_required
@timing_decorator("get_user_energy")
def get_user_energy():
    token = request.headers.get('Authorization')
    return get_user_energy_impl(token)
#  出售能源
@app.route('/sell_energy', methods=["POST"])
def sell_energy():
    try:
        data = request.get_json()
        token = request.headers.get('Authorization')
        
        if not token:
            return gen_result(401, "Token缺失")
            
        username = jwt.decode(token, 'secret_key', algorithms=[
                              'HS256'])["username"]
        
        amount = data["amount"]
        price = data["price"]
        print(f"💰 {username} 尝试出售能源: {amount}单位，价格{price}")
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return gen_result(404, "用户不存在")
            
        if not user.address:
            return gen_result(400, "用户地址为空，请先设置区块链地址")
            
        res = common_utils.common_bc_req(user.address,
                                         contract_name,
                                         'sellEnergy',
                                         [amount,price],
                                         contract_address,
                                         contract_abi)
        
        if res.status_code == 200:
            res_json = json.loads(res.text)
            
            """" status": "0x0" 表示成功 """
            if res_json.get('status') == '0x0':
                print("✅ 能源出售成功")
                return success_result
            else:
                error_msg = res_json.get('message', '未知错误')
                print(f"❌ 能源出售失败: {error_msg}")
                return gen_result(500, error_msg)
        else:
            print(f"❌ HTTP请求失败: 状态码 {res.status_code}")
            return gen_result(res.status_code, res.text)
            
    except jwt.InvalidTokenError as e:
        print(f"❌ Token解码失败: {e}")
        return gen_result(401, "Token无效")
    except KeyError as e:
        print(f"❌ 缺少必要参数: {e}")
        return gen_result(400, f"缺少必要参数: {str(e)}")
    except Exception as e:
        print(f"❌ 服务器内部错误: {e}")
        return gen_result(500, f"服务器内部错误: {str(e)}")

# 获取用户正在出售中的能源数量
@app.route('/get_user_sell_energy', methods=["POST"])
@timing_decorator("get_user_sell_energy")
def get_user_sell_energy():
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    user = User.query.filter_by(username=username).first()
    res = cached_blockchain_call(user.address,
                                 contract_name,
                                 'getUserAvailableEnergy',
                                 [user.address],
                                 contract_address,
                                 contract_abi)
    try:
        response_data = json.loads(res.text)
        output_list = response_data if isinstance(response_data, list) else [response_data]
        
        if len(output_list) > 2 and output_list[2]:
            # 解析第三个元素（能源数量数组）
            amounts_str = output_list[2]
            
            # 如果是字符串格式的数组，需要解析
            if isinstance(amounts_str, str):
                # 移除方括号和空格，然后分割
                amounts_str = amounts_str.strip().strip('[]').strip()
                if amounts_str:
                    amount_parts = [part.strip() for part in amounts_str.split(',')]
                    amounts = []
                    for part in amount_parts:
                        try:
                            amount_val = int(part)
                            amounts.append(amount_val)
                        except (ValueError, TypeError):
                            amounts.append(0)
                else:
                    amounts = []
            elif isinstance(amounts_str, list):
                # 如果已经是列表，直接处理
                amounts = []
                for item in amounts_str:
                    try:
                        amount_val = int(item) if isinstance(item, str) else item
                        amounts.append(amount_val)
                    except (ValueError, TypeError):
                        amounts.append(0)
            else:
                amounts = []
            
            total_amount = sum(amounts)
            return str(total_amount)
        else:
            return "0"
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON解析错误: {e}")
        return gen_result(500, "区块链数据解析失败")

# 获取用户正在出售中的能源数量__列表
@app.route('/getUserAvailableEnergy', methods=["POST"])
def getUserAvailableEnergy():
    # data = request.get_json()
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    user = User.query.filter_by(username=username).first()
    res = cached_blockchain_call(user.address,
                                 contract_name,
                                 'getUserAvailableEnergy',
                                 [user.address],
                                 contract_address,
                                 contract_abi)
    try:
        response_data = json.loads(res.text)
        output_list = response_data if isinstance(response_data, list) else [response_data]
        dict_avilable = {}
        if len(output_list) > 0 and output_list[0]:
            # 检查是否为列表格式
            if isinstance(output_list[0], list):
                for idx, id in enumerate(output_list[0]):
                    price = output_list[1][idx] if len(output_list) > 1 and idx < len(output_list[1]) else 0
                    amount = output_list[2][idx] if len(output_list) > 2 and idx < len(output_list[2]) else 0
                    dict_avilable[id] = {"amount": amount, "price": price}
            elif isinstance(output_list[0], dict):
                # 如果是字典格式，直接返回
                dict_avilable = output_list[0]
        return dict_avilable
    except (json.JSONDecodeError, ValueError, IndexError, KeyError) as e:
        print(f"JSON解析错误: {e}")
        return gen_result(500, "区块链数据解析失败")
# 获取所有正在出售中的能源数量
@app.route('/getAvailableEnergy', methods=["POST"])
@timing_decorator("getAvailableEnergy")
def getAvailableEnergy():
    # 获取能源市场信息不需要用户认证，直接使用admin地址查询
    res = cached_blockchain_call(admin_address,
                                 contract_name,
                                 'getAvailableEnergy',
                                 [],
                                 contract_address,
                                 contract_abi)
    try:
        response_data = json.loads(res.text)
        output_list = response_data if isinstance(response_data, list) else [response_data]
        
        print(f"🏪 能源市场数据: {output_list}")
        
        dict_avilable = {}
        if len(output_list) >= 4 and output_list[0]:
            # 解析四个数组：IDs, Sellers, Prices, Amounts
            ids_str = output_list[0]
            sellers_str = output_list[1]
            prices_str = output_list[2]
            amounts_str = output_list[3]
            
            print(f"  🔧 ID数据: {ids_str} (类型: {type(ids_str)})")
            print(f"  🔧 卖家数据: {sellers_str} (类型: {type(sellers_str)})")
            print(f"  🔧 价格数据: {prices_str} (类型: {type(prices_str)})")
            print(f"  🔧 数量数据: {amounts_str} (类型: {type(amounts_str)})")
            
            # 解析ID数组
            if isinstance(ids_str, str):
                ids_str = ids_str.strip().strip('[]').strip()
                ids = [part.strip() for part in ids_str.split(',')] if ids_str else []
            else:
                ids = ids_str if isinstance(ids_str, list) else []
            
            # 解析卖家地址数组
            if isinstance(sellers_str, str):
                # 处理地址字符串，去除引号
                sellers_str = sellers_str.strip().strip('[]').strip()
                if sellers_str:
                    sellers = []
                    for part in sellers_str.split(','):
                        address = part.strip().strip('"').strip("'")
                        sellers.append(address)
                else:
                    sellers = []
            else:
                sellers = sellers_str if isinstance(sellers_str, list) else []
            
            # 解析价格数组
            if isinstance(prices_str, str):
                prices_str = prices_str.strip().strip('[]').strip()
                if prices_str:
                    prices = []
                    for part in prices_str.split(','):
                        try:
                            price = int(part.strip())
                            prices.append(price)
                        except (ValueError, TypeError):
                            prices.append(0)
                else:
                    prices = []
            else:
                prices = prices_str if isinstance(prices_str, list) else []
            
            # 解析数量数组
            if isinstance(amounts_str, str):
                amounts_str = amounts_str.strip().strip('[]').strip()
                if amounts_str:
                    amounts = []
                    for part in amounts_str.split(','):
                        try:
                            amount = int(part.strip())
                            amounts.append(amount)
                        except (ValueError, TypeError):
                            amounts.append(0)
                else:
                    amounts = []
            else:
                amounts = amounts_str if isinstance(amounts_str, list) else []
            
            print(f"  📊 解析后的IDs: {ids}")
            print(f"  📊 解析后的卖家: {sellers}")
            print(f"  📊 解析后的价格: {prices}")
            print(f"  📊 解析后的数量: {amounts}")
            
            # 构建返回字典
            for idx, id in enumerate(ids):
                address = sellers[idx] if idx < len(sellers) else ""
                price = prices[idx] if idx < len(prices) else 0
                amount = amounts[idx] if idx < len(amounts) else 0
                dict_avilable[id] = {"amount": amount, "price": price, "address": address}
                print(f"    💰 交易{id}: {amount}单位, 价格{price}, 卖家{address[:10]}...")
                
        print(f"  🏪 最终市场数据: {dict_avilable}")
        return dict_avilable
    except (json.JSONDecodeError, ValueError, IndexError, KeyError) as e:
        print(f"JSON解析错误: {e}")
        return gen_result(500, "区块链数据解析失败")

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

# 更新用户区块链地址
@app.route('/update_user_address', methods=["POST"])
def update_user_address():
    try:
        data = request.get_json()
        token = request.headers.get('Authorization')
        
        if not token:
            return gen_result(401, "Token缺失")
            
        username = jwt.decode(token, 'secret_key', algorithms=['HS256'])["username"]
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return gen_result(404, "用户不存在")
        
        # 如果请求中提供了地址，使用提供的地址
        if data and 'address' in data:
            new_address = data['address']
        else:
            # 尝试通过WeBASE生成新地址
            import requests
            url = f"http://{webase_host}:5002/WeBASE-Front/privateKey?type=0&userName={username}&groupId=group0"
            try:
                response = requests.get(url)
                response_data = response.json()
                if response.status_code == 200 and response_data.get("code") == 0:
                    new_address = response_data.get("address")
                else:
                    # 生成一个临时地址（仅用于测试）
                    import hashlib
                    import time
                    temp_string = f"{username}_{int(time.time())}"
                    new_address = "0x" + hashlib.sha256(temp_string.encode()).hexdigest()[:40]
            except Exception as e:
                # 生成一个临时地址（仅用于测试）
                import hashlib
                import time
                temp_string = f"{username}_{int(time.time())}"
                new_address = "0x" + hashlib.sha256(temp_string.encode()).hexdigest()[:40]
        
        # 更新用户地址
        user.address = new_address
        db.session.commit()
        
        return gen_result(200, "地址更新成功", {"address": new_address})
        
    except jwt.InvalidTokenError:
        return gen_result(401, "Token无效")
    except Exception as e:
        return gen_result(500, f"服务器内部错误: {str(e)}")

# 添加测试能源（仅用于测试）
@app.route('/add_test_energy', methods=["POST"])
def add_test_energy():
    try:
        data = request.get_json()
        user_address = data.get("address")
        amount = data.get("amount", 1000)
        
        if not user_address:
            return gen_result(400, "地址不能为空")
            
        print(f"🔋 为地址 {user_address} 添加 {amount} 单位测试能源")
        
        # 使用管理员地址调用addEnergy
        res = common_utils.common_bc_req(admin_address,
                                         contract_name,
                                         'addEnergy',
                                         [user_address, amount],
                                         contract_address,
                                         contract_abi)
        
        if res.status_code == 200:
            res_json = json.loads(res.text)
            if res_json.get('status') == '0x0':
                print("✅ 测试能源添加成功")
                return success_result
            else:
                error_msg = res_json.get('message', '未知错误')
                print(f"❌ 测试能源添加失败: {error_msg}")
                return gen_result(500, error_msg)
        else:
            return gen_result(res.status_code, res.text)
            
    except Exception as e:
        print(f"❌ 添加测试能源失败: {e}")
        return gen_result(500, str(e))

# 记录联系客服访问日志
@app.route('/log_customer_service', methods=['POST'])
@timing_decorator("log_customer_service")
def log_customer_service():
    """记录联系客服的访问日志"""
    try:
        # 验证token获取用户信息
        user_info = verify_token_from_request()
        if not user_info:
            return jsonify({'code': 401, 'errorMessage': 'Invalid token'})
        
        print(f"👨‍💼 客服访问: 用户 {user_info['username']} (ID: {user_info['user_id']}) 访问了联系客服页面")
        
        return jsonify({
            'code': 200, 
            'data': 'success',
            'message': '客服访问记录成功'
        })
    except Exception as e:
        print(f"❌ 客服访问记录失败: {str(e)}")
        return jsonify({'code': 500, 'errorMessage': str(e)})


# 记录页面访问日志
@app.route('/log_page_visit', methods=['POST'])
@timing_decorator("log_page_visit")
def log_page_visit():
    """记录页面访问日志"""
    try:
        data = request.get_json()
        page_name = data.get('page_name', 'unknown')
        
        # 验证token获取用户信息
        user_info = verify_token_from_request()
        if not user_info:
            return jsonify({'code': 401, 'errorMessage': 'Invalid token'})
        
        print(f"📄 页面访问: 用户 {user_info['username']} 访问了 {page_name} 页面")
        
        return jsonify({
            'code': 200,
            'data': 'success', 
            'message': '页面访问记录成功'
        })
    except Exception as e:
        print(f"❌ 页面访问记录失败: {str(e)}")
        return jsonify({'code': 500, 'errorMessage': str(e)})


# 获取缓存统计信息
@app.route('/cache_stats', methods=['GET'])
@timing_decorator("cache_stats")
def get_cache_stats():
    """获取缓存性能统计"""
    try:
        from blockchain_cache import blockchain_cache
        
        stats = blockchain_cache.get_cache_stats()
        
        print(f"📊 缓存统计请求 - 命中率: {stats['hit_rate']:.1f}%, 节省时间: {stats['time_saved_seconds']:.1f}s")
        
        return jsonify({
            'code': 200,
            'data': stats,
            'message': '缓存统计获取成功'
        })
    except Exception as e:
        print(f"❌ 获取缓存统计失败: {str(e)}")
        return jsonify({'code': 500, 'errorMessage': str(e)})


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=8080)