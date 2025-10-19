#!/usr/bin/env python3
"""
检查路由注册情况
"""
import sys
import os

# 添加后端目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

def check_routes():
    """检查应用路由"""
    try:
        from app import create_app
        app = create_app()
        
        print("=== 所有词云相关路由 ===")
        wordcloud_routes = []
        for rule in app.url_map.iter_rules():
            if 'wordcloud' in rule.rule.lower():
                methods = '|'.join(rule.methods - {'HEAD', 'OPTIONS'})
                wordcloud_routes.append(f"{rule.rule} -> {rule.endpoint} [{methods}]")
        
        if wordcloud_routes:
            for route in sorted(wordcloud_routes):
                print(route)
        else:
            print("❌ 没有找到词云相关路由！")
        
        print(f"\n总共找到 {len(wordcloud_routes)} 个词云路由")
        
        # 检查特定的问题路由
        problem_routes = [
            '/api/learning/wordclouds/<wordcloud_id>/my-submissions',
            '/api/learning/wordclouds/<wordcloud_id>/submit'
        ]
        
        print("\n=== 检查问题路由 ===")
        for problem_route in problem_routes:
            found = False
            for rule in app.url_map.iter_rules():
                if rule.rule == problem_route:
                    methods = '|'.join(rule.methods - {'HEAD', 'OPTIONS'})
                    print(f"✅ {problem_route} -> {rule.endpoint} [{methods}]")
                    found = True
                    break
            if not found:
                print(f"❌ {problem_route} - 未找到")
        
    except Exception as e:
        print(f"检查路由失败: {e}")

if __name__ == "__main__":
    check_routes()
