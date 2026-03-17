import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=124, label="Имя")
    surname = forms.CharField(max_length=124, label="Фамилия")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


def normalize_phone(phone: str) -> str:
    """Normalize phone: 8XXXXXXXXXX -> +7XXXXXXXXXX"""
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "Ссылка на GitHub",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone

        pattern_8 = r"^8\d{10}$"
        pattern_7 = r"^\+7\d{10}$"
        if not re.match(pattern_8, phone) and not re.match(pattern_7, phone):
            raise forms.ValidationError(
                "Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
            )

        normalized = normalize_phone(phone)

        # Check uniqueness excluding current user
        qs = User.objects.filter(phone__in=[normalized, phone])
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        # Also check the alternative format
        alt = phone if normalized != phone else ("8" + phone[2:] if phone.startswith("+7") else phone)
        qs2 = User.objects.filter(phone=normalized)
        if self.instance and self.instance.pk:
            qs2 = qs2.exclude(pk=self.instance.pk)
        if qs2.exists():
            raise forms.ValidationError("Этот номер телефона уже используется другим пользователем.")

        return normalized

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url and "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на GitHub (github.com).")
        return url


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput,
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput,
    )
