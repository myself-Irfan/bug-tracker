from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project"
        verbose_name_plural = f"{verbose_name}s"

    # TODO: bug count? open bug count?

class Bug(models.Model):
    class StatusChoice(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETE = 'COMPLETE', _('Complete')

    class PriorityChoice(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        CRITICAL = 'CRITICAL', _('Critical')

    title = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.OPEN, db_index=True)
    priority = models.CharField(max_length=20, choices=PriorityChoice.choices, default=PriorityChoice.LOW, db_index=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bugs')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='bugs')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bugs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.project.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bug"
        verbose_name_plural = f"{verbose_name}s"

class Comment(models.Model):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.commenter.username} on {self.bug.title}"

    class Meta:
        ordering = ['created_at']
        verbose_name = "Comment"
        verbose_name_plural = f"{verbose_name}s"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    bug = models.ForeignKey(Bug, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "ActivityLog"
        verbose_name_plural = f"{verbose_name}s"

class ApiLog(models.Model):
    class LevelChoice(models.TextChoices):
        INFO = 'INFO', _('Info')
        WARN = 'WARN', _('Warn')
        ERROR = 'ERROR', _('Error')
        FATAL = 'FATAL', _('Fatal')

    api_name = models.CharField(max_length=100)
    level = models.CharField(max_length=10, choices=LevelChoice.choices, db_index=True)
    message = models.CharField(max_length=1000, null=True)
    details = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_time = models.FloatField(null=True, blank=True)