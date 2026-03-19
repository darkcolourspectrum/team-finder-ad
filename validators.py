from django import forms

GITHUB_DOMAIN = "github.com"


def validate_github_url(url):
    if url and GITHUB_DOMAIN not in url:
        raise forms.ValidationError("Ссылка должна вести на GitHub")
    return url
