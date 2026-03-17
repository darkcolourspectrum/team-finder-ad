from django.contrib.auth import (
    authenticate, get_user_model, login, logout, update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CustomPasswordChangeForm, EditProfileForm, LoginForm, RegisterForm,
)

User = get_user_model()


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                email=form.cleaned_data["email"],
                name=form.cleaned_data["name"],
                surname=form.cleaned_data["surname"],
                password=form.cleaned_data["password"],
            )
            return redirect("users:login")
        return render(request, "users/register.html", {"form": form})
    form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("projects:list")
            form.add_error(None, "Неверный email или пароль")
        return render(request, "users/login.html", {"form": form})
    form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user
        )
        if form.is_valid():
            form.save()
            return redirect("users:detail", user_id=request.user.pk)
        return render(request, "users/edit_profile.html", {"form": form})
    form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.pk)
        return render(
            request, "users/change_password.html", {"form": form}
        )
    form = CustomPasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def participants_view(request):
    users_qs = User.objects.order_by("-id")
    paginator = Paginator(users_qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "users/participants.html",
        {"participants": page_obj},
    )
