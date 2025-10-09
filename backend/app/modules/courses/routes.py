"""
COMP5241 Group 10 - Courses Module Routes
Responsible: Keith
Enhanced with comprehensive teacher tools and course management features
"""
from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from .services import (
    CourseService, EnrollmentService, MaterialService, 
    AnnouncementService, TeacherToolsService
)
import os
import io

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/health', methods=['GET'])
def courses_health():
    """Health check for Courses module"""
    return jsonify({
        'status': 'healthy', 
        'module': 'courses',
        'message': 'Courses module is running with enhanced features'
    })


# ============================================
# COURSE MANAGEMENT ROUTES
# ============================================

@courses_bp.route('/', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_courses():
    """Get courses with pagination and filtering"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
    
    # Get filters
    filters = {
        'is_active': request.args.get('is_active', type=bool),
        'is_published': request.args.get('is_published', type=bool),
        'category': request.args.get('category'),
        'semester': request.args.get('semester'),
        'search': request.args.get('search')
    }
    
    # Remove None filters
    filters = {k: v for k, v in filters.items() if v is not None}
    
    if user_role == 'teacher':
        # Get instructor's courses
        result = CourseService.get_courses_by_instructor(current_user, page, per_page, filters)
    else:
        # For students, get enrolled courses
        result = EnrollmentService.get_enrolled_courses(current_user, page, per_page)
    
    if result['success']:
        return jsonify({
            'success': True,
            'courses': [course.to_dict() if hasattr(course, 'to_dict') else str(course) for course in result.get('courses', [])],
            'pagination': result.get('pagination', {})
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/', methods=['POST'])
@jwt_required(locations=["cookies"])
def create_course():
    """Create new course (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['title', 'course_code']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    # Create course
    result = CourseService.create_course(
        title=data['title'],
        description=data.get('description', ''),
        course_code=data['course_code'],
        instructor_id=current_user,
        instructor_name=user_claims.get('username', 'Unknown'),
        category=data.get('category', ''),
        difficulty_level=data.get('difficulty_level', 'beginner'),
        max_students=data.get('max_students', 100),
        semester=data.get('semester', ''),
        university=data.get('university', ''),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        is_published=data.get('is_published', False)
    )
    
    if result['success']:
        return jsonify({
            'success': True,
            'course': str(result['course'].id),
            'message': 'Course created successfully'
        }), 201
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/<course_id>', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_course(course_id):
    """Get specific course with statistics"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    include_stats = request.args.get('include_stats', False, type=bool)
    
    result = CourseService.get_course_by_id(course_id, include_stats=include_stats)
    
    if result['success']:
        return jsonify({
            'success': True,
            'course': str(result['course'].id) if result['course'] else None,
            'stats': result.get('stats', {})
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 404


@courses_bp.route('/<course_id>', methods=['PUT'])
@jwt_required(locations=["cookies"])
def update_course(course_id):
    """Update course (instructor only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    result = CourseService.update_course(course_id, current_user, data)
    
    if result['success']:
        return jsonify({
            'success': True,
            'course': str(result['course'].id),
            'message': 'Course updated successfully'
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/<course_id>', methods=['DELETE'])
@jwt_required(locations=["cookies"])
def delete_course(course_id):
    """Delete course (instructor only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    result = CourseService.delete_course(course_id, current_user)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message']
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


# ============================================
# ENROLLMENT MANAGEMENT ROUTES
# ============================================

@courses_bp.route('/<course_id>/enroll', methods=['POST'])
@jwt_required(locations=["cookies"])
def enroll_in_course(course_id):
    """Enroll student in course"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    
    result = EnrollmentService.enroll_student(
        course_id=course_id,
        student_id=current_user,
        student_name=user_claims.get('username', 'Unknown'),
        student_email=user_claims.get('email', ''),
        university=user_claims.get('university', '')
    )
    
    if result['success']:
        return jsonify({
            'success': True,
            'enrollment': str(result['enrollment'].id),
            'message': 'Successfully enrolled in course'
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/<course_id>/students', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_course_students(course_id):
    """Get students enrolled in course with pagination"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    # Only teachers can view student list
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    
    # Get filters
    filters = {
        'status': request.args.get('status'),
        'university': request.args.get('university'),
        'search': request.args.get('search')
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    result = EnrollmentService.get_course_students(course_id, page, per_page, filters)
    
    if result['success']:
        return jsonify({
            'success': True,
            'students': [str(student.id) if student else None for student in result.get('students', [])],
            'pagination': result.get('pagination', {})
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/<course_id>/students/import', methods=['POST'])
@jwt_required(locations=["cookies"])
def import_students(course_id):
    """Import students from CSV (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    # Check if file is uploaded
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'success': False, 'error': 'File must be CSV format'}), 400
    
    try:
        # Read CSV content
        csv_content = file.read().decode('utf-8')
        
        # Import students
        result = EnrollmentService.import_students_from_csv(
            course_id=course_id,
            csv_content=csv_content,
            imported_by=current_user,
            filename=secure_filename(file.filename)
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'results': result['results'],
                'message': 'Import completed'
            }), 200
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
    
    except UnicodeDecodeError:
        return jsonify({'success': False, 'error': 'Invalid file encoding. Please use UTF-8.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@courses_bp.route('/<course_id>/students/export', methods=['GET'])
@jwt_required(locations=["cookies"])
def export_students(course_id):
    """Export students to CSV (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    result = EnrollmentService.export_students_csv(course_id)
    
    if result['success']:
        # Create response
        output = io.StringIO(result['csv_content'])
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=students_{course_id}.csv'
        return response
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/<course_id>/students/<student_id>/progress', methods=['PUT'])
@jwt_required(locations=["cookies"])
def update_student_progress(course_id, student_id):
    """Update student progress (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    data = request.get_json()
    if not data or 'progress_percentage' not in data:
        return jsonify({'success': False, 'error': 'progress_percentage is required'}), 400
    
    progress = data['progress_percentage']
    if not isinstance(progress, (int, float)) or progress < 0 or progress > 100:
        return jsonify({'success': False, 'error': 'progress_percentage must be between 0 and 100'}), 400
    
    result = EnrollmentService.update_student_progress(course_id, student_id, progress)
    
    if result['success']:
        return jsonify({
            'success': True,
            'enrollment': str(result['enrollment'].id),
            'message': 'Progress updated successfully'
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


# ============================================
# COURSE MATERIALS ROUTES
# ============================================

@courses_bp.route('/<course_id>/materials', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_course_materials(course_id):
    """Get course materials with pagination and filtering"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Get filters
    filters = {
        'category': request.args.get('category'),
        'file_type': request.args.get('file_type'),
        'module_id': request.args.get('module_id'),
        'search': request.args.get('search')
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    result = MaterialService.get_course_materials(
        course_id=course_id,
        page=page,
        per_page=per_page,
        filters=filters,
        user_id=current_user,
        user_role=user_role
    )
    
    if result['success']:
        return jsonify({
            'success': True,
            'materials': [str(material.id) if material else None for material in result.get('materials', [])],
            'pagination': result.get('pagination', {})
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/<course_id>/materials', methods=['POST'])
@jwt_required(locations=["cookies"])
def upload_material(course_id):
    """Upload course material (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    # Check if file is uploaded
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Get form data
    title = request.form.get('title')
    if not title:
        return jsonify({'success': False, 'error': 'Title is required'}), 400
    
    # Allowed file types
    allowed_extensions = {'pdf', 'pptx', 'ppt', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'txt', 'zip'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        return jsonify({
            'success': False, 
            'error': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
        }), 400
    
    # Check file size (max 50MB)
    if len(file.read()) > 50 * 1024 * 1024:
        return jsonify({'success': False, 'error': 'File too large. Maximum size is 50MB.'}), 400
    
    file.seek(0)  # Reset file pointer after size check
    
    try:
        result = MaterialService.upload_material(
            course_id=course_id,
            file=file,
            title=title,
            uploaded_by=current_user,
            description=request.form.get('description', ''),
            category=request.form.get('category', 'other'),
            module_id=request.form.get('module_id'),
            is_published=request.form.get('is_published', 'false').lower() == 'true'
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'material': str(result['material'].id),
                'message': 'Material uploaded successfully'
            }), 201
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@courses_bp.route('/materials/<material_id>/download', methods=['GET'])
@jwt_required(locations=["cookies"])
def download_material(material_id):
    """Download course material"""
    current_user = get_jwt_identity()
    
    # Get client info for logging
    ip_address = request.environ.get('REMOTE_ADDR')
    user_agent = request.headers.get('User-Agent')
    
    result = MaterialService.download_material(
        material_id=material_id,
        user_id=current_user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if result['success']:
        try:
            return send_file(
                result['file_path'],
                as_attachment=True,
                download_name=result['filename']
            )
        except FileNotFoundError:
            return jsonify({'success': False, 'error': 'File not found on server'}), 404
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/materials/<material_id>', methods=['DELETE'])
@jwt_required(locations=["cookies"])
def delete_material(material_id):
    """Delete course material (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    result = MaterialService.delete_material(material_id, current_user)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message']
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


# ============================================
# ANNOUNCEMENTS ROUTES
# ============================================

@courses_bp.route('/<course_id>/announcements', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_announcements(course_id):
    """Get course announcements"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    result = AnnouncementService.get_course_announcements(
        course_id=course_id,
        page=page,
        per_page=per_page,
        user_role=user_role
    )
    
    if result['success']:
        return jsonify({
            'success': True,
            'announcements': [str(ann.id) if ann else None for ann in result.get('announcements', [])],
            'pagination': result.get('pagination', {})
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/<course_id>/announcements', methods=['POST'])
@jwt_required(locations=["cookies"])
def create_announcement(course_id):
    """Create course announcement (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Validate required fields
    if not data.get('title') or not data.get('content'):
        return jsonify({'success': False, 'error': 'Title and content are required'}), 400
    
    result = AnnouncementService.create_announcement(
        course_id=course_id,
        title=data['title'],
        content=data['content'],
        created_by=current_user,
        created_by_name=user_claims.get('username', 'Unknown'),
        is_pinned=data.get('is_pinned', False),
        is_urgent=data.get('is_urgent', False),
        priority=data.get('priority', 2),
        publish_at=data.get('publish_at'),
        expire_at=data.get('expire_at')
    )
    
    if result['success']:
        return jsonify({
            'success': True,
            'announcement': str(result['announcement'].id),
            'message': 'Announcement created successfully'
        }), 201
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/announcements/<announcement_id>', methods=['PUT'])
@jwt_required(locations=["cookies"])
def update_announcement(announcement_id):
    """Update announcement (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    result = AnnouncementService.update_announcement(announcement_id, current_user, data)
    
    if result['success']:
        return jsonify({
            'success': True,
            'announcement': str(result['announcement'].id),
            'message': 'Announcement updated successfully'
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/announcements/<announcement_id>', methods=['DELETE'])
@jwt_required(locations=["cookies"])
def delete_announcement(announcement_id):
    """Delete announcement (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    result = AnnouncementService.delete_announcement(announcement_id, current_user)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message']
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


# ============================================
# TEACHER TOOLS & ANALYTICS ROUTES
# ============================================

@courses_bp.route('/teacher/dashboard', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_teacher_dashboard():
    """Get teacher dashboard statistics"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    result = TeacherToolsService.get_dashboard_stats(current_user)
    
    if result['success']:
        return jsonify({
            'success': True,
            'stats': result['stats']
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/teacher/imports', methods=['GET'])
@jwt_required(locations=["cookies"])
def get_import_history():
    """Get import history for teacher"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    course_id = request.args.get('course_id')
    
    result = TeacherToolsService.get_import_history(
        instructor_id=current_user,
        course_id=course_id,
        page=page,
        per_page=per_page
    )
    
    if result['success']:
        return jsonify({
            'success': True,
            'import_logs': [str(log.id) if log else None for log in result.get('import_logs', [])],
            'pagination': result.get('pagination', {})
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@courses_bp.route('/imports/<import_log_id>/errors/export', methods=['GET'])
@jwt_required(locations=["cookies"])
def export_import_errors(import_log_id):
    """Export import errors to CSV (teacher only)"""
    current_user = get_jwt_identity()
    user_claims = get_jwt()
    user_role = user_claims.get('role', 'student')
    
    if user_role != 'teacher':
        return jsonify({'success': False, 'error': 'Access denied. Teachers only.'}), 403
    
    result = EnrollmentService.export_students_csv(
        course_id=None,  # Not needed for error export
        include_errors=True,
        import_log_id=import_log_id
    )
    
    if result['success']:
        # Create response
        output = io.StringIO(result['csv_content'])
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=import_errors_{import_log_id}.csv'
        return response
    else:
        return jsonify({'success': False, 'error': result['error']}), 400
