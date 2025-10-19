#!/usr/bin/env python3
"""
临时修复词云认证问题的脚本
"""
import sys
import os

# 添加后端目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from flask import Flask, request, jsonify
from config.database import get_db_connection
from bson import ObjectId
import requests

def create_temp_app():
    """创建临时应用来测试词云功能"""
    app = Flask(__name__)
    
    @app.route('/api/learning/wordclouds/', methods=['GET'])
    def list_wordclouds():
        """获取词云列表（无认证）"""
        try:
            course_id = request.args.get('course_id')
            
            with get_db_connection() as client:
                db = client['comp5241_g10']
                query = {'is_active': True}
                if course_id:
                    query['course_id'] = course_id
                
                wordclouds = list(db.word_clouds.find(query).sort('created_at', -1))
            
            result = []
            for wc in wordclouds:
                submissions = wc.get('submissions', [])
                word_freq = {}
                for submission in submissions:
                    word = submission.get('word', '').lower()
                    word_freq[word] = word_freq.get(word, 0) + 1
                
                wc_data = {
                    'id': str(wc['_id']),
                    'title': wc['title'],
                    'prompt': wc['prompt'],
                    'submission_count': len(submissions),
                    'unique_words': len(word_freq),
                    'created_by': wc['created_by'],
                    'is_active': wc['is_active'],
                    'created_at': wc['created_at'].isoformat(),
                    'expires_at': wc['expires_at'].isoformat() if wc.get('expires_at') else None,
                    'course_id': wc['course_id'],
                    'max_submissions_per_user': wc['max_submissions_per_user'],
                    'is_expired': False,
                    'user_stats': {
                        'submissions_count': 0,
                        'submissions_remaining': -1,
                        'unlimited_submissions': True
                    }
                }
                result.append(wc_data)
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/learning/wordclouds/<wordcloud_id>/submit', methods=['POST'])
    def submit_word(wordcloud_id):
        """提交词汇（无认证）"""
        try:
            data = request.get_json()
            if not data or 'word' not in data:
                return jsonify({'error': 'Missing word submission'}), 400
            
            word = data['word'].strip()
            if not word:
                return jsonify({'error': 'Word cannot be empty'}), 400
            
            user_id = 'test_user'  # 临时用户ID
            
            with get_db_connection() as client:
                db = client['comp5241_g10']
                wordcloud = db.word_clouds.find_one({'_id': ObjectId(wordcloud_id)})
                
                if not wordcloud:
                    return jsonify({'error': 'Word cloud not found'}), 404
                
                # 创建提交记录
                submission = {
                    'word': word,
                    'submitted_by': user_id,
                    'submitted_at': datetime.utcnow()
                }
                
                # 添加到数据库
                db.word_clouds.update_one(
                    {'_id': ObjectId(wordcloud_id)},
                    {'$push': {'submissions': submission}}
                )
                
                return jsonify({
                    'message': 'Word submitted successfully',
                    'word': word,
                    'submissions_remaining': -1,
                    'unlimited_submissions': True
                }), 200
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

def test_temp_api():
    """测试临时API"""
    print("=== 测试临时词云API ===")
    
    # 启动临时服务器
    app = create_temp_app()
    
    # 测试词云列表
    with app.test_client() as client:
        print("\n1. 测试词云列表:")
        response = client.get('/api/learning/wordclouds/?course_id=COMP5241')
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   词云数量: {len(data)}")
            for wc in data:
                print(f"     - {wc.get('title', 'Unknown')}: {wc.get('submission_count', 0)} 个提交")
        else:
            print(f"   错误: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_temp_api()
