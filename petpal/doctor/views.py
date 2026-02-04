from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import doctor_registration, Appointment

def doctorLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            doctor = doctor_registration.objects.get(email=email, password=password)
            request.session["doctor_id"] = doctor.id
            request.session["doctor_name"] = doctor.name
            return redirect("doctor:doctorHome")
        except doctor_registration.DoesNotExist:
            messages.error(request, "Invalid email or password")

    return render(request, "doctor/doctorLogin.html")


def doctorSignup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        city = request.POST.get("city")
        specialization = request.POST.get("specialization")
        experience = request.POST.get("experience")
        license_no = request.POST.get("license")
        clinic = request.POST.get("clinic")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        image = request.FILES.get("image")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("doctor:doctorSignup")

        if doctor_registration.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("doctor:doctorSignup")

        doctor = doctor_registration(
            name=name,
            email=email,
            phone=phone,
            city=city,
            specialization=specialization,
            experience=experience,
            license=license_no,
            clinic=clinic,
            password=password,
            image=image
        )
        doctor.save()

        messages.success(request, "Doctor registered successfully")
        return redirect("doctor:doctorLogin")

    return render(request, "doctor/doctorSignup.html")


def doctorHome(request):
    doctor_id = request.session.get("doctor_id")
    doctor = get_object_or_404(doctor_registration, id=doctor_id)

    appointments = Appointment.objects.filter(doctor=doctor).order_by("date", "time")

    return render(request, "doctor/doctorHome.html", {
        "doctor": doctor,
        "appointments": appointments
    })


def updateAppointment(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = status
    appointment.save()
    return redirect("doctor:doctorHome")

def doctoractive(request):
    doctor = doctor_registration.objects.get(id=request.session["doctor_id"])

    doctor.is_active = True
    doctor.is_available = True
    doctor.is_checkout = False

    doctor.save(update_fields=["is_active", "is_available", "is_checkout"])
    return redirect("doctor:doctorHome")


def doctorcheckout(request):
    doctor = doctor_registration.objects.get(id=request.session["doctor_id"])

    doctor.is_active = False
    doctor.is_available = False
    doctor.is_checkout = True

    doctor.save(update_fields=["is_active", "is_available", "is_checkout"])
    return redirect("doctor:doctorHome")

