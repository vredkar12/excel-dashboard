# Excel Live Dashboard

A real-time dashboard that displays data from Excel files with auto-refresh capabilities.

## Features
- Live data from Excel files
- Auto-refresh every 30 seconds
- Interactive data tables with filters
- Status highlighting (green/red)
- Shareable via public URL
- Deployable to cloud services

## Quick Deploy to Render (Free)

### Step 1: Push to GitHub

1. Go to https://github.com and sign in
2. Click "+" → "New repository"
3. Name: `excel-dashboard`
4. Select "Public"
5. Click "Create repository" (don't add any files)
6. Run these commands in your terminal:

```bash
git remote add origin https://github.com/YOUR_USERNAME/excel-dashboard.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 2: Deploy on Render

1. Go to https://render.com and sign up with GitHub
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   | Setting | Value |
   |---------|-------|
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
5. Click "Create Web Service"

### Step 3: Upload Excel File

After deployment, upload your Excel file through the dashboard's upload button or add it to your GitHub repo.

## Local Setup

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000
```

3. Open your browser to: http://localhost:5000

## Configuration
- Place your Excel file in the project root
- Update `EXCEL_FILE` in app.py to match your filename
- Adjust refresh interval in templates/index.html