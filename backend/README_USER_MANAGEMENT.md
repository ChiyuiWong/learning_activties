# 🎓 COMP5241 用户管理指南

## 📋 概述

本系统使用MongoDB数据库来管理用户账号，支持安全的密码加密和角色管理。

## 🚀 快速开始

### 1. 设置MongoDB数据库

```bash
# 进入后端目录
cd learning_activties/backend

# 安装依赖
pip install pymongo python-dotenv bcrypt cryptography

# 设置数据库
python setup_mongodb.py

# 检查数据库状态
python setup_mongodb.py check
```

### 2. 管理用户账号

```bash
# 运行用户管理工具
python create_users.py
```

## 🔧 用户管理工具功能

### 主菜单选项：

1. **📝 创建激活码** - 标准的两步注册流程
2. **👤 直接创建用户** - 管理员直接创建账号
3. **📋 查看所有用户** - 列出现有用户
4. **🔑 查看所有激活码** - 列出待激活的账号
5. **🚀 创建演示用户** - 一键创建测试账号
6. **❌ 退出**

## 📝 创建用户的两种方式

### 方式1: 两步注册流程（推荐）

**第一步：管理员创建激活码**
```bash
python create_users.py
# 选择 1 - 创建激活码
# 输入：邮箱、姓名、角色
# 获得：激活码 (UUID)
```

**第二步：用户使用激活码注册**
- 用户访问注册页面
- 输入激活码、用户名、密码
- 系统自动创建账号

### 方式2: 直接创建用户（管理员）

```bash
python create_users.py
# 选择 2 - 直接创建用户
# 输入：用户名、密码、邮箱、姓名、角色
# 立即创建账号
```

## 👥 用户角色

- **student** - 学生：可以参与学习活动
- **teacher** - 教师：可以创建和管理学习活动
- **admin** - 管理员：拥有所有权限

## 🔐 安全特性

### 密码安全
- 使用 bcrypt 进行密码哈希
- 使用 AES 加密存储密码哈希
- 每个密码都有唯一的盐值

### 数据加密
- 密码哈希使用 AES-256-CBC 加密
- 加密密钥通过环境变量管理
- 每个密码都有唯一的初始化向量(IV)

## 🗄️ 数据库结构

### users 集合（用户账号）
```json
{
  "_id": "username",
  "username": "username",
  "email": "user@example.com",
  "encrypted_pw_hash": "...",
  "encrypted_pw_hash_iv": "...",
  "pw_hash_salt": "...",
  "first_name": "名字",
  "last_name": "姓氏", 
  "role": "student|teacher|admin",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### new_users 集合（激活码）
```json
{
  "_id": "activation-uuid",
  "email": "user@example.com",
  "first_name": "名字",
  "last_name": "姓氏",
  "role": "student|teacher|admin",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🔧 环境配置

### .env 文件
```bash
# MongoDB连接
MONGODB_URI=mongodb://localhost:27017/comp5241_g10

# 密码加密密钥（32字节base64编码）
PW_HASH_ENC_KEY=your_32_byte_base64_key

# JWT密钥
JWT_SECRET_KEY=your_jwt_secret

# 其他配置
DISABLE_AUTH=false
FLASK_ENV=development
```

## 🎯 演示账号

系统提供以下演示账号用于测试：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| teacher1 | password123 | teacher | 教师账号 |
| student1 | password123 | student | 学生账号 |
| admin1 | password123 | admin | 管理员账号 |
| demo | demo | teacher | 通用演示账号 |
| 任意用户名 | demo | teacher | 万能演示密码 |

## 🔄 登录优先级

1. **MongoDB数据库验证**（优先）
2. **演示账号验证**（数据库失败时）
3. **万能演示密码**（最后备选）

## 🛠️ 故障排除

### MongoDB连接失败
```bash
# 检查MongoDB服务状态
# Windows
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# 检查连接
python setup_mongodb.py check
```

### 密钥错误
```bash
# 重新生成加密密钥
python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"

# 更新.env文件中的PW_HASH_ENC_KEY
```

### 用户创建失败
- 检查用户名是否已存在
- 确认角色名称正确（student/teacher/admin）
- 验证邮箱格式
- 检查数据库连接

## 📞 技术支持

如果遇到问题，请检查：
1. MongoDB服务是否运行
2. .env文件配置是否正确
3. 网络连接是否正常
4. 用户权限是否足够

---

**注意：** 在生产环境中，请确保：
- 使用强密码策略
- 定期更换加密密钥
- 启用MongoDB身份验证
- 使用HTTPS连接
