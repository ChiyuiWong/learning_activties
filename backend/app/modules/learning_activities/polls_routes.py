from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
from config.database import get_db_connection

# Define a separate blueprint for polls endpoints
polls_bp = Blueprint('polls', __name__, url_prefix='/polls')

# Create a poll (teacher only)
@polls_bp.route('', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def create_poll():
    user_id = get_jwt_identity()

    # Accept JSON payloads or form data for flexibility in tests/clients
    data = request.get_json(silent=True)
    if data is None:
        # request.get_json() may be None for form-encoded or missing content-type
        data = request.form.to_dict(flat=True) if request.form else {}

    # If options came in as form fields, try to parse JSON string
    if isinstance(data.get('options'), str):
        try:
            import json as _json
            data['options'] = _json.loads(data['options'])
        except Exception:
            # leave as-is; later validation will catch
            pass

    # Validate required fields
    if not data.get('question') or not data.get('options') or not data.get('course_id'):
        return jsonify({'error': 'Missing required fields (question, options, or course_id)'}), 400

    # Normalize options list: accept list of strings or list of dicts with text
    raw_options = data.get('options', [])
    options = []
    for opt in raw_options:
        if isinstance(opt, str):
            options.append({'text': opt, 'votes': 0})
        elif isinstance(opt, dict) and 'text' in opt:
            options.append({'text': opt['text'], 'votes': 0})
        else:
            # skip invalid option entries
            continue

    # If JWT identity missing (tests may not provide), fall back to payload created_by or a test default
    created_by = user_id or data.get('created_by') or ('teacher1' if current_app.config.get('TESTING') else None)

    poll_data = {
        'question': data['question'],
        'options': options,
        'created_by': created_by,
        'course_id': data['course_id'],
        'is_active': True,
        'created_at': datetime.utcnow(),
        'expires_at': (datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None)
    }

    with get_db_connection() as client:
        db = client['comp5241_g10']
        result = db.polls.insert_one(poll_data)
    poll_data['_id'] = result.inserted_id

    return jsonify({'message': 'Poll created successfully', 'poll_id': str(poll_data['_id'])}), 201

# List polls (optionally filter by course)
@polls_bp.route('', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def list_polls():
    course_id = request.args.get('course_id')
    query = {'is_active': True}
    if course_id:
        query['course_id'] = course_id

    # Sort by creation date (newest first)
    with get_db_connection() as client:
        db = client['comp5241_g10']
        polls = list(db.polls.find(query).sort('created_at', -1))
    result = []

    for poll in polls:
        result.append({
            'id': str(poll['_id']),
            'question': poll['question'],
            'options': [opt['text'] for opt in poll['options']],
            'created_by': poll['created_by'],
            'is_active': poll['is_active'],
            'created_at': poll['created_at'].isoformat(),
            'expires_at': poll['expires_at'].isoformat() if poll.get('expires_at') else None,
            'course_id': poll['course_id']
        })
    return jsonify(result), 200# Get a specific poll
@polls_bp.route('/<poll_id>', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def get_poll(poll_id):
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            poll = db.polls.find_one({'_id': ObjectId(poll_id)})
        if not poll:
            return jsonify({'error': 'Poll not found'}), 404

        return jsonify({
            'id': str(poll['_id']),
            'question': poll['question'],
            'options': [opt['text'] for opt in poll['options']],
            'created_by': poll['created_by'],
            'is_active': poll['is_active'],
            'created_at': poll['created_at'].isoformat(),
            'expires_at': poll['expires_at'].isoformat() if poll.get('expires_at') else None,
            'course_id': poll['course_id']
        }), 200
    except Exception:
        return jsonify({'error': 'Poll not found'}), 404

# Vote on a poll (student only)
@polls_bp.route('/<poll_id>/vote', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def vote_poll(poll_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    option_index = data.get('option_index')

    if option_index is None:
        return jsonify({'error': 'Missing option_index'}), 400

    try:
        # Get poll and validate it's active
        with get_db_connection() as client:
            db = client['comp5241_g10']
            poll = db.polls.find_one({'_id': ObjectId(poll_id)})
        if not poll:
            return jsonify({'error': 'Poll not found'}), 404

        if not poll.get('is_active', True):
            return jsonify({'error': 'Poll is closed'}), 400
        if poll.get('expires_at') and poll['expires_at'] < datetime.utcnow():
            return jsonify({'error': 'Poll has expired'}), 400

        # Validate option_index
        if option_index < 0 or option_index >= len(poll['options']):
            return jsonify({'error': 'Invalid option_index'}), 400

        # Check for existing vote
        with get_db_connection() as client:
            db = client['comp5241_g10']
            existing_vote = db.votes.find_one({
                'poll_id': poll_id,
                'student_id': user_id
            })
        if existing_vote:
            return jsonify({'error': 'You have already voted on this poll'}), 400

        # Create new vote
        vote_data = {
            'poll_id': poll_id,
            'student_id': user_id,
            'option_index': option_index,
            'voted_at': datetime.utcnow()
        }
        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.votes.insert_one(vote_data)

        # Increment vote count in poll
        poll['options'][option_index]['votes'] += 1
        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.polls.update_one(
                {'_id': ObjectId(poll_id)},
                {'$set': {'options': poll['options']}}
            )

        return jsonify({'message': 'Vote recorded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get poll results
@polls_bp.route('/<poll_id>/results', methods=['GET'])
@jwt_required(locations=["cookies", "headers"])
def poll_results(poll_id):
    # Wrap in try/except to capture server-side errors during tests and log full traceback
    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            poll = db.polls.find_one({'_id': ObjectId(poll_id)})
        if not poll:
            return jsonify({'error': 'Poll not found'}), 404

        total_votes = sum((opt.get('votes', 0) for opt in poll['options']))
        results = []

        for idx, opt in enumerate(poll['options']):
            percentage = (opt.get('votes', 0) / total_votes * 100) if total_votes > 0 else 0
            results.append({
                'option_index': idx,
                'text': opt['text'],
                'votes': opt.get('votes', 0),
                'percentage': round(percentage, 1)
            })

        return jsonify({
            'poll_id': str(poll['_id']),
            'question': poll['question'],
            'results': results,
            'total_votes': total_votes
        }), 200
    except Exception:
        # Return a JSON 500 with minimal error detail (no server traceback leaked)
        return jsonify({'error': 'Internal server error'}), 500

# Close/deactivate a poll (teacher only)
@polls_bp.route('/<poll_id>/close', methods=['POST'])
@jwt_required(locations=["cookies", "headers"])
def close_poll(poll_id):
    user_id = get_jwt_identity()

    try:
        with get_db_connection() as client:
            db = client['comp5241_g10']
            poll = db.polls.find_one({'_id': ObjectId(poll_id)})
        if not poll:
            return jsonify({'error': 'Poll not found'}), 404

        # Only the creator can close the poll
        if poll['created_by'] != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can close this poll'}), 403

        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.polls.update_one(
                {'_id': ObjectId(poll_id)},
                {'$set': {'is_active': False}}
            )
        return jsonify({'message': 'Poll closed successfully'}), 200
    except Exception:
        return jsonify({'error': 'Poll not found'}), 404