"""
COMP5241 Group 10 - Courses Module Models
Responsible: Keith
Enhanced with comprehensive teacher tools and course management features
"""
from mongoengine import Document, StringField, DateTimeField, ListField, BooleanField, IntField, FloatField, DictField, EmbeddedDocument, EmbeddedDocumentField
from datetime import datetime
from bson import ObjectId


class StudentInfo(EmbeddedDocument):
    """Embedded document for student information in bulk operations"""
    student_id = StringField(required=True)
    student_name = StringField(max_length=100)
    email = StringField()
    university = StringField(max_length=200)
    external_id = StringField()  # For LMS integration (Canvas, Moodle ID)
    import_source = StringField(choices=['csv', 'lms', 'manual'], default='manual')


class Course(Document):
    """Enhanced model for courses with teacher tools support"""
    title = StringField(required=True, max_length=200)
    description = StringField()
    course_code = StringField(required=True, unique=True, max_length=20)
    instructor_id = StringField(required=True)  # teacher user_id
    instructor_name = StringField(max_length=100)  # Cached for performance
    category = StringField(max_length=100)
    difficulty_level = StringField(choices=['beginner', 'intermediate', 'advanced'], default='beginner')
    max_students = IntField(default=100)
    current_enrollment = IntField(default=0)  # Cached count for performance
    is_active = BooleanField(default=True)
    is_published = BooleanField(default=False)
    start_date = DateTimeField()
    end_date = DateTimeField()
    semester = StringField(max_length=50)  # e.g., "Fall 2025", "Spring 2026"
    university = StringField(max_length=200)  # Support for multi-university
    
    # LMS Integration
    lms_integration = DictField()  # Store LMS-specific data (Canvas course ID, Moodle ID, etc.)
    sync_with_lms = BooleanField(default=False)
    last_lms_sync = DateTimeField()
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'courses',
        'indexes': [
            'course_code', 
            'instructor_id', 
            'category', 
            'is_active',
            'is_published',
            'university',
            'semester',
            ('instructor_id', 'is_active'),  # Compound index for teacher's active courses
            ('university', 'category'),     # Compound index for cross-university search
            'created_at'
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class CourseEnrollment(Document):
    """Enhanced model for course enrollments with bulk import support"""
    course_id = StringField(required=True)
    student_id = StringField(required=True)
    student_name = StringField(max_length=100)  # Cached for performance
    student_email = StringField()  # Cached for performance
    enrollment_date = DateTimeField(default=datetime.utcnow)
    completion_date = DateTimeField()
    progress_percentage = IntField(default=0)
    final_grade = StringField()
    status = StringField(choices=['enrolled', 'completed', 'dropped', 'pending'], default='enrolled')
    
    # Import tracking
    import_source = StringField(choices=['csv', 'lms', 'manual'], default='manual')
    import_batch_id = StringField()  # Track bulk imports
    external_id = StringField()      # LMS student ID
    
    # University info for cross-university support
    university = StringField(max_length=200)
    
    meta = {
        'collection': 'course_enrollments',
        'indexes': [
            'course_id', 
            'student_id', 
            'status', 
            'enrollment_date',
            'university',
            'import_batch_id',
            'external_id',
            ('course_id', 'status'),     # Compound index for course student lists
            ('student_id', 'status'),    # Compound index for student's courses
            ('course_id', 'student_id')  # Compound index to prevent duplicates
        ]
    }


class CourseMaterial(Document):
    """Model for course materials (files, documents, etc.)"""
    course_id = StringField(required=True)
    title = StringField(required=True, max_length=200)
    description = StringField()
    file_name = StringField(required=True)
    file_path = StringField(required=True)  # Storage path
    file_size = IntField()  # File size in bytes
    file_type = StringField(max_length=50)  # pdf, pptx, doc, jpg, etc.
    mime_type = StringField(max_length=100)
    
    # Organization
    module_id = StringField()  # Optional: associate with course module
    category = StringField(choices=['lecture', 'assignment', 'reading', 'media', 'other'], default='other')
    order = IntField(default=0)
    
    # Access control
    is_published = BooleanField(default=False)
    available_from = DateTimeField()
    available_until = DateTimeField()
    
    # Upload info
    uploaded_by = StringField(required=True)  # instructor user_id
    uploaded_at = DateTimeField(default=datetime.utcnow)
    
    # Download tracking
    download_count = IntField(default=0)
    
    # LMS integration
    lms_file_id = StringField()  # For LMS sync
    sync_with_lms = BooleanField(default=False)
    
    meta = {
        'collection': 'course_materials',
        'indexes': [
            'course_id',
            'file_type',
            'category',
            'is_published',
            'uploaded_by',
            'uploaded_at',
            ('course_id', 'category'),
            ('course_id', 'is_published'),
            ('course_id', 'order')
        ]
    }


class CourseModule(Document):
    """Enhanced model for course modules/chapters"""
    course_id = StringField(required=True)
    title = StringField(required=True, max_length=200)
    description = StringField()
    order = IntField(required=True)
    content = StringField()
    
    # Material references
    material_ids = ListField(StringField())  # Reference to CourseMaterial objects
    
    # Publishing
    is_published = BooleanField(default=False)
    available_from = DateTimeField()
    available_until = DateTimeField()
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'course_modules',
        'indexes': [
            'course_id', 
            'order', 
            'is_published',
            ('course_id', 'order'),
            ('course_id', 'is_published')
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class CourseAnnouncement(Document):
    """Enhanced model for course announcements"""
    course_id = StringField(required=True)
    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    created_by = StringField(required=True)  # instructor user_id
    created_by_name = StringField(max_length=100)  # Cached for performance
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Announcement features
    is_pinned = BooleanField(default=False)
    is_urgent = BooleanField(default=False)
    priority = IntField(choices=[1, 2, 3], default=2)  # 1=High, 2=Normal, 3=Low
    
    # Scheduling
    publish_at = DateTimeField()  # Optional: schedule announcement
    expire_at = DateTimeField()   # Optional: auto-hide after date
    
    # Attachments
    attachment_ids = ListField(StringField())  # Reference to CourseMaterial objects
    
    meta = {
        'collection': 'course_announcements',
        'indexes': [
            'course_id', 
            'created_at', 
            'is_pinned',
            'is_urgent',
            'priority',
            'publish_at',
            ('course_id', '-created_at'),  # For chronological listing
            ('course_id', 'is_pinned', '-created_at')
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class StudentImportLog(Document):
    """Model to track student import operations"""
    course_id = StringField(required=True)
    batch_id = StringField(required=True)  # Unique identifier for this import
    imported_by = StringField(required=True)  # instructor user_id
    import_type = StringField(choices=['csv', 'lms'], required=True)
    
    # Import results
    total_records = IntField(default=0)
    successful_imports = IntField(default=0)
    failed_imports = IntField(default=0)
    duplicate_records = IntField(default=0)
    
    # File info
    original_filename = StringField()
    file_size = IntField()
    
    # Status
    status = StringField(choices=['processing', 'completed', 'failed'], default='processing')
    error_message = StringField()
    
    # Timestamps  
    started_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    
    meta = {
        'collection': 'student_import_logs',
        'indexes': [
            'course_id',
            'batch_id',
            'imported_by',
            'started_at',
            'status',
            ('course_id', 'imported_by')
        ]
    }


class ImportError(Document):
    """Model to track individual import errors for reporting"""
    import_log_id = StringField(required=True)  # Reference to StudentImportLog
    row_number = IntField()
    student_data = DictField()  # The original data that failed to import
    error_type = StringField(required=True)  # 'duplicate', 'validation_error', 'missing_field'
    error_message = StringField(required=True)
    
    meta = {
        'collection': 'import_errors',
        'indexes': [
            'import_log_id',
            'error_type'
        ]
    }


class MaterialDownloadLog(Document):
    """Model to track material download activities"""
    material_id = StringField(required=True)
    course_id = StringField(required=True)
    downloaded_by = StringField(required=True)  # student user_id
    downloaded_at = DateTimeField(default=datetime.utcnow)
    ip_address = StringField()
    user_agent = StringField()
    
    meta = {
        'collection': 'material_download_logs',
        'indexes': [
            'material_id',
            'course_id',
            'downloaded_by',
            'downloaded_at',
            ('course_id', 'downloaded_by'),
            ('material_id', 'downloaded_at')
        ]
    }
