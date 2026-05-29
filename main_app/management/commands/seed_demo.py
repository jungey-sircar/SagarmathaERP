"""Seed demo data for the Sagarmatha College ERP.

Creates HOD/staff/student/admin users plus sample courses, subjects,
admissions, exams, inventory, payslips, and an announcement so that every
button in the dashboard has something meaningful to display.

Usage:
    python manage.py seed_demo
"""
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from main_app.models import (
    Admission,
    Announcement,
    Course,
    CustomUser,
    Exam,
    InventoryItem,
    Payslip,
    Session,
    Staff,
    Student,
    Subject,
    Book,
    LeaveReportStaff,
    LeaveReportStudent,
)


def _upsert_user(*, email, password, first_name, last_name, user_type, gender='M', address='Kathmandu'):
    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'user_type': user_type,
            'gender': gender,
            'address': address,
        },
    )
    if created or user.user_type != user_type:
        user.user_type = user_type
    user.first_name = first_name
    user.last_name = last_name
    user.gender = gender
    user.address = address
    user.set_password(password)
    user.save()
    return user


class Command(BaseCommand):
    help = 'Seed demo users, courses, modules data, and announcements.'

    @transaction.atomic
    def handle(self, *args, **options):
        # --- Users ---
        admin = _upsert_user(
            email='admin@sagarmatha.edu', password='admin123',
            first_name='Super', last_name='Admin', user_type='1',
        )
        hod = _upsert_user(
            email='dinesh.80@hod.com', password='dinesh.80',
            first_name='Dinesh', last_name='Shrestha', user_type='2',
        )
        teacher = _upsert_user(
            email='staff@staff.com', password='staff123',
            first_name='Aakriti', last_name='Karki', user_type='2',
        )
        student = _upsert_user(
            email='student@student.com', password='student123',
            first_name='Ravi', last_name='Thapa', user_type='3',
        )

        # --- Course (Faculty/Department) ---
        course, _ = Course.objects.get_or_create(
            name='Computer Science',
            defaults={'hod': hod},
        )
        course.hod = hod
        course.save()

        secondary_course, _ = Course.objects.get_or_create(
            name='Electronics Engineering',
        )

        # --- Staff profile updates ---
        hod_profile, _ = Staff.objects.get_or_create(admin=hod)
        hod_profile.course = course
        hod_profile.role = 'HOD'
        hod_profile.role_detail = 'Head of Department'
        hod_profile.save()

        teacher_profile, _ = Staff.objects.get_or_create(admin=teacher)
        teacher_profile.course = course
        teacher_profile.role = 'Teacher'
        teacher_profile.role_detail = 'Programming Faculty'
        teacher_profile.save()

        # --- Session ---
        today = date.today()
        session, _ = Session.objects.get_or_create(
            start_year=date(today.year, 1, 1),
            end_year=date(today.year, 12, 31),
        )

        # --- Student profile ---
        student_profile, _ = Student.objects.get_or_create(admin=student)
        student_profile.course = course
        student_profile.session = session
        student_profile.save()

        # --- Subjects ---
        subj1, _ = Subject.objects.get_or_create(
            name='Data Structures', course=course,
            defaults={'staff': teacher_profile},
        )
        subj1.staff = teacher_profile
        subj1.save()
        subj2, _ = Subject.objects.get_or_create(
            name='Operating Systems', course=course,
            defaults={'staff': teacher_profile},
        )
        subj2.staff = teacher_profile
        subj2.save()

        # --- Books ---
        Book.objects.get_or_create(
            isbn=9780131103627,
            defaults={'name': 'The C Programming Language', 'author': 'Kernighan & Ritchie', 'category': 'Programming'},
        )
        Book.objects.get_or_create(
            isbn=9780262033848,
            defaults={'name': 'Introduction to Algorithms', 'author': 'CLRS', 'category': 'Algorithms'},
        )

        # --- Admissions / Pre-Admissions ---
        if Admission.objects.count() == 0:
            samples = [
                ('Sita Rai', 'sita.rai@example.com', '9841000001', 'inquiry', 'pending'),
                ('Hari Lama', 'hari.lama@example.com', '9841000002', 'inquiry', 'pending'),
                ('Maya Gurung', 'maya.gurung@example.com', '9841000003', 'inquiry', 'approved'),
                ('Sandeep KC', 'sandeep.kc@example.com', '9841000004', 'admitted', 'approved'),
                ('Anjali Tamang', 'anjali.tamang@example.com', '9841000005', 'admitted', 'approved'),
            ]
            for name, email, phone, stage, status in samples:
                Admission.objects.create(
                    candidate_name=name, email=email, phone=phone,
                    course=course, stage=stage, status=status,
                )

        # --- Exams ---
        if Exam.objects.count() == 0:
            Exam.objects.create(
                name='Mid-Term', subject=subj1,
                exam_date=today + timedelta(days=10),
                total_marks=100, duration_minutes=180, status='scheduled',
            )
            Exam.objects.create(
                name='Final', subject=subj2,
                exam_date=today + timedelta(days=45),
                total_marks=100, duration_minutes=180, status='scheduled',
            )

        # --- Inventory ---
        if InventoryItem.objects.count() == 0:
            InventoryItem.objects.create(name='Whiteboard Marker', category='Stationery', quantity=3, unit='pcs', location='Store-A', reorder_level=10)
            InventoryItem.objects.create(name='Projector Bulb', category='Electronics', quantity=2, unit='pcs', location='Lab-1', reorder_level=3)
            InventoryItem.objects.create(name='A4 Paper Ream', category='Stationery', quantity=40, unit='reams', location='Store-A', reorder_level=10)
            InventoryItem.objects.create(name='Lab Coats', category='Apparel', quantity=25, unit='pcs', location='Lab-2', reorder_level=5)

        # --- Payslips ---
        if Payslip.objects.filter(staff=hod_profile).count() == 0:
            for m in range(max(1, today.month - 2), today.month + 1):
                Payslip.objects.update_or_create(
                    staff=hod_profile, month=m, year=today.year,
                    defaults={
                        'basic_salary': Decimal('60000'),
                        'allowances': Decimal('8000'),
                        'deductions': Decimal('3000'),
                        'paid': True,
                    },
                )

        # --- Sample leave requests ---
        if LeaveReportStaff.objects.count() == 0:
            LeaveReportStaff.objects.create(
                staff=teacher_profile, date=str(today + timedelta(days=3)),
                message='Personal work in Pokhara', status=0,
            )
            LeaveReportStaff.objects.create(
                staff=teacher_profile, date=str(today - timedelta(days=10)),
                message='Family function', status=1,
            )
        if LeaveReportStudent.objects.count() == 0:
            LeaveReportStudent.objects.create(
                student=student_profile, date=str(today + timedelta(days=2)),
                message='Medical appointment', status=0,
            )

        # --- Announcement ---
        if Announcement.objects.count() == 0:
            Announcement.objects.create(
                title='Welcome to Sagarmatha ERP',
                body='All modules are now live. Use the Modules dropdown to navigate Pre Admissions, Admissions, Examination, HR, Inventory and more.',
                audience='all',
            )

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
        self.stdout.write('  Admin    : admin@sagarmatha.edu / admin123')
        self.stdout.write('  HOD      : dinesh.80@hod.com / dinesh.80')
        self.stdout.write('  Staff    : staff@staff.com / staff123')
        self.stdout.write('  Student  : student@student.com / student123')
