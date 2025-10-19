#!/usr/bin/env python3
"""
检查词云数据库数据
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from config.database import get_db_connection
from bson import ObjectId

def check_wordcloud_data():
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            wordclouds_collection = db.word_clouds
            
            # 获取所有词云
            wordclouds = list(wordclouds_collection.find())
            
            print(f"数据库中共有 {len(wordclouds)} 个词云:")
            print("=" * 60)
            
            for i, wordcloud in enumerate(wordclouds, 1):
                print(f"{i}. ID: {wordcloud['_id']}")
                print(f"   标题: {wordcloud.get('title', 'N/A')}")
                print(f"   提示: {wordcloud.get('prompt', 'N/A')}")
                print(f"   课程: {wordcloud.get('course_id', 'N/A')}")
                print(f"   创建时间: {wordcloud.get('created_at', 'N/A')}")
                print(f"   是否活跃: {wordcloud.get('is_active', 'N/A')}")
                
                # 检查提交数据
                submissions = wordcloud.get('submissions', [])
                print(f"   提交数据: {len(submissions)} 个提交")
                
                if submissions:
                    print("   提交详情:")
                    for j, submission in enumerate(submissions[:5], 1):  # 只显示前5个
                        word = submission.get('word', 'N/A')
                        user = submission.get('submitted_by', 'N/A')
                        time = submission.get('submitted_at', 'N/A')
                        print(f"     {j}. 词汇: '{word}' | 用户: {user} | 时间: {time}")
                    if len(submissions) > 5:
                        print(f"     ... 还有 {len(submissions) - 5} 个提交")
                else:
                    print("   没有提交数据")
                
                print("-" * 40)
                
            if not wordclouds:
                print("数据库中没有词云数据")
                
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_wordcloud_data()
