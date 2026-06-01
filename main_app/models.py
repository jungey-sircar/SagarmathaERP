from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]

    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    must_change_password = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.first_name + " " + self.last_name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Course(models.Model):
    name = models.CharField(max_length=120)
    hod = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hod_course",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    category = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1, help_text="Number of copies / accession count")
    purchase_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.name) + " [" + str(self.isbn) + "]"


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.DO_NOTHING, null=True, blank=False
    )
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Library(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=False
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=False)

    def __str__(self):
        return str(self.student)


def expiry():
    return datetime.today() + timedelta(days=14)


class IssuedBook(models.Model):
    student_id = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=13)
    issued_date = models.DateField(auto_now=True)
    expiry_date = models.DateField(default=expiry)


class Staff(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
    ]

    course = models.ForeignKey(
        Course, on_delete=models.DO_NOTHING, null=True, blank=False
    )
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=120, default="Teacher")
    role_detail = models.CharField(max_length=120, blank=True, default="")
    division = models.CharField(max_length=120, blank=True, default="")
    department = models.CharField(max_length=120, blank=True, default="")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, default='full_time')
    duty_shift = models.CharField(max_length=50, blank=True, default="")
    date_of_join = models.DateField(null=True, blank=True)
    permanent_on = models.DateField(null=True, blank=True)
    last_promotion_date = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, blank=True, default="")
    hr_extra_details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.admin.first_name + " " + self.admin.last_name


class EmployeeIdentificationDetails(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='identification_details')
    bank_name = models.CharField(max_length=200, blank=True, default="")
    account_number = models.CharField(max_length=50, blank=True, default="")
    citizenship_number = models.CharField(max_length=50, blank=True, default="")
    citizenship_issue_date = models.DateField(null=True, blank=True)
    citizenship_issue_place = models.CharField(max_length=200, blank=True, default="")
    pf_number = models.CharField(max_length=50, blank=True, default="")
    cit_number = models.CharField(max_length=50, blank=True, default="")
    pan_number = models.CharField(max_length=50, blank=True, default="")
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID Details - {self.staff}"


class EmployeeEducationDetails(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('slc', 'SLC'),
        ('intermediate', 'Intermediate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='education_details')
    level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES)
    title_of_qualification = models.CharField(max_length=200, blank=True, default="")
    institution = models.CharField(max_length=300, blank=True, default="")
    passed_year = models.IntegerField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    specialization = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-passed_year']

    def __str__(self):
        return f"{self.level} - {self.staff}"


class EmployeePromotionHistory(models.Model):
    PROMOTION_TYPE_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'External'),
        ('lateral', 'Lateral'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='promotion_history')
    date = models.DateField()
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPE_CHOICES, blank=True, default='internal')
    from_level = models.CharField(max_length=200, blank=True, default="")
    to_level = models.CharField(max_length=200, blank=True, default="")
    unpaid_leaves = models.IntegerField(default=0)
    remarks = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Promotion - {self.staff} - {self.date}"


class EmployeeTransferHistory(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='transfer_history')
    transfer_date = models.DateField()
    from_department = models.CharField(max_length=200, blank=True, default="")
    to_department = models.CharField(max_length=200, blank=True, default="")
    transfer_type = models.CharField(max_length=100, blank=True, default="")
    remarks = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transfer_date']

    def __str__(self):
        return f"Transfer - {self.staff} - {self.transfer_date}"


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BiometricLog(models.Model):
    """Records employee punch-in and punch-out times from biometric system"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='biometric_logs')
    date = models.DateField(auto_now_add=False)
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)
    in_timestamp = models.DateTimeField(null=True, blank=True)
    out_timestamp = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('staff', 'date')
        ordering = ['-date', '-in_timestamp']

    def __str__(self):
        return f"{self.staff} - {self.date}"

    @property
    def worked_hours(self):
        """Calculate worked hours from in_time and out_time"""
        if self.in_time and self.out_time:
            start = datetime.combine(datetime.today(), self.in_time)
            end = datetime.combine(datetime.today(), self.out_time)
            if end < start:  # Handle cross-midnight shifts
                end = datetime.combine(datetime.today() + timedelta(days=1), self.out_time)
            delta = end - start
            hours = delta.total_seconds() / 3600
            return round(hours, 2)
        return None


class Attendance(models.Model):
    """Attendance record for student sessions"""
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING, null=True, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance - {self.date} - {self.session}"


class EmployeeAttendance(models.Model):
    """Daily attendance record with status (Present/Absent/Late/Early Out) for employees"""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('early_out', 'Early Out'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='employee_attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    late_by_minutes = models.IntegerField(default=0)  # Minutes late
    early_out_by_minutes = models.IntegerField(default=0)  # Minutes early out
    remarks = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('staff', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.staff} - {self.date} - {self.status}"


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Admission(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    STAGE_CHOICES = (
        ("inquiry", "Pre-Admission Inquiry"),
        ("admitted", "Admitted"),
    )
    candidate_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    stage = models.CharField(max_length=12, choices=STAGE_CHOICES, default="inquiry")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    applied_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.candidate_name} ({self.get_stage_display()})"


class Exam(models.Model):
    STATUS_CHOICES = (
        ("scheduled", "Scheduled"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
    )
    name = models.CharField(max_length=120)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_date = models.DateField()
    total_marks = models.PositiveIntegerField(default=100)
    duration_minutes = models.PositiveIntegerField(default=180)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default="scheduled"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-exam_date"]

    def __str__(self):
        return f"{self.name} - {self.subject.name}"


class InventoryItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('consumable', 'Consumable'),
        ('fixed', 'Fixed Asset'),
        ('general', 'General'),
    ]
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80, default="General")
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='general')
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default="pcs")
    location = models.CharField(max_length=120, blank=True)
    reorder_level = models.PositiveIntegerField(default=5)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    def __str__(self):
        return self.name


class ConsumableItem(models.Model):
    """Consumable items (used up and need to be replenished)"""
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80, default="General")
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default="pcs")
    location = models.CharField(max_length=120, blank=True)
    reorder_level = models.PositiveIntegerField(default=5)
    supplier_name = models.CharField(max_length=160, blank=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    @property
    def total_cost(self):
        return self.quantity * self.cost_per_unit

    def __str__(self):
        return f"{self.name} ({self.category})"


class FixedItem(models.Model):
    """Fixed assets (long-term items that don't get consumed)"""
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ]
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80, default="General")
    quantity = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=120, blank=True)
    serial_number = models.CharField(max_length=100, blank=True, unique=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Percentage per year")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    warranty_expiry = models.DateField(null=True, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    @property
    def current_value(self):
        """Calculate current value based on depreciation"""
        if not self.purchase_date:
            return self.purchase_cost
        from datetime import datetime
        years_owned = (datetime.now().date() - self.purchase_date).days / 365.25
        depreciation_factor = 1 - (self.depreciation_rate / 100) * years_owned
        return self.purchase_cost * max(depreciation_factor, 0)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Payslip(models.Model):
    MONTH_CHOICES = [
        (i, m)
        for i, m in enumerate(
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
            start=1,
        )
    ]
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="payslips")
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-month"]
        unique_together = ("staff", "month", "year")

    @property
    def net_pay(self):
        return (
            (self.basic_salary or 0) + (self.allowances or 0) - (self.deductions or 0)
        )

    def __str__(self):
        return f"{self.staff} - {self.get_month_display()} {self.year}"


class Announcement(models.Model):
    title = models.CharField(max_length=160)
    body = models.TextField()
    audience = models.CharField(
        max_length=10,
        choices=(("all", "All"), ("staff", "Staff"), ("students", "Students")),
        default="all",
    )
    targets = models.ManyToManyField(
        "Staff",
        blank=True,
        related_name="announcements",
        help_text="Optional: target this announcement to specific staff members (overrides audience for those staff).",
    )
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


# ---------- Leave / Kaaj / Optional Holiday / Substitute ----------

STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED = 0, 1, -1
APPROVAL_STATUS_CHOICES = (
    (STATUS_PENDING, "Pending"),
    (STATUS_APPROVED, "Approved"),
    (STATUS_REJECTED, "Rejected"),
)


class KaajRequest(models.Model):
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="kaaj_requests"
    )
    purpose = models.CharField(max_length=255)
    destination = models.CharField(max_length=160, blank=True)
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.SmallIntegerField(
        choices=APPROVAL_STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class OptionalHolidayRequest(models.Model):
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="optional_holiday_requests"
    )
    holiday_name = models.CharField(max_length=160)
    holiday_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.SmallIntegerField(
        choices=APPROVAL_STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class SubstituteRequest(models.Model):
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="substitute_requests"
    )
    substitute_for = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="substituted_by_requests",
    )
    work_date = models.DateField()
    description = models.CharField(max_length=255)
    status = models.SmallIntegerField(
        choices=APPROVAL_STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


# ---------- Store Requisition (approval workflow) ----------


class StoreRequisition(models.Model):
    REQUESTED, APPROVED_STORE, FULFILLED, REJECTED_STORE = 0, 1, 2, -1
    STATUS_CHOICES = (
        (REQUESTED, "Requested"),
        (APPROVED_STORE, "Approved"),
        (FULFILLED, "Fulfilled"),
        (REJECTED_STORE, "Rejected"),
    )

    requested_by = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="requisitions"
    )
    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="requisitions"
    )
    quantity = models.PositiveIntegerField(default=1)
    reason = models.CharField(max_length=255, blank=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=REQUESTED)
    decided_by = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_requisitions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class Clearance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.SmallIntegerField(
        choices=APPROVAL_STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


# ---------- Academic items (Assessment, Study Material, Assignment, Lesson Plan) ----------


class AssessmentMark(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="assessment_marks"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="assessment_marks"
    )
    assessment_name = models.CharField(max_length=120, default="Internal")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]


class StudyMaterial(models.Model):
    title = models.CharField(max_length=160)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="study_materials"
    )
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]


class Assignment(models.Model):
    title = models.CharField(max_length=160)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="assignments"
    )
    description = models.TextField(blank=True)
    due_date = models.DateField()
    assigned_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-due_date"]


class LessonPlan(models.Model):
    title = models.CharField(max_length=160)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="lesson_plans"
    )
    week_number = models.PositiveSmallIntegerField(default=1)
    topics = models.TextField(blank=True)
    is_lab = models.BooleanField(default=False)
    prepared_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["week_number"]


# ---------- Library issue / return ----------


class BookLoan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans")
    borrower = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="book_loans"
    )
    issued_on = models.DateField(auto_now_add=True)
    due_on = models.DateField()
    returned_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_on"]

    @property
    def is_returned(self):
        return self.returned_on is not None


class Holiday(models.Model):
    """Editable Nepali holiday record. Replaces the hardcoded curated list
    once data has been seeded into the database."""

    bs_date = models.CharField(
        max_length=10, help_text="BS date as YYYY/MM/DD e.g. 2083/06/24"
    )
    name = models.CharField(max_length=255, help_text="Nepali / Devanagari name")
    remarks = models.CharField(
        max_length=255, blank=True, help_text="English remark or context"
    )
    is_holiday = models.BooleanField(
        default=True, help_text="Government public holiday"
    )
    is_optional = models.BooleanField(
        default=False, help_text="Optional / cultural day"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["bs_date"]

    def __str__(self):
        return f"{self.bs_date} — {self.name}"


class HolidaySettings(models.Model):
    """Singleton record (id=1) that controls the dashboard holiday range."""

    range_start = models.CharField(max_length=10, default="2083/02/15")
    range_end = models.CharField(max_length=10, default="2084/03/32")
    period_label = models.CharField(max_length=120, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Holiday Settings"
        verbose_name_plural = "Holiday Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        if not self.period_label:
            self.period_label = f"Holidays from {self.range_start} to {self.range_end}"
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.period_label or f"{self.range_start} → {self.range_end}"


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    user_type = str(instance.user_type)
    if user_type == "1":
        Admin.objects.get_or_create(admin=instance)
    if user_type == "2":
        Staff.objects.get_or_create(admin=instance)
    if user_type == "3":
        Student.objects.get_or_create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    user_type = str(instance.user_type)
    if user_type == "1":
        profile, _ = Admin.objects.get_or_create(admin=instance)
        profile.save()
    if user_type == "2":
        profile, _ = Staff.objects.get_or_create(admin=instance)
        profile.save()
    if user_type == "3":
        profile, _ = Student.objects.get_or_create(admin=instance)
        profile.save()


# ---------- Library: Clearance ----------


class ClearanceRequest(models.Model):
    STATUS_CHOICES = (
        (0, "Pending"),
        (1, "Approved"),
        (-1, "Rejected"),
    )
    student = models.ForeignKey(
        "CustomUser", on_delete=models.CASCADE, related_name="clearance_requests"
    )
    requested_on = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-requested_on"]

    def __str__(self):
        return f"Clearance: {self.student.email} — {self.get_status_display()}"


# todos
