from flask import request, json
import jwt
from config import User, contract_name, contract_address, contract_abi
#from utils import common_utils
import common_utils
from results import *
# 对剩余能源进行交易
def transfer_energy_impl(data):
    token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    id = data["id"]
    amount = data["amount"]
    user = User.query.filter_by(username=username).first()
    res = common_utils.common_bc_req(user.address,
                                     contract_name,
                                     'buyEnergy',
                                     [id , amount],
                                     contract_address,
                                     contract_abi)
    # return res.text


    if res.status_code == 200:
            res_json = json.loads(res.text)
            if res_json['status'] == '0x0':
                return success_result
            else:
                return gen_result(500, res_json['message'])
    else:
        return gen_result(res.status_code, res.text)
