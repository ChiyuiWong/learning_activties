<<<<<<< Updated upstream
"""
COMP5241 Group 10 - Main Application Entry Point
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create app without database initialization
app = create_app()

if __name__ == '__main__':
    try:
        # Try to import and initialize database
        from database_connection import init_db
        print("Initializing database connection...")
        try:
            client, db = init_db.init_database()
            app.db_client = client
            app.db = db
            print("Database initialized successfully.")
        except Exception as e:
            print(f"WARNING: Database initialization failed: {e}")
            print("Continuing in mock database mode.")
            app.db = {}  # Use a simple dict as a mock DB
            app.config['USING_MOCK_DB'] = True
    except Exception as e:
        print(f"WARNING: Could not load database module: {e}")
        print("Continuing without database support.")
        app.db = {}  # Use a simple dict as a mock DB
        app.config['USING_MOCK_DB'] = True
            
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5001)
=======
"""
COMP5241 Group 10 - Main Application Entry Point
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create app without database initialization
app = create_app()

if __name__ == '__main__':
    # 设置Windows控制台编码
    if sys.platform == "win32":
        try:
            import locale
            locale.setlocale(locale.LC_ALL, 'Chinese (Simplified)_China.utf8')
        except:
            pass
    
    print("=" * 60)
    print("COMP5241 Group 10 - 学习管理系统")
    print("=" * 60)
    print()
    
    # 自动启动MongoDB
    print("检查MongoDB状态...")
    mongodb_ok = False
    try:
        import pymongo
        import subprocess
        import time
        from pathlib import Path
        
        # 快速检查MongoDB是否已经运行
        def quick_mongodb_check():
            try:
                client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=1000)
                client.server_info()
                client.close()
                return True
            except:
                return False
        
        if quick_mongodb_check():
            print("[OK] MongoDB已经在运行")
            mongodb_ok = True
        else:
            print("[INFO] MongoDB未运行，正在自动启动...")
            
            # 查找mongod可执行文件
            project_root = Path(__file__).parent.parent.parent
            mongodb_dir = project_root / "mongodb-win32-x86_64-windows-7.0.14" / "bin"
            mongod_path = mongodb_dir / "mongod.exe"
            config_file = project_root / "mongod.conf"
            
            if mongod_path.exists() and config_file.exists():
                try:
                    # 启动MongoDB
                    print(f"[INFO] 启动MongoDB: {mongod_path}")
                    process = subprocess.Popen(
                        [str(mongod_path), "--config", str(config_file)],
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    
                    # 等待MongoDB启动
                    print("[INFO] 等待MongoDB启动...")
                    for i in range(30):  # 等待最多30秒
                        time.sleep(1)
                        if quick_mongodb_check():
                            print("[OK] MongoDB启动成功!")
                            mongodb_ok = True
                            break
                        if i % 5 == 0:
                            print(f"[INFO] 等待中... ({i+1}/30)")
                    
                    if not mongodb_ok:
                        print("[ERROR] MongoDB启动超时")
                        print("[ERROR] 无法启动MongoDB，应用将退出")
                        
                except Exception as e:
                    print(f"[ERROR] MongoDB启动失败: {e}")
            else:
                print("[ERROR] MongoDB可执行文件或配置文件不存在")
                print(f"[INFO] 需要文件: {mongod_path}")
                print(f"[INFO] 需要文件: {config_file}")
                print("[ERROR] 无法找到MongoDB，应用将退出")
            
    except Exception as e:
        print(f"[ERROR] MongoDB自动启动失败: {e}")
    
    # 初始化数据库连接（必须使用MongoDB）
    print("初始化数据库连接...")
    
    if not mongodb_ok:
        print("[ERROR] MongoDB未启动，无法继续运行应用")
        print("[INFO] 请确保MongoDB正确安装并可以启动")
        print("[INFO] 或检查mongod.exe和mongod.conf文件是否存在")
        print("应用将在3秒后退出...")
        time.sleep(3)
        sys.exit(1)
    
    try:
        # Try to import and initialize database
        from database_connection import init_db
        try:
            client, db = init_db.init_database()
            app.db_client = client
            app.db = db
            print("[OK] MongoDB数据库连接成功")
        except Exception as e:
            print(f"[ERROR] MongoDB数据库连接失败: {e}")
            print("[ERROR] 应用无法在没有MongoDB的情况下运行")
            print("[INFO] 请检查MongoDB服务状态和配置")
            input("按回车键退出...")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 无法加载数据库模块: {e}")
        print("[ERROR] 应用无法在没有数据库支持的情况下运行")
        print("应用将在3秒后退出...")
        time.sleep(3)
        sys.exit(1)
    
    print()
    print("启动Flask应用...")
    print("后端API: http://127.0.0.1:5001/api")
    print("前端界面: http://127.0.0.1:5001")
    print("登录页面: http://127.0.0.1:5001/login.html")
    print()
    print("测试账号:")
    print("   教师: prof.smith/password (史密斯教授)")
    print("   教师: dr.johnson/password (约翰逊博士)")
    print("   学生: alice.wang/password (Alice Wang)")
    print("   学生: bob.chen/password (Bob Chen)")
    print("   学生: charlie.li/password (Charlie Li)")
    print()
    print("按 Ctrl+C 停止服务器...")
    print("=" * 60)
    
    # 延迟打开浏览器（只在第一次启动时打开）
    try:
        import webbrowser
        from threading import Timer
        import os
        
        # 检查是否是重新加载（debug模式会重启）
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            def open_browser():
                try:
                    webbrowser.open('http://127.0.0.1:5001/login.html')
                    print("浏览器已自动打开")
                except:
                    pass
            timer = Timer(3.0, open_browser)
            timer.start()
    except:
        pass
            
    # Run the Flask application
    try:
        print(f"[INFO] Flask应用启动在 http://127.0.0.1:5001")
        print(f"[INFO] 测试路由: http://127.0.0.1:5001/api/learning/wordclouds/test")
        # 开启debug模式以确保代码重新加载
        app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=True)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"\n[ERROR] 服务器启动失败: {e}")
        print("[INFO] 请检查端口5001是否被占用")
>>>>>>> Stashed changes
