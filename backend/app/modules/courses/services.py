"""
COMP5241 Group 10 - Courses Module Services
Responsible: Keith
Enhanced with comprehensive teacher tools and course management features
"""
from .models import (
    Course, CourseEnrollment, CourseModule, CourseAnnouncement, 
    CourseMaterial, StudentImportLog, ImportError, MaterialDownloadLog
)
from datetime import datetime
from mongoengine import Q
import csv
import io
import os
import uuid
from werkzeug.utils import secure_filename


class CourseService:
    """Service class for course operations with enhanced teacher tools"""
    
    @staticmethod
    def create_course(title, description, course_code, instructor_id, instructor_name=None, **kwargs):
        """Create new course with comprehensive features"""
        try:
            # Check if course code already exists
            if Course.objects(course_code=course_code).first():
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
                'semester': kwargs.get('semester', 'Fall 2025'),
                'university': kwargs.get('university', 'PolyU'),
                'is_published': kwargs.get('is_published', False),
                'start_date': kwargs.get('start_date'),
                'end_date': kwargs.get('end_date'),
                'enrollment_start_date': kwargs.get('enrollment_start_date'),
                'enrollment_end_date': kwargs.get('enrollment_end_date'),
                'lms_integration': kwargs.get('lms_integration', {}),
                'sync_with_lms': kwargs.get('sync_with_lms', False)
            }
            
            course = Course(**course_data)
            course.save()
            
            return {'success': True, 'course': course}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_courses_by_instructor(instructor_id, page=1, per_page=20, filters=None):
        """Get courses by instructor with pagination and filtering"""
        try:
            query = Q(instructor_id=instructor_id)
            
            # Apply filters
            if filters:
                if filters.get('is_active') is not None:
                    query &= Q(is_active=filters['is_active'])
                if filters.get('is_published') is not None:
                    query &= Q(is_published=filters['is_published'])
                if filters.get('category'):
                    query &= Q(category=filters['category'])
                if filters.get('search'):
                    search = filters['search']
                    query &= (Q(title__icontains=search) | 
                             Q(course_code__icontains=search) | 
                             Q(description__icontains=search))
            
            # Apply ordering
            order_by = filters.get('order_by', '-created_at') if filters else '-created_at'
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            total = Course.objects(query).count()
            
            # Get courses
            courses = Course.objects(query).order_by('-created_at').skip(offset).limit(per_page)
            
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
            course = Course.objects(id=course_id).first()
            if not course:
                return {'success': False, 'error': 'Course not found'}
            
            result = {'success': True, 'course': course}
            
            if include_stats:
                # Get enrollment statistics
                enrollments = CourseEnrollment.objects(course_id=str(course.id))
                stats = {
                    'total_enrolled': enrollments.count(),
                    'active_students': enrollments.filter(status='enrolled').count(),
                    'completed': enrollments.filter(status='completed').count(),
                    'dropped': enrollments.filter(status='dropped').count(),
                    'materials_count': CourseMaterial.objects(course_id=str(course.id)).count(),
                    'announcements_count': CourseAnnouncement.objects(course_id=str(course.id)).count()
                }
                result['stats'] = stats
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_course(course_id, instructor_id, update_data):
        """Update course (only by instructor)"""
        try:
            course = Course.objects(id=course_id, instructor_id=instructor_id).first()
            if not course:
                return {'success': False, 'error': 'Course not found or access denied'}
            
            # Update allowed fields
            allowed_fields = [
                'title', 'description', 'category', 'difficulty_level', 'max_students',
                'semester', 'university', 'start_date', 'end_date', 'is_published',
                'lms_integration', 'sync_with_lms'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(course, field, update_data[field])
            
            course.save()
            return {'success': True, 'course': course}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_course(course_id, instructor_id):
        """Soft delete course (only by instructor)"""
        try:
            course = Course.objects(id=course_id, instructor_id=instructor_id).first()
            if not course:
                return {'success': False, 'error': 'Course not found or access denied'}
            
            course.is_active = False
            course.save()
            return {'success': True, 'message': 'Course deactivated successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class EnrollmentService:
    """Service class for enrollment operations with bulk import support"""
    
    @staticmethod
    def enroll_student(course_id, student_id, student_name=None, student_email=None, **kwargs):
        """Enroll single student in course"""
        try:
            # Check if course exists and has capacity
            course = Course.objects(id=course_id).first()
            if not course:
                return {'success': False, 'error': 'Course not found'}
            
            if course.current_enrollment >= course.max_students:
                return {'success': False, 'error': 'Course is full'}
            
            # Check if already enrolled
            existing = CourseEnrollment.objects(course_id=course_id, student_id=student_id).first()
            if existing:
                return {'success': False, 'error': 'Student already enrolled'}
            
            # Create enrollment
            enrollment_data = {
                'course_id': course_id,
                'student_id': student_id,
                'student_name': student_name or 'Unknown',
                'student_email': student_email or '',
                'university': kwargs.get('university', ''),
                'import_source': kwargs.get('import_source', 'manual'),
                'import_batch_id': kwargs.get('import_batch_id'),
                'external_id': kwargs.get('external_id')
            }
            
            enrollment = CourseEnrollment(**enrollment_data)
            enrollment.save()
            
            # Update course enrollment count
            course.current_enrollment += 1
            course.save()
            
            return {'success': True, 'enrollment': enrollment}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def import_students_from_csv(course_id, csv_content, imported_by, filename=None):
        """Import students from CSV with duplicate prevention and error tracking"""
        try:
            # Create import log
            batch_id = str(uuid.uuid4())
            import_log = StudentImportLog(
                course_id=course_id,
                batch_id=batch_id,
                imported_by=imported_by,
                import_type='csv',
                original_filename=filename,
                file_size=len(csv_content)
            )
            import_log.save()
            
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
                        error = ImportError(
                            import_log_id=str(import_log.id),
                            row_number=row_number,
                            student_data=dict(row),
                            error_type='missing_field',
                            error_message='Missing student_id'
                        )
                        error.save()
                        results['failed_imports'] += 1
                        results['errors'].append({
                            'row': row_number,
                            'error': 'Missing student_id',
                            'data': dict(row)
                        })
                        continue
                    
                    # Check for duplicates
                    existing = CourseEnrollment.objects(
                        course_id=course_id, 
                        student_id=row['student_id']
                    ).first()
                    
                    if existing:
                        error = ImportError(
                            import_log_id=str(import_log.id),
                            row_number=row_number,
                            student_data=dict(row),
                            error_type='duplicate',
                            error_message=f'Student {row["student_id"]} already enrolled'
                        )
                        error.save()
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
                        error = ImportError(
                            import_log_id=str(import_log.id),
                            row_number=row_number,
                            student_data=dict(row),
                            error_type='validation_error',
                            error_message=enrollment_result['error']
                        )
                        error.save()
                        results['failed_imports'] += 1
                        results['errors'].append({
                            'row': row_number,
                            'error': enrollment_result['error'],
                            'data': dict(row)
                        })
                
                except Exception as e:
                    error = ImportError(
                        import_log_id=str(import_log.id),
                        row_number=row_number,
                        student_data=dict(row),
                        error_type='processing_error',
                        error_message=str(e)
                    )
                    error.save()
                    results['failed_imports'] += 1
                    results['errors'].append({
                        'row': row_number,
                        'error': str(e),
                        'data': dict(row)
                    })
            
            # Update import log
            import_log.total_records = results['total_records']
            import_log.successful_imports = results['successful_imports']
            import_log.failed_imports = results['failed_imports']
            import_log.duplicate_records = results['duplicate_records']
            import_log.status = 'completed'
            import_log.completed_at = datetime.utcnow()
            import_log.save()
            
            results['import_log_id'] = str(import_log.id)
            results['batch_id'] = batch_id
            
            return {'success': True, 'results': results}
        
        except Exception as e:
            # Update import log with error
            if 'import_log' in locals():
                import_log.status = 'failed'
                import_log.error_message = str(e)
                import_log.completed_at = datetime.utcnow()
                import_log.save()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_course_students(course_id, page=1, per_page=50, filters=None):
        """Get students enrolled in course with pagination"""
        try:
            query = Q(course_id=course_id)
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    query &= Q(status=filters['status'])
                if filters.get('university'):
                    query &= Q(university=filters['university'])
                if filters.get('search'):
                    search = filters['search']
                    query &= (Q(student_name__icontains=search) | 
                             Q(student_email__icontains=search) | 
                             Q(student_id__icontains=search))
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            total = CourseEnrollment.objects(query).count()
            
            # Get enrollments
            enrollments = CourseEnrollment.objects(query).order_by('-enrollment_date').skip(offset).limit(per_page)
            
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
            output = io.StringIO()
            
            if include_errors and import_log_id:
                # Export import errors
                errors = ImportError.objects(import_log_id=import_log_id)
                if errors:
                    # Get field names from first error's student data
                    first_error = errors.first()
                    fieldnames = list(first_error.student_data.keys()) + ['error_type', 'error_message', 'row_number']
                    
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for error in errors:
                        row_data = dict(error.student_data)
                        row_data.update({
                            'error_type': error.error_type,
                            'error_message': error.error_message,
                            'row_number': error.row_number
                        })
                        writer.writerow(row_data)
            else:
                # Export enrolled students
                enrollments = CourseEnrollment.objects(course_id=course_id)
                
                fieldnames = ['student_id', 'student_name', 'student_email', 'enrollment_date', 
                             'status', 'progress_percentage', 'university', 'external_id']
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for enrollment in enrollments:
                    writer.writerow({
                        'student_id': enrollment.student_id,
                        'student_name': enrollment.student_name,
                        'student_email': enrollment.student_email,
                        'enrollment_date': enrollment.enrollment_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': enrollment.status,
                        'progress_percentage': enrollment.progress_percentage,
                        'university': enrollment.university,
                        'external_id': enrollment.external_id
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
            # Validate course access
            course = Course.objects(id=course_id, instructor_id=uploaded_by).first()
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
                'is_published': kwargs.get('is_published', False),
                'available_from': kwargs.get('available_from'),
                'available_until': kwargs.get('available_until')
            }
            
            material = CourseMaterial(**material_data)
            material.save()
            
            return {'success': True, 'material': material}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_course_materials(course_id, page=1, per_page=20, filters=None, user_id=None, user_role=None):
        """Get course materials with access control"""
        try:
            query = Q(course_id=course_id)
            
            # Apply visibility filters based on user role
            if user_role != 'teacher':
                query &= Q(is_published=True)
                # Check availability dates
                now = datetime.utcnow()
                query &= (Q(available_from__lte=now) | Q(available_from=None))
                query &= (Q(available_until__gte=now) | Q(available_until=None))
            
            # Apply additional filters
            if filters:
                if filters.get('category'):
                    query &= Q(category=filters['category'])
                if filters.get('file_type'):
                    query &= Q(file_type=filters['file_type'])
                if filters.get('module_id'):
                    query &= Q(module_id=filters['module_id'])
                if filters.get('search'):
                    search = filters['search']
                    query &= (Q(title__icontains=search) | Q(description__icontains=search))
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            total = CourseMaterial.objects(query).count()
            
            # Get materials
            materials = CourseMaterial.objects(query).order_by('order', '-uploaded_at').skip(offset).limit(per_page)
            
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
            material = CourseMaterial.objects(id=material_id).first()
            if not material:
                return {'success': False, 'error': 'Material not found'}
            
            # Check if file exists
            if not os.path.exists(material.file_path):
                return {'success': False, 'error': 'File not found on server'}
            
            # Log download
            download_log = MaterialDownloadLog(
                material_id=material_id,
                course_id=material.course_id,
                downloaded_by=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            download_log.save()
            
            # Update download count
            material.download_count += 1
            material.save()
            
            return {'success': True, 'file_path': material.file_path, 'filename': material.file_name}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class AnnouncementService:
    """Service class for course announcements"""
    
    @staticmethod
    def create_announcement(course_id, title, content, created_by, created_by_name=None, **kwargs):
        """Create course announcement"""
        try:
            # Validate course access
            course = Course.objects(id=course_id, instructor_id=created_by).first()
            if not course:
                return {'success': False, 'error': 'Course not found or access denied'}
            
            announcement_data = {
                'course_id': course_id,
                'title': title,
                'content': content,
                'created_by': created_by,
                'created_by_name': created_by_name or 'Unknown',
                'is_pinned': kwargs.get('is_pinned', False),
                'is_urgent': kwargs.get('is_urgent', False),
                'priority': kwargs.get('priority', 2),
                'publish_at': kwargs.get('publish_at'),
                'expire_at': kwargs.get('expire_at'),
                'attachment_ids': kwargs.get('attachment_ids', [])
            }
            
            announcement = CourseAnnouncement(**announcement_data)
            announcement.save()
            
            return {'success': True, 'announcement': announcement}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_course_announcements(course_id, page=1, per_page=10, user_role=None):
        """Get course announcements with filtering"""
        try:
            query = Q(course_id=course_id)
            
            # Apply visibility filters for students
            if user_role != 'teacher':
                now = datetime.utcnow()
                query &= (Q(publish_at__lte=now) | Q(publish_at=None))
                query &= (Q(expire_at__gte=now) | Q(expire_at=None))
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            total = CourseAnnouncement.objects(query).count()
            
            # Get announcements (pinned first, then by date)
            announcements = CourseAnnouncement.objects(query).order_by('-is_pinned', '-created_at').skip(offset).limit(per_page)
            
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
            # Get instructor's courses
            courses = Course.objects(instructor_id=instructor_id)
            course_ids = [str(course.id) for course in courses]
            
            # Get enrollment statistics
            total_enrollments = CourseEnrollment.objects(course_id__in=course_ids).count()
            active_students = CourseEnrollment.objects(course_id__in=course_ids, status='enrolled').count()
            
            # Get material statistics
            total_materials = CourseMaterial.objects(course_id__in=course_ids).count()
            total_downloads = sum([m.download_count for m in CourseMaterial.objects(course_id__in=course_ids)])
            
            # Get announcement statistics
            total_announcements = CourseAnnouncement.objects(course_id__in=course_ids).count()
            
            # Recent activity
            recent_enrollments = CourseEnrollment.objects(
                course_id__in=course_ids
            ).order_by('-enrollment_date').limit(10)
            
            recent_downloads = MaterialDownloadLog.objects(
                course_id__in=course_ids
            ).order_by('-downloaded_at').limit(10)
            
            stats = {
                'courses': {
                    'total': courses.count(),
                    'published': courses.filter(is_published=True).count(),
                    'active': courses.filter(is_active=True).count()
                },
                'students': {
                    'total_enrollments': total_enrollments,
                    'active_students': active_students,
                    'completed': CourseEnrollment.objects(course_id__in=course_ids, status='completed').count()
                },
                'materials': {
                    'total': total_materials,
                    'total_downloads': total_downloads,
                    'published': CourseMaterial.objects(course_id__in=course_ids, is_published=True).count()
                },
                'announcements': {
                    'total': total_announcements,
                    'pinned': CourseAnnouncement.objects(course_id__in=course_ids, is_pinned=True).count()
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
            query = Q(imported_by=instructor_id)
            if course_id:
                query &= Q(course_id=course_id)
            
            offset = (page - 1) * per_page
            total = StudentImportLog.objects(query).count()
            
            import_logs = StudentImportLog.objects(query).order_by('-started_at').skip(offset).limit(per_page)
            
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