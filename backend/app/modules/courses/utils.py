"""
Course Management Utility Functions

This module provides utility functions for the course management system including
file handling, validation, formatting, and helper functions.
"""

import os
import re
import csv
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

from .config import CourseConfig


class FileHandler:
    """Utility class for handling file operations"""
    
    @staticmethod
    def secure_filename_with_timestamp(filename: str) -> str:
        """
        Generate a secure filename with timestamp prefix
        
        Args:
            filename: Original filename
            
        Returns:
            Secure filename with timestamp
        """
        if not filename:
            return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_unnamed"
        
        # Secure the filename
        secured = secure_filename(filename)
        if not secured:
            # If filename becomes empty after securing, generate one
            extension = filename.rsplit('.', 1)[1] if '.' in filename else 'txt'
            secured = f"file.{extension}"
        
        # Add timestamp prefix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{timestamp}_{secured}"
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """
        Calculate MD5 hash of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError):
            return ""
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive file information
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'size': stat.st_size,
                'mime_type': mime_type or 'application/octet-stream',
                'created_at': datetime.fromtimestamp(stat.st_ctime),
                'modified_at': datetime.fromtimestamp(stat.st_mtime),
                'hash': FileHandler.get_file_hash(file_path),
                'exists': True
            }
        except (IOError, OSError):
            return {
                'size': 0,
                'mime_type': 'application/octet-stream',
                'created_at': None,
                'modified_at': None,
                'hash': '',
                'exists': False
            }
    
    @staticmethod
    def ensure_upload_directory(course_id: str, subdirectory: str = None) -> str:
        """
        Ensure upload directory exists for a course
        
        Args:
            course_id: Course identifier
            subdirectory: Optional subdirectory (e.g., 'materials', 'imports')
            
        Returns:
            Full path to the directory
        """
        base_path = CourseConfig.UPLOAD_FOLDER
        course_path = os.path.join(base_path, str(course_id))
        
        if subdirectory:
            full_path = os.path.join(course_path, subdirectory)
        else:
            full_path = course_path
        
        os.makedirs(full_path, exist_ok=True)
        return full_path
    
    @staticmethod
    def cleanup_temp_files(older_than_hours: int = 24):
        """
        Clean up temporary files older than specified hours
        
        Args:
            older_than_hours: Remove files older than this many hours
        """
        temp_path = os.path.join(CourseConfig.UPLOAD_FOLDER, 'temp')
        if not os.path.exists(temp_path):
            return
        
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        for root, dirs, files in os.walk(temp_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if datetime.fromtimestamp(os.path.getctime(file_path)) < cutoff_time:
                        os.remove(file_path)
                except (IOError, OSError):
                    pass  # Skip files we can't access


class CSVHandler:
    """Utility class for handling CSV operations"""
    
    @staticmethod
    def validate_csv_format(file_path: str, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate CSV file format and required columns
        
        Args:
            file_path: Path to CSV file
            required_columns: List of required column names
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Try to detect the delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                # Read the header
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    errors.append("CSV file has no headers")
                    return False, errors
                
                # Check for required columns
                missing_columns = set(required_columns) - set(headers)
                if missing_columns:
                    errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                
                # Check for empty file
                try:
                    first_row = next(reader)
                    if not any(first_row.values()):
                        errors.append("CSV file appears to be empty")
                except StopIteration:
                    errors.append("CSV file has no data rows")
        
        except UnicodeDecodeError:
            errors.append("CSV file encoding is not supported. Please use UTF-8.")
        except csv.Error as e:
            errors.append(f"CSV format error: {str(e)}")
        except Exception as e:
            errors.append(f"Error reading CSV file: {str(e)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def read_csv_data(file_path: str, max_rows: int = None) -> List[Dict[str, str]]:
        """
        Read CSV data into a list of dictionaries
        
        Args:
            file_path: Path to CSV file
            max_rows: Maximum number of rows to read
            
        Returns:
            List of dictionaries representing CSV rows
        """
        data = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Auto-detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for i, row in enumerate(reader):
                    if max_rows and i >= max_rows:
                        break
                    
                    # Clean up the row data
                    cleaned_row = {k.strip(): v.strip() if v else '' for k, v in row.items()}
                    data.append(cleaned_row)
        
        except Exception as e:
            current_app.logger.error(f"Error reading CSV data: {str(e)}")
        
        return data
    
    @staticmethod
    def write_csv_data(file_path: str, data: List[Dict[str, Any]], fieldnames: List[str] = None):
        """
        Write data to CSV file
        
        Args:
            file_path: Path to output CSV file
            data: List of dictionaries to write
            fieldnames: Optional list of field names (uses keys from first row if not provided)
        """
        if not data:
            return
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            current_app.logger.error(f"Error writing CSV data: {str(e)}")


class ValidationHelper:
    """Utility class for validation functions"""
    
    @staticmethod
    def validate_course_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate course data
        
        Args:
            data: Course data dictionary
            
        Returns:
            Tuple of (is_valid, field_errors)
        """
        errors = {}
        
        # Required fields
        required_fields = ['title', 'course_code']
        for field in required_fields:
            if not data.get(field):
                errors.setdefault(field, []).append(f"{field.replace('_', ' ').title()} is required")
        
        # Title validation
        title = data.get('title', '')
        if len(title) > CourseConfig.MAX_COURSE_TITLE_LENGTH:
            errors.setdefault('title', []).append(f"Title must be less than {CourseConfig.MAX_COURSE_TITLE_LENGTH} characters")
        
        # Course code validation
        course_code = data.get('course_code', '')
        if course_code and not CourseConfig.validate_course_code(course_code):
            errors.setdefault('course_code', []).append("Invalid course code format")
        
        # Description validation
        description = data.get('description', '')
        if len(description) > CourseConfig.MAX_COURSE_DESCRIPTION_LENGTH:
            errors.setdefault('description', []).append(f"Description must be less than {CourseConfig.MAX_COURSE_DESCRIPTION_LENGTH} characters")
        
        # Max students validation
        max_students = data.get('max_students')
        if max_students is not None:
            try:
                max_students = int(max_students)
                if max_students < 1 or max_students > CourseConfig.MAX_STUDENTS_PER_COURSE:
                    errors.setdefault('max_students', []).append(f"Max students must be between 1 and {CourseConfig.MAX_STUDENTS_PER_COURSE}")
            except (ValueError, TypeError):
                errors.setdefault('max_students', []).append("Max students must be a valid number")
        
        # University validation
        university = data.get('university', '')
        if university and university not in CourseConfig.SUPPORTED_UNIVERSITIES:
            errors.setdefault('university', []).append("Unsupported university")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_student_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate student data
        
        Args:
            data: Student data dictionary
            
        Returns:
            Tuple of (is_valid, field_errors)
        """
        errors = {}
        
        # Required fields
        required_fields = ['student_id', 'student_name']
        for field in required_fields:
            if not data.get(field):
                errors.setdefault(field, []).append(f"{field.replace('_', ' ').title()} is required")
        
        # Student ID validation
        student_id = data.get('student_id', '')
        if student_id and not CourseConfig.validate_student_id(student_id):
            errors.setdefault('student_id', []).append("Invalid student ID format")
        
        # Email validation
        email = data.get('email', '')
        if email and not CourseConfig.validate_email(email):
            errors.setdefault('email', []).append("Invalid email format")
        
        # University validation
        university = data.get('university', '')
        if university and university not in CourseConfig.SUPPORTED_UNIVERSITIES:
            errors.setdefault('university', []).append("Unsupported university")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_material_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate material data
        
        Args:
            data: Material data dictionary
            
        Returns:
            Tuple of (is_valid, field_errors)
        """
        errors = {}
        
        # Required fields
        if not data.get('title'):
            errors.setdefault('title', []).append("Title is required")
        
        # Title validation
        title = data.get('title', '')
        if len(title) > CourseConfig.MAX_MATERIAL_TITLE_LENGTH:
            errors.setdefault('title', []).append(f"Title must be less than {CourseConfig.MAX_MATERIAL_TITLE_LENGTH} characters")
        
        # Description validation
        description = data.get('description', '')
        if len(description) > CourseConfig.MAX_MATERIAL_DESCRIPTION_LENGTH:
            errors.setdefault('description', []).append(f"Description must be less than {CourseConfig.MAX_MATERIAL_DESCRIPTION_LENGTH} characters")
        
        # Category validation
        category = data.get('category', '')
        if category and category not in CourseConfig.MATERIAL_CATEGORIES:
            errors.setdefault('category', []).append("Invalid material category")
        
        return len(errors) == 0, errors


class DateTimeHelper:
    """Utility class for date and time operations"""
    
    @staticmethod
    def parse_date_string(date_string: str) -> Optional[datetime]:
        """
        Parse various date string formats into datetime object
        
        Args:
            date_string: Date string to parse
            
        Returns:
            datetime object or None if parsing fails
        """
        if not date_string:
            return None
        
        # Common date formats to try
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%m-%d-%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def format_datetime_for_display(dt: datetime) -> str:
        """
        Format datetime for user display
        
        Args:
            dt: datetime object
            
        Returns:
            Formatted datetime string
        """
        if not dt:
            return ""
        
        return dt.strftime('%B %d, %Y at %I:%M %p')
    
    @staticmethod
    def get_relative_time(dt: datetime) -> str:
        """
        Get relative time string (e.g., "2 hours ago", "3 days ago")
        
        Args:
            dt: datetime object
            
        Returns:
            Relative time string
        """
        if not dt:
            return ""
        
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"


class PaginationHelper:
    """Utility class for pagination operations"""
    
    @staticmethod
    def paginate_query(query, page: int, per_page: int):
        """
        Apply pagination to a MongoEngine query
        
        Args:
            query: MongoEngine query object
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Tuple of (items, pagination_info)
        """
        # Ensure valid page and per_page values
        page = max(1, page)
        per_page = min(max(1, per_page), CourseConfig.MAX_PAGE_SIZE)
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        total = query.count()
        
        # Get items for current page
        items = query.skip(offset).limit(per_page)
        
        # Calculate pagination info
        pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < pages
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
            'has_prev': has_prev,
            'has_next': has_next
        }
        
        return items, pagination_info


class SecurityHelper:
    """Utility class for security-related operations"""
    
    @staticmethod
    def generate_secure_token() -> str:
        """
        Generate a secure random token
        
        Returns:
            Secure token string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for security
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed_file"
        
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\.\.+', '.', filename)  # Remove path traversal attempts
        filename = filename.strip('. ')  # Remove leading/trailing dots and spaces
        
        # Ensure filename is not empty after sanitization
        if not filename:
            return "unnamed_file"
        
        return filename
    
    @staticmethod
    def is_safe_path(path: str, base_path: str) -> bool:
        """
        Check if a path is safe (no path traversal)
        
        Args:
            path: Path to check
            base_path: Base path that should contain the file
            
        Returns:
            True if path is safe
        """
        try:
            real_path = os.path.realpath(path)
            real_base = os.path.realpath(base_path)
            return real_path.startswith(real_base)
        except (OSError, ValueError):
            return False


# Convenience functions for common operations
def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def generate_course_code() -> str:
    """
    Generate a random course code for testing
    
    Returns:
        Random course code
    """
    import random
    import string
    
    prefix = ''.join(random.choices(string.ascii_uppercase, k=4))
    number = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{number}"


def create_sample_csv_data(num_records: int = 10) -> List[Dict[str, str]]:
    """
    Create sample CSV data for testing
    
    Args:
        num_records: Number of records to create
        
    Returns:
        List of dictionaries representing student data
    """
    import random
    
    universities = ['PolyU', 'HKU', 'CUHK', 'HKUST', 'CityU']
    first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Tom', 'Emma', 'Chris', 'Anna']
    last_names = ['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Miller', 'Taylor', 'Anderson', 'Thomas', 'Jackson']
    
    data = []
    for i in range(num_records):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        record = {
            'student_id': f"STU{i+1:03d}",
            'student_name': f"{first_name} {last_name}",
            'email': f"{first_name.lower()}.{last_name.lower()}@student.edu",
            'university': random.choice(universities),
            'external_id': f"EXT{i+1:04d}"
        }
        data.append(record)
    
    return data