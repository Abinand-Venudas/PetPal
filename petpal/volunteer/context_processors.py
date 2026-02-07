from .models import VolunteerNotification

def notification_count(request):
    volunteer_id = request.session.get("volunteer_id")

    if volunteer_id:
        count = VolunteerNotification.objects.filter(
            volunteer_id=volunteer_id,
            is_read=False
        ).count()
    else:
        count = 0

    return {"notification_count": count}
