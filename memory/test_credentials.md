# Test Credentials

Login URL: `/` (preview URL root)

| Role          | Email                       | Password         | Lands on                          |
|---------------|-----------------------------|------------------|-----------------------------------|
| Admin         | `admin@sagarmatha.edu`      | `admin123`       | `/admin/home/` (Admin Dashboard)  |
| HOD (Staff)   | `dinesh.80@hod.com`         | `dinesh.80`      | `/staff/home/` (HOD Dashboard, Nepali calendar) |
| Teacher       | `staff@staff.com`           | `staff123`       | `/staff/home/` (Teacher Dashboard) |
| Store Manager | `store@staff.com`           | `store123`       | `/staff/home/` (Store Manager Dashboard) |
| Accountant    | `accountant@staff.com`      | `accountant123`  | `/staff/home/` (Accountant Dashboard) |
| Librarian     | `librarian@staff.com`       | `librarian123`   | `/staff/home/` (Library Admin Dashboard) |
| Student       | `student@student.com`       | `student123`     | `/student/home/` (Student Dashboard) |
| Promoted student (post-bulk-promote, iteration 3) | `bulk.alpha@bulk2.test` | `NewPass#2026` | Forced first-login flow already done |

Re-seed any time with:
```
python manage.py seed_demo
```

**Note on temp passwords from `Promote to Student`**: console email backend writes the temp password to `/var/log/supervisor/backend.out.log` under a `Subject: Welcome to Sagarmatha College ...` block. Switch to real SMTP/SendGrid by setting `EMAIL_BACKEND`/`EMAIL_HOST`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` env vars.
