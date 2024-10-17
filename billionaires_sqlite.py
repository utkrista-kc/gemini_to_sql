import sqlite3
import pandas as pd

# Load data from CSV files
billionaires_csv_file = "cleaned_billionaires_data.csv"

# Load data into DataFrames
df_billionaires = pd.read_csv(billionaires_csv_file)


# Set the database name
database = "data.db"

# Select only the columns that match your SQLite table for billionaires
columns_to_insert_billionaires = [
    "rank",
    "category",
    "person_name",
    "country",
    "city",
    "source",
    "industries",
    "country_of_citizenship",
    "organization",
    "self_made",
    "status",
    "gender",
    "title",
    "birth_year",
]

filtered_df_billionaires = df_billionaires[columns_to_insert_billionaires]

# Connect to SQLite
connection = sqlite3.connect(database)

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Create the BILLIONAIRES_DATA table if it doesn't exist already
table_info_billionaires = """
CREATE TABLE IF NOT EXISTS BILLIONAIRES_DATA (
    rank INTEGER,
    category VARCHAR(100),
    person_name VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    source VARCHAR(100),
    industries VARCHAR(100),
    country_of_citizenship VARCHAR(100),
    organization VARCHAR(100),
    self_made BOOLEAN,
    status VARCHAR(50),
    gender VARCHAR(10),
    title VARCHAR(100),
    birth_year INTEGER
);
"""
cursor.execute(table_info_billionaires)


# Insert data into BILLIONAIRES_DATA table
for _, row in filtered_df_billionaires.iterrows():
    cursor.execute(
        """
    INSERT INTO BILLIONAIRES_DATA (
        rank, category, person_name, country, city, source, industries,
        country_of_citizenship, organization, self_made, status, gender,
     title, birth_year
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
        tuple(row),
    )


# Display the first 5 records inserted from BILLIONAIRES_DATA
data_billionaires = cursor.execute("""SELECT * FROM BILLIONAIRES_DATA LIMIT 5""")
print("\nThe first 5 inserted records from BILLIONAIRES_DATA are:")
for row in data_billionaires:
    print(row)


# Count the total number of records inserted into BILLIONAIRES_DATA
cursor.execute("""SELECT COUNT(*) FROM BILLIONAIRES_DATA""")
total_records_billionaires = cursor.fetchone()[0]
print(
    f"Total number of records inserted into BILLIONAIRES_DATA table: {total_records_billionaires}"
)


# Commit your changes to the database and close the connection
connection.commit()
connection.close()
