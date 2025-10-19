from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost/lifesync_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    gender = db.Column(db.String(10))
    activity_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Dietitian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    specialization = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories_per_100g = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    fiber = db.Column(db.Float)
    category = db.Column(db.String(50))
    is_veg = db.Column(db.Boolean, default=True)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=date.today)
    total_calories = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MealItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Float, nullable=False)
    intensity = db.Column(db.String(20))
    date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sleep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sleep_time = db.Column(db.Time, nullable=False)
    wake_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    quality = db.Column(db.String(20))
    date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BodyStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float)
    body_fat = db.Column(db.Float)
    muscle_mass = db.Column(db.Float)
    bmi = db.Column(db.Float)
    date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Steps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    step_count = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.Float)
    calories_burned = db.Column(db.Float)
    date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        age = int(request.form['age'])
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        gender = request.form['gender']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            age=age,
            height=height,
            weight=weight,
            gender=gender,
            activity_level=request.form.get('activity_level') or None
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
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
    
    # Get today's data
    today_meals = Meal.query.filter_by(user_id=current_user.id, date=today).all()
    today_workouts = Workout.query.filter_by(user_id=current_user.id, date=today).all()
    today_steps = Steps.query.filter_by(user_id=current_user.id, date=today).first()
    today_sleep = Sleep.query.filter_by(user_id=current_user.id, date=today).first()
    
    total_calories_consumed = sum(meal.total_calories for meal in today_meals)
    total_calories_burned = sum(workout.calories_burned for workout in today_workouts)
    net_calories = total_calories_consumed - total_calories_burned
    
    return render_template('dashboard.html', 
                         total_calories_consumed=total_calories_consumed,
                         total_calories_burned=total_calories_burned,
                         net_calories=net_calories,
                         today_meals=today_meals,
                         today_workouts=today_workouts,
                         today_steps=today_steps,
                         today_sleep=today_sleep)

@app.route('/meals')
@login_required
def meals():
    # Show all foods (all are vegetarian now)
    foods = Food.query.all()
    user_meals = Meal.query.filter_by(user_id=current_user.id).order_by(Meal.date.desc()).limit(10).all()
    return render_template('meals.html', foods=foods, user_meals=user_meals)

@app.route('/add_meal', methods=['POST'])
@login_required
def add_meal():
    meal = Meal(
        user_id=current_user.id,
        meal_type=request.form['meal_type']
    )
    db.session.add(meal)
    db.session.flush()
    
    total_calories = 0
    food_ids = request.form.getlist('food_id')
    quantities = request.form.getlist('quantity')
    
    for food_id, quantity in zip(food_ids, quantities):
        if food_id and quantity:
            food = Food.query.get(food_id)
            calories = (food.calories_per_100g * float(quantity)) / 100
            total_calories += calories
            
            meal_item = MealItem(
                meal_id=meal.id,
                food_id=food_id,
                quantity=float(quantity),
                calories=calories
            )
            db.session.add(meal_item)
    
    meal.total_calories = total_calories
    db.session.commit()
    flash('Meal added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/workouts')
@login_required
def workouts():
    user_workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).limit(10).all()
    return render_template('workouts.html', workouts=user_workouts)

@app.route('/add_workout', methods=['POST'])
@login_required
def add_workout():
    workout = Workout(
        user_id=current_user.id,
        exercise_name=request.form['exercise_name'],
        duration=int(request.form['duration']),
        calories_burned=float(request.form['calories_burned']),
        intensity=request.form['intensity']
    )
    db.session.add(workout)
    db.session.commit()
    flash('Workout added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/sleep')
@login_required
def sleep():
    user_sleep = Sleep.query.filter_by(user_id=current_user.id).order_by(Sleep.date.desc()).limit(10).all()
    return render_template('sleep.html', sleep_records=user_sleep)

@app.route('/add_sleep', methods=['POST'])
@login_required
def add_sleep():
    sleep_time = datetime.strptime(request.form['sleep_time'], '%H:%M').time()
    wake_time = datetime.strptime(request.form['wake_time'], '%H:%M').time()
    
    # Calculate duration
    sleep_dt = datetime.combine(date.today(), sleep_time)
    wake_dt = datetime.combine(date.today(), wake_time)
    if wake_dt < sleep_dt:
        wake_dt += timedelta(days=1)
    duration = (wake_dt - sleep_dt).total_seconds() / 3600
    
    sleep_record = Sleep(
        user_id=current_user.id,
        sleep_time=sleep_time,
        wake_time=wake_time,
        duration=duration,
        quality=request.form['quality']
    )
    db.session.add(sleep_record)
    db.session.commit()
    flash('Sleep record added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/body_stats')
@login_required
def body_stats():
    stats = BodyStats.query.filter_by(user_id=current_user.id).order_by(BodyStats.date.desc()).limit(10).all()
    return render_template('body_stats.html', stats=stats)

@app.route('/add_body_stats', methods=['POST'])
@login_required
def add_body_stats():
    weight = float(request.form['weight'])
    height = float(request.form['height']) if request.form['height'] else None
    bmi = (weight / ((height/100) ** 2)) if height else None
    
    stats = BodyStats(
        user_id=current_user.id,
        weight=weight,
        height=height,
        body_fat=float(request.form['body_fat']) if request.form['body_fat'] else None,
        muscle_mass=float(request.form['muscle_mass']) if request.form['muscle_mass'] else None,
        bmi=bmi
    )
    db.session.add(stats)
    db.session.commit()
    flash('Body stats updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/steps')
@login_required
def steps():
    user_steps = Steps.query.filter_by(user_id=current_user.id).order_by(Steps.date.desc()).limit(10).all()
    return render_template('steps.html', steps_records=user_steps)

@app.route('/add_steps', methods=['POST'])
@login_required
def add_steps():
    steps_record = Steps(
        user_id=current_user.id,
        step_count=int(request.form['step_count']),
        distance=float(request.form['distance']) if request.form['distance'] else None,
        calories_burned=float(request.form['calories_burned']) if request.form['calories_burned'] else None
    )
    db.session.add(steps_record)
    db.session.commit()
    flash('Steps record added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/dietitian')
@login_required
def dietitian():
    return render_template('dietitian_chat.html')

@app.route('/chat_with_ai', methods=['POST'])
@login_required
def chat_with_ai():
    user_message = request.json.get('message')
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                headers={'Content-Type': 'application/json'},
                json={"contents": [{"parts": [{"text": user_message}]}]},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result:
                    ai_text = result['candidates'][0]['content']['parts'][0]['text']
                    return jsonify({'response': ai_text})
        except:
            pass
    
    return jsonify({'response': 'I am an AI assistant. How can I help you?'})

@app.route('/update_activity_level', methods=['POST'])
@login_required
def update_activity_level():
    activity_level = request.form.get('activity_level') or None
    current_user.activity_level = activity_level
    db.session.commit()
    flash('Activity level updated successfully!')
    return redirect(url_for('dashboard'))



@app.route('/analytics')
@login_required
def analytics():
    week_ago = date.today() - timedelta(days=7)
    
    weekly_meals = db.session.query(Meal.date, db.func.sum(Meal.total_calories)).filter(
        Meal.user_id == current_user.id,
        Meal.date >= week_ago
    ).group_by(Meal.date).all()
    
    weekly_workouts = db.session.query(Workout.date, db.func.sum(Workout.calories_burned)).filter(
        Workout.user_id == current_user.id,
        Workout.date >= week_ago
    ).group_by(Workout.date).all()
    
    weekly_steps = db.session.query(Steps.date, Steps.step_count).filter(
        Steps.user_id == current_user.id,
        Steps.date >= week_ago
    ).all()
    
    return render_template('analytics.html', 
                         weekly_meals=weekly_meals,
                         weekly_workouts=weekly_workouts,
                         weekly_steps=weekly_steps)

def init_sample_data():
    """Initialize sample vegetarian food data"""
    if Food.query.count() == 0:
        foods = [
            Food(name='Rice', calories_per_100g=130, protein=2.7, carbs=28, fat=0.3, category='Grains', is_veg=True),
            Food(name='Paneer', calories_per_100g=265, protein=18.3, carbs=1.2, fat=20.8, category='Dairy', is_veg=True),
            Food(name='Broccoli', calories_per_100g=34, protein=2.8, carbs=7, fat=0.4, category='Vegetables', is_veg=True),
            Food(name='Banana', calories_per_100g=89, protein=1.1, carbs=23, fat=0.3, category='Fruits', is_veg=True),
            Food(name='Oats', calories_per_100g=389, protein=16.9, carbs=66, fat=6.9, category='Grains', is_veg=True),
            Food(name='Spinach', calories_per_100g=23, protein=2.9, carbs=3.6, fat=0.4, category='Vegetables', is_veg=True),
            Food(name='Lentils (Dal)', calories_per_100g=116, protein=9, carbs=20, fat=0.4, category='Legumes', is_veg=True),
            Food(name='Almonds', calories_per_100g=579, protein=21.2, carbs=21.6, fat=49.9, category='Nuts', is_veg=True),
            Food(name='Greek Yogurt', calories_per_100g=59, protein=10, carbs=3.6, fat=0.4, category='Dairy', is_veg=True),
            Food(name='Quinoa', calories_per_100g=368, protein=14.1, carbs=64.2, fat=6.1, category='Grains', is_veg=True),
            Food(name='Sweet Potato', calories_per_100g=86, protein=1.6, carbs=20.1, fat=0.1, category='Vegetables', is_veg=True),
            Food(name='Chickpeas', calories_per_100g=164, protein=8.9, carbs=27.4, fat=2.6, category='Legumes', is_veg=True)
        ]
        for food in foods:
            db.session.add(food)
        
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)