#!/usr/bin/env python3
"""
调试投票创建问题
"""
import sys
import traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from config.database import get_db_connection
from datetime import datetime, timezone
from bson import ObjectId

def test_poll_creation():
    """测试投票创建"""
    try:
        print("🚀 开始测试投票创建...")
        
        # 测试数据
        data = {
            'question': 'MongoDB连接测试投票',
            'options': ['MongoDB', 'MySQL', 'PostgreSQL'],
            'course_id': 'COMP5241'
        }
        user_id = 'prof.smith'
        
        print(f"📝 投票问题: {data['question']}")
        print(f"🗳️ 选项: {data['options']}")
        
        # 连接MongoDB
        print("🔌 连接MongoDB...")
        with get_db_connection() as client:
            db = client['comp5241_g10']
            polls_collection = db.polls
            
            print("✅ MongoDB连接成功")
            
            # 准备投票数据
            poll_data = {
                'question': data['question'],
                'options': [{'text': opt, 'votes': 0} for opt in data['options']],
                'course_id': data.get('course_id', 'COMP5241'),
                'created_by': user_id or 'teacher1',
                'created_at': datetime.now(timezone.utc),
                'is_active': True,
                'allow_multiple_votes': data.get('allow_multiple_votes', False)
            }
            
            print("📊 准备投票数据:")
            for key, value in poll_data.items():
                if key == 'created_at':
                    print(f"  {key}: {value.isoformat()}")
                else:
                    print(f"  {key}: {value}")
            
            # 插入投票
            print("💾 插入投票到MongoDB...")
            result = polls_collection.insert_one(poll_data)
            poll_id = str(result.inserted_id)
            
            print(f"✅ 投票创建成功!")
            print(f"📊 MongoDB ObjectId: {poll_id}")
            
            # 验证插入
            inserted_poll = polls_collection.find_one({'_id': ObjectId(poll_id)})
            if inserted_poll:
                print("✅ 投票验证成功")
                print(f"📝 问题: {inserted_poll['question']}")
                print(f"🗳️ 选项数量: {len(inserted_poll['options'])}")
            else:
                print("❌ 投票验证失败")
            
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("🔍 详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_poll_creation()
    if success:
        print("\n🎉 投票创建测试成功！")
    else:
        print("\n💥 投票创建测试失败！")
