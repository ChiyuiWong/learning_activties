"""
COMP5241 Group 10 - Courses Module Services
Responsible: Keith
Enhanced with comprehensive teacher tools and course management features
"""
from datetime import datetime
import csv
import io
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from bson import ObjectId
from config.database import get_db_connection


class CourseService:
    """Service class for course operations with enhanced teacher tools"""
    
    @staticmethod
    def create_course(title, description, course_code, instructor_id, instructor_name=None, **kwargs):
        """Create new course with comprehensive features"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            # Check if course code already exists
            if db.courses.find_one({'course_code': course_code}):
                return {'success': False, 'error': 'Course code already exists'}
            
            course_data = {
                'title': title,
                'description': description,
                'course_code': course_code,
                'instructor_id': instructor_id,
                'instructor_name': instructor_name or 'Unknown',
                'category': kwargs.get('category', 'General'),
                'difficulty_level': kwargs.get('difficulty_level', 'intermediate'),
                'max_students': kwargs.get('max_students', 50),
                'current_enrollment': 0,
                'is_active': True,
                'is_published': kwargs.get('is_published', False),
                'start_date': kwargs.get('start_date'),
                'end_date': kwargs.get('end_date'),
                'semester': kwargs.get('semester', 'Fall 2025'),
                'university': kwargs.get('university', 'PolyU'),
                'lms_integration': kwargs.get('lms_integration', {}),
                'sync_with_lms': kwargs.get('sync_with_lms', False),
                'last_lms_sync': None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = db.courses.insert_one(course_data)
            course_data['_id'] = result.inserted_id
            
            return {'success': True, 'course': course_data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_courses_by_instructor(instructor_id, page=1, per_page=20, filters=None):
        """Get courses by instructor with pagination and filtering"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            query = {'instructor_id': instructor_id}
            
            # Apply filters
            if filters:
                if filters.get('is_active') is not None:
                    query['is_active'] = filters['is_active']
                if filters.get('is_published') is not None:
                    query['is_published'] = filters['is_published']
                if filters.get('category'):
                    query['category'] = filters['category']
                if filters.get('search'):
                    search = filters['search']
                    query['$or'] = [
                        {'title': {'$regex': search, '$options': 'i'}},
                        {'course_code': {'$regex': search, '$options': 'i'}},
                        {'description': {'$regex': search, '$options': 'i'}}
                    ]
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            total = db.courses.count_documents(query)
            
            # Get courses
            courses = list(db.courses.find(query).sort('created_at', -1).skip(offset).limit(per_page))
            
            return {
                'success': True,
                'courses': courses,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_course_by_id(course_id, include_stats=False):
        """Get specific course by ID with optional statistics"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            course = db.courses.find_one({'_id': ObjectId(course_id)})
            if not course:
                return {'success': False, 'error': 'Course not found'}
            
            result = {'success': True, 'course': course}
            
            if include_stats:
                # Get enrollment statistics
                enrollments = list(db.course_enrollments.find({'course_id': course_id}))
                stats = {
                    'total_enrolled': len(enrollments),
                    'active_students': len([e for e in enrollments if e.get('status') == 'enrolled']),
                    'completed': len([e for e in enrollments if e.get('status') == 'completed']),
                    'dropped': len([e for e in enrollments if e.get('status') == 'dropped']),
                    'materials_count': db.course_materials.count_documents({'course_id': course_id}),
                    'announcements_count': db.course_announcements.count_documents({'course_id': course_id})
                }
                result['stats'] = stats
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_course(course_id, instructor_id, update_data):
        """Update course (only by instructor)"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            course = db.courses.find_one({'_id': ObjectId(course_id), 'instructor_id': instructor_id})
            if not course:
                return {'success': False, 'error': 'Course not found or access denied'}
            
            # Update allowed fields
            allowed_fields = [
                'title', 'description', 'category', 'difficulty_level', 'max_students',
                'semester', 'university', 'start_date', 'end_date', 'is_published',
                'lms_integration', 'sync_with_lms'
            ]
            
            update_dict = {}
            for field in allowed_fields:
                if field in update_data:
                    update_dict[field] = update_data[field]
            
            update_dict['updated_at'] = datetime.utcnow()
            
            db.courses.update_one({'_id': ObjectId(course_id)}, {'$set': update_dict})
            
            # Get updated course
            updated_course = db.courses.find_one({'_id': ObjectId(course_id)})
            return {'success': True, 'course': updated_course}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_course(course_id, instructor_id):
        """Soft delete course (only by instructor)"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            course = db.courses.find_one({'_id': ObjectId(course_id), 'instructor_id': instructor_id})
            if not course:
                return {'success': False, 'error': 'Course not found or access denied'}
            
            db.courses.update_one({'_id': ObjectId(course_id)}, {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}})
            return {'success': True, 'message': 'Course deactivated successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class EnrollmentService:
    """Service class for enrollment operations with bulk import support"""
    
    @staticmethod
    def enroll_student(course_id, student_id, student_name=None, student_email=None, **kwargs):
        """Enroll single student in course"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            # Check if course exists and has capacity
            course = db.courses.find_one({'_id': ObjectId(course_id)})
            if not course:
                return {'success': False, 'error': 'Course not found'}
            
            if course.get('current_enrollment', 0) >= course.get('max_students', 100):
                return {'success': False, 'error': 'Course is full'}
            
            # Check if already enrolled
            existing = db.course_enrollments.find_one({'course_id': course_id, 'student_id': student_id})
            if existing:
                return {'success': False, 'error': 'Student already enrolled'}
            
            # Create enrollment
            enrollment_data = {
                'course_id': course_id,
                'student_id': student_id,
                'student_name': student_name or 'Unknown',
                'student_email': student_email or '',
                'enrollment_date': datetime.utcnow(),
                'progress_percentage': 0,
                'status': 'enrolled',
                'university': kwargs.get('university', ''),
                'import_source': kwargs.get('import_source', 'manual'),
                'import_batch_id': kwargs.get('import_batch_id'),
                'external_id': kwargs.get('external_id')
            }
            
            result = db.course_enrollments.insert_one(enrollment_data)
            enrollment_data['_id'] = result.inserted_id
            
            # Update course enrollment count
            db.courses.update_one({'_id': ObjectId(course_id)}, {'$inc': {'current_enrollment': 1}})
            
            return {'success': True, 'enrollment': enrollment_data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def import_students_from_csv(course_id, csv_content, imported_by, filename=None):
        """Import students from CSV with duplicate prevention and error tracking"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            # Create import log
            batch_id = str(uuid.uuid4())
            import_log_data = {
                'course_id': course_id,
                'batch_id': batch_id,
                'imported_by': imported_by,
                'import_type': 'csv',
                'original_filename': filename,
                'file_size': len(csv_content),
                'total_records': 0,
                'successful_imports': 0,
                'failed_imports': 0,
                'duplicate_records': 0,
                'status': 'processing',
                'started_at': datetime.utcnow()
            }
            
            result = db.student_import_logs.insert_one(import_log_data)
            import_log_id = result.inserted_id
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            results = {
                'total_records': 0,
                'successful_imports': 0,
                'failed_imports': 0,
                'duplicate_records': 0,
                'errors': []
            }
            
            row_number = 0
            for row in csv_reader:
                row_number += 1
                results['total_records'] += 1
                
                try:
                    # Validate required fields
                    if not row.get('student_id'):
                        error_data = {
                            'import_log_id': str(import_log_id),
                            'row_number': row_number,
                            'student_data': dict(row),
                            'error_type': 'missing_field',
                            'error_message': 'Missing student_id'
                        }
                        db.import_errors.insert_one(error_data)
                        results['failed_imports'] += 1
                        results['errors'].append({
                            'row': row_number,
                            'error': 'Missing student_id',
                            'data': dict(row)
                        })
                        continue
                    
                    # Check for duplicates
                    existing = db.course_enrollments.find_one({
                        'course_id': course_id, 
                        'student_id': row['student_id']
                    })
                    
                    if existing:
                        error_data = {
                            'import_log_id': str(import_log_id),
                            'row_number': row_number,
                            'student_data': dict(row),
                            'error_type': 'duplicate',
                            'error_message': f'Student {row["student_id"]} already enrolled'
                        }
                        db.import_errors.insert_one(error_data)
                        results['duplicate_records'] += 1
                        results['errors'].append({
                            'row': row_number,
                            'error': f'Student {row["student_id"]} already enrolled',
                            'data': dict(row)
                        })
                        continue
                    
                    # Enroll student
                    enrollment_result = EnrollmentService.enroll_student(
                        course_id=course_id,
                        student_id=row['student_id'],
                        student_name=row.get('student_name', ''),
                        student_email=row.get('email', ''),
                        university=row.get('university', ''),
                        external_id=row.get('external_id', ''),
                        import_source='csv',
                        import_batch_id=batch_id
                    )
                    
                    if enrollment_result['success']:
                        results['successful_imports'] += 1
                    else:
                        error_data = {
                            'import_log_id': str(import_log_id),
                            'row_number': row_number,
                            'student_data': dict(row),
                            'error_type': 'validation_error',
                            'error_message': enrollment_result['error']
                        }
                        db.import_errors.insert_one(error_data)
                        results['failed_imports'] += 1
                        results['errors'].append({
                            'row': row_number,
                            'error': enrollment_result['error'],
                            'data': dict(row)
                        })
                
                except Exception as e:
                    error_data = {
                        'import_log_id': str(import_log_id),
                        'row_number': row_number,
                        'student_data': dict(row),
                        'error_type': 'processing_error',
                        'error_message': str(e)
                    }
                    db.import_errors.insert_one(error_data)
                    results['failed_imports'] += 1
                    results['errors'].append({
                        'row': row_number,
                        'error': str(e),
                        'data': dict(row)
                    })
            
            # Update import log
            db.student_import_logs.update_one(
                {'_id': import_log_id},
                {'$set': {
                    'total_records': results['total_records'],
                    'successful_imports': results['successful_imports'],
                    'failed_imports': results['failed_imports'],
                    'duplicate_records': results['duplicate_records'],
                    'status': 'completed',
                    'completed_at': datetime.utcnow()
                }}
            )
            
            results['import_log_id'] = str(import_log_id)
            results['batch_id'] = batch_id
            
            return {'success': True, 'results': results}
        
        except Exception as e:
            # Update import log with error
            if 'import_log_id' in locals():
                db.student_import_logs.update_one(
                    {'_id': import_log_id},
                    {'$set': {
                        'status': 'failed',
                        'error_message': str(e),
                        'completed_at': datetime.utcnow()
                    }}
                )
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_course_students(course_id, page=1, per_page=50, filters=None):
        """Get students enrolled in course with pagination"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            query = {'course_id': course_id}
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    query['status'] = filters['status']
                if filters.get('university'):
                    query['university'] = filters['university']
                if filters.get('search'):
                    search = filters['search']
                    query['$or'] = [
                        {'student_name': {'$regex': search, '$options': 'i'}},
                        {'student_email': {'$regex': search, '$options': 'i'}},
                        {'student_id': {'$regex': search, '$options': 'i'}}
                    ]
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            total = db.course_enrollments.count_documents(query)
            
            # Get enrollments
            enrollments = list(db.course_enrollments.find(query).sort('enrollment_date', -1).skip(offset).limit(per_page))
            
            return {
                'success': True,
                'students': enrollments,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def export_students_csv(course_id, include_errors=False, import_log_id=None):
        """Export students or import errors to CSV"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            output = io.StringIO()
            
            if include_errors and import_log_id:
                # Export import errors
                errors = list(db.import_errors.find({'import_log_id': import_log_id}))
                if errors:
                    # Get field names from first error's student data
                    first_error = errors[0]
                    fieldnames = list(first_error['student_data'].keys()) + ['error_type', 'error_message', 'row_number']
                    
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for error in errors:
                        row_data = dict(error['student_data'])
                        row_data.update({
                            'error_type': error['error_type'],
                            'error_message': error['error_message'],
                            'row_number': error['row_number']
                        })
                        writer.writerow(row_data)
            else:
                # Export enrolled students
                enrollments = list(db.course_enrollments.find({'course_id': course_id}))
                
                fieldnames = ['student_id', 'student_name', 'student_email', 'enrollment_date', 
                             'status', 'progress_percentage', 'university', 'external_id']
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for enrollment in enrollments:
                    writer.writerow({
                        'student_id': enrollment['student_id'],
                        'student_name': enrollment['student_name'],
                        'student_email': enrollment['student_email'],
                        'enrollment_date': enrollment['enrollment_date'].strftime('%Y-%m-%d %H:%M:%S'),
                        'status': enrollment['status'],
                        'progress_percentage': enrollment['progress_percentage'],
                        'university': enrollment['university'],
                        'external_id': enrollment['external_id']
                    })
            
            return {'success': True, 'csv_content': output.getvalue()}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class MaterialService:
    """Service class for course material management"""
    
    @staticmethod
    def upload_material(course_id, file, title, uploaded_by, **kwargs):
        """Upload course material"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            # Validate course access
            course = db.courses.find_one({'_id': ObjectId(course_id), 'instructor_id': uploaded_by})
            if not course:
                return {'success': False, 'error': 'Course not found or access denied'}
            
            # Generate secure filename
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            # Create upload directory if not exists
            upload_dir = f'uploads/courses/{course_id}/materials'
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Create material record
            material_data = {
                'course_id': course_id,
                'title': title,
                'description': kwargs.get('description', ''),
                'file_name': filename,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_type': file_extension,
                'mime_type': file.content_type,
                'category': kwargs.get('category', 'other'),
                'module_id': kwargs.get('module_id'),
                'uploaded_by': uploaded_by,
                'uploaded_at': datetime.utcnow(),
                'is_published': kwargs.get('is_published', False),
                'available_from': kwargs.get('available_from'),
                'available_until': kwargs.get('available_until'),
                'download_count': 0
            }
            
            result = db.course_materials.insert_one(material_data)
            material_data['_id'] = result.inserted_id
            
            return {'success': True, 'material': material_data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_course_materials(course_id, page=1, per_page=20, filters=None, user_id=None, user_role=None):
        """Get course materials with access control"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            query = {'course_id': course_id}
            
            # Apply visibility filters based on user role
            if user_role != 'teacher':
                query['is_published'] = True
                # Check availability dates
                now = datetime.utcnow()
                query['$or'] = [
                    {'available_from': {'$lte': now}},
                    {'available_from': None}
                ]
                query['$and'] = [
                    {'$or': [{'available_until': {'$gte': now}}, {'available_until': None}]}
                ]
            
            # Apply additional filters
            if filters:
                if filters.get('category'):
                    query['category'] = filters['category']
                if filters.get('file_type'):
                    query['file_type'] = filters['file_type']
                if filters.get('module_id'):
                    query['module_id'] = filters['module_id']
                if filters.get('search'):
                    search = filters['search']
                    query['$or'] = [
                        {'title': {'$regex': search, '$options': 'i'}},
                        {'description': {'$regex': search, '$options': 'i'}}
                    ]
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            total = db.course_materials.count_documents(query)
            
            # Get materials
            materials = list(db.course_materials.find(query).sort([('order', 1), ('uploaded_at', -1)]).skip(offset).limit(per_page))
            
            return {
                'success': True,
                'materials': materials,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def download_material(material_id, user_id, ip_address=None, user_agent=None):
        """Download material with access logging"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            material = db.course_materials.find_one({'_id': ObjectId(material_id)})
            if not material:
                return {'success': False, 'error': 'Material not found'}
            
            # Check if file exists
            if not os.path.exists(material['file_path']):
                return {'success': False, 'error': 'File not found on server'}
            
            # Log download
            download_log_data = {
                'material_id': material_id,
                'course_id': material['course_id'],
                'downloaded_by': user_id,
                'downloaded_at': datetime.utcnow(),
                'ip_address': ip_address,
                'user_agent': user_agent
            }
            db.material_download_logs.insert_one(download_log_data)
            
            # Update download count
            db.course_materials.update_one({'_id': ObjectId(material_id)}, {'$inc': {'download_count': 1}})
            
            return {'success': True, 'file_path': material['file_path'], 'filename': material['file_name']}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class AnnouncementService:
    """Service class for course announcements"""
    
    @staticmethod
    def create_announcement(course_id, title, content, created_by, created_by_name=None, **kwargs):
        """Create course announcement"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            # Validate course access
            course = db.courses.find_one({'_id': ObjectId(course_id), 'instructor_id': created_by})
            if not course:
                return {'success': False, 'error': 'Course not found or access denied'}
            
            announcement_data = {
                'course_id': course_id,
                'title': title,
                'content': content,
                'created_by': created_by,
                'created_by_name': created_by_name or 'Unknown',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_pinned': kwargs.get('is_pinned', False),
                'is_urgent': kwargs.get('is_urgent', False),
                'priority': kwargs.get('priority', 2),
                'publish_at': kwargs.get('publish_at'),
                'expire_at': kwargs.get('expire_at'),
                'attachment_ids': kwargs.get('attachment_ids', [])
            }
            
            result = db.course_announcements.insert_one(announcement_data)
            announcement_data['_id'] = result.inserted_id
            
            return {'success': True, 'announcement': announcement_data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_course_announcements(course_id, page=1, per_page=10, user_role=None):
        """Get course announcements with filtering"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            query = {'course_id': course_id}
            
            # Apply visibility filters for students
            if user_role != 'teacher':
                now = datetime.utcnow()
                query['$or'] = [
                    {'publish_at': {'$lte': now}},
                    {'publish_at': None}
                ]
                query['$and'] = [
                    {'$or': [{'expire_at': {'$gte': now}}, {'expire_at': None}]}
                ]
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            total = db.course_announcements.count_documents(query)
            
            # Get announcements (pinned first, then by date)
            announcements = list(db.course_announcements.find(query).sort([('is_pinned', -1), ('created_at', -1)]).skip(offset).limit(per_page))
            
            return {
                'success': True,
                'announcements': announcements,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class TeacherToolsService:
    """Comprehensive service for teacher-specific tools and analytics"""
    
    @staticmethod
    def get_dashboard_stats(instructor_id):
        """Get comprehensive dashboard statistics for teacher"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            # Get instructor's courses
            courses = list(db.courses.find({'instructor_id': instructor_id}))
            course_ids = [str(course['_id']) for course in courses]
            
            # Get enrollment statistics
            total_enrollments = db.course_enrollments.count_documents({'course_id': {'$in': course_ids}})
            active_students = db.course_enrollments.count_documents({'course_id': {'$in': course_ids}, 'status': 'enrolled'})
            
            # Get material statistics
            total_materials = db.course_materials.count_documents({'course_id': {'$in': course_ids}})
            material_download_logs = list(db.material_download_logs.find({'course_id': {'$in': course_ids}}))
            total_downloads = len(material_download_logs)
            
            # Get announcement statistics
            total_announcements = db.course_announcements.count_documents({'course_id': {'$in': course_ids}})
            
            # Recent activity
            recent_enrollments = list(db.course_enrollments.find(
                {'course_id': {'$in': course_ids}}
            ).sort('enrollment_date', -1).limit(10))
            
            recent_downloads = list(db.material_download_logs.find(
                {'course_id': {'$in': course_ids}}
            ).sort('downloaded_at', -1).limit(10))
            
            stats = {
                'courses': {
                    'total': len(courses),
                    'published': len([c for c in courses if c.get('is_published')]),
                    'active': len([c for c in courses if c.get('is_active')])
                },
                'students': {
                    'total_enrollments': total_enrollments,
                    'active_students': active_students,
                    'completed': db.course_enrollments.count_documents({'course_id': {'$in': course_ids}, 'status': 'completed'})
                },
                'materials': {
                    'total': total_materials,
                    'total_downloads': total_downloads,
                    'published': db.course_materials.count_documents({'course_id': {'$in': course_ids}, 'is_published': True})
                },
                'announcements': {
                    'total': total_announcements,
                    'pinned': db.course_announcements.count_documents({'course_id': {'$in': course_ids}, 'is_pinned': True})
                },
                'recent_activity': {
                    'enrollments': recent_enrollments,
                    'downloads': recent_downloads
                }
            }
            
            return {'success': True, 'stats': stats}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_import_history(instructor_id, course_id=None, page=1, per_page=20):
        """Get import history for instructor"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
            
            query = {'imported_by': instructor_id}
            if course_id:
                query['course_id'] = course_id
            
            offset = (page - 1) * per_page
            total = db.student_import_logs.count_documents(query)
            
            import_logs = list(db.student_import_logs.find(query).sort('started_at', -1).skip(offset).limit(per_page))
            
            return {
                'success': True,
                'import_logs': import_logs,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}