from django.core.paginator import Paginator

from constants import PROJECTS_PER_PAGE


def paginate(queryset, page_number):
    paginator = Paginator(queryset, PROJECTS_PER_PAGE)
    return paginator.get_page(page_number)
