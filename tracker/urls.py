from django.urls import path,  include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from tracker import views


router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'bugs', views.BugViewSet, basename='bug')
router.register(r'activity', views.ActivityLogViewSet, basename='activity')

bugs_router = routers.NestedDefaultRouter(router, r'bugs', lookup='bug')
bugs_router.register(r'comments', views.CommentViewSet, basename='bug-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(bugs_router.urls)),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats')
]