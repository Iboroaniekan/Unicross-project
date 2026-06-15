from django.shortcuts import render

# Create your views here.
#Function to Display my Frontpage
def home(request):
    return render(request, 'index.html')
