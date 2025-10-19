#!/usr/bin/env python3
"""
测试学生提交短答题答案
"""
import requests
import json

def test_submit_answer():
    # 使用真实的短答题ID
    question_ids = [
        "68f2110e642a96b61c6eeca8",  # 测试的
        "68f2111a642a96b61c6eecac"   # 测试题
    ]
    
    base_url = "http://127.0.0.1:5001/api/learning/shortanswers"
    
    # 测试答案
    test_answers = [
        "这是我对第一个问题的回答。我认为这个问题很有趣，需要深入思考。",
        "这是我对第二个问题的详细回答。我会从多个角度来分析这个问题。"
    ]
    
    print("开始测试学生提交答案...")
    print("=" * 50)
    
    for i, question_id in enumerate(question_ids):
        print(f"\n测试提交到问题 {i+1}: {question_id}")
        
        # 准备提交数据
        submit_data = {
            "answer": test_answers[i]
        }
        
        try:
            # 提交答案
            response = requests.post(
                f"{base_url}/{question_id}/submit",
                json=submit_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"提交状态: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 提交成功!")
            else:
                print("❌ 提交失败!")
                
        except Exception as e:
            print(f"❌ 提交出错: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！现在检查教师页面是否能看到提交的答案。")

if __name__ == "__main__":
    test_submit_answer()
