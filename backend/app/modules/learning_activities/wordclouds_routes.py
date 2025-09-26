"""
COMP5241 Group 10 - Word Cloud Routes
API endpoints for word cloud functionality
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from mongoengine import Q
from .activities import WordCloud, WordCloudSubmission
from datetime import datetime
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

# Define a separate blueprint for word cloud endpoints
wordclouds_bp = Blueprint('wordclouds', __name__, url_prefix='/wordclouds')

def validate_wordcloud_data(data):
    """Validate word cloud creation data"""
    errors = []
    
    if not data:
        return ['No data provided']
    
    # Required fields
    if not data.get('title') or not str(data.get('title')).strip():
        errors.append('Title is required and cannot be empty')
    
    if not data.get('prompt') or not str(data.get('prompt')).strip():
        errors.append('Prompt is required and cannot be empty')
    
    if not data.get('course_id') or not str(data.get('course_id')).strip():
        errors.append('Course ID is required and cannot be empty')
    
    # Validate max submissions per user
    max_submissions = data.get('max_submissions_per_user', 3)
    if not isinstance(max_submissions, int) or max_submissions < 1 or max_submissions > 10:
        errors.append('Max submissions per user must be an integer between 1 and 10')
    
    # Validate expiration date
    if data.get('expires_at'):
        try:
            expires_at = datetime.fromisoformat(data['expires_at'])
            if expires_at <= datetime.utcnow():
                errors.append('Expiration date must be in the future')
        except ValueError:
            errors.append('Invalid expiration date format')
    
    return errors

def validate_word(word):
    """Validate and clean a word submission"""
    if not word or not isinstance(word, str):
        return None, "Word must be a non-empty string"
    
    # Clean the word
    cleaned_word = word.strip().lower()
    
    # Remove special characters except hyphens and spaces
    cleaned_word = re.sub(r'[^\w\s-]', '', cleaned_word)
    
    # Replace multiple spaces with single space
    cleaned_word = re.sub(r'\s+', ' ', cleaned_word)
    
    if not cleaned_word:
        return None, "Word contains only invalid characters"
    
    if len(cleaned_word) < 1 or len(cleaned_word) > 50:
        return None, "Word must be between 1 and 50 characters after cleaning"
    
    return cleaned_word, None

# Create a word cloud (teacher only)
@wordclouds_bp.route('/', methods=['POST'])
@jwt_required(locations=["cookies"])
def create_wordcloud():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        validation_errors = validate_wordcloud_data(data)
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Create and save word cloud
        wordcloud = WordCloud(
            title=str(data['title']).strip(),
            prompt=str(data['prompt']).strip(),
            created_by=user_id,
            course_id=str(data['course_id']).strip(),
            max_submissions_per_user=data.get('max_submissions_per_user', 3),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        wordcloud.save()
        
        logger.info(f"Word cloud created successfully by user {user_id}: {wordcloud.id}")
        return jsonify({
            'message': 'Word cloud created successfully', 
            'wordcloud_id': str(wordcloud.id)
        }), 201
        
    except ValidationError as e:
        logger.error(f"Word cloud validation error: {str(e)}")
        return jsonify({'error': 'Validation error', 'details': str(e)}), 400
    except Exception as e:
        logger.error(f"Word cloud creation error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# List word clouds (optionally filter by course)
@wordclouds_bp.route('/', methods=['GET'])
@jwt_required(locations=["cookies"])
def list_wordclouds():
    try:
        user_id = get_jwt_identity()
        course_id = request.args.get('course_id')
        include_expired = request.args.get('include_expired', 'false').lower() == 'true'
        
        # Build query
        query = WordCloud.objects(is_active=True)
        if course_id:
            query = query.filter(course_id=course_id)
        
        # Filter expired word clouds unless specifically requested
        if not include_expired:
            query = query.filter(
                Q(expires_at=None) | Q(expires_at__gt=datetime.utcnow())
            )
        
        # Sort by creation date (newest first)
        wordclouds = query.order_by('-created_at')
        result = []
        
        for wc in wordclouds:
            user_submissions_count = wc.get_user_submissions_count(user_id)
            
            wc_data = {
                'id': str(wc.id),
                'title': wc.title,
                'prompt': wc.prompt,
                'submission_count': len(wc.submissions),
                'unique_words': len(wc.get_word_frequency()),
                'created_by': wc.created_by,
                'is_active': wc.is_active,
                'created_at': wc.created_at.isoformat(),
                'expires_at': wc.expires_at.isoformat() if wc.expires_at else None,
                'course_id': wc.course_id,
                'max_submissions_per_user': wc.max_submissions_per_user,
                'is_expired': wc.is_expired(),
                'user_stats': {
                    'submissions_count': user_submissions_count,
                    'submissions_remaining': max(0, wc.max_submissions_per_user - user_submissions_count)
                }
            }
            result.append(wc_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error listing word clouds: {str(e)}")
        return jsonify({'error': 'Failed to retrieve word clouds', 'details': str(e)}), 500

# Get a specific word cloud
@wordclouds_bp.route('/<wordcloud_id>', methods=['GET'])
@jwt_required(locations=["cookies"])
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

# Submit a word to the word cloud with enhanced validation
@wordclouds_bp.route('/<wordcloud_id>/submit', methods=['POST'])
@jwt_required(locations=["cookies"])
def submit_word(wordcloud_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'word' not in data:
            return jsonify({'error': 'Missing word submission'}), 400
        
        # Validate and clean the word
        word, error = validate_word(data['word'])
        if error:
            return jsonify({'error': error}), 400
        
        wordcloud = WordCloud.objects.get(id=wordcloud_id)
        
        # Check if the word cloud is still active and not expired
        if not wordcloud.is_active:
            return jsonify({'error': 'Word cloud is closed'}), 400
        
        if wordcloud.is_expired():
            return jsonify({'error': 'Word cloud has expired'}), 400
        
        # Check user submission limit
        user_submissions_count = wordcloud.get_user_submissions_count(user_id)
        if user_submissions_count >= wordcloud.max_submissions_per_user:
            return jsonify({
                'error': f'Maximum submission limit ({wordcloud.max_submissions_per_user}) reached'
            }), 400
        
        # Check for duplicate word from the same user
        user_words = [s.word.lower() for s in wordcloud.submissions if s.submitted_by == user_id]
        if word in user_words:
            return jsonify({'error': 'You have already submitted this word'}), 400
        
        # Create and add submission
        submission = WordCloudSubmission(
            word=word,
            submitted_by=user_id
        )
        
        wordcloud.submissions.append(submission)
        wordcloud.save()
        
        remaining_submissions = wordcloud.max_submissions_per_user - (user_submissions_count + 1)
        
        logger.info(f"Word '{word}' submitted to wordcloud {wordcloud_id} by user {user_id}")
        
        return jsonify({
            'message': 'Word submitted successfully',
            'word': word,
            'submissions_remaining': remaining_submissions,
            'total_submissions': len(wordcloud.submissions)
        }), 200
        
    except DoesNotExist:
        return jsonify({'error': 'Word cloud not found'}), 404
    except Exception as e:
        logger.error(f"Error submitting word: {str(e)}")
        return jsonify({'error': 'Failed to submit word', 'details': str(e)}), 500

# Get enhanced word cloud results with analytics
@wordclouds_bp.route('/<wordcloud_id>/results', methods=['GET'])
@jwt_required(locations=["cookies"])
def wordcloud_results(wordcloud_id):
    try:
        wordcloud = WordCloud.objects.get(id=wordcloud_id)
        user_id = get_jwt_identity()
        
        # Get word frequency data
        word_frequency = wordcloud.get_word_frequency()
        
        # Format results for word cloud visualization
        word_data = []
        for word, count in word_frequency.items():
            word_data.append({
                'text': word,
                'value': count,
                'weight': count  # For word cloud sizing
            })
        
        # Sort by frequency (highest first)
        word_data.sort(key=lambda x: x['value'], reverse=True)
        
        # Get user's submissions
        user_submissions = [s.word for s in wordcloud.submissions if s.submitted_by == user_id]
        
        # Analytics data
        total_submissions = len(wordcloud.submissions)
        unique_contributors = len(set(s.submitted_by for s in wordcloud.submissions))
        
        # Most popular words (top 10)
        top_words = word_data[:10]
        
        # Recent submissions (last 20)
        recent_submissions = sorted(
            [{'word': s.word, 'submitted_at': s.submitted_at.isoformat()} 
             for s in wordcloud.submissions],
            key=lambda x: x['submitted_at'],
            reverse=True
        )[:20]
        
        return jsonify({
            'wordcloud_id': wordcloud_id,
            'title': wordcloud.title,
            'prompt': wordcloud.prompt,
            'created_by': wordcloud.created_by,
            'is_active': wordcloud.is_active,
            'is_expired': wordcloud.is_expired(),
            'analytics': {
                'total_submissions': total_submissions,
                'unique_words': len(word_frequency),
                'unique_contributors': unique_contributors,
                'average_submissions_per_user': round(total_submissions / unique_contributors, 1) if unique_contributors > 0 else 0
            },
            'words': word_data,
            'top_words': top_words,
            'recent_submissions': recent_submissions,
            'user_data': {
                'submissions': user_submissions,
                'submissions_count': len(user_submissions),
                'submissions_remaining': wordcloud.max_submissions_per_user - len(user_submissions)
            }
        }), 200
        
    except DoesNotExist:
        return jsonify({'error': 'Word cloud not found'}), 404
    except Exception as e:
        logger.error(f"Error getting word cloud results: {str(e)}")
        return jsonify({'error': 'Failed to get results', 'details': str(e)}), 500

# Remove a user's word submission
@wordclouds_bp.route('/<wordcloud_id>/remove', methods=['POST'])
@jwt_required(locations=["cookies"])
def remove_word(wordcloud_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'word' not in data:
            return jsonify({'error': 'Missing word to remove'}), 400
        
        word_to_remove = str(data['word']).strip().lower()
        
        wordcloud = WordCloud.objects.get(id=wordcloud_id)
        
        # Find and remove the user's submission
        original_count = len(wordcloud.submissions)
        wordcloud.submissions = [
            s for s in wordcloud.submissions 
            if not (s.submitted_by == user_id and s.word.lower() == word_to_remove)
        ]
        
        if len(wordcloud.submissions) == original_count:
            return jsonify({'error': 'Word not found in your submissions'}), 404
        
        wordcloud.save()
        
        logger.info(f"Word '{word_to_remove}' removed from wordcloud {wordcloud_id} by user {user_id}")
        
        return jsonify({
            'message': 'Word removed successfully',
            'removed_word': word_to_remove,
            'submissions_remaining': wordcloud.max_submissions_per_user - wordcloud.get_user_submissions_count(user_id)
        }), 200
        
    except DoesNotExist:
        return jsonify({'error': 'Word cloud not found'}), 404
    except Exception as e:
        logger.error(f"Error removing word: {str(e)}")
        return jsonify({'error': 'Failed to remove word', 'details': str(e)}), 500

# Close/deactivate a word cloud (teacher only)
@wordclouds_bp.route('/<wordcloud_id>/close', methods=['POST'])
@jwt_required(locations=["cookies"])
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