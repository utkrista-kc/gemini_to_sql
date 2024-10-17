from dotenv import load_dotenv
import os
import vertexai
import sqlite3
import streamlit as st
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool

load_dotenv()  ## load all the environment variables

PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)


# SQLite Database file path
DB_FILE = "music_store.db"


def connect_to_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # To return dict-like rows
    return conn


# Define Function Declarations
list_tables_func = FunctionDeclaration(
    name="list_tables",
    description="List tables in the SQL database that will help answer the user's question",
    parameters={
        "type": "object",
        "properties": {},
    },
)
get_table_func = FunctionDeclaration(
    name="get_table",
    description="Get information about a table, including the description, schema, and number of rows that will help answer the user's question.",
    parameters={
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Name of the table to get information about",
            }
        },
        "required": [
            "table_name",
        ],
    },
)


sql_query_func = FunctionDeclaration(
    name="sql_query",
    description="Execute SQL queries on the database to retrieve information that answers the user's question.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query that will be executed on the database.",
            }
        },
        "required": [
            "query",
        ],
    },
)


# Create a Tool for the model
sql_query_tool = Tool(
    function_declarations=[
        list_tables_func,
        get_table_func,
        sql_query_func,
    ],
)

# Initialize the Gemini model
model = GenerativeModel(
    "gemini-1.5-pro",
    generation_config={"temperature": 0},
    tools=[sql_query_tool],
)

# Streamlit UI setup
st.set_page_config(
    page_title="SQL Talk with SQLite",
    layout="wide",
)

col1, col2 = st.columns([8, 1])
with col1:
    st.title("SQL Talk with SQLite")

st.subheader("Powered by Function Calling in Gemini")


with st.expander("Sample prompts", expanded=True):
    st.write(
        """
        - What kind of information is in this database?
        - How many rows are in the users table?
        - List 5 product categories.
    """
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", r"\$"))
        try:
            with st.expander("Function calls, parameters, and responses"):
                st.markdown(message["backend_details"])
        except KeyError:
            pass

if prompt := st.chat_input("Ask me about information in the database..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        chat = model.start_chat()

        conn = connect_to_db()

        prompt += """
            Please give a concise, high-level summary followed by detail in
            plain language about where the information in your response is
            coming from in the database. Only use information that you learn
            from SQLite, do not make up information. The table name or field name can be any case sent as input. You have to analyse based on table information
            """

        try:
            response = chat.send_message(prompt)
            response = response.candidates[0].content.parts[0]

            api_requests_and_responses = []
            backend_details = ""

            function_calling_in_process = True
            while function_calling_in_process:
                try:
                    params = {}
                    for key, value in response.function_call.args.items():
                        params[key] = value

                    if response.function_call.name == "list_tables":
                        cursor = conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table';"
                        )
                        api_response = [row["name"] for row in cursor.fetchall()]
                        st.write("List of Tables:")
                        st.dataframe(api_response)  # Display table names
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )

                    elif response.function_call.name == "get_table":
                        cursor = conn.execute(
                            f"PRAGMA table_info({params['table_name']});"
                        )
                        api_response = [dict(row) for row in cursor.fetchall()]
                        st.write(
                            f"Schema information for table {params['table_name']}:"
                        )
                        st.dataframe(api_response)  # Display schema
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )

                    elif response.function_call.name == "sql_query":
                        cursor = conn.execute(params["query"])
                        api_response = [dict(row) for row in cursor.fetchall()]
                        st.write(f"Query Results for: {params['query']}")
                        st.dataframe(api_response)  # Display query results
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )

                    backend_details += "- Function call:\n"
                    backend_details += (
                        "   - Function name: ```"
                        + str(api_requests_and_responses[-1][0])
                        + "```"
                    )
                    backend_details += "\n\n"
                    backend_details += (
                        "   - Function parameters: ```"
                        + str(api_requests_and_responses[-1][1])
                        + "```"
                    )
                    backend_details += "\n\n"
                    backend_details += (
                        "   - API response: ```"
                        + str(api_requests_and_responses[-1][2])
                        + "```"
                    )
                    backend_details += "\n\n"
                    with message_placeholder.container():
                        st.markdown(backend_details)

                    response = chat.send_message(
                        Part.from_function_response(
                            name=response.function_call.name,
                            response={
                                "content": api_response,
                            },
                        ),
                    )
                    response = response.candidates[0].content.parts[0]

                except AttributeError:
                    function_calling_in_process = False

            full_response = response.text
            with message_placeholder.container():
                st.markdown(full_response.replace("$", r"\$"))  # noqa: W605
                with st.expander("Function calls, parameters, and responses:"):
                    st.markdown(backend_details)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "backend_details": backend_details,
                }
            )
        except Exception as e:
            print(e)
            error_message = f"""
                Something went wrong! We encountered an unexpected error while
                trying to process your request. Please try rephrasing your
                question. Details:

                {str(e)}"""
            st.error(error_message)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )
