from flask import request, json
import jwt
from config import User, contract_name, contract_address, contract_abi
#from utils import common_utils

import common_utils

from results import *
from config import *

# 添加能源
def add_user_energy_impl(data):
    to_address = data['address']
    amount = data['amount'] #数量
    # energy_number = data["energy"]
    res = common_utils.common_bc_req(admin_address,
                                     contract_name,
                                     'addEnergy',
                                     [to_address, amount],
                                     contract_address,
                                     contract_abi)
    return res.text
