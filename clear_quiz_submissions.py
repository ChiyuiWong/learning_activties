#!/usr/bin/env python3
"""
清除测验提交记录的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config.database import get_db_connection

def clear_quiz_submissions():
    """清除所有测验提交记录"""
    try:
        client = get_db_connection()
        db = client['comp5241_g10']
        submissions_collection = db.quiz_submissions
        
        # 删除所有提交记录
        result = submissions_collection.delete_many({})
        
        print(f"[SUCCESS] 已清除 {result.deleted_count} 条测验提交记录")
        print("[INFO] 现在可以重新提交所有测验")
        
    except Exception as e:
        print(f"[ERROR] 清除提交记录失败: {e}")

if __name__ == "__main__":
    print("[INFO] 准备清除所有测验提交记录...")
    confirm = input("确定要清除所有测验提交记录吗？(y/N): ")
    
    if confirm.lower() == 'y':
        clear_quiz_submissions()
    else:
        print("[INFO] 操作已取消")
