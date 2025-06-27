# 配置文件引用依赖包内容
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask
from flask_login import UserMixin
import hashlib
# from functools import wraps
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# CORS(app, resources=r'/*')
CORS(app)


# 初始化 Flask-CORS 扩展  --跨域请求
# r'/*' 是通配符，让本服务器所有的URL 都允许跨域请求
# cors = CORS(app, resources={r"/*": {"origins": "*"}})  # *是表示所有域名，后期可以更换

'''
# 数据库相关配置
HOSTNAME = '127.0.0.1'
PORT = 3306
DATABASE = 'flask_ces'
USERNAME = 'root'
PASSWORD = '123456'
#app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTN
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
#db = SQLAlchemy(app)AME}:{PORT}/{DATABASE}?charset=utf8mb4"
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = "sfdsdaf"
'''

# 数据库相关配置
HOSTNAME = 'localhost'  # SQL Server 默认本地地址
PORT = 1433             # SQL Server 默认端口（命名实例需调整）
DATABASE = 'flask_ces'  # 数据库名称保持不变
USERNAME = 'root'      # SQL Server 账户名（需具有访问权限）
PASSWORD = '123456'    # SQL Server 密码

''''# SQL Server 连接配置（使用 pyodbc 驱动）
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT};"
    f"database={DATABASE};"
    "driver=ODBC+Driver+17+for+SQL+Server;"  # 指定 SQL Server ODBC 驱动版本
)
'''

app.config["SQLALCHEMY_DATABASE_URI"] = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&charset=utf8"

db = SQLAlchemy(app)
app.config['SECRET_KEY'] = "sfdsdaf"


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(255))  #地址可为空
    balance = db.Column(db.Float, default=0)  # 添加用户余额，默认值为0

    # 使用hash加密密码
    def set_password(self, password):
        self.password = hashlib.sha256(
            password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return self.password == hashlib.sha256(password.encode('utf-8')).hexdigest()
# print(User["username"])


# WeBASE-Front功能配置
admin_address = '0xca1441cb46f1dec3455a53bc1dd8cf00479174fe'
webase_host = '192.168.233.132'
contract_name = 'ItemContract'
contract_address = '0xffa8da01f3edaf69724f44e73439f37e8cce5b2c'
contract_abi =[{"constant":True,"inputs":[],"name":"getAvailableEnergy","outputs":[{"name":"ids","type":"uint256[]"},{"name":"sellers","type":"address[]"},{"name":"prices","type":"uint256[]"},{"name":"amounts","type":"uint256[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"itemId","type":"uint256"},{"name":"price","type":"uint256"}],"name":"addItemToSaleList","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"name":"user","type":"address"},{"name":"amount","type":"uint256"}],"name":"addEnergy","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"itemId","type":"uint256"}],"name":"getItem","outputs":[{"components":[{"name":"id","type":"uint256"},{"name":"name","type":"string"},{"name":"power","type":"uint256"},{"name":"owner","type":"address"},{"name":"equ_address","type":"string"},{"name":"price","type":"uint256"},{"name":"addTime","type":"string"}],"name":"","type":"tuple"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"user","type":"address"}],"name":"getUserAvailableEnergy","outputs":[{"name":"ids","type":"uint256[]"},{"name":"prices","type":"uint256[]"},{"name":"amounts","type":"uint256[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"energyCounter","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getAllItems","outputs":[{"name":"","type":"uint256[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"address"},{"name":"","type":"uint256"}],"name":"userItems","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"energyId","type":"uint256"}],"name":"cancelEnergySale","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"name":"to","type":"address"},{"name":"itemId","type":"uint256"}],"name":"transferItem","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"itemCounter","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"user","type":"address"}],"name":"getUserEnergy","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"uint256"}],"name":"energyPrices","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"energyId","type":"uint256"}],"name":"getEnergyPrice","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"address"}],"name":"userEnergy","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"getIdList","outputs":[{"name":"","type":"uint256[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"uint256"}],"name":"energyAmounts","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"uint256"}],"name":"items","outputs":[{"name":"id","type":"uint256"},{"name":"name","type":"string"},{"name":"power","type":"uint256"},{"name":"owner","type":"address"},{"name":"equ_address","type":"string"},{"name":"price","type":"uint256"},{"name":"addTime","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"name":"","type":"uint256"}],"name":"id_list","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"energyId","type":"uint256"},{"name":"amountToBuy","type":"uint256"}],"name":"buyEnergy","outputs":[],"payable":True,"stateMutability":"payable","type":"function"},{"constant":True,"inputs":[{"name":"_user","type":"address"}],"name":"getUserItems","outputs":[{"name":"","type":"uint256[]"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"_name","type":"string"},{"name":"_power","type":"uint256"},{"name":"_owner","type":"address"},{"name":"_equ_local","type":"string"},{"name":"_price","type":"uint256"},{"name":"_addTime","type":"string"}],"name":"createItem","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"name":"","type":"uint256"}],"name":"energySellers","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"name":"amount","type":"uint256"},{"name":"price","type":"uint256"}],"name":"sellEnergy","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"anonymous":False,"inputs":[{"indexed":False,"name":"id","type":"uint256"},{"indexed":False,"name":"name","type":"string"},{"indexed":False,"name":"power","type":"uint256"},{"indexed":False,"name":"owner","type":"address"},{"indexed":False,"name":"equ_address","type":"string"},{"indexed":False,"name":"price","type":"uint256"},{"indexed":False,"name":"addTime","type":"string"}],"name":"ItemCreated","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"id","type":"uint256"},{"indexed":False,"name":"from","type":"address"},{"indexed":False,"name":"to","type":"address"}],"name":"ItemTransferred","type":"event"}]