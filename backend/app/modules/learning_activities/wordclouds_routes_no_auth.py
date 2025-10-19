"""
COMP5241 Group 10 - Word Cloud Routes (No Authentication)
临时无认证版本，用于调试
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone
from bson import ObjectId
from config.database import get_db_connection
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

# Define a separate blueprint for word cloud endpoints
wordclouds_no_auth_bp = Blueprint('wordclouds_no_auth', __name__, url_prefix='/wordclouds-debug')

def validate_word(word):
    """Validate and clean a word submission"""
    if not word or not isinstance(word, str):
        return None, "Word must be a non-empty string"
    
    # Clean the word - 保持原始大小写，只去除首尾空格
    cleaned_word = word.strip()
    
    # 只替换多个连续空格为单个空格
    cleaned_word = re.sub(r'\s+', ' ', cleaned_word)
    
    if not cleaned_word:
        return None, "Word cannot be empty"
    
    if len(cleaned_word) < 1 or len(cleaned_word) > 50:
        return None, "Word must be between 1 and 50 characters"
    
    return cleaned_word, None

# List word clouds (NO AUTH)
@wordclouds_no_auth_bp.route('/', methods=['GET'])
def list_wordclouds_no_auth():
    try:
        user_id = 'debug_user'  # 固定用户ID
        course_id = request.args.get('course_id')
        include_expired = request.args.get('include_expired', 'false').lower() == 'true'
        
        # Build query
        query = {'is_active': True}
        if course_id:
            query['course_id'] = course_id

        # Filter expired word clouds unless specifically requested
        if not include_expired:
            now = datetime.now(timezone.utc)
            query['$or'] = [
                {'expires_at': None},
                {'expires_at': {'$gt': now}}
            ]

        # Sort by creation date (newest first)
        with get_db_connection() as client:
            db = client['comp5241_g10']
            wordclouds = list(db.word_clouds.find(query).sort('created_at', -1))
        result = []

        for wc in wordclouds:
            # Count user submissions
            user_submissions_count = len([s for s in wc.get('submissions', []) if s.get('submitted_by') == user_id])

            # Get word frequency
            submissions = wc.get('submissions', [])
            word_freq = {}
            for submission in submissions:
                word = submission.get('word', '').lower()
                word_freq[word] = word_freq.get(word, 0) + 1

            wc_data = {
                'id': str(wc['_id']),
                'title': wc['title'],
                'prompt': wc['prompt'],
                'submission_count': len(submissions),  # 使用 submission_count
                'unique_words': len(word_freq),
                'created_by': wc['created_by'],
                'is_active': wc['is_active'],
                'created_at': wc['created_at'].isoformat(),
                'expires_at': wc['expires_at'].isoformat() if wc.get('expires_at') else None,
                'course_id': wc['course_id'],
                'max_submissions_per_user': wc['max_submissions_per_user'],
                'is_expired': wc.get('expires_at') and wc['expires_at'] < datetime.utcnow(),
                'user_stats': {
                    'submissions_count': user_submissions_count,
                    'submissions_remaining': -1,  # 无限制
                    'unlimited_submissions': True
                }
            }
            result.append(wc_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error listing word clouds: {str(e)}")
        return jsonify({'error': 'Failed to retrieve word clouds', 'details': str(e)}), 500

# Get a specific word cloud (NO AUTH)
@wordclouds_no_auth_bp.route('/<wordcloud_id>', methods=['GET'])
def get_wordcloud_no_auth(wordcloud_id):
    try:
        user_id = 'debug_user'  # 固定用户ID
        
        # Check if it's a valid ObjectId format
        is_valid_objectid = len(wordcloud_id) == 24 and all(c in '0123456789abcdef' for c in wordcloud_id.lower())
        
        if is_valid_objectid:
            try:
                with get_db_connection() as client:
                    db = client['comp5241_g10']
                    wordcloud = db.word_clouds.find_one({'_id': ObjectId(wordcloud_id)})
                if not wordcloud:
                    return jsonify({'error': 'Word cloud not found'}), 404
            except Exception as db_error:
                logger.warning(f"Database operation failed: {db_error}")
                wordcloud = None
        else:
            wordcloud = None
        
        if not wordcloud:
            # Return dummy word cloud for non-ObjectId IDs or when database fails
            return jsonify({
                'id': wordcloud_id,
                'title': 'Sample Word Cloud',
                'prompt': 'Share words related to programming concepts',
                'created_by': 'teacher123',
                'is_active': True,
                'created_at': '2025-10-16T10:00:00Z',
                'expires_at': None,
                'course_id': 'COMP5241',
                'max_submissions_per_user': 3,
                'user_submissions': [],
                'submissions_remaining': -1,
                'unlimited_submissions': True
            }), 200

        # Get user's submissions
        user_submissions = [s['word'] for s in wordcloud.get('submissions', []) if s.get('submitted_by') == user_id]

        return jsonify({
            'id': str(wordcloud['_id']),
            'title': wordcloud['title'],
            'prompt': wordcloud['prompt'],
            'created_by': wordcloud['created_by'],
            'is_active': wordcloud['is_active'],
            'created_at': wordcloud['created_at'].isoformat(),
            'expires_at': wordcloud['expires_at'].isoformat() if wordcloud.get('expires_at') else None,
            'course_id': wordcloud['course_id'],
            'max_submissions_per_user': wordcloud['max_submissions_per_user'],
            'user_submissions': user_submissions,
            'submissions_remaining': -1,  # 无限制
            'unlimited_submissions': True
        }), 200
    except Exception:
        return jsonify({'error': 'Word cloud not found'}), 404

# Submit a word to the word cloud (NO AUTH)
@wordclouds_no_auth_bp.route('/<wordcloud_id>/submit', methods=['POST'])
def submit_word_no_auth(wordcloud_id):
    try:
        user_id = 'debug_user'  # 固定用户ID
        data = request.get_json()
        
        print(f"[INFO] ===== WORDCLOUD SUBMIT (NO AUTH) =====")
        print(f"[INFO] Wordcloud ID: {wordcloud_id}")
        print(f"[INFO] User ID: {user_id}")
        print(f"[INFO] Submit data: {data}")

        if not data or 'word' not in data:
            print(f"[ERROR] Missing word submission")
            return jsonify({'error': 'Missing word submission'}), 400

        # Validate and clean the word
        word, error = validate_word(data['word'])
        if error:
            return jsonify({'error': error}), 400

        # Check if it's a valid ObjectId format
        is_valid_objectid = len(wordcloud_id) == 24 and all(c in '0123456789abcdef' for c in wordcloud_id.lower())
        
        if is_valid_objectid:
            try:
                client = get_db_connection()
                db = client['comp5241_g10']
                print(f"[INFO] Connected to MongoDB for submission")
                
                wordcloud = db.word_clouds.find_one({'_id': ObjectId(wordcloud_id)})
                print(f"[INFO] Wordcloud found for submission: {wordcloud is not None}")
                
                if not wordcloud:
                    print(f"[ERROR] Wordcloud {wordcloud_id} not found for submission")
                    return jsonify({'error': 'Word cloud not found'}), 404
                    
            except Exception as e:
                print(f"[ERROR] Database connection failed during submission: {e}")
                return jsonify({'error': f'Database error: {str(e)}'}), 500
        else:
            print(f"[ERROR] Invalid ObjectId format for submission: {wordcloud_id}")
            return jsonify({'error': 'Invalid wordcloud ID format'}), 400

        # Check if the word cloud is still active and not expired
        if not wordcloud.get('is_active', True):
            return jsonify({'error': 'Word cloud is closed'}), 400

        if wordcloud.get('expires_at') and wordcloud['expires_at'] < datetime.utcnow():
            return jsonify({'error': 'Word cloud has expired'}), 400

        # 不检查提交次数限制和重复词汇 - 允许无限制提交

        # Create and add submission
        submission = {
            'word': word,
            'submitted_by': user_id,
            'submitted_at': datetime.utcnow()
        }

        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.word_clouds.update_one(
                {'_id': ObjectId(wordcloud_id)},
                {'$push': {'submissions': submission}}
            )

        logger.info(f"Word '{word}' submitted to wordcloud {wordcloud_id} by user {user_id}")

        return jsonify({
            'message': 'Word submitted successfully',
            'word': word,
            'submissions_remaining': -1,  # 无限制
            'unlimited_submissions': True,
            'total_submissions': len(wordcloud.get('submissions', [])) + 1
        }), 200

    except Exception as e:
        logger.error(f"Error submitting word: {str(e)}")
        return jsonify({'error': 'Failed to submit word', 'details': str(e)}), 500

# Get user's submissions for a word cloud (NO AUTH)
@wordclouds_no_auth_bp.route('/<wordcloud_id>/my-submissions', methods=['GET'])
def get_my_submissions_no_auth(wordcloud_id):
    try:
        user_id = 'debug_user'  # 固定用户ID
        
        print(f"[INFO] ===== GET MY SUBMISSIONS (NO AUTH) =====")
        print(f"[INFO] Wordcloud ID: {wordcloud_id}")
        print(f"[INFO] User ID: {user_id}")
        
        # Check if it's a valid ObjectId format
        is_valid_objectid = len(wordcloud_id) == 24 and all(c in '0123456789abcdef' for c in wordcloud_id.lower())
        
        if is_valid_objectid:
            try:
                client = get_db_connection()
                db = client['comp5241_g10']
                
                wordcloud = db.word_clouds.find_one({'_id': ObjectId(wordcloud_id)})
                
                if not wordcloud:
                    return jsonify({'error': 'Word cloud not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': f'Database error: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Invalid wordcloud ID format'}), 400

        # Get user's submissions
        user_submissions = [
            {
                'word': s['word'],
                'submitted_at': s.get('submitted_at', datetime.now(timezone.utc)).isoformat()
            }
            for s in wordcloud.get('submissions', []) 
            if s.get('submitted_by') == user_id
        ]

        return jsonify(user_submissions), 200

    except Exception as e:
        logger.error(f"Error getting user submissions: {str(e)}")
        return jsonify({'error': 'Failed to get submissions', 'details': str(e)}), 500
