import os
import re
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from flask import (
    Flask, render_template, request, redirect,
    url_for, jsonify, flash, session
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

app.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', os.urandom(24).hex()),
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///site.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SESSION_COOKIE_SECURE': False,
    'SESSION_COOKIE_HTTPONLY': True
})

db = SQLAlchemy(app)

@app.template_filter('strftime')
def strftime_filter(value, fmt):
    if value == 'now':
        return datetime.now().strftime(fmt)
    if isinstance(value, datetime):
        return value.strftime(fmt)
    return value

# --- MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    open_time = db.Column(db.String(10))
    close_time = db.Column(db.String(10))

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin / admin123")

init_db()

def extract_coordinates(url):
    try:
        parsed = urlparse(url)
        if 'google.com/maps' in parsed.netloc:
            qs = parse_qs(parsed.query)
            if 'q' in qs:
                lat, lng = qs['q'][0].split(',', 1)
                return float(lat), float(lng)
            m = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
            if m:
                return float(m.group(1)), float(m.group(2))
    except Exception:
        pass
    return None

def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Unauthorized', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if len(p) < 8:
            flash('Password ≥ 8 chars', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=u).first():
            flash('Username exists', 'danger')
            return redirect(url_for('register'))
        pwd = generate_password_hash(p)
        db.session.add(User(username=u, password=pwd))
        db.session.commit()
        flash('Registered. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        user = User.query.filter_by(username=u).first()
        if user and check_password_hash(user.password, p):
            session.update({
                'user_id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            })
            return redirect(url_for('admin_dashboard' if user.is_admin else 'dashboard'))
        flash('Invalid login', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',
        locations=Location.query.all(),
        faculties=Faculty.query.all()
    )

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html',
        locations=Location.query.all(),
        faculties=Faculty.query.all()
    )

@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    f = request.files.get('qr_image')
    if not f or f.filename == '':
        return jsonify(error='No file'), 400
    try:
        img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
        obj = decode(img)
        if not obj:
            return jsonify(error='No QR detected'), 400
        data = obj[0].data.decode()
        loc = Location.query.filter_by(name=data).first()
        url = url_for('navigate', destination=data) if loc else (data if data.startswith('http') else '#')
        return jsonify(redirect=url)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/navigate')
def navigate():
    dest = request.args.get('destination')
    loc = Location.query.filter_by(name=dest).first()
    if not loc:
        return jsonify(error='Not found'), 400
    return jsonify(google_map_link=f"https://www.google.com/maps?q={loc.latitude},{loc.longitude}")

@app.route('/get_locations')
def get_locations():
    return jsonify([{
        'id': L.id, 'name': L.name,
        'lat': L.latitude, 'lng': L.longitude,
        'description': L.description,
        'open_time': L.open_time,
        'close_time': L.close_time,
        'google_map_link': f"https://www.google.com/maps?q={L.latitude},{L.longitude}"
    } for L in Location.query.all()])

@app.route('/get_faculties')
def get_faculties():
    return jsonify([{
        'id': F.id, 'name': F.name,
        'department': F.department,
        'year': F.year
    } for F in Faculty.query.all()])

# Admin add/edit/delete
@app.route('/admin/add_location', methods=['POST'])
@login_required
@admin_required
def add_location():
    data = request.form
    try:
        db.session.add(Location(
            name=data['name'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            description=data.get('description'),
            open_time=data.get('open_time'),
            close_time=data.get('close_time')
        ))
        db.session.commit()
        flash('Location added', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_location/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_location(id):
    L = Location.query.get_or_404(id)
    if request.method == 'POST':
        try:
            form = request.form
            L.name = form['name']
            L.latitude = float(form['latitude'])
            L.longitude = float(form['longitude'])
            L.description = form.get('description')
            L.open_time = form.get('open_time')
            L.close_time = form.get('close_time')
            db.session.commit()
            flash('Updated', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}', 'danger')
    return render_template('edit_location.html', location=L)

@app.route('/admin/delete_location/<int:id>')
@login_required
@admin_required
def delete_location(id):
    L = Location.query.get_or_404(id)
    try:
        db.session.delete(L)
        db.session.commit()
        flash('Deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_faculty', methods=['POST'])
@login_required
@admin_required
def add_faculty():
    data = request.form
    try:
        db.session.add(Faculty(
            name=data['name'],
            department=data['department'],
            year=int(data['year'])
        ))
        db.session.commit()
        flash('Faculty added', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_faculty/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_faculty(id):
    F = Faculty.query.get_or_404(id)
    if request.method == 'POST':
        try:
            form = request.form
            F.name = form['name']
            F.department = form['department']
            F.year = int(form['year'])
            db.session.commit()
            flash('Updated', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}', 'danger')
    return render_template('edit_faculty.html', faculty=F)

@app.route('/admin/delete_faculty/<int:id>')
@login_required
@admin_required
def delete_faculty(id):
    F = Faculty.query.get_or_404(id)
    try:
        db.session.delete(F)
        db.session.commit()
        flash('Deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# --- START SERVER ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
