from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from .models import volunteer_registration, VolunteerAttendance
from .models import (
    volunteer_registration,
    VolunteerAttendance,
    VolunteerTask,
    VolunteerPet,
    VolunteerNotification
)

# ---------------- SIGNUP ----------------
def volunteerSignup(request):
    if request.method == "POST":
        vname = request.POST.get("vname")
        vemail = request.POST.get("vemail")
        vpassword = request.POST.get("vpassword")
        vcpassword = request.POST.get("vcpassword")

        if vpassword != vcpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('volunteer:volunteerSignup')

        if volunteer_registration.objects.filter(email=vemail).exists():
            messages.error(request, "Email already registered.")
            return redirect('volunteer:volunteerSignup')

        volunteer_registration.objects.create(
            name=vname,
            email=vemail,
            password=make_password(vpassword),  # 🔒 hashed
            phone=request.POST.get("phone"),
            address=request.POST.get("vaddress"),
            skills=request.POST.get("skills"),
            proof=request.FILES.get("vfile")
        )

        messages.success(request, "Registration successful.")
        return redirect('volunteer:volunteerLogin')

    return render(request, "volunteer/volunteerSignup.html")


# ---------------- LOGIN ----------------
def volunteerLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            volunteer = volunteer_registration.objects.get(email=email)

            if check_password(password, volunteer.password):
                request.session['volunteer_id'] = volunteer.id
                request.session['volunteer_name'] = volunteer.name
                request.session['volunteer_email'] = volunteer.email
                return redirect('volunteer:volunteerHome')
            else:
                messages.error(request, "Invalid credentials.")

        except volunteer_registration.DoesNotExist:
            messages.error(request, "Invalid credentials.")

    return render(request, "volunteer/volunteerLogin.html")


# ---------------- DASHBOARD ----------------
def volunteerHome(request):
    if 'volunteer_id' not in request.session:
        return redirect('volunteer:volunteerLogin')

    volunteer = volunteer_registration.objects.get(
        id=request.session['volunteer_id']
    )

    attendances = VolunteerAttendance.objects.filter(volunteer=volunteer)

    total_hours = sum(a.worked_hours() for a in attendances)

    checked_in = attendances.filter(check_out__isnull=True).exists()

    pets_helped = VolunteerPet.objects.filter(volunteer=volunteer).count()

    upcoming_tasks = VolunteerTask.objects.filter(
        volunteer=volunteer,
        status='upcoming'
    ).count()

    today_tasks = VolunteerTask.objects.filter(
        volunteer=volunteer,
        task_time__date=timezone.now().date()
    ).order_by('task_time')

    notifications = VolunteerNotification.objects.filter(
        volunteer=volunteer,
        is_read=False
    ).count()

    return render(request, "volunteer/volunteerHome.html", {
        "volunteer": volunteer,
        "hours_completed": round(total_hours, 2),
        "checked_in": checked_in,
        "pets_helped": pets_helped,
        "upcoming_tasks": upcoming_tasks,
        "today_tasks": today_tasks,
        "notifications": notifications
    })

# ---------------- CHECK-IN (ANTI DOUBLE) ----------------
def volunteerCheckIn(request):
    active = VolunteerAttendance.objects.filter(
        volunteer_id=request.session['volunteer_id'],
        check_out__isnull=True
    ).exists()

    if not active:
        VolunteerAttendance.objects.create(
            volunteer_id=request.session['volunteer_id']
        )
        volunteer_registration.objects.filter(
            id=request.session['volunteer_id']
        ).update(is_available=True)

    return redirect('volunteer:volunteerHome')


# ---------------- CHECK-OUT ----------------
def volunteerCheckOut(request):
    attendance = VolunteerAttendance.objects.filter(
        volunteer_id=request.session['volunteer_id'],
        check_out__isnull=True
    ).last()

    if attendance:
        attendance.check_out = timezone.now()
        attendance.save()

    volunteer_registration.objects.filter(
        id=request.session['volunteer_id']
    ).update(is_available=False)

    return redirect('volunteer:volunteerHome')


# ---------------- ATTENDANCE HISTORY ----------------
def volunteerAttendanceHistory(request):
    if 'volunteer_id' not in request.session:
        return redirect('volunteer:volunteerLogin')

    records = VolunteerAttendance.objects.filter(
        volunteer_id=request.session['volunteer_id']
    ).order_by('-check_in')

    return render(request, "volunteer/volunteerAttendance.html", {
        "records": records
    })


# ---------------- STATIC ----------------
def volunteerAppointments(request):
    if 'volunteer_id' not in request.session:
        return redirect('volunteer:volunteerLogin')

    tasks = VolunteerTask.objects.filter(
        volunteer_id=request.session['volunteer_id']
    ).order_by("task_time")

    return render(request, "volunteer/volunteerAppointments.html", {
        "tasks": tasks
    })


def volunteerPets(request):
    if 'volunteer_id' not in request.session:
        return redirect('volunteer:volunteerLogin')

    pets = VolunteerPet.objects.filter(
        volunteer_id=request.session['volunteer_id']
    )

    return render(request, "volunteer/volunteerPets.html", {
        "pets": pets
    })


def volunteerNotification(request):
    if 'volunteer_id' not in request.session:
        return redirect('volunteer:volunteerLogin')

    notes = VolunteerNotification.objects.filter(
        volunteer_id=request.session['volunteer_id']
    ).order_by("-created_at")

    return render(request, "volunteer/volunteerNotification.html", {
        "notes": notes
    })

