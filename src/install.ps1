# python3 -m "venv" "envsource" "env/bin/activate"
python -m "pip" "install" -r "requirements.txt"


# Make database migrations
python manage.py makemigrations
python "manage.py" "makemigrations" "landing_page"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python manage.py migrate
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Renames project
# Write-Host "Enter a new project name: (ensure name is allowed by Django before pressing enter)"
# $project_name = Read-Host

# python manage.py rename djangotemplate $project_name
# if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Run server
# python manage.py runserver

# Install tailwind dependencies
python manage.py tailwind install
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Project setup complete."

npm install --save-dev cross-env
python "manage.py" "tailwind" "install"

# python "manage.py" "tailwind" "start"
# python "manage.py" "runserver"
