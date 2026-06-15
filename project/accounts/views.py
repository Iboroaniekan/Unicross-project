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





# User = get_user_model()

# def signup(request):
    
#     if request.method == "POST":
#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password1 = request.POST.get("password1")
#         password2 = request.POST.get("password2")

#         if password1 != password2:
#             messages.error(request, "Passwords do not match.")
#             return redirect('/')  # show signup form popup

#         if User.objects.filter(email=email).exists():
#             messages.error(request, "Email already registered.")
#             return redirect('/')  # Popup will show error

#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password1,
#             is_staff=False,   # regular user by default
#             is_superuser=False
#         )

#         messages.success(request, "Account created. Please log in.")
#         return redirect('/')  # Show login form popup

#     return redirect('/')








