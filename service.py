from django.core.paginator import Paginator

from constants import PROJECTS_PER_PAGE


def paginate(queryset, request):
    paginator = Paginator(queryset, PROJECTS_PER_PAGE)
    return paginator.get_page(request.GET.get("page"))
