from datetime import datetime

from django.db.models import QuerySet
from rest_framework import generics, status, filters, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import PermissionDenied, NotFound
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.views import APIView

from tracker.models import Project, Bug, Comment, ActivityLog
from tracker.serializers import ProjectSerializer, BugSerializer, CommentSerializer
from django.contrib.auth.models import User
from bugtracker.utils.logger import get_logger
from tracker.services.summary_service import SummaryService
from bugtracker.utils import apilogger

logger = get_logger(__name__)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Project CRUD operations with proper permissions
    """
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['name', 'description']

    def get_queryset(self) -> QuerySet:
        return Project.objects.filter(
            models.Q(owner=self.request.user) | models.Q(members=self.request.user)
        ).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            logger.info(f'No project found for user-{request.user}')
            return Response(
                data={'message': 'No projects found', 'data': None},
                status=status.HTTP_200_OK
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated = self.get_paginated_response(serializer.data).data
            paginated['message'] = "Project list retrieved"
            return Response(paginated)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Project list retrieved',
            'data': serializer.data
        })

    def perform_create(self, serializer) -> Response:
        """
        set current user as owner and log
        :param serializer:
        :return: None
        """
        project = serializer.save(owner=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            project=project,
            action='created',
            description=f'Created project: {project.name}'
        )
        return Response(
            data={'message': 'Project created successfully'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def add_member(self, request) -> Response:
        """
        add a member to the project
        :param request:
        :return: Response
        """
        project = self.get_object()
        if project.owner != request.user:
            return Response(
                data={'error': 'Only project owner can add members'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username')
        if not username:
            return Response(
                data={'error': 'Username required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
            project.members.add(user)
            ActivityLog.objects.create(
                user=self.request.user,
                project=project,
                action='updated',
                description=f'Added user-{username} to project-{project.name}'
            )
            return Response(
                data={'message': f'User {username} added to project'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                data={'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class BugViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Bug CRUD op with filtering and real-time updates
    """
    serializer_class = BugSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['status', 'project', 'priority', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet:
        """
        only return bugs from projects user has aceess to
        :return: QuerySet
        """
        user_projects = Project.objects.filter(
            models.Q(owner=self.request.user) | models.Q(members=self.request.user)
        ).distinct()
        return Bug.objects.filter(project__in=user_projects)

    def perform_create(self, serializer):
        """
        create bug with activity log and WebSocket notification
        :param serializer:
        :return:
        """
        bug = serializer.save(created_by=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            project=bug.project,
            bug=bug,
            action='created',
            description=f'Created bug: {bug.title}'
        )

        self.send_bug_notification(bug, 'bug_created')

    def perform_update(self, serializer):
        """
        update bug with change tracking and notification
        :param serializer:
        :return:
        """
        old_bug = self.get_object()
        old_status = old_bug.status
        old_assigned = old_bug.assigned_to

        bug = serializer.save()

        if old_status != bug.status:
            ActivityLog.objects.create(
                user=self.request.user,
                project=bug.project,
                bug=bug,
                action='status_changed',
                description=f'Changed status from {old_status} to {bug.status}'
            )

        if old_assigned != bug.assigned_to:
            assigned_name = bug.assigned_to.username if bug.assigned_to else 'Unassigned'
            ActivityLog.objects.create(
                user=self.request.user,
                project=bug.project,
                bug=bug,
                action='assigned',
                description=f'Assigned bug to {assigned_name}'
            )

        if old_status == bug.status and old_assigned == bug.assigned_to:
            ActivityLog.objects.create(
                user=self.request.user,
                project=bug.project,
                bug=bug,
                action='updated',
                description=f'Updated bug: {bug.title}'
            )

        self.send_bug_notification(bug, 'bug_updated')

    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        """
        get bugs assigned to current user
        :param request:
        :return:
        """
        bugs = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(bugs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_created(self, request):
        """
        get bugs created by cur user
        :param request:
        :return:
        """
        bugs = self.get_queryset().filter(created_by=request.user)
        serializer = self.get_serializer(bugs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request):
        """
        quick close bug action
        :param request:
        :return:
        """
        bug = self.get_object()
        bug.status = Bug.StatusChoice.COMPLETE
        bug.save()

        ActivityLog.objects.create(
            user=request.user,
            project=bug.project,
            bug=bug,
            action='status changed',
            description=f'Closed bug: {bug.title}'
        )

        self.send_bug_notification(bug, 'bug_closed')
        return Response(
            data={'message': 'Bug closed successfully'},
            status=status.HTTP_200_OK
        )


    def send_bug_notification(self, bug, event_type):
        """
        send websocket notification for bug change
        :param bug:
        :param event_type:
        :return:
        """
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'project_{bug.project.id}',
                {
                    'type': 'bug_notification',
                    'event_type': event_type,
                    'bug_id': bug.id,
                    'bug_title': bug.title,
                    'bug_status': bug.status,
                    'project_id': bug.project.id,
                    'user': self.request.user.username,
                    'assigned_to': bug.assigned_to.username if bug.assigned_to else None
                }
            )
        except Exception as e:
            print(f'Websocket notification failed: {e}')

class CommentViewSet(viewsets.ModelViewSet):
    """
    viewset for handling Comment CRUD operations with real-time updates
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (filters.OrderingFilter, )
    ordering = ['-created_at']

    def get_queryset(self):
        """
        filter comments by bug_id from URL and user permissions
        :return:
        """
        bug_id = self.kwargs.get('bug_pk')
        if bug_id:
            user_projects = Project.objects.filter(
                models.Q(owner=self.request.user) |
                models.Q(members=self.request.user)
            ).distinct()
            return Comment.objects.filter(
                bug_id=bug_id,
                bug__project__in=user_projects
            )
        return Comment.objects.none()

    def perform_create(self, serializer):
        """
        create comment + log + notification
        :param serializer:
        :return:
        """
        bug_id = self.kwargs.get('bug_pk')
        bug = get_object_or_404(Bug, id=bug_id)

        user_project = Project.objects.filter(
            models.Q(owner=self.request.user) |
            models.Q(members=self.request.user)
        ).distinct()

        if bug.project not in user_project:
            raise PermissionDenied('You dont have permission to comment on this bug')

        comment = serializer.save(
            bug=bug,
            commenter=self.request.user
        )

        ActivityLog.objects.create(
            user=self.request.user,
            project=bug.project,
            bug=bug,
            action='commented',
            description=f'Added comment: {comment.message[:50]}...'
        )

        self.send_comment_notification(comment)
        # Response?

    def send_comment_notification(self, comment):
        """
        send websocket notification for new comments
        :param comment:
        :return:
        """
        try:
            channel_layer = get_channel_layer()
            if channel_layer is not None:
                async_to_sync(channel_layer.group_send)(
                    f'Project_{comment.bug.project.id}',
                    {
                        'type': 'comment_notification',
                        'comment_id': comment.id,
                        'bug_id': comment.bug.id,
                        'bug_title': comment.bug.title,
                        'commenter': comment.commenter.username,
                        'message': comment.message,
                        'project_id': comment.bug.project.id,
                        'created_at': comment.created_at.isoformat()
                    }
                )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")

class DashboardStatsAPIView(APIView):
    api_name = 'v1-dashboard-stats'
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        start_time = datetime.now()
        user = request.user

        apilogger.info(
            api_name=self.api_name,
            message='Request received',
            details=request.query_params.dict(),
            user=user
        )

        try:
            stats = SummaryService().get_dashboard_stats(user)
            apilogger.info(
                api_name=self.api_name,
                message='Response generated',
                details=stats,
                user=user,
                total_time=(datetime.now() - start_time).total_seconds()
            )
            return Response(
                data=stats,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            apilogger.error(
                api_name=self.api_name,
                message='Response generated',
                details=e,
                user=user,
                total_time=(datetime.now() - start_time).total_seconds()
            )
            return Response(
                data={'detail': 'Internal Server Error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
