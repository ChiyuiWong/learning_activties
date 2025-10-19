# 🚀 快速开始 - MongoDB用户管理

## 📋 前提条件

1. **安装MongoDB**
   - 下载并安装 MongoDB Community Server
   - 启动MongoDB服务

2. **安装Python依赖**
   ```bash
   pip install pymongo python-dotenv bcrypt cryptography
   ```

## 🔧 第一次设置

### 1. 启动MongoDB服务

**Windows:**
```bash
# 方法1: 服务管理器启动MongoDB服务
# 方法2: 命令行启动
mongod --dbpath C:\data\db
```

**macOS:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
```

### 2. 初始化数据库

```bash
cd learning_activties/backend
python setup_mongodb.py
```

### 3. 创建用户账号

```bash
python create_users.py
```

## 👤 添加用户的步骤

### 方法1: 直接创建用户（推荐）

1. 运行 `python create_users.py`
2. 选择 `2 - 直接创建用户`
3. 输入用户信息：
   - 用户名: `teacher1`
   - 密码: `password123`
   - 邮箱: `teacher1@comp5241.edu`
   - 名字: `张`
   - 姓氏: `老师`
   - 角色: `teacher`

### 方法2: 快速创建演示用户

1. 运行 `python create_users.py`
2. 选择 `5 - 创建演示用户`
3. 自动创建3个测试账号

## 🎯 测试登录

创建用户后，可以使用以下账号登录：

- **teacher1** / **password123** (教师)
- **student1** / **password123** (学生)
- **admin1** / **password123** (管理员)

## ❗ 常见问题

### MongoDB连接失败
- 确保MongoDB服务正在运行
- 检查端口27017是否被占用
- 确认MongoDB安装正确

### 密钥错误
- 运行 `python setup_mongodb.py` 会自动生成密钥
- 检查 `.env` 文件是否存在

### 用户创建失败
- 检查用户名是否已存在
- 确认MongoDB连接正常
- 验证输入的角色名称（student/teacher/admin）

## 🔄 系统行为

修改后的登录系统会：

1. **优先使用MongoDB验证** - 如果数据库中有用户，优先验证
2. **备用演示账号** - 数据库验证失败时，使用演示账号
3. **万能演示密码** - 任何用户名+密码"demo"都能登录

这样既保证了MongoDB的正常使用，又提供了演示功能的备选方案。
