from flask import Flask, render_template, jsonify, request, session
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-before-production")

# Configuration
EXCEL_FILE = "Beauty_PF Status_20260416.xlsx"
UPLOAD_ADMIN_PASSWORD = os.environ.get("UPLOAD_ADMIN_PASSWORD", "")

# Create sample Excel file if it doesn't exist (for first deployment)
def create_sample_excel():
    if not os.path.exists(EXCEL_FILE):
        sample_data = {
            'Employee Code': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
            'Employee Name': ['John Smith', 'Jane Doe', 'Mike Johnson', 'Sarah Williams', 'Tom Brown'],
            'Reporting Manager': ['Manager A', 'Manager A', 'Manager B', 'Manager B', 'Manager A'],
            'Store Name': ['Store 1', 'Store 2', 'Store 1', 'Store 3', 'Store 2'],
            'Cluster Region': ['North', 'South', 'North', 'East', 'South'],
            'Employee UAN No': ['UAN001', 'UAN002', 'UAN003', 'UAN004', 'UAN005'],
            'Employee Member ID': ['MEM001', 'MEM002', 'MEM003', 'MEM004', 'MEM005'],
            'Gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
            'Date of Joining': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', '2024-05-01'],
            'Marital Status': ['Single', 'Married', 'Single', 'Married', 'Single'],
            'Status': ['Pending', 'Completed', 'Pending', 'Completed', 'Yes']
        }
        df = pd.DataFrame(sample_data)
        df.to_excel(EXCEL_FILE, index=False, sheet_name='Data')
        print(f"Created sample Excel file: {EXCEL_FILE}")

# Initialize sample file on startup
create_sample_excel()

# Configure upload folder
UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_upload_admin():
    return session.get("can_upload") is True

@app.route('/api/admin/status')
def admin_status():
    """Return whether upload is configured and the current user can upload."""
    return jsonify({
        "upload_configured": bool(UPLOAD_ADMIN_PASSWORD),
        "can_upload": is_upload_admin()
    })

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Authenticate an upload admin for the current session."""
    if not UPLOAD_ADMIN_PASSWORD:
        return jsonify({"error": "Upload access is not configured on the server."}), 503

    payload = request.get_json(silent=True) or {}
    password = str(payload.get("password", ""))

    if password != UPLOAD_ADMIN_PASSWORD:
        return jsonify({"error": "Invalid admin password."}), 401

    session["can_upload"] = True
    return jsonify({"success": True, "message": "Upload access granted."})

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Remove upload admin access for the current session."""
    session.pop("can_upload", None)
    return jsonify({"success": True})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload to update Excel data"""
    try:
        if not UPLOAD_ADMIN_PASSWORD:
            return jsonify({"error": "Upload access is disabled until an admin password is configured."}), 503

        if not is_upload_admin():
            return jsonify({"error": "Admin login required to upload master data."}), 403

        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            # Save the file with the configured filename
            file.save(EXCEL_FILE)
            return jsonify({
                "success": True,
                "message": "File uploaded successfully",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({"error": "Invalid file type. Please upload .xlsx or .xls file"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def read_excel_data():
    """Read and process Excel file data"""
    try:
        if not os.path.exists(EXCEL_FILE):
            return {"sheets": {}, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": "No data file. Upload an Excel file to get started."}
        
        # Read all sheets from Excel
        excel_file = pd.ExcelFile(EXCEL_FILE)
        sheets_data = {}
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Convert to dict and handle NaN values
            df = df.fillna('')
            sheets_data[sheet_name] = {
                "columns": df.columns.tolist(),
                "data": df.to_dict(orient="records"),
                "row_count": len(df)
            }
        
        return {
            "sheets": sheets_data,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get Excel data"""
    data = read_excel_data()
    return jsonify(data)

@app.route('/api/summary')
def get_summary():
    """API endpoint to get summary statistics"""
    try:
        if not os.path.exists(EXCEL_FILE):
            return jsonify({"sheets": [], "total_sheets": 0, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        
        excel_file = pd.ExcelFile(EXCEL_FILE)
        summary = {
            "sheets": excel_file.sheet_names,
            "total_sheets": len(excel_file.sheet_names),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Get row counts for each sheet
        sheet_counts = {}
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            sheet_counts[sheet_name] = len(df)
        
        summary["sheet_counts"] = sheet_counts
        return jsonify(summary)
    except Exception as e:
        return jsonify({"sheets": [], "total_sheets": 0, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Excel Dashboard on port {port}...")
    print(f"Reading from: {EXCEL_FILE}")
    app.run(debug=False, host='0.0.0.0', port=port)
