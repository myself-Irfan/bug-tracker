from typing import cast

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status, filters
from django.utils import timezone

from bugtracker.utils import apilogger
from bugtracker.utils.logger import get_logger
from tracker.serializers import ProjectSerializer
from tracker.services.project_service import ProjectService


logger = get_logger(__name__)


class ProjectViewSet(ModelViewSet):
    """
    ViewSet for handling Project CRUD operations with proper permissions
    """
    api_name = 'v1-project'
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['name', 'description']

    def _log_api_request(self, message, details):
        apilogger.info(
            api_name=self.api_name,
            message=message,
            details=details,
            user=self.authenticated_user
        )

    def _log_api_response(self, details):
        start_time = getattr(self.request, "_start_time", timezone.now())
        apilogger.info(
            api_name=self.api_name,
            message='Response generated',
            details=details,
            user=self.authenticated_user,
            total_time=(timezone.now() - start_time).total_seconds()
        )

    @property
    def authenticated_user(self) -> User:
        """Get the authenticated user (guaranteed by IsAuthenticated)"""
        return cast(User, self.request.user)

    def get_queryset(self) -> QuerySet:
        """
        return projects accessible to current user
        """
        return ProjectService.get_project_list(self.authenticated_user)

    def list(self, request, *args, **kwargs) -> Response:
        """
        get request for all project(s) accessible to user
        """
        self._log_api_request('Request received', request.query_params.dict())

        queryset = self.filter_queryset(self.get_queryset())

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
        self._log_api_response(f'{queryset.count()} projects retrieved')
        return Response({
            'message': 'Project list retrieved',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs) -> Response:
        """
        create a project using post method
        """
        self._log_api_request(
            "Request received",
            request.data
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.create_project(
            serializer.validated_data,
            self.authenticated_user
        )
        serializer.instance = project

        self._log_api_response(f"Project: {project.name} created successfully by User: {request.user}")
        return Response(
            {
                'message': 'Project created successfully',
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs) -> Response:
        project_id = kwargs.get('pk')
        self._log_api_request("Request (GET) received", project_id)

        project = ProjectService.get_project_by_id(
            request.user,
            project_id
        )
        serializer = self.get_serializer(project)

        self._log_api_response('Project retrieved successfully')
        return Response(
            data={
                "message": "Project retrieved successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def _update_project(self, request, *args, partial=False, **kwargs):
        """
        common logic for PUT and PATCH
        """
        project_id = kwargs.get('pk')

        self._log_api_request(
            f'Request received {'PATCH' if partial else 'PUT'}',
            request.data
        )

        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.update_project(
            request.user,
            project_id,
            serializer.validated_data
        )
        serializer.instance = project

        self._log_api_response(f'Project-{project.pk} updated by {request.user}')
        return Response(
            data={
            "message": f'Project-{project.pk} updated by {request.user}',
            "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        return self._update_project(
            request,
            *args,
            partial=False,
            **kwargs
        )

    def partial_update(self, request, *args, **kwargs):
        return self._update_project(
            request,
            *args,
            partial=True,
            **kwargs
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete project
        """
        project_id = kwargs.get('pk')
        self._log_api_request('Request received', project_id)

        ProjectService.delete_project(
            request.user,
            project_id
        )

        self._log_api_response(
            f'Project deleted by {request.user}'
        )
        return Response(
            data={
                "message": f"Project-{project_id} deleted successfully",
            },
            status=status.HTTP_204_NO_CONTENT
        )