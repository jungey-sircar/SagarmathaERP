# Quick Start Guide - Biometric Attendance Module

## 🚀 Quick Setup (5 minutes)

### Step 1: Verify Installation ✅
```bash
cd "E:\students data\SERP\SagarmathaERP"
python manage.py check  # Should show: System check identified no issues (0 silenced).
```

### Step 2: Create Sample Data 📊
```bash
python create_sample_attendance.py
```
This will generate 5 days of sample attendance records for your testing.

### Step 3: Start the Server 🖥️
```bash
python manage.py runserver
```

### Step 4: Access the Dashboard 🎯
1. Open: `http://localhost:8000/`
2. Register/Login as a Staff user
3. Click **Modules** → **Attendance**

---

## 📖 Common Tasks

### View Today's Attendance
1. Go to Attendance module
2. Date will default to today
3. Click "View Result"

### Filter by Status
1. In Attendance dashboard
2. Select status from dropdown (Present, Absent, Late, etc.)
3. Click "View Result"

### Sync Biometric Data
1. Click **Sync** button
2. Select date
3. Confirm operation
4. Check success message

### Print Attendance Report
1. View the attendance data
2. Click **Print** button
3. Use browser print dialog (Ctrl+P or Cmd+P)
4. Save as PDF or print

### Manage in Admin
1. Go to `/admin/`
2. Click **Biometric Logs** or **Employee Attendance**
3. Add/edit/delete records as needed

---

## 🔑 Key Points

| Feature | Shortcut | How-To |
|---------|----------|--------|
| View Attendance | Dashboard | Go to Modules → Attendance |
| Filter Date | Date Field | Select date and click "View Result" |
| Filter Status | Status Dropdown | Choose status and click "View Result" |
| Sync Data | Sync Button | Click sync, select date, confirm |
| Print Report | Print Button | Click print, use browser print dialog |
| Manual Mark | Admin Panel | Go to /admin/, select Employee Attendance |

---

## ⚙️ Configuration

### Change Working Hours
Edit `/main_app/module_views.py`, line ~825:
```python
CUTOFF_TIME = datetime.strptime('09:00', '%H:%M').time()  # Change 09:00
EXPECTED_OUT_TIME = datetime.strptime('18:00', '%H:%M').time()  # Change 18:00
```

### Enable for Other User Types
Edit `/main_app/templates/main_app/base.html`, line ~90:
Change from:
```django
{% if user.is_authenticated and user.user_type == '2' %}
```
To include other user types (1=HOD, 3=Student, etc.)

---

## 📱 What You See

### Dashboard Statistics
```
┌─────────────┬─────────┬────────┬──────────┐
│ Total Staff │ Present │ Absent │   Other  │
│     25      │   20    │   3    │    2     │
└─────────────┴─────────┴────────┴──────────┘
```

### Attendance Table
```
S.N | Code | Name | Department | InTime | OutTime | Status
 1  | 101  | John | Admin      | 09:00  | 18:00   | Present  
 2  | 102  | Jane | Admin      | 09:45  | 17:30   | Late/EarlyOut
 3  | 103  | Bob  | IT         |   --   |   --    | Absent
```

---

## 🎓 Database Models

### BiometricLog
Stores raw punch times from biometric system
- `staff` - Which employee
- `date` - Which day
- `in_time` - Entry time
- `out_time` - Exit time
- `worked_hours` - Auto-calculated

### EmployeeAttendance  
Processed daily attendance record
- `staff` - Which employee
- `date` - Which day
- `status` - Present/Absent/Late/Early/Leave/Half
- `late_by_minutes` - How many minutes late
- `worked_hours` - Total hours worked

---

## 🔗 Important URLs

| URL | Purpose | Access |
|-----|---------|--------|
| `/modules/attendance/` | Main Dashboard | Staff+ |
| `/admin/` | Admin Panel | Admin Only |
| `/admin/main_app/biometriclog/` | Manage Biometric Logs | Admin |
| `/admin/main_app/employeeattendance/` | Manage Attendance | Admin |

---

## 🆘 Troubleshooting

### No attendance records showing?
- [ ] Check date is correct
- [ ] Verify staff members exist
- [ ] Run `create_sample_attendance.py` for test data

### Worked hours showing --?
- [ ] Ensure both IN and OUT times exist
- [ ] Check time format is HH:MM

### Can't see modules menu?
- [ ] Make sure you're logged in as Staff (user_type='2')
- [ ] Verify user is active in admin

### Sync not working?
- [ ] Check database migrations applied
- [ ] Verify biometric logs exist for selected date
- [ ] Check error message in logs

---

## 📚 Full Documentation

For detailed information, see:
- **ATTENDANCE_MODULE_README.md** - Complete feature guide
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **Code comments** in module_views.py

---

## 💡 Tips & Tricks

1. **Batch Operations**: Use admin to bulk update multiple records
2. **Date Navigation**: Admin has date hierarchy for faster browsing
3. **Search**: Use admin search to find specific employees
4. **Filters**: Admin has multiple filter options (date, status, department)
5. **Printing**: Use browser's "Save as PDF" when printing reports

---

## 🎯 Next Steps

1. ✅ Download/review the code
2. ✅ Run `create_sample_attendance.py`
3. ✅ Test the dashboard
4. ✅ Set up biometric data import
5. ✅ Configure working hours
6. ✅ Deploy to production

---

## 🤝 Support

- **Admin Issues?** Check `/admin/main_app/`
- **Data Issues?** Review ATTENDANCE_MODULE_README.md
- **Code Questions?** Check comments in module_views.py
- **Feature Requests?** See Future Enhancements section

---

**Last Updated**: June 1, 2026  
**Version**: 1.0  
**Status**: ✅ Ready to Use

