import sqlite3

# Set the database name
database = "data.db"

# Connect to SQLite
connection = sqlite3.connect(database)

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Define multiple SQL queries for the demo
queries = [
    {
        "description": "Give me the information about the top 5 billionaires:",
        "query": """
        SELECT *
        FROM BILLIONAIRES_DATA
        ORDER BY rank
        LIMIT 5;
        """,
    },
    {
        "description": "Tell me the top 10 billionaires from Australia:",
        "query": """
        SELECT person_name, rank, organization, industries
        FROM BILLIONAIRES_DATA
        WHERE country = 'Australia'
        ORDER BY rank
        LIMIT 10;
        """,
    },
    {
        "description": "List billionaires under the age of 30:",
        "query": """
        SELECT person_name, birth_year, country, industries
        FROM BILLIONAIRES_DATA
        WHERE 2023 - birth_year < 30;
        """,
    },
    {
        "description": "What is the ratio of male to female billionaires:",
        "query": """
     SELECT 
            SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) * 1.0 / 
            NULLIF(SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END), 0) AS male_to_female_ratio
        FROM BILLIONAIRES_DATA;

        """,
    },
    {
        "description": "Compare self-made billionaires and with not self-made:",
        "query": """
       SELECT 
        CASE 
            WHEN self_made = 1 THEN 'Self-Made' 
            WHEN self_made = 0 THEN 'Not Self-Made' 
            ELSE 'Unknown' 
        END AS wealth_type,
        COUNT(*) AS total_billionaires
    FROM BILLIONAIRES_DATA
    GROUP BY wealth_type;


        """,
    },
    {
        "description": "Show how many billionaires each industry has:",
        "query": """
        SELECT industries, COUNT(*) AS total_billionaires
        FROM BILLIONAIRES_DATA
        GROUP BY industries
        ORDER BY total_billionaires DESC;
        """,
    },
    {
        "description": "Which countries have the most billionaires, sorted by count?",
        "query": """
        SELECT country, COUNT(*) AS total_billionaires
        FROM BILLIONAIRES_DATA
        GROUP BY country
        ORDER BY total_billionaires DESC;
        """,
    },
    {
        "description": "Which industries have the most billionaires?",
        "query": """
        SELECT industries, COUNT(*) AS total_billionaires
        FROM BILLIONAIRES_DATA
        GROUP BY industries
        ORDER BY total_billionaires DESC
        LIMIT 1;
        """,
    },
]

# Interactive menu to execute one query at a time
while True:
    # Display the available queries to the user
    print("\nAvailable Queries:")
    for i, q in enumerate(queries):
        print(f"{i + 1}. {q['description']}")

    # Ask the user to select a query to execute
    try:
        choice = int(
            input("\nEnter the number of the query you want to execute (0 to exit): ")
        )
        if choice == 0:
            break
        elif 1 <= choice <= len(queries):
            selected_query = queries[choice - 1]
            print(f"\nExecuting: {selected_query['description']}")

            # Execute the selected query
            data = cursor.execute(selected_query["query"])
            rows = data.fetchall()

            # Display the results
            for row in rows:
                print(row)
            print(f"Total rows: {len(rows)}")
        else:
            print("Invalid choice. Please enter a number between 0 and", len(queries))
    except ValueError:
        print("Invalid input. Please enter a valid number.")

# Close the database connection
connection.close()
