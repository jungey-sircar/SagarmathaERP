# Biometric Attendance Module - Documentation

## Overview

The Biometric Attendance Module is a comprehensive employee attendance tracking system based on real-time biometric entry and exit data. It automatically calculates attendance status, worked hours, late arrivals, and early departures.

## Features

### 1. **Biometric Log Tracking**
   - Records employee punch-in (entry) and punch-out (exit) times
   - Stores both time and timestamp information
   - Unique daily record per employee prevents duplicate entries
   - Automatic calculation of worked hours

### 2. **Attendance Dashboard**
   - Daily attendance log sheet with multiple filtering options
   - Real-time statistics showing:
     - Total staff count
     - Present employees
     - Absent employees
     - Late arrivals
     - Early departures
   - Sortable and searchable table display

### 3. **Attendance Status Calculation**
   The system automatically determines attendance status based on:
   
   - **Present**: Employee punched in on time (by 9:00 AM) and out before 6:00 PM
   - **Late**: Employee punched in after 9:00 AM
   - **Early Out**: Employee exited more than 1 hour before 6:00 PM
   - **Absent**: No biometric entry for the day
   - **Leave**: Manually marked by admin
   - **Half Day**: Worked less than minimum hours

### 4. **Worked Hours Calculation**
   - Automatically calculated from IN time to OUT time
   - Handles cross-midnight shifts
   - Displayed in decimal format (e.g., 8.5 hours)
   - Stored in EmployeeAttendance records

### 5. **Deviation Tracking**
   - **Late By Minutes**: Minutes late after cutoff (9:00 AM)
   - **Early Out By Minutes**: Minutes before expected exit (6:00 PM)

## Data Models

### BiometricLog Model
Stores raw biometric punch data from the biometric system.

**Fields:**
- `staff` (ForeignKey to Staff)
- `date` (DateField)
- `in_time` (TimeField) - Punch-in time
- `out_time` (TimeField) - Punch-out time
- `in_timestamp` (DateTimeField) - Full punch-in datetime
- `out_timestamp` (DateTimeField) - Full punch-out datetime
- `created_at` (DateTimeField) - Record creation time
- `updated_at` (DateTimeField) - Last update time
- `worked_hours` (property) - Auto-calculated hours worked

### EmployeeAttendance Model
Aggregated daily attendance record with status and calculations.

**Fields:**
- `staff` (ForeignKey to Staff)
- `date` (DateField)
- `status` (CharField) - One of: present, absent, late, early_out, half_day, leave
- `in_time` (TimeField)
- `out_time` (TimeField)
- `worked_hours` (DecimalField)
- `late_by_minutes` (IntegerField)
- `early_out_by_minutes` (IntegerField)
- `remarks` (TextField) - Optional notes
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

## Accessing the Module

### Navigation
1. Go to the top navigation bar
2. Click on **Modules** dropdown
3. Select **Attendance**

### Direct URL
`/modules/attendance/` - Main attendance dashboard

### URL Routes Available
- `/modules/attendance/` - Attendance Dashboard (GET for view, POST for sync)
- `/modules/attendance/mark/` - Mark individual attendance (POST)
- `/modules/attendance/sync/` - Sync all biometric data (POST)

## Using the Attendance Dashboard

### Viewing Attendance

1. **Select Date**: Choose the date for which you want to view attendance
2. **Filter by Status**: Optionally filter by attendance status (Present, Absent, Late, etc.)
3. **View Result**: Click to load the attendance data

### Features Available

- **Print**: Print the attendance report for the selected date
- **Sync Biometric Data**: Synchronize all biometric records for a specific date

### Table Columns

| Column | Description |
|--------|-------------|
| S.N | Serial number |
| Code | Employee ID |
| Name | Employee name |
| Department | Department/Course |
| Late In | Minutes late (if applicable) |
| InTime | Punch-in time |
| OutTime | Punch-out time |
| Early Out | Minutes early out (if applicable) |
| Worked Hrs | Total hours worked |
| Status | Attendance status (color-coded) |
| Remarks | Additional notes |

## Syncing Biometric Data

The sync operation processes biometric logs and generates attendance records:

1. **Process Biometric Logs**: For each employee with a biometric entry:
   - Calculate attendance status
   - Compute worked hours
   - Determine late/early out deviations
   - Create or update EmployeeAttendance record

2. **Mark Absent**: All staff without biometric entries are marked as ABSENT

3. **Confirmation**: System displays the number of records processed

### How to Sync

1. Open Attendance Dashboard
2. Click **Sync** button
3. Select the date to sync
4. Confirm the operation
5. Wait for completion message

## Configuration

### Default Working Hours
- **Cutoff Time**: 09:00 (9:00 AM)
- **Expected Exit Time**: 18:00 (6:00 PM)

To modify, edit the `calculate_attendance_status()` function in `module_views.py`:

```python
CUTOFF_TIME = datetime.strptime('09:00', '%H:%M').time()
EXPECTED_OUT_TIME = datetime.strptime('18:00', '%H:%M').time()
```

## Admin Interface

BiometricLog and EmployeeAttendance models are registered in Django Admin:

1. Go to `/admin/`
2. Navigate to **Main App** section
3. Click on **Biometric Logs** or **Employee Attendance**

### Admin Features
- List view with filters by date, department, status
- Search by employee name or email
- Date hierarchy navigation
- Detailed view with all fields
- Bulk operations support

## API Endpoints

All views support both GET and POST:

### GET Parameters
- `date`: Date to filter (format: YYYY/MM/DD)
- `status`: Filter by status (all, present, absent, late, etc.)

### Sample Requests

**View attendance for 2026/06/01:**
```
GET /modules/attendance/?date=2026/06/01&status=all
```

**View late arrivals:**
```
GET /modules/attendance/?date=2026/06/01&status=late
```

## Security & Permissions

- **Access Control**: Available to authenticated Staff users (user_type='2')
- **Data Privacy**: Only staff members can view/edit their own biometric data
- **Admin Only**: Sync operations and bulk modifications require admin privileges

## Troubleshooting

### Issue: No attendance records showing

**Solution:**
- Ensure biometric logs exist for the selected date
- Check that staff members are properly linked to the system
- Verify the database migrations were applied (`python manage.py migrate`)

### Issue: Worked hours not calculating

**Solution:**
- Ensure both `in_time` and `out_time` are recorded
- Check time format is correct (HH:MM)
- Verify the `calculate_attendance_status()` function is correct

### Issue: Status not updating

**Solution:**
- Run the sync operation to process biometric logs
- Check the remarkable field for any notes
- Manually mark attendance if needed through admin interface

## Reports & Analytics

The attendance dashboard provides:

1. **Daily Summary**: Total present, absent, late arrivals
2. **Department Breakdown**: Filtered views by department
3. **Printable Reports**: Export attendance logs to paper/PDF
4. **Date Range Views**: Navigate through dates easily

## Future Enhancements

Potential features for future versions:

1. Monthly/quarterly reports
2. Attendance trends analysis
3. Automatic email notifications for absences
4. Biometric device API integration
5. Mobile app for punch management
6. Late penalty calculations
7. Leave balance integration
8. Export to Excel/CSV
9. Dashboard analytics and charts
10. Overtime tracking

## Support & Contact

For issues or feature requests, please contact:
- System Administrator
- HR Department

---

**Version**: 1.0  
**Last Updated**: June 1, 2026  
**Module Name**: Biometric Attendance System  
**Django Version**: 3.2+  
**Database**: SQLite3 / PostgreSQL

