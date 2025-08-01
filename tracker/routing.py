from django.urls import re_path
from tracker import consumers


websocket_urlpatterns = [
    re_path(r'ws/project/(?P<project_id>\w+)/$', consumers.BugTrackerConsumer.as_asgi()),
]