from django.shortcuts import render, redirect
 
from .forms import ProjectForm
from .models import Project
 
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
 
def contact(request):
    return render(request, 'landing_page/contact.html')
 
#Add other views here