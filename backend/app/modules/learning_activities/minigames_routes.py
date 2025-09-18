"""
COMP5241 Group 10 - Mini-Games Routes
API endpoints for mini-game functionality
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from .activities import MiniGame, MiniGameScore
from datetime import datetime

# Define a separate blueprint for mini-game endpoints
minigames_bp = Blueprint('minigames', __name__, url_prefix='/minigames')

# Create a mini-game (teacher only)
@minigames_bp.route('/', methods=['POST'])
@jwt_required()
def create_minigame():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title') or not data.get('game_type') or not data.get('course_id'):
        return jsonify({'error': 'Missing required fields (title, game_type, or course_id)'}), 400
    
    # Validate game_type
    valid_game_types = ['matching', 'sorting', 'sequence', 'memory', 'custom']
    if data.get('game_type') not in valid_game_types:
        return jsonify({'error': f'Invalid game_type. Must be one of: {", ".join(valid_game_types)}'}), 400
    
    try:
        minigame = MiniGame(
            title=data['title'],
            game_type=data['game_type'],
            description=data.get('description', ''),
            instructions=data.get('instructions', ''),
            game_config=data.get('game_config', {}),
            created_by=user_id,
            course_id=data['course_id'],
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        minigame.save()
        return jsonify({'message': 'Mini-game created successfully', 'minigame_id': str(minigame.id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# List mini-games (optionally filter by course or game type)
@minigames_bp.route('/', methods=['GET'])
@jwt_required()
def list_minigames():
    course_id = request.args.get('course_id')
    game_type = request.args.get('game_type')
    
    query = MiniGame.objects(is_active=True)
    if course_id:
        query = query.filter(course_id=course_id)
    if game_type:
        query = query.filter(game_type=game_type)
    
    # Sort by creation date (newest first)
    minigames = query.order_by('-created_at')
    result = []
    
    for game in minigames:
        result.append({
            'id': str(game.id),
            'title': game.title,
            'game_type': game.game_type,
            'description': game.description,
            'created_by': game.created_by,
            'is_active': game.is_active,
            'created_at': game.created_at.isoformat(),
            'expires_at': game.expires_at.isoformat() if game.expires_at else None,
            'course_id': game.course_id,
            'play_count': len(game.scores)
        })
    return jsonify(result), 200

# Get a specific mini-game
@minigames_bp.route('/<minigame_id>', methods=['GET'])
@jwt_required()
def get_minigame(minigame_id):
    try:
        minigame = MiniGame.objects.get(id=minigame_id)
        user_id = get_jwt_identity()
        is_creator = minigame.created_by == user_id
        
        # Get user's high score if any
        user_scores = [s for s in minigame.scores if s.student_id == user_id]
        user_high_score = max([s.score for s in user_scores]) if user_scores else None
        
        # Basic game data
        result = {
            'id': str(minigame.id),
            'title': minigame.title,
            'game_type': minigame.game_type,
            'description': minigame.description,
            'instructions': minigame.instructions,
            'created_by': minigame.created_by,
            'is_active': minigame.is_active,
            'created_at': minigame.created_at.isoformat(),
            'expires_at': minigame.expires_at.isoformat() if minigame.expires_at else None,
            'course_id': minigame.course_id,
            'game_config': minigame.game_config,
            'user_high_score': user_high_score
        }
        
        # Add top scores
        top_scores = sorted(minigame.scores, key=lambda s: s.score, reverse=True)[:10]
        result['top_scores'] = [{
            'student_id': score.student_id,
            'score': score.score,
            'time_taken': score.time_taken,
            'achieved_at': score.achieved_at.isoformat()
        } for score in top_scores]
            
        return jsonify(result), 200
    except DoesNotExist:
        return jsonify({'error': 'Mini-game not found'}), 404

# Submit a score for a mini-game
@minigames_bp.route('/<minigame_id>/score', methods=['POST'])
@jwt_required()
def submit_score(minigame_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not isinstance(data.get('score'), int):
        return jsonify({'error': 'Missing or invalid score submission'}), 400
    
    try:
        minigame = MiniGame.objects.get(id=minigame_id)
        
        # Check if the mini-game is still active
        if not minigame.is_active:
            return jsonify({'error': 'This mini-game is closed'}), 400
            
        # Check if the mini-game has expired
        if minigame.expires_at and minigame.expires_at < datetime.utcnow():
            return jsonify({'error': 'This mini-game has expired'}), 400
        
        # Create score submission
        score = MiniGameScore(
            student_id=user_id,
            score=data['score'],
            time_taken=data.get('time_taken')  # Optional time taken
        )
        
        minigame.scores.append(score)
        minigame.save()
        
        # Get user's high score
        user_scores = [s.score for s in minigame.scores if s.student_id == user_id]
        user_high_score = max(user_scores)
        
        # Get global high score
        all_scores = [s.score for s in minigame.scores]
        global_high_score = max(all_scores)
        
        # Get user rank
        ranked_students = {}
        for s in minigame.scores:
            if s.student_id not in ranked_students or s.score > ranked_students[s.student_id]:
                ranked_students[s.student_id] = s.score
                
        ranked_list = sorted(ranked_students.items(), key=lambda x: x[1], reverse=True)
        user_rank = next((i + 1 for i, (sid, _) in enumerate(ranked_list) if sid == user_id), 0)
        
        return jsonify({
            'message': 'Score submitted successfully',
            'score': data['score'],
            'user_high_score': user_high_score,
            'global_high_score': global_high_score,
            'user_rank': user_rank,
            'total_players': len(ranked_students)
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Mini-game not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get leaderboard for a mini-game
@minigames_bp.route('/<minigame_id>/leaderboard', methods=['GET'])
@jwt_required()
def minigame_leaderboard(minigame_id):
    try:
        minigame = MiniGame.objects.get(id=minigame_id)
        user_id = get_jwt_identity()
        
        # Get best score for each student
        best_scores = {}
        for score in minigame.scores:
            if score.student_id not in best_scores or score.score > best_scores[score.student_id]['score']:
                best_scores[score.student_id] = {
                    'student_id': score.student_id,
                    'score': score.score,
                    'time_taken': score.time_taken,
                    'achieved_at': score.achieved_at
                }
                
        # Sort by score (highest first), then by time taken (shortest first) if available
        leaderboard = sorted(best_scores.values(), 
                             key=lambda s: (-s['score'], s.get('time_taken', float('inf'))))
                             
        # Format results
        result = []
        for i, entry in enumerate(leaderboard):
            result.append({
                'rank': i + 1,
                'student_id': entry['student_id'],
                'score': entry['score'],
                'time_taken': entry['time_taken'],
                'achieved_at': entry['achieved_at'].isoformat(),
                'is_current_user': entry['student_id'] == user_id
            })
            
        return jsonify({
            'minigame_id': minigame_id,
            'title': minigame.title,
            'game_type': minigame.game_type,
            'total_players': len(best_scores),
            'leaderboard': result
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Mini-game not found'}), 404

# Close/deactivate a mini-game (teacher only)
@minigames_bp.route('/<minigame_id>/close', methods=['POST'])
@jwt_required()
def close_minigame(minigame_id):
    user_id = get_jwt_identity()
    
    try:
        minigame = MiniGame.objects.get(id=minigame_id)
        # Only the creator can close the mini-game
        if minigame.created_by != user_id:
            return jsonify({'error': 'Unauthorized: only the creator can close this mini-game'}), 403
            
        minigame.is_active = False
        minigame.save()
        return jsonify({'message': 'Mini-game closed successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'Mini-game not found'}), 404