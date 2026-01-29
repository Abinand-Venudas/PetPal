from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import Service
from .models import Service, GroomingBooking, GroomingSlotLock
from django.db import transaction

from .models import DaycareBooking, Pet, AdoptionRequest, user_registration, SlotLock
from doctor.models import doctor_registration, Appointment
from volunteer.models import volunteer_registration
from Petadmin.models import *

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import inch
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
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("petapp:login")
    user = user_registration.objects.get(id=user_id)

    if request.method == "POST":
        user.name = request.POST.get("name")
        user.email = request.POST.get("email")
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("petapp:profile")

    return render(request, "user/editprofile.html", {"user": user})


# ================== CHANGE PASSWORD ==================
def change_password(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("petapp:login")
    user = user_registration.objects.get(id=user_id)

    if request.method == "POST":
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        if user.password != current:
            messages.error(request, "Current password is incorrect.")
        elif new != confirm:
            messages.error(request, "Passwords do not match.")
        else:
            user.password = new
            user.save()
            messages.success(request, "Password updated successfully.")
            return redirect("petapp:profile")

    return render(request, "user/changepassword.html")


# ================== MY BOOKINGS ==================
# ================== MY BOOKINGS ==================
CANCEL_LOCK_HOURS = 2

def my_bookings(request):
    if not request.session.get("user_id"):
        return redirect("petapp:login")

    user_id = request.session["user_id"]

    # ================= CANCEL CONSULTATION =================
    cancel_id = request.GET.get("cancel")
    if cancel_id:
        booking = get_object_or_404(Appointment, id=cancel_id, user_id=user_id)

        booking_dt = datetime.combine(booking.date, booking.time)
        booking_dt = timezone.make_aware(booking_dt)

        if timezone.now() >= booking_dt - timedelta(hours=CANCEL_LOCK_HOURS):
            messages.error(request, "This appointment can no longer be cancelled.")
            return redirect("petapp:my_bookings")

        booking.status = "Rejected"
        booking.save()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect("petapp:my_bookings")

    # ================= CANCEL DAYCARE =================
    cancel_daycare_id = request.GET.get("cancel_daycare")
    if cancel_daycare_id:
        booking = get_object_or_404(DaycareBooking, id=cancel_daycare_id, user_id=user_id)

        booking_dt = datetime.combine(booking.date, booking.start_time)
        booking_dt = timezone.make_aware(booking_dt)

        if timezone.now() >= booking_dt - timedelta(hours=CANCEL_LOCK_HOURS):
            messages.error(request, "This daycare booking can no longer be cancelled.")
            return redirect("petapp:my_bookings")

        booking.status = "Cancelled"
        booking.save()
        messages.success(request, "Daycare booking cancelled successfully.")
        return redirect("petapp:my_bookings")

    # ================= FETCH BOOKINGS =================
    bookings = Appointment.objects.filter(user_id=user_id).order_by("-created_at")
    daycare_bookings = DaycareBooking.objects.filter(user_id=user_id).order_by("-created_at")
    grooming_bookings = GroomingBooking.objects.filter(user_id=user_id).order_by("-created_at")

    return render(request, "user/userBookings.html", {
        "bookings": bookings,
        "daycare_bookings": daycare_bookings,
        "grooming_bookings": grooming_bookings,
    })


# ================== GROOMING ==================
# =========================
# TIME HELPERS
# =========================
def time_to_minutes(t):
    return t.hour * 60 + t.minute

def str_time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

# ================== GROOMING ==================

def grooming(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("petapp:login")

    user = user_registration.objects.get(id=user_id)
    services = Service.objects.all()

    # =========================
    # LOAD EXISTING BOOKINGS WITH TIME RANGES
    # =========================
    bookings = GroomingBooking.objects.all()
    booked_slots = {}

    for b in bookings:
        d = str(b.date)
        start = b.time.strftime("%H:%M")
        end = (datetime.combine(b.date, b.time) + timedelta(minutes=b.total_duration)).strftime("%H:%M")

        booked_slots.setdefault(d, []).append({
            "start": start,
            "end": end
        })

    # =========================
    # POST REQUEST (BOOKING)
    # =========================
    if request.method == "POST":
        try:
            date_str = request.POST.get("date")
            time_str = request.POST.get("time")
            phone = request.POST.get("phone")
            service_ids = request.POST.getlist("services")

            # ---------- Validation ----------
            if not (date_str and time_str and phone and service_ids):
                messages.error(request, "All fields are required")
                return redirect("petapp:grooming")

            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # 🔐 Block past dates
            if booking_date < timezone.now().date():
                messages.error(request, "You cannot book grooming for past dates.")
                return redirect("petapp:grooming")

            booking_time = datetime.strptime(time_str, "%H:%M").time()

            # ---------- Services ----------
            services_qs = Service.objects.filter(id__in=service_ids)

            total = sum(int(s.price) for s in services_qs)
            total_duration = sum(int(s.duration) for s in services_qs)

            if total_duration <= 0:
                messages.error(request, "Service duration not configured. Contact admin.")
                return redirect("petapp:grooming")

            # ---------- Time calc ----------
            start_min = booking_time.hour * 60 + booking_time.minute
            BUFFER = 1  # safety buffer
            end_min = start_min + total_duration + BUFFER

            # ---------- Closing time ----------
            if end_min > 22 * 60:
                messages.error(request, "Selected services exceed closing time (10 PM).")
                return redirect("petapp:grooming")

            # ---------- Slot lock ----------
            if GroomingSlotLock.objects.filter(date=booking_date, time=booking_time).exists():
                messages.error(request, "This slot is temporarily locked. Try another slot.")
                return redirect("petapp:grooming")

            # =========================
            # HARD OVERLAP ENGINE (BACKEND)
            # =========================
            same_day_bookings = GroomingBooking.objects.filter(date=booking_date)

            for b in same_day_bookings:
                b_start = b.time.hour * 60 + b.time.minute
                b_end = b_start + b.total_duration

                # HARD overlap rule
                if start_min < b_end and end_min > b_start:
                    messages.error(request, "Selected time overlaps with another booking.")
                    return redirect("petapp:grooming")

            # =========================
            # ATOMIC BOOKING
            # =========================
            with transaction.atomic():

                GroomingSlotLock.objects.create(
                    user=user,
                    date=booking_date,
                    time=booking_time
                )

                if GroomingBooking.objects.filter(date=booking_date, time=booking_time).exists():
                    messages.error(request, "Slot already booked.")
                    return redirect("petapp:grooming")

                GroomingBooking.objects.create(
                    user=user,
                    date=booking_date,
                    time=booking_time,
                    phone=phone,
                    services=service_ids,
                    total=total,
                    total_duration=total_duration
                )

                GroomingSlotLock.objects.filter(date=booking_date, time=booking_time).delete()

            messages.success(request, "Grooming booked successfully!")
            return redirect("petapp:groomsuccess")

        except Exception as e:
            messages.error(request, f"Booking failed: {str(e)}")
            return redirect("petapp:grooming")

    # =========================
    # GET REQUEST
    # =========================
    context = {
        "services": services,
        "booked_slots": booked_slots
    }

    return render(request, "user/grooming.html", context)

def groomsuccess(request):

    # 🔐 Session-based login check
    if "user_id" not in request.session:
        return redirect("/login/")

    user_id = request.session["user_id"]

    # Get latest booking for this user
    booking = GroomingBooking.objects.filter(user_id=user_id).order_by("-created_at").first()

    if not booking:
        return redirect("petapp:grooming")

    # Convert service IDs → names
    services = Service.objects.filter(id__in=booking.services)
    service_names = [s.name for s in services]

    context = {
        "booking_id": booking.id,
        "date": booking.date.strftime("%d %B %Y"),
        "time": booking.time.strftime("%I:%M %p"),
        "phone": booking.phone,
        "services": service_names,
        "total": booking.total,
        "created": booking.created_at.strftime("%d %b %Y, %I:%M %p"),
    }

    # ✅ correct template path (based on your folder)
    return render(request, "user/groomingSuccess.html", context)

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
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        total_cost = request.POST.get("total_cost")

        # 🔴 Validate required fields
        if not date or not start_time or not end_time:
            messages.error(request, "Please select a valid date and time.")
            return redirect("petapp:daycare")

        booking = DaycareBooking.objects.create(
            user=user,
            pet_name=pet_name,
            pet_type=pet_type,
            plan=plan,
            duration=duration,
            date=date,   # must be YYYY-MM-DD
            start_time=start_time,
            end_time=end_time,
            total_cost=total_cost,
            status="Confirmed"
        )

        return redirect("petapp:daycareSuccess", booking.id)

    return redirect("petapp:daycare")

from django.http import JsonResponse
from .models import DaycareBooking

# ================= API: FETCH DAYCARE BOOKED TIMES =================
def get_daycare_booked_slots(request):
    date = request.GET.get("date")
    if not date:
        return JsonResponse({"times": []})

    bookings = DaycareBooking.objects.filter(date=date)
    times = [str(b.start_time) for b in bookings]

    return JsonResponse({"times": times})

# ================== ADOPTION ==================
def adoptionlist(request):
    pets = Pet.objects.all()
    requested_pets = []

    user_id = request.session.get("user_id")
    if user_id:
        try:
            user = user_registration.objects.get(id=user_id)
            requested_pets = AdoptionRequest.objects.filter(user=user).values_list("pet_id", flat=True)
        except user_registration.DoesNotExist:
            pass

    return render(request, "user/adoptionlist.html", {
        "pets": pets,
        "requested_pets": requested_pets
    })


def petDetails(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    adoption = None
    if "user_id" in request.session:
        user = user_registration.objects.get(id=request.session["user_id"])
        adoption = AdoptionRequest.objects.filter(user=user, pet=pet).first()
        if adoption:
            return redirect("petapp:adoptionSuccess", id=adoption.id)

    return render(request, "user/petDetails.html", {
        "pet": pet,
        "adoption": adoption
    })


def adoptPet(request, pet_id):
    if "user_id" not in request.session:
        messages.error(request, "Please login to adopt a pet")
        return redirect("petapp:login")

    pet = get_object_or_404(Pet, id=pet_id)
    user = user_registration.objects.get(id=request.session["user_id"])

    existing = AdoptionRequest.objects.filter(user=user, pet=pet).first()
    if existing:
        messages.warning(request, "You already requested adoption for this pet")
        return redirect("petapp:adoptionSuccess", id=existing.id)

    if request.method == "POST":
        visit_date = request.POST.get("visit_date")

        if not visit_date:
            messages.error(request, "Please select a visit date.")
            return redirect("petapp:petDetails", pet_id=pet.id)

        adoption = AdoptionRequest.objects.create(
            user=user,
            pet=pet,
            visit_date=visit_date
        )

        messages.success(request, "Adoption request submitted successfully")
        return redirect("petapp:adoptionSuccess", id=adoption.id)

    return redirect("petapp:petDetails", pet_id=pet.id)


def adoptionSuccess(request, id):
    if "user_id" not in request.session:
        return redirect("petapp:login")

    adoption = get_object_or_404(AdoptionRequest, id=id)
    return render(request, "user/adoptionrequestSuccess.html", {"adoption": adoption})


# ================== CONSULTATION (APPOINTMENT) =================
def consultation(request):
    dc = doctor_registration.objects.all()

    if request.method == "POST":
        if not request.session.get("user_id"):
            messages.error(request, "Please log in to book a consultation.")
            return redirect("petapp:login")

        pet_name = request.POST.get("pet_name")
        pet_type = request.POST.get("pet_type")
        issue = request.POST.get("issue")
        doctor_id = request.POST.get("doctor_id")
        date = request.POST.get("date")
        time = request.POST.get("time")

        doctor = doctor_registration.objects.get(id=doctor_id)
        user = user_registration.objects.get(id=request.session["user_id"])

        if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
            messages.error(request, "This time slot is already booked.")
            return redirect("petapp:consultation")

        appointment = Appointment.objects.create(
            user=user,
            doctor=doctor,
            pet_name=pet_name,
            pet_type=pet_type,
            reason=issue,
            date=date,
            time=time,
            status="pending"
        )

        messages.success(request, "Consultation booked successfully!")
        return redirect("petapp:consultationSuccess", id=appointment.id)

    return render(request, "user/consultation.html", {"dc": dc})


def consultationSuccess(request, id):
    if "user_id" not in request.session:
        return redirect("petapp:login")
    appointment = get_object_or_404(Appointment, id=id)
    return render(request, "user/consultationSuccess.html", {"consultation": appointment})


# ================= CLEAN EXPIRED LOCKS =================
def cleanup_expired_locks():
    expiry_time = timezone.now() - timedelta(minutes=5)
    SlotLock.objects.filter(locked_at__lt=expiry_time).delete()


# ================= API: FETCH BOOKED SLOTS =================
def get_booked_slots(request):
    date = request.GET.get("date")
    if not date:
        return JsonResponse({})

    cleanup_expired_locks()

    bookings = Appointment.objects.filter(date=date)
    locks = SlotLock.objects.filter(date=date)

    data = {}

    for b in bookings:
        data.setdefault(str(b.doctor_id), []).append(str(b.time))

    for lock in locks:
        data.setdefault(str(lock.doctor_id), []).append(str(lock.time))

    return JsonResponse(data)


# ================= LOCK SLOT =================
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

    if Appointment.objects.filter(doctor_id=doctor_id, date=date, time=time).exists():
        return JsonResponse({"success": False, "message": "Slot already booked"})

    existing_lock = SlotLock.objects.filter(doctor_id=doctor_id, date=date, time=time).first()

    if existing_lock and existing_lock.user_id != user_id:
        return JsonResponse({"success": False, "message": "Slot currently locked by another user"})

    SlotLock.objects.update_or_create(
        doctor_id=doctor_id,
        date=date,
        time=time,
        defaults={"user_id": user_id, "locked_at": timezone.now()}
    )

    return JsonResponse({"success": True, "message": "Slot locked"})


# ================= RELEASE SLOT =================
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

    SlotLock.objects.filter(
        doctor_id=doctor_id,
        date=date,
        time=time,
        user_id=user_id
    ).delete()

    return JsonResponse({"success": True, "message": "Slot released"})


# ================= PDF RECEIPT =================
def download_booking_pdf(request, booking_id):
    if not request.session.get("user_id"):
        return redirect("petapp:login")

    booking = Appointment.objects.get(id=booking_id, user_id=request.session["user_id"])

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Consultation_{booking.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 80

    p.setFont("Helvetica-Bold", 20)
    p.drawString(80, y, "Pawfect – Consultation Details")

    y -= 60
    p.setFont("Helvetica", 12)

    lines = [
        f"Doctor: Dr. {booking.doctor.name}",
        f"Specialization: {booking.doctor.specialization if hasattr(booking.doctor,'specialization') else 'Veterinary Specialist'}",
        f"Date: {booking.date}",
        f"Time: {booking.time}",
        f"Status: {booking.status}",
        f"Pet Name: {booking.pet_name}",
        f"Issue: {booking.reason}",
    ]

    for line in lines:
        p.drawString(80, y, line)
        y -= 25

    y -= 40
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(80, y, "Thank you for choosing Pawfect 🐾")

    p.showPage()
    p.save()

    return response
