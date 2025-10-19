#!/usr/bin/env python3
"""
测试MongoDB连接并设置投票数据
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pymongo
from datetime import datetime
from bson import ObjectId

def test_mongodb_connection():
    """测试MongoDB连接并创建示例数据"""
    try:
        # 连接到MongoDB
        client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
        db = client['comp5241_g10']
        polls_collection = db.polls
        
        print("✅ 成功连接到MongoDB")
        
        # 清空现有投票数据
        polls_collection.delete_many({})
        print("🗑️ 清空现有投票数据")
        
        # 插入示例投票数据
        sample_polls = [
            {
                'question': 'What is your favorite programming language?',
                'options': [
                    {'text': 'Python', 'votes': 15},
                    {'text': 'JavaScript', 'votes': 12},
                    {'text': 'Java', 'votes': 8},
                    {'text': 'C++', 'votes': 5}
                ],
                'course_id': 'COMP5241',
                'created_by': 'teacher1',
                'created_at': datetime.utcnow(),
                'is_active': True,
                'allow_multiple_votes': False
            },
            {
                'question': 'Which development framework do you prefer?',
                'options': [
                    {'text': 'React', 'votes': 18},
                    {'text': 'Vue.js', 'votes': 10},
                    {'text': 'Angular', 'votes': 7}
                ],
                'course_id': 'COMP5241',
                'created_by': 'teacher1',
                'created_at': datetime.utcnow(),
                'is_active': True,
                'allow_multiple_votes': False
            }
        ]
        
        # 插入投票数据
        result = polls_collection.insert_many(sample_polls)
        print(f"📊 成功插入 {len(result.inserted_ids)} 个投票到MongoDB")
        
        # 验证数据
        count = polls_collection.count_documents({})
        print(f"📈 数据库中现在有 {count} 个投票")
        
        # 显示投票列表
        print("\n📋 投票列表:")
        for poll in polls_collection.find({}):
            total_votes = sum(option['votes'] for option in poll['options'])
            print(f"  - {poll['question']} ({total_votes} 票)")
            for option in poll['options']:
                print(f"    • {option['text']}: {option['votes']} 票")
        
        client.close()
        print("\n🎉 MongoDB连接测试成功！")
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ 无法连接到MongoDB服务器")
        print("请确保MongoDB正在运行在 127.0.0.1:27017")
        return False
    except Exception as e:
        print(f"❌ 测试MongoDB时出错: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试MongoDB连接...")
    success = test_mongodb_connection()
    if success:
        print("\n✅ 现在可以测试创建新投票功能了！")
    else:
        print("\n❌ MongoDB连接失败，请检查服务器状态")

