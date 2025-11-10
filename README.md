# LifeSync - Health Tracker Web Application

A comprehensive health tracking web application built with Flask and MySQL that helps users monitor their daily activities, meals, exercise routines, and body metrics to achieve their health goals.

## Features

- **User Authentication**: Secure registration and login system
- **Meal Tracking**: Log meals with detailed nutrition information
- **Workout Logging**: Track various workout types with duration and calories burned
- **Sleep Tracking**: Monitor sleep hours and quality
- **Body Metrics**: Track weight, BMI, body fat, and muscle mass
- **Analytics Dashboard**: Visual charts showing weekly trends

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Charts**: Chart.js
- **Authentication**: Flask-Login

## Installation

1. **Clone the repository**
   ```bash
   cd "c:\Users\Administrator\Desktop\TPBL Project"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup MySQL Database**
   - Install MySQL Server
   - Update database credentials in `app.py` and `setup_database.py`
   - Run the database setup script:
   ```bash
   python setup_database.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Database Configuration

Update the following line in `app.py` with your MySQL credentials:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/lifesync_db'
```

Also update the credentials in `setup_database.py` if different from the default (root/root).

## Usage

1. **Register**: Create a new account with your basic information
2. **Dashboard**: View daily calorie summary and recent activities
3. **Add Meals**: Log your food intake with nutrition information
4. **Add Workouts**: Record exercises and calories burned
5. **Sleep Tracking**: Log sleep hours and quality
6. **Body Metrics**: Track weight and body composition changes
7. **Analytics**: View weekly trends and calorie balance charts

## Project Structure

```
TPBL Project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup_database.py      # Database setup script
├── README.md             # Project documentation
└── app/
    └── templates/        # HTML templates
        ├── base.html
        ├── index.html
        ├── register.html
        ├── login.html
        ├── dashboard.html
        ├── add_meal.html
        ├── add_activity.html
        ├── body_metrics.html
        └── analytics.html
```

## Key Features Explained

### Health Tracking
- Log meals with detailed nutrition information (calories, protein, carbs, fats)
- Track various workout types with duration and calories burned
- Monitor sleep patterns and quality
- Record body metrics including weight, BMI, body fat, and muscle mass

### Progress Monitoring
- Visual charts showing weekly calorie intake and burn trends
- Calorie balance tracking
- Body metric tracking over time

### User Experience
- Responsive design for mobile and desktop
- Intuitive navigation and clean interface
- Real-time feedback and notifications