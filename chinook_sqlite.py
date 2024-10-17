import sqlite3

# Path to the SQL file
sql_file_path = "Chinook_Sqlite.sql"

# Path to the SQLite database file you want to create (or connect to if it already exists)
db_file = "music_store.db"

# Connect to SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()


# Function to read the SQL file and execute the queries
def execute_sql_from_file(file_path):
    with open(file_path, "r") as file:
        sql_script = file.read()

    try:
        # Execute the SQL script
        cursor.executescript(sql_script)
        print(f"Successfully executed SQL script from {file_path}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


# Execute the SQL queries from the file
execute_sql_from_file(sql_file_path)

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database {db_file} created and populated.")
