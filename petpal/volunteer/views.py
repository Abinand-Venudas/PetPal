from django.shortcuts import render
# def volunteerHome(request):
#     return render(request, "volunteer/volunteer.html")  
from .models import volunteer_registration
from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.

def volunteerSignup(request):
    if request.method == "POST":
        vname = request.POST.get("vname")
        vemail = request.POST.get("vemail")
        vpassword = request.POST.get("vpassword")
        vcpassword = request.POST.get("vcpassword")
        vphone = request.POST.get("phone")
        vaddress = request.POST.get("vaddress")
        skills = request.POST.get("skills")
        vfile = request.FILES.get("vfile")
        if vpassword == vcpassword:
            # messages.error(request, "Passwords do not match.")
            # return redirect('userReg')
        # Check if the email already exists
            if volunteer_registration.objects.filter(email=vemail).exists():
                messages.error(request, "Email already registered.")
                return redirect('volunteerSignup')
            else:
                vfile = request.FILES.get("vfile")
                volunteer = volunteer_registration(
                    name=vname,
                    email=vemail,
                    password=vpassword,
                    phone=vphone,
                    address=vaddress,
                    proof=vfile,
                    skills=skills
                )
                volunteer.save()
                messages.success(request, "Registration successful.")
                return redirect('volunteerLogin')
    return render(request, "volunteer/volunteerSignup.html")

def volunteerLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            volunteer = volunteer_registration.objects.get(email=email, password=password)
            messages.success(request, "Login successful.")
            return redirect('volunteerHome')
        except volunteer_registration.DoesNotExist:
            messages.error(request, "Invalid email or password.")
    return render(request, "volunteer/volunteerLogin.html")

def volunteerHome(request):
    return render(request, "volunteer/volunteerHome.html")  
def volunteerAppointments(request):
    return render(request, "volunteer/volunteerAppointments.html")
def volunteerPets(request):
    return render(request, "volunteer/volunteerPets.html")
def volunteerNotification(request):
    return render(request, "volunteer/volunteerNotification.html")
# Create your views here.
