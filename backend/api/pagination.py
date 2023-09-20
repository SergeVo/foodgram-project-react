from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Класс пагинации."""

    page_size_query_param = "limit"
