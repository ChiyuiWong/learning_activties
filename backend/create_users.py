#!/usr/bin/env python3
"""
COMP5241 Group 10 - User Management Tool
用于在MongoDB中创建用户账号的管理工具
"""

import os
import sys
import base64
import datetime
import uuid
from getpass import getpass

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import pymongo
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get MongoDB connection"""
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/comp5241_g10')
    client = pymongo.MongoClient(mongodb_uri)
    return client

def create_activation_code(email, first_name, last_name, role):
    """创建激活码 - 第一步"""
    activation_id = str(uuid.uuid4())
    
    with get_db_connection() as client:
        db = client['comp5241_g10']
        
        # 检查邮箱是否已存在
        existing = db["new_users"].find_one({"email": email})
        if existing:
            print(f"❌ 邮箱 {email} 已存在激活码: {existing['_id']}")
            return existing['_id']
        
        # 创建新的激活码
        new_user_doc = {
            "_id": activation_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        
        db["new_users"].insert_one(new_user_doc)
        print(f"✅ 激活码创建成功: {activation_id}")
        print(f"   邮箱: {email}")
        print(f"   姓名: {first_name} {last_name}")
        print(f"   角色: {role}")
        
        return activation_id

def create_user_directly(username, password, email, first_name, last_name, role):
    """直接创建用户账号 - 跳过激活码流程"""
    
    # 检查是否有加密密钥
    if not os.environ.get("PW_HASH_ENC_KEY"):
        print("❌ 缺少 PW_HASH_ENC_KEY 环境变量")
        print("请在 .env 文件中设置: PW_HASH_ENC_KEY=<32字节的base64编码密钥>")
        
        # 生成一个新的密钥
        key = os.urandom(32)
        key_b64 = base64.b64encode(key).decode('utf-8')
        print(f"建议使用这个密钥: PW_HASH_ENC_KEY={key_b64}")
        return False
    
    with get_db_connection() as client:
        db = client['comp5241_g10']
        
        # 检查用户名是否已存在
        existing = db["users"].find_one({"username": username})
        if existing:
            print(f"❌ 用户名 {username} 已存在")
            return False
        
        # 生成密码哈希和加密
        salt = os.urandom(16)
        iv = os.urandom(16)
        
        # 使用bcrypt生成密码哈希
        hashed_pw = bcrypt.kdf(
            password=password.encode("utf-8"),
            salt=salt,
            desired_key_bytes=32,
            rounds=1000
        )
        
        # 使用AES加密密码哈希
        cipher = Cipher(
            algorithms.AES(base64.b64decode(os.environ.get("PW_HASH_ENC_KEY"))), 
            modes.CBC(iv)
        )
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_plaintext = padder.update(hashed_pw) + padder.finalize()
        pw_ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        # 创建用户文档
        user_doc = {
            "_id": username,
            "username": username,
            "email": email,
            "encrypted_pw_hash": pw_ciphertext,
            "encrypted_pw_hash_iv": iv,
            "pw_hash_salt": salt,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        
        db["users"].insert_one(user_doc)
        print(f"✅ 用户创建成功!")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email}")
        print(f"   姓名: {first_name} {last_name}")
        print(f"   角色: {role}")
        
        return True

def list_users():
    """列出所有用户"""
    with get_db_connection() as client:
        db = client['comp5241_g10']
        
        print("\n📋 现有用户列表:")
        print("-" * 80)
        users = db["users"].find({})
        count = 0
        for user in users:
            count += 1
            print(f"{count}. 用户名: {user['username']}")
            print(f"   邮箱: {user.get('email', 'N/A')}")
            print(f"   姓名: {user.get('first_name', '')} {user.get('last_name', '')}")
            print(f"   角色: {user.get('role', 'N/A')}")
            print(f"   状态: {'激活' if user.get('is_active') else '未激活'}")
            print(f"   创建时间: {user.get('created_at', 'N/A')}")
            print("-" * 40)
        
        if count == 0:
            print("   (暂无用户)")
        
        print(f"\n总计: {count} 个用户")

def list_activation_codes():
    """列出所有激活码"""
    with get_db_connection() as client:
        db = client['comp5241_g10']
        
        print("\n🔑 现有激活码列表:")
        print("-" * 80)
        codes = db["new_users"].find({})
        count = 0
        for code in codes:
            count += 1
            print(f"{count}. 激活码: {code['_id']}")
            print(f"   邮箱: {code.get('email', 'N/A')}")
            print(f"   姓名: {code.get('first_name', '')} {code.get('last_name', '')}")
            print(f"   角色: {code.get('role', 'N/A')}")
            print(f"   创建时间: {code.get('created_at', 'N/A')}")
            print("-" * 40)
        
        if count == 0:
            print("   (暂无激活码)")
        
        print(f"\n总计: {count} 个激活码")

def create_demo_users():
    """创建演示用户"""
    demo_users = [
        {
            "username": "teacher1",
            "password": "password123",
            "email": "teacher1@comp5241.edu",
            "first_name": "张",
            "last_name": "老师",
            "role": "teacher"
        },
        {
            "username": "student1", 
            "password": "password123",
            "email": "student1@comp5241.edu",
            "first_name": "李",
            "last_name": "同学",
            "role": "student"
        },
        {
            "username": "admin1",
            "password": "password123", 
            "email": "admin1@comp5241.edu",
            "first_name": "系统",
            "last_name": "管理员",
            "role": "admin"
        }
    ]
    
    print("🚀 创建演示用户...")
    success_count = 0
    
    for user in demo_users:
        if create_user_directly(**user):
            success_count += 1
    
    print(f"\n✅ 成功创建 {success_count}/{len(demo_users)} 个演示用户")

def main():
    """主菜单"""
    while True:
        print("\n" + "="*60)
        print("🎓 COMP5241 用户管理工具")
        print("="*60)
        print("1. 📝 创建激活码 (两步注册流程)")
        print("2. 👤 直接创建用户 (跳过激活码)")
        print("3. 📋 查看所有用户")
        print("4. 🔑 查看所有激活码")
        print("5. 🚀 创建演示用户")
        print("6. ❌ 退出")
        print("-"*60)
        
        choice = input("请选择操作 (1-6): ").strip()
        
        if choice == "1":
            print("\n📝 创建激活码")
            email = input("邮箱: ").strip()
            first_name = input("名字: ").strip()
            last_name = input("姓氏: ").strip()
            print("角色选择: student, teacher, admin")
            role = input("角色: ").strip()
            
            if role not in ["student", "teacher", "admin"]:
                print("❌ 无效角色")
                continue
                
            create_activation_code(email, first_name, last_name, role)
            
        elif choice == "2":
            print("\n👤 直接创建用户")
            username = input("用户名: ").strip()
            password = getpass("密码: ")
            email = input("邮箱: ").strip()
            first_name = input("名字: ").strip()
            last_name = input("姓氏: ").strip()
            print("角色选择: student, teacher, admin")
            role = input("角色: ").strip()
            
            if role not in ["student", "teacher", "admin"]:
                print("❌ 无效角色")
                continue
                
            create_user_directly(username, password, email, first_name, last_name, role)
            
        elif choice == "3":
            list_users()
            
        elif choice == "4":
            list_activation_codes()
            
        elif choice == "5":
            create_demo_users()
            
        elif choice == "6":
            print("👋 再见!")
            break
            
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
