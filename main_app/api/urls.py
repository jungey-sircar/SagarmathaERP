from django.urls import path, include
from rest_framework import routers
from .views import HODDashboardAPIView, InventoryDashboardAPIView
from .viewsets import (
    CourseViewSet, StaffViewSet, SubjectViewSet, StudentViewSet, AttendanceViewSet,
    AttendanceReportViewSet, LeaveReportStaffViewSet, BookViewSet, SessionViewSet,
    StudentResultViewSet, InventoryItemViewSet, ConsumableItemViewSet, FixedItemViewSet
)

try:
    from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
except ModuleNotFoundError:
    TokenObtainPairView = None
    TokenRefreshView = None

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
router.register(r'inventory-items', InventoryItemViewSet)
router.register(r'consumable-items', ConsumableItemViewSet)
router.register(r'fixed-items', FixedItemViewSet)

urlpatterns = [
    path('hod/dashboard/', HODDashboardAPIView.as_view(), name='api_hod_dashboard'),
    path('inventory/dashboard/', InventoryDashboardAPIView.as_view(), name='api_inventory_dashboard'),
    path('', include(router.urls)),
]

if TokenObtainPairView and TokenRefreshView:
    urlpatterns = [
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        *urlpatterns,
    ]
