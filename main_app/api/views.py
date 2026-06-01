from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
