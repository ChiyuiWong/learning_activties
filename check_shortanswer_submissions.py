#!/usr/bin/env python3
"""
检查短答题提交数据
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from config.database import get_db_connection
from bson import ObjectId

def check_shortanswer_submissions():
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            shortanswers_collection = db.shortanswers
            submissions_collection = db.shortanswer_submissions
            
            # 获取所有短答题
            questions = list(shortanswers_collection.find())
            
            print(f"数据库中共有 {len(questions)} 个短答题:")
            print("=" * 60)
            
            for i, question in enumerate(questions, 1):
                print(f"{i}. 短答题 ID: {question['_id']}")
                print(f"   标题: {question.get('title', 'N/A')}")
                print(f"   题目: {question.get('question', 'N/A')}")
                print(f"   课程: {question.get('course_id', 'N/A')}")
                
                # 查找该题目的提交数据
                submissions = list(submissions_collection.find({'question_id': question['_id']}))
                print(f"   提交数量: {len(submissions)}")
                
                if submissions:
                    print("   提交详情:")
                    for j, submission in enumerate(submissions, 1):
                        answer = submission.get('answer', 'N/A')
                        user_id = submission.get('user_id', 'N/A')
                        submitted_at = submission.get('submitted_at', 'N/A')
                        score = submission.get('score', 'N/A')
                        print(f"     {j}. 用户: {user_id}")
                        print(f"        答案: {answer[:100]}{'...' if len(str(answer)) > 100 else ''}")
                        print(f"        时间: {submitted_at}")
                        print(f"        分数: {score}")
                        print()
                else:
                    print("   没有提交数据")
                
                print("-" * 40)
                
            # 检查是否有孤立的提交数据（没有对应题目的）
            all_submissions = list(submissions_collection.find())
            question_ids = {q['_id'] for q in questions}
            orphaned_submissions = [s for s in all_submissions if s.get('question_id') not in question_ids]
            
            if orphaned_submissions:
                print(f"\n发现 {len(orphaned_submissions)} 个孤立的提交数据（没有对应的题目）:")
                for submission in orphaned_submissions:
                    print(f"  - 提交ID: {submission.get('_id')}")
                    print(f"    题目ID: {submission.get('question_id')}")
                    print(f"    用户: {submission.get('user_id')}")
                    print(f"    答案: {submission.get('answer', '')[:50]}...")
                    print()
                
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_shortanswer_submissions()
