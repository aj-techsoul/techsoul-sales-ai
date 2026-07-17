@echo off
echo ==============================================
echo Git Push Automator for TechSoul-AI
echo ==============================================

cd /d "%~dp0"

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/ and try again.
    pause
    exit /b
)

:: Initialize git repository if not already initialized
if not exist .git (
    echo Initializing Git repository...
    git init
)

:: Configure remote origin
echo Configuring remote origin to https://github.com/aj-techsoul/techsoul-sales-ai...
git remote remove origin >nul 2>nul
git remote add origin https://github.com/aj-techsoul/techsoul-sales-ai

:: Stage files
echo Staging files...
git add .

:: Commit files
echo Committing files...
git commit -m "Initial commit of sales AI repository"

:: Rename branch to main
git branch -M main

:: Push files to GitHub
echo Pushing files to GitHub (main branch)...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [!] Direct push failed. This might happen if the remote repository is not empty.
    echo Do you want to force push? (WARNING: This will overwrite files on the remote repo).
    set /p CHOICE="Force push? (y/n): "
    if /i "%CHOICE%"=="y" (
        echo Force pushing to GitHub...
        git push -u origin main --force
    ) else (
        echo Push cancelled.
    )
)

echo.
echo Process complete.
pause
