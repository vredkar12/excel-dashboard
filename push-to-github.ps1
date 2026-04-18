# Git commit and push dashboard theme changes to GitHub
# This will trigger GitHub Actions to deploy to Azure App Service

Set-Location "c:\Users\Vishal\New folder"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "GitHub Deployment Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if git is available
try {
    $gitVersion = git --version 2>$null
    Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Git is not installed" -ForegroundColor Red
    Write-Host "Install from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Show current status
Write-Host "`nCurrent git status:" -ForegroundColor Cyan
git status
Write-Host ""

# Add changes
Write-Host "Adding files..." -ForegroundColor Yellow
git add templates/index.html

# Commit with message
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Update dashboard with peach pink and white theme

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

Write-Host ""
Write-Host "Pushing to GitHub (this will trigger Azure deployment)..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Changes pushed to GitHub" -ForegroundColor Green
    Write-Host "GitHub Actions will automatically deploy to Azure`n" -ForegroundColor Green
    Write-Host "Check deployment status at:" -ForegroundColor Cyan
    Write-Host "https://portal.azure.com/" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Your dashboard:" -ForegroundColor Cyan
    Write-Host "https://dashboards.azurewebsites.net/" -ForegroundColor Blue
    Write-Host ""
} else {
    Write-Host "`nERROR: Failed to push to GitHub" -ForegroundColor Red
    Write-Host "Make sure you have:" -ForegroundColor Yellow
    Write-Host "- Git credentials configured" -ForegroundColor Yellow
    Write-Host "- GitHub repository set as origin" -ForegroundColor Yellow
}

Read-Host "Press Enter to exit"
