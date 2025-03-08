from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password

from .forms import CustomLoginForm

# Login View
def custom_login(request):
    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser:
                return redirect("admin_app:admin_dashboard")
            elif user.role == "faculty":
                return redirect("faculty_app:faculty_dashboard")
            else:
                return redirect("student_app:student_dashboard")
    else:
        form = CustomLoginForm()

    return render(request, "registration/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect('registration:login')
