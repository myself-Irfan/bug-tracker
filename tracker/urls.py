from django.urls import path,  include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from tracker import views
from tracker.api.project_api import ProjectViewSet
from tracker.views import DashboardStatsAPIView
from tracker.api.activity_api import ActivityLogListApiView, ActivityLogDetailApiView

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'bugs', views.BugViewSet, basename='bug')

bugs_router = routers.NestedDefaultRouter(router, r'bugs', lookup='bug')
bugs_router.register(r'comments', views.CommentViewSet, basename='bug-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(bugs_router.urls)),
    path('v1/activity/', ActivityLogListApiView.as_view(), name=ActivityLogListApiView.api_name),
    path('v1/activity/<int:pk>', ActivityLogDetailApiView.as_view(), name=ActivityLogDetailApiView.api_name),
    path('v1/dashboard-stats/', DashboardStatsAPIView.as_view(), name=DashboardStatsAPIView.api_name)
]