from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Класс пагинации."""

    page_size_query_param = "limit"
    max_page_size = 100
    page_size = 6
