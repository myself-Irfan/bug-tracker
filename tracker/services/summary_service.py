from django.db import models
from django.db.models import QuerySet
from django.core.exceptions import PermissionDenied

from tracker.models import Project, Bug, ActivityLog


class SummaryService:
    @classmethod
    def get_user_projects(cls, user) -> QuerySet:
        """
        get all projects the user owns or is a member of
        :param user: auth user
        :return: QuerySet: projects user has access to
        """
        if not user or not user.is_authenticated:
            raise PermissionDenied('Authentication required')

        return Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()

    @classmethod
    def get_user_activity_list(cls, user) -> QuerySet:
        user_projects = cls.get_user_projects(user)

        if not user_projects.exists():
            raise PermissionDenied('No accessible project found')

        return ActivityLog.objects.select_related(
            'project', 'bug', 'user'
        ).filter(
            project__in=user_projects
        )

    @classmethod
    def get_user_activity(cls, user, activity_id) -> ActivityLog:
        """
        get specific activity log if user has access
        :param user: auth_user
        :param activity_id: pk of activitylog
        :return: QuerySet:
        """
        if not user or not user.is_authenticated:
            raise PermissionDenied('Authentication required')

        user_projects = cls.get_user_projects(user)

        if not user_projects.exists():
            raise PermissionDenied("No accessible projects found")

        if not ActivityLog.objects.filter(pk=activity_id).exists():
            raise ActivityLog.DoesNotExist(f"Activity-{activity_id} not found")

        try:
            return ActivityLog.objects.select_related(
                'project', 'bug', 'user'
            ).get(
                pk=activity_id,
                project__in=user_projects
            )
        except ActivityLog.DoesNotExist:
            raise PermissionDenied("You do not have permission to access this activity")

    @classmethod
    def get_dashboard_stats(cls, user):
        user_projects = cls.get_user_projects(user)
        bugs = Bug.objects.filter(project__in=user_projects)

        return {
            'total_projects': user_projects.count(),
            'total_bugs': bugs.count(),
            'assigned_to_me': bugs.filter(assigned_to=user).count(),
            'created_by_me': bugs.filter(created_by=user).count(),
            'open_bugs': bugs.filter(status=Bug.StatusChoice.OPEN).count(),
            'in_progress_bugs': bugs.filter(status=Bug.StatusChoice.IN_PROGRESS).count(),
            'complete_bugs': bugs.filter(status=Bug.StatusChoice.COMPLETE).count(),
        }