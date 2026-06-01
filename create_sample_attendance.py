#!/usr/bin/env python
"""
Sample script to generate test biometric and attendance data.
Usage: python create_sample_attendance.py
This creates sample biometric logs and attendance records for testing.
"""

from datetime import datetime, timedelta
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.utils import timezone
from main_app.models import Staff, BiometricLog, EmployeeAttendance
import random

def create_sample_attendance_data():
    """Generate sample biometric and attendance data for testing"""

    # Get all staff members
    staff_members = Staff.objects.all()[:10]  # Limit to first 10 staff

    if not staff_members:
        print("❌ No staff members found. Please create staff first.")
        return

    print(f"📊 Creating sample attendance data for {len(staff_members)} staff members...")

    # Create data for the last 5 days
    today = datetime.now().date()

    biometric_created = 0
    attendance_created = 0

    for i in range(5):
        date = today - timedelta(days=i)

        for staff in staff_members:
            # Skip some staff randomly to create absences
            if random.random() < 0.2:  # 20% absence rate
                status = 'absent'
                in_time = None
                out_time = None
                worked_hours = 0
                late_minutes = 0
                early_out_minutes = 0
            else:
                # Generate realistic punch times
                hour_in = random.randint(7, 10)  # 7-10 AM
                minute_in = random.randint(0, 59)

                hour_out = random.randint(16, 19)  # 4-7 PM
                minute_out = random.randint(0, 59)

                in_time = datetime.strptime(f"{hour_in:02d}:{minute_in:02d}", "%H:%M").time()
                out_time = datetime.strptime(f"{hour_out:02d}:{minute_out:02d}", "%H:%M").time()

                # Calculate worked hours
                start = datetime.combine(date, in_time)
                end = datetime.combine(date, out_time)
                if end < start:
                    end = end + timedelta(days=1)
                worked_hours = round((end - start).total_seconds() / 3600, 2)

                # Determine status
                cutoff_time = datetime.strptime("09:00", "%H:%M").time()
                expected_out = datetime.strptime("18:00", "%H:%M").time()

                if in_time > cutoff_time:
                    status = 'late'
                    late_delta = datetime.combine(date, in_time) - datetime.combine(date, cutoff_time)
                    late_minutes = int(late_delta.total_seconds() / 60)
                    early_out_minutes = 0
                elif out_time and out_time < expected_out:
                    status = 'early_out'
                    early_delta = datetime.combine(date, expected_out) - datetime.combine(date, out_time)
                    early_out_minutes = int(early_delta.total_seconds() / 60)
                    late_minutes = 0
                else:
                    status = 'present'
                    late_minutes = 0
                    early_out_minutes = 0

            # Create or update BiometricLog
            if in_time:
                biometric, created = BiometricLog.objects.update_or_create(
                    staff=staff,
                    date=date,
                    defaults={
                        'in_time': in_time,
                        'out_time': out_time,
                        'in_timestamp': datetime.combine(date, in_time) if in_time else None,
                        'out_timestamp': datetime.combine(date, out_time) if out_time else None,
                    }
                )
                if created:
                    biometric_created += 1

            # Create or update EmployeeAttendance
            attendance, created = EmployeeAttendance.objects.update_or_create(
                staff=staff,
                date=date,
                defaults={
                    'status': status,
                    'in_time': in_time,
                    'out_time': out_time,
                    'worked_hours': worked_hours,
                    'late_by_minutes': late_minutes if status == 'late' else 0,
                    'early_out_by_minutes': early_out_minutes if status == 'early_out' else 0,
                    'remarks': 'Sample test data',
                }
            )
            if created:
                attendance_created += 1

    print(f"✅ Successfully created sample data!")
    print(f"   📝 Biometric logs created: {biometric_created}")
    print(f"   📋 Attendance records created: {attendance_created}")
    print(f"\n💡 Tip: Visit /modules/attendance/ to view the attendance dashboard")

if __name__ == '__main__':
    create_sample_attendance_data()

