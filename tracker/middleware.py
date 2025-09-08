from django.utils import timezone

class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request._start_time = timezone.now()
        response = self.get_response(request)
        return response