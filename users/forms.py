import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from constants import NAME_MAX_LENGTH, SURNAME_MAX_LENGTH
from projects.forms import validate_github_url
from users.service import normalize_phone

User = get_user_model()


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=NAME_MAX_LENGTH, label="Имя")
    surname = forms.CharField(max_length=SURNAME_MAX_LENGTH, label="Фамилия")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


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
            "avatar": forms.FileInput(),
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

        qs = User.objects.filter(phone=normalized)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Этот номер телефона уже используется другим пользователем."
            )

        return normalized

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        return validate_github_url(url)


class UserPasswordChangeForm(PasswordChangeForm):
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
