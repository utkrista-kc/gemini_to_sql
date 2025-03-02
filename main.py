from dotenv import load_dotenv
import pandas as pd

load_dotenv()  ## load all the environment variables

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

## Configure genai key
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

# Set the database name
database = "data.db"

# Set model name
model_name = "gemini-2.0-flash"


## Function to load google gemini model (responsible for giving the query as response)
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt[0], question])
        return response.text
    except Exception as e:
        st.error(f"Error generating SQL query: {e}")
        return None


## Function to retrieve query from the database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None


# Function to interpret data using Gemini
def interpret_data_with_gemini(data, query):
    try:
        data_str = "\n".join([str(row) for row in data])
        # Construct a new prompt specifically for interpreting the data
        if len(data) == 1 and len(data[0]) == 1:
            # Handle single-value results separately
            interpretation_prompt = f"""
            You are an expert data analyst. Given the result of the following query:

            Result:
            {data_str}

            Please explain what this result means in simple terms. Add any useful recommendations based on the query's context. 
            Provide actionable insights if applicable.
            Avoid using complex formatting..

            """
        else:
            # Handle larger result sets normally
            interpretation_prompt = f"""
            You are an expert data analyst. Given the following data, provide a detailed summary of the key insights:

            Data:
            {data_str}

            Please describe the key observations, trends, and provide any interesting insights that could help the user to better understand the data.
            Use simple formatting and avoid unnecessary italics or fancy visual representations. 
            """

            #
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([query, interpretation_prompt])
        return response.text
    except Exception as e:
        print("e", e)
        st.error(f"Error interpreting the data: {e}")
        return None


## Define your prompt to generate SQL
prompt = [
    """
You are an expert in converting English questions to SQL queries!
The database has the following table:

 The table `BILLIONAIRES_DATA` contains information about billionaires and has the following columns:
- rank (INTEGER)- The ranking of the billionaire in terms of wealth. e.g. 1
- category (VARCHAR) - The category or industry in which the billionaire's business operates. e.g. "Technology"
- person_name (VARCHAR) - The full name of the billionaire.e.g. "Elon Musk"
- country (VARCHAR) -  The country in which the billionaire resides. e.g. "United States"
- city (VARCHAR) - The city in which the billionaire resides. e.g. "Austin"
- source (VARCHAR) - The source of the billionaire's wealth. e.g. "Tesla, SpaceX"
- industries (VARCHAR) - The industries associated with the billionaire's business interests. e.g. "Automotive"
- country_of_citizenship (VARCHAR) - The country of citizenship of the billionaire. e.g. "United States"
- organization (VARCHAR) - The name of the organization or company associated with the billionaire. e.g. "Tesla"
- self_made (BOOLEAN)- Indicates whether the billionaire is self-made (True/False). e.g. True
- status (VARCHAR) -  "D" represents self-made billionaires (Founders/Entrepreneurs) and "U" indicates inherited or unearned wealth. e.g. "U" or "D" 
- gender (VARCHAR) - The gender of the billionaire. e.g. "M" (Male)
- title (VARCHAR) - The title or honorific of the billionaire. e.g. "CEO"
- birth_year (INTEGER) - The birth year of the billionaire. e.g. 1971

Important Notes:
1. The billionaires data is from the year 2023.

For example:

Example 1 - What is the total number of billionaires from the United States? The SQL command will be:
SELECT COUNT(*) FROM BILLIONAIRES_DATA WHERE country = "United States";

Example 2 - Find the number of billionaires in each industry. The SQL command will be:
SELECT industries, COUNT(*) AS num_billionaires FROM BILLIONAIRES_DATA GROUP BY industries;

Example 3 - How many billionaires have inherited their wealth? The SQL command will be:
SELECT COUNT(*) FROM BILLIONAIRES_DATA WHERE status = "U";

Example 4 - List the top 5 billionaires along with their organization and title. The SQL command will be:
SELECT * FROM BILLIONAIRES_DATA ORDER BY rank LIMIT 5;

Note: 
1. The SQL command should be presented without backticks (```), Markdown formatting, or the word 'sql' at the beginning or end.
2. The query should only include valid SQL syntax.
3. Always use double quotes for string values if necessary.
4. Do not provide the SQL command with starting with ```sql

"""
]


## Streamlit App
st.set_page_config(page_title="Gemini to SQL Query Generator", layout="centered")
st.header("Query SQL database with Google Gemini")

question = st.text_input("Enter your question: ", key="input")

submitButtonClick = st.button("Retrieve Response")

# Placeholder for info or error messages
message_placeholder = st.empty()

# if Submit Button is clicked
if submitButtonClick:
    # If no question is provided, show a warning and skip the rest
    if not question.strip():
        message_placeholder.warning(
            "Please enter a valid question to generate a query."
        )
    else:
        # Get the SQL query from Gemini response
        sql_query = get_gemini_response(question, prompt)

        if sql_query:
            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")

            # Execute the SQL query and retrieve data
            rows = read_sql_query(sql_query, database)

            if rows:
                # Display the result as a DataFrame for better presentation
                st.subheader("Query Result")
                try:
                    # Convert rows to a DataFrame for easy visualization
                    conn = sqlite3.connect(database)
                    cur = conn.cursor()
                    cur.execute(sql_query)
                    columns = [desc[0] for desc in cur.description]
                    conn.close()
                    df = pd.DataFrame(rows, columns=columns)

                    st.dataframe(df)  # Display DataFrame in a nice UI
                except Exception as e:
                    st.error(f"Error displaying data: {e}")

                # Use Gemini to interpret the retrieved data
                interpretation = interpret_data_with_gemini(rows, question)
                if interpretation:
                    st.subheader("Gemini's Interpretation of the Data")
                    st.write(interpretation)

            else:
                message_placeholder.info("No results found for the given query.")
        else:
            message_placeholder.error(
                "Failed to generate a valid SQL query. Please try again."
            )
