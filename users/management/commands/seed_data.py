from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project, Skill

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей и проекты"

    def handle(self, *args, **kwargs):
        if User.objects.filter(email="alice@example.com").exists():
            self.stdout.write("Тестовые данные уже существуют, пропускаем.")
            return

        # Пользователи
        alice = User.objects.create_user(
            email="alice@example.com",
            name="Алиса",
            surname="Иванова",
            password="testpass123",
            about="Фронтенд-разработчик, люблю React и TypeScript.",
            github_url="https://github.com/alice",
        )
        bob = User.objects.create_user(
            email="bob@example.com",
            name="Борис",
            surname="Петров",
            password="testpass123",
            about="Бэкенд-разработчик, Python/Django.",
            github_url="https://github.com/bob",
        )
        carol = User.objects.create_user(
            email="carol@example.com",
            name="Карина",
            surname="Смирнова",
            password="testpass123",
            about="UI/UX дизайнер.",
        )

        # Навыки
        python = Skill.objects.get_or_create(name="Python")[0]
        react = Skill.objects.get_or_create(name="React")[0]
        django = Skill.objects.get_or_create(name="Django")[0]
        figma = Skill.objects.get_or_create(name="Figma")[0]
        typescript = Skill.objects.get_or_create(name="TypeScript")[0]

        # Проекты
        p1 = Project.objects.create(
            name="Трекер задач",
            description="Простое приложение для отслеживания задач в команде.",
            owner=alice,
            github_url="https://github.com/alice/task-tracker",
            status="open",
        )
        p1.skills.set([python, django])
        p1.participants.add(alice)

        p2 = Project.objects.create(
            name="Портфолио-генератор",
            description="Сервис для автоматической генерации красивых портфолио по GitHub профилю.",
            owner=bob,
            github_url="https://github.com/bob/portfolio-gen",
            status="open",
        )
        p2.skills.set([react, typescript])
        p2.participants.add(bob)

        p3 = Project.objects.create(
            name="Дизайн-система",
            description="Набор UI-компонентов и гайдлайнов для командной разработки.",
            owner=carol,
            status="open",
        )
        p3.skills.set([figma, react])
        p3.participants.add(carol)

        self.stdout.write(self.style.SUCCESS(
            "Тестовые данные созданы: 3 пользователя, 3 проекта."
        ))