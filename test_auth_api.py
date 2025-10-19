#!/usr/bin/env python3
"""
测试带认证的API调用
"""
import requests
import json

def test_authenticated_api():
    """测试带认证的API调用"""
    base_url = "http://127.0.0.1:5001"
    
    # 使用与前端相同的JWT token
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbGljZS53YW5nIiwiaWF0IjoxNjk5MzQ0MDAwLCJleHAiOjE3MzA4ODAwMDAsInJvbGUiOiJzdHVkZW50IiwidXNlcm5hbWUiOiJhbGljZS53YW5nIn0.test"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    cookies = {
        "access_token_cookie": token
    }
    
    print("=== 测试带认证的API调用 ===\n")
    
    # 1. 测试词云列表
    print("1. 测试词云列表:")
    try:
        response = requests.get(f"{base_url}/api/learning/wordclouds/?course_id=COMP5241", 
                              headers=headers, cookies=cookies)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   词云数量: {len(data)}")
            for wc in data:
                print(f"     - {wc.get('title', 'Unknown')}: {wc.get('submission_count', 0)} 个提交")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 2. 测试词云详情
    wordcloud_id = "68f1d0c27a93ac676124ea2d"
    print(f"\n2. 测试词云详情 (ID: {wordcloud_id}):")
    try:
        response = requests.get(f"{base_url}/api/learning/wordclouds/{wordcloud_id}", 
                              headers=headers, cookies=cookies)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   标题: {data.get('title', 'Unknown')}")
            print(f"   用户提交: {len(data.get('user_submissions', []))}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 3. 测试用户提交记录
    print(f"\n3. 测试用户提交记录:")
    try:
        response = requests.get(f"{base_url}/api/learning/wordclouds/{wordcloud_id}/my-submissions", 
                              headers=headers, cookies=cookies)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   用户提交数量: {len(data)}")
            for submission in data:
                print(f"     - {submission.get('word', 'Unknown')}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 4. 测试提交新词汇
    print(f"\n4. 测试提交新词汇:")
    try:
        response = requests.post(f"{base_url}/api/learning/wordclouds/{wordcloud_id}/submit", 
                               headers=headers, cookies=cookies,
                               json={"word": "测试词汇"})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   提交成功: {data.get('message', 'Unknown')}")
            print(f"   提交的词汇: {data.get('word', 'Unknown')}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")

if __name__ == "__main__":
    test_authenticated_api()
