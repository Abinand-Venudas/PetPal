from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from petapp.models import AdoptionRequest, Consultation, GroomingBooking, Pet, user_registration
from .models import Pro_Admin
from petapp.models import Service   # ✅ IMPORT FROM CORRECT APP
from doctor.models import doctor_registration
from volunteer.models import volunteer_registration
from volunteer.models import VolunteerNotification
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from petapp.models import Service
from .forms import ServiceForm
from .models import DaycarePlan
from .forms import DaycarePlanForm
from django.views.decorators.http import require_POST
from decimal import Decimal, InvalidOperation
from django.utils.timezone import now
from volunteer.models import VolunteerApplication
import random
import string
from django.core.mail import send_mail

# ================== AUTH ==================

def loginAdmin(request):
    if request.method == "POST":
        admin_email = request.POST.get("email")
        admin_password = request.POST.get("password")

        try:
            admin = Pro_Admin.objects.get(
                admin_email=admin_email,
                admin_password=admin_password
            )

            request.session["admin_id"] = admin.id
            request.session["admin_name"] = admin.admin_name

            messages.success(request, "Admin login successful")
            return redirect("petadmin:homeAdmin")

        except Pro_Admin.DoesNotExist:
            messages.error(request, "Invalid email or password")

    return render(request, "Petadmin/loginAdmin.html")


def logoutAdmin(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect("petadmin:loginAdmin")


# ================== DASHBOARD ==================

def homeAdmin(request):
    if "admin_id" not in request.session:
        messages.error(request, "Please login as admin")
        return redirect("petadmin:loginAdmin")

    if request.method == "POST":
        name = request.POST.get("name")
        pet_type = request.POST.get("pet_type")
        age = request.POST.get("age")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        if not all([name, pet_type, age, description, image]):
            messages.error(request, "All fields are required")
            return redirect("petadmin:homeAdmin")

        Pet.objects.create(
            name=name,
            pet_type=pet_type,
            age=age,
            description=description,
            image=image
        )

        messages.success(request, "Pet added successfully")
        return redirect("petadmin:homeAdmin")

    pets = Pet.objects.all()

    doctor_count = doctor_registration.objects.count()
    volunteer_count = volunteer_registration.objects.count()
    user_count = user_registration.objects.count()

    return render(
        request,
        "Petadmin/homeAdmin.html",
        {
            "pets": pets,
            "doctor_count": doctor_count,
            "volunteer_count": volunteer_count,
            "user_count": user_count,
        }
    )


# ================== DOCTORS ==================

def doctorAdmin(request):
    if "admin_id" not in request.session:
        messages.error(request, "Please login as admin")
        return redirect("petadmin:loginAdmin")

    doctors = doctor_registration.objects.all()

    # 🔍 SEARCH
    query = request.GET.get("q", "")
    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(city__icontains=query)
        )

    # ✅ AVAILABILITY FILTER (THIS IS THE PART YOU ASKED ABOUT)
    availability = request.GET.get("availability", "")
    if availability == "available":
        doctors = doctors.filter(is_available=True)
    elif availability == "offline":
        doctors = doctors.filter(is_available=False)

    return render(
        request,
        "petadmin/doctorAdmin.html",
        {
            "doctors": doctors,
            "query": query,
            "availability": availability,
        }
    )


def deleteDoctor(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    doctor = get_object_or_404(doctor_registration, id=id)
    doctor.delete()
    messages.success(request, "Doctor removed successfully")
    return redirect("petadmin:doctorAdmin")


def toggleDoctorAvailability(request, id):
    if "admin_id" not in request.session:
        messages.error(request, "Admin login required")
        return redirect("petadmin:loginAdmin")

    doctor = get_object_or_404(doctor_registration, id=id)

    doctor.is_active = not doctor.is_active
    doctor.is_available = doctor.is_active
    doctor.is_checkout = not doctor.is_active

    doctor.save(update_fields=["is_active", "is_available", "is_checkout"])

    messages.success(request, f"{doctor.name} availability updated")
    return redirect("petadmin:doctorAdmin")


def doctorDetailsAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    doctor = get_object_or_404(doctor_registration, id=id)
    return render(request, "petadmin/doctorDetailsAdmin.html", {"doctor": doctor})

def forceDoctorOnline(request, id):
    doctor = get_object_or_404(doctor_registration, id=id)

    doctor.is_active = True          # ✅ MASTER FLAG
    doctor.is_available = True       # 🔄 SYNC
    doctor.is_checkout = False

    doctor.save(update_fields=["is_active", "is_available", "is_checkout"])

    messages.success(request, f"Dr. {doctor.name} is now ONLINE")
    return redirect("petadmin:doctorAdmin")


def forceDoctorOffline(request, id):
    doctor = get_object_or_404(doctor_registration, id=id)

    doctor.is_active = False         # ✅ MASTER FLAG
    doctor.is_available = False      # 🔄 SYNC
    doctor.is_checkout = True

    doctor.save(update_fields=["is_active", "is_available", "is_checkout"])

    messages.warning(request, f"Dr. {doctor.name} is now OFFLINE")
    return redirect("petadmin:doctorAdmin")


# ================== VOLUNTEERS ==================

def volunteerAdmin(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    volunteers = volunteer_registration.objects.all()
    return render(request, "petadmin/volunteerAdmin.html", {"volunteers": volunteers})


def toggleVolunteerAvailability(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    volunteer = get_object_or_404(volunteer_registration, id=id)

    # ❌ Block availability change if volunteer is disabled
    if not volunteer.is_active:
        messages.error(request, "Cannot change availability of a disabled volunteer.")
        return redirect("petadmin:volunteerAdmin")

    volunteer.is_available = not volunteer.is_available
    volunteer.save(update_fields=["is_available"])

    messages.success(request, "Volunteer availability updated.")
    return redirect("petadmin:volunteerAdmin")


def toggleVolunteerStatus(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    volunteer = get_object_or_404(volunteer_registration, id=id)

    volunteer.is_active = not volunteer.is_active

    # 🔒 If disabling → force offline
    if not volunteer.is_active:
        volunteer.is_available = False

    volunteer.save(update_fields=["is_active", "is_available"])

    status = "disabled" if not volunteer.is_active else "enabled"
    messages.success(request, f"Volunteer account {status} successfully.")
    return redirect("petadmin:volunteerAdmin")


def deleteVolunteer(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    volunteer = get_object_or_404(volunteer_registration, id=id)
    volunteer.delete()

    messages.warning(request, "Volunteer removed permanently.")
    return redirect("petadmin:volunteerAdmin")


# ================== USERS ==================

def userAdmin(request):
    if "admin_id" not in request.session:
        messages.error(request, "Please login as admin")
        return redirect("petadmin:loginAdmin")

    users = user_registration.objects.all()

    # 🔍 SEARCH
    query = request.GET.get("q", "")
    if query:
        users = users.filter(
            Q(name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    # 🚫 FILTER ACTIVE / BLOCKED
    status = request.GET.get("status", "")
    if status == "active":
        users = users.filter(is_active=True)
    elif status == "blocked":
        users = users.filter(is_active=False)

    # 🐾 ATTACH ADOPTION REQUEST COUNT
    for u in users:
        u.adoption_count = AdoptionRequest.objects.filter(user=u, status="Pending").count()

    return render(
        request,
        "petadmin/userAdmin.html",
        {
            "users": users,
            "query": query,
            "status": status
        }
    )


def userDetailsAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    user = get_object_or_404(user_registration, id=id)
    adoptions = AdoptionRequest.objects.filter(user=user)

    return render(
        request,
        "petadmin/userDetailsAdmin.html",
        {
            "user": user,
            "adoptions": adoptions
        }
    )


def toggleUserStatus(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    user = get_object_or_404(user_registration, id=id)
    user.is_active = not user.is_active
    user.save()

    messages.success(request, "User status updated")
    return redirect("petadmin:userAdmin")


def deleteUser(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    user = get_object_or_404(user_registration, id=id)
    user.delete()

    messages.success(request, "User deleted successfully")
    return redirect("petadmin:userAdmin")


# ================== ADOPTION PETS ==================

def adoptionPetsAdmin(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    pets = Pet.objects.all()
    return render(request, "petadmin/adoptionPetsAdmin.html", {"pets": pets})


def addPetAdmin(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    if request.method == "POST":
        Pet.objects.create(
            name=request.POST.get("name"),
            pet_type=request.POST.get("pet_type"),
            age=request.POST.get("age"),
            description=request.POST.get("description"),
            vaccinated=request.POST.get("vaccinated") == "on",
            status=request.POST.get("status"),
            image=request.FILES.get("image")
        )

        messages.success(request, "Adoption pet added successfully")
        return redirect("petadmin:adoptionPetsAdmin")

    return render(request, "petadmin/addPetAdmin.html")


def editPetAdmin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    adoption = AdoptionRequest.objects.filter(pet=pet).first()

    if request.method == "POST":
        pet.name = request.POST.get("name")
        pet.pet_type = request.POST.get("pet_type")
        pet.age = request.POST.get("age")
        pet.description = request.POST.get("description")
        pet.status = request.POST.get("status")  # 🔥 IMPORTANT
        pet.vaccinated = "vaccinated" in request.POST

        if "image" in request.FILES:
            pet.image = request.FILES["image"]

        pet.save()
        return redirect("petadmin:adoptionPetsAdmin")

    return render(request, "petadmin/editPetAdmin.html", {
        "pet": pet,
        "adoption": adoption,
    })


def deletePetAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    pet = get_object_or_404(Pet, id=id)
    pet.delete()

    messages.success(request, "Pet removed successfully")
    return redirect("petadmin:adoptionPetsAdmin")

# ================= CONSULTATIONS ==================

def consultationAdmin(request):
    consultations = Consultation.objects.all().order_by("-created_at")
    return render(request, "petadmin/consultationAdmin.html", {"consultations": consultations})

# ================== ADOPTION REQUESTS ==================

def adoption_requests(request):
    user_id = request.GET.get("user")

    if user_id:
        requests = AdoptionRequest.objects.filter(user_id=user_id).select_related("user", "pet")
    else:
        requests = AdoptionRequest.objects.select_related("user", "pet")

    return render(request, "petadmin/adoption_requests.html", {
        "requests": requests
    })



def update_adoption_status(request, id, status):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    adoption = get_object_or_404(AdoptionRequest, id=id)

    if status not in ["Approved", "Rejected", "Visited"]:
        messages.error(request, "Invalid status")
        return redirect("petadmin:adminAdoptions")

    adoption.status = status

    # ✅ Safety: ensure visit_date exists
    if status in ["Approved", "Visited"] and not adoption.visit_date:
        adoption.visit_date = now().date()

    adoption.save()
    messages.success(request, f"Marked as {status}")

    return redirect("petadmin:adminAdoptionView", id=id)


def adminAdoptions(request):
    users = user_registration.objects.all()
    adoptions = AdoptionRequest.objects.select_related("user", "pet")

    selected_user = request.GET.get("user")
    status = request.GET.get("status")

    if selected_user:
        adoptions = adoptions.filter(user_id=selected_user)

    if status:
        adoptions = adoptions.filter(status=status)

    return render(request, "Petadmin/adoptions_list.html", {
    "adoptions": adoptions,
    "users": users,
    "selected_user": selected_user,
    "selected_status": status,
})


def adminAdoptionView(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    adoption = get_object_or_404(
        AdoptionRequest.objects.select_related("user", "pet"),
        id=id
    )

    return render(request, "Petadmin/adminAdoptionView.html", {
    "adoption": adoption
})


@require_POST
def deleteAdoptionRequest(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    adoption = get_object_or_404(AdoptionRequest, id=id)
    adoption.delete()

    messages.success(request, "Adoption request deleted successfully.")
    return redirect("petadmin:adminAdoptions")


# ================== SERVICES ==================

def groomingServicesAdmin(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    services = Service.objects.filter(service_type="grooming")

    return render(request, "Petadmin/servicesAdmin.html", {
        "services": services
    })


def addGroomingServiceAdmin(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    form = ServiceForm(request.POST or None, initial={"service_type": "grooming"})

    if form.is_valid():
        service = form.save(commit=False)
        service.service_type = "grooming"
        service.save()

        messages.success(request, "Grooming service added successfully")
        return redirect("petadmin:groomingServicesAdmin")

    return render(request, "petadmin/addServiceAdmin.html", {
        "form": form,
        "title": "Add Grooming Service"
    })


def editGroomingServiceAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    service = get_object_or_404(Service, id=id, service_type="grooming")

    form = ServiceForm(request.POST or None, instance=service)

    if form.is_valid():
        form.save()
        messages.success(request, "Grooming service updated successfully")
        return redirect("petadmin:groomingServicesAdmin")

    return render(request, "petadmin/services/service_form.html", {
        "form": form,
        "title": "Edit Grooming Service"
    })


def deleteGroomingServiceAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    if request.method != "POST":
        return redirect("petadmin:groomingServicesAdmin")

    service = get_object_or_404(Service, id=id, service_type="grooming")

    # ✅ SOFT DELETE
    service.is_active = False
    service.save(update_fields=["is_active"])

    messages.success(request, "Grooming service removed successfully")
    return redirect("petadmin:groomingServicesAdmin")


# ================= GROOMING BOOKINGS =================

def adminGroomingBookings(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    bookings = GroomingBooking.objects.select_related(
        "user", "volunteer"
    ).order_by("-created_at")

    volunteers = volunteer_registration.objects.filter(is_available=True)

    return render(request, "petadmin/groomingBookingsAdmin.html", {
        "bookings": bookings,
        "volunteers": volunteers
    })


# ================= ASSIGN VOLUNTEER =================

def assignGroomingVolunteer(request, booking_id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    booking = get_object_or_404(GroomingBooking, id=booking_id)

    if request.method == "POST":
        volunteer_id = request.POST.get("volunteer_id")
        volunteer = get_object_or_404(volunteer_registration, id=volunteer_id)

        booking.volunteer = volunteer
        booking.status = "Assigned"
        booking.save()

        # 🔔 CREATE NOTIFICATION
        VolunteerNotification.objects.create(
            volunteer=volunteer,
            title="New Grooming Assignment",
            message=f"You have been assigned a new grooming task for {booking.user.name} on {booking.date} at {booking.start_time}.",
            link="/volunteer/tasks/"
        )

        messages.success(request, "Volunteer assigned and notified successfully")
        return redirect("petadmin:adminGroomingBookings")

# ================= UPDATE STATUS =================

def updateGroomingStatus(request, booking_id, status):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    booking = get_object_or_404(GroomingBooking, id=booking_id)

    if status not in ["Pending", "Assigned", "In Progress", "Completed", "Cancelled"]:
        messages.error(request, "Invalid status")
        return redirect("petadmin:adminGroomingBookings")

    booking.status = status
    booking.save()

    messages.success(request, f"Booking marked as {status}")
    return redirect("petadmin:adminGroomingBookings")

# ================= DAYCARE SERVICES ADMIN =================


def daycarePlansAdmin(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    plans = DaycarePlan.objects.all()   # ✅ CORRECT

    return render(request, "petadmin/daycareServicesAdmin.html", {
        "plans": plans
    })

# ===============================
# ADD DAYCARE PLAN (ADMIN)
# ===============================
def addDaycarePlanAdmin(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    if request.method == "POST":
        form = DaycarePlanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("petadmin:daycarePlansAdmin")
        else:
            print(form.errors)  # 🔥 DEBUG LINE
    else:
        form = DaycarePlanForm()

    return render(request, "Petadmin/serviceformAdmin.html", {
        "form": form,
        "title": "Add Daycare Plan"
    })

# ===============================
# EDIT DAYCARE PLAN (ADMIN)
# ===============================
def editDaycarePlanAdmin(request, id):
    plan = get_object_or_404(DaycarePlan, id=id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price_per_hour = request.POST.get("price_per_hour", "").strip()
        max_days = request.POST.get("max_days", "").strip()
        description = request.POST.get("description", "")
        is_active = request.POST.get("is_active") == "on"

        # 🔒 VALIDATION
        if not name or not price_per_hour or not max_days:
            messages.error(request, "Please fill all required fields.")
            return render(
                request,
                "Petadmin/editDaycarePlanAdmin.html",
                {"plan": plan},
            )

        try:
            price_per_hour = Decimal(price_per_hour)
        except InvalidOperation:
            messages.error(request, "Price per hour must be a valid number.")
            return render(
                request,
                "Petadmin/editDaycarePlanAdmin.html",
                {"plan": plan},
            )

        try:
            max_days = int(max_days)
            if max_days < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Maximum days must be a positive number.")
            return render(
                request,
                "Petadmin/editDaycarePlanAdmin.html",
                {"plan": plan},
            )

        # ✅ SAVE (NEW MODEL FIELDS)
        plan.name = name
        plan.price_per_hour = price_per_hour
        plan.max_days = max_days
        plan.description = description
        plan.is_active = is_active
        plan.save()

        messages.success(request, "Daycare plan updated successfully.")
        return redirect("petadmin:daycarePlansAdmin")

    return render(
        request,
        "Petadmin/editDaycarePlanAdmin.html",
        {"plan": plan},
    )

# ===============================
# DELETE DAYCARE PLAN (ADMIN)
# ===============================
@require_POST
def deleteDaycarePlanAdmin(request, id):
    plan = get_object_or_404(DaycarePlan, id=id)

    plan.delete()
    messages.success(request, "Daycare plan deleted successfully.")
    return redirect("petadmin:daycarePlansAdmin")

@require_POST
def toggleDaycarePlanStatusAdmin(request, id):
    plan = get_object_or_404(DaycarePlan, id=id)
    plan.is_active = not plan.is_active
    plan.save(update_fields=["is_active"])

    status = "activated" if plan.is_active else "deactivated"
    messages.success(request, f"Daycare plan {status} successfully.")

    return redirect("petadmin:daycarePlansAdmin")

# ================== VOLUNTEER APPLICATIONS ==================

def volunteerApplicationsAdmin(request):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    applications = VolunteerApplication.objects.all().order_by("-applied_at")

    return render(
        request,
        "Petadmin/volunteerApplicationsAdmin.html",
        {"applications": applications}
    )


def approveVolunteerApplicationAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    application = get_object_or_404(VolunteerApplication, id=id)

    if application.status != "Pending":
        messages.warning(request, "Application already processed.")
        return redirect("petadmin:volunteerApplicationsAdmin")

    application.status = "Approved"
    application.generate_code()
    application.save()

    send_mail(
        subject="PetPal Volunteer Authorization Code",
        message=(
            f"Hi {application.name},\n\n"
            f"Your volunteer application has been approved.\n\n"
            f"Authorization Code: {application.authorization_code}\n"
            f"This code is valid for 24 hours.\n\n"
            f"Visit PetPal to complete signup."
        ),
        from_email="petpal@support.com",
        recipient_list=[application.email],
        fail_silently=True,
    )

    messages.success(request, "Application approved and code sent.")
    return redirect("petadmin:volunteerApplicationsAdmin")


def rejectVolunteerApplicationAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    application = get_object_or_404(VolunteerApplication, id=id)

    if application.status != "Pending":
        messages.warning(request, "Application already processed.")
        return redirect("petadmin:volunteerApplicationsAdmin")

    application.status = "Rejected"
    application.authorization_code = None
    application.code_used = False
    application.save()

    messages.success(request, "Application rejected.")
    return redirect("petadmin:volunteerApplicationsAdmin")
