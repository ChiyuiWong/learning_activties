#!/usr/bin/env python3
"""
启动学习管理系统
"""
import os
import sys
import subprocess
import webbrowser
from threading import Timer

def start_server():
    """启动服务器"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    print("🚀 启动学习管理系统...")
    print("📊 后端 API: http://localhost:5000/api")
    print("🌐 前端界面: http://localhost:5000")
    print()
    print("测试账号:")
    print("👨‍🏫 教师: teacher1/password123")
    print("👨‍🎓 学生: student1/password123")
    print()
    print("按 Ctrl+C 停止服务器...")
    
    try:
        # 切换到后端目录
        os.chdir(backend_dir)
        
        # 启动服务器
        from app import create_app
        from app.config.config import TestConfig
        
        app = create_app(TestConfig)
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 请检查依赖是否正确安装")
        return False

def open_browser():
    """打开浏览器"""
    try:
        webbrowser.open('http://localhost:5000')
    except:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print("🎓 学习管理系统")
    print("=" * 60)
    print()
    
    # 延迟打开浏览器
    timer = Timer(3.0, open_browser)
    timer.start()
    
    # 启动服务器
    start_server()
