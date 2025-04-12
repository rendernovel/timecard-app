import os
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# Configuration
EXPORT_DIR = 'exports'
RECIPIENT_EMAIL = 'admin@example.com'  # This will be replaced with the actual recipient email

# Ensure export directory exists
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

def generate_weekly_report(app, query_db):
    """Generate weekly timecard report for all employees"""
    # Get the date range for the past week (Monday to Sunday)
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Format dates for filename and query
    start_date_str = start_of_week.isoformat()
    end_date_str = end_of_week.isoformat()
    filename = f"timecard_report_{start_date_str}_to_{end_date_str}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    # Query data for the report
    with app.app_context():
        # Get all time entries for the week
        time_entries = query_db(
            '''
            SELECT 
                e.name as employee_name,
                e.email as employee_email,
                te.date,
                te.clock_in,
                te.clock_out,
                te.total_hours,
                (SELECT SUM(duration) FROM break_entries WHERE time_entry_id = te.id) as break_hours
            FROM time_entries te
            JOIN employees e ON te.employee_id = e.id
            WHERE te.date BETWEEN ? AND ?
            ORDER BY e.name, te.date
            ''',
            (start_date_str, end_date_str)
        )
        
        # Write data to CSV file
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['Employee Name', 'Email', 'Date', 'Clock In', 'Clock Out', 
                         'Break Hours', 'Total Hours', 'Status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for entry in time_entries:
                # Format times for readability
                clock_in_time = datetime.fromisoformat(entry['clock_in']).strftime('%H:%M:%S') if entry['clock_in'] else 'N/A'
                clock_out_time = datetime.fromisoformat(entry['clock_out']).strftime('%H:%M:%S') if entry['clock_out'] else 'N/A'
                
                # Calculate status
                status = 'Completed' if entry['clock_out'] else 'Incomplete'
                
                # Format break hours
                break_hours = round(entry['break_hours'] * 100) / 100 if entry['break_hours'] else 0
                
                # Format total hours
                total_hours = round(entry['total_hours'] * 100) / 100 if entry['total_hours'] else 0
                
                writer.writerow({
                    'Employee Name': entry['employee_name'],
                    'Email': entry['employee_email'],
                    'Date': entry['date'],
                    'Clock In': clock_in_time,
                    'Clock Out': clock_out_time,
                    'Break Hours': break_hours,
                    'Total Hours': total_hours,
                    'Status': status
                })
    
    # Log the export
    with app.app_context():
        query_db(
            'INSERT INTO export_logs (export_date, status, file_path, recipient_email) VALUES (?, ?, ?, ?)',
            (datetime.now().isoformat(), 'generated', filepath, RECIPIENT_EMAIL),
            one=True
        )
    
    return filepath

def send_export_email(filepath, app, query_db):
    """Send the export file via email"""
    # This is a placeholder for the actual email sending functionality
    # In a production environment, you would configure this with your SMTP server details
    
    try:
        # Log the email attempt
        with app.app_context():
            query_db(
                'UPDATE export_logs SET status = ? WHERE file_path = ?',
                ('sent', filepath),
                one=True
            )
        
        print(f"Export email would be sent to {RECIPIENT_EMAIL} with file {filepath}")
        return True
    except Exception as e:
        # Log the error
        with app.app_context():
            query_db(
                'UPDATE export_logs SET status = ? WHERE file_path = ?',
                (f'error: {str(e)}', filepath),
                one=True
            )
        print(f"Error sending export email: {str(e)}")
        return False

def scheduled_export(app, query_db):
    """Function to be called by the scheduler every Sunday at 6 PM"""
    print(f"Running scheduled export at {datetime.now()}")
    filepath = generate_weekly_report(app, query_db)
    send_export_email(filepath, app, query_db)

def init_scheduler(app, query_db):
    """Initialize the scheduler for automated exports"""
    scheduler = BackgroundScheduler()
    
    # Schedule the export job for every Sunday at 6 PM
    scheduler.add_job(lambda: scheduled_export(app, query_db), 'cron', day_of_week='sun', hour=18, minute=0)
    
    # Start the scheduler
    scheduler.start()
    print("Scheduler started. Export will run every Sunday at 6 PM.")
    
    return scheduler

# Manual export function that can be called from the API
def trigger_manual_export(app, query_db):
    """Manually trigger an export"""
    filepath = generate_weekly_report(app, query_db)
    success = send_export_email(filepath, app, query_db)
    return {
        'success': success,
        'filepath': filepath,
        'timestamp': datetime.now().isoformat()
    }
