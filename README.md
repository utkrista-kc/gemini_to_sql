# Leveraging Google Gemini: Querying Database with Natural Language

This project demonstrates the use of **Google Gemini** for generating SQL queries to query database using natural language. There are two implementations:

1. **Generating SQL queries using prompts**: This implementation uses the **Billionaires dataset** from Kaggle.
2. **Generating SQL queries using Gemini Function Calling**: This is a modification of the [SQL Talk app](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/function-calling/sql-talk-app) for querying **SQLite** using the **Chinook dataset**.

## Requirements

- Google Cloud Account and Project
- Gemini API Key
- Vertex AI API enabled on your Google Cloud project
- Set Environment Variables:`GOOGLE_GEMINI_API_KEY`, `GOOGLE_PROJECT_ID`

The following Python packages are required:

- `streamlit`
- `google-generativeai`
- `python-dotenv`
- `vertexai`

## Project Overview

- **Billionaires Dataset**: It consists of a single table with information of billionaires. [Dataset Link](https://www.kaggle.com/datasets/nelgiriyewithana/billionaires-statistics-dataset)
- **Chinook Dataset**: Leverages Google Gemini’s **function calling** to interact with complex SQL databases. It has many tables and relationships exist between these tables. [Dataset Link](https://github.com/lerocha/chinook-database/blob/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql)

For more information on Gemini Function Calling, visit the [documentation](https://ai.google.dev/gemini-api/docs/function-calling).

### References

- [SQL Talk App](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/function-calling/sql-talk-app/app.py)
  
- [Google Function Calling Example](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/function-calling/function_calling_data_structures.ipynb)

## Running the Project

1. Create a Python environment:
   
```
   conda create -p venv python==3.10 -y
   conda activate venv/
   ```

2. Install dependencies:
   ```pip install -r requirements.txt```



3. Inserting Billionaires Data into SQLite:
   ```python sqlite.py```
4. Running the Streamlit App (Billionaires Data):
Start the Streamlit app to interact with the Billionaires dataset:

    ```streamlit run main.py```
5. Inserting Chinook Data into SQLite:
Insert the Chinook dataset into the SQLite database:
    ```python chinook_sqlite.py```
6. Running the Streamlit App (Chinook Data with Google Gemini):
Interact with the Chinook dataset using Google Gemini's function calling:
    ```streamlit run function_calling.py``` 

**Note**: You need to authenticate with Google Cloud and ensure default-login is set up. Also, enable the Vertex AI API in your Google Cloud project to interact with Chinook database using Function calling.
