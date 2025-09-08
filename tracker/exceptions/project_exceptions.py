from rest_framework.exceptions import APIException
from rest_framework import status


class ProjectServiceException(APIException):
    """
    Base exception for project service errors
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A service error occurred.'
    default_code = 'service_error'

    def __init__(self, message: str = None, details: str = None, status_code: int = None):
        self.message = message or str(self.default_detail)
        self.details = details

        if status_code:
            self.status_code = status_code

        super().__init__(detail=self.message, code=self.default_code)

class ProjectNotFoundError(ProjectServiceException):
    """
    Raised when a project is not found
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Project not found.'
    default_code = 'project_not_found'

class ProjectAccessDeniedError(ProjectServiceException):
    """
    Raised when user doesn't have access to a project
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied for requested project.'
    default_code = 'project_access_denied'

class ProjectCreationError(ProjectServiceException):
    """
    Raised when project creation fails
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to create project.'
    default_code = 'project_creation_error'


class ProjectUpdateError(ProjectServiceException):
    """
    Raised when project update fails
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to update project.'
    default_code = 'project_update_error'


class ProjectDeletionError(ProjectServiceException):
    """
    Raised when project deletion fails
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to delete project.'
    default_code = 'project_deletion_error'