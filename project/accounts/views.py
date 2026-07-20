from django.contrib.auth import authenticate, login 
from django.shortcuts import redirect,render
from django.contrib import messages
from django.contrib.auth import get_user_model



# Create your views here.
User = get_user_model()
#Function to Login to admin dashboard
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # get the first user with this email
            user_obj = User.objects.filter(email=email).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = None
        except Exception:
            user = None

        if user and user.is_staff:
            login(request, user)
            return redirect("/admin/")
        else:
            messages.error(request, "Invalid email or password")
    return redirect("/")









