from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from accounts.models import User
from accounts.forms import CustomUserCreationForm
from landing_page.models import Project

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
        'pending_projects': Project.objects.filter(is_approved=False)
            .select_related('admin_approved_by')
            .prefetch_related('images', 'members'),
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

    if request.session.get('is_staff_member'):
        return redirect('dashboard:staff')
    return redirect('dashboard:admin')

@login_required
def staff_index(request):

    #only users who passed the staff passkey check can view this
    if not request.session.get('is_staff_member'):
        return redirect('accounts:staff_login')

    #staff can do everything admins can, including adding users
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:staff')
    else:
        form = CustomUserCreationForm()

    pending = (
        Project.objects.filter(is_approved=False)
        .select_related('admin_approved_by')
        .prefetch_related('images', 'members')
    )
    return render(request, 'dashboard/staff.html', {
        'users': User.objects.all().order_by('username'),
        'form': form,
        'admin_reviewed_projects': pending.filter(admin_approved_by__isnull=False),
        'unreviewed_projects': pending.filter(admin_approved_by__isnull=True),
    })
