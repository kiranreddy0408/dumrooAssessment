from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import PromptTemplate
from sqlalchemy import text
from pydantic import BaseModel, Field
from db import SessionLocal
from db import engine
from models import Queries, Admin 

import pandas as pd
import uuid
import os

# Setup
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
# model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)  # Uncomment for using OpenAI
db = SQLDatabase(engine)
schema = db.get_table_info(table_names=["students","submissions","quizzes","quiz_scores"])


# Pydantic output structures
class QueryAndCode(BaseModel):
    query: str = Field(..., description="A valid SQL query only.")
    python_code: str = Field(..., description="Python plotting code using Plotly. Save plot as HTML using plotly.offline.plot or equivalent.")

class TitleAndInsights(BaseModel):
    title: str = Field(..., description="A suitable title based on the question")
    insights: str = Field(..., description="Generate insights or summarize the result against the question given")

structured_model = model.with_structured_output(QueryAndCode)
insights_structure = model.with_structured_output(TitleAndInsights)


# Save Plot
def save_figure(fig):
    static_dir = r"c:\Users\kiran\Desktop\dumroo_ai_admin\backend\static"
    os.makedirs(static_dir, exist_ok=True)
    filename = f"plot_{uuid.uuid4().hex[:8]}.html"
    path = os.path.join(static_dir, filename)
    fig.write_html(path, include_plotlyjs="cdn", full_html=True)
    return f"/{filename}"


# Step 1: Get Admin Scope
def get_admin_scope(admin_id: int):
    session = SessionLocal()
    admin = session.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise ValueError("Admin not found")

    return {
        "grade": admin.grade_scope,
        "class": admin.class_scope,
        "region": admin.region_scope
    }

# Step 2: Validate Question Scope
def validate_question_scope(question: str, scope: dict):
    prompt = PromptTemplate(
        template="""
        You are an expert at access control.
        The following user question must be restricted to only the given scope:
        - grade = '{grade}'
        - class = '{class_}'
        - region = '{region}'

        If the question asks for data outside this scope, or does not respect these restrictions, respond with "ERROR: Question violates scope".
        Otherwise, respond with "OK".

        Scope:
        grade: {grade}
        class: {class_}
        region: {region}

        Question:
        {question}
        """,
        input_variables=["grade", "class_", "region", "question"]
    )
    chain = prompt | model
    result = chain.invoke({
        "grade": scope["grade"],
        "class_": scope["class"],
        "region": scope["region"],
        "question": question
    })
    if "ERROR" in result.content:
        
        raise RuntimeError("You do not have access to the mentioned class, grade, or region. Please recheck your query/question.")


# Step 3: Generate SQL and Plotting Code
def generate_sql_and_plot_code(question: str, scope: dict):
    scope_filter = f"""
    Important: You must restrict the SQL query to return results only where(every query must respect the following scope):
    - grade = '{scope['grade']}'
    - class_name = '{scope['class']}'
    - region = '{scope['region']}'
    """
    
    prompt = PromptTemplate(
        template=f"""
        You are provided with the following PostgreSQL database schema:
        {{schema}}

       

        Your task is to:
        1. Write a valid SQL query (PostgreSQL-compliant) that accurately answers the user's question.
        2. Generate Python code using Plotly to visualize(Pie, Line, Bar, etc which ever best suits the data) the query results.

        Requirements:
           {scope_filter}
        ❗ Only join students if the question requires student-level output (e.g., performance, attendance).    
            For admin questions like "List upcoming quizzes", directly query the quizzes table without joining students
        - The SQL query must be syntactically correct and fully compatible with PostgreSQL.
        -Avoid escaping quotes. Use standard SQL string syntax: 'value' not \\'value\\'.
        - Do NOT use SQLite-specific functions like `strftime`.
        - Use PostgreSQL functions such as `EXTRACT`, `DATE_PART`, etc., for time-based logic.
        - The result of the SQL query will be loaded into a Pandas DataFrame named `df`.
        - Your plotting code must reference only the columns returned by the SQL query. also handle cases where there are 2 more resluts for single student.
        - Assign the final plot to a variable named `fig`.
        - Do NOT call fig.show() or display it.

        Question:
        {{question}}

        Output format:
        query: <SQL query>
        python_code: <Python plotting code>
        """,
        input_variables=["schema", "question"]
    )
    chain = prompt | structured_model
    return chain.invoke({"schema": schema, "question": question})


# Step 4: Get Insights
def get_insights(sql, question, result_df):
    prompt = PromptTemplate(
        template="""
        Generate a suitable title and detailed insights based on the result for question.
        Question:{question}
        Result:{result}
        SQL Query:{sql}
        Output format:
        title: <Title>
        insights: <Insights>
        """,
        input_variables=["sql", "question", "result"]
    )
    chain = prompt | insights_structure
    result = chain.invoke({
        "sql": sql,
        "question": question,
        "result": result_df.to_dict(orient="records")[:35]  # limit rows to avoid overload
    })
    return result.title, result.insights


# Step 5: Execute SQL and run plot code
def get_results_for_query(sql):
    db = SessionLocal()
    result = db.execute(text(sql))
    return pd.DataFrame(result.fetchall(), columns=result.keys())

def execute_sql_and_generate_plot(sql, plot_code, question,admin_id):
    df = get_results_for_query(sql)
    title, insights = get_insights(sql, question, df)

    exec_namespace = {"df": df.copy()}
    try:
        exec(plot_code, exec_namespace)
        fig = exec_namespace.get("fig")
        if fig is None:
            raise RuntimeError("Plotting code did not produce a 'fig' object.")
        chart_url = save_figure(fig)
    except Exception as e:
        raise RuntimeError(f"Plotting code execution failed: {e}")

    session = SessionLocal()
    new_query = Queries(
        admin_id=admin_id,
        sql=sql,
        title=title,
        chart_url=chart_url,
        insights=insights,
        question=question

    )
    session.add(new_query)
    session.commit()
    session.refresh(new_query)

    return {
        "sql": sql,
        "question": question,
        "title": title,
        "insights": insights,
        "chart_url": chart_url,
        "data": df.to_dict(orient="records"),
        "columns": list(df.columns)
    }


# Main function to handle the question and return results
def visual_and_data(question: str, admin_id: int):
    # try:
    scope = get_admin_scope(admin_id)
    validate_question_scope(question, scope)
    response = generate_sql_and_plot_code(question, scope)
    print(response)
    return execute_sql_and_generate_plot(response.query, response.python_code, question,admin_id)
    # except Exception as e:
    #     return {"error": str(e)}
