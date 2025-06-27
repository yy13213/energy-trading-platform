from flask import jsonify
import jwt
from config import User
from results import *
#  查询自己当前余额
def get_user_balance_impl(token):
    username = jwt.decode(token, 'secret_key', algorithms=[
                          'HS256'])["username"]
    user = User.query.filter_by(username=username).first()
    nb = float(str(user.balance)) 
    return jsonify({"余额":nb})
