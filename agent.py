import os
import asyncio
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity.aio import AzureCliCredential
from agent_framework.azure import AzureAIAgentClient
from dotenv import load_dotenv
import pyodbc
from typing import Annotated
from pydantic import Field
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

load_dotenv()
SERVER = os.getenv("DB_SERVER_ENDPOINT")  # Public endpoint & port
DATABASE = os.getenv("DB_NAME")
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD") 

conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

def list_tables() -> list[str]:
    """
    List all tables in the database
    """
    SERVER = "penn-sql-mi.public.5d1770b5a04a.database.windows.net,3342"  # Public endpoint & port
    DATABASE = "db1"
    USERNAME = "sqladmin"
    PASSWORD = "fvx!msz1Uz*TJ3&$" 

    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            print("✅ Connected successfully!\n")

            # Query all user tables
            cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")
            tables = cursor.fetchall()

            #print("📋 Tables in database:")
            tables_list = []
            for schema, name in tables:
                #print(f"  {schema}.{name}")
                tables_list.append(f"{schema}.{name}")
            return tables_list

    except Exception as e:
        print("❌ Connection failed:")
        print(e)

def query_table():
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            print("✅ Connected successfully!\n")

            query = "SELECT TOP 100 * FROM [dbo].[CasinoMetrics];"
            cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            # Convert each row to a dict of strings
            result = []
            for row in rows:
                record = {}
                for col, val in zip(columns, row):
                    # Force everything to a string (dates, decimals, etc.)
                    record[col] = str(val)
                result.append(record)

            # Truncate safely
            if len(result) > 20:
                truncated = result[:20]
                return {
                    "rows": truncated,
                    "note": f"Truncated: showing 20 of {len(result)} rows."
                }

            return {"rows": result}

    except Exception as e:
        print("❌ Connection failed:")
        print(e)

async def main():
    instructions = """
    You are a helpful database admin meant to answer questions about items in a database. 
    Use the tools available to query the necessary info and then answer the questions.
    Don't ask any follow up questions, just answer the original question asked.
    """
    
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions=instructions,
            tools=[list_tables, query_table]
        ) as agent,
    ):
        print("**********Should call the list_tables tool*****")
        result = await agent.run("List the tables in the database.")
        print(f"Listed tables: {result.text}")
        print("***********************************************")

        print("Should call the query_table tool")
        db_result = await agent.run("Query the CasinoMetrics table.")
        print(f"Db contents successfully queried, not printing to save space.")
        print("****************************************")
        
        print("RAG Section:")
        question_1 = await agent.run(f"What are the contents of this databases' data?: {db_result.text}")
        print(f"Question 1: {question_1.text}")
        print("****************************************")
    
if __name__ == "__main__":
    asyncio.run(main())