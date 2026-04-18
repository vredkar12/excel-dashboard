# Deploy updated dashboard to Azure App Service
Set-Location "c:\Users\Vishal\New folder"

Write-Host "Deploying to Azure App Service..." -ForegroundColor Cyan

# Check if Azure CLI is installed
try {
    $azVersion = az version | Out-String
    Write-Host "Azure CLI found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Azure CLI is not installed. Install it from https://aka.ms/installazurecliwindows" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if logged in
try {
    $account = az account show 2>$null
    if ($null -eq $account) {
        Write-Host "Not logged in. Opening Azure login..." -ForegroundColor Yellow
        az login
    }
} catch {
    Write-Host "Please log in to Azure" -ForegroundColor Yellow
    az login
}

# Deploy
Write-Host "`nDeploying application..." -ForegroundColor Cyan
az webapp up --name dashboards --resource-group tira --src-path "c:\Users\Vishal\New folder"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSUCCESS! Dashboard updated on Azure" -ForegroundColor Green
    Write-Host "Visit: https://dashboards.azurewebsites.net/" -ForegroundColor Green
} else {
    Write-Host "`nDEPLOYMENT FAILED" -ForegroundColor Red
    Write-Host "Error code: $LASTEXITCODE" -ForegroundColor Red
}

Read-Host "`nPress Enter to exit"
