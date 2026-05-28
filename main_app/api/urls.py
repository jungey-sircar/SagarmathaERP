from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import HODDashboardAPIView
from .viewsets import (
    CourseViewSet, StaffViewSet, SubjectViewSet, StudentViewSet, AttendanceViewSet,
    AttendanceReportViewSet, LeaveReportStaffViewSet, BookViewSet, SessionViewSet, StudentResultViewSet
)

router = routers.DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'students', StudentViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'attendance-report', AttendanceReportViewSet)
router.register(r'leave-staff', LeaveReportStaffViewSet)
router.register(r'books', BookViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'results', StudentResultViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('hod/dashboard/', HODDashboardAPIView.as_view(), name='api_hod_dashboard'),
    path('', include(router.urls)),
]
