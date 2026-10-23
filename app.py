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

# డేటాబేస్ కనెక్షన్ మరియు టేబుల్స్ ఏర్పాటు (పర్మినెంట్ స్టోరేజ్ కోసం)
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
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; color: #1e293b; }
        header { background-color: #1d4ed8; color: #ffffff; padding: 20px; text-align: center; border-bottom: 5px solid #6b21a8; }
        nav { background-color: #6b21a8; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; color: white; font-weight: bold; flex-wrap: wrap; gap: 10px; }
        nav a { color: white; text-decoration: none; }
        .container { max-width: 950px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #6b21a8; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box; }
        .btn { background-color: #15803d; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn-edit { background-color: #d97706; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; display: inline-block; }
        .btn-report { background-color: #1d4ed8; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; display: inline-block; }
        .btn-delete { background-color: #dc2626; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; display: inline-block; }
        .bio-card { border: 2px solid #15803d; border-radius: 8px; padding: 15px; margin-bottom: 25px; background-color: #f0fdf4; display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
        .student-photo { width: 90px; height: 110px; border: 2px solid #15803d; border-radius: 4px; object-fit: cover; background: #e2e8f0; }
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
            <a href="/admin/dashboard" style="background: #15803d; padding: 6px 12px; border-radius: 4px; margin-right: 15px;">అడ్మిన్ డ్యాష్‌బోర్డ్</a>
            <a href="/logout" style="color: #fecaca;">లాగౌట్</a>
        {% else %}
            <a href="/?show_admin_login=true" style="background: #15803d; padding: 6px 12px; border-radius: 4px;">అడ్మిన్ లాగిన్</a>
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
        <div style="border: 2px solid #6b21a8; padding: 20px; border-radius: 8px; background: #faf5ff; margin-bottom: 25px;">
            <h3 style="color: #6b21a8; margin-top: 0;">అడ్మిన్ లాగిన్ ప్యానెల్</h3>
            <form method="POST" action="/admin/login">
                <div class="form-group">
                    <label>ఈమెయిల్:</label>
                    <input type="text" name="username" required placeholder="sailakshmikalyanam5990@gmail.com">
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
        <div style="border: 2px solid #15803d; padding: 20px; border-radius: 8px; background: #f0fdf4; margin-bottom: 25px;">
            <h3 style="color: #15803d; margin-top: 0;">➕ కొత్త విద్యార్థిని చేర్చండి</h3>
            <form method="POST" action="/admin/add_student" enctype="multipart/form-data">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div class="form-group"><label>పేరు:</label><input type="text" name="name" required></div>
                    <div class="form-group"><label>కేటగిరీ:</label><select name="category"><option value="Scout">Scout</option><option value="Guide">Guide</option></select></div>
                    <div class="form-group"><label>UID:</label><input type="text" name="uid"></div>
                    <div class="form-group"><label>BSG ID:</label><input type="text" name="bsg_uid"></div>
                    <div class="form-group"><label>తండ్రి పేరు:</label><input type="text" name="father_name"></div>
                    <div class="form-group"><label>కులం:</label><input type="text" name="caste"></div>
                    <div class="form-group"><label>తరగతి:</label><input type="text" name="class_name"></div>
                    <div class="form-group"><label>ఫోటో / డాక్యుమెంట్:</label><input type="file" name="student_file"></div>
                </div>
                <button type="submit" class="btn" style="margin-top: 10px;">సేవ్ చేయి</button>
            </form>
        </div>
    {% endif %}

    {% if generate_report_student and session.get('is_admin') %}
        <div style="border: 2px solid #1d4ed8; padding: 20px; border-radius: 8px; background: #eff6ff; margin-bottom: 25px;">
            <h3 style="color: #1d4ed8; margin-top: 0;">MONTHLY REPORT ({{ generate_report_student[1] }})</h3>
            <form method="POST" action="/admin/save_report/{{ generate_report_student[0] }}">
                <div class="form-group"><label>హాజరైన తరగతులు:</label><input type="text" name="classes_attended" required></div>
                <div class="form-group"><label>యూనిఫాం నిర్వహణ:</label><input type="text" name="uniform_maint" required></div>
                <div class="form-group"><label>సమీక్షలు / రిమార్క్స్:</label><textarea name="remarks" rows="2" required></textarea></div>
                <div class="form-group"><label>మెరుగుదల అవసరం:</label><input type="text" name="improvement" required></div>
                <div class="form-group"><label>పూర్తయిన నోట్స్:</label><input type="text" name="notes_completed" required></div>
                <div class="form-group"><label>అనుభవం:</label><textarea name="experience" rows="2" required></textarea></div>
                <button type="submit" class="btn" style="background-color: #1d4ed8;">రిపోర్ట్ సేవ్ చేయి</button>
                <a href="/admin/dashboard" style="margin-left: 10px; color: #64748b; text-decoration: none;">క్యాన్సిల్</a>
            </form>
        </div>
    {% endif %}

    {% if view_report %}
        <div class="report-sheet">
            <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px;">
                <h3>THE BHARAT SCOUTS AND GUIDES</h3>
                <h2>MONTHLY REPORT</h2>
            </div>
            <p><strong>Name of the scout :-</strong> {{ view_report[1] }}</p>
            <p><strong>Classes attended :-</strong> {{ view_report[2] }}</p>
            <p><strong>Uniform maintenance :-</strong> {{ view_report[3] }}</p>
            <p><strong>Remarks :-</strong> {{ view_report[4] }}</p>
            <p><strong>Improvement needed :-</strong> {{ view_report[5] }}</p>
            <p><strong>Notes completed :-</strong> {{ view_report[6] }}</p>
            <p><strong>Experience :-</strong> {{ view_report[7] }}</p>
            <div style="text-align: center; margin-top: 20px;"><a href="/" class="btn" style="text-decoration: none;">హోమ్ పేజీ</a></div>
        </div>
    {% endif %}

    {% if edit_student and session.get('is_admin') %}
        <div style="border: 2px solid #d97706; padding: 20px; border-radius: 8px; background: #fffbeb; margin-bottom: 25px;">
            <h3 style="color: #d97706; margin-top: 0;">ప్రొఫైల్ సవరించు ({{ edit_student[1] }})</h3>
            <form method="POST" action="/admin/edit/{{ edit_student[0] }}" enctype="multipart/form-data">
                <div class="form-group"><label>పేరు:</label><input type="text" name="name" value="{{ edit_student[1] }}" required></div>
                <div class="form-group"><label>కేటగిరీ:</label><select name="category"><option value="Scout" {% if edit_student[2] == 'Scout' %}selected{% endif %}>Scout</option><option value="Guide" {% if edit_student[2] == 'Guide' %}selected{% endif %}>Guide</option></select></div>
                <div class="form-group"><label>UID:</label><input type="text" name="uid" value="{{ edit_student[3] }}"></div>
                <div class="form-group"><label>BSG ID:</label><input type="text" name="bsg_uid" value="{{ edit_student[4] }}"></div>
                <div class="form-group"><label>తండ్రి పేరు:</label><input type="text" name="father_name" value="{{ edit_student[5] }}"></div>
                <div class="form-group"><label>కులం:</label><input type="text" name="caste" value="{{ edit_student[6] }}"></div>
                <div class="form-group"><label>తరగతి:</label><input type="text" name="class_name" value="{{ edit_student[7] }}"></div>
                <div class="form-group"><label>కొత్త ఫోటో (ఆప్షనల్):</label><input type="file" name="student_file"></div>
                <button type="submit" class="btn" style="background-color: #d97706;">మార్పులు సేవ్ చేయి</button>
                <a href="/admin/dashboard" style="margin-left: 10px; color: #64748b; text-decoration: none;">క్యాన్సిల్</a>
            </form>
        </div>
    {% endif %}

    {% if not view_report %}
    <form method="GET" action="/" style="display: flex; gap: 10px; margin-bottom: 20px;">
        <input type="text" name="search" value="{{ search_query }}" placeholder="పేరు లేదా UID తో సెర్చ్ చేయండి..." style="flex: 1; padding: 10px;">
        <button type="submit" class="btn">సెర్చ్</button>
    </form>

    {% if search_results %}
        <h3>విద్యార్థుల జాబితా ({{ search_results|length }} మంది):</h3>
        {% for scout in search_results %}
            <div class="bio-card">
                {% if scout[9] %}
                    <img src="{{ url_for('uploaded_file', filename=scout[9]) }}" class="student-photo">
                {% else %}
                    <div class="student-photo" style="display: flex; align-items: center; justify-content: center; color: #64748b; font-size: 12px;">No Photo</div>
                {% endif %}
                <div style="flex: 1; min-width: 250px;">
                    <h3 style="margin-top: 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 5px;">
                        <span>[{{ loop.index }}] {{ scout[1] }} ({{ scout[2] }})</span>
                        {% if session.get('is_admin') %}
                            <div>
                                <a href="/admin/report_form/{{ scout[0] }}" class="btn-report">Report</a>
                                <a href="/admin/edit_form/{{ scout[0] }}" class="btn-edit">Edit</a>
                                <a href="/admin/delete_student/{{ scout[0] }}" class="btn-delete" onclick="return confirm('డిలీట్ చేయాలా?');">Delete</a>
                            </div>
                        {% else %}
                            {% set has_rep = namespace(val=False) %}
                            {% for r in all_reports %}{% if r[0] == scout[0] %}{% set has_rep.val = True %}{% endif %}{% endfor %}
                            {% if has_rep.val %}<a href="/view_report/{{ scout[0] }}" class="btn-report">View Report</a>{% endif %}
                        {% endif %}
                    </h3>
                    <p><strong>UID:</strong> {{ scout[3] }} | <strong>BSG ID:</strong> {{ scout[4] }}</p>
                    <p><strong>తండ్రి:</strong> {{ scout[5] }} | <strong>కులం:</strong> {{ scout[6] }} | <strong>తరగతి:</strong> {{ scout[7] }}</p>
                    {% if scout[9] %}<p><a href="{{ url_for('uploaded_file', filename=scout[9]) }}" target="_blank" style="color: #1d4ed8;">డాక్యుమెంట్ వీక్షించండి</a></p>{% endif %}
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p style="text-align: center; color: #64748b;">ప్రస్తుతం విద్యార్థులు లేరు.</p>
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
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if ADMIN_CREDENTIALS.get(request.form.get('username')) == request.form.get('password'):
        session['is_admin'] = True
        flash('లాగిన్ విజయవంతమైంది!', 'success')
        return redirect(url_for('admin_dashboard'))
    flash('తప్పు వివరాలు!', 'error')
    return redirect(url_for('index', show_admin_login=True))

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'): return redirect(url_for('index'))
    conn = sqlite3.connect('scouts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    results = cursor.fetchall()
    cursor.execute("SELECT * FROM reports")
    all_reports = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, search_results=results, all_reports=all_reports)

@app.route('/admin/add_student', methods=['POST'])
def add_student():
    if not session.get('is_admin'): return redirect(url_for('index'))
    file = request.files.get('student_file')
    filename = secure_filename(file.filename) if file and allowed_file(file.filename) else ""
    if filename: file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    conn = sqlite3.connect('scouts.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (name, category, uid, bsg_uid, father_name, caste, class_name, section, filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        request.form.get('name'), request.form.get('category'), request.form.get('uid'),
        request.form.get('bsg_uid'), request.form.get('father_name'), request.form.get('caste'),
        request.form.get('class_name'), 'A', filename
    ))
    conn.commit()
    conn.close()
    
    flash('విద్యార్థి విజయవంతంగా చేర్చబడ్డారు!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_form/<int:sl_no>')
def edit_form(sl_no):
    if not session.get('is_admin'): return redirect(url_for('index'))
    conn = sqlite3.connect('scouts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE sl_no = ?", (sl_no,))
    student = cursor.fetchone()
    conn.close()
    return render_template_string(HTML_TEMPLATE, edit_student=student)

@app.route('/admin/edit/<int:sl_no>', methods=['POST'])
def edit_student(sl_no):
    if not session.get('is_admin'): return redirect(url_for('index'))
    
    conn = sqlite3.connect('scouts.db')
    cursor = conn.cursor()
    
    file = request.files.get('student_file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor.execute('''
            UPDATE students SET name=?, category=?, uid=?, bsg_uid=?, father_name=?, caste=?, class_name=?, filename=? WHERE sl_no=?
        ''', (
            request.form.get('name'), request.form.get('category'), request.form.get('uid'),
            request.form.get('bsg_uid'), request.form.get('father_name'), request.form.get('caste'),
            request.form.get('class_name'), filename, sl_no
        ))
    else:
        cursor.execute('''
            UPDATE students SET name=?, category=?, uid=?, bsg_uid=?, father_name=?, caste=?, class_name=? WHERE sl_no=?
        ''', (
            request.form.get('name'), request.form.get('category'), request.form.get('uid'),
            request.form.get('bsg_uid'), request.form.get('father_name'), request.form.get('caste'),
            request.form.get('class_name'), sl_no
        ))
    
    conn.commit()
    conn.close()
    flash('ప్రొఫైల్ విజయవంతంగా నవీకరించబడింది!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_student/<int:sl_no>')
def delete_student(sl_no):
    if not session.get('is_admin'): return redirect(url_for('index'))
    conn = sqlite3.connect('scouts.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE sl_no = ?", (sl_no,))
    cursor.execute("DELETE FROM reports WHERE student_sl = ?", (sl_no,))
    conn.commit()
    conn.close()
    flash('విద్యార్థి తొలగించబడ్డారు!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/report_form/<int:sl_no>')
def report_form(sl_no):
    if not session.get('is_admin'): return redirect(url_for('index'))
    conn
