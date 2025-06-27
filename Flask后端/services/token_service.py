
import jwt
import datetime
def refresh_token_impl(token):
    try:
        # 解码原有的 token 并获取 payload
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        # 获取当前时间
        now = datetime.datetime.utcnow()
        # 设置新的过期时间
        exp = now + datetime.timedelta(minutes=60)
        # 更新 payload 中的过期时间
        payload['exp'] = exp
        # 生成新的 token
        new_token = jwt.encode(payload, 'secret_key', algorithm='HS256')
        # 返回新的 token
        return {'msg': 'success', 'new_token': new_token.encode('utf-8').decode('utf-8')}
    except jwt.ExpiredSignatureError:
        # token 过期异常
        return {'msg': 'token expired'}
    except jwt.InvalidTokenError:
        # token 无效异常
        return {'msg': 'invalid token'}
    