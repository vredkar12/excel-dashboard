@echo off
REM Git commit and push dashboard theme changes to GitHub
REM This will trigger GitHub Actions to deploy to Azure App Service

cd /d "c:\Users\Vishal\New folder"

echo.
echo ========================================
echo GitHub Deployment Script
echo ========================================
echo.

REM Check if git is available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Install from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Current status:
git status
echo.

REM Add changes
echo Adding files...
git add templates/index.html
echo.

REM Commit with message
echo Committing changes...
git commit -m "Update dashboard with peach pink and white theme"
echo.

REM Push to GitHub
echo Pushing to GitHub (this will trigger Azure deployment)...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo Changes pushed to GitHub
    echo GitHub Actions will automatically deploy to Azure
    echo.
    echo Check deployment status at:
    echo https://portal.azure.com/
    echo.
    echo Your dashboard: https://dashboards.azurewebsites.net/
    echo.
) else (
    echo.
    echo ERROR: Failed to push to GitHub
    echo Make sure you have:
    echo - Git credentials configured
    echo - GitHub repository set as origin
    echo.
)

pause
