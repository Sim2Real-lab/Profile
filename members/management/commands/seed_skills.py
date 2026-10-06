from django.core.management.base import BaseCommand
from members.forms import seed_default_skills
from members.models import Skill

class Command(BaseCommand):
    help = 'Seed default SIG skills into database'

    def handle(self, *args, **options):
        seed_default_skills()
        count = Skill.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} skills across all SIGs.'))
