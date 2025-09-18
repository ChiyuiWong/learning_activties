"""
COMP5241 Group 10 - Short Answer Routes
API endpoints for short answer question functionality
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from mongoengine import Q
from .activities import ShortAnswerQuestion, ShortAnswerSubmission
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define a separate blueprint for short answer question endpoints
shortanswers_bp = Blueprint('shortanswers', __name__, url_prefix='/shortanswers')

def validate_shortanswer_data(data):
    """Validate short answer question creation data"""
    errors = []
    
    if not data:
        return ['No data provided']
    
    # Required fields
    if not data.get('question') or not str(data.get('question')).strip():
        errors.append('Question is required and cannot be empty')
    
    if not data.get('course_id') or not str(data.get('course_id')).strip():
        errors.append('Course ID is required and cannot be empty')
    
    # Validate max_length
    max_length = data.get('max_length', 1000)
    if not isinstance(max_length, int) or max_length < 100 or max_length > 5000:
        errors.append('Max length must be an integer between 100 and 5000')
    
    # Validate expiration date
    if data.get('expires_at'):
        try:
            expires_at = datetime.fromisoformat(data['expires_at'])
            if expires_at <= datetime.utcnow():
                errors.append('Expiration date must be in the future')
        except ValueError:
            errors.append('Invalid expiration date format')
    
    return errors

# Create a short answer question (teacher only)
@shortanswers_bp.route('/', methods=['POST'])
@jwt_required()
def create_shortanswer():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        validation_errors = validate_shortanswer_data(data)
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Create and save short answer question
        shortanswer = ShortAnswerQuestion(
            question=str(data['question']).strip(),
            answer_hint=str(data.get('answer_hint', '')).strip(),
            example_answer=str(data.get('example_answer', '')).strip(),
            max_length=data.get('max_length', 1000),
            created_by=user_id,
            course_id=str(data['course_id']).strip(),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        shortanswer.save()
        
        logger.info(f"Short answer question created successfully by user {user_id}: {shortanswer.id}")
        return jsonify({
            'message': 'Short answer question created successfully', 
            'question_id': str(shortanswer.id)
        }), 201
        
    except ValidationError as e:
        logger.error(f"Short answer validation error: {str(e)}")
        return jsonify({'error': 'Validation error', 'details': str(e)}), 400
    except Exception as e:
        logger.error(f"Short answer creation error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

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

# Enhanced answer submission with better validation
@shortanswers_bp.route('/<question_id>/submit', methods=['POST'])
@jwt_required()
def submit_answer(question_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'answer' not in data:
            return jsonify({'error': 'Missing answer submission'}), 400
        
        answer = str(data['answer']).strip()
        if not answer:
            return jsonify({'error': 'Answer cannot be empty'}), 400
        
        question = ShortAnswerQuestion.objects.get(id=question_id)
        
        # Check if the question is still available
        if not question.is_active:
            return jsonify({'error': 'This question is closed'}), 400
        
        if question.is_expired():
            return jsonify({'error': 'This question has expired'}), 400
        
        # Check answer length
        if len(answer) > question.max_length:
            return jsonify({
                'error': f'Answer exceeds maximum length of {question.max_length} characters',
                'current_length': len(answer),
                'max_length': question.max_length
            }), 400
        
        # Find existing submission
        existing_submission = question.get_user_submission(user_id)
        
        if existing_submission:
            # Update existing submission
            existing_submission.text = answer
            existing_submission.submitted_at = datetime.utcnow()
            existing_submission.is_graded = False  # Reset graded status on resubmission
            existing_submission.feedback = ''
            existing_submission.score = None
            is_update = True
        else:
            # Create new submission
            submission = ShortAnswerSubmission(
                text=answer,
                submitted_by=user_id
            )
            question.submissions.append(submission)
            is_update = False
        
        question.save()
        
        logger.info(f"Answer {'updated' if is_update else 'submitted'} for question {question_id} by user {user_id}")
        
        return jsonify({
            'message': f'Answer {"updated" if is_update else "submitted"} successfully',
            'is_update': is_update,
            'answer_length': len(answer),
            'submitted_at': datetime.utcnow().isoformat()
        }), 200
        
    except DoesNotExist:
        return jsonify({'error': 'Short answer question not found'}), 404
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        return jsonify({'error': 'Failed to submit answer', 'details': str(e)}), 500

# Enhanced feedback system with batch grading
@shortanswers_bp.route('/<question_id>/feedback/<student_id>', methods=['POST'])
@jwt_required()
def provide_feedback(question_id, student_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Missing feedback data'}), 400
        
        question = ShortAnswerQuestion.objects.get(id=question_id)
        
        # Ensure user is the creator of the question
        if question.created_by != user_id:
            return jsonify({'error': 'Only the creator can provide feedback'}), 403
        
        # Find the student's submission
        submission = question.get_user_submission(student_id)
        
        if not submission:
            return jsonify({'error': 'Student submission not found'}), 404
        
        # Update feedback
        if 'feedback' in data:
            feedback = str(data['feedback']).strip()
            submission.feedback = feedback
        
        # Update score with validation
        if 'score' in data:
            try:
                score = float(data['score'])
                if score < 0 or score > 100:
                    return jsonify({'error': 'Score must be between 0 and 100'}), 400
                submission.score = score
                submission.is_graded = True
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid score format - must be a number'}), 400
        
        question.save()
        
        logger.info(f"Feedback provided for question {question_id}, student {student_id} by user {user_id}")
        
        return jsonify({
            'message': 'Feedback provided successfully',
            'student_id': student_id,
            'feedback': submission.feedback,
            'score': submission.score,
            'is_graded': submission.is_graded
        }), 200
        
    except DoesNotExist:
        return jsonify({'error': 'Short answer question not found'}), 404
    except Exception as e:
        logger.error(f"Error providing feedback: {str(e)}")
        return jsonify({'error': 'Failed to provide feedback', 'details': str(e)}), 500

# Batch grading endpoint
@shortanswers_bp.route('/<question_id>/batch-grade', methods=['POST'])
@jwt_required()
def batch_grade(question_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'grades' not in data:
            return jsonify({'error': 'Missing grades data'}), 400
        
        question = ShortAnswerQuestion.objects.get(id=question_id)
        
        # Ensure user is the creator of the question
        if question.created_by != user_id:
            return jsonify({'error': 'Only the creator can grade submissions'}), 403
        
        grades = data['grades']
        if not isinstance(grades, list):
            return jsonify({'error': 'Grades must be provided as a list'}), 400
        
        successful_grades = []
        failed_grades = []
        
        for grade_data in grades:
            try:
                student_id = grade_data.get('student_id')
                feedback = grade_data.get('feedback', '')
                score = grade_data.get('score')
                
                if not student_id:
                    failed_grades.append({'error': 'Missing student_id', 'data': grade_data})
                    continue
                
                # Find submission
                submission = question.get_user_submission(student_id)
                if not submission:
                    failed_grades.append({'error': f'Submission not found for student {student_id}', 'student_id': student_id})
                    continue
                
                # Update submission
                if feedback:
                    submission.feedback = str(feedback).strip()
                
                if score is not None:
                    try:
                        score_value = float(score)
                        if score_value < 0 or score_value > 100:
                            failed_grades.append({'error': f'Invalid score {score_value} for student {student_id}', 'student_id': student_id})
                            continue
                        submission.score = score_value
                        submission.is_graded = True
                    except (ValueError, TypeError):
                        failed_grades.append({'error': f'Invalid score format for student {student_id}', 'student_id': student_id})
                        continue
                
                successful_grades.append({
                    'student_id': student_id,
                    'feedback': submission.feedback,
                    'score': submission.score
                })
                
            except Exception as e:
                failed_grades.append({'error': str(e), 'data': grade_data})
        
        question.save()
        
        logger.info(f"Batch grading completed for question {question_id}: {len(successful_grades)} successful, {len(failed_grades)} failed")
        
        return jsonify({
            'message': 'Batch grading completed',
            'successful_grades': len(successful_grades),
            'failed_grades': len(failed_grades),
            'success_details': successful_grades,
            'error_details': failed_grades
        }), 200
        
    except DoesNotExist:
        return jsonify({'error': 'Short answer question not found'}), 404
    except Exception as e:
        logger.error(f"Error in batch grading: {str(e)}")
        return jsonify({'error': 'Failed to process batch grading', 'details': str(e)}), 500

# Get grading statistics for teachers
@shortanswers_bp.route('/<question_id>/stats', methods=['GET'])
@jwt_required()
def get_grading_stats(question_id):
    try:
        user_id = get_jwt_identity()
        question = ShortAnswerQuestion.objects.get(id=question_id)
        
        # Ensure user is the creator of the question
        if question.created_by != user_id:
            return jsonify({'error': 'Only the creator can view statistics'}), 403
        
        total_submissions = len(question.submissions)
        graded_count = question.get_graded_submissions_count()
        ungraded_count = total_submissions - graded_count
        
        # Calculate score statistics
        graded_submissions = [s for s in question.submissions if s.is_graded and s.score is not None]
        
        if graded_submissions:
            scores = [s.score for s in graded_submissions]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
        else:
            avg_score = max_score = min_score = 0
        
        # Get submission timeline data
        submission_timeline = []
        for submission in question.submissions:
            submission_timeline.append({
                'student_id': submission.submitted_by,
                'submitted_at': submission.submitted_at.isoformat(),
                'is_graded': submission.is_graded,
                'score': submission.score,
                'word_count': len(submission.text.split())
            })
        
        return jsonify({
            'question_id': question_id,
            'title': question.question[:100] + '...' if len(question.question) > 100 else question.question,
            'statistics': {
                'total_submissions': total_submissions,
                'graded_submissions': graded_count,
                'ungraded_submissions': ungraded_count,
                'grading_progress': round((graded_count / total_submissions * 100), 1) if total_submissions > 0 else 0,
                'average_score': round(avg_score, 1),
                'highest_score': max_score,
                'lowest_score': min_score
            },
            'submission_timeline': sorted(submission_timeline, key=lambda x: x['submitted_at'], reverse=True)
        }), 200
        
    except DoesNotExist:
        return jsonify({'error': 'Short answer question not found'}), 404
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to get statistics', 'details': str(e)}), 500

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