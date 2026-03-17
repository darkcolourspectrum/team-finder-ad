import io
import random

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


AVATAR_COLORS = [
    "#5B8CFF",
    "#FF7B7B",
    "#6BCB77",
    "#FFD166",
    "#A78BFA",
    "#F97316",
    "#06B6D4",
    "#EC4899",
    "#84CC16",
    "#FB923C",
]


def generate_avatar(letter: str) -> ContentFile:
    """Generate a simple avatar image with the first letter of the user's name."""
    size = 200
    color = random.choice(AVATAR_COLORS)

    img = Image.new("RGB", (size, size), color=color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
    except OSError:
        font = ImageFont.load_default()

    text = letter.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) / 2 - bbox[0]
    y = (size - text_height) / 2 - bbox[1]
    draw.text((x, y), text, fill="white", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=12, blank=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Generate avatar on first save if not provided
        if not self.pk and not self.avatar:
            letter = self.name[0] if self.name else "U"
            avatar_content = generate_avatar(letter)
            filename = f"avatar_{self.email.split('@')[0]}.png"
            self.avatar.save(filename, avatar_content, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
