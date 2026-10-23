import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'zphs_nandigama_scouts_secret_key'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 32 మంది విద్యార్థుల జాబితా (మొదటి పేరు కళ్యాణం ప్రశాంత్ కుమార్)
DEFAULT_STUDENTS = [
    ("కళ్యాణం ప్రశాంత్ కుమార్", "Scout", "UID1001", "BSG1001", "తండ్రి పేరు", "OC", "8th Class", "A", ""),
    ("ఎన్. సాయి కృష్ణ", "Scout", "UID1002", "BSG1002", "రామారావు", "BC-B", "8th Class", "A", ""),
    ("బి. గణేష్", "Scout", "UID1003", "BSG1003", "శ్రీనివాస్", "BC-A", "8th Class", "A", ""),
    ("సి. దుర్గ భవాని", "Guide", "UID1004", "BSG1004", "వెంకటేశ్వర్లు", "SC", "8th Class", "A", ""),
    ("డి. లక్ష్మి", "Guide", "UID1005", "BSG1005", "నారాయణ", "BC-D", "8th Class", "A", ""),
    ("ఇ. పవన్ కుమార్", "Scout", "UID1006", "BSG1006", "సత్యనారాయణ", "OC", "8th Class", "A", ""),
    ("ఎఫ్. దివ్య", "Guide", "UID1007", "BSG1007", "ప్రసాద్", "BC-A", "8th Class", "A", ""),
    ("జి. రాజేష్", "Scout", "UID1008", "BSG1008", "కోటేశ్వర రావు", "SC", "8th Class", "A", ""),
    ("హెచ్. స్వాతి", "Guide", "UID1009", "BSG1009", "బాబు", "ST", "8th Class", "A", ""),
    ("ఐ. నాగేష్", "Scout", "UID1010", "BSG1010", "అంజనేయులు", "BC-B", "8th Class", "A", ""),
    ("జె. మౌనిక", "Guide", "UID1011", "BSG1011", "సుబ్బారావు", "OC", "8th Class", "A", ""),
    ("కె. కిరణ్", "Scout", "UID1012", "BSG1012", "శివ", "BC-D", "8th Class", "A", ""),
    ("ఎల్. రమ్య", "Guide", "UID1013", "BSG1013", "బ్రహ్మం", "SC", "8th Class", "A", ""),
    ("ఎం. సురేష్", "Scout", "UID1014", "BSG1014", "వీరయ్య", "OC", "8th Class", "A", ""),
    ("ఎన్. భావన", "Guide", "UID1015", "BSG1015", "మల్లేశ్వర రావు", "BC-A", "8th Class", "A", ""),
    ("ఓ. రవి", "Scout", "UID1016", "BSG1016", "సాంబశివ రావు", "BC-B", "8th Class", "A", ""),
    ("పి. అనుష", "Guide", "UID1017", "BSG1017", "సాంబయ్య", "SC", "8th Class", "A", ""),
    ("క్యూ. వంశీ", "Scout", "UID1018", "BSG1018", "నాగేశ్వర రావు", "OC", "8th Class", "A", ""),
    ("ఆర్. స్నేహ", "Guide", "UID1019", "BSG1019", "శ్రీను", "BC-D", "8th Class", "A", ""),
    ("ఎస్. మహేష్", "Scout", "UID1020", "BSG1020", "అప్పారావు", "BC-A", "8th Class", "A", ""),
    ("టి. కీర్తి", "Guide", "UID1021", "BSG1021", "వెంకట్", "OC", "8th Class", "A", ""),
    ("యు. తరుణ్", "Scout", "UID1022", "BSG1022", "మురళి", "SC", "8th Class", "A", ""),
    ("వి. జ్యోత్స్న", "Guide", "UID1023", "BSG1023", "సత్యం", "BC-B", "8th Class", "A", ""),
    ("డబ్ల్యూ. అశోక్", "Scout", "UID1024", "BSG1024", "చిన్న", "ST", "8th Class", "A", ""),
    ("ఎక్స్. వర్ష", "Guide", "UID1025", "BSG1025", "పెద్ద", "OC", "8th Class", "A", ""),
    ("వై. నవీన్", "Scout", "UID1026", "BSG1026", "గోపయ్య", "BC-A", "8th Class", "A", ""),
    ("జెడ్. ప్రియాంక", "Guide", "UID1027", "BSG1027", "లింగయ్య", "SC", "8th Class", "A", ""),
    ("ఏఏ. కోటేష్", "Scout", "UID1028", "BSG1028", "కోట", "BC-D", "8th Class", "A", ""),
    ("ఏబీ. హరిత", "Guide", "UID1029", "BSG1029", "హరి", "OC", "8th Class", "A", ""),
    ("ఏసీ. సతీష్", "Scout", "UID1030", "BSG1030", "సత్యనారాయణ", "BC-B", "8th Class", "A", ""),
    ("ఏడీ. లావణ్య", "Guide", "UID1031", "BSG1031", "సుబ్బారావు", "SC", "8th Class", "A", ""),
    ("ఏఈ. మణికంఠ", "Scout", "UID1032", "BSG1032", "రంగారావు", "OC", "8th Class", "A", "")
]

def init_db():
    conn = sqlite3.connect('scouts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            sl_no INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            uid TEXT,
            bsg_uid TEXT,
            father_name TEXT,
            caste TEXT,
            class_name TEXT,
            section TEXT,
            filename TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            student_sl INTEGER PRIMARY KEY,
            student_name TEXT,
            classes_attended TEXT,
            uniform_maint TEXT,
            remarks TEXT,
            improvement TEXT,
            notes_completed TEXT,
            experience TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO students (name, category, uid, bsg_uid, father_name, caste, class_name, section, filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', DEFAULT_STUDENTS)
        
    conn.commit()
    conn.close()

init_db()

ADMIN_CREDENTIALS = {
    "sailakshmikalyanam5990@gmail.com": "admin123",
    "sundarrao@gmail.com": "admin123"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="te">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZPHS Nandigama Scouts & Guides Portal</title>
    <style>
        :root { --white: #ffffff; --blue: #1d4ed8; --green: #15803d; --violet: #6b21a8; --red: #dc2626; --bg: #f8fafc; }
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: var(--bg); color: #1e293b; }
        header { background-color: var(--blue); color: var(--white); padding: 20px; text-align: center; border-bottom: 5px solid var(--violet); }
        header h1 { margin: 0; font-size: 22px; }
        header h2 { margin: 5px 0 0 0; font-size: 16px; color: #cbd5e1; }
        nav { background-color: var(--violet); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; color: white; font-weight: bold; flex-wrap: wrap; gap: 10px; }
        nav a { color: white; text-decoration: none; }
        .container { max-width: 950px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: var(--violet); }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box; }
        .btn { background-color: var(--green); color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn-edit { background-color: #d97706; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; display: inline-block; font-weight: bold; }
        .btn-report { background-color: var(--blue); color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; display: inline-block; font-weight: bold; }
        .btn-delete { background-color: var(--red); color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; display: inline-block; font-weight: bold; }
        .bio-card { border: 2px solid var(--green); border-radius: 8px; padding: 15px; margin-bottom: 25px; background-color: #f0fdf4; display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
        .student-photo { width: 90px; height: 110px; border: 2px solid var(--green); border-radius: 4px; object-fit: cover; background: #e2e8f0; }
        .flash { background-color: #fef2f2; color: #991b1b; padding: 10px; border-radius: 4px; margin-bottom: 15px; border: 1px solid #fecaca; }
        .report-sheet { border: 2px solid #000; padding: 30px; background: #fff; margin-top: 20px; font-family: 'Times New Roman', serif; }
    </style>
</head>
<body>
<header>
    <h1>ZPHS NANDIGAMA HIGH SCHOOL</h1>
    <h2>BHARAT SCOUTS AND GUIDES PORTAL</h2>
</header>
<nav>
    <span>స్కౌట్స్ & గైడ్స్ సమాచార వ్యవస్థ</span>
    <div>
        {% if session.get('is_admin') %}
            <a href="/admin/dashboard" style="background: var(--green); padding: 6px 12px; border-radius: 4px; margin-right: 15px;">అడ్మిన్ డ్యాష్‌బోర్డ్</a>
            <a href="/logout" style="color: #fecaca;">లాగౌట్ (Logout)</a>
        {% else %}
            <a href="/?show_admin_login=true" style="background: var(--green); padding: 6px 12px; border-radius: 4px;">అడ్మిన్ లాగిన్ (Admin Login)</a>
        {% endif %}
    </div>
</nav>
<div class="container">
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <div class="flash">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {% if show_admin_login and not session.get('is_admin') %}
        <div style="border: 2px solid var(--violet); padding: 20px; border-radius: 8px; background: #faf5ff; margin-bottom: 25px;">
            <h3 style="color: var(--violet); margin-top: 0;">అడ్మిన్ లాగిన్ ప్యానెల్</h3>
            <form method="POST" action="/admin/login">
                <div class="form-group">
                    <label>ఈమెయిల్ ఐడీ / యూజర్ నేమ్:</label>
                    <input type="text" name="username" required placeholder="sailakshmikalyanam5990@gmail.com లేదా sundarrao@gmail.com">
                </div>
                <div class="form-group">
                    <label>పాస్‌వర్డ్:</label>
                    <input type="password" name="password" required placeholder="admin123">
                </div>
                <button type="submit" class="btn">లాగిన్ అవ్వండి</button>
                <a href="/" style="margin-left: 10px; color: #64748b; text-decoration: none;">క్యాన్సిల్</a>
            </form>
        </div>
    {% endif %}

    {% if session.get('is_admin') and not generate_report_student and not edit_student %}
        <div style="border: 2px solid var(--green); padding: 20px; border-radius: 8px; background: #f0fdf4; margin-bottom: 25px;">
            <h3 style="color: var(--green); margin-top: 0;">➕ కొత్త విద్యార్థిని చేర్చండి</h3>
            <form method="POST" action="/admin/add_student" enctype="multipart/form-data">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div class="form-group"><label>విద్యార్థి పేరు:</label><input type="text" name="name" required placeholder="విద్యార్థి పేరు రాయండి"></div>
                    <div class="form-group"><label>కేటగిరీ:</label><select name="category"><option value="Scout">Scout</option><option value="Guide">Guide</option></select></div>
                    <div class="form-group"><label>UID:</label><input type="text" name="uid" placeholder="UID నంబర్"></div>
                    <div class="form-group"><label>BSG ID:</label><input type="text" name="bsg_uid" placeholder="BSG ID నంబర్"></div>
                    <div class="form-group"><label>తండ్రి పేరు:</label><input type="text" name="father_name" placeholder="తండ్రి పేరు"></div>
                    <div class="form-group"><label>కులం:</label><input type="text" name="caste" placeholder="కులం"></div>
                    <div class="form-group"><label>తరగతి:</label><input type="text" name="class_name" placeholder="ఉదా: 8th Class"></div>
                    <div class="form-group"><label>ఫోటో / డాక్యుమెంట్:</label><input type="file" name="student_file"></div>
                </div>
                <button type="submit" class="btn" style="margin-top: 10px;">సేవ్ చేయి</button>
            </form>
        </div>
    {% endif %}

    {% if generate_report_student and session.get('is_admin') %}
        <div style="border: 2px solid var(--blue); padding: 20px; border-radius: 8px; background: #eff6ff; margin-bottom: 25px;">
            <h3 style="color: var(--blue); margin-top: 0;">MONTHLY REPORT ({{ generate_report_student[1] }})</h3>
            <form method="POST" action="/admin/save_report/{{ generate_report_student[0] }}">
                <div class="form-group"><label>హాజరైన తరగతులు:</label><input type="text" name="classes_attended" required placeholder="ఉదా: 4 / 4"></div>
                <div class="form-group"><label>యూనిఫాం నిర్వహణ:</label><input type="text" name="uniform_maint" required placeholder="ఉదా: Good"></div>
                <div class="form-group"><label>సమీక్షలు / రిమార్క్స్:</label><textarea name="remarks" rows="2" required placeholder="రిమార్క్స్ రాయండి..."></textarea></div>
                <div class="form-group"><label>మెరుగుదల అవసరం:</label><input type="text" name="improvement" required placeholder="ఉదా: Scarf & Cap proper"></div>
                <div class="form-group"><label>పూర్తయిన నోట్స్:</label><input type="text" name="notes_completed" required placeholder="ఉదా: Fully Completed"></div>
                <div class="form-group"><label>అనుభవం:</label><textarea name="experience" rows="2" required placeholder="అనుభవం రాయండి..."></textarea></div>
                <button type="submit" class="btn" style="background-color: var(--blue);">రిపోర్ట్ సేవ్ చేయి</button>
                <a href="/admin/dashboard" style="margin-left: 10px; color: #64748b; text-decoration: none;">క్యాన్సిల్</a>
            </form>
        </div>
    {% endif %}

    {% if view_report %}
        <div class="report-sheet">
            <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px;">
                <h3>THE BHARAT SCOUTS AND GUIDES</h3>
                <h2>MONTHLY REPORT</h2>
                <p>Z.P.H.S plus N.T.R Dt. 521185</p>
            </div>
            <p><strong>Name of the scout :-</strong> {{ view_report[1] }}</p>
            <p><strong>UDISE Code :-</strong> 28160400523</p>
            <hr style="border: 1px solid #000; margin: 15px 0;">
            <p><strong>Classes attended :-</strong> {{ view_report[2] }}</p>
            <p><strong>Uniform maintenance :-</strong> {{ view_report[3] }}</p>
            <p><strong>Remarks :-</strong> {{ view_report[4] }}</p>
            <p><strong>Improvement needed :-</strong> {{ view_report[5] }}</p>
            <p><strong>Notes completed :-</strong> {{ view_report[6] }}</p>
            <p><strong>Experience :-</strong> {{ view_report[7] }}</p>
            <div style="text-align: center; margin-top: 20px;"><a href="/" class="btn" style="text-decoration: none;">హోమ్ పేజీకి వెళ్ళు</a></div>
        </div>
    {% endif %}

    {% if edit_student and session.get('is_admin') %}
        <div style="border: 2px solid var(--d97706); padding: 20px; border-radius: 8px; background: #fffbeb; margin-bottom: 25px;">
            <h3 style="color: #d97706; margin-top: 0;">✏️ ప్రొఫైల్ సవరించు (Edit: {{ edit_student[1] }})</h3>
            <form method="POST" action="/admin/edit/{{ edit_student[0] }}" enctype="multipart/form-data">
                <div class="form-group"><label>విద్యార్థి పేరు:</label><input type="text" name="name" value="{{ edit_student[1] }}" required></div>
                <div class="form-group"><label>కేటగిరీ:</label><select name="category"><option value="Scout" {% if edit_student[2] == 'Scout' %}selected{% endif %}>Scout</option><option value="Guide" {% if edit_student[2] == 'Guide' %}selected{% endif %}>Guide</option></select></div>
                <div class="form-group"><label>UID:</label><input type="text" name="uid" value="{{ edit_student[3] }}"></div>
                <div class="form-group"><label>BSG ID:</label><input type="text" name="bsg_uid" value="{{ edit_student[4] }}"></div>
                <div class="form-group"><label>తండ్రి పేరు:</label><input type="text" name="father_name" value="{{ edit_student[5] }}"></div>
                <div class="form-group"><label>కులం:</label><input type="text" name="caste" value="{{ edit_student[6] }}"></div>
                <div class="form-group"><label>తరగతి:</label><input type="text" name="class_name" value="{{ edit_student[7] }}"></div>
                <div class="form-group"><label>కొత్త ఫోటో / డాక్యుమెంట్ (ఆప్షనల్):</label><input type="file" name="student_file"></div>
                <button type="submit" class="btn" style="background-color: #d97706;">మార్పులు సేవ్ చేయి</button>
                <a href="/admin/dashboard" style="margin-left: 10px; color: #64748b; text-decoration: none;">క్యాన్సిల్</a>
            </form>
        </div>
    {% endif %}

    {% if not view_report %}
    <form method="GET" action="/" style="display: flex; gap: 10px; margin-bottom: 20px;">
        <input type="text" name="search" value="{{ search_query }}" placeholder="స్కౌట్ పేరు లేదా UID టైప్ చేసి సెర్చ్ చేయండి..." style="flex: 1; padding: 10px;">
        <button type="submit" class="btn">సెర్చ్</button>
    </form>

    {% if search_results %}
        <h3>విద్యార్థుల జాబితా (మొత్తం {{ search_results|length }} మంది):</h3>
        {% for scout in search_results %}
            <div class="bio-card">
                {% if scout[9] %}
                    <img src="{{ url_for('uploaded_file', filename=scout[9]) }}" class="student-photo">
                {% else %}
                    <div class="student-photo" style="display: flex; align-items: center; justify-content: center; color: #64748b; font-size: 12px; text-align: center;">No Photo</div>
                {% endif %}
                <div style="flex: 1; min-width: 250px;">
                    <h3 style="margin-top: 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 5px; color: var(--violet);">
                        <span>
  [{{ loop.index }}] {{ scout[1] }} 
  ({{ scout[2] }})
</span>

                        {% if session.get('is_admin') %}
                            <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                                <a href="/admin/report_form/{{ scout[0] }}" class="btn-report">📄 Report</a>
                                <a href="/admin/edit_form/{{ scout[0] }}" class="btn-edit">✏️ Edit</a>
                                <a href="/admin/delete_student/{{ scout[0] }}" class="btn-delete" onclick="return confirm('ఈ విద్యార్థిని డిలీట్ చేయాలా?');">🗑️ Delete</a>
                            </div>
                        {% else %}
                            {% set has_rep = namespace(val=False) %}
                            {% for r in all_reports %}{% if r[0] == scout[0] %}{% set has_rep.val = True %}{% endif %}{% endfor %}
                            {% if has_rep.val %}<a href="/view_report/{{ scout[0] }}" class="btn-report">View Report</a>{% endif %}
                        {% endif %}
                    </h3>
                    <p><strong>UID:</strong> {{ scout[3] }} | <strong>BSG ID:</strong> {{ scout[4] }}</p>
                    <p><strong>తండ్రి పేరు:</strong> {{ scout[5] }} | <strong>కులం:</strong> {{ scout[6] }} | <strong>తరగతి:</strong> {{ scout[7] }}</p>
                    {% if scout[9] %}<p><a href="{{ url_for('uploaded_file', filename=scout[9]) }}" target="_blank" style="color: var(--blue);">📄 డాక్యుమెంట్ / ఫోటో వీక్షించండి</a></p>{% endif %}
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p style="text-align: center; color: #64748b; padding: 20px;">ప్రస్తుతం విద్యార్థుల వివరాలు లేవు.</p>
    {% endif %}
    {% endif %}
</div>
</body>
</html>
"""

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip().lower()
    show_admin_login = request.args.get('show_admin_login')
    
    conn = sqlite3.connect('scouts.db')
    cursor = conn.cursor()
    if search_query:
        cursor.execute("SELECT * FROM students WHERE lower(name) LIKE ? OR lower(uid) LIKE ? OR lower(bsg_uid) LIKE ?", 
                       (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("SELECT * FROM students")
    results = cursor.fetchall()
    
    cursor.execute("SELECT * FROM reports")
    all_reports = cursor.fetchall()
    conn.close()

    return render_template_string(HTML_TEMPLATE, search_results=results, search_query=search_query, show_admin_login=show_admin_login, all_reports=all_reports)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
