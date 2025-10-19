#!/usr/bin/env python3
"""
对比测验、投票和词云的API调用
"""
import requests
import json

def test_api_endpoints():
    """测试不同功能的API端点"""
    base_url = "http://127.0.0.1:5001"
    
    print("=== 对比API端点测试 ===\n")
    
    # 测试认证头
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    # 测试cookies
    cookies = {
        "access_token_cookie": "test-token"
    }
    
    endpoints = [
        # 测验相关
        ("GET", "/api/learning/quizzes/?course_id=COMP5241", "测验列表"),
        
        # 投票相关  
        ("GET", "/api/learning/polls/?course_id=COMP5241", "投票列表"),
        
        # 词云相关
        ("GET", "/api/learning/wordclouds/?course_id=COMP5241", "词云列表"),
        ("GET", "/api/learning/wordclouds/68f1d0c27a93ac676124ea2d", "词云详情"),
        ("GET", "/api/learning/wordclouds/68f1d0c27a93ac676124ea2d/my-submissions", "词云用户提交"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\n--- {description} ---")
        print(f"{method} {endpoint}")
        
        try:
            if method == "GET":
                # 测试不同的认证方式
                print("\n1. 无认证:")
                response = requests.get(f"{base_url}{endpoint}")
                print(f"   状态码: {response.status_code}")
                if response.status_code != 200:
                    print(f"   错误: {response.text[:100]}...")
                
                print("\n2. Header认证:")
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
                print(f"   状态码: {response.status_code}")
                if response.status_code != 200:
                    print(f"   错误: {response.text[:100]}...")
                
                print("\n3. Cookie认证:")
                response = requests.get(f"{base_url}{endpoint}", cookies=cookies)
                print(f"   状态码: {response.status_code}")
                if response.status_code != 200:
                    print(f"   错误: {response.text[:100]}...")
                else:
                    if endpoint.endswith("wordclouds/?course_id=COMP5241"):
                        data = response.json()
                        print(f"   成功! 词云数量: {len(data)}")
                        for wc in data:
                            print(f"     - {wc.get('title', 'Unknown')}: {wc.get('submission_count', 0)} 提交")
                
        except Exception as e:
            print(f"   请求异常: {e}")

if __name__ == "__main__":
    test_api_endpoints()
