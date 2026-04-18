# GitHub Setup Script for Excel Dashboard
# Run this in PowerShell after you've created a GitHub repository

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if gh is available
$ghPath = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghPath) {
    Write-Host "GitHub CLI not found. Please install it from:" -ForegroundColor Yellow
    Write-Host "https://github.com/cli/cli/releases" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or use these manual steps:" -ForegroundColor Cyan
}

Write-Host "STEP 1: Create GitHub Repository" -ForegroundColor Green
Write-Host "  1. Go to https://github.com and sign in" -ForegroundColor White
Write-Host "  2. Click '+' and select 'New repository'" -ForegroundColor White
Write-Host "  3. Name: excel-dashboard" -ForegroundColor White
Write-Host "  4. Select 'Public'" -ForegroundColor White
Write-Host "  5. Click 'Create repository'" -ForegroundColor White
Write-Host ""

Write-Host "STEP 2: After creating repo, run these commands:" -ForegroundColor Green
Write-Host "  git remote add origin https://github.com/YOUR_USERNAME/excel-dashboard.git" -ForegroundColor Yellow
Write-Host "  git branch -M main" -ForegroundColor Yellow
Write-Host "  git push -u origin main" -ForegroundColor Yellow
Write-Host ""

Write-Host "STEP 3: Deploy to Render" -ForegroundColor Green
Write-Host "  1. Go to https://render.com and sign up with GitHub" -ForegroundColor White
Write-Host "  2. Click 'New' -> 'Web Service'" -ForegroundColor White
Write-Host "  3. Connect your GitHub repository" -ForegroundColor White
Write-Host "  4. Set Build Command: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  5. Set Start Command: gunicorn app:app --bind 0.0.0.0:\$PORT" -ForegroundColor White
Write-Host "  6. Click 'Create Web Service'" -ForegroundColor White
Write-Host ""

Write-Host "Your project is ready for deployment!" -ForegroundColor Green