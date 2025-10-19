"""
COMP5241 Group 10 - Delete Routes for Learning Activities
API endpoints for deleting learning activities
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from config.database import get_db_connection
from .services import LearningActivityService
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define a separate blueprint for delete endpoints
delete_bp = Blueprint('delete', __name__)

@delete_bp.route('/activities/<activity_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_activity(activity_id):
    """Delete a learning activity (soft delete by default)"""
    try:
        user_id = get_jwt_identity()
        hard_delete = request.args.get('hard_delete', 'false').lower() == 'true'
        
        # Use the service to delete the activity
        success = LearningActivityService.delete_activity(activity_id, user_id, hard_delete)
        
        if success:
            delete_type = "permanently deleted" if hard_delete else "deleted"
            logger.info(f"Activity {activity_id} {delete_type} by user {user_id}")
            return jsonify({
                'message': f'Activity {delete_type} successfully',
                'activity_id': activity_id,
                'hard_delete': hard_delete
            }), 200
        else:
            return jsonify({
                'error': 'Activity not found or you are not authorized to delete it'
            }), 404
            
    except Exception as e:
        logger.error(f"Error deleting activity {activity_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete activity', 'details': str(e)}), 500

@delete_bp.route('/polls/<poll_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_poll(poll_id):
    """Delete a poll"""
    try:
        user_id = get_jwt_identity()
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
            poll = db.polls.find_one({'_id': ObjectId(poll_id)})
            
        if not poll:
            return jsonify({'error': 'Poll not found'}), 404
            
        # Check if user is the creator
        if poll.get('created_by') != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can delete this poll'}), 403
            
        # Delete the poll and related data
        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.polls.delete_one({'_id': ObjectId(poll_id)})
            # Also delete related votes
            db.votes.delete_many({'poll_id': poll_id})
            
        logger.info(f"Poll {poll_id} deleted by user {user_id}")
        return jsonify({'message': 'Poll deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting poll {poll_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete poll', 'details': str(e)}), 500

@delete_bp.route('/shortanswers/<question_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_shortanswer(question_id):
    """Delete a short answer question"""
    try:
        user_id = get_jwt_identity()
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
            question = db.short_answer_questions.find_one({'_id': ObjectId(question_id)})
            
        if not question:
            return jsonify({'error': 'Short answer question not found'}), 404
            
        # Check if user is the creator
        if question.get('created_by') != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can delete this question'}), 403
            
        # Delete the question
        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.short_answer_questions.delete_one({'_id': ObjectId(question_id)})
            
        logger.info(f"Short answer question {question_id} deleted by user {user_id}")
        return jsonify({'message': 'Short answer question deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting short answer question {question_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete short answer question', 'details': str(e)}), 500

@delete_bp.route('/quizzes/<quiz_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_quiz(quiz_id):
    """Delete a quiz"""
    try:
        user_id = get_jwt_identity()
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
            quiz = db.quizzes.find_one({'_id': ObjectId(quiz_id)})
            
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        # Check if user is the creator
        if quiz.get('created_by') != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can delete this quiz'}), 403
            
        # Delete the quiz and related data
        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.quizzes.delete_one({'_id': ObjectId(quiz_id)})
            # Also delete related attempts
            db.quiz_attempts.delete_many({'quiz_id': quiz_id})
            
        logger.info(f"Quiz {quiz_id} deleted by user {user_id}")
        return jsonify({'message': 'Quiz deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting quiz {quiz_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete quiz', 'details': str(e)}), 500

@delete_bp.route('/wordclouds/<wordcloud_id>', methods=['DELETE'])
@jwt_required(locations=["cookies", "headers"])
def delete_wordcloud(wordcloud_id):
    """Delete a word cloud"""
    try:
        user_id = get_jwt_identity()
        
        with get_db_connection() as client:
            db = client['comp5241_g10']
            wordcloud = db.wordclouds.find_one({'_id': ObjectId(wordcloud_id)})
            
        if not wordcloud:
            return jsonify({'error': 'Word cloud not found'}), 404
            
        # Check if user is the creator
        if wordcloud.get('created_by') != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can delete this word cloud'}), 403
            
        # Delete the word cloud
        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.wordclouds.delete_one({'_id': ObjectId(wordcloud_id)})
            
        logger.info(f"Word cloud {wordcloud_id} deleted by user {user_id}")
        return jsonify({'message': 'Word cloud deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting word cloud {wordcloud_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete word cloud', 'details': str(e)}), 500
