from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):

    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    return render(request, 'dashboard/index.html')

@login_required
def admin_index(request):

    #only users who passed the admin passkey check can view this
    if not request.session.get('is_admin'):
        return redirect('accounts:admin_login')

    #doesn't do anything special yet
    return render(request, 'dashboard/admin.html')