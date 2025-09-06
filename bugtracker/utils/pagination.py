from rest_framework.pagination import PageNumberPagination

from django.conf import settings

class SetPagination(PageNumberPagination):
    page_size = settings.DEFAULT_PAGE_NUMBER
    page_size_query_param = 'page_size'
    max_page_size = settings.MAX_PAGE_NUMBER