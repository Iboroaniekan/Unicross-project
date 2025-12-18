from django.contrib.auth import authenticate, login 
from django.shortcuts import redirect,render
from django.contrib import messages
from django.contrib.auth import get_user_model



# Create your views here.


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("/admin/")
        else:
            messages.error(request, "Invalid username or password")
            return render(request, "index.html")  # render same page with messages

    return redirect("/")




User = get_user_model()

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('/')  # show signup form popup

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('/')  # Popup will show error

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_staff=False,   # regular user by default
            is_superuser=False
        )

        messages.success(request, "Account created. Please log in.")
        return redirect('/')  # Show login form popup

    return redirect('/')

  
