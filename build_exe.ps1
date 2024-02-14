# Help
#  Run Nuitka to build executable.
#  Archive the executable as yanga.windows.amd64.<tag>.zip
#  The <tag> is the latest git tag on remote origin.

# Usage: .\build_exe.ps1
# Example: .\build_exe.ps1

# Fetch the latest git tag from remote origin
git fetch --tags

# Get the latest git tag
$tag = git describe --tags --abbrev=0
Write-Host "Latest git tag: $tag"

# Determine the path to the VERSION.txt file for cookiecutter
$cookiecutterVersionFilePath = "<path_to_cookiecutter_VERSION.txt_file>"

# Build the executable by running Nuitka
$python = ".\.venv\Scripts\python"
& $python -m nuitka --standalone --onefile `
       --include-data-dir="src/yanga/commands/project_templates/=yanga/commands/project_templates/" `
       --include-data-dir="src/yanga/gui/resources=yanga/gui/resources" `
       --include-data-files=".venv/Lib/site-packages/cookiecutter/VERSION.txt=cookiecutter" `
       --include-module=cookiecutter.extensions `
       --include-module=yanga.ybuild.stages `
       --output-dir="dist" `
       --windows-icon-from-ico="src/yanga/gui/resources/yanga.ico" `
       --main="src/yanga/ymain.py" `
       --enable-plugin=tk-inter

# Rename the output executable to match the project name
Rename-Item -Path "dist\ymain.dist\ymain.exe" -NewName "dist\yanga.exe"

# Archive the executable
$tag = $tag -replace "v", ""
$zip = "dist\yanga-$tag-windows-amd64.zip"
Compress-Archive -Path "dist\yanga.exe", "dist\yanga-*.dll" -DestinationPath $zip
Write-Host "Archive created: $zip"
