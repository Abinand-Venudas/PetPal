from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import user_registration
from django.contrib import messages
# Create your views here.

def home(request):
    return render(request, "index.html")     
def userLogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = user_registration.objects.get(username=username, password=password)
            messages.success(request, "Login successful.")
            return redirect('userHome')
        except user_registration.DoesNotExist:
            messages.error(request, "Invalid username or password.")
    return render(request, "user/userLogin.html")

def userReg(request):
    if request.method == "POST":
        name1 = request.POST.get("name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        cpassword = request.POST.get("password2")
        if password == cpassword:
            # messages.error(request, "Passwords do not match.")
            # return redirect('userReg')
        # Check if the email already exists
            if user_registration.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            elif user_registration.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
            else:
                # return redirect('userReg')
                user = user_registration(name=name1, email=email,username=username, password=password)
                user.save()
                messages.success(request, "Registration successful.")
                return redirect('login')
    return render(request, "user/userReg.html")

def grooming(request):
    return render(request, "user/groom.html")
def daycare(request):
    return render(request, "user/daycare.html")
def consultation(request):
    return render(request, "user/consultation.html")
def userForm(request):
    return render(request, "user/userForm.html")
def adoptionlist(request):
    return render(request, "user/adoptionlist.html")  
def userHome(request):
    return render(request, "user/userHome.html")
     



