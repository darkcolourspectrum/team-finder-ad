from django import forms

from projects.models import Project
from validators import validate_github_url


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
