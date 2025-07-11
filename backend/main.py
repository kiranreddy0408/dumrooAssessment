from db import engine
import models
models.Base.metadata.create_all(bind=engine)
from fastapi import FastAPI, HTTPException, Depends, status
from services import llm_agent
from services.llm_agent import visual_and_data
from db import SessionLocal, get_db
from models import Queries
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

origins = [
    "http://localhost",]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
app.mount("/static", StaticFiles(directory="c:/Users/kiran/Desktop/dumroo_ai_admin/backend/static"), name="static")



@app.post("/ask")
def ask_query(question: str,admin_id:int):
    try:
        res = visual_and_data(question,admin_id)
        # print("Response:", res)
        if not res:
            raise HTTPException(status_code=404, detail="No data found for the given question.")
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/query/{query_id}",status_code=status.HTTP_200_OK)
def get_query(query_id: int, db: Session = Depends(get_db)):
    db = SessionLocal()
    query = db.query(Queries).filter(Queries.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="ID not found.")
    # print("Query:", query.insights)
    df = llm_agent.get_results_for_query(query.sql)
    return {
        "sql": query.sql,
        "title": query.title,
        "chart_url": query.chart_url,
        "insights": query.insights,
        "data": df.to_dict(orient="records"),
        "columns": list(df.columns)
    }

@app.get("/queries/{admin_id}",status_code=status.HTTP_200_OK)
def get_all_queries(admin_id: int,db: Session = Depends(get_db)):
    db = SessionLocal()
    queries = db.query(Queries).filter(Queries.admin_id == admin_id).order_by(Queries.timestamp.desc()).all()
    if not queries:
        raise HTTPException(status_code=404, detail="No queries found.")
    return queries

