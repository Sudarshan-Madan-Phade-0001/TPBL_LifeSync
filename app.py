from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/lifesync_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    height_cm = db.Column(db.Numeric(5,2))
    weight_kg = db.Column(db.Numeric(5,2))
    created_date = db.Column(db.Date, default=date.today)
    created_time = db.Column(db.Time, default=datetime.now().time)
    
    def get_id(self):
        return str(self.user_id)

class Workout(db.Model):
    __tablename__ = 'workout'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    date = db.Column(db.Date, default=date.today, primary_key=True)
    time = db.Column(db.Time, default=datetime.now().time, primary_key=True)
    workout_type = db.Column(db.String(100))
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Numeric(6,2))
    notes = db.Column(db.Text)

class Meal(db.Model):
    __tablename__ = 'meal'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    date = db.Column(db.Date, default=date.today, primary_key=True)
    time = db.Column(db.Time, default=datetime.now().time, primary_key=True)
    meal_type = db.Column(db.String(50))
    food_items = db.Column(db.Text)
    calories = db.Column(db.Numeric(6,2))
    protein_g = db.Column(db.Numeric(5,2))
    carbs_g = db.Column(db.Numeric(5,2))
    fats_g = db.Column(db.Numeric(5,2))

class Sleep(db.Model):
    __tablename__ = 'sleep'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    date = db.Column(db.Date, default=date.today, primary_key=True)
    time = db.Column(db.Time, default=datetime.now().time, primary_key=True)
    sleep_hours = db.Column(db.Numeric(4,2))
    sleep_quality = db.Column(db.String(50))
    bedtime = db.Column(db.Time)
    wakeup_time = db.Column(db.Time)

class BodyStats(db.Model):
    __tablename__ = 'body_stats'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    date = db.Column(db.Date, default=date.today, primary_key=True)
    time = db.Column(db.Time, default=datetime.now().time, primary_key=True)
    weight_kg = db.Column(db.Numeric(5,2))
    bmi = db.Column(db.Numeric(4,2))
    body_fat_percent = db.Column(db.Numeric(5,2))
    muscle_mass_kg = db.Column(db.Numeric(5,2))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = int(request.form['age']) if request.form['age'] else None
        height_cm = float(request.form['height_cm']) if request.form['height_cm'] else None
        weight_kg = float(request.form['weight_kg']) if request.form['weight_kg'] else None
        gender = request.form['gender']
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            gender=gender
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
            print(f"Login failed for email: {email}")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    
    try:
        # Get today's data
        today_meals = Meal.query.filter_by(user_id=current_user.user_id, date=today).all()
        today_workouts = Workout.query.filter_by(user_id=current_user.user_id, date=today).all()
        today_sleep = Sleep.query.filter_by(user_id=current_user.user_id, date=today).first()
        
        total_calories_consumed = sum(float(meal.calories or 0) for meal in today_meals)
        total_calories_burned = sum(float(workout.calories_burned or 0) for workout in today_workouts)
        net_calories = total_calories_consumed - total_calories_burned
    except Exception as e:
        print(f"Dashboard error: {e}")
        today_meals = []
        today_workouts = []
        today_sleep = None
        total_calories_consumed = 0
        total_calories_burned = 0
        net_calories = 0
    
    return render_template('dashboard.html', 
                         total_calories_consumed=total_calories_consumed,
                         total_calories_burned=total_calories_burned,
                         net_calories=net_calories,
                         today_meals=today_meals,
                         today_workouts=today_workouts,
                         today_sleep=today_sleep)

@app.route('/meals')
@login_required
def meals():
    try:
        user_meals = Meal.query.filter_by(user_id=current_user.user_id).order_by(Meal.date.desc()).limit(10).all()
    except Exception as e:
        print(f"Meals error: {e}")
        user_meals = []
    return render_template('meals.html', user_meals=user_meals)

@app.route('/add_meal', methods=['POST'])
@login_required
def add_meal():
    meal = Meal(
        user_id=current_user.user_id,
        meal_type=request.form['meal_type'],
        food_items=request.form['food_items'],
        calories=float(request.form['calories']) if request.form['calories'] else None,
        protein_g=float(request.form['protein_g']) if request.form['protein_g'] else None,
        carbs_g=float(request.form['carbs_g']) if request.form['carbs_g'] else None,
        fats_g=float(request.form['fats_g']) if request.form['fats_g'] else None
    )
    db.session.add(meal)
    db.session.commit()
    flash('Meal added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/workouts')
@login_required
def workouts():
    user_workouts = Workout.query.filter_by(user_id=current_user.user_id).order_by(Workout.date.desc()).limit(10).all()
    return render_template('workouts.html', workouts=user_workouts)

@app.route('/add_workout', methods=['POST'])
@login_required
def add_workout():
    workout = Workout(
        user_id=current_user.user_id,
        workout_type=request.form['workout_type'],
        duration_minutes=int(request.form['duration_minutes']) if request.form['duration_minutes'] else None,
        calories_burned=float(request.form['calories_burned']) if request.form['calories_burned'] else None,
        notes=request.form.get('notes')
    )
    db.session.add(workout)
    db.session.commit()
    flash('Workout added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/sleep')
@login_required
def sleep():
    user_sleep = Sleep.query.filter_by(user_id=current_user.user_id).order_by(Sleep.date.desc()).limit(10).all()
    return render_template('sleep.html', sleep_records=user_sleep)

@app.route('/add_sleep', methods=['POST'])
@login_required
def add_sleep():
    bedtime = datetime.strptime(request.form['bedtime'], '%H:%M').time() if request.form['bedtime'] else None
    wakeup_time = datetime.strptime(request.form['wakeup_time'], '%H:%M').time() if request.form['wakeup_time'] else None
    
    # Calculate sleep hours automatically if both times provided
    sleep_hours = None
    if bedtime and wakeup_time:
        bedtime_dt = datetime.combine(date.today(), bedtime)
        wakeup_dt = datetime.combine(date.today(), wakeup_time)
        
        # If wake up time is earlier than bedtime, assume next day
        if wakeup_dt <= bedtime_dt:
            wakeup_dt += timedelta(days=1)
        
        sleep_duration = wakeup_dt - bedtime_dt
        sleep_hours = sleep_duration.total_seconds() / 3600
    elif request.form['sleep_hours']:
        sleep_hours = float(request.form['sleep_hours'])
    
    sleep_record = Sleep(
        user_id=current_user.user_id,
        sleep_hours=sleep_hours,
        sleep_quality=request.form.get('sleep_quality'),
        bedtime=bedtime,
        wakeup_time=wakeup_time
    )
    db.session.add(sleep_record)
    db.session.commit()
    flash('Sleep record added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/body_stats')
@login_required
def body_stats():
    stats = BodyStats.query.filter_by(user_id=current_user.user_id).order_by(BodyStats.date.desc()).limit(10).all()
    return render_template('body_stats.html', stats=stats)

@app.route('/add_body_stats', methods=['POST'])
@login_required
def add_body_stats():
    weight_kg = float(request.form['weight_kg']) if request.form['weight_kg'] else None
    height_cm = float(current_user.height_cm) if current_user.height_cm else None
    bmi = (weight_kg / ((height_cm/100) ** 2)) if weight_kg and height_cm else None
    
    stats = BodyStats(
        user_id=current_user.user_id,
        weight_kg=weight_kg,
        bmi=bmi,
        body_fat_percent=float(request.form['body_fat_percent']) if request.form['body_fat_percent'] else None,
        muscle_mass_kg=float(request.form['muscle_mass_kg']) if request.form['muscle_mass_kg'] else None
    )
    db.session.add(stats)
    db.session.commit()
    flash('Body stats updated successfully!')
    return redirect(url_for('dashboard'))





@app.route('/get_nutrition', methods=['POST'])
@login_required
def get_nutrition():
    food_query = request.json.get('query').lower()
    
    # Comprehensive food database with nutrition per 100g
    food_db = {
    'rice': {'cal': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3},
    'paneer': {'cal': 265, 'protein': 18, 'carbs': 1.2, 'fat': 20},
    'dal': {'cal': 116, 'protein': 9, 'carbs': 20, 'fat': 0.4},
    'roti': {'cal': 297, 'protein': 11, 'carbs': 51, 'fat': 7},
    'banana': {'cal': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3},
    'apple': {'cal': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2},
    'milk': {'cal': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1},
    'bread': {'cal': 265, 'protein': 9, 'carbs': 49, 'fat': 3.2},
    'pasta': {'cal': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1},
    'potato': {'cal': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1},
    'tomato': {'cal': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2},
    'onion': {'cal': 40, 'protein': 1.1, 'carbs': 9.3, 'fat': 0.1},
    'yogurt': {'cal': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4},
    'cheese': {'cal': 113, 'protein': 25, 'carbs': 1, 'fat': 0.3},
    'peanut': {'cal': 567, 'protein': 25.8, 'carbs': 16.1, 'fat': 49.2},
    'idli': {'cal': 58, 'protein': 2, 'carbs': 12, 'fat': 0.4},
    'dosa': {'cal': 168, 'protein': 3.9, 'carbs': 33, 'fat': 3.7},
    'uttapam': {'cal': 190, 'protein': 4, 'carbs': 34, 'fat': 4.5},
    'poha': {'cal': 180, 'protein': 4, 'carbs': 30, 'fat': 5},
    'upma': {'cal': 180, 'protein': 4, 'carbs': 27, 'fat': 6},
    'khichdi': {'cal': 150, 'protein': 5, 'carbs': 25, 'fat': 3},
    'sabudana khichdi': {'cal': 250, 'protein': 3, 'carbs': 45, 'fat': 6},
    'rajma': {'cal': 130, 'protein': 9, 'carbs': 22, 'fat': 0.5},
    'chole': {'cal': 140, 'protein': 8, 'carbs': 23, 'fat': 2},
    'bhindi masala': {'cal': 90, 'protein': 3, 'carbs': 10, 'fat': 5},
    'aloo gobi': {'cal': 120, 'protein': 3, 'carbs': 18, 'fat': 4},
    'palak paneer': {'cal': 190, 'protein': 10, 'carbs': 8, 'fat': 12},
    'matar paneer': {'cal': 210, 'protein': 11, 'carbs': 12, 'fat': 13},
    'shahi paneer': {'cal': 290, 'protein': 12, 'carbs': 10, 'fat': 22},
    'paneer butter masala': {'cal': 320, 'protein': 13, 'carbs': 12, 'fat': 25},
    'kadai paneer': {'cal': 270, 'protein': 15, 'carbs': 10, 'fat': 18},
    'mix veg': {'cal': 100, 'protein': 4, 'carbs': 14, 'fat': 3},
    'jeera rice': {'cal': 150, 'protein': 3, 'carbs': 30, 'fat': 2},
    'veg biryani': {'cal': 250, 'protein': 6, 'carbs': 38, 'fat': 8},
    'veg pulao': {'cal': 230, 'protein': 5, 'carbs': 36, 'fat': 7},
    'curd rice': {'cal': 160, 'protein': 5, 'carbs': 22, 'fat': 4},
    'sambar': {'cal': 70, 'protein': 3, 'carbs': 10, 'fat': 2},
    'rasam': {'cal': 40, 'protein': 1, 'carbs': 7, 'fat': 1},
    'chapati': {'cal': 120, 'protein': 3, 'carbs': 18, 'fat': 3},
    'paratha': {'cal': 210, 'protein': 5, 'carbs': 30, 'fat': 8},
    'stuffed paratha': {'cal': 240, 'protein': 6, 'carbs': 32, 'fat': 10},
    'thepla': {'cal': 150, 'protein': 4, 'carbs': 20, 'fat': 5},
    'dhokla': {'cal': 160, 'protein': 6, 'carbs': 20, 'fat': 5},
    'khandvi': {'cal': 120, 'protein': 5, 'carbs': 15, 'fat': 4},
    'handvo': {'cal': 180, 'protein': 6, 'carbs': 22, 'fat': 7},
    'sev khamani': {'cal': 210, 'protein': 7, 'carbs': 25, 'fat': 8},
    'patra': {'cal': 150, 'protein': 5, 'carbs': 18, 'fat': 6},
    'batata vada': {'cal': 280, 'protein': 4, 'carbs': 30, 'fat': 15},
    'vada pav': {'cal': 300, 'protein': 6, 'carbs': 40, 'fat': 12},
    'pav bhaji': {'cal': 400, 'protein': 9, 'carbs': 45, 'fat': 18},
    'misal pav': {'cal': 350, 'protein': 10, 'carbs': 38, 'fat': 15},
    'poori bhaji': {'cal': 450, 'protein': 8, 'carbs': 50, 'fat': 20},
    'idiyappam': {'cal': 160, 'protein': 3, 'carbs': 35, 'fat': 1},
    'pongal': {'cal': 220, 'protein': 6, 'carbs': 35, 'fat': 7},
    'upkari': {'cal': 120, 'protein': 3, 'carbs': 15, 'fat': 5},
    'avial': {'cal': 150, 'protein': 5, 'carbs': 12, 'fat': 8},
    'poriyal': {'cal': 100, 'protein': 3, 'carbs': 10, 'fat': 5},
    'kootu': {'cal': 130, 'protein': 6, 'carbs': 14, 'fat': 4},
    'cabbage sabzi': {'cal': 80, 'protein': 3, 'carbs': 10, 'fat': 4},
    'lauki sabzi': {'cal': 70, 'protein': 2, 'carbs': 9, 'fat': 3},
    'tinda sabzi': {'cal': 75, 'protein': 2, 'carbs': 9, 'fat': 3},
    'karela sabzi': {'cal': 85, 'protein': 3, 'carbs': 10, 'fat': 4},
    'gajar matar sabzi': {'cal': 110, 'protein': 3, 'carbs': 15, 'fat': 5},
    'methi aloo': {'cal': 120, 'protein': 3, 'carbs': 18, 'fat': 4},
    'baingan bharta': {'cal': 150, 'protein': 4, 'carbs': 12, 'fat': 8},
    'lauki kofta': {'cal': 200, 'protein': 6, 'carbs': 14, 'fat': 12},
    'malai kofta': {'cal': 280, 'protein': 8, 'carbs': 15, 'fat': 20},
    'navratan korma': {'cal': 260, 'protein': 7, 'carbs': 20, 'fat': 17},
    'veg manchurian': {'cal': 220, 'protein': 6, 'carbs': 25, 'fat': 10},
    'hakka noodles': {'cal': 250, 'protein': 6, 'carbs': 35, 'fat': 9},
    'veg fried rice': {'cal': 230, 'protein': 5, 'carbs': 38, 'fat': 6},
    'vegetable curry': {'cal': 180, 'protein': 6, 'carbs': 20, 'fat': 7},
    'dal makhani': {'cal': 230, 'protein': 9, 'carbs': 20, 'fat': 12},
    'moong dal': {'cal': 110, 'protein': 8, 'carbs': 18, 'fat': 0.5},
    'toor dal': {'cal': 120, 'protein': 7, 'carbs': 22, 'fat': 0.8},
    'masoor dal': {'cal': 130, 'protein': 9, 'carbs': 24, 'fat': 0.6},
    'tadka dal': {'cal': 180, 'protein': 8, 'carbs': 22, 'fat': 6},
    'chana dal': {'cal': 150, 'protein': 9, 'carbs': 25, 'fat': 3},
    'idiyappam': {'cal': 160, 'protein': 3, 'carbs': 35, 'fat': 1},
    'kheer': {'cal': 200, 'protein': 6, 'carbs': 25, 'fat': 8},
    'halwa': {'cal': 250, 'protein': 5, 'carbs': 30, 'fat': 12},
    'gulab jamun': {'cal': 150, 'protein': 3, 'carbs': 25, 'fat': 6},
    'jalebi': {'cal': 220, 'protein': 2, 'carbs': 35, 'fat': 8},
    'rasgulla': {'cal': 125, 'protein': 4, 'carbs': 22, 'fat': 2},
    'barfi': {'cal': 180, 'protein': 5, 'carbs': 20, 'fat': 8},
    'laddu': {'cal': 220, 'protein': 4, 'carbs': 25, 'fat': 10},
    'mysore pak': {'cal': 250, 'protein': 5, 'carbs': 28, 'fat': 12},
    'soan papdi': {'cal': 200, 'protein': 4, 'carbs': 25, 'fat': 9},
    'rabri': {'cal': 250, 'protein': 6, 'carbs': 28, 'fat': 13},
    'sandesh': {'cal': 140, 'protein': 5, 'carbs': 20, 'fat': 5},
    'basundi': {'cal': 230, 'protein': 7, 'carbs': 25, 'fat': 11},
    'sheera': {'cal': 190, 'protein': 4, 'carbs': 25, 'fat': 8},
    'tea': {'cal': 30, 'protein': 1, 'carbs': 5, 'fat': 0.5},
    'coffee': {'cal': 40, 'protein': 1, 'carbs': 6, 'fat': 1},
    'lassi': {'cal': 150, 'protein': 6, 'carbs': 18, 'fat': 5},
    'buttermilk': {'cal': 40, 'protein': 3, 'carbs': 4, 'fat': 1},
    'lemon juice': {'cal': 25, 'protein': 0.4, 'carbs': 6, 'fat': 0.1},
    'coconut water': {'cal': 19, 'protein': 0.7, 'carbs': 3.7, 'fat': 0.2},
    'bhel puri': {'cal': 280, 'protein': 8, 'carbs': 45, 'fat': 8},
    'sev puri': {'cal': 300, 'protein': 6, 'carbs': 40, 'fat': 12},
    'pani puri': {'cal': 330, 'protein': 7, 'carbs': 45, 'fat': 14},
    'dahi puri': {'cal': 340, 'protein': 8, 'carbs': 46, 'fat': 14},
    'samosa': {'cal': 260, 'protein': 6, 'carbs': 32, 'fat': 12},
    'kachori': {'cal': 280, 'protein': 7, 'carbs': 35, 'fat': 14},
    'pakora': {'cal': 200, 'protein': 6, 'carbs': 20, 'fat': 10},
    'aloo tikki': {'cal': 220, 'protein': 5, 'carbs': 30, 'fat': 9},
    'dhokla sandwich': {'cal': 210, 'protein': 7, 'carbs': 25, 'fat': 8},
    'corn chaat': {'cal': 180, 'protein': 5, 'carbs': 28, 'fat': 6},
    'fruit chaat': {'cal': 120, 'protein': 2, 'carbs': 25, 'fat': 1},
    'sprouts salad': {'cal': 150, 'protein': 10, 'carbs': 18, 'fat': 3},
    'moong chaat': {'cal': 160, 'protein': 9, 'carbs': 20, 'fat': 3},
    'oats porridge': {'cal': 150, 'protein': 6, 'carbs': 27, 'fat': 3},
    'ragi dosa': {'cal': 160, 'protein': 5, 'carbs': 30, 'fat': 3},
    'rava dosa': {'cal': 170, 'protein': 4, 'carbs': 32, 'fat': 4},
    'set dosa': {'cal': 200, 'protein': 5, 'carbs': 35, 'fat': 5},
    'neer dosa': {'cal': 120, 'protein': 3, 'carbs': 20, 'fat': 3},
    'adai': {'cal': 180, 'protein': 6, 'carbs': 28, 'fat': 5},
    'pesarattu': {'cal': 150, 'protein': 7, 'carbs': 24, 'fat': 3},
    'puttu': {'cal': 180, 'protein': 4, 'carbs': 32, 'fat': 5},
    'appam': {'cal': 120, 'protein': 3, 'carbs': 22, 'fat': 3},
    'veg cutlet': {'cal': 200, 'protein': 6, 'carbs': 25, 'fat': 9},
    'paneer tikka': {'cal': 270, 'protein': 18, 'carbs': 8, 'fat': 20},
    'veg sandwich': {'cal': 220, 'protein': 7, 'carbs': 28, 'fat': 8},
    'cheese sandwich': {'cal': 250, 'protein': 9, 'carbs': 30, 'fat': 10},
    'grilled sandwich': {'cal': 280, 'protein': 10, 'carbs': 30, 'fat': 12},
    'veg burger': {'cal': 350, 'protein': 9, 'carbs': 45, 'fat': 14},
    'veg pizza': {'cal': 300, 'protein': 10, 'carbs': 36, 'fat': 12},
    'aloo paratha': {'cal': 250, 'protein': 6, 'carbs': 35, 'fat': 10},
    'gobi paratha': {'cal': 230, 'protein': 7, 'carbs': 32, 'fat': 9}
  }
    
    total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    
    # Parse food items with quantities
    items = food_query.split(',')
    
    for item in items:
        item = item.strip()
        # Extract quantity (grams)
        import re
        gram_match = re.search(r'(\d+)\s*g', item)
        quantity = int(gram_match.group(1)) if gram_match else 100
        
        # Find matching food
        for food_name, nutrition in food_db.items():
            if food_name in item:
                multiplier = quantity / 100
                total_nutrition['calories'] += nutrition['cal'] * multiplier
                total_nutrition['protein'] += nutrition['protein'] * multiplier
                total_nutrition['carbs'] += nutrition['carbs'] * multiplier
                total_nutrition['fat'] += nutrition['fat'] * multiplier
                break
    
    return jsonify(total_nutrition)

@app.route('/dietitian')
@login_required
def dietitian():
    return render_template('dietitian_chat.html')

@app.route('/chat_with_ai', methods=['POST'])
@login_required
def chat_with_ai():
    from ai_service import get_ai_response
    user_message = request.json.get('message')
    ai_response = get_ai_response(user_message)
    return jsonify({'response': ai_response})

@app.route('/suggestions')
@login_required
def suggestions():
    week_ago = date.today() - timedelta(days=7)
    
    # Get user data for analysis
    weekly_meals = db.session.query(db.func.sum(Meal.calories), db.func.avg(Meal.protein_g)).filter(
        Meal.user_id == current_user.user_id,
        Meal.date >= week_ago
    ).first()
    
    weekly_workouts = db.session.query(db.func.sum(Workout.calories_burned), db.func.count(Workout.user_id)).filter(
        Workout.user_id == current_user.user_id,
        Workout.date >= week_ago
    ).first()
    
    avg_sleep = db.session.query(db.func.avg(Sleep.sleep_hours)).filter(
        Sleep.user_id == current_user.user_id,
        Sleep.date >= week_ago
    ).scalar()
    
    latest_weight = db.session.query(BodyStats.weight_kg, BodyStats.bmi).filter(
        BodyStats.user_id == current_user.user_id
    ).order_by(BodyStats.date.desc()).first()
    
    # Generate suggestions
    suggestions = generate_suggestions(
        weekly_meals[0] or 0, weekly_meals[1] or 0,
        weekly_workouts[0] or 0, weekly_workouts[1] or 0,
        avg_sleep or 0, latest_weight, current_user
    )
    
    return render_template('suggestions.html', suggestions=suggestions)

def generate_suggestions(total_calories, avg_protein, calories_burned, workout_count, avg_sleep, weight_data, user):
    suggestions = []
    
    # Calorie analysis
    daily_calories = total_calories / 7 if total_calories else 0
    daily_burned = calories_burned / 7 if calories_burned else 0
    net_calories = daily_calories - daily_burned
    
    if daily_calories < 1200:
        suggestions.append({
            'type': 'warning',
            'title': 'Low Calorie Intake',
            'message': f'Your average daily intake is {daily_calories:.0f} calories. Consider increasing to at least 1200 calories for proper nutrition.',
            'action': 'Add healthy snacks like nuts, fruits, or yogurt between meals.'
        })
    elif daily_calories > 2500:
        suggestions.append({
            'type': 'info',
            'title': 'High Calorie Intake',
            'message': f'Your average daily intake is {daily_calories:.0f} calories. Consider portion control if weight loss is your goal.',
            'action': 'Focus on nutrient-dense, lower-calorie foods like vegetables and lean proteins.'
        })
    
    # Protein analysis
    if avg_protein and avg_protein < 50:
        suggestions.append({
            'type': 'warning',
            'title': 'Low Protein Intake',
            'message': f'Your average protein intake is {avg_protein:.1f}g daily. Aim for at least 1.2g per kg body weight.',
            'action': 'Include more chicken, fish, eggs, paneer, or dal in your meals.'
        })
    
    # Workout analysis
    if workout_count < 3:
        suggestions.append({
            'type': 'info',
            'title': 'Increase Physical Activity',
            'message': f'You worked out {workout_count} times this week. Aim for at least 3-4 sessions weekly.',
            'action': 'Try 30-minute walks, home workouts, or join a fitness class.'
        })
    
    if daily_burned < 200:
        suggestions.append({
            'type': 'info',
            'title': 'Low Calorie Burn',
            'message': f'Your average daily calorie burn is {daily_burned:.0f}. Increase workout intensity or duration.',
            'action': 'Add cardio exercises like running, cycling, or swimming to your routine.'
        })
    
    # Sleep analysis
    if avg_sleep and avg_sleep < 7:
        suggestions.append({
            'type': 'warning',
            'title': 'Insufficient Sleep',
            'message': f'Your average sleep is {avg_sleep:.1f} hours. Aim for 7-9 hours for optimal health.',
            'action': 'Set a consistent bedtime, avoid screens before sleep, and create a relaxing environment.'
        })
    elif avg_sleep and avg_sleep > 9:
        suggestions.append({
            'type': 'info',
            'title': 'Excessive Sleep',
            'message': f'Your average sleep is {avg_sleep:.1f} hours. This might indicate underlying health issues.',
            'action': 'Consider consulting a healthcare provider if you consistently need more than 9 hours.'
        })
    
    # BMI analysis
    if weight_data and weight_data.bmi:
        bmi = float(weight_data.bmi)
        if bmi < 18.5:
            suggestions.append({
                'type': 'warning',
                'title': 'Underweight',
                'message': f'Your BMI is {bmi:.1f}. Consider gaining weight through healthy foods.',
                'action': 'Increase calorie intake with nuts, healthy oils, and protein-rich foods.'
            })
        elif bmi > 25:
            suggestions.append({
                'type': 'info',
                'title': 'Weight Management',
                'message': f'Your BMI is {bmi:.1f}. Consider a balanced approach to weight management.',
                'action': 'Focus on portion control, regular exercise, and sustainable lifestyle changes.'
            })
    
    # Calorie balance
    if net_calories > 500:
        suggestions.append({
            'type': 'info',
            'title': 'Calorie Surplus',
            'message': f'You have a daily surplus of {net_calories:.0f} calories. This may lead to weight gain.',
            'action': 'Increase physical activity or reduce portion sizes if weight maintenance is your goal.'
        })
    elif net_calories < -500:
        suggestions.append({
            'type': 'warning',
            'title': 'Large Calorie Deficit',
            'message': f'You have a daily deficit of {abs(net_calories):.0f} calories. This may be too aggressive.',
            'action': 'Consider increasing calorie intake slightly for sustainable weight loss.'
        })
    
    # Default positive message if no issues
    if not suggestions:
        suggestions.append({
            'type': 'success',
            'title': 'Great Progress!',
            'message': 'Your health metrics look good. Keep up the excellent work!',
            'action': 'Continue your current routine and consider setting new fitness goals.'
        })
    
    return suggestions

@app.route('/analytics')
@login_required
def analytics():
    week_ago = date.today() - timedelta(days=7)
    
    weekly_meals = db.session.query(Meal.date, db.func.sum(Meal.calories)).filter(
        Meal.user_id == current_user.user_id,
        Meal.date >= week_ago
    ).group_by(Meal.date).all()
    
    weekly_workouts = db.session.query(Workout.date, db.func.sum(Workout.calories_burned)).filter(
        Workout.user_id == current_user.user_id,
        Workout.date >= week_ago
    ).group_by(Workout.date).all()
    
    return render_template('analytics.html', 
                         weekly_meals=weekly_meals,
                         weekly_workouts=weekly_workouts)

def init_sample_data():
    """Initialize sample data"""
    try:
        # Sample data can be added here if needed
        pass
    except Exception as e:
        print(f"Database initialization error: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            init_sample_data()
            print(f"Database tables created successfully")
        except Exception as e:
            print(f"Database error: {e}")
    print("Starting LifeSync on http://127.0.0.1:3000")
    app.run(host='localhost', port=3000, debug=True, use_reloader=False)
