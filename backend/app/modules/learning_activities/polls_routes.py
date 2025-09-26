from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from .poll import Poll, Vote, Option
from datetime import datetime

# Define a separate blueprint for polls endpoints
polls_bp = Blueprint('polls', __name__, url_prefix='/polls')

# Create a poll (teacher only)
@polls_bp.route('/', methods=['POST'])
@jwt_required(locations=["cookies"])
def create_poll():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('question') or not data.get('options') or not data.get('course_id'):
        return jsonify({'error': 'Missing required fields (question, options, or course_id)'}), 400
    
    # Create poll options from the provided list
    options = [Option(text=opt) for opt in data.get('options', [])]
    
    try:
        poll = Poll(
            question=data['question'],
            options=options,
            created_by=user_id,
            course_id=data['course_id'],
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        poll.save()
        return jsonify({'message': 'Poll created successfully', 'poll_id': str(poll.id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# List polls (optionally filter by course)
@polls_bp.route('/', methods=['GET'])
@jwt_required(locations=["cookies"])
def list_polls():
    course_id = request.args.get('course_id')
    query = Poll.objects(is_active=True)
    if course_id:
        query = query.filter(course_id=course_id)
    
    # Sort by creation date (newest first)
    polls = query.order_by('-created_at')
    result = []
    
    for poll in polls:
        result.append({
            'id': str(poll.id),
            'question': poll.question,
            'options': [opt.text for opt in poll.options],
            'created_by': poll.created_by,
            'is_active': poll.is_active,
            'created_at': poll.created_at.isoformat(),
            'expires_at': poll.expires_at.isoformat() if poll.expires_at else None,
            'course_id': poll.course_id
        })
    return jsonify(result), 200

# Get a specific poll
@polls_bp.route('/<poll_id>', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_poll(poll_id):
    try:
        poll = Poll.objects.get(id=poll_id)
        return jsonify({
            'id': str(poll.id),
            'question': poll.question,
            'options': [opt.text for opt in poll.options],
            'created_by': poll.created_by,
            'is_active': poll.is_active,
            'created_at': poll.created_at.isoformat(),
            'expires_at': poll.expires_at.isoformat() if poll.expires_at else None,
            'course_id': poll.course_id
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Poll not found'}), 404

# Vote on a poll (student only)
@polls_bp.route('/<poll_id>/vote', methods=['POST'])
@jwt_required(locations=["cookies"])
def vote_poll(poll_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    option_index = data.get('option_index')
    
    if option_index is None:
        return jsonify({'error': 'Missing option_index'}), 400
    
    try:
        # Get poll and validate it's active
        poll = Poll.objects.get(id=poll_id)
        if not poll.is_active:
            return jsonify({'error': 'Poll is closed'}), 400
        if poll.expires_at and poll.expires_at < datetime.utcnow():
            return jsonify({'error': 'Poll has expired'}), 400
            
        # Validate option_index
        if option_index < 0 or option_index >= len(poll.options):
            return jsonify({'error': 'Invalid option_index'}), 400
            
        # Check for existing vote
        existing_vote = Vote.objects(poll=poll, student_id=user_id).first()
        if existing_vote:
            return jsonify({'error': 'You have already voted on this poll'}), 400
            
        # Create new vote
        vote = Vote(poll=poll, student_id=user_id, option_index=option_index)
        vote.save()
        
        # Increment vote count in poll
        poll.options[option_index].votes += 1
        poll.save()
        
        return jsonify({'message': 'Vote recorded successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'Poll not found'}), 404
    except NotUniqueError:
        return jsonify({'error': 'You have already voted on this poll'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get poll results
@polls_bp.route('/<poll_id>/results', methods=['GET'])
@jwt_required(locations=["cookies"])
def poll_results(poll_id):
    try:
        poll = Poll.objects.get(id=poll_id)
        total_votes = sum(opt.votes for opt in poll.options)
        results = []
        
        for idx, opt in enumerate(poll.options):
            percentage = (opt.votes / total_votes * 100) if total_votes > 0 else 0
            results.append({
                'option_index': idx,
                'text': opt.text,
                'votes': opt.votes,
                'percentage': round(percentage, 1)
            })
            
        return jsonify({
            'poll_id': str(poll.id),
            'question': poll.question,
            'results': results,
            'total_votes': total_votes
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Poll not found'}), 404

# Close/deactivate a poll (teacher only)
@polls_bp.route('/<poll_id>/close', methods=['POST'])
@jwt_required(locations=["cookies"])
def close_poll(poll_id):
    user_id = get_jwt_identity()
    
    try:
        poll = Poll.objects.get(id=poll_id)
        # Only the creator can close the poll
        if poll.created_by != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can close this poll'}), 403
            
        poll.is_active = False
        poll.save()
        return jsonify({'message': 'Poll closed successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'Poll not found'}), 404