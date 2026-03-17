from django import forms

from .models import Project

GITHUB_DOMAIN = "github.com"


def validate_github_url(url):
    if url and GITHUB_DOMAIN not in url:
        raise forms.ValidationError("Ссылка должна вести на GitHub")
    return url


class ProjectForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=Project.STATUS_CHOICES,
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
        return validate_github_url(url)
