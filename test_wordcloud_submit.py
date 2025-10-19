#!/usr/bin/env python3
"""
测试词云提交功能
"""
import sys
import os
import requests
import json

# 添加后端目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

def test_wordcloud_submit():
    """测试词云提交功能"""
    base_url = "http://127.0.0.1:5001"
    
    # 测试词云ID（从数据库中获取的）
    wordcloud_id = "68f1d0c27a93ac676124ea2d"  # 第二个词云的ID
    
    print("=== 测试词云提交功能 ===")
    
    # 1. 测试无认证的提交
    print("\n1. 测试无认证提交:")
    try:
        response = requests.post(
            f"{base_url}/api/learning/wordclouds/{wordcloud_id}/submit",
            json={"word": "测试词汇"},
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试获取词云信息
    print("\n2. 测试获取词云信息:")
    try:
        response = requests.get(f"{base_url}/api/learning/wordclouds/{wordcloud_id}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试获取用户提交记录
    print("\n3. 测试获取用户提交记录:")
    try:
        response = requests.get(f"{base_url}/api/learning/wordclouds/{wordcloud_id}/my-submissions")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 4. 测试词云列表
    print("\n4. 测试词云列表:")
    try:
        response = requests.get(f"{base_url}/api/learning/wordclouds/?course_id=COMP5241")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"词云数量: {len(data)}")
            for wc in data:
                print(f"- {wc.get('title', 'Unknown')}: {wc.get('submission_count', 0)} 个提交")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_wordcloud_submit()
