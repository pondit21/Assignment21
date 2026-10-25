from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Category, Comment, Education, Experience, Post, Profile, Project, Skill, Tag


class Command(BaseCommand):
    help = 'Seed demo portfolio data for the assignment.'

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True})
        if not user.check_password('admin123'):
            user.set_password('admin123')
            user.save()

        profile, _ = Profile.objects.get_or_create(user=user, defaults={
            'full_name': 'Rifat Hasan',
            'headline': 'Full-stack developer',
            'bio': 'I build modern web apps with Django and React.',
            'email': 'admin@example.com',
            'phone': '+123456789',
            'location': 'Dhaka, Bangladesh',
            'github_url': 'https://github.com',
            'linkedin_url': 'https://linkedin.com',
            'website_url': 'https://example.com',
            'is_available_for_hire': True,
        })

        for skill_name, category, proficiency, order in [
            ('Django', 'BACKEND', 95, 1),
            ('Django REST Framework', 'BACKEND', 94, 2),
            ('React', 'FRONTEND', 90, 3),
            ('TypeScript', 'FRONTEND', 82, 4),
            ('PostgreSQL', 'DATABASE', 88, 5),
            ('Docker', 'TOOLS', 70, 6),
        ]:
            Skill.objects.get_or_create(owner=user, name=skill_name, defaults={'category': category, 'proficiency': proficiency, 'display_order': order})

        for company, role, start, end, desc in [
            ('Acme Labs', 'Senior Django Engineer', date(2022, 1, 1), None, 'Built APIs and dashboards for cloud products.'),
            ('Open Source', 'Frontend Engineer', date(2020, 4, 1), date(2021, 12, 31), 'Improved UI and product flows.')
        ]:
            Experience.objects.get_or_create(owner=user, company=company, role=role, defaults={'location': 'Remote', 'start_date': start, 'end_date': end, 'is_current': end is None, 'description': desc})

        Education.objects.get_or_create(owner=user, institution='University of Dhaka', degree='B.Sc. in Computer Science', defaults={'field_of_study': 'Software Engineering', 'start_year': 2014, 'end_year': 2018, 'grade': '3.80'})

        category_blog, _ = Category.objects.get_or_create(name='Web Development', slug='web-development', defaults={'description': 'Website and app notes.'})
        category_project, _ = Category.objects.get_or_create(name='Portfolio', slug='portfolio', defaults={'description': 'Portfolio work.'})
        tag_1, _ = Tag.objects.get_or_create(name='Django', slug='django')
        tag_2, _ = Tag.objects.get_or_create(name='React', slug='react')

        project = Project.objects.get_or_create(
            owner=user,
            slug='portfolio-site',
            defaults={
                'title': 'Portfolio Site',
                'summary': 'A personal portfolio and blog built with Django and React.',
                'description': 'A portfolio site with blog, project showcase, and contact form.',
                'live_url': 'https://example.com',
                'github_url': 'https://github.com',
                'category': 'Portfolio',
                'completed_date': date(2025, 1, 1),
                'display_order': 1,
            },
        )[0]
        project.tags.set([tag_1, tag_2])

        for idx, title in enumerate(['First Post', 'Second Post']):
            post, created = Post.objects.get_or_create(
                author=user,
                slug=f'post-{idx + 1}',
                defaults={
                    'title': title,
                    'excerpt': 'Example article',
                    'content': 'This is seeded content for a portfolio blog. You can edit it later from the dashboard.',
                    'status': 'PUBLISHED',
                    'published_at': timezone.now(),
                    'reading_time': 5,
                    'category': category_blog,
                },
            )
            post.tags.set([tag_1, tag_2])
            Comment.objects.get_or_create(
                post=post,
                name='Visitor',
                email='visitor@example.com',
                content='Nice article.',
                defaults={'is_approved': True},
            )

        self.stdout.write(self.style.SUCCESS('Seed data created successfully.'))
