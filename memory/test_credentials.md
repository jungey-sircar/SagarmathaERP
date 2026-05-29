# Test Credentials

Login URL: `/` (preview URL root)

| Role         | Email                    | Password    | Notes                                  |
|--------------|--------------------------|-------------|----------------------------------------|
| Admin        | `admin@sagarmatha.edu`   | `admin123`  | user_type=1, redirects to `/admin/home/` |
| HOD (Staff)  | `dinesh.80@hod.com`      | `dinesh.80` | user_type=2, role=HOD, dashboard `/staff/home/` |
| Staff (Teacher) | `staff@staff.com`     | `staff123`  | user_type=2, role=Teacher              |
| Student      | `student@student.com`    | `student123`| user_type=3, dashboard `/student/home/` |

Re-seed any time with:
```
python manage.py seed_demo
```
