from rest_framework import serializers
from ..models import (
    CustomUser, Course, Staff, Subject, Student, Attendance, AttendanceReport,
    LeaveReportStaff, Book, Session, StudentResult, InventoryItem, ConsumableItem, FixedItem
)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ('password',)


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    admin = CustomUserSerializer(read_only=True)
    admin_id = serializers.PrimaryKeyRelatedField(write_only=True, source='admin', queryset=CustomUser.objects.all())

    class Meta:
        model = Staff
        fields = ['id', 'course', 'admin', 'admin_id', 'role', 'role_detail']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    admin = CustomUserSerializer(read_only=True)
    admin_id = serializers.PrimaryKeyRelatedField(write_only=True, source='admin', queryset=CustomUser.objects.all())

    class Meta:
        model = Student
        fields = ['id', 'admin', 'admin_id', 'course', 'session']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class AttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceReport
        fields = '__all__'


class LeaveReportStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveReportStaff
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class StudentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentResult
        fields = '__all__'


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'


class ConsumableItemSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = ConsumableItem
        fields = '__all__'

    def get_total_cost(self, obj):
        return float(obj.total_cost)


class FixedItemSerializer(serializers.ModelSerializer):
    current_value = serializers.SerializerMethodField()

    class Meta:
        model = FixedItem
        fields = '__all__'

    def get_current_value(self, obj):
        return float(obj.current_value)

