from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def redirect_by_role(user):
    if user.role == 'manager':
        return redirect('manager_dashboard')
    elif user.role == 'staff':
        return redirect('staff_dashboard')
    else:
        return redirect('client_dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')
