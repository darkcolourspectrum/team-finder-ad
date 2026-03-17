from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project, Skill

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей и проекты"

    def handle(self, *args, **kwargs):
        if User.objects.filter(email="alice@example.com").exists():
            self.stdout.write("Тестовые данные уже существуют, пропускаем.")
            return

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

        skill_python = Skill.objects.get_or_create(name="Python")[0]
        skill_react = Skill.objects.get_or_create(name="React")[0]
        skill_django = Skill.objects.get_or_create(name="Django")[0]
        skill_figma = Skill.objects.get_or_create(name="Figma")[0]
        skill_typescript = Skill.objects.get_or_create(name="TypeScript")[0]

        task_tracker = Project.objects.create(
            name="Трекер задач",
            description="Простое приложение для отслеживания задач в команде.",
            owner=alice,
            github_url="https://github.com/alice/task-tracker",
            status="open",
        )
        task_tracker.skills.set([skill_python, skill_django])
        task_tracker.participants.add(alice)

        portfolio_generator = Project.objects.create(
            name="Портфолио-генератор",
            description="Сервис для автоматической генерации красивых портфолио по GitHub профилю.",
            owner=bob,
            github_url="https://github.com/bob/portfolio-gen",
            status="open",
        )
        portfolio_generator.skills.set([skill_react, skill_typescript])
        portfolio_generator.participants.add(bob)

        design_system = Project.objects.create(
            name="Дизайн-система",
            description="Набор UI-компонентов и гайдлайнов для командной разработки.",
            owner=carol,
            status="open",
        )
        design_system.skills.set([skill_figma, skill_react])
        design_system.participants.add(carol)

        self.stdout.write(self.style.SUCCESS(
            "Тестовые данные созданы: 3 пользователя, 3 проекта."
        ))
