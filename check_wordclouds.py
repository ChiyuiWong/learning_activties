#!/usr/bin/env python3
"""
检查词云数据的脚本
"""
import sys
import os

# 添加后端目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from config.database import get_db_connection

def check_wordclouds():
    """检查数据库中的词云数据"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            
            # 检查词云集合
            wordclouds = list(db.word_clouds.find({}))
            print(f"词云数量: {len(wordclouds)}")
            
            if wordclouds:
                print("\n现有词云:")
                for i, wc in enumerate(wordclouds[:5]):  # 只显示前5个
                    print(f"{i+1}. 标题: {wc.get('title', 'Unknown')}")
                    print(f"   ID: {wc['_id']}")
                    print(f"   创建者: {wc.get('created_by', 'Unknown')}")
                    print(f"   提交数: {len(wc.get('submissions', []))}")
                    print()
            else:
                print("❌ 数据库中没有词云数据！")
                print("这就是为什么提交失败的原因 - 没有可以提交的词云活动")
                
            # 检查其他集合
            quizzes = list(db.quizzes.find({}))
            polls = list(db.polls.find({}))
            
            print(f"测验数量: {len(quizzes)}")
            print(f"投票数量: {len(polls)}")
            
            if len(quizzes) > 0 and len(polls) > 0 and len(wordclouds) == 0:
                print("\n🔍 问题确认:")
                print("- 测验和投票有数据 ✅")
                print("- 词云没有数据 ❌")
                print("- 这就是为什么只有词云提交失败的原因！")
                
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_wordclouds()