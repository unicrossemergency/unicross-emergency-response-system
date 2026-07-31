
# Create your views here.
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages



def staff_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("/admin/")

        messages.error(request, "login_error")
        return redirect("/")

    return redirect("/")