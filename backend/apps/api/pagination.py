from rest_framework import pagination

from foodgram.settings import ITEMS_ON_PAGE


class Pagination(pagination.PageNumberPagination):
    """Класс пагинации страниц."""

    page_size = ITEMS_ON_PAGE
    max_page_size = ITEMS_ON_PAGE
    page_size_query_param = 'limit'
