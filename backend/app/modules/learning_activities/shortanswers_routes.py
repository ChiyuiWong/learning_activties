"""
COMP5241 Group 10 - Short Answer Routes
API endpoints for short answer question functionality
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from .activities import ShortAnswerQuestion, ShortAnswerSubmission
from datetime import datetime

# Define a separate blueprint for short answer question endpoints
shortanswers_bp = Blueprint('shortanswers', __name__, url_prefix='/shortanswers')

# Create a short answer question (teacher only)
@shortanswers_bp.route('/', methods=['POST'])
@jwt_required()
def create_shortanswer():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('question') or not data.get('course_id'):
        return jsonify({'error': 'Missing required fields (question or course_id)'}), 400
    
    try:
        shortanswer = ShortAnswerQuestion(
            question=data['question'],
            answer_hint=data.get('answer_hint', ''),
            example_answer=data.get('example_answer', ''),
            max_length=data.get('max_length', 1000),
            created_by=user_id,
            course_id=data['course_id'],
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        shortanswer.save()
        return jsonify({'message': 'Short answer question created successfully', 'question_id': str(shortanswer.id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# List short answer questions (optionally filter by course)
@shortanswers_bp.route('/', methods=['GET'])
@jwt_required()
def list_shortanswers():
    course_id = request.args.get('course_id')
    query = ShortAnswerQuestion.objects(is_active=True)
    if course_id:
        query = query.filter(course_id=course_id)
    
    # Sort by creation date (newest first)
    questions = query.order_by('-created_at')
    result = []
    user_id = get_jwt_identity()
    
    for q in questions:
        # Check if user has already submitted an answer
        has_submitted = any(sub.submitted_by == user_id for sub in q.submissions)
        
        question_data = {
            'id': str(q.id),
            'question': q.question,
            'created_by': q.created_by,
            'is_active': q.is_active,
            'created_at': q.created_at.isoformat(),
            'expires_at': q.expires_at.isoformat() if q.expires_at else None,
            'course_id': q.course_id,
            'max_length': q.max_length,
            'submission_count': len(q.submissions),
            'has_submitted': has_submitted
        }
        
        # Include hints for students
        if q.answer_hint and q.created_by != user_id:
            question_data['answer_hint'] = q.answer_hint
            
        # Include example answer for teacher
        if q.created_by == user_id and q.example_answer:
            question_data['example_answer'] = q.example_answer
            
        result.append(question_data)
    
    return jsonify(result), 200

# Get a specific short answer question
@shortanswers_bp.route('/<question_id>', methods=['GET'])
@jwt_required()
def get_shortanswer(question_id):
    try:
        question = ShortAnswerQuestion.objects.get(id=question_id)
        user_id = get_jwt_identity()
        is_creator = question.created_by == user_id
        
        # Find user's submission if exists
        user_submission = next((sub for sub in question.submissions if sub.submitted_by == user_id), None)
        
        result = {
            'id': str(question.id),
            'question': question.question,
            'created_by': question.created_by,
            'is_active': question.is_active,
            'created_at': question.created_at.isoformat(),
            'expires_at': question.expires_at.isoformat() if question.expires_at else None,
            'course_id': question.course_id,
            'max_length': question.max_length
        }
        
        # Add hint if present and user is not creator
        if question.answer_hint and not is_creator:
            result['answer_hint'] = question.answer_hint
            
        # Add example answer if user is creator
        if is_creator and question.example_answer:
            result['example_answer'] = question.example_answer
            
        # Add user's submission if exists
        if user_submission:
            result['user_submission'] = {
                'text': user_submission.text,
                'submitted_at': user_submission.submitted_at.isoformat(),
                'feedback': user_submission.feedback,
                'score': user_submission.score
            }
            
        # Add all submissions if user is creator
        if is_creator:
            result['submissions'] = [{
                'text': sub.text,
                'submitted_by': sub.submitted_by,
                'submitted_at': sub.submitted_at.isoformat(),
                'feedback': sub.feedback,
                'score': sub.score
            } for sub in question.submissions]
            
        return jsonify(result), 200
    except DoesNotExist:
        return jsonify({'error': 'Short answer question not found'}), 404

# Submit an answer
@shortanswers_bp.route('/<question_id>/submit', methods=['POST'])
@jwt_required()
def submit_answer(question_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('answer'):
        return jsonify({'error': 'Missing answer submission'}), 400
    
    answer = data['answer'].strip()
    if not answer:
        return jsonify({'error': 'Answer cannot be empty'}), 400
    
    try:
        question = ShortAnswerQuestion.objects.get(id=question_id)
        
        # Check if the question is still active
        if not question.is_active:
            return jsonify({'error': 'This question is closed'}), 400
            
        # Check if the question has expired
        if question.expires_at and question.expires_at < datetime.utcnow():
            return jsonify({'error': 'This question has expired'}), 400
            
        # Check answer length
        if len(answer) > question.max_length:
            return jsonify({'error': f'Answer exceeds maximum length of {question.max_length} characters'}), 400
            
        # Check if user already submitted
        existing_submission = next((sub for sub in question.submissions if sub.submitted_by == user_id), None)
        
        if existing_submission:
            # Update existing submission
            existing_submission.text = answer
            existing_submission.submitted_at = datetime.utcnow()
        else:
            # Create new submission
            submission = ShortAnswerSubmission(
                text=answer,
                submitted_by=user_id
            )
            question.submissions.append(submission)
            
        question.save()
        
        return jsonify({
            'message': 'Answer submitted successfully',
            'is_update': existing_submission is not None
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Short answer question not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Provide feedback on submission (teacher only)
@shortanswers_bp.route('/<question_id>/feedback/<student_id>', methods=['POST'])
@jwt_required()
def provide_feedback(question_id, student_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Missing feedback data'}), 400
    
    try:
        question = ShortAnswerQuestion.objects.get(id=question_id)
        
        # Ensure user is the creator of the question
        if question.created_by != user_id:
            return jsonify({'error': 'Only the creator can provide feedback'}), 403
            
        # Find the student's submission
        submission = next((sub for sub in question.submissions if sub.submitted_by == student_id), None)
        
        if not submission:
            return jsonify({'error': 'Student submission not found'}), 404
            
        # Update feedback and optional score
        if 'feedback' in data:
            submission.feedback = data['feedback']
            
        if 'score' in data:
            try:
                score = float(data['score'])
                submission.score = score
            except ValueError:
                return jsonify({'error': 'Invalid score format'}), 400
                
        question.save()
        
        return jsonify({
            'message': 'Feedback provided successfully',
            'student_id': student_id
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Short answer question not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Close/deactivate a short answer question (teacher only)
@shortanswers_bp.route('/<question_id>/close', methods=['POST'])
@jwt_required()
def close_shortanswer(question_id):
    user_id = get_jwt_identity()
    
    try:
        question = ShortAnswerQuestion.objects.get(id=question_id)
        # Only the creator can close the question
        if question.created_by != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can close this question'}), 403
            
        question.is_active = False
        question.save()
        return jsonify({'message': 'Short answer question closed successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'Short answer question not found'}), 404