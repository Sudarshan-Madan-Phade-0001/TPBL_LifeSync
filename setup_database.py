import mysql.connector
from mysql.connector import Error

def setup_database():
    """Setup the LifeSync database with the new schema"""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Execute the SQL schema
            sql_commands = """
-- Drop old database (if exists) and create a new one
DROP DATABASE IF EXISTS lifesync_db;
CREATE DATABASE lifesync_db;
USE lifesync_db;

-- Table: user
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    gender VARCHAR(10),
    age INT,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    created_date DATE DEFAULT (CURRENT_DATE),
    created_time TIME DEFAULT (CURRENT_TIME)
);

-- Table: workout
CREATE TABLE workout (
    user_id INT,
    date DATE DEFAULT (CURRENT_DATE),
    time TIME DEFAULT (CURRENT_TIME),
    workout_type VARCHAR(100),
    duration_minutes INT,
    calories_burned DECIMAL(6,2),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Table: meal
CREATE TABLE meal (
    user_id INT,
    date DATE DEFAULT (CURRENT_DATE),
    time TIME DEFAULT (CURRENT_TIME),
    meal_type VARCHAR(50),
    food_items TEXT,
    calories DECIMAL(6,2),
    protein_g DECIMAL(5,2),
    carbs_g DECIMAL(5,2),
    fats_g DECIMAL(5,2),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Table: sleep
CREATE TABLE sleep (
    user_id INT,
    date DATE DEFAULT (CURRENT_DATE),
    time TIME DEFAULT (CURRENT_TIME),
    sleep_hours DECIMAL(4,2),
    sleep_quality VARCHAR(50),
    bedtime TIME,
    wakeup_time TIME,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Table: body_stats
CREATE TABLE body_stats (
    user_id INT,
    date DATE DEFAULT (CURRENT_DATE),
    time TIME DEFAULT (CURRENT_TIME),
    weight_kg DECIMAL(5,2),
    bmi DECIMAL(4,2),
    body_fat_percent DECIMAL(5,2),
    muscle_mass_kg DECIMAL(5,2),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);
"""
            
            # Execute each command
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command)
            
            connection.commit()
            print("Database setup completed successfully!")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database()