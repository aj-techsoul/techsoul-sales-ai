@echo off
echo ==============================================
echo Git Force Push Automator for TechSoul-AI
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
git commit -m "Initial force push of sales AI repository"

:: Rename branch to main
git branch -M main

:: Force push files to GitHub
echo Force pushing files to GitHub (main branch)...
git push -u origin main --force

echo.
echo Process complete.
pause
