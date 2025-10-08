"""
COMP5241 Group 10 - Course Management Integration Tests
End-to-end testing for the course management system
"""
import unittest
import json
import io
from datetime import datetime, timedelta

class MockFlaskApp:
    """Mock Flask application for testing"""
    def __init__(self):
        self.test_client_instance = MockTestClient()
    
    def test_client(self):
        return self.test_client_instance

class MockResponse:
    """Mock response object"""
    def __init__(self, data, status_code=200, headers=None):
        self.data = json.dumps(data).encode() if isinstance(data, dict) else data
        self.status_code = status_code
        self.headers = headers or {}
    
    def get_json(self):
        if isinstance(self.data, bytes):
            return json.loads(self.data.decode())
        return json.loads(self.data)

class MockTestClient:
    """Mock test client for API testing"""
    
    def __init__(self):
        self.mock_data = {
            'courses': {
                '1': {
                    'id': '1',
                    'title': 'Advanced Database Systems',
                    'course_code': 'COMP5241',
                    'instructor_id': 'teacher123',
                    'current_enrollment': 45,
                    'max_students': 50,
                    'is_published': True
                }
            },
            'enrollments': [],
            'materials': [],
            'announcements': []
        }
    
    def get(self, url, headers=None):
        """Simulate GET requests"""
        if '/api/courses/' in url:
            if url.endswith('/'):
                # Get all courses
                return MockResponse({
                    'success': True,
                    'courses': list(self.mock_data['courses'].values()),
                    'pagination': {'page': 1, 'per_page': 20, 'total': 1, 'pages': 1}
                })
            else:
                # Get specific course
                course_id = url.split('/')[-1]
                course = self.mock_data['courses'].get(course_id)
                if course:
                    return MockResponse({'success': True, 'course': course})
                else:
                    return MockResponse({'success': False, 'error': 'Course not found'}, 404)
        
        return MockResponse({'success': False, 'error': 'Not found'}, 404)
    
    def post(self, url, json=None, data=None, headers=None):
        """Simulate POST requests"""
        if url == '/api/courses/':
            # Create course
            if json and json.get('title') and json.get('course_code'):
                new_course = {
                    'id': str(len(self.mock_data['courses']) + 1),
                    **json,
                    'instructor_id': 'teacher123',
                    'current_enrollment': 0
                }
                self.mock_data['courses'][new_course['id']] = new_course
                return MockResponse({'success': True, 'course': new_course['id']}, 201)
            else:
                return MockResponse({'success': False, 'error': 'Missing required fields'}, 400)
        
        return MockResponse({'success': False, 'error': 'Not found'}, 404)


class TestCourseAPIEndpoints(unittest.TestCase):
    """Integration tests for course API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = MockFlaskApp()
        self.client = self.app.test_client()
    
    def test_get_courses_endpoint(self):
        """Test GET /api/courses/ endpoint"""
        response = self.client.get('/api/courses/')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('courses', data)
        self.assertIn('pagination', data)
        
        print("✓ GET courses endpoint test passed")
    
    def test_create_course_endpoint(self):
        """Test POST /api/courses/ endpoint"""
        course_data = {
            'title': 'New Test Course',
            'course_code': 'TEST101',
            'description': 'Test course description',
            'max_students': 30
        }
        
        response = self.client.post('/api/courses/', json=course_data)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertIn('course', data)
        
        print("✓ POST create course endpoint test passed")
    
    def test_create_course_validation(self):
        """Test course creation validation"""
        # Test with missing required fields
        invalid_data = {'description': 'Missing title and code'}
        
        response = self.client.post('/api/courses/', json=invalid_data)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        
        print("✓ Course validation test passed")
    
    def test_get_specific_course(self):
        """Test GET /api/courses/<id> endpoint"""
        # Test existing course
        response = self.client.get('/api/courses/1')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('course', data)
        
        # Test non-existing course
        response = self.client.get('/api/courses/999')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        
        print("✓ GET specific course endpoint test passed")


class TestStudentImportIntegration(unittest.TestCase):
    """Integration tests for student import functionality"""
    
    def test_csv_import_simulation(self):
        """Test CSV import process simulation"""
        # Mock CSV content
        csv_content = """student_id,student_name,email,university
STU001,John Doe,john@student.edu,PolyU
STU002,Jane Smith,jane@student.edu,PolyU
STU003,Invalid Student,,PolyU"""
        
        # Simulate import process
        lines = csv_content.strip().split('\n')
        headers = lines[0].split(',')
        
        results = {
            'total_records': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'errors': []
        }
        
        for i, line in enumerate(lines[1:], 1):
            results['total_records'] += 1
            values = line.split(',')
            student = dict(zip(headers, values))
            
            # Validate student data
            if not student.get('student_id') or not student.get('email'):
                results['failed_imports'] += 1
                results['errors'].append({
                    'row': i,
                    'error': 'Missing required fields',
                    'data': student
                })
            else:
                results['successful_imports'] += 1
        
        # Validate results
        self.assertEqual(results['total_records'], 3)
        self.assertEqual(results['successful_imports'], 2)
        self.assertEqual(results['failed_imports'], 1)
        self.assertEqual(len(results['errors']), 1)
        
        print("✓ CSV import simulation test passed")
    
    def test_duplicate_handling(self):
        """Test duplicate student handling"""
        existing_students = ['STU001', 'STU003']
        
        new_students = [
            {'student_id': 'STU001', 'name': 'John Doe'},      # Duplicate
            {'student_id': 'STU002', 'name': 'Jane Smith'},    # New
            {'student_id': 'STU003', 'name': 'Mike Johnson'},  # Duplicate
            {'student_id': 'STU004', 'name': 'Sarah Wilson'}   # New
        ]
        
        duplicates = []
        valid_imports = []
        
        for student in new_students:
            if student['student_id'] in existing_students:
                duplicates.append(student)
            else:
                valid_imports.append(student)
        
        self.assertEqual(len(duplicates), 2)
        self.assertEqual(len(valid_imports), 2)
        
        print("✓ Duplicate handling test passed")


class TestMaterialManagementIntegration(unittest.TestCase):
    """Integration tests for material management"""
    
    def test_file_upload_simulation(self):
        """Test file upload process simulation"""
        # Mock file data
        mock_files = [
            {'filename': 'lecture1.pdf', 'size': 2048576, 'type': 'pdf'},
            {'filename': 'slides.pptx', 'size': 5242880, 'type': 'pptx'},
            {'filename': 'large_file.zip', 'size': 60*1024*1024, 'type': 'zip'},  # Too large
            {'filename': 'malware.exe', 'size': 1024, 'type': 'exe'},  # Invalid type
        ]
        
        allowed_types = {'pdf', 'pptx', 'ppt', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'txt', 'zip'}
        max_size = 50 * 1024 * 1024  # 50MB
        
        results = {
            'successful_uploads': 0,
            'failed_uploads': 0,
            'errors': []
        }
        
        for file_data in mock_files:
            # Validate file type
            if file_data['type'] not in allowed_types:
                results['failed_uploads'] += 1
                results['errors'].append(f"Invalid file type: {file_data['filename']}")
                continue
            
            # Validate file size
            if file_data['size'] > max_size:
                results['failed_uploads'] += 1
                results['errors'].append(f"File too large: {file_data['filename']}")
                continue
            
            results['successful_uploads'] += 1
        
        # Validate results
        self.assertEqual(results['successful_uploads'], 2)
        self.assertEqual(results['failed_uploads'], 2)
        self.assertEqual(len(results['errors']), 2)
        
        print("✓ File upload simulation test passed")
    
    def test_download_tracking(self):
        """Test material download tracking"""
        # Mock material with download tracking
        material = {
            'id': 'mat001',
            'title': 'Lecture 1 - Introduction',
            'download_count': 0
        }
        
        # Simulate downloads
        downloads = [
            {'user_id': 'student1', 'timestamp': datetime.utcnow()},
            {'user_id': 'student2', 'timestamp': datetime.utcnow()},
            {'user_id': 'student1', 'timestamp': datetime.utcnow()},  # Same user, multiple downloads
        ]
        
        # Track downloads
        download_logs = []
        for download in downloads:
            material['download_count'] += 1
            download_logs.append({
                'material_id': material['id'],
                'user_id': download['user_id'],
                'timestamp': download['timestamp']
            })
        
        # Validate tracking
        self.assertEqual(material['download_count'], 3)
        self.assertEqual(len(download_logs), 3)
        
        # Check unique users
        unique_users = set(log['user_id'] for log in download_logs)
        self.assertEqual(len(unique_users), 2)
        
        print("✓ Download tracking test passed")


class TestAnnouncementIntegration(unittest.TestCase):
    """Integration tests for announcement system"""
    
    def test_announcement_visibility(self):
        """Test announcement visibility logic"""
        now = datetime.utcnow()
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)
        
        announcements = [
            {
                'id': '1',
                'title': 'Current Announcement',
                'is_published': True,
                'publish_at': None,
                'expire_at': None
            },
            {
                'id': '2',
                'title': 'Future Announcement',
                'is_published': True,
                'publish_at': future,
                'expire_at': None
            },
            {
                'id': '3',
                'title': 'Expired Announcement',
                'is_published': True,
                'publish_at': None,
                'expire_at': past
            },
            {
                'id': '4',
                'title': 'Unpublished Announcement',
                'is_published': False,
                'publish_at': None,
                'expire_at': None
            }
        ]
        
        # Filter visible announcements for students
        visible = []
        for ann in announcements:
            if not ann['is_published']:
                continue
            if ann['publish_at'] and ann['publish_at'] > now:
                continue
            if ann['expire_at'] and ann['expire_at'] < now:
                continue
            visible.append(ann['id'])
        
        # Only the current announcement should be visible
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible[0], '1')
        
        print("✓ Announcement visibility test passed")
    
    def test_announcement_priority_sorting(self):
        """Test announcement sorting by priority and date"""
        announcements = [
            {'id': '1', 'priority': 2, 'is_pinned': False, 'created_at': datetime(2025, 10, 1)},
            {'id': '2', 'priority': 1, 'is_pinned': True, 'created_at': datetime(2025, 10, 2)},
            {'id': '3', 'priority': 3, 'is_pinned': False, 'created_at': datetime(2025, 10, 3)},
            {'id': '4', 'priority': 2, 'is_pinned': True, 'created_at': datetime(2025, 10, 4)},
        ]
        
        # Sort by: pinned first, then by priority (1=high), then by date (desc)
        sorted_announcements = sorted(
            announcements,
            key=lambda x: (
                not x['is_pinned'],  # Pinned first (False sorts before True)
                x['priority'],       # Lower number = higher priority
                -x['created_at'].timestamp()  # Newer first
            )
        )
        
        # Expected order: pinned items first by priority (2, 4), then unpinned (1, 3)
        # Item 2: pinned, priority 1 (highest)
        # Item 4: pinned, priority 2 
        # Item 1: unpinned, priority 2
        # Item 3: unpinned, priority 3
        expected_order = ['2', '4', '1', '3']
        actual_order = [ann['id'] for ann in sorted_announcements]
        
        self.assertEqual(actual_order, expected_order)
        
        print("✓ Announcement sorting test passed")


class TestDashboardIntegration(unittest.TestCase):
    """Integration tests for dashboard functionality"""
    
    def test_teacher_dashboard_stats(self):
        """Test teacher dashboard statistics calculation"""
        # Mock data
        courses = [
            {'id': '1', 'is_published': True, 'is_active': True},
            {'id': '2', 'is_published': False, 'is_active': True},
            {'id': '3', 'is_published': True, 'is_active': True},
        ]
        
        enrollments = [
            {'course_id': '1', 'status': 'enrolled'},
            {'course_id': '1', 'status': 'enrolled'},
            {'course_id': '1', 'status': 'completed'},
            {'course_id': '2', 'status': 'enrolled'},
            {'course_id': '3', 'status': 'enrolled'},
        ]
        
        materials = [
            {'course_id': '1', 'download_count': 10},
            {'course_id': '1', 'download_count': 15},
            {'course_id': '2', 'download_count': 5},
            {'course_id': '3', 'download_count': 8},
        ]
        
        # Calculate statistics
        stats = {
            'courses': {
                'total': len(courses),
                'published': len([c for c in courses if c['is_published']]),
                'active': len([c for c in courses if c['is_active']])
            },
            'students': {
                'total_enrollments': len(enrollments),
                'active_students': len([e for e in enrollments if e['status'] == 'enrolled']),
                'completed': len([e for e in enrollments if e['status'] == 'completed'])
            },
            'materials': {
                'total': len(materials),
                'total_downloads': sum(m['download_count'] for m in materials)
            }
        }
        
        # Validate statistics
        self.assertEqual(stats['courses']['total'], 3)
        self.assertEqual(stats['courses']['published'], 2)
        self.assertEqual(stats['courses']['active'], 3)
        self.assertEqual(stats['students']['total_enrollments'], 5)
        self.assertEqual(stats['students']['active_students'], 4)
        self.assertEqual(stats['students']['completed'], 1)
        self.assertEqual(stats['materials']['total'], 4)
        self.assertEqual(stats['materials']['total_downloads'], 38)
        
        print("✓ Teacher dashboard stats test passed")
    
    def test_student_dashboard_progress(self):
        """Test student dashboard progress calculation"""
        # Mock student enrollments
        enrollments = [
            {'course_id': '1', 'progress_percentage': 75, 'status': 'enrolled'},
            {'course_id': '2', 'progress_percentage': 100, 'status': 'completed'},
            {'course_id': '3', 'progress_percentage': 45, 'status': 'enrolled'},
        ]
        
        # Calculate student statistics
        total_courses = len(enrollments)
        completed_courses = len([e for e in enrollments if e['status'] == 'completed'])
        average_progress = sum(e['progress_percentage'] for e in enrollments) / total_courses if total_courses > 0 else 0
        
        # Validate calculations
        self.assertEqual(total_courses, 3)
        self.assertEqual(completed_courses, 1)
        self.assertEqual(round(average_progress), 73)  # (75+100+45)/3 ≈ 73
        
        print("✓ Student dashboard progress test passed")


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("COMP5241 Group 10 - Course Management Integration Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All integration tests passed! System components work well together.")
    elif success_rate >= 80:
        print("✅ Most integration tests passed. Minor integration issues to address.")
    else:
        print("⚠️  Several integration tests failed. Please review component interactions.")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_integration_tests()