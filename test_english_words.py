#!/usr/bin/env python3
"""
测试英文词汇提交功能
"""
import requests
import json

def test_english_word_validation():
    """测试英文词汇验证"""
    base_url = "http://127.0.0.1:5001/api/learning/wordclouds"
    
    # 使用一个测试的词云ID
    wordcloud_id = "test_wordcloud_id"
    
    # 测试不同类型的词汇
    test_words = [
        "hello",           # 简单英文单词
        "world",           # 另一个英文单词
        "machine learning", # 英文短语
        "AI",              # 英文缩写
        "data-science",    # 带连字符的英文
        "programming",     # 较长的英文单词
        "Python",          # 首字母大写
        "JavaScript",      # 混合大小写
        "你好",            # 中文词汇
        "hello world",     # 英文句子
        "123",             # 数字
        "hello123",        # 英文+数字
        "test@email",      # 包含特殊字符
        "",                # 空字符串
        "   ",             # 空格
        "a" * 60,          # 超长词汇
    ]
    
    print("开始测试英文词汇验证...")
    print("=" * 60)
    
    for word in test_words:
        print(f"\n测试词汇: '{word}'")
        
        try:
            response = requests.post(
                f"{base_url}/{wordcloud_id}/submit",
                json={"word": word},
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"OK 成功: {result.get('message', 'N/A')}")
                if 'cleaned_word' in result:
                    print(f"   清理后的词汇: '{result['cleaned_word']}'")
            else:
                try:
                    error_data = response.json()
                    print(f"FAIL 失败: {error_data.get('error', 'N/A')}")
                except:
                    print(f"FAIL 失败: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"EXCEPTION 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")

def test_word_validation_function():
    """直接测试validate_word函数"""
    import sys
    import os
    
    # 添加backend路径到sys.path
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    try:
        # 导入validate_word函数
        from app.modules.learning_activities.wordclouds_routes import validate_word
        
        test_words = [
            "hello",
            "world", 
            "machine learning",
            "AI",
            "data-science",
            "你好",
            "hello world",
            "123",
            "hello123",
            "test@email",
            "",
            "   ",
            "a" * 60,
        ]
        
        print("\n直接测试validate_word函数:")
        print("-" * 40)
        
        for word in test_words:
            cleaned_word, error = validate_word(word)
            if error:
                print(f"'{word}' -> FAIL {error}")
            else:
                print(f"'{word}' -> OK '{cleaned_word}'")
                
    except ImportError as e:
        print(f"无法导入validate_word函数: {e}")
        print("将使用API测试")

if __name__ == "__main__":
    # 先测试函数本身
    test_word_validation_function()
    
    # 再测试API
    print("\n" + "=" * 60)
    test_english_word_validation()
