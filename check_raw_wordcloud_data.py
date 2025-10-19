#!/usr/bin/env python3
"""
检查词云原始数据
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.database import get_db_connection
from bson import ObjectId

def check_wordcloud_data():
    """检查词云原始数据"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            
            # 获取词云数据
            wordcloud_id = "68f1d0c27a93ac676124ea2d"
            wordcloud = db.word_clouds.find_one({'_id': ObjectId(wordcloud_id)})
            
            if not wordcloud:
                print("词云不存在")
                return
            
            print(f"词云标题: {wordcloud.get('title', 'N/A')}")
            print(f"提示问题: {wordcloud.get('prompt', 'N/A')}")
            
            submissions = wordcloud.get('submissions', [])
            print(f"总提交数: {len(submissions)}")
            
            print("\n最近20个提交的原始数据:")
            print("-" * 60)
            
            for i, submission in enumerate(submissions[-20:], 1):
                word = submission.get('word', 'N/A')
                user = submission.get('submitted_by', 'N/A')
                time = submission.get('submitted_at', 'N/A')
                
                # 检查是否为英文
                is_english = word.encode('ascii', errors='ignore').decode('ascii') == word
                lang_indicator = "[EN]" if is_english else "[CN]"
                
                print(f"{i:2d}. {lang_indicator} '{word}' - 用户: {user} - 时间: {time}")
            
            # 统计英文和中文词汇
            english_count = 0
            chinese_count = 0
            
            for submission in submissions:
                word = submission.get('word', '')
                if word.encode('ascii', errors='ignore').decode('ascii') == word:
                    english_count += 1
                else:
                    chinese_count += 1
            
            print(f"\n统计:")
            print(f"英文词汇: {english_count}")
            print(f"中文词汇: {chinese_count}")
            print(f"总计: {len(submissions)}")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    check_wordcloud_data()

