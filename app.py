from flask import Flask, render_template, jsonify, request, session, redirect, url_for, Response
import pandas as pd
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-before-production")

# Configuration
DEFAULT_EXCEL_FILE = "Beauty_PF Status_20260416.xlsx"
PME_EXCEL_FILE = "Beauty_PME Status_20260416.xlsx"
ACTIVE_EMPLOYEE_XLSX_FILE = "Active_Employee_Codes.xlsx"
ACTIVE_EMPLOYEE_CSV_FILE = "Active_Employee_Codes.csv"
UPLOAD_ADMIN_PASSWORD = os.environ.get("UPLOAD_ADMIN_PASSWORD", "")

DASHBOARDS = {
    "e-nomination-pendancy": {
        "title": "E Nomination pendancy",
        "file": DEFAULT_EXCEL_FILE,
    },
    "pme-dashboard": {
        "title": "PME Dashboard",
        "file": PME_EXCEL_FILE,
    },
}

# Create sample Excel file if it doesn't exist (for first deployment)
def create_sample_excel():
    if not os.path.exists(DEFAULT_EXCEL_FILE):
        sample_data = {
            'Employee Code': ['10000001', '10000002', '10000003', '10000004', '10000005'],
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
        df.to_excel(DEFAULT_EXCEL_FILE, index=False, sheet_name='Data')
        print(f"Created sample Excel file: {DEFAULT_EXCEL_FILE}")

# Initialize sample file on startup
create_sample_excel()

# Configure upload folder
UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_employee_code(value):
    return ''.join(ch for ch in str(value).strip() if ch.isdigit())

def has_dashboard_access():
    return bool(session.get("employee_access"))

def is_upload_admin():
    return session.get("can_upload") is True

def get_active_employee_file():
    if os.path.exists(ACTIVE_EMPLOYEE_XLSX_FILE):
        return ACTIVE_EMPLOYEE_XLSX_FILE
    if os.path.exists(ACTIVE_EMPLOYEE_CSV_FILE):
        return ACTIVE_EMPLOYEE_CSV_FILE
    return ""

def get_code_column(columns):
    for column in columns:
        normalized = str(column).strip().lower().replace('_', ' ')
        if 'employee' in normalized and 'code' in normalized:
            return column
    return None

def read_active_employee_codes():
    active_file = get_active_employee_file()
    if not active_file:
        return set()

    try:
        if active_file.lower().endswith('.csv'):
            df = pd.read_csv(active_file, dtype=str)
        else:
            df = pd.read_excel(active_file, dtype=str)

        code_column = get_code_column(df.columns)
        if not code_column:
            return set()

        codes = {
            normalize_employee_code(value)
            for value in df[code_column].fillna('')
            if len(normalize_employee_code(value)) == 8
        }
        return codes
    except Exception:
        return set()

def active_employee_list_info():
    codes = read_active_employee_codes()
    last_updated = ""
    active_file = get_active_employee_file()
    if active_file:
        last_updated = datetime.fromtimestamp(os.path.getmtime(active_file)).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "configured": bool(active_file),
        "count": len(codes),
        "last_updated": last_updated
    }

def get_dashboard_config(dashboard_slug):
    return DASHBOARDS.get(dashboard_slug)

def count_words(text):
    return len([word for word in str(text).strip().split() if word])

def ensure_remark_columns(df):
    if 'Remark' not in df.columns:
        df['Remark'] = ''
    if 'Remark Added By' not in df.columns:
        df['Remark Added By'] = ''
    return df

def get_status_column(columns):
    for column in columns:
        normalized = str(column).strip().lower()
        if 'status' in normalized:
            return column
    return None

def normalize_status_value(value):
    normalized = str(value).strip().lower()
    mapping = {
        'completed': 'Completed',
        'pending': 'Pending',
        'yes': 'Yes',
        'no': 'No',
    }
    return mapping.get(normalized, '')

def build_pf_analytics(excel_path):
    analytics = {
        "total_rows": 0,
        "sheets": [],
        "charts": []
    }
    status_counts = {"Completed": 0, "Pending": 0, "Yes": 0, "No": 0}
    pending_breakdowns = {
        "store_name": {"label": "Stores", "column": "Store Name", "counts": {}},
        "cluster_region": {"label": "Cluster", "column": "Cluster Region", "counts": {}},
        "hrbp": {"label": "HRBP", "column": "HRBP", "counts": {}},
        "reporting_manager": {"label": "Reporting Manager", "column": "Reporting Manager", "counts": {}},
        "gender": {"label": "Gender", "column": "Gender", "counts": {}},
        "marital_status": {"label": "Marital Status", "column": "Marital Status", "counts": {}},
    }

    if not os.path.exists(excel_path):
        return analytics

    excel_file = pd.ExcelFile(excel_path)
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df = df.fillna('')
        row_count = len(df)
        analytics["total_rows"] += row_count
        analytics["sheets"].append({
            "name": sheet_name,
            "row_count": row_count
        })

        pf_pending_column = next((column for column in df.columns if 'pendingmination pendancy' in str(column).strip().lower() or 'nomination pendancy' in str(column).strip().lower()), None)

        for column in df.columns:
            if str(column).strip().lower() in {'employee code', 'employee name', 'reporting manager', 'store name', 'cluster region', 'employee uan no', 'employee member id', 'gender', 'date of joining', 'marital status', 'hrbp', 'remark', 'remark added by'}:
                continue

            for value in df[column]:
                normalized = normalize_status_value(value)
                if normalized:
                    status_counts[normalized] += 1

        if pf_pending_column:
            for _, row in df.iterrows():
                if is_pending_like(row.get(pf_pending_column, '')):
                    for breakdown in pending_breakdowns.values():
                        column_name = breakdown["column"]
                        if column_name in df.columns:
                            key = str(row.get(column_name, '')).strip() or 'Unassigned'
                            breakdown["counts"][key] = breakdown["counts"].get(key, 0) + 1

    analytics["sheets"].sort(key=lambda item: item["name"])
    analytics["charts"] = [
        {
            "label": "PF Status Mix",
            "counts": {key: value for key, value in status_counts.items() if value > 0}
        },
        {
            "label": "PF Pendancy Breakdown",
            "type": "dropdown-pie",
            "default_key": "hrbp",
            "breakdowns": {
                key: {
                    "label": value["label"],
                    "counts": dict(sorted(value["counts"].items(), key=lambda item: item[0].lower()))
                }
                for key, value in pending_breakdowns.items()
            }
        }
    ]
    return analytics

def is_pending_like(value):
    normalized = str(value).strip().lower()
    return normalized in {'pending', 'no', 'not done', 'pme not done', 'none', 'false', 'n', 'fail'}

def build_pme_analytics(excel_path):
    analytics = {
        "total_rows": 0,
        "sheets": [],
        "charts": []
    }
    hrbp_pending_counts = {}

    if not os.path.exists(excel_path):
        return analytics

    excel_file = pd.ExcelFile(excel_path)
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df = df.fillna('')
        row_count = len(df)
        analytics["total_rows"] += row_count
        analytics["sheets"].append({
            "name": sheet_name,
            "row_count": row_count
        })

        status_column = get_status_column(df.columns)
        hrbp_column = next((column for column in df.columns if str(column).strip().lower() == 'hrbp'), None)
        if status_column and hrbp_column:
            filtered = df[df[status_column].map(is_pending_like)]
            counts = filtered[hrbp_column].astype(str).str.strip()
            counts = counts[counts != '']
            for hrbp, count in counts.value_counts().items():
                hrbp_pending_counts[hrbp] = hrbp_pending_counts.get(hrbp, 0) + int(count)

    analytics["sheets"].sort(key=lambda item: item["name"])
    analytics["charts"] = [
        {
            "label": "PME Pendancy HRBP Wise",
            "counts": dict(sorted(hrbp_pending_counts.items(), key=lambda item: item[0].lower()))
        }
    ]
    return analytics

def build_dashboard_analytics(dashboard_slug, excel_path):
    if dashboard_slug == 'e-nomination-pendancy':
        return build_pf_analytics(excel_path)
    if dashboard_slug == 'pme-dashboard':
        return build_pme_analytics(excel_path)

    return {
        "total_rows": 0,
        "sheets": [],
        "charts": []
    }

def employee_code_exists(employee_code):
    normalized_code = normalize_employee_code(employee_code)
    if len(normalized_code) != 8:
        return False

    active_codes = read_active_employee_codes()
    if active_codes:
        return normalized_code in active_codes

    if not os.path.exists(EXCEL_FILE):
        return False

    try:
        excel_file = pd.ExcelFile(EXCEL_FILE)
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype=str)
            code_column = get_code_column(df.columns)
            if not code_column:
                continue

            codes = df[code_column].fillna('').map(normalize_employee_code)
            if (codes == normalized_code).any():
                return True
    except Exception:
        return False

    return False

def dashboard_required(route_handler):
    @wraps(route_handler)
    def wrapped(*args, **kwargs):
        if not has_dashboard_access():
            return redirect(url_for('index'))
        return route_handler(*args, **kwargs)
    return wrapped

def dashboard_api_required(route_handler):
    @wraps(route_handler)
    def wrapped(*args, **kwargs):
        if not has_dashboard_access():
            return jsonify({"error": "Employee code verification required."}), 401
        return route_handler(*args, **kwargs)
    return wrapped

@app.route('/api/access/status')
def access_status():
    """Return whether the current session has dashboard access."""
    return jsonify({
        "has_access": has_dashboard_access(),
        "employee_code": session.get("employee_code", "")
    })

@app.route('/api/access/login', methods=['POST'])
def access_login():
    """Validate employee code before allowing dashboard access."""
    payload = request.get_json(silent=True) or {}
    employee_code = normalize_employee_code(payload.get("employee_code", ""))

    if len(employee_code) != 8:
        return jsonify({"error": "Enter a valid 8-digit employee code."}), 400

    if not employee_code_exists(employee_code):
        return jsonify({"error": "Employee code not found. Please check and try again."}), 401

    session["employee_access"] = True
    session["employee_code"] = employee_code
    return jsonify({"success": True, "message": "Access granted."})

@app.route('/api/access/logout', methods=['POST'])
def access_logout():
    """Clear dashboard access for the current session."""
    session.pop("employee_access", None)
    session.pop("employee_code", None)
    session.pop("can_upload", None)
    return jsonify({"success": True})

@app.route('/api/admin/status')
def admin_status():
    """Return whether upload is configured and the current user can upload."""
    active_info = active_employee_list_info()
    return jsonify({
        "upload_configured": bool(UPLOAD_ADMIN_PASSWORD),
        "can_upload": is_upload_admin(),
        "active_codes_configured": active_info["configured"],
        "active_codes_count": active_info["count"],
        "active_codes_last_updated": active_info["last_updated"]
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

@app.route('/api/active-codes/upload', methods=['POST'])
def upload_active_employee_codes():
    """Upload the active employee code list used for dashboard access."""
    try:
        if not UPLOAD_ADMIN_PASSWORD:
            return jsonify({"error": "Upload access is disabled until an admin password is configured."}), 503

        if not is_upload_admin():
            return jsonify({"error": "Admin login required to upload active employee codes."}), 403

        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Please upload .xlsx, .xls, or .csv file"}), 400

        extension = file.filename.rsplit('.', 1)[1].lower()
        target_file = ACTIVE_EMPLOYEE_XLSX_FILE if extension != 'csv' else ACTIVE_EMPLOYEE_CSV_FILE

        file.save(target_file)
        if target_file == ACTIVE_EMPLOYEE_XLSX_FILE and os.path.exists(ACTIVE_EMPLOYEE_CSV_FILE):
            os.remove(ACTIVE_EMPLOYEE_CSV_FILE)
        if target_file == ACTIVE_EMPLOYEE_CSV_FILE and os.path.exists(ACTIVE_EMPLOYEE_XLSX_FILE):
            os.remove(ACTIVE_EMPLOYEE_XLSX_FILE)

        active_codes = read_active_employee_codes()
        if not active_codes:
            return jsonify({"error": "No valid 8-digit employee codes were found in the uploaded file."}), 400

        return jsonify({
            "success": True,
            "message": "Active employee code list uploaded successfully",
            "count": len(active_codes),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/active-codes/template')
def download_active_employee_template():
    """Download a template file for active employee code uploads."""
    if not UPLOAD_ADMIN_PASSWORD:
        return jsonify({"error": "Upload access is disabled until an admin password is configured."}), 503

    if not is_upload_admin():
        return jsonify({"error": "Admin login required to download the active employee template."}), 403

    csv_content = "\n".join([
        "Employee Code,Employee Name",
        "10000001,Sample Employee 1",
        "10000002,Sample Employee 2"
    ])

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=active_employee_codes_template.csv"
        }
    )

@app.route('/api/upload/<dashboard_slug>', methods=['POST'])
@dashboard_api_required
def upload_file(dashboard_slug):
    """Handle file upload to update Excel data"""
    try:
        dashboard = get_dashboard_config(dashboard_slug)
        if not dashboard:
            return jsonify({"error": "Unknown dashboard."}), 404

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
            file.save(dashboard["file"])
            return jsonify({
                "success": True,
                "message": "File uploaded successfully",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({"error": "Invalid file type. Please upload .xlsx or .xls file"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def read_excel_data(excel_path):
    """Read and process Excel file data"""
    try:
        if not os.path.exists(excel_path):
            return {"sheets": {}, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": "No data file. Upload an Excel file to get started."}
        
        # Read all sheets from Excel
        excel_file = pd.ExcelFile(excel_path)
        sheets_data = {}
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Convert to dict and handle NaN values
            df = df.fillna('')
            df = ensure_remark_columns(df)
            df['_row_id'] = df.index
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

@app.route('/api/remarks/<dashboard_slug>', methods=['POST'])
@dashboard_api_required
def update_remark(dashboard_slug):
    """Update the remark for a single row, capped at 500 words."""
    dashboard = get_dashboard_config(dashboard_slug)
    if not dashboard:
        return jsonify({"error": "Unknown dashboard."}), 404

    payload = request.get_json(silent=True) or {}
    sheet_name = str(payload.get("sheet_name", ""))
    row_id = payload.get("row_id")
    remark = str(payload.get("remark", "")).strip()

    try:
        row_id = int(row_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid row reference."}), 400

    if count_words(remark) > 500:
        return jsonify({"error": "Remark cannot exceed 500 words."}), 400

    excel_path = dashboard["file"]
    if not os.path.exists(excel_path):
        return jsonify({"error": "Dashboard file not found."}), 404

    try:
        excel_file = pd.ExcelFile(excel_path)
        if sheet_name not in excel_file.sheet_names:
            return jsonify({"error": "Sheet not found."}), 404

        updated_sheets = {}
        target_found = False
        for current_sheet in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=current_sheet)
            df = df.fillna('')
            df = ensure_remark_columns(df)

            if current_sheet == sheet_name:
                if row_id < 0 or row_id >= len(df):
                    return jsonify({"error": "Row not found."}), 404
                df.at[row_id, 'Remark'] = remark
                df.at[row_id, 'Remark Added By'] = session.get("employee_code", "")
                target_found = True

            updated_sheets[current_sheet] = df

        if not target_found:
            return jsonify({"error": "Remark target not found."}), 404

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for current_sheet, df in updated_sheets.items():
                df.to_excel(writer, sheet_name=current_sheet, index=False)

        return jsonify({
            "success": True,
            "message": "Remark updated successfully.",
            "word_count": count_words(remark),
            "added_by": session.get("employee_code", ""),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Master dashboard page"""
    active_info = active_employee_list_info()
    return render_template(
        'home.html',
        has_access=has_dashboard_access(),
        employee_code=session.get("employee_code", ""),
        can_upload=is_upload_admin(),
        upload_configured=bool(UPLOAD_ADMIN_PASSWORD),
        active_codes_configured=active_info["configured"],
        active_codes_count=active_info["count"],
        active_codes_last_updated=active_info["last_updated"]
    )

@app.route('/api/analytics-overview')
def analytics_overview():
    """Return analytics for all dashboards shown on the home page."""
    if not has_dashboard_access():
        return jsonify({"error": "Employee code verification required."}), 401

    dashboards = {}
    for slug, dashboard in DASHBOARDS.items():
        dashboards[slug] = {
            "title": dashboard["title"],
            "analytics": build_dashboard_analytics(slug, dashboard["file"])
        }

    return jsonify({
        "dashboards": dashboards,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/<dashboard_slug>')
@dashboard_required
def dashboard_page(dashboard_slug):
    """Dashboard page"""
    dashboard = get_dashboard_config(dashboard_slug)
    if not dashboard:
        return redirect(url_for('index'))
    return render_template(
        'index.html',
        dashboard_title=dashboard["title"],
        dashboard_slug=dashboard_slug
    )

@app.route('/api/data/<dashboard_slug>')
@dashboard_api_required
def get_data(dashboard_slug):
    """API endpoint to get Excel data"""
    dashboard = get_dashboard_config(dashboard_slug)
    if not dashboard:
        return jsonify({"error": "Unknown dashboard."}), 404
    data = read_excel_data(dashboard["file"])
    return jsonify(data)

@app.route('/api/summary/<dashboard_slug>')
@dashboard_api_required
def get_summary(dashboard_slug):
    """API endpoint to get summary statistics"""
    try:
        dashboard = get_dashboard_config(dashboard_slug)
        if not dashboard:
            return jsonify({"error": "Unknown dashboard."}), 404

        excel_path = dashboard["file"]
        if not os.path.exists(excel_path):
            return jsonify({"sheets": [], "total_sheets": 0, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        
        excel_file = pd.ExcelFile(excel_path)
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
    print(f"Default dashboard file: {DEFAULT_EXCEL_FILE}")
    app.run(debug=False, host='0.0.0.0', port=port)
