"""Views for the new HOD/Staff modules surfaced in the Modules dropdown:
Pre Admissions, Admissions, Examination, Human Resource, Inventory.
Library and Attendance reuse existing views.
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import (
    Admission,
    Announcement,
    Course,
    CustomUser,
    Exam,
    InventoryItem,
    ConsumableItem,
    FixedItem,
    LeaveReportStaff,
    LeaveReportStudent,
    Payslip,
    Session,
    Staff,
    Student,
    Subject,
    EmployeeIdentificationDetails,
    EmployeeEducationDetails,
    EmployeePromotionHistory,
    EmployeeTransferHistory,
    BiometricLog,
    EmployeeAttendance,
    Book,
    BookLoan,
    ClearanceRequest,
)

# ---------- Pre Admissions / Admissions ----------


def _save_admission_from_post(request, admission=None):
    candidate_name = (request.POST.get("candidate_name") or "").strip()
    email = (request.POST.get("email") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    course_id = request.POST.get("course")
    stage = request.POST.get("stage") or "inquiry"
    status = request.POST.get("status") or "pending"
    notes = request.POST.get("notes") or ""

    if not candidate_name or not email:
        messages.error(request, "Candidate name and email are required.")
        return None

    course = Course.objects.filter(id=course_id).first() if course_id else None
    if admission is None:
        admission = Admission()
    admission.candidate_name = candidate_name
    admission.email = email
    admission.phone = phone
    admission.course = course
    admission.stage = stage
    admission.status = status
    admission.notes = notes
    admission.save()
    return admission


@login_required
def pre_admissions(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            Admission.objects.filter(id=request.POST.get("id")).delete()
            messages.success(request, "Inquiry removed.")
        elif action == "promote":
            admission = get_object_or_404(Admission, id=request.POST.get("id"))
            admission.stage = "admitted"
            admission.status = "approved"
            admission.save()
            messages.success(
                request, f"{admission.candidate_name} promoted to Admissions."
            )
        else:
            forced_stage = request.POST.copy()
            forced_stage["stage"] = "inquiry"
            request.POST = forced_stage
            if _save_admission_from_post(request):
                messages.success(request, "Inquiry added.")
        return redirect(reverse("pre_admissions"))

    inquiries = Admission.objects.filter(stage="inquiry")

    # Get admission years and group by year
    admission_years = Admission.objects.exclude(applied_at__isnull=True).dates(
        "applied_at", "year", order="DESC"
    )
    admission_stats = []
    for date in admission_years:
        year = date.year
        count = Admission.objects.filter(applied_at__year=year).count()
        admission_stats.append(
            {
                "year": year,
                "count": count,
            }
        )

    # IOE Results Log stats
    ioe_results_log_count = (
        Admission.objects.exclude(applied_at__isnull=True)
        .values("applied_at__year")
        .distinct()
        .count()
    )

    context = {
        "page_title": "Pre Admissions",
        "inquiries": inquiries,
        "courses": Course.objects.all(),
        "pending_count": inquiries.filter(status="pending").count(),
        "approved_count": inquiries.filter(status="approved").count(),
        "rejected_count": inquiries.filter(status="rejected").count(),
        "admission_stats": admission_stats,
        "ioe_results_log_count": ioe_results_log_count,
    }
    return render(request, "modules/pre_admissions.html", context)


@login_required
def entrance_results_by_year(request, year):
    """Display entrance results (admissions) for a specific year."""
    try:
        year = int(year)
        admissions = Admission.objects.filter(applied_at__year=year).order_by(
            "-applied_at"
        )
    except (ValueError, TypeError):
        admissions = Admission.objects.none()

    context = {
        "page_title": f"Entrance Result - {year}",
        "year": year,
        "admissions": admissions,
        "total_count": admissions.count(),
        "approved_count": admissions.filter(status="approved").count(),
        "pending_count": admissions.filter(status="pending").count(),
        "rejected_count": admissions.filter(status="rejected").count(),
        "admitted_count": admissions.filter(stage="admitted").count(),
        "ready_to_promote_count": admissions.exclude(stage="admitted").count(),
        "current_path": request.path,
    }
    return render(request, "modules/entrance_results.html", context)


@login_required
def ioe_results_log(request):
    """Display IOE results log (all admissions)."""
    admissions = Admission.objects.exclude(applied_at__isnull=True).order_by(
        "-applied_at"
    )

    year_filter = request.GET.get("year")
    if year_filter:
        try:
            year_filter = int(year_filter)
            admissions = admissions.filter(applied_at__year=year_filter)
        except (ValueError, TypeError):
            year_filter = None

    # Get list of distinct years
    admission_years = list(
        Admission.objects.exclude(applied_at__isnull=True)
        .values_list("applied_at__year", flat=True)
        .distinct()
        .order_by("-applied_at__year")
    )

    context = {
        "page_title": "IOE Results Log",
        "admissions": admissions,
        "admission_years": admission_years,
        "selected_year": year_filter,
        "total_count": admissions.count(),
        "approved_count": admissions.filter(status="approved").count(),
        "pending_count": admissions.filter(status="pending").count(),
        "rejected_count": admissions.filter(status="rejected").count(),
    }
    return render(request, "modules/ioe_results_log.html", context)


@login_required
def admissions(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            Admission.objects.filter(id=request.POST.get("id")).delete()
            messages.success(request, "Admission removed.")
        else:
            forced_stage = request.POST.copy()
            forced_stage["stage"] = "admitted"
            request.POST = forced_stage
            if _save_admission_from_post(request):
                messages.success(request, "Admission saved.")
        return redirect(reverse("admissions"))

    admitted = Admission.objects.filter(stage="admitted")

    # Build dashboard aggregates for students by batch (session) and program (course)
    students_qs = Student.objects.select_related("admin", "course", "session").all()
    total_students = students_qs.count()

    # counts per course
    course_counts = {}
    for c in Course.objects.all():
        course_counts[c.id] = {"name": c.name, "count": 0}
    for s in students_qs:
        if s.course:
            entry = course_counts.setdefault(s.course.id, {"name": s.course.name, "count": 0})
            entry["count"] += 1

    # counts per (session year, course)
    batch_program = {}
    for s in students_qs:
        session = s.session
        year_label = None
        if session:
            try:
                year_label = session.end_year.year
            except Exception:
                try:
                    year_label = session.start_year.year
                except Exception:
                    year_label = str(session)
        else:
            year_label = "Unknown"
        course_name = s.course.name if s.course else "Unknown"
        key = (year_label, course_name, s.course.id if s.course else 0)
        batch_program[key] = batch_program.get(key, 0) + 1

    # Build rows sorted by year desc then course
    rows = []
    for (year_label, course_name, course_id), cnt in batch_program.items():
        rows.append({"year": year_label, "course": course_name, "count": cnt, "course_id": course_id})
    rows.sort(key=lambda r: (str(r["year"]), r["course"]), reverse=True)

    # Get current (latest) batch year
    latest_year = None
    latest_year_counts = {}
    if rows:
        latest_year = rows[0]["year"]
        for row in rows:
            if row["year"] == latest_year:
                latest_year_counts[row["course"]] = row["count"]

    # Build line chart data: year -> [course counts]
    # Group rows by year and collect data for all courses
    year_course_data = {}
    all_courses_in_data = set()
    for row in rows:
        year = row["year"]
        course = row["course"]
        count = row["count"]
        all_courses_in_data.add(course)
        if year not in year_course_data:
            year_course_data[year] = {}
        year_course_data[year][course] = count

    # Sort years ascending for line chart
    sorted_years = sorted(year_course_data.keys(), key=lambda x: str(x))

    # Build line chart series for each course
    chart_labels = [str(y) for y in sorted_years]
    chart_datasets = []
    colors = [
        "rgba(255, 99, 132, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(75, 192, 192, 1)",
        "rgba(255, 159, 64, 1)",
        "rgba(153, 102, 255, 1)",
    ]
    for idx, course_name in enumerate(sorted(all_courses_in_data)):
        data_points = [year_course_data.get(y, {}).get(course_name, 0) for y in sorted_years]
        chart_datasets.append({
            "label": course_name,
            "data": data_points,
            "borderColor": colors[idx % len(colors)],
            "backgroundColor": colors[idx % len(colors)].replace("1)", "0.1)"),
            "tension": 0.3,
        })

    # Donut chart for latest batch
    donut_labels = list(latest_year_counts.keys()) if latest_year_counts else []
    donut_data = list(latest_year_counts.values()) if latest_year_counts else []
    donut_colors = colors[:len(donut_labels)]

    context = {
        "page_title": "Admissions",
        "admissions": admitted,
        "students": students_qs,
        "courses": Course.objects.all(),
        "total_admissions": admitted.count(),
        "approved_count": admitted.filter(status="approved").count(),
        "pending_count": admitted.filter(status="pending").count(),
        "total_students": total_students,
        "course_counts": list(course_counts.values()),
        "batch_program_rows": rows,
        "latest_year": latest_year,
        "latest_year_total": sum(latest_year_counts.values()) if latest_year_counts else 0,
        "latest_year_programs": len(latest_year_counts),
        # Chart data
        "chart_labels": chart_labels,
        "chart_datasets": chart_datasets,
        "donut_labels": donut_labels,
        "donut_data": donut_data,
        "donut_colors": donut_colors,
    }
    return render(request, "modules/admissions_dashboard.html", context)


@login_required
def admissions_list(request, year, course_id):
    """List students for a given batch year and course id."""
    # resolve session objects whose end_year or start_year year matches requested year
    sessions = Session.objects.filter(
        Q(end_year__year=year) | Q(start_year__year=year)
    )
    students = Student.objects.filter(course_id=course_id, session__in=sessions).select_related(
        "admin", "course", "session"
    )
    course = Course.objects.filter(id=course_id).first()
    context = {
        "page_title": f"Students: {year} / {course.name if course else 'Course'}",
        "students": students,
        "year": year,
        "course": course,
    }
    return render(request, "modules/admissions_list.html", context)


# ---------- Examination ----------


def examination(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            Exam.objects.filter(id=request.POST.get("id")).delete()
            messages.success(request, "Exam removed.")
        else:
            name = (request.POST.get("name") or "").strip()
            subject_id = request.POST.get("subject")
            exam_date = request.POST.get("exam_date")
            total_marks = request.POST.get("total_marks") or 100
            duration_minutes = request.POST.get("duration_minutes") or 180
            status = request.POST.get("status") or "scheduled"
            subject = Subject.objects.filter(id=subject_id).first()
            if not name or not subject or not exam_date:
                messages.error(request, "Name, subject, and exam date are required.")
            else:
                Exam.objects.create(
                    name=name,
                    subject=subject,
                    exam_date=exam_date,
                    total_marks=int(total_marks),
                    duration_minutes=int(duration_minutes),
                    status=status,
                )
                messages.success(request, "Exam scheduled.")
        return redirect(reverse("examination"))

    exams = Exam.objects.select_related("subject", "subject__course").all()
    context = {
        "page_title": "Examination",
        "exams": exams,
        "subjects": Subject.objects.select_related("course").all(),
        "scheduled_count": exams.filter(status="scheduled").count(),
        "ongoing_count": exams.filter(status="ongoing").count(),
        "completed_count": exams.filter(status="completed").count(),
    }
    return render(request, "modules/examination.html", context)


# ---------- Human Resource ----------


@login_required
def human_resource(request):
    staff_qs = (
        Staff.objects.select_related("admin", "course")
        .all()
        .order_by("admin__first_name")
    )
    staff_rows = []
    for staff in staff_qs:
        staff_rows.append(
            {
                "id": staff.id,
                "name": f"{staff.admin.first_name} {staff.admin.last_name}".strip()
                or staff.admin.email,
                "email": staff.admin.email,
                "role": staff.role,
                "role_detail": staff.role_detail,
                "department": staff.department or staff.course.name if staff.course else "-",
                "date_of_join": staff.date_of_join,
                "permanent_on": staff.permanent_on,
                "last_promotion_date": staff.last_promotion_date,
                "contact_number": staff.contact_number,
            }
        )

    pending_staff_leaves = LeaveReportStaff.objects.filter(status=0).count()
    approved_staff_leaves = LeaveReportStaff.objects.filter(status=1).count()
    pending_student_leaves = LeaveReportStudent.objects.filter(status=0).count()

    context = {
        "page_title": "Human Resource",
        "staff_rows": staff_rows,
        "total_staff": len(staff_rows),
        "total_students": Student.objects.count(),
        "total_departments": Course.objects.count(),
        "pending_staff_leaves": pending_staff_leaves,
        "approved_staff_leaves": approved_staff_leaves,
        "pending_student_leaves": pending_student_leaves,
    }
    return render(request, "modules/human_resource.html", context)


@login_required
def employee_details(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)

    extra_details = staff.hr_extra_details or {}

    if request.method == "POST":
        tab = request.POST.get("tab", "personal")

        try:
            if tab == "personal":
                staff.division = request.POST.get("division", "").strip()
                staff.department = request.POST.get("department", "").strip()
                staff.role = request.POST.get("role", "").strip()
                staff.role_detail = request.POST.get("role_detail", "").strip()
                staff.employment_type = request.POST.get("employment_type", "full_time")
                staff.duty_shift = request.POST.get("duty_shift", "").strip()
                staff.contact_number = request.POST.get("contact_number", "").strip()

                if request.POST.get("date_of_join"):
                    staff.date_of_join = request.POST.get("date_of_join")
                if request.POST.get("permanent_on"):
                    staff.permanent_on = request.POST.get("permanent_on")
                if request.POST.get("last_promotion_date"):
                    staff.last_promotion_date = request.POST.get("last_promotion_date")

                staff.admin.first_name = request.POST.get("first_name", "").strip()
                staff.admin.last_name = request.POST.get("last_name", "").strip()
                staff.admin.address = request.POST.get("address", "").strip()
                staff.admin.gender = request.POST.get("gender", "M")

                if request.FILES.get("profile_pic"):
                    staff.admin.profile_pic = request.FILES["profile_pic"]

                staff.admin.save()
                staff.save()
                messages.success(request, "Personal details updated successfully!")

            elif tab == "identification":
                id_details, _ = EmployeeIdentificationDetails.objects.get_or_create(staff=staff)
                id_details.bank_name = request.POST.get("bank_name", "").strip()
                id_details.account_number = request.POST.get("account_number", "").strip()
                id_details.citizenship_number = request.POST.get("citizenship_number", "").strip()
                if request.POST.get("citizenship_issue_date"):
                    id_details.citizenship_issue_date = request.POST.get("citizenship_issue_date")
                id_details.citizenship_issue_place = request.POST.get("citizenship_issue_place", "").strip()
                id_details.pf_number = request.POST.get("pf_number", "").strip()
                id_details.cit_number = request.POST.get("cit_number", "").strip()
                id_details.pan_number = request.POST.get("pan_number", "").strip()
                id_details.blood_group = request.POST.get("blood_group", "").strip()
                id_details.save()
                messages.success(request, "Identification details updated successfully!")

            elif tab == "education":
                education_levels = request.POST.getlist("education_level[]")
                education_qualifications = request.POST.getlist("education_qualification[]")
                education_institutions = request.POST.getlist("education_institution[]")
                education_years = request.POST.getlist("education_year[]")
                education_percentages = request.POST.getlist("education_percentage[]")
                education_specializations = request.POST.getlist("education_specialization[]")

                staff.education_details.all().delete()
                for i, level in enumerate(education_levels):
                    if not level:
                        continue
                    EmployeeEducationDetails.objects.create(
                        staff=staff,
                        level=level,
                        title_of_qualification=education_qualifications[i] if i < len(education_qualifications) else "",
                        institution=education_institutions[i] if i < len(education_institutions) else "",
                        passed_year=int(education_years[i]) if i < len(education_years) and education_years[i] else None,
                        percentage=education_percentages[i] if i < len(education_percentages) and education_percentages[i] else None,
                        specialization=education_specializations[i] if i < len(education_specializations) else "",
                    )
                messages.success(request, "Education details updated successfully!")

            elif tab == "promotion":
                promo_dates = request.POST.getlist("promo_date[]")
                promo_types = request.POST.getlist("promo_type[]")
                promo_from_levels = request.POST.getlist("promo_from_level[]")
                promo_to_levels = request.POST.getlist("promo_to_level[]")
                promo_unpaid_leaves = request.POST.getlist("promo_unpaid_leaves[]")
                promo_remarks = request.POST.getlist("promo_remarks[]")

                staff.promotion_history.all().delete()
                for i, promo_date in enumerate(promo_dates):
                    if not promo_date:
                        continue
                    EmployeePromotionHistory.objects.create(
                        staff=staff,
                        date=promo_date,
                        promotion_type=promo_types[i] if i < len(promo_types) else "internal",
                        from_level=promo_from_levels[i] if i < len(promo_from_levels) else "",
                        to_level=promo_to_levels[i] if i < len(promo_to_levels) else "",
                        unpaid_leaves=int(promo_unpaid_leaves[i]) if i < len(promo_unpaid_leaves) and promo_unpaid_leaves[i] else 0,
                        remarks=promo_remarks[i] if i < len(promo_remarks) else "",
                    )
                messages.success(request, "Promotion history updated successfully!")

            elif tab == "transfer":
                transfer_dates = request.POST.getlist("transfer_date[]")
                transfer_types = request.POST.getlist("transfer_type[]")
                transfer_from_depts = request.POST.getlist("transfer_from_department[]")
                transfer_to_depts = request.POST.getlist("transfer_to_department[]")
                transfer_remarks = request.POST.getlist("transfer_remarks[]")
                rows = []
                for i, transfer_date in enumerate(transfer_dates):
                    if transfer_date:
                        rows.append({
                            "date": transfer_date,
                            "type": transfer_types[i] if i < len(transfer_types) else "Internal",
                            "from_department": transfer_from_depts[i] if i < len(transfer_from_depts) else "",
                            "to_department": transfer_to_depts[i] if i < len(transfer_to_depts) else "",
                            "remarks": transfer_remarks[i] if i < len(transfer_remarks) else "",
                        })
                extra_details["transfer_history"] = rows
                staff.hr_extra_details = extra_details
                staff.save(update_fields=["hr_extra_details"])
                messages.success(request, "Transfer history updated successfully!")

            elif tab == "work":
                work_orgs = request.POST.getlist("work_organization[]")
                work_designations = request.POST.getlist("work_designation[]")
                work_from_dates = request.POST.getlist("work_from_date[]")
                work_to_dates = request.POST.getlist("work_to_date[]")
                work_remarks = request.POST.getlist("work_remarks[]")
                rows = []
                for i, org in enumerate(work_orgs):
                    if org:
                        rows.append({
                            "organization": org,
                            "designation": work_designations[i] if i < len(work_designations) else "",
                            "from_date": work_from_dates[i] if i < len(work_from_dates) else "",
                            "to_date": work_to_dates[i] if i < len(work_to_dates) else "",
                            "remarks": work_remarks[i] if i < len(work_remarks) else "",
                        })
                extra_details["work_experiences"] = rows
                staff.hr_extra_details = extra_details
                staff.save(update_fields=["hr_extra_details"])
                messages.success(request, "Work experiences updated successfully!")

            elif tab == "documents":
                doc_names = request.POST.getlist("document_name[]")
                doc_numbers = request.POST.getlist("document_number[]")
                doc_issue_dates = request.POST.getlist("document_issue_date[]")
                doc_expiry_dates = request.POST.getlist("document_expiry_date[]")
                doc_remarks = request.POST.getlist("document_remarks[]")
                rows = []
                for i, name in enumerate(doc_names):
                    if name:
                        rows.append({
                            "name": name,
                            "number": doc_numbers[i] if i < len(doc_numbers) else "",
                            "issue_date": doc_issue_dates[i] if i < len(doc_issue_dates) else "",
                            "expiry_date": doc_expiry_dates[i] if i < len(doc_expiry_dates) else "",
                            "remarks": doc_remarks[i] if i < len(doc_remarks) else "",
                        })
                extra_details["documents"] = rows
                staff.hr_extra_details = extra_details
                staff.save(update_fields=["hr_extra_details"])
                messages.success(request, "Documents updated successfully!")

            elif tab == "login":
                login_detail = extra_details.get("login_detail", {})
                login_detail["email"] = (request.POST.get("login_email") or staff.admin.email).strip()
                login_detail["must_change_password"] = request.POST.get("must_change_password") == "on"
                login_detail["is_active"] = request.POST.get("is_active") == "on"
                login_detail["username"] = login_detail["email"]
                new_password = request.POST.get("new_password") or ""
                confirm_password = request.POST.get("confirm_password") or ""
                if new_password:
                    if new_password != confirm_password:
                        raise ValueError("Password and confirm password do not match")
                    staff.admin.set_password(new_password)
                    login_detail["password_updated"] = True
                staff.admin.email = login_detail["email"]
                staff.admin.must_change_password = login_detail["must_change_password"]
                staff.admin.is_active = login_detail["is_active"]
                staff.admin.save()
                extra_details["login_detail"] = login_detail
                staff.hr_extra_details = extra_details
                staff.save(update_fields=["hr_extra_details"])
                messages.success(request, "Login details updated successfully!")

            elif tab == "leftout":
                leftout_status = {
                    "is_left_out": request.POST.get("is_left_out") == "on",
                    "left_out_date": request.POST.get("left_out_date", "").strip(),
                    "reason": request.POST.get("left_out_reason", "").strip(),
                    "remarks": request.POST.get("left_out_remarks", "").strip(),
                }
                extra_details["leftout_status"] = leftout_status
                staff.hr_extra_details = extra_details
                staff.save(update_fields=["hr_extra_details"])
                messages.success(request, "Left-out status updated successfully!")

            return redirect(reverse("employee_details", args=[staff_id]))

        except Exception as e:
            messages.error(request, f"Error saving details: {str(e)}")

    try:
        id_details = staff.identification_details
    except EmployeeIdentificationDetails.DoesNotExist:
        id_details, _ = EmployeeIdentificationDetails.objects.get_or_create(staff=staff)

    context = {
        "page_title": "Employee Details",
        "staff": staff,
        "employee": staff.admin,
        "id_details": id_details,
        "education_details": staff.education_details.all(),
        "promotion_history": staff.promotion_history.all(),
        "transfer_history": extra_details.get("transfer_history", []),
        "work_experiences": extra_details.get("work_experiences", []),
        "documents": extra_details.get("documents", []),
        "login_detail": extra_details.get("login_detail", {}),
        "leftout_status": extra_details.get("leftout_status", {}),
        "employment_type_choices": Staff.EMPLOYMENT_TYPE_CHOICES,
        "blood_group_choices": EmployeeIdentificationDetails.BLOOD_GROUP_CHOICES,
        "education_level_choices": EmployeeEducationDetails.EDUCATION_LEVEL_CHOICES,
        "promotion_type_choices": EmployeePromotionHistory.PROMOTION_TYPE_CHOICES,
    }
    return render(request, "modules/employee_details.html", context)


# ---------- Inventory ----------


@login_required
def inventory(request):
    if request.method == "POST":
        action = request.POST.get("action")
        item_type = request.POST.get("item_type", "general")

        if action == "delete":
            item_id = request.POST.get("id")
            if item_type == "consumable":
                ConsumableItem.objects.filter(id=item_id).delete()
            elif item_type == "fixed":
                FixedItem.objects.filter(id=item_id).delete()
            else:
                InventoryItem.objects.filter(id=item_id).delete()
            messages.success(request, "Item removed.")
        elif action == "edit":
            item_id = request.POST.get("id")
            if item_type == "consumable":
                item = get_object_or_404(ConsumableItem, id=item_id)
                item.name = (request.POST.get("name") or item.name).strip()
                item.category = (request.POST.get("category") or item.category).strip()
                item.quantity = int(request.POST.get("quantity") or item.quantity)
                item.unit = (request.POST.get("unit") or item.unit).strip()
                item.location = (request.POST.get("location") or "").strip()
                item.reorder_level = int(request.POST.get("reorder_level") or item.reorder_level)
                item.supplier_name = (request.POST.get("supplier_name") or item.supplier_name).strip()
                item.cost_per_unit = request.POST.get("cost_per_unit", item.cost_per_unit)
                item.save()
            elif item_type == "fixed":
                item = get_object_or_404(FixedItem, id=item_id)
                item.name = (request.POST.get("name") or item.name).strip()
                item.category = (request.POST.get("category") or item.category).strip()
                item.quantity = int(request.POST.get("quantity") or item.quantity)
                item.location = (request.POST.get("location") or "").strip()
                item.serial_number = (request.POST.get("serial_number") or item.serial_number).strip()
                item.condition = request.POST.get("condition", item.condition)
                item.remarks = request.POST.get("remarks", "").strip()
                item.save()
            else:
                item = get_object_or_404(InventoryItem, id=item_id)
                item.name = (request.POST.get("name") or item.name).strip()
                item.category = (request.POST.get("category") or item.category).strip()
                item.quantity = int(request.POST.get("quantity") or item.quantity)
                item.unit = (request.POST.get("unit") or item.unit).strip()
                item.location = (request.POST.get("location") or "").strip()
                item.reorder_level = int(request.POST.get("reorder_level") or item.reorder_level)
                item.item_type = item_type
                item.save()
            messages.success(request, "Item updated.")
        else:
            # Add new item
            name = (request.POST.get("name") or "").strip()
            if not name:
                messages.error(request, "Item name is required.")
            else:
                if item_type == "consumable":
                    ConsumableItem.objects.create(
                        name=name,
                        category=(request.POST.get("category") or "General").strip(),
                        quantity=int(request.POST.get("quantity") or 0),
                        unit=(request.POST.get("unit") or "pcs").strip(),
                        location=(request.POST.get("location") or "").strip(),
                        reorder_level=int(request.POST.get("reorder_level") or 5),
                        supplier_name=(request.POST.get("supplier_name") or "").strip(),
                        cost_per_unit=request.POST.get("cost_per_unit", 0),
                    )
                elif item_type == "fixed":
                    FixedItem.objects.create(
                        name=name,
                        category=(request.POST.get("category") or "General").strip(),
                        quantity=int(request.POST.get("quantity") or 1),
                        location=(request.POST.get("location") or "").strip(),
                        serial_number=(request.POST.get("serial_number") or "").strip(),
                        purchase_cost=request.POST.get("purchase_cost", 0),
                        condition=request.POST.get("condition", "new"),
                    )
                else:
                    InventoryItem.objects.create(
                        name=name,
                        category=(request.POST.get("category") or "General").strip(),
                        quantity=int(request.POST.get("quantity") or 0),
                        unit=(request.POST.get("unit") or "pcs").strip(),
                        location=(request.POST.get("location") or "").strip(),
                        reorder_level=int(request.POST.get("reorder_level") or 5),
                        item_type=item_type,
                    )
                messages.success(request, "Item added.")
        return redirect(reverse("inventory"))

    # Get all inventory items
    all_items = InventoryItem.objects.all()
    consumable_items = ConsumableItem.objects.all()
    fixed_items = FixedItem.objects.all()

    # Calculate statistics
    total_inventory_qty = all_items.aggregate(total=Sum("quantity"))["total"] or 0
    consumable_qty = consumable_items.aggregate(total=Sum("quantity"))["total"] or 0
    fixed_qty = fixed_items.aggregate(total=Sum("quantity"))["total"] or 0

    # Low stock items
    low_stock_inventory = [i for i in all_items if i.is_low_stock]
    low_stock_consumable = [i for i in consumable_items if i.is_low_stock]

    # Calculate total costs for consumable items
    total_consumable_cost = sum(item.total_cost for item in consumable_items)

    # Calculate total value for fixed items
    total_fixed_value = sum(item.current_value for item in fixed_items)

    context = {
        "page_title": "Inventory Management",
        "all_items": all_items,
        "consumable_items": consumable_items,
        "fixed_items": fixed_items,

        # Summary cards
        "total_items_count": all_items.count(),
        "total_items_qty": total_inventory_qty,
        "total_consumable_count": consumable_items.count(),
        "total_consumable_qty": consumable_qty,
        "total_fixed_count": fixed_items.count(),
        "total_fixed_qty": fixed_qty,

        # Additional stats
        "total_consumable_cost": total_consumable_cost,
        "total_fixed_value": total_fixed_value,
        "low_stock_inventory_count": len(low_stock_inventory),
        "low_stock_consumable_count": len(low_stock_consumable),
        "healthy_stock_count": all_items.count() - len(low_stock_inventory),
        "low_stock_items": low_stock_inventory,
        "low_stock_consumable": low_stock_consumable,
    }
    return render(request, "modules/inventory.html", context)


@login_required
def inventory_items_list(request):
    """Paginated list of all InventoryItems – matches the reference ERP screenshot."""
    from django.core.paginator import Paginator

    search_q = (request.GET.get("q") or "").strip()
    qs = InventoryItem.objects.all().order_by("name")
    if search_q:
        qs = qs.filter(Q(name__icontains=search_q) | Q(category__icontains=search_q))

    # Handle POST for edit / delete
    if request.method == "POST":
        action = request.POST.get("action")
        item_id = request.POST.get("id")
        if action == "delete" and item_id:
            InventoryItem.objects.filter(id=item_id).delete()
            messages.success(request, "Item deleted.")
        elif action == "edit" and item_id:
            item = get_object_or_404(InventoryItem, id=item_id)
            item.name = (request.POST.get("name") or item.name).strip()
            item.category = (request.POST.get("category") or item.category).strip()
            item.quantity = int(request.POST.get("quantity") or item.quantity)
            item.unit = (request.POST.get("unit") or item.unit).strip()
            item.location = (request.POST.get("location") or "").strip()
            item.reorder_level = int(request.POST.get("reorder_level") or item.reorder_level)
            item.save()
            messages.success(request, "Item updated.")
        elif action == "add":
            name = (request.POST.get("name") or "").strip()
            if name:
                InventoryItem.objects.create(
                    name=name,
                    category=(request.POST.get("category") or "General").strip(),
                    quantity=int(request.POST.get("quantity") or 0),
                    unit=(request.POST.get("unit") or "pcs").strip(),
                    location=(request.POST.get("location") or "").strip(),
                    reorder_level=int(request.POST.get("reorder_level") or 5),
                )
                messages.success(request, "Item added.")
        return redirect(reverse("inventory_items_list"))

    paginator = Paginator(qs, 15)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_title": "List of Items",
        "list_subtitle": "",
        "item_type": "general",
        "items": page_obj,
        "page_obj": page_obj,
        "search_q": search_q,
        "total_count": paginator.count,
        "show_unit": True,
        "show_reorder_level": True,
    }
    return render(request, "modules/inventory_item_list.html", context)


@login_required
def inventory_consumables_list(request):
    """Paginated list of ConsumableItems."""
    from django.core.paginator import Paginator

    search_q = (request.GET.get("q") or "").strip()
    qs = ConsumableItem.objects.all().order_by("name")
    if search_q:
        qs = qs.filter(Q(name__icontains=search_q) | Q(category__icontains=search_q))

    if request.method == "POST":
        action = request.POST.get("action")
        item_id = request.POST.get("id")
        if action == "delete" and item_id:
            ConsumableItem.objects.filter(id=item_id).delete()
            messages.success(request, "Item deleted.")
        elif action == "edit" and item_id:
            item = get_object_or_404(ConsumableItem, id=item_id)
            item.name = (request.POST.get("name") or item.name).strip()
            item.category = (request.POST.get("category") or item.category).strip()
            item.quantity = int(request.POST.get("quantity") or item.quantity)
            item.unit = (request.POST.get("unit") or item.unit).strip()
            item.location = (request.POST.get("location") or "").strip()
            item.reorder_level = int(request.POST.get("reorder_level") or item.reorder_level)
            item.save()
            messages.success(request, "Item updated.")
        elif action == "add":
            name = (request.POST.get("name") or "").strip()
            if name:
                ConsumableItem.objects.create(
                    name=name,
                    category=(request.POST.get("category") or "General").strip(),
                    quantity=int(request.POST.get("quantity") or 0),
                    unit=(request.POST.get("unit") or "pcs").strip(),
                    location=(request.POST.get("location") or "").strip(),
                    reorder_level=int(request.POST.get("reorder_level") or 5),
                )
                messages.success(request, "Item added.")
        return redirect(reverse("inventory_consumables_list"))

    paginator = Paginator(qs, 15)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_title": "List of Items",
        "list_subtitle": "Consumable Goods",
        "item_type": "consumable",
        "items": page_obj,
        "page_obj": page_obj,
        "search_q": search_q,
        "total_count": paginator.count,
        "show_unit": True,
        "show_reorder_level": True,
    }
    return render(request, "modules/inventory_item_list.html", context)


@login_required
def inventory_fixed_list(request):
    """Paginated list of FixedItems."""
    from django.core.paginator import Paginator

    search_q = (request.GET.get("q") or "").strip()
    qs = FixedItem.objects.all().order_by("name")
    if search_q:
        qs = qs.filter(Q(name__icontains=search_q) | Q(category__icontains=search_q))

    if request.method == "POST":
        action = request.POST.get("action")
        item_id = request.POST.get("id")
        if action == "delete" and item_id:
            FixedItem.objects.filter(id=item_id).delete()
            messages.success(request, "Item deleted.")
        elif action == "edit" and item_id:
            item = get_object_or_404(FixedItem, id=item_id)
            item.name = (request.POST.get("name") or item.name).strip()
            item.category = (request.POST.get("category") or item.category).strip()
            item.quantity = int(request.POST.get("quantity") or item.quantity)
            item.location = (request.POST.get("location") or "").strip()
            item.serial_number = (request.POST.get("serial_number") or item.serial_number).strip()
            item.condition = request.POST.get("condition", item.condition)
            item.save()
            messages.success(request, "Item updated.")
        elif action == "add":
            name = (request.POST.get("name") or "").strip()
            if name:
                FixedItem.objects.create(
                    name=name,
                    category=(request.POST.get("category") or "General").strip(),
                    quantity=int(request.POST.get("quantity") or 1),
                    location=(request.POST.get("location") or "").strip(),
                    serial_number=(request.POST.get("serial_number") or "").strip(),
                    condition=request.POST.get("condition", "new"),
                )
                messages.success(request, "Item added.")
        return redirect(reverse("inventory_fixed_list"))

    paginator = Paginator(qs, 15)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_title": "List of Items",
        "list_subtitle": "Fixed Assets",
        "item_type": "fixed",
        "items": page_obj,
        "page_obj": page_obj,
        "search_q": search_q,
        "total_count": paginator.count,
        "show_unit": True,
        "show_reorder_level": False,
    }
    return render(request, "modules/inventory_item_list.html", context)


@login_required
def inventory_edit_item(request, item_type, item_id):
    """Full-page edit form for an inventory item – matches the reference ERP screenshot."""
    # Resolve the item
    if item_type == "consumable":
        item = get_object_or_404(ConsumableItem, id=item_id)
        list_url = reverse("inventory_consumables_list")
        type_label = "Consumable Goods"
    elif item_type == "fixed":
        item = get_object_or_404(FixedItem, id=item_id)
        list_url = reverse("inventory_fixed_list")
        type_label = "Fixed Assets"
    else:
        item = get_object_or_404(InventoryItem, id=item_id)
        list_url = reverse("inventory_items_list")
        type_label = ""

    if request.method == "POST":
        item.name = (request.POST.get("name") or item.name).strip()
        item.category = (request.POST.get("category") or item.category).strip()
        item.quantity = int(request.POST.get("quantity") or item.quantity)

        if hasattr(item, "unit"):
            item.unit = (request.POST.get("unit") or item.unit).strip()
        if hasattr(item, "location"):
            item.location = (request.POST.get("location") or "").strip()
        if hasattr(item, "reorder_level"):
            val = request.POST.get("reorder_level")
            if val:
                item.reorder_level = int(val)

        # Extra fields for specific types
        if item_type == "consumable":
            item.supplier_name = (request.POST.get("supplier_name") or "").strip()
            cost = request.POST.get("cost_per_unit")
            if cost:
                item.cost_per_unit = cost
        elif item_type == "fixed":
            item.serial_number = (request.POST.get("serial_number") or "").strip()
            item.condition = request.POST.get("condition", item.condition)

        # Generic fields
        item.lp_no = (request.POST.get("lp_no") or "").strip() if hasattr(item, "lp_no") else None
        remarks = request.POST.get("remarks", "").strip()
        if hasattr(item, "remarks"):
            item.remarks = remarks

        item.save()
        messages.success(request, "Item updated successfully.")
        return redirect(list_url)

    context = {
        "page_title": "Item Entry Form",
        "type_label": type_label,
        "item_type": item_type,
        "item": item,
        "list_url": list_url,
    }
    return render(request, "modules/inventory_edit_item.html", context)


# ---------- Library Dashboard ----------


@login_required
def library_dashboard(request):
    """Library dashboard matching the Sagarmatha ERP screenshot layout."""
    from django.db.models import Sum, Count

    # Summary cards
    total_resources = Book.objects.count()
    total_accession = Book.objects.aggregate(total=Sum("quantity"))["total"] or 0
    active_loans = BookLoan.objects.filter(returned_on__isnull=True)
    total_checkouts = active_loans.count()
    pending_clearance = ClearanceRequest.objects.filter(status=0).count()

    # Recent purchases (books with purchase_date, sorted newest first)
    recent_purchases = Book.objects.exclude(purchase_date__isnull=True).order_by("-purchase_date")[:12]
    if not recent_purchases.exists():
        recent_purchases = Book.objects.all().order_by("-id")[:12]

    # Recent clearance requests
    recent_clearance = ClearanceRequest.objects.select_related("student").all()[:10]

    # Handle POST actions (add book, issue, return, clearance approve/reject)
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_book":
            name = (request.POST.get("name") or "").strip()
            if name:
                isbn = (request.POST.get("isbn") or "").strip()
                Book.objects.update_or_create(
                    isbn=isbn,
                    defaults={
                        "name": name,
                        "author": (request.POST.get("author") or "").strip(),
                        "category": (request.POST.get("category") or "General").strip(),
                        "quantity": int(request.POST.get("quantity") or 1),
                        "purchase_date": request.POST.get("purchase_date") or None,
                    },
                )
                messages.success(request, "Book saved.")
            else:
                messages.error(request, "Book name is required.")

        elif action == "clearance_approve":
            cr = get_object_or_404(ClearanceRequest, id=request.POST.get("id"))
            cr.status = 1
            cr.save()
            messages.success(request, "Clearance approved.")

        elif action == "clearance_reject":
            cr = get_object_or_404(ClearanceRequest, id=request.POST.get("id"))
            cr.status = -1
            cr.save()
            messages.success(request, "Clearance rejected.")

        return redirect(reverse("library_dashboard"))

    context = {
        "page_title": "Dashboard Library",
        "total_resources": total_resources,
        "total_accession": total_accession,
        "total_checkouts": total_checkouts,
        "pending_clearance": pending_clearance,
        "recent_purchases": recent_purchases,
        "recent_clearance": recent_clearance,
    }
    return render(request, "modules/library_dashboard.html", context)


# ---------- Payslip (real implementation) ----------


def payslip(request):
    staff = Staff.objects.filter(admin=request.user).first()
    if request.method == "POST" and staff and request.POST.get("action") == "generate":
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))
        basic = Decimal(request.POST.get("basic_salary") or "40000")
        allowances = Decimal(request.POST.get("allowances") or "5000")
        deductions = Decimal(request.POST.get("deductions") or "2000")
        Payslip.objects.update_or_create(
            staff=staff,
            month=month,
            year=year,
            defaults={
                "basic_salary": basic,
                "allowances": allowances,
                "deductions": deductions,
                "paid": True,
            },
        )
        messages.success(request, "Payslip generated.")
        return redirect(reverse("payslip_dashboard"))

    if staff:
        payslips = Payslip.objects.filter(staff=staff)
        owner_name = staff.admin.get_full_name() or staff.admin.first_name
    else:
        payslips = Payslip.objects.select_related("staff", "staff__admin").all()
        owner_name = request.user.get_full_name() or request.user.first_name

    context = {
        "page_title": "Payslip",
        "payslips": payslips,
        "owner_name": owner_name,
        "is_staff": bool(staff),
        "month_choices": Payslip.MONTH_CHOICES,
    }
    return render(request, "modules/payslip.html", context)


# ---------- Store (Store Requisitions) ----------


def store(request):
    # Reuse inventory data + low-stock requisitions view
    items = InventoryItem.objects.all()
    low_stock = [i for i in items if i.is_low_stock]
    requisitions = sorted(low_stock, key=lambda i: i.quantity)
    context = {
        "page_title": "Store",
        "requisitions": requisitions,
        "requisition_count": len(requisitions),
        "total_items": items.count(),
    }
    return render(request, "modules/store.html", context)


# ---------- Attendance (Biometric-based) ----------


from django.utils.dateparse import parse_date
from datetime import datetime, timedelta


def attendance_dashboard(request):
    """Main attendance dashboard showing daily log sheet"""
    # Get date and status filters
    date_str = request.GET.get('date')
    status_filter = request.GET.get('status', 'all')

    if date_str:
        try:
            filter_date = parse_date(date_str)
        except:
            filter_date = datetime.today().date()
    else:
        filter_date = datetime.today().date()

    # Get all attendance records for the selected date
    attendance_records = EmployeeAttendance.objects.filter(date=filter_date).select_related('staff', 'staff__admin', 'staff__course')

    # Apply status filter
    if status_filter and status_filter != 'all':
        attendance_records = attendance_records.filter(status=status_filter)

    # Calculate statistics
    total_staff = Staff.objects.count()
    present = attendance_records.filter(status__in=['present', 'late']).count()
    absent = attendance_records.filter(status='absent').count()
    early_out = attendance_records.filter(status='early_out').count()
    on_leave = attendance_records.filter(status='leave').count()

    # Format data for template
    attendance_list = []
    for idx, record in enumerate(attendance_records, 1):
        attendance_list.append({
            'sn': idx,
            'code': record.staff.admin.id,
            'name': f"{record.staff.admin.first_name} {record.staff.admin.last_name}",
            'department': record.staff.department or record.staff.course.name if record.staff.course else 'N/A',
            'late_in': record.late_by_minutes if record.status == 'late' else '',
            'in_time': record.in_time.strftime('%H:%M') if record.in_time else '--',
            'out_time': record.out_time.strftime('%H:%M') if record.out_time else '--',
            'early_out': record.early_out_by_minutes if record.status == 'early_out' else '',
            'worked_hours': f"{record.worked_hours:.2f}" if record.worked_hours else '--',
            'status': record.get_status_display(),
            'status_class': get_status_color_class(record.status),
            'remarks': record.remarks or '',
            'record_id': record.id,
        })

    context = {
        'page_title': 'Employees Attendance',
        'date': filter_date.strftime('%Y/%m/%d'),
        'status_filter': status_filter,
        'attendance_records': attendance_list,
        'total_staff': total_staff,
        'present_count': present,
        'absent_count': absent,
        'early_out_count': early_out,
        'on_leave_count': on_leave,
        'status_choices': EmployeeAttendance.STATUS_CHOICES,
    }

    return render(request, 'modules/attendance.html', context)


def mark_biometric_attendance(request):
    """Mark attendance based on biometric entry/exit times"""
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')
        date_str = request.POST.get('date')
        in_time = request.POST.get('in_time')
        out_time = request.POST.get('out_time')

        try:
            staff = Staff.objects.get(admin_id=staff_id)
            date = parse_date(date_str)

            # Parse times
            in_time_obj = datetime.strptime(in_time, '%H:%M').time() if in_time else None
            out_time_obj = datetime.strptime(out_time, '%H:%M').time() if out_time else None

            # Create or update biometric log
            biometric, created = BiometricLog.objects.update_or_create(
                staff=staff,
                date=date,
                defaults={
                    'in_time': in_time_obj,
                    'out_time': out_time_obj,
                    'in_timestamp': datetime.combine(date, in_time_obj) if in_time_obj else None,
                    'out_timestamp': datetime.combine(date, out_time_obj) if out_time_obj else None,
                }
            )

            # Calculate attendance status
            attendance_status = calculate_attendance_status(staff, date, biometric)

            # Create or update attendance record
            attendance, _ = EmployeeAttendance.objects.update_or_create(
                staff=staff,
                date=date,
                defaults=attendance_status
            )

            messages.success(request, f"Attendance marked for {staff.admin.first_name} on {date}")
        except Staff.DoesNotExist:
            messages.error(request, "Staff member not found.")
        except Exception as e:
            messages.error(request, f"Error marking attendance: {str(e)}")

        return redirect(reverse('attendance_dashboard'))

    return redirect(reverse('attendance_dashboard'))


def sync_biometric_data(request):
    """Sync biometric data and auto-generate attendance records"""
    if request.method == "POST":
        date_str = request.POST.get('sync_date')

        try:
            sync_date = parse_date(date_str) if date_str else datetime.today().date()

            # Get all biometric logs for the date
            biometric_logs = BiometricLog.objects.filter(date=sync_date)

            processed = 0
            for log in biometric_logs:
                # Calculate attendance status
                status_data = calculate_attendance_status(log.staff, sync_date, log)

                # Create or update attendance
                attendance, created = EmployeeAttendance.objects.update_or_create(
                    staff=log.staff,
                    date=sync_date,
                    defaults=status_data
                )
                processed += 1

            # Mark all staff without biometric entry as absent
            all_staff = Staff.objects.all()
            for staff in all_staff:
                if not BiometricLog.objects.filter(staff=staff, date=sync_date).exists():
                    EmployeeAttendance.objects.update_or_create(
                        staff=staff,
                        date=sync_date,
                        defaults={
                            'status': 'absent',
                            'in_time': None,
                            'out_time': None,
                            'worked_hours': 0,
                        }
                    )
                    processed += 1

            messages.success(request, f"Synced attendance for {processed} staff members on {sync_date}")
        except Exception as e:
            messages.error(request, f"Error syncing biometric data: {str(e)}")

        return redirect(reverse('attendance_dashboard'))

    return redirect(reverse('attendance_dashboard'))


def get_status_color_class(status):
    """Return CSS class for status color"""
    color_map = {
        'present': 'badge-success',
        'late': 'badge-warning',
        'early_out': 'badge-info',
        'absent': 'badge-danger',
        'half_day': 'badge-secondary',
        'leave': 'badge-light',
    }
    return color_map.get(status, 'badge-secondary')


def calculate_attendance_status(staff, date, biometric_log):
    """Calculate attendance status based on biometric log"""
    # Define working hours (e.g., 9 AM to 6 PM)
    CUTOFF_TIME = datetime.strptime('09:00', '%H:%M').time()
    EXPECTED_OUT_TIME = datetime.strptime('18:00', '%H:%M').time()

    if not biometric_log.in_time:
        return {
            'status': 'absent',
            'in_time': None,
            'out_time': None,
            'worked_hours': 0,
            'late_by_minutes': 0,
            'early_out_by_minutes': 0,
        }

    in_time = biometric_log.in_time
    out_time = biometric_log.out_time

    # Calculate late minutes
    late_minutes = 0
    if in_time > CUTOFF_TIME:
        late_delta = datetime.combine(date, in_time) - datetime.combine(date, CUTOFF_TIME)
        late_minutes = int(late_delta.total_seconds() / 60)

    # Calculate early out minutes
    early_out_minutes = 0
    if out_time and out_time < EXPECTED_OUT_TIME:
        early_delta = datetime.combine(date, EXPECTED_OUT_TIME) - datetime.combine(date, out_time)
        early_out_minutes = int(early_delta.total_seconds() / 60)

    # Calculate worked hours
    worked_hours = 0
    if out_time:
        start = datetime.combine(date, in_time)
        end = datetime.combine(date, out_time)
        if end < start:  # Handle cross-midnight shifts
            end = datetime.combine(date + timedelta(days=1), out_time)
        delta = end - start
        worked_hours = Decimal(str(round(delta.total_seconds() / 3600, 2)))

    # Determine status
    if late_minutes > 0:
        status = 'late'
    elif early_out_minutes > 60:  # More than 1 hour early
        status = 'early_out'
    else:
        status = 'present'

    return {
        'status': status,
        'in_time': in_time,
        'out_time': out_time,
        'worked_hours': worked_hours,
        'late_by_minutes': late_minutes,
        'early_out_by_minutes': early_out_minutes,
    }

