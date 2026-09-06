from django.core.management.base import BaseCommand

from apps.training.models import TrainingModule


DEMO_MODULES = (
    {
        'module_id': 'demo-python-foundations',
        'title': 'Python Foundations for Business Applications',
        'category': 'python',
        'difficulty': 'beginner',
        'duration_minutes': 180,
        'description': 'Core Python syntax, data structures, and practical automation exercises.',
    },
    {
        'module_id': 'demo-sql-essentials',
        'title': 'SQL Essentials',
        'category': 'sql',
        'difficulty': 'beginner',
        'duration_minutes': 150,
        'description': 'Querying, joins, filtering, and aggregating business data.',
    },
    {
        'module_id': 'demo-communication',
        'title': 'Effective Workplace Communication',
        'category': 'communication',
        'difficulty': 'beginner',
        'duration_minutes': 90,
        'description': 'Clear written communication, feedback, and productive meetings.',
    },
    {
        'module_id': 'demo-soft-skills',
        'title': 'Collaboration and Professional Effectiveness',
        'category': 'soft_skills',
        'difficulty': 'intermediate',
        'duration_minutes': 120,
        'description': 'Teamwork, stakeholder management, and conflict resolution.',
    },
    {
        'module_id': 'demo-project-management',
        'title': 'Project Management Fundamentals',
        'category': 'project_management',
        'difficulty': 'beginner',
        'duration_minutes': 180,
        'description': 'Planning, prioritisation, risk management, and delivery tracking.',
    },
    {
        'module_id': 'demo-data-analysis',
        'title': 'Practical Data Analysis',
        'category': 'data_analysis',
        'difficulty': 'intermediate',
        'duration_minutes': 210,
        'description': 'Exploring data, interpreting metrics, and presenting useful insights.',
    },
    {
        'module_id': 'demo-problem-solving',
        'title': 'Structured Problem Solving',
        'category': 'problem_solving',
        'difficulty': 'intermediate',
        'duration_minutes': 120,
        'description': 'Root-cause analysis, decision-making frameworks, and experimentation.',
    },
    {
        'module_id': 'demo-system-design',
        'title': 'System Design Patterns',
        'category': 'technical',
        'difficulty': 'advanced',
        'duration_minutes': 240,
        'description': 'Scalable systems, reliability patterns, and architecture trade-offs.',
    },
)


class Command(BaseCommand):
    help = 'Create the idempotent demo training catalog used in local development.'

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        for module_data in DEMO_MODULES:
            if TrainingModule.objects(module_id=module_data['module_id']).first():
                skipped += 1
                continue
            TrainingModule(**module_data).save()
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Demo catalog ready: {created} created, {skipped} already present.'
            )
        )
