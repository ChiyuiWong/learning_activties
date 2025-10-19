#!/usr/bin/env python3
"""
清除词云提交记录的工具脚本
用于解决用户达到提交次数限制的问题
"""
import sys
import os

# 添加后端目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from config.database import get_db_connection
from bson import ObjectId

def clear_user_wordcloud_submissions(user_id=None, wordcloud_id=None):
    """
    清除用户的词云提交记录
    
    Args:
        user_id: 用户ID，如果为None则清除所有用户的提交
        wordcloud_id: 词云ID，如果为None则清除所有词云的提交
    """
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            
            if wordcloud_id:
                # 清除特定词云的提交记录
                if user_id:
                    # 清除特定用户在特定词云的提交
                    result = db.word_clouds.update_one(
                        {'_id': ObjectId(wordcloud_id)},
                        {'$pull': {'submissions': {'submitted_by': user_id}}}
                    )
                    print(f"✅ 已清除用户 {user_id} 在词云 {wordcloud_id} 的提交记录")
                else:
                    # 清除特定词云的所有提交
                    result = db.word_clouds.update_one(
                        {'_id': ObjectId(wordcloud_id)},
                        {'$set': {'submissions': []}}
                    )
                    print(f"✅ 已清除词云 {wordcloud_id} 的所有提交记录")
            else:
                # 清除所有词云的提交记录
                if user_id:
                    # 清除特定用户的所有词云提交
                    result = db.word_clouds.update_many(
                        {},
                        {'$pull': {'submissions': {'submitted_by': user_id}}}
                    )
                    print(f"✅ 已清除用户 {user_id} 的所有词云提交记录，影响 {result.modified_count} 个词云")
                else:
                    # 清除所有词云的所有提交
                    result = db.word_clouds.update_many(
                        {},
                        {'$set': {'submissions': []}}
                    )
                    print(f"✅ 已清除所有词云的提交记录，影响 {result.modified_count} 个词云")
                    
    except Exception as e:
        print(f"❌ 清除失败: {e}")
        return False
    
    return True

def list_wordcloud_submissions():
    """列出所有词云及其提交情况"""
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            
            wordclouds = db.word_clouds.find({})
            
            print("\n词云提交情况：")
            print("=" * 80)
            
            for wc in wordclouds:
                submissions = wc.get('submissions', [])
                print(f"\n词云: {wc.get('title', 'Unknown')}")
                print(f"   ID: {wc['_id']}")
                print(f"   总提交数: {len(submissions)}")
                print(f"   每用户限制: {wc.get('max_submissions_per_user', 3)}")
                
                # 按用户统计提交数
                user_counts = {}
                for sub in submissions:
                    user_id = sub.get('submitted_by', 'Unknown')
                    user_counts[user_id] = user_counts.get(user_id, 0) + 1
                
                if user_counts:
                    print("   用户提交统计:")
                    for user_id, count in user_counts.items():
                        status = "[已达限制]" if count >= wc.get('max_submissions_per_user', 3) else "[可继续提交]"
                        print(f"     - {user_id}: {count} 次 {status}")
                        
                        # 显示该用户提交的词汇
                        user_words = [s.get('word', '') for s in submissions if s.get('submitted_by') == user_id]
                        if user_words:
                            print(f"       词汇: {', '.join(user_words)}")
                else:
                    print("   暂无提交记录")
                    
    except Exception as e:
        print(f"❌ 查询失败: {e}")

def main():
    """主函数"""
    print("词云提交记录管理工具")
    print("=" * 50)
    
    # 首先显示当前状态
    list_wordcloud_submissions()
    
    print("\n" + "=" * 50)
    print("选择操作:")
    print("1. 清除特定用户的所有词云提交")
    print("2. 清除所有用户的所有词云提交") 
    print("3. 清除特定词云的所有提交")
    print("4. 仅查看当前状态")
    print("0. 退出")
    
    choice = input("\n请输入选择 (0-4): ").strip()
    
    if choice == "1":
        user_id = input("请输入用户ID (例如: alice.wang): ").strip()
        if user_id:
            if clear_user_wordcloud_submissions(user_id=user_id):
                print(f"\n✅ 用户 {user_id} 现在可以重新提交词汇了！")
            
    elif choice == "2":
        confirm = input("⚠️  确认清除所有提交记录？这将影响所有用户！(yes/no): ").strip().lower()
        if confirm == "yes":
            if clear_user_wordcloud_submissions():
                print("\n✅ 所有用户现在都可以重新提交词汇了！")
        else:
            print("❌ 操作已取消")
            
    elif choice == "3":
        wordcloud_id = input("请输入词云ID: ").strip()
        if wordcloud_id:
            if clear_user_wordcloud_submissions(wordcloud_id=wordcloud_id):
                print(f"\n✅ 词云 {wordcloud_id} 的提交记录已清除！")
                
    elif choice == "4":
        print("\n✅ 状态查看完成")
        
    elif choice == "0":
        print("👋 再见！")
        
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
