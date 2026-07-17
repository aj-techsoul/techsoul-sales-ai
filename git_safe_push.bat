@echo off
echo ==============================================
echo Git Safe Push Automator (Keeping Remote MDs)
echo ==============================================

cd /d "%~dp0"

:: Try to find git
set "GIT_CMD=git"
where git >nul 2>nul
if %errorlevel% neq 0 (
    :: Try standard installation paths
    if exist "%ProgramFiles%\Git\cmd\git.exe" (
        set "GIT_CMD=%ProgramFiles%\Git\cmd\git.exe"
    ) else if exist "%ProgramFiles(x86)%\Git\cmd\git.exe" (
        set "GIT_CMD=%ProgramFiles(x86)%\Git\cmd\git.exe"
    ) else if exist "%LocalAppData%\Programs\Git\cmd\git.exe" (
        set "GIT_CMD=%LocalAppData%\Programs\Git\cmd\git.exe"
    ) else (
        echo Error: Git is not installed or not in PATH.
        echo Please restart VS Code to reload your environment path variables.
        echo If that doesn't work, install Git from https://git-scm.com/
        pause
        exit /b
    )
)

:: Initialize git repository if not already initialized
if not exist .git (
    echo Initializing Git repository...
    "%GIT_CMD%" init
)

:: Configure remote origin
echo Configuring remote origin to https://github.com/aj-techsoul/techsoul-sales-ai.git...
"%GIT_CMD%" remote remove origin >nul 2>nul
"%GIT_CMD%" remote add origin https://github.com/aj-techsoul/techsoul-sales-ai.git

:: Fetch from remote
echo Fetching remote repository...
"%GIT_CMD%" fetch origin

:: Stage local files
echo Staging local files...
"%GIT_CMD%" add .

:: Configure local git user if not set
"%GIT_CMD%" config user.name >nul 2>nul
if %errorlevel% neq 0 (
    echo Configuring local Git user.name...
    "%GIT_CMD%" config user.name "TechSoul AI Developer"
)
"%GIT_CMD%" config user.email >nul 2>nul
if %errorlevel% neq 0 (
    echo Configuring local Git user.email...
    "%GIT_CMD%" config user.email "developer@techsoul.ai"
)

:: Commit local files
echo Committing local files...
"%GIT_CMD%" commit -m "Commit local changes before merging remote files"

:: Rename branch to main to ensure it exists
"%GIT_CMD%" branch -M main

:: Pull from remote, keeping remote versions in case of conflicts
echo Pulling existing files from remote (keeping remote versions on conflict)...
"%GIT_CMD%" pull origin main --allow-unrelated-histories -X theirs --no-edit

:: Push files to GitHub
echo Pushing files to GitHub (main branch)...
"%GIT_CMD%" push -u origin main

echo.
echo Process complete.
pause
