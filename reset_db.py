import pymysql

# Connect to MySQL and drop/recreate database
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root'
    )
    
    with connection.cursor() as cursor:
        cursor.execute("DROP DATABASE IF EXISTS lifesync_db")
        cursor.execute("CREATE DATABASE lifesync_db")
        print("Database reset successfully!")
        
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")