from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    STATUS_CHOICES_RU = [
        ("open", "Открыт"),
        ("closed", "Закрыт"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES_RU,
        label="Статус",
    )

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url and "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return url
