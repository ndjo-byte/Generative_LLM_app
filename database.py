import os
from dotenv import load_dotenv
import pymysql
from urllib.parse import urlparse

# Load environment variables from the .env file
load_dotenv()
parsed_url = urlparse(os.getenv('DATABASE_URL'))

# Check if DATABASE_URL is present
if not parsed_url.netloc:
    raise ValueError("DATABASE_URL environment variable is not set")

# Connection to the MySQL database
db = pymysql.connect(
    host=parsed_url.hostname,
    user=parsed_url.username,
    password=parsed_url.password,
    cursorclass=pymysql.cursors.DictCursor
)
cursor = db.cursor()

# Version check (to confirm we are connected to MySQL)
cursor.execute('SELECT VERSION()')
version = cursor.fetchone()
print(f'MySQL version: {version["VERSION()"]}')  # Printing the version of MySQL

# Function to create database
def create_database(database_name):
    cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {database_name}")
        print(f"Database '{database_name}' created successfully.")
    else:
        print(f"Database '{database_name}' already exists.")

# Function to create table
def create_table(table_name):
    # Properly use f-string to format the table name in SQL query
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    if not cursor.fetchone():
        create_table_sql = f'''
        CREATE TABLE {table_name} (
            id INT NOT NULL auto_increment,
            name VARCHAR(100),
            description TEXT,
            deadline DATE,
            goal_plan TEXT,
            status VARCHAR(50) DEFAULT 'in-progress',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        )
        '''
        cursor.execute(create_table_sql)
        print(f"Table '{table_name}' created successfully.")
    else:
        print(f"Table '{table_name}' already exists.")

# Creating database and table
database_name = parsed_url.path[1:]  # Extract database name (without leading slash)
create_database('goals_db')
cursor.execute('USE goals_db')
create_table('goals')

# Insert goal function for use in MAIN.PY
def insert_goal(name, description, deadline, goal_plan, status='in-progress'):
    try:
        # Using the previously established database connection
        with db.cursor() as cursor:
            insert_query = '''
            INSERT INTO goals (name, description, deadline, goal_plan, status)
            VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (name, description, deadline, goal_plan, status))
            db.commit()  # Commit the transaction
            print(f"Goal '{name}' inserted successfully.")
            primary_id = cursor.lastrowid
            return primary_id
    except Exception as e:
        print(f"Error inserting goal: {e}")
        db.rollback()  # Rollback in case of an error


# Close connection function (to use in MAIN.PY)
def close_connection():
    try:
        db.close()
        print("Database connection closed.")
    except Exception as e:
        print(f"Error closing connection: {e}")
