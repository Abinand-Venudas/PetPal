from django.core.management.base import BaseCommand
from django.utils import timezone
from volunteer.models import VolunteerAttendance, volunteer_registration


class Command(BaseCommand):
    help = "Automatically checks out all active volunteers at 10 PM"

    def handle(self, *args, **kwargs):
        now = timezone.now()

        active_attendance = VolunteerAttendance.objects.filter(
            check_out__isnull=True
        )

        count = 0
        for attendance in active_attendance:
            attendance.check_out = now
            attendance.save()

            volunteer_registration.objects.filter(
                id=attendance.volunteer_id
            ).update(is_available=False)

            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Auto checkout completed for {count} volunteers at {now.strftime('%I:%M %p')}"
            )
        )
