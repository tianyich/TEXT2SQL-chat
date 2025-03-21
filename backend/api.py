from fastapi import FastAPI, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
from pydantic import BaseModel
from contextlib import asynccontextmanager
from tabulate import tabulate


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
URL = "https://api.deepseek.com"

schema = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_schema
    db_schema = get_db_schema()
    print("Database schema loaded during lifespan startup.")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


def ask(question: str, hint: str) -> str:
    client = OpenAI(api_key=API_KEY, base_url=URL)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": hint},
            {"role": "user", "content": question},
        ],
        stream=False,
    )
    content = response.choices[0].message.content
    return "" if content is None else content


def get_db_schema():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    tables = cursor.fetchall()

    schema = ""
    for table in tables:
        table_name = table[0]
        schema += f"\nTable: {table_name}\nColumns:\n"

        cursor.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s;
        """,
            (table_name,),
        )
        columns = cursor.fetchall()

        for column in columns:
            schema += f"  - {column[0]}: {column[1]}\n"

    cursor.close()
    conn.close()
    return schema


def execute_query(query: str) -> str:
    # DANGEROUS_KEYWORD =  ["drop", "alter", "create"]

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    if cursor.description is not None:
        colnames = [desc[0] for desc in cursor.description]
    else:
        colnames = ""
    formatted_result = [dict(zip(colnames, row)) for row in result]

    cursor.close()
    conn.close()
    table_string = tabulate(formatted_result, headers="keys", tablefmt="html")
    return table_string


@app.post("/ask")
def ask_query(request: AskRequest):
    question = request.question
    schema = get_db_schema()
    HINT = f"""
    You are a SQL assistant. You can generate a SQL statement that is compliant with PostgreSQL syntax based on the user's input question and the table structure of the database. Please ensure that the logic of the SQL you generate is consistent with the table structure information and the user's question.
    1. You have the access to this schema {schema}
    2. If you can generate a SQL statement that meets the user's question requirements, directly return the SQL text that is compliant with the requirements and can be executed directly.
    3. If you cannot generate a SQL statement that meets the user's question requirements, do not generate a SQL statement, but give a prompt to the user to re-modify the question.
    4. If the user's question exceeds your ability to handle, please directly answer '无法处理' with the language of the user's question.
    5. Output only contain SQL code, pure SQL code with no comment or '无法处理' if you cannot write the corresponding SQL code. Try best to give a SQL code answer, use less '无法处理'
    6. Output with no quote around
    """
    try:
        query = ask(question, HINT)
        if query is None or "无法处理" in query:
            return query
        result = execute_query(query)
        return f"<p>{query}</p> <br> {result}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
