import hashlib
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, ADMIN_TOKEN_LIFETIME
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
        'pending_projects': Project.objects.filter(is_approved=False).prefetch_related('images', 'members'),
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


def _hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


@login_required
def request_admin_role(request, user_id):

    #only users who passed the admin passkey check can do this
    if not request.session.get('is_admin'):
        return redirect('accounts:admin_login')

    if request.method == 'POST':
        target = get_object_or_404(User, pk=user_id)

        if target.pk == request.user.pk:
            messages.error(request, "You can't change your own role.")
        elif target.role == 'admin':
            messages.info(request, f'{target.username} is already an admin.')
        elif not target.email:
            messages.error(request, f'{target.username} has no email address, so no confirmation email can be sent.')
        else:
            #random secret that goes in the emailed link; only its hash is saved
            token = secrets.token_urlsafe(32)
            link = request.build_absolute_uri(reverse('dashboard:confirm_admin', args=[token]))
            hours = int(ADMIN_TOKEN_LIFETIME.total_seconds() // 3600)
            try:
                send_mail(
                    subject='Confirm your SwampWorks admin role',
                    message=(
                        f"Hi {target.username},\n\n"
                        f"{request.user.username} asked to make you an admin on SwampWorks.\n\n"
                        f"To accept, open this link and confirm:\n{link}\n\n"
                        f"The link works once and expires in {hours} hours. "
                        f"If you weren't expecting this, you can ignore this email and nothing will change."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[target.email],
                    fail_silently=False,
                )
            except Exception:
                messages.error(request, 'The confirmation email could not be sent. Check the email settings and try again.')
            else:
                target.admin_token_hash = _hash_token(token)
                target.admin_token_created = timezone.now()
                target.save(update_fields=['admin_token_hash', 'admin_token_created'])
                messages.success(
                    request,
                    f'Confirmation email sent to {target.email}. {target.username} becomes an admin once they open the link and confirm.',
                )

    return redirect('dashboard:admin')


@login_required
def make_regular_user(request, user_id):

    #only users who passed the admin passkey check can do this
    if not request.session.get('is_admin'):
        return redirect('accounts:admin_login')

    if request.method == 'POST':
        target = get_object_or_404(User, pk=user_id)

        if target.pk == request.user.pk:
            messages.error(request, "You can't change your own role.")
        else:
            target.role = 'user'
            target.admin_token_hash = ''
            target.admin_token_created = None
            target.save(update_fields=['role', 'admin_token_hash', 'admin_token_created'])
            messages.success(request, f'{target.username} is now a regular user.')

    return redirect('dashboard:admin')


def confirm_admin(request, token):
    #opened from the emailed link; showing the page changes nothing, only the button does
    target = User.objects.filter(admin_token_hash=_hash_token(token)).first()
    valid = bool(target and target.admin_confirmation_pending)

    if request.method == 'POST' and valid:
        target.role = 'admin'
        target.admin_token_hash = ''
        target.admin_token_created = None
        target.save(update_fields=['role', 'admin_token_hash', 'admin_token_created'])
        return render(request, 'dashboard/confirm_admin.html', {'confirmed': True, 'target': target})

    return render(request, 'dashboard/confirm_admin.html', {'valid': valid, 'target': target if valid else None})