from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from tracker.models import ActivityLog
from tracker.serializers import ActivityLogDetailSerializer, ActivityLogListSerializer
from tracker.services.summary_service import SummaryService
from bugtracker.utils.logger import get_logger
from bugtracker.utils import apilogger
from bugtracker.utils.pagination import SetPagination

logger = get_logger(__name__)


class ActivityLogListApiView(APIView):
    api_name = 'v1-activity-list'
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
            queryset = SummaryService.get_user_activity_list(user)

            action = request.query_params.get('action')
            project = request.query_params.get('project')
            bug = request.query_params.get('bug')

            if action:
                queryset = queryset.filter(action=action)
            if project:
                queryset = queryset.filter(project__id=project)
            if bug:
                queryset = queryset.filter(bug__id=bug)

            queryset = queryset.order_by('-created_at')

            paginator = SetPagination()
            paginated_qs = paginator.paginate_queryset(queryset, request)
            serializer = ActivityLogListSerializer(paginated_qs, many=True)

            apilogger.info(
                api_name=self.api_name,
                message='Response generated',
                details=serializer.data,
                user=user,
                total_time=(datetime.now() - start_time).total_seconds()
            )

            return paginator.get_paginated_response(serializer.data)

        except PermissionDenied as perm_err:
            logger.warning(f'Unauthorized access from user-{user}. Error: {perm_err}')
            apilogger.info(
                api_name=self.api_name,
                message='Response generated',
                details=f'Unauthorized access from user-{user}: {perm_err}',
                user=user,
                total_time=(datetime.now() - start_time).total_seconds()
            )
            return Response(
                data={
                    'detail': 'You do not have permission to access activities'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            logger.error(f'Unexpected error in activity list: {e}')
            apilogger.error(
                api_name=self.api_name,
                message='Response generated',
                details=str(e),
                user=user,
                total_time=(datetime.now() - start_time).total_seconds()
            )
            return Response(
                data={'detail': f'Unexpected error: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ActivityLogDetailApiView(APIView):
    api_name = 'v1-activity-detail'
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        start_time = datetime.now()
        user = request.user

        apilogger.info(
            api_name=self.api_name,
            message='Request received',
            details=request.query_params.dict(),
            user=user
        )

        try:
            activity = SummaryService.get_user_activity(user, pk)
        except PermissionDenied as perm_err:
            logger.warning(f'Unauthorized access from user-{user}. Error: {perm_err}')
            apilogger.info(
                api_name=self.api_name,
                message='Response generated',
                details=f'Unauthorized access from user-{user}: {perm_err}',
                user=user,
                total_time=(datetime.now() - start_time).total_seconds()
            )
            return Response(
                data={
                    'detail': 'You do not have permission to access this activity'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except ActivityLog.DoesNotExist:
            apilogger.warn(
                api_name=self.api_name,
                message='Response generated',
                details=f'Activity-{pk} not found',
                user=user,
                total_time=(datetime.now() - start_time).total_seconds()
            )
            return Response(
                {'detail': 'Activity not found'},
                status=status.HTTP_404_NOT_FOUND
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
                {'detail': 'Could not retrieve activity'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            data = ActivityLogDetailSerializer(activity).data
            apilogger.info(
                api_name=self.api_name,
                message='Response generated',
                details=data,
                user=user,
                total_time=(datetime.now() - start_time).total_seconds()
            )
            return Response(
                data=data,
                status=status.HTTP_200_OK
            )