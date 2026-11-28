import calendar
from datetime import date
from functools import wraps

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .forms import (
    ProjectForm, ProjectMemberFormSet, ProjectEditForm, EditMemberFormSet,
    IdeaForm, MeetingForm, ContactForm,
)
from .models import Project, ProjectImage, Idea, ClubMeeting, Contact


def login_required_to_post(view):
    """Anyone can view the page, but submitting its form needs a login."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST' and not request.user.is_authenticated:
            return redirect('accounts:login')
        return view(request, *args, **kwargs)
    return wrapper


def _is_pending_member(request, project):
    """Someone added to the project's team, while the project is still awaiting approval."""
    return (
        request.user.is_authenticated
        and not project.is_approved
        and project.members.filter(user=request.user).exists()
    )


def _can_manage(request, project):
    return _is_admin(request) or _is_pending_member(request, project)


def _is_admin(request):
    return request.user.is_authenticated and request.session.get('is_admin')


def _notify_admin_of_new_project(request, project):
    if not settings.ADMIN_EMAIL:
        return

    review_url = request.build_absolute_uri(reverse('dashboard:admin'))
    send_mail(
        subject='New project submitted for approval',
        message=(
            f"A new project was submitted and is waiting for approval.\n\n"
            f"Title: {project.title}\n"
            f"Description: {project.description}\n\n"
            f"Review, edit and approve it here: {review_url}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )


def _notify_admin_of_new_idea(request, idea):
    if not settings.ADMIN_EMAIL:
        return

    ideas_url = request.build_absolute_uri(reverse('landing_page:ideas'))
    send_mail(
        subject='New project IDEA posted',
        message=(
            f"A new project idea was posted on the Project Ideas page.\n\n"
            f"Idea: {idea.description}\n\n"
            f"View all ideas here: {ideas_url}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )


def index(request):

    if request.method == 'POST':
        # only a logged-in admin can add a meeting
        if not _is_admin(request):
            return redirect('landing_page:index')

        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing_page:index')
    else:
        form = MeetingForm()

    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year, month = today.year, today.month

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    meetings_this_month = ClubMeeting.objects.filter(date__year=year, date__month=month)
    meetings_by_day = {}
    for meeting in meetings_this_month:
        meetings_by_day.setdefault(meeting.date.day, []).append(meeting)

    weeks = []
    for week in month_days:
        week_data = []
        for day in week:
            week_data.append({
                'day': day,
                'is_today': day != 0 and date(year, month, day) == today,
                'meetings': meetings_by_day.get(day, []) if day != 0 else [],
            })
        weeks.append(week_data)

    prev_month, prev_year = (month - 1, year) if month > 1 else (12, year - 1)
    next_month, next_year = (month + 1, year) if month < 12 else (1, year + 1)

    return render(request, 'landing_page/index.html', {
        'weeks': weeks,
        'weekday_labels': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'month_name': calendar.month_name[month],
        'year': year,
        'month': month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'upcoming_meetings': ClubMeeting.objects.filter(date__gte=today),
        'form': form,
        'is_admin': _is_admin(request),
    })


def delete_meeting(request, meeting_id):
    if not _is_admin(request):
        return redirect('landing_page:index')

    if request.method == 'POST':
        meeting = get_object_or_404(ClubMeeting, pk=meeting_id)
        meeting.delete()

    return redirect('landing_page:index')


def about(request):
    return render(request, 'landing_page/about.html')


def _save_new_images(project, files):
    for uploaded in files:
        ProjectImage.objects.create(project=project, image=uploaded)


@login_required_to_post
def projects(request):
    submitted = False

    if request.method == 'POST':
        # logged-in members can submit a project, but it starts unapproved
        form = ProjectForm(request.POST, request.FILES)
        member_formset = ProjectMemberFormSet(request.POST, instance=Project())
        if form.is_valid() and member_formset.is_valid():
            with transaction.atomic():
                project = form.save(commit=False)
                project.is_approved = False
                project.save()
                _save_new_images(project, form.cleaned_data['new_images'])
                member_formset.instance = project
                member_formset.save()
            _notify_admin_of_new_project(request, project)
            return redirect(reverse('landing_page:projects') + '?submitted=1#add-project')
    else:
        form = ProjectForm()
        member_formset = ProjectMemberFormSet(instance=Project())
        submitted = request.GET.get('submitted') == '1'

    approved = Project.objects.filter(is_approved=True).prefetch_related('images', 'members')

    # projects still awaiting approval are shown only to the people added to them
    awaiting = Project.objects.none()
    if request.user.is_authenticated:
        awaiting = (
            Project.objects.filter(is_approved=False, members__user=request.user)
            .distinct()
            .prefetch_related('images', 'members')
        )

    return render(request, 'landing_page/projects.html', {
        'awaiting_projects': awaiting,
        'ongoing_projects': approved.filter(status='ongoing'),
        'completed_projects': approved.filter(status='completed'),
        'form': form,
        'member_formset': member_formset,
        'submitted': submitted,
    })


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related('images', 'members'),
        pk=project_id,
    )
    #pending projects can only be viewed by admins and the people added to them
    can_edit = _can_manage(request, project)
    if not project.is_approved and not can_edit:
        raise Http404
    return render(request, 'landing_page/project_detail.html', {'project': project, 'can_edit': can_edit})


def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # admins, or the project's own team while it is still awaiting approval
    if not _can_manage(request, project):
        return redirect('landing_page:projects')

    back_url = reverse('landing_page:project_detail', args=[project.pk])

    if request.method == 'POST':
        form = ProjectEditForm(request.POST, request.FILES, instance=project)
        member_formset = EditMemberFormSet(request.POST, instance=project)
        if form.is_valid() and member_formset.is_valid():
            with transaction.atomic():
                form.save()
                form.cleaned_data['delete_images'].delete()
                _save_new_images(project, form.cleaned_data['new_images'])
                member_formset.save()
            return redirect(back_url)
    else:
        form = ProjectEditForm(instance=project)
        member_formset = EditMemberFormSet(instance=project)

    return render(request, 'landing_page/edit_project.html', {
        'project': project,
        'form': form,
        'member_formset': member_formset,
        'back_url': back_url,
    })


def update_project_status(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # admins, or the project's own team while it is still awaiting approval
    if not _can_manage(request, project):
        return redirect('landing_page:projects')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Project.STATUS_CHOICES):
            project.status = new_status
            project.save()

    return redirect('landing_page:projects')


def approve_project(request, project_id):
    if not _is_admin(request):
        return redirect('dashboard:admin')

    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        project.is_approved = True
        project.admin_approved_by = request.user
        project.admin_approved_at = timezone.now()
        project.save()

    return redirect('dashboard:admin')


def reject_project(request, project_id):
    if not _is_admin(request):
        return redirect('dashboard:admin')

    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        project.delete()

    return redirect('dashboard:admin')


def delete_project(request, project_id):
    if not _is_admin(request):
        return redirect('landing_page:projects')

    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        project.delete()

    return redirect('landing_page:projects')


def delete_idea(request, idea_id):
    if not _is_admin(request):
        return redirect('landing_page:ideas')

    if request.method == 'POST':
        idea = get_object_or_404(Idea, pk=idea_id)
        idea.delete()

    return redirect('landing_page:ideas')


@login_required_to_post
def ideas(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save()
            _notify_admin_of_new_idea(request, idea)
            return redirect('landing_page:ideas')
    else:
        form = IdeaForm()

    return render(request, 'landing_page/ideas.html', {
        'ideas': Idea.objects.all(),
        'form': form,
    })

def contact(request):
    if request.method == 'POST':
        # only a logged-in admin can add a contact
        if not _is_admin(request):
            return redirect('landing_page:contact')

        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing_page:contact')
    else:
        form = ContactForm()

    return render(request, 'landing_page/contact.html', {
        'contacts': Contact.objects.all(),
        'form': form,
        'is_admin': _is_admin(request),
    })


def delete_contact(request, contact_id):
    if not _is_admin(request):
        return redirect('landing_page:contact')

    if request.method == 'POST':
        person = get_object_or_404(Contact, pk=contact_id)
        person.delete()

    return redirect('landing_page:contact')

#Add other views here