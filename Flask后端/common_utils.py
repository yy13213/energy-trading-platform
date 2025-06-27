import requests
import json
import config
import time
# import hashlib
# import random


# def get_token():
#     """
#     随机生成token
#     """
#     src = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz!@#$%^&*()', 20))
#     m2 = hashlib.md5()
#     m2.update(src.encode("utf8"))
#     return m2.hexdigest()

# def get_time(num):
#     """
#     将区块链时间转为时间格式
#     """
#     timeArray = time.localtime(int(num/1000))
#     otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
#     return otherStyleTime

def common_bc_req(user_address, contract_name, func_name, param, contract_address, abi):
    start_time = time.time()
    
    data = {
        "groupId": "group0",
        "user": user_address,  #使用这个接口的用户 地址
        "contractName": contract_name, #合约名称
        "version": "",  #版本
        "funcName": func_name,  # 智能合约调用的功能
        "funcParam": param,  # 参数
        "contractAddress": contract_address,  # 合约的地址
        "contractAbi": abi,
        "useAes": False,
        "useCns": False,
        "cnsName": ""
    }
    
    headers = {'Content-Type': 'application/json'}
    url = f"http://{config.webase_host}:5002/WeBASE-Front/trans/handle"
    
    json_data = json.dumps(data).replace("False", "false").replace("True", "true")
    
    try:
        res = requests.post(url=url,
                            headers=headers,
                            data=json_data)
        
        duration = round((time.time() - start_time) * 1000, 2)
        print(f"⛓️ 区块链调用 {func_name}: {duration}ms")
        
        if duration > 1000:
            print(f"🐌 区块链调用慢: {func_name} 耗时 {duration}ms")
        
        return res
        
    except Exception as e:
        duration = round((time.time() - start_time) * 1000, 2)
        print(f"❌ 区块链请求异常: {e} (耗时: {duration}ms)")
        raise
