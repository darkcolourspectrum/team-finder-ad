import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project, Skill


def project_list_view(request):
    projects = Project.objects.select_related("owner").prefetch_related(
        "participants"
    )
    all_skills = Skill.objects.order_by("name").values_list("name", flat=True)
    active_skill = request.GET.get("skill", "").strip()

    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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
    if request.method == "POST":
        form = ProjectForm(request.POST)
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
    form = ProjectForm()
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", project_id=project.pk)
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True},
        )
    form = ProjectForm(instance=project)
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
            {"status": "error", "detail": "Forbidden"}, status=403
        )
    if project.status != "open":
        return JsonResponse(
            {"status": "error", "detail": "Already closed"}, status=400
        )
    project.status = "closed"
    project.save()
    return JsonResponse({"status": "ok", "project_status": "closed"})


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
            status=400,
        )
    if user in project.participants.all():
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
    if project in user.favorites.all():
        user.favorites.remove(project)
        favorited = False
    else:
        user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


def skills_autocomplete_view(request):
    q = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__istartswith=q).order_by("name")[:10]
    data = [{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "detail": "Forbidden"}, status=403
        )

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"status": "error", "detail": "Invalid JSON"}, status=400
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
            status=400,
        )

    added = skill not in project.skills.all()
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
            {"status": "error", "detail": "Forbidden"}, status=403
        )
    skill = get_object_or_404(Skill, pk=skill_id)
    if skill not in project.skills.all():
        return JsonResponse(
            {"status": "error", "detail": "Skill not in project"}, status=400
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
