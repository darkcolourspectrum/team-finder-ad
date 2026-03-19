import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from constants import (
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    SKILLS_AUTOCOMPLETE_LIMIT
)
from .forms import ProjectForm
from .models import Project, Skill
from service import paginate


def project_list_view(request):
    projects = Project.objects.select_related("owner").prefetch_related(
        "participants"
    )
    all_skills = Skill.objects.order_by("name").values_list("name", flat=True)
    active_skill = request.GET.get("skill", "").strip()

    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    page_obj = paginate(projects, request)

    return render(request, "projects/project_list.html", {
        "projects": page_obj,
        "all_skills": all_skills,
        "active_skill": active_skill,
    })


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related(
            "participants", "skills"
        ),
        pk=project_id,
    )
    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.pk)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", project_id=project.pk)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "detail": "Forbidden"},
            status=HTTPStatus.FORBIDDEN,
        )
    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "detail": "Already closed"},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = PROJECT_STATUS_CLOSED
    project.save()
    return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if project.owner == user:
        return JsonResponse(
            {
                "status": "error",
                "detail": "Owner cannot toggle participate",
            },
            status=HTTPStatus.BAD_REQUEST,
        )
    if project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
        participating = False
    else:
        project.participants.add(user)
        participating = True
    return JsonResponse({"status": "ok", "participant": participating})


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if user.favorites.filter(pk=project.pk).exists():
        user.favorites.remove(project)
        favorited = False
    else:
        user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


def skills_autocomplete_view(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(
        name__istartswith=query
    ).order_by("name")[:SKILLS_AUTOCOMPLETE_LIMIT]
    data = [{"id": skill.id, "name": skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "detail": "Forbidden"},
            status=HTTPStatus.FORBIDDEN,
        )

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"status": "error", "detail": "Invalid JSON"},
            status=HTTPStatus.BAD_REQUEST,
        )

    skill_id = body.get("skill_id")
    name = body.get("name", "").strip()

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        created = False
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse(
            {"status": "error", "detail": "skill_id or name required"},
            status=HTTPStatus.BAD_REQUEST,
        )

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse(
        {
            "id": skill.id, "name": skill.name,
            "created": created, "added": added,
        }
    )


@login_required
@require_POST
def remove_skill_view(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "detail": "Forbidden"},
            status=HTTPStatus.FORBIDDEN,
        )
    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {"status": "error", "detail": "Skill not in project"},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})


@login_required
def favorites_view(request):
    projects = request.user.favorites.all().order_by("-created_at")
    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": projects},
    )
