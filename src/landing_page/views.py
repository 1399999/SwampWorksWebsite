import calendar
from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import ProjectForm, IdeaForm, MeetingForm
from .models import Project, Idea, ClubMeeting


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
            f"Description: {project.description}\n\n"
            f"Review and approve it here: {review_url}"
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


def projects(request):
    submitted = False

    if request.method == 'POST':
        # anyone - logged in or not - can submit a project, but it starts unapproved
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.is_approved = False
            project.save()
            _notify_admin_of_new_project(request, project)
            return redirect(reverse('landing_page:projects') + '?submitted=1')
    else:
        form = ProjectForm()
        submitted = request.GET.get('submitted') == '1'

    return render(request, 'landing_page/projects.html', {
        'projects': Project.objects.filter(is_approved=True),
        'form': form,
        'submitted': submitted,
    })


def update_project_status(request, project_id):
    if not _is_admin(request):
        return redirect('landing_page:projects')

    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
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
        project.save()

    return redirect('dashboard:admin')


def reject_project(request, project_id):
    if not _is_admin(request):
        return redirect('dashboard:admin')

    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        project.delete()

    return redirect('dashboard:admin')


def ideas(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing_page:ideas')
    else:
        form = IdeaForm()

    return render(request, 'landing_page/ideas.html', {
        'ideas': Idea.objects.all(),
        'form': form,
    })

def contact(request):
    return render(request, 'landing_page/contact.html')

#Add other views here