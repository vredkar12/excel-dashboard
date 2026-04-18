# Excel Live Dashboard

A real-time dashboard that displays data from Excel files with auto-refresh capabilities.

## Features
- Live data from Excel files
- Auto-refresh every 30 seconds
- Interactive data tables with filters
- Status highlighting (green/red)
- Shareable via public URL
- Deployable to cloud services

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
python app.py
```

3. Open http://localhost:5000

## Deploy to Render (Free)

1. Push your code to GitHub
2. Go to https://render.com and sign up
3. Create a new Web Service
4. Connect your GitHub repository
5. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
6. Click "Create Web Service"

## Deploy to Railway ($5/month)

1. Go to https://railway.app and sign up
2. Create a new project
3. Connect your GitHub repository
4. Set environment variables if needed
5. Deploy

## Deploy to Fly.io (Free tier)

1. Install flyctl: `winget install flyctl.fly`
2. Run: `fly launch`
3. Follow the prompts
4. Deploy: `fly deploy`

## Excel File Setup

Place your Excel file named `Beauty_PF Status_20260416.xlsx` in the project root. The dashboard will automatically read all sheets and display them.
```

3. Open your browser to: http://localhost:5000

## Configuration
- Place your Excel file in the project root
- Update `EXCEL_FILE` in app.py to match your filename
- Adjust refresh interval in templates/index.html