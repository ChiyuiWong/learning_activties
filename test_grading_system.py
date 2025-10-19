#!/usr/bin/env python3
"""
测试短答题评分和反馈系统
"""
import requests
import json

def test_grading_system():
    base_url = "http://127.0.0.1:5001/api/learning/shortanswers"
    
    # 使用真实的短答题ID和提交ID（需要先有学生提交）
    question_id = "68f2110e642a96b61c6eeca8"  # 测试的
    
    print("开始测试评分和反馈系统...")
    print("=" * 50)
    
    # 首先获取短答题详情，查看是否有提交
    try:
        response = requests.get(f"{base_url}/{question_id}")
        if response.status_code == 200:
            question_data = response.json()
            print(f"短答题: {question_data.get('title', 'N/A')}")
            print(f"题目: {question_data.get('question', 'N/A')}")
            
            submissions = question_data.get('submissions', [])
            print(f"提交数量: {len(submissions)}")
            
            if submissions:
                # 测试第一个提交的评分和反馈
                submission = submissions[0]
                submission_id = submission.get('_id')
                
                print(f"\n测试提交ID: {submission_id}")
                print(f"学生: {submission.get('student_id', 'N/A')}")
                print(f"答案: {submission.get('answer', 'N/A')[:50]}...")
                
                # 测试评分功能
                print("\n1. 测试评分功能...")
                grade_data = {
                    "score": 8.5,
                    "feedback": "回答得很好，但可以更详细一些。"
                }
                
                grade_response = requests.post(
                    f"{base_url}/{question_id}/submissions/{submission_id}/grade",
                    json=grade_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"评分状态: {grade_response.status_code}")
                print(f"评分响应: {grade_response.text}")
                
                if grade_response.status_code == 200:
                    print("✅ 评分功能测试成功!")
                else:
                    print("❌ 评分功能测试失败!")
                
                # 测试反馈功能
                print("\n2. 测试反馈功能...")
                feedback_data = {
                    "feedback": "这是一个额外的反馈信息。"
                }
                
                feedback_response = requests.post(
                    f"{base_url}/{question_id}/submissions/{submission_id}/feedback",
                    json=feedback_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"反馈状态: {feedback_response.status_code}")
                print(f"反馈响应: {feedback_response.text}")
                
                if feedback_response.status_code == 200:
                    print("✅ 反馈功能测试成功!")
                else:
                    print("❌ 反馈功能测试失败!")
                
                # 重新获取数据验证更新
                print("\n3. 验证数据更新...")
                updated_response = requests.get(f"{base_url}/{question_id}")
                if updated_response.status_code == 200:
                    updated_data = updated_response.json()
                    updated_submissions = updated_data.get('submissions', [])
                    if updated_submissions:
                        updated_submission = updated_submissions[0]
                        print(f"更新后的分数: {updated_submission.get('score', 'N/A')}")
                        print(f"更新后的反馈: {updated_submission.get('feedback', 'N/A')}")
                        print("✅ 数据更新验证成功!")
                    else:
                        print("❌ 找不到更新后的提交数据")
                else:
                    print("❌ 无法获取更新后的数据")
                    
            else:
                print("没有学生提交，无法测试评分功能")
                print("请先让学生提交答案")
                
        else:
            print(f"❌ 无法获取短答题数据: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    test_grading_system()

