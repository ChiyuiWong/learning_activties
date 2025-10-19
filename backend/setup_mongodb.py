#!/usr/bin/env python3
"""
COMP5241 Group 10 - MongoDB Setup Script
用于初始化MongoDB数据库和集合的脚本
"""

import os
import sys
import base64
from dotenv import load_dotenv
import pymongo

load_dotenv()

def setup_mongodb():
    """设置MongoDB数据库和集合"""
    
    # 生成加密密钥
    if not os.environ.get("PW_HASH_ENC_KEY"):
        key = os.urandom(32)
        key_b64 = base64.b64encode(key).decode('utf-8')
        print("🔑 生成密码加密密钥:")
        print(f"PW_HASH_ENC_KEY={key_b64}")
        print("\n请将此密钥添加到 .env 文件中")
        
        # 创建 .env 文件
        env_content = f"""# COMP5241 Group 10 - Environment Configuration
MONGODB_URI=mongodb://localhost:27017/comp5241_g10
PW_HASH_ENC_KEY={key_b64}
JWT_SECRET_KEY=your_jwt_secret_key_here
DISABLE_AUTH=false
FLASK_ENV=development
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env 文件已创建")
    
    # 连接MongoDB
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/comp5241_g10')
    
    try:
        client = pymongo.MongoClient(mongodb_uri)
        db = client['comp5241_g10']
        
        # 测试连接
        client.admin.command('ping')
        print(f"✅ MongoDB连接成功: {mongodb_uri}")
        
        # 创建集合和索引
        collections_to_create = [
            'users',           # 用户账号
            'new_users',       # 激活码
            'courses',         # 课程
            'quizzes',         # 测验
            'polls',           # 投票
            'wordclouds',      # 词云
            'shortanswers',    # 简答题
            'sessions',        # 会话
            'logs'             # 日志
        ]
        
        for collection_name in collections_to_create:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"✅ 创建集合: {collection_name}")
            else:
                print(f"ℹ️  集合已存在: {collection_name}")
        
        # 创建索引
        print("\n🔍 创建索引...")
        
        # 用户集合索引
        db.users.create_index("username", unique=True)
        db.users.create_index("email")
        print("✅ users 集合索引创建完成")
        
        # 激活码集合索引
        db.new_users.create_index("email")
        print("✅ new_users 集合索引创建完成")
        
        # 学习活动集合索引
        for collection in ['quizzes', 'polls', 'wordclouds', 'shortanswers']:
            db[collection].create_index("course_id")
            db[collection].create_index("created_by")
            print(f"✅ {collection} 集合索引创建完成")
        
        print("\n🎉 MongoDB数据库设置完成!")
        print(f"数据库名称: comp5241_g10")
        print(f"集合数量: {len(collections_to_create)}")
        
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ 无法连接到MongoDB服务器")
        print("请确保MongoDB服务正在运行:")
        print("  - Windows: 启动MongoDB服务")
        print("  - macOS: brew services start mongodb-community")
        print("  - Linux: sudo systemctl start mongod")
        return False
        
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        return False

def check_mongodb_status():
    """检查MongoDB连接状态"""
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/comp5241_g10')
    
    try:
        client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db = client['comp5241_g10']
        collections = db.list_collection_names()
        
        print("✅ MongoDB状态检查:")
        print(f"   连接地址: {mongodb_uri}")
        print(f"   数据库: comp5241_g10")
        print(f"   集合数量: {len(collections)}")
        print(f"   集合列表: {', '.join(collections)}")
        
        # 检查用户数量
        user_count = db.users.count_documents({})
        activation_count = db.new_users.count_documents({})
        
        print(f"   用户数量: {user_count}")
        print(f"   激活码数量: {activation_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        return False

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    
    print("🎓 COMP5241 MongoDB设置工具")
    print("="*50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_mongodb_status()
    else:
        setup_mongodb()
