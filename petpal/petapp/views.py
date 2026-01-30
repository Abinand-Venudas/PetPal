from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.db import IntegrityError 

from django.db import transaction

from .models import (
    DaycareSlotLock, Service, GroomingBooking, GroomingSlotLock,
    DaycareBooking, Pet, AdoptionRequest, user_registration, SlotLock
)

from doctor.models import doctor_registration, Appointment
from volunteer.models import volunteer_registration
from Petadmin.models import *

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# ================= HOME =================
def home(request):
    username = request.session.get("username")
    return render(request, "index.html", {"username": username})


# ================== LOGIN ==================
def userLogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = user_registration.objects.get(username=username, password=password)
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            messages.success(request, "Login successful")
            return redirect("petapp:home")
        except user_registration.DoesNotExist:
            messages.error(request, "Invalid username or password")

    return render(request, "user/userLogin.html")


# ================== REGISTER ==================
def userReg(request):
    if request.method == "POST":
        name1 = request.POST.get("name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        cpassword = request.POST.get("password2")

        if password == cpassword:
            if user_registration.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            elif user_registration.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
            else:
                user_registration.objects.create(
                    name=name1,
                    email=email,
                    username=username,
                    password=password
                )
                messages.success(request, "Registration successful.")
                return redirect("petapp:login")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, "user/userReg.html")


# ================== LOGOUT ==================
def userLogout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect("petapp:home")


# ================== PROFILE ==================
def profile(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("petapp:login")
    user = user_registration.objects.get(id=user_id)
    return render(request, "user/profile.html", {"user": user})

# ================== EDIT PROFILE ==================
def edit_profile(request):
    if "user_id" not in request.session:
        return redirect("petapp:login")

    user = user_registration.objects.get(id=request.session["user_id"])

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")

        if not name or not email:
            messages.error(request, "All fields are required.")
            return redirect("petapp:edit_profile")

        user.name = name
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("petapp:profile")

    return render(request, "user/editprofile.html", {"user": user})

# ================== CHANGE PASSWORD ==================
def change_password(request):
    if "user_id" not in request.session:
        return redirect("petapp:login")

    user = user_registration.objects.get(id=request.session["user_id"])

    if request.method == "POST":
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        if not current or not new or not confirm:
            messages.error(request, "All fields are required.")
            return redirect("petapp:change_password")

        if user.password != current:
            messages.error(request, "Current password is incorrect.")
            return redirect("petapp:change_password")

        if new != confirm:
            messages.error(request, "New passwords do not match.")
            return redirect("petapp:change_password")

        user.password = new
        user.save()

        messages.success(request, "Password updated successfully.")
        return redirect("petapp:profile")

    return render(request, "user/changepassword.html")


# ================== MY BOOKINGS ==================
CANCEL_LOCK_HOURS = 2

def my_bookings(request):
    if not request.session.get("user_id"):
        return redirect("petapp:login")

    user_id = request.session["user_id"]

    bookings = Appointment.objects.filter(user_id=user_id).order_by("-created_at")
    daycare_bookings = DaycareBooking.objects.filter(user_id=user_id).order_by("-created_at")
    grooming_bookings = GroomingBooking.objects.filter(user_id=user_id).order_by("-created_at")

    return render(request, "user/userBookings.html", {
        "bookings": bookings,
        "daycare_bookings": daycare_bookings,
        "grooming_bookings": grooming_bookings,
    })


# ================== GROOMING ==================
def grooming(request):
    if not request.session.get("user_id"):
        return redirect("petapp:login")

    user = user_registration.objects.get(id=request.session["user_id"])
    services = Service.objects.all()

    if request.method == "POST":
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")
        phone = request.POST.get("phone")
        service_ids = request.POST.getlist("services")

        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        booking_time = datetime.strptime(time_str, "%H:%M").time()

        services_qs = Service.objects.filter(id__in=service_ids)
        total = sum(int(s.price) for s in services_qs)
        total_duration = sum(int(s.duration) for s in services_qs)

        with transaction.atomic():
            GroomingBooking.objects.create(
                user=user,
                date=booking_date,
                time=booking_time,
                phone=phone,
                services=service_ids,
                total=total,
                total_duration=total_duration
            )

        return redirect("petapp:groomsuccess")

    return render(request, "user/grooming.html", {"services": services})


def groomsuccess(request):
    if "user_id" not in request.session:
        return redirect("petapp:login")

    booking = GroomingBooking.objects.filter(user_id=request.session["user_id"]).order_by("-created_at").first()
    return render(request, "user/groomingSuccess.html", {"booking": booking})


# ================== DAYCARE ==================
def daycare(request):
    return render(request, "user/daycare.html")


def daycareSuccess(request, id):
    if "user_id" not in request.session:
        return redirect("petapp:login")

    booking = get_object_or_404(DaycareBooking, id=id)
    return render(request, "user/daycareSuccess.html", {"booking": booking})


def confirmbook(request):
    if request.method == "POST":

        if "user_id" not in request.session:
            return redirect("petapp:login")

        user = user_registration.objects.get(id=request.session["user_id"])

        pet_name = request.POST.get("pet_name")
        pet_type = request.POST.get("pet_type")
        plan = request.POST.get("plan")
        duration = request.POST.get("duration")
        date_str = request.POST.get("date")
        start_time_str = request.POST.get("start_time")
        total_cost = request.POST.get("total_cost")

        if not all([pet_name, pet_type, plan, duration, date_str, start_time_str, total_cost]):
            messages.error(request, "All fields are required.")
            return redirect("petapp:daycare")

        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        booking_time = datetime.strptime(start_time_str, "%H:%M").time()

        if booking_date < timezone.now().date():
            messages.error(request, "You cannot book past dates.")
            return redirect("petapp:daycare")

        cleanup_daycare_locks()

        try:
            with transaction.atomic():

                # 🔐 TEMP LOCK
                if DaycareSlotLock.objects.filter(date=booking_date, time=booking_time).exists():
                    messages.error(request, "Slot temporarily locked. Try another time.")
                    return redirect("petapp:daycare")

                DaycareSlotLock.objects.create(
                    user=user,
                    date=booking_date,
                    time=booking_time
                )

                # 🔒 HARD CHECK (pre-check)
                if DaycareBooking.objects.filter(date=booking_date, start_time=booking_time).exists():
                    DaycareSlotLock.objects.filter(date=booking_date, time=booking_time).delete()
                    messages.error(request, "This time slot is already booked.")
                    return redirect("petapp:daycare")

                # ✅ CREATE BOOKING
                booking = DaycareBooking.objects.create(
                    user=user,
                    pet_name=pet_name,
                    pet_type=pet_type,
                    plan=plan,
                    duration=duration,
                    date=booking_date,
                    start_time=booking_time,
                    end_time=booking_time,
                    total_cost=total_cost,
                    status="Confirmed"
                )

                # 🔓 RELEASE LOCK
                DaycareSlotLock.objects.filter(date=booking_date, time=booking_time).delete()

        except IntegrityError:
            # ✅ DB-level unique constraint protection
            DaycareSlotLock.objects.filter(date=booking_date, time=booking_time).delete()
            messages.error(request, "This slot was just booked by another user. Please choose another time.")
            return redirect("petapp:daycare")

        except Exception as e:
            DaycareSlotLock.objects.filter(date=booking_date, time=booking_time).delete()
            messages.error(request, f"Booking failed: {str(e)}")
            return redirect("petapp:daycare")

        # ✅ SUCCESS REDIRECT
        return redirect("petapp:daycareSuccess", id=booking.id)

    return redirect("petapp:daycare")


def cleanup_daycare_locks():
    expiry_time = timezone.now() - timedelta(minutes=5)
    DaycareSlotLock.objects.filter(locked_at__lt=expiry_time).delete()


# ================= API: FETCH DAYCARE BOOKED TIMES =================
# ================= API: FETCH DAYCARE BOOKED TIMES =================
def get_daycare_booked_slots(request):
    date = request.GET.get("date")
    if not date:
        return JsonResponse({"times": []})

    cleanup_daycare_locks()

    bookings = DaycareBooking.objects.filter(date=date)
    locks = DaycareSlotLock.objects.filter(date=date)

    times = set()

    # bookings
    for b in bookings:
        times.add(b.start_time.strftime("%H:%M"))  # 🔥 force HH:MM

    # locks
    for l in locks:
        times.add(l.time.strftime("%H:%M"))  # 🔥 force HH:MM

    return JsonResponse({"times": list(times)})


# ================= API: FETCH BOOKED CONSULTATION SLOTS =================
def get_booked_slots(request):
    date = request.GET.get("date")
    if not date:
        return JsonResponse({})

    # Clean expired locks
    cleanup_expired_locks()

    bookings = Appointment.objects.filter(date=date)
    locks = SlotLock.objects.filter(date=date)

    data = {}

    # Booked slots
    for b in bookings:
        data.setdefault(str(b.doctor_id), []).append(str(b.time))

    # Locked slots
    for lock in locks:
        data.setdefault(str(lock.doctor_id), []).append(str(lock.time))

    return JsonResponse(data)

# ================= LOCK SLOT (CONSULTATION) =================
@csrf_exempt
def lock_slot(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

    data = json.loads(request.body)
    doctor_id = data.get("doctor_id")
    date = data.get("date")
    time = data.get("time")

    if "user_id" not in request.session:
        return JsonResponse({"success": False, "message": "Not authenticated"}, status=403)

    user_id = request.session["user_id"]

    cleanup_expired_locks()

    # Already booked
    if Appointment.objects.filter(doctor_id=doctor_id, date=date, time=time).exists():
        return JsonResponse({"success": False, "message": "Slot already booked"})

    # Already locked by another user
    existing_lock = SlotLock.objects.filter(doctor_id=doctor_id, date=date, time=time).first()
    if existing_lock and existing_lock.user_id != user_id:
        return JsonResponse({"success": False, "message": "Slot locked by another user"})

    # Create / refresh lock
    SlotLock.objects.update_or_create(
        doctor_id=doctor_id,
        date=date,
        time=time,
        defaults={"user_id": user_id, "locked_at": timezone.now()}
    )

    return JsonResponse({"success": True, "message": "Slot locked"})

# ================= RELEASE SLOT (CONSULTATION) =================
@csrf_exempt
def release_slot(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

    data = json.loads(request.body)
    doctor_id = data.get("doctor_id")
    date = data.get("date")
    time = data.get("time")

    if "user_id" not in request.session:
        return JsonResponse({"success": False, "message": "Not authenticated"}, status=403)

    user_id = request.session["user_id"]

    # Delete only this user's lock
    SlotLock.objects.filter(
        doctor_id=doctor_id,
        date=date,
        time=time,
        user_id=user_id
    ).delete()

    return JsonResponse({"success": True, "message": "Slot released"})


# ================== ADOPTION ==================
def adoptionlist(request):
    pets = Pet.objects.all()
    return render(request, "user/adoptionlist.html", {"pets": pets})


def petDetails(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, "user/petDetails.html", {"pet": pet})


def adoptPet(request, pet_id):
    if "user_id" not in request.session:
        return redirect("petapp:login")

    pet = get_object_or_404(Pet, id=pet_id)
    user = user_registration.objects.get(id=request.session["user_id"])

    adoption = AdoptionRequest.objects.create(user=user, pet=pet)
    return redirect("petapp:adoptionSuccess", id=adoption.id)


def adoptionSuccess(request, id):
    if "user_id" not in request.session:
        return redirect("petapp:login")

    adoption = get_object_or_404(AdoptionRequest, id=id)
    return render(request, "user/adoptionrequestSuccess.html", {"adoption": adoption})


# ================== CONSULTATION =================
def consultation(request):
    dc = doctor_registration.objects.all()

    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        date = request.POST.get("date")
        time = request.POST.get("time")

        doctor = doctor_registration.objects.get(id=doctor_id)
        user = user_registration.objects.get(id=request.session["user_id"])

        appointment = Appointment.objects.create(
            user=user,
            doctor=doctor,
            date=date,
            time=time,
            status="pending"
        )

        return redirect("petapp:consultationSuccess", id=appointment.id)

    return render(request, "user/consultation.html", {"dc": dc})


def consultationSuccess(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    return render(request, "user/consultationSuccess.html", {"consultation": appointment})


# ================= PDF =================
def download_booking_pdf(request, booking_id):
    booking = Appointment.objects.get(id=booking_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Consultation_{booking.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    p.drawString(80, 800, "PetPal – Consultation Receipt")
    p.drawString(80, 760, f"Doctor: {booking.doctor.name}")
    p.drawString(80, 730, f"Date: {booking.date}")
    p.drawString(80, 700, f"Time: {booking.time}")

    p.showPage()
    p.save()

    return response
