import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from tracker.models import Project


class BugTrackerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.project_group_name = f'project_{self.project_id}'

        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return

        has_permission = await self.check_project_permission(user, self.project_id)
        if not has_permission:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.project_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.project_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            if message_type == 'typing_indicator':
                await self.channel_layer.group_send(
                    self.project_group_name,
                    {
                        'type': 'typing_indicator',
                        'user': self.scope.get('user').username,
                        'bug_id': text_data_json.get('bug_id'),
                        'is_typing': text_data_json.get('is_typing', False)
                    }
                )
        except json.JSONDecodeError:
            pass

    async def bug_notification(self, event):
        await self.send(
            text_data=json.dumps({
                'type': 'bug_notification',
                'event_type': event.get('event_type'),
                'bug_id': event.get('bug_id'),
                'bug_title': event.get('bug_title'),
                'bug_status': event.get('bug_status'),
                'project_id': event.get('project_id'),
                'user': event.get('user')
            })
        )

    async def typing_indicator(self, event):
        await self.send(
            text_data=json.dumps({
                'type': 'typing_indicator',
                'user': event['user'],
                'bug_id': event['bug_id'],
                'is_typing': event['is_typing']
            })
        )

    async def activity_log(self, event):
        await self.send(
            text_data=json.dumps({
                'type': 'activity_log',
                'activity': event['activity']
            })
        )

    @database_sync_to_async
    def check_project_permission(self, user, project_id):
        try:
            project = Project.objects.get(id=project_id)
            return project.owner == user or user in project.members.all()
        except Project.DoesNotExist:
            return False