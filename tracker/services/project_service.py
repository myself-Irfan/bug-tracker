from django.db import models
from django.db.models import QuerySet, Q

from bugtracker.utils.logger import get_logger
from tracker.models import Project, ActivityLog, User
from tracker.exceptions.project_exceptions import ProjectNotFoundError, ProjectAccessDeniedError, ProjectUpdateError, ProjectCreationError, ProjectDeletionError


logger = get_logger(__name__)

class ProjectService:
    @staticmethod
    def get_project_list(request_user: User) -> QuerySet:
        qs = Project.objects.filter(
            models.Q(owner=request_user) | models.Q(members=request_user)
        ).distinct().select_related('owner').prefetch_related('members')

        return qs.order_by("-created_at")

    @staticmethod
    def create_project(validated_data: dict, request_user: User) -> Project:
        try:
            project = Project.objects.create(
                owner=request_user,
                **validated_data
            )
        except Exception as err:
            logger.error(
                f"Failed to create project | {err}"
            )
            raise ProjectCreationError(
                message="Failed to create project",
                details=str(err)
            )
        else:
            ActivityLog.objects.create(
                user=request_user,
                project=project,
                action='created',
                description=f"Created project: {project.name}"
            )

            return project
        
    @staticmethod
    def get_project_by_id(request_user: User, project_id: int) -> Project:
        try:
            project: Project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise ProjectNotFoundError(
                message=f"Project-{project_id} not found",
                details=f"Project-{project_id} does not exist"
            )
        else:
            has_access = project.owner == request_user or request_user in project.members.all()
            if not has_access:
                raise ProjectAccessDeniedError(
                    message=f"Permission denied for project-{project_id}",
                    details=f"User-{request_user.username} does not have access to project-{project_id}"
                )
            return project

    @staticmethod
    def update_project(request_user: User, project_id: int, validated_data: dict) -> Project:
        project = ProjectService.get_project_by_id(request_user, project_id)

        original_name = project.name
        changes = []

        try:
            for key, value in validated_data.items():
                old_value = getattr(project, key, None)
                if old_value != value:
                    setattr(project, key, value)
                    changes.append(f"{key}: {old_value} -> {value}")
            project.save()
        except Exception as err:
            logger.error(f'Failed to update project-{project.pk} | {err}')
            raise ProjectUpdateError(
                message=f"Failed to update project-{project.pk}",
                details=str(err)
            )
        else:
            if changes:
                ActivityLog.objects.create(
                    user=request_user,
                    project=project,
                    action='updated',
                    description=f"Updated project '{original_name}': {', '.join(changes)}"
                )
            return project

    @staticmethod
    def delete_project(request_user: User, project_id: int) -> None:
        if not project_id:
            logger.warning('Project ID not provided')
            raise ProjectNotFoundError(
                message='Project ID is required',
                details='No project id provided'
            )

        project = ProjectService.get_project_by_id(request_user, project_id)

        if project.owner != request_user:
            raise ProjectAccessDeniedError(
                message=f"Permission denied for project-{project_id}",
                details=f"Only project owner can delete project-{project_id}"
            )

        try:
            ActivityLog.objects.create(
                user=request_user,
                project=project,
                action='deleted',
                description=f"Deleted project: {project_id}"
            )
            project.delete()
        except Exception as err:
            logger.error(f'Failed to delete project-{project_id} | {err}')
            raise ProjectDeletionError(
                message=f"Failed to delete project-{project_id}",
                details=str(err)
            )