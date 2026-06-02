from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

# Register your models here.


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "gender",
            "profile_pic",
            "address",
            "user_type",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "gender",
            "profile_pic",
            "address",
            "user_type",
            "is_active",
            "is_staff",
            "is_superuser",
        )


class UserModel(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "user_type", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("user_type", "is_staff", "is_superuser", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "profile_pic",
                    "address",
                    "user_type",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "gender",
                    "profile_pic",
                    "address",
                    "user_type",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


admin.site.register(CustomUser, UserModel)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Book)
admin.site.register(IssuedBook)
admin.site.register(Library)
admin.site.register(Subject)
admin.site.register(Session)
from .models import Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "published_at")
    search_fields = ("title", "body")
    list_filter = ("audience", "published_at")
    filter_horizontal = ("targets",)


admin.site.register(Announcement, AnnouncementAdmin)


# Attendance and Biometric Models
class BiometricLogAdmin(admin.ModelAdmin):
    list_display = ("get_name", "date", "in_time", "out_time", "worked_hours", "created_at")
    list_filter = ("date", "created_at")
    search_fields = (
        "staff__admin__first_name", "staff__admin__last_name", "staff__admin__email",
        "student__admin__first_name", "student__admin__last_name", "student__admin__email"
    )
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at", "worked_hours")
    fieldsets = (
        ("User Link", {"fields": ("staff", "student", "date")}),
        ("Punch Times", {"fields": ("in_time", "out_time", "in_timestamp", "out_timestamp")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_name(self, obj):
        if obj.staff:
            return f"Staff: {obj.staff}"
        if obj.student:
            return f"Student: {obj.student}"
        return "Unknown"
    get_name.short_description = "Name"


class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ("staff", "date", "status", "in_time", "out_time", "worked_hours", "late_by_minutes")
    list_filter = ("status", "date", "staff__department")
    search_fields = ("staff__admin__first_name", "staff__admin__last_name", "staff__admin__email")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Staff & Date", {"fields": ("staff", "date", "status")}),
        ("Punch Times", {"fields": ("in_time", "out_time", "worked_hours")}),
        ("Deviations", {"fields": ("late_by_minutes", "early_out_by_minutes")}),
        ("Notes", {"fields": ("remarks",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status", "in_time", "out_time", "worked_hours", "late_by_minutes")
    list_filter = ("status", "date", "student__course")
    search_fields = ("student__admin__first_name", "student__admin__last_name", "student__admin__email")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Student & Date", {"fields": ("student", "date", "status")}),
        ("Punch Times", {"fields": ("in_time", "out_time", "worked_hours")}),
        ("Deviations", {"fields": ("late_by_minutes", "early_out_by_minutes")}),
        ("Notes", {"fields": ("remarks",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


admin.site.register(BiometricLog, BiometricLogAdmin)
admin.site.register(EmployeeAttendance, EmployeeAttendanceAdmin)
admin.site.register(StudentAttendance, StudentAttendanceAdmin)

