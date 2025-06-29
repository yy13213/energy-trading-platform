from flask import request,jsonify
from config import User, db
from results import *

# from config import *


#  添加用户余额
def add_user_balance_impl(data):
    user_id = data['user_id']
    amount = data['amount']
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    user.balance += amount
    db.session.commit()
    return jsonify({"message": "Balance added successfully", "balance": user.balance})
