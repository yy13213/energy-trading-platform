import requests
import json
import config
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

    data = {
        "groupId": "1",
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
    res = requests.post(url="http://%s:5002/WeBASE-Front/trans/handle"%(config.webase_host),
                        headers=headers,
                        data=json.dumps(data).replace("False", "false").replace("True", "true"))
 # 这一行代码是将数据中的任何布尔值（True或False）替换为其小写等效物（true或false）。
 # 这样做是为了确保数据处于向WeBASE API发送请求的正确格式，因为API不会接受大写中的布尔值。
    return res
