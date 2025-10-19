# LifeSync - Health Tracker Web Application

A comprehensive health tracking web application built with Flask and MySQL that helps users monitor their daily activities, meals, exercise routines, and body metrics to achieve their health goals.

## Features

- **User Authentication**: Secure registration and login system
- **Meal Tracking**: Log meals with calorie information
- **Exercise Logging**: Track workouts and calories burned
- **Body Metrics**: Monitor weight, body fat, and muscle mass
- **Analytics Dashboard**: Visual charts and health insights
- **Personalized Recommendations**: Data-driven health tips

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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/health_tracker'
```

## Usage

1. **Register**: Create a new account with your basic information
2. **Dashboard**: View daily calorie summary and recent activities
3. **Add Meals**: Log your food intake with calorie information
4. **Add Activities**: Record exercises and calories burned
5. **Body Metrics**: Track weight and body composition changes
6. **Analytics**: View weekly trends and get personalized recommendations

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

### Calorie Tracking
- Log meals with detailed calorie information
- Track exercise activities and calories burned
- Calculate net calorie balance

### Progress Monitoring
- Visual charts showing weekly trends
- Body metric tracking over time
- Personalized health recommendations

### User Experience
- Responsive design for mobile and desktop
- Intuitive navigation and clean interface
- Real-time feedback and notifications