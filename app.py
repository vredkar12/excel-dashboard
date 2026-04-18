from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
EXCEL_FILE = "Beauty_PF Status_20260416.xlsx"

# Configure upload folder
UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload to update Excel data"""
    try:
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
    print(f"Starting Excel Dashboard...")
    print(f"Reading from: {EXCEL_FILE}")
    app.run(debug=True, host='0.0.0.0', port=5000)