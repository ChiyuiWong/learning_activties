#!/usr/bin/env python3
"""
测试无认证的API调用
"""
import requests
import json

def test_no_auth_api():
    """测试无认证的API调用"""
    base_url = "http://127.0.0.1:5001"
    
    print("=== 测试无认证API调用 ===\n")
    
    # 1. 测试词云列表
    print("1. 测试词云列表:")
    try:
        response = requests.get(f"{base_url}/api/learning/wordclouds/?course_id=COMP5241")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   词云数量: {len(data)}")
            for wc in data:
                print(f"     - {wc.get('title', 'Unknown')}: {wc.get('submission_count', 0)} 个提交")
        else:
            print(f"   错误: {response.text[:200]}...")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 2. 测试词云详情
    wordcloud_id = "68f1d0c27a93ac676124ea2d"
    print(f"\n2. 测试词云详情:")
    try:
        response = requests.get(f"{base_url}/api/learning/wordclouds/{wordcloud_id}")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   标题: {data.get('title', 'Unknown')}")
            print(f"   用户提交: {len(data.get('user_submissions', []))}")
        else:
            print(f"   错误: {response.text[:200]}...")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 3. 测试提交词汇
    print(f"\n3. 测试提交词汇:")
    try:
        response = requests.post(f"{base_url}/api/learning/wordclouds/{wordcloud_id}/submit",
                               json={"word": "无认证测试"})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   提交成功: {data.get('message', 'Unknown')}")
        else:
            print(f"   错误: {response.text[:200]}...")
    except Exception as e:
        print(f"   异常: {e}")

if __name__ == "__main__":
    test_no_auth_api()
