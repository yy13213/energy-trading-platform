# 🌟 蕴能汇能源交易平台

## 📖 项目介绍

蕴能汇是一款基于 **FISCO BCOS** 构建的新能源交易平台，通过区块链技术实现了电力能源交易链上可溯源、不可篡改等特性。平台支持电力能源交易、新能源设备交易等功能，提供安全、高效、透明的交易体验，为新能源行业的交易提供全新解决方案。

## ⚡ 最新优化亮点

### 🚀 重大性能提升
- **区块链缓存系统**: 15秒智能缓存，性能提升 **99.7%**
- **前端API缓存**: 30秒缓存机制，避免重复请求  
- **并发加载优化**: 仪表盘数据并发获取，大幅提升响应速度
- **智能预加载**: 数据预获取机制，提供瞬时响应体验

### 📊 性能数据
- **首次访问**: 2-3秒 (受区块链网络限制)
- **缓存命中**: 1-6ms (性能提升 99.7%)
- **重复访问**: 200-500ms (性能提升 80-90%)

## 🛠️ 技术架构

### 后端技术栈
- **Flask**: 轻量级Web框架
- **FISCO BCOS**: 区块链底层网络
- **WeBASE**: 区块链中间件平台
- **MySQL**: 数据库存储
- **JWT**: 用户认证

### 前端技术栈
- **Vue.js**: 响应式前端框架
- **Element UI**: 组件库
- **ECharts**: 数据可视化
- **Axios**: HTTP客户端

### 🔧 核心功能模块
```
能源交易平台
├── 👤 用户管理
│   ├── 用户注册/登录
│   ├── 个人中心
│   └── 权限管理
├── ⚡ 能源交易
│   ├── 能源市场浏览
│   ├── 能源出售/购买
│   ├── 我的能源管理
│   └── 交易记录查询
├── 🏭 设备管理  
│   ├── 产权市场
│   ├── 设备创建/交易
│   ├── 我的设备列表
│   └── 设备详情查看
├── 📊 仪表盘
│   ├── 能源统计图表
│   ├── 设备交易趋势
│   └── 实时数据监控
└── 🛠️ 系统管理
    ├── 区块链缓存管理
    ├── 性能监控
    └── 日志记录
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 14+
- MySQL 5.7+
- FISCO BCOS 2.8+

### 1. 克隆项目
```bash
git clone https://github.com/yy13213/energy-trading-platform.git
cd energy-trading-platform
```

### 2. 后端设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
cd Flask后端
pip install -r requirements.txt

# 配置数据库
# 修改 config.py 中的数据库连接信息

# 启动后端服务
python app.py
```

### 3. 前端访问
```bash
# 直接访问前端页面
open dist/login/login.html
```

### 4. 区块链环境
```bash
# 启动WeBASE服务
cd ../webase-deploy
python deploy.py startAll
```

## 📈 性能监控

### 缓存统计接口
```bash
GET /cache_stats
```
返回缓存命中率、节省时间等统计信息

### 实时性能监控
- 响应时间统计中间件
- 函数级执行时间装饰器  
- 慢请求警告系统

## 🔧 配置说明

### 数据库配置 (config.py)
```python
HOSTNAME = '127.0.0.1'
PORT = 3306
DATABASE = 'flask_ces'
USERNAME = 'root'
PASSWORD = 'root'
```

### 区块链配置
```python
webase_host = "127.0.0.1"
contract_address = "0x8c17cf316c1063fcb6896e86b4f17b9900a5bd43"
admin_address = "0x84703c57a736246296d33ad2efa22126afba5c9e"
```

## 📱 主要页面功能

| 页面 | 功能描述 | 特色功能 |
|------|----------|----------|
| 🏠 主页 | 平台概览和导航 | 智能仪表盘 |
| ⚡ 能源市场 | 浏览和购买能源 | 实时价格更新 |
| 🔋 我的能源 | 管理个人能源资产 | 出售状态追踪 |
| 🏭 产权市场 | 设备交易市场 | 设备详情展示 |
| 📊 仪表盘 | 数据可视化分析 | 并发数据加载 |
| 👨‍💼 联系客服 | 在线客服支持 | 访问日志记录 |

## 🛡️ 安全特性

- **JWT Token认证**: 安全的用户身份验证
- **区块链加密**: 交易数据链上加密存储
- **权限控制**: 细粒度的功能权限管理
- **数据校验**: 前后端双重数据验证

## 🔄 API接口

### 用户管理
- `POST /login` - 用户登录
- `POST /register` - 用户注册
- `POST /change_password` - 修改密码

### 能源交易
- `POST /get_user_energy` - 获取用户能源
- `POST /sell_energy` - 出售能源
- `POST /getAvailableEnergy` - 获取市场能源

### 设备管理
- `POST /create_equipment` - 创建设备
- `POST /get_equipment_id` - 获取设备列表
- `POST /get_items` - 获取设备详情

### 系统监控
- `GET /cache_stats` - 缓存统计
- `POST /log_customer_service` - 客服访问日志

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 [MulanPSL-2.0](LICENSE) 许可证

## 📞 联系我们

- 项目地址: [https://github.com/yy13213/energy-trading-platform](https://github.com/yy13213/energy-trading-platform)
- 问题反馈: 请在 GitHub Issues 中提交

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！ 