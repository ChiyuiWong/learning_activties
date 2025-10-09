"""
Course Management Configuration

This file contains configuration settings specific to the course management module.
These settings control various aspects of course management functionality.
"""

import os

class CourseConfig:
    """Configuration class for course management module"""
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = os.path.join('uploads', 'courses')
    ALLOWED_EXTENSIONS = {
        'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf'},
        'presentations': {'ppt', 'pptx', 'odp'},
        'spreadsheets': {'xls', 'xlsx', 'ods', 'csv'},
        'images': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'},
        'archives': {'zip', 'rar', '7z', 'tar', 'gz'},
        'media': {'mp4', 'avi', 'mov', 'wmv', 'mp3', 'wav'}
    }
    
    # CSV Import Settings
    MAX_IMPORT_RECORDS = 1000  # Maximum records per import
    IMPORT_BATCH_SIZE = 100    # Process imports in batches
    IMPORT_TIMEOUT = 300       # 5 minutes timeout for imports
    
    # Pagination Settings
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Course Settings
    MAX_COURSE_TITLE_LENGTH = 200
    MAX_COURSE_DESCRIPTION_LENGTH = 2000
    MAX_STUDENTS_PER_COURSE = 1000
    
    # Material Settings
    MAX_MATERIAL_TITLE_LENGTH = 200
    MAX_MATERIAL_DESCRIPTION_LENGTH = 1000
    MATERIAL_CATEGORIES = [
        'lecture',
        'assignment', 
        'reading',
        'media',
        'reference',
        'other'
    ]
    
    # Announcement Settings
    MAX_ANNOUNCEMENT_TITLE_LENGTH = 200
    MAX_ANNOUNCEMENT_CONTENT_LENGTH = 5000
    ANNOUNCEMENT_EXPIRY_DAYS = 365  # Default expiry in days
    
    # Dashboard Settings
    RECENT_ACTIVITY_LIMIT = 10
    STATISTICS_CACHE_TIME = 300  # 5 minutes cache
    
    # Security Settings
    ENABLE_FILE_VIRUS_SCAN = False  # Future feature
    ENABLE_WATERMARKING = False     # Future feature
    TRACK_DOWNLOADS = True
    TRACK_ACCESS_LOGS = True
    
    # Feature Flags
    FEATURES = {
        'BULK_IMPORT': True,
        'BULK_EXPORT': True,
        'MATERIAL_UPLOAD': True,
        'MATERIAL_DOWNLOAD_TRACKING': True,
        'ANNOUNCEMENT_SCHEDULING': True,
        'COURSE_ANALYTICS': True,
        'LMS_INTEGRATION': False,      # Future feature
        'EMAIL_NOTIFICATIONS': False,   # Future feature
        'ADVANCED_ANALYTICS': False,    # Future feature
        'VIDEO_STREAMING': False,       # Future feature
        'DISCUSSION_FORUMS': False,     # Future feature
        'GRADEBOOK': False,            # Future feature
    }
    
    # University Settings
    SUPPORTED_UNIVERSITIES = [
        'PolyU',
        'HKU', 
        'CUHK',
        'HKUST',
        'CityU',
        'HKBU',
        'LingU',
        'EdUHK',
        'Other'
    ]
    
    # LMS Integration Settings (Future)
    LMS_PROVIDERS = {
        'canvas': {
            'name': 'Canvas LMS',
            'api_version': 'v1',
            'enabled': False
        },
        'moodle': {
            'name': 'Moodle',
            'api_version': 'v3.9',
            'enabled': False
        },
        'blackboard': {
            'name': 'Blackboard Learn',
            'api_version': 'v3000',
            'enabled': False
        }
    }
    
    # Validation Rules
    VALIDATION_RULES = {
        'course_code': {
            'min_length': 4,
            'max_length': 10,
            'pattern': r'^[A-Z]{2,4}\d{4}[A-Z]?$'  # e.g., COMP5241, MATH1001A
        },
        'student_id': {
            'min_length': 3,
            'max_length': 20,
            'pattern': r'^[A-Z0-9]+$'
        },
        'email': {
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }
    }
    
    # Error Messages
    ERROR_MESSAGES = {
        'file_too_large': 'File size exceeds maximum limit of 50MB',
        'invalid_file_type': 'File type not supported',
        'course_not_found': 'Course not found or access denied',
        'student_already_enrolled': 'Student is already enrolled in this course',
        'course_capacity_full': 'Course has reached maximum capacity',
        'import_file_invalid': 'Invalid CSV file format',
        'unauthorized_access': 'You do not have permission to perform this action',
        'material_not_available': 'Material is not available for download',
        'invalid_date_range': 'Invalid date range specified'
    }
    
    # Success Messages
    SUCCESS_MESSAGES = {
        'course_created': 'Course created successfully',
        'course_updated': 'Course updated successfully',
        'course_deleted': 'Course deleted successfully',
        'student_enrolled': 'Student enrolled successfully',
        'student_imported': 'Students imported successfully',
        'material_uploaded': 'Material uploaded successfully',
        'announcement_created': 'Announcement created successfully'
    }
    
    @classmethod
    def get_allowed_extensions_flat(cls):
        """Get all allowed file extensions as a flat set"""
        extensions = set()
        for category_extensions in cls.ALLOWED_EXTENSIONS.values():
            extensions.update(category_extensions)
        return extensions
    
    @classmethod
    def is_allowed_file(cls, filename):
        """Check if a filename has an allowed extension"""
        if '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in cls.get_allowed_extensions_flat()
    
    @classmethod
    def get_file_category(cls, filename):
        """Get the category of a file based on its extension"""
        if '.' not in filename:
            return 'other'
        extension = filename.rsplit('.', 1)[1].lower()
        
        for category, extensions in cls.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return category
        return 'other'
    
    @classmethod
    def validate_course_code(cls, course_code):
        """Validate course code format"""
        import re
        if not course_code:
            return False
        
        rules = cls.VALIDATION_RULES['course_code']
        if len(course_code) < rules['min_length'] or len(course_code) > rules['max_length']:
            return False
        
        return bool(re.match(rules['pattern'], course_code))
    
    @classmethod
    def validate_student_id(cls, student_id):
        """Validate student ID format"""
        import re
        if not student_id:
            return False
        
        rules = cls.VALIDATION_RULES['student_id']
        if len(student_id) < rules['min_length'] or len(student_id) > rules['max_length']:
            return False
        
        return bool(re.match(rules['pattern'], student_id))
    
    @classmethod
    def validate_email(cls, email):
        """Validate email format"""
        import re
        if not email:
            return True  # Email is optional in many cases
        
        pattern = cls.VALIDATION_RULES['email']['pattern']
        return bool(re.match(pattern, email))


# Development/Testing Configuration
class CourseTestConfig(CourseConfig):
    """Test configuration for course management"""
    
    # Override settings for testing
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB for testing
    MAX_IMPORT_RECORDS = 100  # Smaller limit for testing
    DEFAULT_PAGE_SIZE = 5     # Smaller pages for testing
    STATISTICS_CACHE_TIME = 10  # Shorter cache for testing
    
    # Enable all features for testing
    FEATURES = {
        'BULK_IMPORT': True,
        'BULK_EXPORT': True,
        'MATERIAL_UPLOAD': True,
        'MATERIAL_DOWNLOAD_TRACKING': True,
        'ANNOUNCEMENT_SCHEDULING': True,
        'COURSE_ANALYTICS': True,
        'LMS_INTEGRATION': True,       # Enable for testing
        'EMAIL_NOTIFICATIONS': True,    # Enable for testing
        'ADVANCED_ANALYTICS': True,     # Enable for testing
        'VIDEO_STREAMING': True,        # Enable for testing
        'DISCUSSION_FORUMS': True,      # Enable for testing
        'GRADEBOOK': True,             # Enable for testing
    }


# Production Configuration
class CourseProductionConfig(CourseConfig):
    """Production configuration for course management"""
    
    # Stricter limits for production
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB for production
    MAX_IMPORT_RECORDS = 5000  # Higher limit for production
    IMPORT_TIMEOUT = 600       # 10 minutes for large imports
    STATISTICS_CACHE_TIME = 900  # 15 minutes cache
    
    # Security settings for production
    ENABLE_FILE_VIRUS_SCAN = True
    TRACK_DOWNLOADS = True
    TRACK_ACCESS_LOGS = True
    
    # Conservative feature flags for production
    FEATURES = {
        'BULK_IMPORT': True,
        'BULK_EXPORT': True,
        'MATERIAL_UPLOAD': True,
        'MATERIAL_DOWNLOAD_TRACKING': True,
        'ANNOUNCEMENT_SCHEDULING': True,
        'COURSE_ANALYTICS': True,
        'LMS_INTEGRATION': False,      # Disable until fully tested
        'EMAIL_NOTIFICATIONS': False,   # Disable until configured
        'ADVANCED_ANALYTICS': False,    # Disable until optimized
        'VIDEO_STREAMING': False,       # Disable until infrastructure ready
        'DISCUSSION_FORUMS': False,     # Disable until implemented
        'GRADEBOOK': False,            # Disable until implemented
    }