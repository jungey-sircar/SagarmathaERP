from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from ..models import (
    Staff,
    Subject,
    Student,
    Attendance,
    Course,
    LeaveReportStaff,
    Book,
    AttendanceReport,
    InventoryItem,
    ConsumableItem,
    FixedItem,
)
from ..holiday_service import get_nepali_holiday_dashboard_data


class HODDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # ensure user has a Staff profile
        staff = get_object_or_404(Staff, admin=request.user)
        role_text = (staff.role or "").strip().lower()
        # only HODs should use this endpoint, but return data anyway
        department_subjects = Subject.objects.filter(course=staff.course)
        department_students = Student.objects.filter(course=staff.course)
        department_staff = Staff.objects.filter(course=staff.course)

        subject_list = [s.name for s in department_subjects]
        attendance_list = [
            Attendance.objects.filter(subject=s).count() for s in department_subjects
        ]

        holiday_data = get_nepali_holiday_dashboard_data()

        class_routine = [
            ("Sun", "Routine has not been uploaded for Sunday."),
            ("Mon", "Routine has not been uploaded for Monday."),
            ("Tue", "Routine has not been uploaded for Tuesday."),
            ("Wed", "Routine has not been uploaded for Wednesday."),
            ("Thu", "Routine has not been uploaded for Thursday."),
            ("Fri", "Routine has not been uploaded for Friday."),
            ("Sat", "Routine has not been uploaded for Saturday."),
        ]

        data = {
            "page_title": "HOD Dashboard",
            "staff_name": staff.admin.get_full_name() or staff.admin.first_name,
            "role_title": staff.role,
            "role_detail": staff.role_detail
            or (staff.course.name if staff.course else ""),
            "department_name": staff.course.name if staff.course else "Unassigned",
            "total_students": department_students.count(),
            "total_staff": department_staff.count(),
            "total_subject": department_subjects.count(),
            "total_attendance": Attendance.objects.filter(
                subject__in=department_subjects
            ).count(),
            "total_leave": LeaveReportStaff.objects.filter(staff=staff).count(),
            "subject_list": subject_list,
            "attendance_list": attendance_list,
            "clearance_request_count": 0,
            "library_books_count": Book.objects.count(),
            "leave_balance_count": 0,
            "pending_leave_count": LeaveReportStaff.objects.filter(status=0).count(),
            "holiday_rows": holiday_data["holiday_rows"],
            "optional_holiday_rows": holiday_data["optional_holiday_rows"],
            "holiday_period_label": holiday_data["holiday_period_label"],
            "class_routine": class_routine,
            "announcement": "",
        }

        return Response(data)


class InventoryDashboardAPIView(APIView):
    """API endpoint for inventory dashboard statistics"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from django.db.models import Sum

        # Get all items
        all_items = InventoryItem.objects.all()
        consumable_items = ConsumableItem.objects.all()
        fixed_items = FixedItem.objects.all()

        # Calculate quantities
        total_inventory_qty = all_items.aggregate(total=Sum("quantity"))["total"] or 0
        consumable_qty = consumable_items.aggregate(total=Sum("quantity"))["total"] or 0
        fixed_qty = fixed_items.aggregate(total=Sum("quantity"))["total"] or 0

        # Low stock items
        low_stock_inventory = [i for i in all_items if i.is_low_stock]
        low_stock_consumable = [i for i in consumable_items if i.is_low_stock]

        # Calculate total costs for consumable items
        total_consumable_cost = float(sum(item.total_cost for item in consumable_items))

        # Calculate total value for fixed items
        total_fixed_value = float(sum(item.current_value for item in fixed_items))

        data = {
            "page_title": "Inventory Dashboard",
            "inventory_stats": {
                "total_items_count": all_items.count(),
                "total_items_qty": total_inventory_qty,
                "low_stock_count": len(low_stock_inventory),
                "healthy_stock_count": all_items.count() - len(low_stock_inventory),
            },
            "consumable_stats": {
                "total_count": consumable_items.count(),
                "total_qty": consumable_qty,
                "total_cost": total_consumable_cost,
                "low_stock_count": len(low_stock_consumable),
            },
            "fixed_stats": {
                "total_count": fixed_items.count(),
                "total_qty": fixed_qty,
                "total_value": total_fixed_value,
            },
            "low_stock_items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "reorder_level": item.reorder_level,
                }
                for item in low_stock_inventory[:5]  # Top 5
            ],
        }

        return Response(data)


class BiometricPunchAPIView(APIView):
    """
    Publicly accessible API endpoint for actual physical biometric devices at the college gates.
    Handles automatic 'login' (Punch-IN) and 'logout' (Punch-OUT) in real-time.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user_type = request.data.get('user_type')  # 'staff' or 'student'
        identifier = request.data.get('identifier')  # email or ID/Code

        if not user_type or not identifier:
            return Response({
                "status": "error",
                "message": "Missing user_type or identifier (email or user ID)"
            }, status=400)

        from datetime import datetime
        from ..models import Staff, Student, BiometricLog, EmployeeAttendance, StudentAttendance
        from ..module_views import calculate_attendance_status

        now = datetime.now()
        current_date = now.date()
        current_time = now.time()

        try:
            user = None
            if user_type == "staff":
                # Find staff by admin ID, email, or profile ID
                if str(identifier).isdigit():
                    user = Staff.objects.filter(admin_id=int(identifier)).first()
                if not user:
                    user = Staff.objects.filter(admin__email=identifier).first()
                if not user:
                    user = Staff.objects.filter(id=identifier).first()

                if not user:
                    return Response({"status": "error", "message": "Staff member not found"}, status=404)

                # Create or update biometric log
                log, created = BiometricLog.objects.get_or_create(
                    staff=user,
                    date=current_date,
                    defaults={
                        'in_time': current_time,
                        'in_timestamp': now,
                    }
                )

                punch_type = "IN"
                if not created:
                    log.out_time = current_time
                    log.out_timestamp = now
                    log.save()
                    punch_type = "OUT"

                # Automatically calculate daily attendance status in real-time
                status_data = calculate_attendance_status(user, current_date, log)
                EmployeeAttendance.objects.update_or_create(
                    staff=user,
                    date=current_date,
                    defaults=status_data
                )

                name = f"{user.admin.first_name} {user.admin.last_name}"
                role = "Staff"

            elif user_type == "student":
                # Find student by admin ID, email, or profile ID
                if str(identifier).isdigit():
                    user = Student.objects.filter(admin_id=int(identifier)).first()
                if not user:
                    user = Student.objects.filter(admin__email=identifier).first()
                if not user:
                    user = Student.objects.filter(id=identifier).first()

                if not user:
                    return Response({"status": "error", "message": "Student not found"}, status=404)

                # Create or update biometric log
                log, created = BiometricLog.objects.get_or_create(
                    student=user,
                    date=current_date,
                    defaults={
                        'in_time': current_time,
                        'in_timestamp': now,
                    }
                )

                punch_type = "IN"
                if not created:
                    log.out_time = current_time
                    log.out_timestamp = now
                    log.save()
                    punch_type = "OUT"

                # Automatically calculate daily attendance status in real-time
                status_data = calculate_attendance_status(user, current_date, log)
                StudentAttendance.objects.update_or_create(
                    student=user,
                    date=current_date,
                    defaults=status_data
                )

                name = f"{user.admin.first_name} {user.admin.last_name}"
                role = "Student"

            else:
                return Response({"status": "error", "message": "Invalid user_type"}, status=400)

            formatted_time = current_time.strftime('%I:%M:%S %p')
            return Response({
                "status": "success",
                "punch_type": punch_type,
                "name": name,
                "role": role,
                "time": formatted_time,
                "in_time": log.in_time.strftime('%I:%M %p') if log.in_time else '--',
                "out_time": log.out_time.strftime('%I:%M %p') if log.out_time else '--',
                "worked_hours": f"{log.worked_hours:.2f}" if log.worked_hours else '--',
                "daily_status": status_data['status'].upper()
            })

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)

