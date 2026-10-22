from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'zphs_nandigama_scouts_secret_key'

# అడ్మిన్ లాగిన్ వివరాలు
ADMIN_CREDENTIALS = {
    "sailakshmikalyanam5990@gmail.com": "admin123",
    "sundarrao@gmail.com": "admin123"
}

students = []
monthly_reports = []

# పూర్తి వెబ్‌సైట్ డిజైన్ మరియు లాజిక్ కోడ్
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="te">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZPHS Nandigama Scouts & Guides Portal</title>
    <style>
        :root { --white: #ffffff; --blue: #1d4ed8; --green: #15803d; --violet: #6b21a8; --bg: #f8fafc; }
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: var(--bg); color: #1e293b; }
        header { background-color: var(--blue); color: var(--white); padding: 20px; text-align: center; border-bottom: 5px solid var(--violet); }
        header h1 { margin: 0; font-size: 22px; }
        header h2 { margin: 5px 0 0 0; font-size: 16px; color: #cbd5e1; }
        nav { background-color: var(--violet); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        nav span, nav a { color: var(--white); text-decoration: none; font-weight: bold; }
        .admin-login-btn { background-color: var(--green); color: var(--white); padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 14px; }
        .container { max-width: 950px; margin: 20px auto; padding: 20px; background: var(--white); border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .search-box { display: flex; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }
        .search-box input { flex: 1; min-width: 200px; padding: 12px; border: 2px solid var(--blue); border-radius: 6px; font-size: 16px; }
        .search-box button { width: 140px; background-color: var(--blue); color: var(--white); border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; }
        .bio-card { border: 2px solid var(--green); border-radius: 8px; padding: 15px; margin-bottom: 25px; background-color: #f0fdf4; }
        .bio-card h3 { color: var(--violet); margin-top: 0; border-bottom: 2px solid var(--green); padding-bottom: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .bio-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }
        .modal-login { border: 2px solid var(--violet); padding: 20px; border-radius: 8px; background: #faf5ff; margin-bottom: 25px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: var(--violet); }
        input[type="text"], input[type="password"], select, textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box; }
        .btn { background-color: var(--green); color: var(--white); border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn-edit { background-color: #d97706; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; text-decoration: none; }
        .btn-report { background-color: var(--blue); color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; text-decoration: none; }
        .flash-msg { background-color: #fef2f2; color: #991b1b; padding: 10px; border-radius: 4px; margin-bottom: 15px; border: 1px solid #fecaca; }
        .report-sheet { border: 2px solid #000; padding: 30px; background: #fff; margin-top: 20px; font-family: 'Times New Roman', serif; }
        .report-header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 15px; margin-bottom: 20px; }
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
            <a href="/admin/dashboard" style="margin-right: 15px; background: var(--green); padding: 6px 12px; border-radius: 4px;">అడ్మిన్ డ్యాష్‌బోర్డ్</a>
            <a href="/logout" style="color: #fecaca;">లాగౌట్ (Logout)</a>
        {% else %}
            <a href="/?show_admin_login=true" class="admin-login-btn">అడ్మిన్ లాగిన్ (Admin Login)</a>
        {% endif %}
    </div>
</nav>
<div class="container">
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <div class="flash-msg">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {% if show_admin_login and not session.get('is_admin') %}
        <div class="modal-login">
            <h3 style="color: var(--violet); margin-top: 0;">అడ్మిన్ లాగిన్ ప్యానెల్</h3>
            <form method="POST" action="/admin/login">
                <div class="form-group">
                    <label>ఈమెయిల్ / యూజర్ నేమ్:</label>
                    <input type="text" name="username" required placeholder="sailakshmikalyanam5990@gmail.com లేదా sundarrao@gmail.com">
                </div>
                <div class="form-group">
                    <label>పాస్‌వర్డ్:</label>
                    <input type="password" name="password" required placeholder="పాస్‌వర్డ్ టైప్ చేయండి">
                </div>
                <button type="submit" class="btn">లాగిన్ అవ్వండి</button>
                <a href="/" style="margin-left: 10px; color: #64748b; text-decoration: none;">క్యాన్సిల్</a>
            </form>
        </div>
    {% endif %}

    {% if session.get('is_admin') and not generate_report_student and not edit_student %}
        <div class="modal-login" style="border-color: var(--green); background: #f0fdf4; margin-bottom: 30px;">
            <h3 style="color: var(--green); margin-top: 0;">➕ కొత్త విద్యార్థిని చేర్చండి (Add New Student)</h3>
            <form method="POST" action="/admin/add_student">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div class="form-group">
                        <label>విద్యార్థి పేరు:</label>
                        <input type="text" name="name" required placeholder="పేరు రాయండి">
                    </div>
                    <div class="form-group">
                        <label>కేటగిరీ:</label>
                        <select name="category">
                            <option value="Scout">Scout</option>
                            <option value="Guide">Guide</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>UID:</label>
                        <input type="text" name="uid" placeholder="UID నంబర్">
                    </div>
                    <div class="form-group">
                        <label>BSG ID:</label>
                        <input type="text" name="bsg_uid" placeholder="BSG ID నంబర్">
                    </div>
                    <div class="form-group">
                        <label>తండ్రి పేరు:</label>
                        <input type="text" name="father_name" placeholder="తండ్రి పేరు">
                    </div>
                    <div class="form-group">
                        <label>కులం:</label>
                        <input type="text" name="caste" placeholder="కులం">
                    </div>
                    <div class="form-group">
                        <label>తరగతి:</label>
                        <input type="text" name="class_name" placeholder="ఉదా: 8th Class">
                    </div>
                </div>
                <button type="submit" class="btn" style="margin-top: 10px;">విద్యార్థిని సేవ్ చేయి</button>
            </form>
        </div>
    {% endif %}

    {% if generate_report_student and session.get('is_admin') %}
        <div class="modal-login" style="border-color: var(--blue); background: #eff6ff;">
            <h3 style="color: var(--blue); margin-top: 0;">MONTHLY REPORT జనరేట్ చేయండి ({{ generate_report_student.name }})</h3>
            <form method="POST" action="/admin/save_report/{{ generate_report_student.sl_no }}">
                <div class="form-group">
                    <label>మొత్తం హాజరైన తరగతులు:</label>
                    <input type="text" name="classes_attended" required placeholder="ఉదా: 4 / 4">
                </div>
                <div class="form-group">
                    <label>యూనిఫాం నిర్వహణ:</label>
                    <input type="text" name="uniform_maint" required placeholder="ఉదా: Good">
                </div>
                <div class="form-group">
                    <label>సమీక్షలు / రిమార్క్స్:</label>
                    <textarea name="remarks" rows="2" required placeholder="రిమార్క్స్ రాయండి..."></textarea>
                </div>
                <div class="form-group">
                    <label>మెరుగుదల అవసరం:</label>
                    <input type="text" name="improvement" required placeholder="ఉదా: Scarf & Cap proper">
                </div>
                <div class="form-group">
                    <label>పూర్తయిన నోట్స్:</label>
                    <input type="text" name="notes_completed" required placeholder="ఉదా: Fully Completed">
                </div>
                <div class="form-group">
                    <label>అనుభవం మరియు లీడర్ ఫిర్యాదులు:</label>
                    <textarea name="experience" rows="3" required placeholder="అనుభవం రాయండి..."></textarea>
                </div>
                <button type="submit" class="btn" style="background-color: var(--blue);">మంత్లీ రిపోర్ట్ అప్లోడ్ చేయి</button>
                <a href="/admin/dashboard" style="margin-left: 10px; color: #64748b; text-decoration: none;">క్యాన్సిల్</a>
            </form>
        </div>
    {% endif %}

    {% if view_report %}
        <div class="report-sheet">
            <div class="report-header">
                <h3>THE BHARAT SCOUTS AND GUIDES</h3>
                <h2>MONTHLY REPORT</h2>
                <p>Z.P.H.S plus N.T.R Dt. 521185</p>
            </div>
            <p><strong>Name of the scout :-</strong> {{ view_report.student_name }}</p>
            <p><strong>UDISE Code :-</strong> 28160400523</p>
            <hr style="border: 1px solid #000; margin: 15px 0;">
            <p><strong>No. of classes attended this month :-</strong> {{ view_report.classes_attended }}</p>
            <p><strong>Uniform maintenance :-</strong> {{ view_report.uniform_maint }}</p>
            <p><strong>Remarks :-</strong> {{ view_report.remarks }}</p>
            <p><strong>Improvement needed :-</strong> {{ view_report.improvement }}</p>
            <p><strong>How many notes completed :-</strong> {{ view_report.notes_completed }}</p>
            <p><strong>Experience and complaints from leader :-</strong> {{ view_report.experience }}</p>
            <br><br>
            <div style="display: flex; justify-content: space-between; margin-top: 40px;">
                <div><strong>HM signature :-</strong> <br><br> (Signed)</div>
                <div><strong>SCOUT MASTER signature :-</strong> <br><br> (Signed)</div>
            </div>
            <br>
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn" style="text-decoration: none;">హోమ్ పేజీకి వెళ్ళు</a>
            </div>
        </div>
    {% endif %}

    {% if edit_student and session.get('is_admin') %}
        <div class="modal-login" style="border-color: #d97706; background: #fffbeb;">
            <h3 style="color: #d97706; margin-top: 0;">విద్యార్థి ప్రొఫైల్ సవరించు (Edit: {{ edit_student.name }})</h3>
            <form method="POST" action="/admin/edit/{{ edit_student.sl_no }}">
                <div class="form-group">
                    <label>విద్యార్థి పేరు:</label>
                    <input type="text" name="name" value="{{ edit_student.name }}" required>
                </div>
                <div class="form-group">
                    <label>కేటగిరీ (Scout / Guide):</label>
                    <select name="category">
                        <option value="Scout" {% if edit_student.category == 'Scout' %}selected{% endif %}>Scout</option>
                        <option value="Guide" {% if edit_student.category == 'Guide' %}selected{% endif %}>Guide</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>UID:</label>
                    <input type="text" name="uid" value="{{ edit_student.uid }}">
                </div>
                <div class="form-group">
                    <label>BSG ID:</label>
                    <input type="text" name="bsg_uid" value="{{ edit_student.bsg_uid }}">
                </div>
                <button type="submit" class="btn" style="background-color: #d97706;">సేవ్ చేయి</button>
                <a href="/admin/dashboard" style="margin-left: 10px; color: #64748b; text-decoration: none;">క్యాన్సిల్</a>
            </form>
        </div>
    {% endif %}

    {% if not view_report %}
    <form method="GET" action="/" class="search-box">
        <input type="text" name="search" value="{{ search_query }}" placeholder="స్కౌట్ పేరు లేదా UID టైప్ చేసి సెర్చ్ చేయండి...">
        <button type="submit">సెర్చ్</button>
    </form>

    {% if search_results %}
        <h3>విద్యార్థుల జాబితా / సెర్చ్ ఫలితాలు ({{ search_results|length }} మంది):</h3>
        {% for scout in search_results %}
            <div class="bio-card">
                <h3>
                    <span>[{{ loop.index }}] {{ scout.name }} ({{ scout.category }})</span>
                    {% if session.get('is_admin') %}
                        <div>
                            <a href="/admin/report_form/{{ scout.sl_no }}" class="btn-report" style="margin-right: 5px;">Generate Monthly Report</a>
                            <a href="/admin/edit_form/{{ scout.sl_no }}" class="btn-edit">Edit Profile</a>
                        </div>
                    {% else %}
                        {% set ns = namespace(has_report=False) %}
                        {% for rep in monthly_reports %}
                            {% if rep.student_sl == scout.sl_no %}
                                {% set ns.has_report = True %}
                            {% endif %}
                        {% endfor %}
                        {% if ns.has_report %}
                            <a href="/view_report/{{ scout.sl_no }}" class="btn-report">View Monthly Report</a>
                        {% endif %}
                    {% endif %}
                </h3>
                <div class="bio-grid">
                    <p><strong>UID:</strong> {{ scout.uid }}</p>
                    <p><strong>BSG ID:</strong> {{ scout.bsg_uid }}</p>
                    <p><strong>తండ్రి పేరు:</strong> {{ scout.father_name }}</p>
                    <p><strong>కులం:</strong> {{ scout.caste }}</p>
                    <p><strong>తరగతి:</strong> {{ scout.class_name }} - {{ scout.section }}</p>
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p style="text-align: center; color: #64748b; padding: 20px;">ప్రస్తుతం ఎలాంటి విద్యార్థులు లేరు. అడ్మిన్ లాగిన్ అయి కొత్త విద్యార్థులను చేర్చండి.</p>
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
    
    if search_query:
        search_results = [
            s for s in students 
            if search_query in s['name'].lower() 
            or search_query in str(s['uid']).lower() 
            or search_query in str(s['bsg_uid']).lower()
        ]
    else:
        search_results = students

    return render_template_string(HTML_TEMPLATE, 
                           search_results=search_results, 
                           search_query=search_query,
                           show_admin_login=show_admin_login,
                           monthly_reports=monthly_reports)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        session['is_admin'] = True
        flash('అడ్మిన్ లాగిన్ విజయవంతమైంది!', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('తప్పు ఈమెయిల్ లేదా పాస్‌వర్డ్!', 'error')
        return redirect(url_for('index', show_admin_login=True))

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    flash('లాగౌట్ అయ్యారు.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    return render_template_string(HTML_TEMPLATE, search_results=students, monthly_reports=monthly_reports)

@app.route('/admin/add_student', methods=['POST'])
def add_student():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    
    new_student = {
        "sl_no": len(students) + 1,
        "name": request.form.get('name'),
        "category": request.form.get('category'),
        "uid": request.form.get('uid'),
        "bsg_uid": request.form.get('bsg_uid'),
        "father_name": request.form.get('father_name'),
        "caste": request.form.get('caste'),
        "class_name": request.form.get('class_name'),
        "section": request.form.get('section', 'A')
    }
    
    students.append(new_student)
    flash('కొత్త విద్యార్థి విజయవంతంగా చేర్చబడ్డారు!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_form/<int:sl_no>')
def edit_form(sl_no):
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    student = next((s for s in students if s['sl_no'] == sl_no), None)
    return render_template_string(HTML_TEMPLATE, edit_student=student, search_results=students, monthly_reports=monthly_reports)

@app.route('/admin/edit/<int:sl_no>', methods=['POST'])
def edit_student(sl_no):
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    student = next((s for s in students if s['sl_no'] == sl_no), None)
    if student:
        student['name'] = request.form.get('name')
        student['category'] = request.form.get('category')
        student['uid'] = request.form.get('uid')
        student['bsg_uid'] = request.form.get('bsg_uid')
        flash('ప్రొఫైల్ విజయవంతంగా నవీకరించబడింది!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/report_form/<int:sl_no>')
def report_form(sl_no):
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    student = next((s for s in students if s['sl_no'] == sl_no), None)
    return render_template_string(HTML_TEMPLATE, generate_report_student=student, search_results=students, monthly_reports=monthly_reports)

@app.route('/admin/save_report/<int:sl_no>', methods=['POST'])
def save_report(sl_no):
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    student = next((s for s in students if s['sl_no'] == sl_no), None)
    if student:
        report = {
            "student_sl": sl_no,
            "student_name": student['name'],
            "classes_attended": request.form.get('classes_attended'),
            "uniform_maint": request.form.get('uniform_maint'),
            "remarks": request.form.get('remarks'),
            "improvement": request.form.get('improvement'),
            "notes_completed": request.form.get('notes_completed'),
            "experience": request.form.get('experience')
        }
        global monthly_reports
        monthly_reports = [r for r in monthly_reports if r['student_sl'] != sl_no]
        
