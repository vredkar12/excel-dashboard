@echo off
REM Deploy updated dashboard to Azure App Service
cd /d "c:\Users\Vishal\New folder"

echo Deploying to Azure App Service...
az webapp up --name dashboards --resource-group tira --src-path "c:\Users\Vishal\New folder"

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS! Dashboard updated on Azure
    echo Visit: https://dashboards.azurewebsites.net/
) else (
    echo.
    echo DEPLOYMENT FAILED. Error code: %errorlevel%
    echo Make sure you are logged in to Azure: az login
)
pause
