import json
# from utils import datetime_utils
# 方法不允许
sb_request = json.dumps({"code": 203, "message": "'not support other method'"})
# 数据为空时使用的返回内容
empty_result = json.dumps({'code': 404001, 'data': '存在数据为空'}, ensure_ascii=False)
# 数据已存在时使用的返回内容
exists_result = json.dumps({'code': 201001, 'data': '数据已存在'}, ensure_ascii=False)
# 操作成功时使用的返回内容
success_result = json.dumps({'code': 200, 'data': 'ok'}, ensure_ascii=False)
# 用户名错误时使用的返回内容
user_password_error = json.dumps(
    {'code': 202, 'data': '密码错误'}, ensure_ascii=False
)
# 用户未登录时使用的返回总内容
not_login_result = json.dumps(
    {'code': 500001, 'data': '用户未登录'}, ensure_ascii=False
)

# # 生成自定义返回内容的函数
# # 例如gen_result(500,message)
def gen_result(code, data):
    return json.dumps({'code': code, 'data': data}, ensure_ascii=False, sort_keys=True)
