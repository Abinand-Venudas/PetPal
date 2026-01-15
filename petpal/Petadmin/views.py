from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from petapp.models import AdoptionRequest, Consultation, Pet, user_registration
from .models import Pro_Admin
from doctor.models import doctor_registration
from volunteer.models import volunteer_registration


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

    return render(request, "petadmin/loginAdmin.html")


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
        "petadmin/homeAdmin.html",
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

    query = request.GET.get("q", "")
    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(city__icontains=query)
        )

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
    doctor.is_available = not doctor.is_available
    doctor.save()

    messages.success(request, f"{doctor.name} availability updated")
    return redirect("petadmin:doctorAdmin")


def doctorDetailsAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    doctor = get_object_or_404(doctor_registration, id=id)
    return render(request, "petadmin/doctorDetailsAdmin.html", {"doctor": doctor})


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
    volunteer.is_available = not volunteer.is_available
    volunteer.save()

    messages.success(request, "Volunteer availability updated")
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


def editPetAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    pet = get_object_or_404(Pet, id=id)

    if request.method == "POST":
        pet.name = request.POST.get("name")
        pet.pet_type = request.POST.get("pet_type")
        pet.age = request.POST.get("age")
        pet.description = request.POST.get("description")
        pet.vaccinated = request.POST.get("vaccinated") == "on"
        pet.status = request.POST.get("status")

        if request.FILES.get("image"):
            pet.image = request.FILES.get("image")

        pet.save()
        messages.success(request, "Pet updated successfully")
        return redirect("petadmin:adoptionPetsAdmin")

    return render(request, "petadmin/editPetAdmin.html", {"pet": pet})


def deletePetAdmin(request, id):
    if "admin_id" not in request.session:
        return redirect("petadmin:loginAdmin")

    pet = get_object_or_404(Pet, id=id)
    pet.delete()

    messages.success(request, "Pet removed successfully")
    return redirect("petadmin:adoptionPetsAdmin")


# ================== CONSULTATIONS ==================

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
    adoption = get_object_or_404(AdoptionRequest, id=id)
    adoption.status = status
    adoption.save()
    messages.success(request, f"Request {status} successfully.")
    return redirect("petadmin:adoption_requests")

def adminAdoptions(request):
    user_id = request.GET.get("user")

    adoptions = AdoptionRequest.objects.select_related("user", "pet")

    if user_id:
        adoptions = adoptions.filter(user_id=user_id)
        selected_user = user_registration.objects.get(id=user_id)
    else:
        selected_user = None

    return render(request, "Petadmin/adoptionRequest.html", {
        "adoptions": adoptions,
        "selected_user": selected_user
    })

def adminAdoptionView(request, id):
    # Ensure admin is logged in
    if not request.session.get("admin_id"):
        return redirect("petadmin:loginAdmin")

    adoption = get_object_or_404(AdoptionRequest, id=id)

    return render(request, "petadmin/adminAdoptionView.html", {
        "adoption": adoption
    })