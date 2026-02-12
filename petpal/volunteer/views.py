from email.mime import application
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .models import (
    volunteer_registration,
    VolunteerAttendance,
    VolunteerTask,
    VolunteerPet,
    VolunteerNotification,
    VolunteerApplication,   # ✅ ADD THIS
)


from petapp.models import GroomingBooking
from django.http import JsonResponse
from django.views.decorators.http import require_POST



# =========================================================
# HELPER
# =========================================================
def get_logged_volunteer(request):
    volunteer_id = request.session.get("volunteer_id")
    if not volunteer_id:
        return None
    return volunteer_registration.objects.filter(id=volunteer_id).first()


# =========================================================
# SIGNUP
# =========================================================
def volunteerSignup(request):

     # 🔒 Block access without verification
    if not request.session.get("verified_volunteer_email"):
        messages.error(request, "Please verify your authorization code first.")
        return redirect("volunteer:verify_code")
    
    
    if request.method == "POST":
        vpassword = request.POST.get("vpassword")
        vcpassword = request.POST.get("vcpassword")

        if vpassword != vcpassword:
            messages.error(request, "Passwords do not match.")
            return redirect("volunteer:volunteerSignup")

        if volunteer_registration.objects.filter(
            email=request.POST.get("vemail")
        ).exists():
            messages.error(request, "Email already registered.")
            return redirect("volunteer:volunteerSignup")

        volunteer_registration.objects.create(
            name=request.POST.get("vname"),
            email=request.POST.get("vemail"),
            password=make_password(vpassword),
            phone=request.POST.get("phone"),
            address=request.POST.get("vaddress"),
            skills=request.POST.get("skills"),
            proof=request.FILES.get("vfile")
        )

        messages.success(request, "Registration successful.")
        return redirect("volunteer:volunteerLogin")

    return render(request, "volunteer/volunteerSignup.html")


# =========================================================
# APPLY
# =========================================================
def volunteerApply(request):
    if request.method == "POST":

        # prevent duplicate applications
        if VolunteerApplication.objects.filter(
            email=request.POST.get("email"),
            status="Pending"
        ).exists():
            messages.error(
                request,
                "You already have a pending volunteer application."
            )
            return redirect("volunteer:apply")

        interests = request.POST.getlist("interest[]")

        if not interests:
            messages.error(
                request,
                "Please select at least one area of interest."
            )
            return redirect("volunteer:apply")

        proof = request.FILES.get("proof")
        if not proof:
            messages.error(
                request,
                "Proof document is required."
            )
            return redirect("volunteer:apply")

        VolunteerApplication.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            city=request.POST.get("city"),
            interest=",".join(interests),  # ✅ store multiple
            availability=request.POST.get("availability"),
            reason=request.POST.get("reason"),
            proof=proof,
        )

        messages.success(
            request,
            "Your volunteer application has been submitted successfully."
        )

        return redirect("volunteer:apply_success")

    return render(request, "volunteer/volunteerApply.html")


def volunteerApplySuccess(request):
    return render(request, "volunteer/volunteerApplySuccess.html")


def verify_code(request):
    if request.method == "POST":
        code = request.POST.get("code")

        if not code:
            messages.error(request, "Authorization code is required.")
            return redirect("volunteer:verify_code")

        application = VolunteerApplication.objects.filter(
            authorization_code=code,
            status="Approved"
        ).first()

        if not application:
            messages.error(request, "Invalid or expired authorization code.")
            return redirect("volunteer:verify_code")

        # ✅ Save verification in session
        request.session["verified_volunteer_email"] = application.email

        messages.success(request, "Code verified successfully. Please complete signup.")
        return redirect("volunteer:volunteerSignup")

    return render(request, "volunteer/verifyCode.html")


ADMIN_AUTH_CODE = "PETPAL-ADMIN-2025"  # only admin recruits

def admin_volunteer_access(request):
    if request.method == "POST":
        code = request.POST.get("code")

        if code != ADMIN_AUTH_CODE:
            messages.error(request, "Invalid admin authorization code.")
            return redirect("volunteer:admin_access")

        # 🔓 Unlock signup
        request.session["volunteer_signup_allowed"] = True
        request.session["admin_recruited"] = True

        return redirect("volunteer:volunteerSignup")

    return render(request, "volunteer/adminAccess.html")

# =========================================================
# LOGIN / LOGOUT
# =========================================================
def volunteerLogin(request):
    if request.method == "POST":
        volunteer = volunteer_registration.objects.filter(
            email=request.POST.get("email")
        ).first()

        if volunteer and check_password(
            request.POST.get("password"),
            volunteer.password
        ):
            request.session["volunteer_id"] = volunteer.id
            request.session["volunteer_name"] = volunteer.name
            request.session["volunteer_email"] = volunteer.email
            return redirect("volunteer:volunteerHome")

        messages.error(request, "Invalid credentials.")

    return render(request, "volunteer/volunteerLogin.html")


def volunteerLogout(request):
    request.session.flush()
    return redirect("volunteer:volunteerLogin")


# =========================================================
# DASHBOARD
# =========================================================
def volunteerHome(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    attendances = VolunteerAttendance.objects.filter(
        volunteer=volunteer,
        check_out__isnull=False
    )

    total_minutes = sum(int(a.worked_hours() * 60) for a in attendances)
    hours_completed = f"{total_minutes // 60}h {total_minutes % 60}m"

    checked_in = VolunteerAttendance.objects.filter(
        volunteer=volunteer,
        check_out__isnull=True
    ).exists()

    unread_notifications = VolunteerNotification.objects.filter(
        volunteer=volunteer,
        is_read=False
    )

    return render(request, "volunteer/volunteerHome.html", {
        "volunteer": volunteer,
        "hours_completed": hours_completed,
        "checked_in": checked_in,
        "pets_helped": VolunteerPet.objects.filter(volunteer=volunteer).count(),
        "upcoming_tasks": VolunteerTask.objects.filter(volunteer=volunteer).count(),
        "today_tasks": VolunteerTask.objects.filter(
            volunteer=volunteer,
            task_time__date=timezone.now().date()
        ).order_by("task_time"),
        "notifications": unread_notifications.count(),
        "latest_notifications": unread_notifications[:3],
    })


# =========================================================
# CHECK-IN / CHECK-OUT
# =========================================================
def volunteerCheckIn(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    if not VolunteerAttendance.objects.filter(
        volunteer=volunteer,
        check_out__isnull=True
    ).exists():
        VolunteerAttendance.objects.create(volunteer=volunteer)
        volunteer.is_available = True
        volunteer.save()

    return redirect("volunteer:volunteerHome")


def volunteerCheckOut(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    attendance = VolunteerAttendance.objects.filter(
        volunteer=volunteer,
        check_out__isnull=True
    ).last()

    if attendance:
        attendance.check_out = timezone.now()
        attendance.save()

    volunteer.is_available = False
    volunteer.save()

    return redirect("volunteer:volunteerHome")


# ATTENDANCE HISTORY
# =========================================================
def volunteerAttendanceHistory(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    records = VolunteerAttendance.objects.filter(
        volunteer=volunteer
    ).order_by("-check_in")

    notifications = VolunteerNotification.objects.filter(
        volunteer=volunteer,
        is_read=False
    )

    return render(request, "volunteer/volunteerAttendance.html", {
        "records": records,
        "notifications": notifications[:5],
        "unread_count": notifications.count(),
    })


# =========================================================
# TASKS / APPOINTMENTS
# =========================================================
def volunteerAppointments(request):
    volunteer_id = request.session.get("volunteer_id")
    if not volunteer_id:
        return redirect("volunteer:volunteerLogin")

    volunteer = get_object_or_404(volunteer_registration, id=volunteer_id)

    # ✅ ONLY use REAL fields
    appointments = GroomingBooking.objects.filter(
        volunteer=volunteer,
        status="Assigned"
    ).select_related(
        "user",
        "volunteer"
    ).order_by("date", "start_time")

    return render(request, "volunteer/volunteerAppointments.html", {
        "tasks": appointments
    })


def volunteerTasks(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    tasks = GroomingBooking.objects.filter(
        volunteer=volunteer
    ).order_by("-created_at")

    notifications = VolunteerNotification.objects.filter(
        volunteer=volunteer
    )

    return render(request, "volunteer/volunteerAppointments.html", {
        "tasks": tasks,
        "notifications": notifications[:5],
        "unread_count": notifications.filter(is_read=False).count()
    })


# =========================================================
# PETS
# =========================================================
def volunteerPets(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    pets = VolunteerPet.objects.filter(volunteer=volunteer)

    return render(request, "volunteer/volunteerPets.html", {
        "pets": pets
    })


# =========================================================
# NOTIFICATIONS
# =========================================================
def volunteerNotification(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    notes = VolunteerNotification.objects.filter(
        volunteer=volunteer
    ).order_by("-created_at")

    return render(request, "volunteer/volunteerNotification.html", {
        "notes": notes
    })


def mark_notification_read(request, id):
    volunteer_id = request.session.get("volunteer_id")
    if not volunteer_id:
        return redirect("volunteer:volunteerLogin")

    note = get_object_or_404(
        VolunteerNotification,
        id=id,
        volunteer_id=volunteer_id
    )

    note.is_read = True
    note.save()

    # ✅ Always redirect to appointments
    return redirect("volunteer:volunteerAppointments")



# =========================================================
# PROFILE
# =========================================================
def volunteerProfile(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    return render(request, "volunteer/volunteerProfile.html", {
        "volunteer": volunteer
    })


# =========================================================
# CHANGE PASSWORD
# =========================================================
def volunteerChangePassword(request):
    volunteer = get_logged_volunteer(request)
    if not volunteer:
        return redirect("volunteer:volunteerLogin")

    if request.method == "POST":
        old = request.POST.get("old_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        if not check_password(old, volunteer.password):
            messages.error(request, "Current password incorrect")
        elif new != confirm:
            messages.error(request, "Passwords do not match")
        else:
            volunteer.password = make_password(new)
            volunteer.save()
            messages.success(request, "Password updated successfully")
            return redirect("volunteer:volunteerHome")

    return render(request, "volunteer/volunteerChangePassword.html")


# =========================================================
# ADMIN → ASSIGN VOLUNTEER
# =========================================================
def assignGroomingVolunteer(request, booking_id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    booking = get_object_or_404(GroomingBooking, id=booking_id)

    if request.method == "POST":
        volunteer = get_object_or_404(
            volunteer_registration,
            id=request.POST.get("volunteer_id")
        )

        booking.volunteer = volunteer
        booking.status = "Assigned"
        booking.save()

        VolunteerNotification.objects.create(
            volunteer=volunteer,
            title="New Grooming Assignment",
            message=f"You have been assigned a grooming task on {booking.date}.",
            link="/volunteer/tasks/"
        )

        VolunteerTask.objects.create(
            volunteer=volunteer,
            title="Grooming Service",
            location="PetPal Center",
            task_time=booking.date
        )

        messages.success(request, "Volunteer assigned and notified successfully")
        return redirect("petadmin:adminGroomingBookings")

def notification_count_api(request):
    volunteer_id = request.session.get("volunteer_id")
    if not volunteer_id:
        return JsonResponse({"count": 0})

    count = VolunteerNotification.objects.filter(
        volunteer_id=volunteer_id,
        is_read=False
    ).count()

    return JsonResponse({"count": count})


@require_POST
def markAppointmentCompleted(request, booking_id):
    volunteer_id = request.session.get("volunteer_id")
    if not volunteer_id:
        return redirect("volunteer:volunteerLogin")

    booking = get_object_or_404(
        GroomingBooking,
        id=booking_id,
        volunteer_id=volunteer_id
    )

    # ✅ Update status
    booking.status = "Completed"
    booking.save()

    # 🔔 Optional notification
    VolunteerNotification.objects.create(
        volunteer_id=volunteer_id,
        title="Appointment Completed",
        message="You marked a grooming appointment as completed.",
        link="/volunteer/volunteerAppointments/"
    )

    return redirect("volunteer:volunteerAppointments")