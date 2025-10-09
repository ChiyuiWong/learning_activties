"""
Course Management Module - Keith's responsibility

This module provides comprehensive course management functionality including:
- Course creation and management
- Student enrollment and import/export  
- Course material management
- Announcement system
- Teacher and student dashboards
"""

from .models import (
    Course,
    CourseEnrollment,
    CourseMaterial,
    CourseAnnouncement,
    StudentImportLog,
    ImportError,
    MaterialDownloadLog,
    CourseModule
)

from .services import (
    CourseService,
    EnrollmentService,
    MaterialService,
    AnnouncementService,
    TeacherToolsService
)

from .routes import courses_bp

__all__ = [
    'Course', 'CourseEnrollment', 'CourseMaterial', 'CourseAnnouncement',
    'StudentImportLog', 'ImportError', 'MaterialDownloadLog', 'CourseModule',
    'CourseService', 'EnrollmentService', 'MaterialService', 'AnnouncementService', 'TeacherToolsService',
    'courses_bp'
]

__version__ = '1.0.0'
