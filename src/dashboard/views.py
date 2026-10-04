from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from accounts.models import User
from accounts.forms import CustomUserCreationForm

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

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:admin')
    else:
        form = CustomUserCreationForm()

    return render(request, 'dashboard/admin.html', {
        'users': User.objects.all().order_by('username'),
        'form': form,
    })

@login_required
def admin_delete_user(request, user_id):

    #only users who passed the admin passkey check can do this
    if not request.session.get('is_admin'):
        return redirect('accounts:admin_login')

    if request.method == 'POST':
        user_to_delete = get_object_or_404(User, pk=user_id)

        #prevent the logged in admin from deleting their own account
        if user_to_delete.pk != request.user.pk:
            user_to_delete.delete()

    return redirect('dashboard:admin')