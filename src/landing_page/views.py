import calendar
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProjectForm, IdeaForm, MeetingForm
from .models import Project, Idea, ClubMeeting


def _is_admin(request):
    return request.user.is_authenticated and request.session.get('is_admin')


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

    # keep the month in a valid range, rolling the year over as needed
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
    if request.method == 'POST':
        # only logged in users can add projects
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('landing_page:projects')
    else:
        form = ProjectForm()

    return render(request, 'landing_page/projects.html', {
        'projects': Project.objects.all(),
        'form': form,
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