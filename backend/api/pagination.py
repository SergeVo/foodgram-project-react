from rest_framework.pagination import PageNumberPagination

from common.constants import MAX_PAGE


class CustomPagination(PageNumberPagination):
    page_size = MAX_PAGE
    page_size_query_param = 'limit'
