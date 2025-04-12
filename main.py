import unittest
import os
import json
import tempfile
from datetime import datetime, timedelta


class TimecardAppTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Initialize the database with a modified schema that doesn't include sample data
        with app.app_context():
            db = get_db()
            with open('schema_test.sql', 'r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            
            # Add a test employee manually with a unique email for each test run
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            db.execute(
                'INSERT INTO employees (name, email, created_at) VALUES (?, ?, ?)',
                ('Test User', f'test.user.{timestamp}@example.com', datetime.now().isoformat())
            )
            db.commit()
    
    def tearDown(self):
        # Close and remove the temporary database
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def test_index_page(self):
        """Test that the index page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Employee Timecard System', response.data)
    
    def test_get_employees(self):
        """Test retrieving the list of employees"""
        response = self.client.get('/api/employees')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)  # Should have our test employee
        self.assertEqual(data[0]['name'], 'Test User')
        self.assertTrue('@example.com' in data[0]['email'])
    
    def test_add_employee(self):
        """Test adding a new employee"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post(
            '/api/employees',
            data=json.dumps({
                'name': 'New Employee',
                'email': f'new.employee.{timestamp}@example.com'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify the employee was added
        response = self.client.get('/api/employees')
        employees = json.loads(response.data)
        self.assertEqual(len(employees), 2)  # Now should have 2 employees
        found = False
        for employee in employees:
            if 'new.employee' in employee['email']:
                found = True
                break
        self.assertTrue(found)
    
    def test_timecard_workflow(self):
        """Test the complete timecard workflow"""
        # Get the test employee ID
        response = self.client.get('/api/employees')
        employees = json.loads(response.data)
        employee_id = employees[0]['id']
        
        # 1. Clock in
        response = self.client.post(
            '/api/time/clock-in',
            data=json.dumps({'employee_id': employee_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 2. Check status (should be working)
        response = self.client.get(f'/api/time/current-status/{employee_id}')
        status = json.loads(response.data)
        self.assertEqual(status['status'], 'working')
        
        # 3. Start break
        response = self.client.post(
            '/api/time/start-break',
            data=json.dumps({'employee_id': employee_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 4. Check status (should be on break)
        response = self.client.get(f'/api/time/current-status/{employee_id}')
        status = json.loads(response.data)
        self.assertEqual(status['status'], 'break')
        
        # 5. End break
        response = self.client.post(
            '/api/time/end-break',
            data=json.dumps({'employee_id': employee_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 6. Check status (should be working again)
        response = self.client.get(f'/api/time/current-status/{employee_id}')
        status = json.loads(response.data)
        self.assertEqual(status['status'], 'working')
        
        # 7. Clock out
        response = self.client.post(
            '/api/time/clock-out',
            data=json.dumps({'employee_id': employee_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('hours_worked', data)
        
        # 8. Check status (should be off)
        response = self.client.get(f'/api/time/current-status/{employee_id}')
        status = json.loads(response.data)
        self.assertEqual(status['status'], 'off')
    
    def test_duplicate_clock_in(self):
        """Test that an employee cannot clock in twice"""
        # Get the test employee ID
        response = self.client.get('/api/employees')
        employees = json.loads(response.data)
        employee_id = employees[0]['id']
        
        # First clock in should succeed
        response = self.client.post(
            '/api/time/clock-in',
            data=json.dumps({'employee_id': employee_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Second clock in should fail
        response = self.client.post(
            '/api/time/clock-in',
            data=json.dumps({'employee_id': employee_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_break_without_clock_in(self):
        """Test that an employee cannot start a break without clocking in"""
        # Add another test employee
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post(
            '/api/employees',
            data=json.dumps({
                'name': 'Another Test User',
                'email': f'another.test.{timestamp}@example.com'
            }),
            content_type='application/json'
        )
        
        # Get the new employee ID
        response = self.client.get('/api/employees')
        employees = json.loads(response.data)
        employee_id = None
        for employee in employees:
            if 'another.test' in employee['email']:
                employee_id = employee['id']
                break
        
        # Attempt to start break without clocking in
        response = self.client.post(
            '/api/time/start-break',
            data=json.dumps({'employee_id': employee_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == "__main__":
    pass
    
    
