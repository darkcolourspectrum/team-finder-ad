import io
import random

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from constants import (
    ABOUT_MAX_LENGTH,
    AVATAR_FONT_SIZE,
    AVATAR_COLORS,
    AVATAR_SIZE,
    NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
)

from users.managers import UserManager


def generate_avatar(letter: str) -> ContentFile:
    size = AVATAR_SIZE
    color = random.choice(AVATAR_COLORS)

    img = Image.new("RGB", (size, size), color=color)
    draw = ImageDraw.Draw(img)

    font = None
    font_size = AVATAR_FONT_SIZE

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            font_size,
        )
    except OSError:
        pass

    if font is None:
        try:
            import ctypes.util
            win_font = ctypes.util.find_library("arial")
            if win_font:
                font = ImageFont.truetype(win_font, font_size)
        except Exception:
            pass

    if font is None:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            pass

    if font is None:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except OSError:
            pass

    if font is None:
        font = ImageFont.load_default(size=font_size)

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


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Имя",
    )
    surname = models.CharField(
        max_length=SURNAME_MAX_LENGTH,
        verbose_name="Фамилия",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        verbose_name="Аватар",
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        verbose_name="Телефон",
    )
    github_url = models.URLField(
        blank=True,
        verbose_name="GitHub",
    )
    about = models.TextField(
        max_length=ABOUT_MAX_LENGTH,
        blank=True,
        verbose_name="О себе",
    )
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Администратор",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            letter = self.name[0] if self.name else "U"
            avatar_content = generate_avatar(letter)
            filename = f"avatar_{self.email.split('@')[0]}.png"
            self.avatar.save(filename, avatar_content, save=False)
        super().save(*args, **kwargs)
