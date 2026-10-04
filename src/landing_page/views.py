from django.shortcuts import render, redirect

from .forms import ProjectForm, IdeaForm
from .models import Project, Idea

# Initial landing page view.
def index(request):
    return render(request, 'landing_page/index.html')

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

def ideas(request):
    # anyone, logged in or not, can post an idea
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