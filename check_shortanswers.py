#!/usr/bin/env python3
"""
检查短答题数据库数据
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from config.database import get_db_connection
from bson import ObjectId

def check_shortanswers():
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            shortanswers_collection = db.shortanswers
            
            # 获取所有短答题
            questions = list(shortanswers_collection.find())
            
            print(f"数据库中共有 {len(questions)} 个短答题:")
            print("=" * 50)
            
            for i, question in enumerate(questions, 1):
                print(f"{i}. ID: {question['_id']}")
                print(f"   标题: {question.get('title', 'N/A')}")
                print(f"   题目: {question.get('question', 'N/A')}")
                print(f"   课程: {question.get('course_id', 'N/A')}")
                print(f"   创建时间: {question.get('created_at', 'N/A')}")
                print(f"   是否活跃: {question.get('is_active', 'N/A')}")
                print("-" * 30)
                
            if not questions:
                print("数据库中没有短答题数据")
                
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_shortanswers()
