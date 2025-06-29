from flask import request, json
import jwt
from config import User, contract_name, contract_address, contract_abi
#from utils import common_utils
import common_utils
from results import *
from blockchain_cache import cached_blockchain_call


# 获取剩余能源
def get_user_energy_impl(token):
    # token = request.headers.get('Authorization')
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    user = User.query.filter_by(username=username).first()
    res = cached_blockchain_call(user.address,
                                 contract_name,
                                 'getUserEnergy',
                                 [user.address],
                                 contract_address,
                                 contract_abi)
    # print(res.text)
    return res.text
