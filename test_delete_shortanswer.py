#!/usr/bin/env python3
"""
测试短答题删除功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from config.database import get_db_connection
from bson import ObjectId

def test_delete_shortanswer():
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            shortanswers_collection = db.shortanswers
            
            # 获取删除前的短答题数量
            before_count = shortanswers_collection.count_documents({})
            print(f"删除前短答题数量: {before_count}")
            
            # 获取所有短答题
            questions = list(shortanswers_collection.find())
            
            if questions:
                # 选择第一个短答题进行删除测试
                test_question = questions[0]
                test_id = test_question['_id']
                print(f"准备删除的短答题:")
                print(f"  ID: {test_id}")
                print(f"  标题: {test_question.get('title', 'N/A')}")
                print(f"  题目: {test_question.get('question', 'N/A')}")
                
                # 执行删除
                result = shortanswers_collection.delete_one({'_id': test_id})
                print(f"删除操作结果: {result.deleted_count} 个文档被删除")
                
                # 获取删除后的短答题数量
                after_count = shortanswers_collection.count_documents({})
                print(f"删除后短答题数量: {after_count}")
                
                if before_count - after_count == 1:
                    print("✅ 删除功能正常工作")
                else:
                    print("❌ 删除功能有问题")
                    
                # 恢复删除的数据（用于测试）
                shortanswers_collection.insert_one(test_question)
                print("已恢复测试数据")
                
            else:
                print("数据库中没有短答题数据可供测试")
                
    except Exception as e:
        print(f"测试删除功能时出错: {e}")

if __name__ == "__main__":
    test_delete_shortanswer()
