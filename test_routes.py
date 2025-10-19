#!/usr/bin/env python3
"""
测试Flask路由是否正确注册
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_routes():
    """测试路由注册"""
    try:
        from app import create_app
        
        print("[INFO] 创建Flask应用...")
        app = create_app()
        
        print("[INFO] 检查所有路由:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if 'wordcloud' in rule.rule.lower():
                    print(f"  ✅ {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
                elif 'learning' in rule.rule.lower():
                    print(f"  📚 {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
        
        print("[INFO] 测试完成")
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routes()
