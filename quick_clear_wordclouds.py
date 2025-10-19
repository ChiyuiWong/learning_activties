#!/usr/bin/env python3
"""
快速清除所有词云提交记录
"""
import sys
import os

# 添加后端目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from config.database import get_db_connection

def clear_all_wordcloud_submissions():
    """清除所有词云的提交记录"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            
            # 清除所有词云的提交记录
            result = db.word_clouds.update_many(
                {},
                {'$set': {'submissions': []}}
            )
            
            print(f"成功清除 {result.modified_count} 个词云的提交记录")
            print("现在您可以重新提交词汇了！")
            
            return True
            
    except Exception as e:
        print(f"清除失败: {e}")
        return False

if __name__ == "__main__":
    print("清除所有词云提交记录...")
    clear_all_wordcloud_submissions()
