"""
COMP5241 Group 10 - Word Cloud Routes
API endpoints for word cloud functionality
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from .activities import WordCloud, WordCloudSubmission
from datetime import datetime

# Define a separate blueprint for word cloud endpoints
wordclouds_bp = Blueprint('wordclouds', __name__, url_prefix='/wordclouds')

# Create a word cloud (teacher only)
@wordclouds_bp.route('/', methods=['POST'])
@jwt_required()
def create_wordcloud():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title') or not data.get('prompt') or not data.get('course_id'):
        return jsonify({'error': 'Missing required fields (title, prompt, or course_id)'}), 400
    
    try:
        wordcloud = WordCloud(
            title=data['title'],
            prompt=data['prompt'],
            created_by=user_id,
            course_id=data['course_id'],
            max_submissions_per_user=data.get('max_submissions_per_user', 3),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        wordcloud.save()
        return jsonify({'message': 'Word cloud created successfully', 'wordcloud_id': str(wordcloud.id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# List word clouds (optionally filter by course)
@wordclouds_bp.route('/', methods=['GET'])
@jwt_required()
def list_wordclouds():
    course_id = request.args.get('course_id')
    query = WordCloud.objects(is_active=True)
    if course_id:
        query = query.filter(course_id=course_id)
    
    # Sort by creation date (newest first)
    wordclouds = query.order_by('-created_at')
    result = []
    
    for wc in wordclouds:
        result.append({
            'id': str(wc.id),
            'title': wc.title,
            'prompt': wc.prompt,
            'submission_count': len(wc.submissions),
            'created_by': wc.created_by,
            'is_active': wc.is_active,
            'created_at': wc.created_at.isoformat(),
            'expires_at': wc.expires_at.isoformat() if wc.expires_at else None,
            'course_id': wc.course_id,
            'max_submissions_per_user': wc.max_submissions_per_user
        })
    return jsonify(result), 200

# Get a specific word cloud
@wordclouds_bp.route('/<wordcloud_id>', methods=['GET'])
@jwt_required()
def get_wordcloud(wordcloud_id):
    try:
        wordcloud = WordCloud.objects.get(id=wordcloud_id)
        user_id = get_jwt_identity()
        
        # Get user's submissions
        user_submissions = [s.word for s in wordcloud.submissions if s.submitted_by == user_id]
        
        return jsonify({
            'id': str(wordcloud.id),
            'title': wordcloud.title,
            'prompt': wordcloud.prompt,
            'created_by': wordcloud.created_by,
            'is_active': wordcloud.is_active,
            'created_at': wordcloud.created_at.isoformat(),
            'expires_at': wordcloud.expires_at.isoformat() if wordcloud.expires_at else None,
            'course_id': wordcloud.course_id,
            'max_submissions_per_user': wordcloud.max_submissions_per_user,
            'user_submissions': user_submissions,
            'submissions_remaining': wordcloud.max_submissions_per_user - len(user_submissions)
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Word cloud not found'}), 404

# Submit a word to the word cloud
@wordclouds_bp.route('/<wordcloud_id>/submit', methods=['POST'])
@jwt_required()
def submit_word(wordcloud_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('word'):
        return jsonify({'error': 'Missing word submission'}), 400
    
    # Clean and validate the word
    word = data['word'].strip()
    if not word or len(word) > 50:
        return jsonify({'error': 'Word must be between 1 and 50 characters'}), 400
    
    try:
        wordcloud = WordCloud.objects.get(id=wordcloud_id)
        
        # Check if the word cloud is still active
        if not wordcloud.is_active:
            return jsonify({'error': 'Word cloud is closed'}), 400
            
        # Check if the word cloud has expired
        if wordcloud.expires_at and wordcloud.expires_at < datetime.utcnow():
            return jsonify({'error': 'Word cloud has expired'}), 400
            
        # Check user submission limit
        user_submissions = [s for s in wordcloud.submissions if s.submitted_by == user_id]
        if len(user_submissions) >= wordcloud.max_submissions_per_user:
            return jsonify({'error': f'Maximum submission limit ({wordcloud.max_submissions_per_user}) reached'}), 400
            
        # Create submission
        submission = WordCloudSubmission(
            word=word,
            submitted_by=user_id
        )
        
        wordcloud.submissions.append(submission)
        wordcloud.save()
        
        return jsonify({
            'message': 'Word submitted successfully',
            'submissions_remaining': wordcloud.max_submissions_per_user - (len(user_submissions) + 1)
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Word cloud not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get word cloud results
@wordclouds_bp.route('/<wordcloud_id>/results', methods=['GET'])
@jwt_required()
def wordcloud_results(wordcloud_id):
    try:
        wordcloud = WordCloud.objects.get(id=wordcloud_id)
        
        # Count frequency of each word
        word_counts = {}
        for submission in wordcloud.submissions:
            word = submission.word.lower()  # Case-insensitive counting
            word_counts[word] = word_counts.get(word, 0) + 1
            
        # Format results
        results = [{'text': word, 'value': count} for word, count in word_counts.items()]
        
        # Sort by frequency (highest first)
        results.sort(key=lambda x: x['value'], reverse=True)
        
        return jsonify({
            'wordcloud_id': wordcloud_id,
            'title': wordcloud.title,
            'prompt': wordcloud.prompt,
            'total_submissions': len(wordcloud.submissions),
            'unique_words': len(word_counts),
            'words': results
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Word cloud not found'}), 404

# Close/deactivate a word cloud (teacher only)
@wordclouds_bp.route('/<wordcloud_id>/close', methods=['POST'])
@jwt_required()
def close_wordcloud(wordcloud_id):
    user_id = get_jwt_identity()
    
    try:
        wordcloud = WordCloud.objects.get(id=wordcloud_id)
        # Only the creator can close the word cloud
        if wordcloud.created_by != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can close this word cloud'}), 403
            
        wordcloud.is_active = False
        wordcloud.save()
        return jsonify({'message': 'Word cloud closed successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'Word cloud not found'}), 404