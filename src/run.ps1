$subDir = "mysite"
$scriptName = "manage.py"
$scriptPath = Join-Path -Path $subDir -ChildPath $scriptName

# REMOVE IN PRODUCTION
python $scriptPath "makemigrations"
# REMOVE IN PRODUCTION
python $scriptPath "migrate"
# CHANGE IN PRODUCTION
python $scriptPath "createsuperuser"
