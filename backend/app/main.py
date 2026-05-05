from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import os

app = FastAPI()

DATABASE_URL = "postgresql://admin:admin123@postgres:5432/bi_recommendation"

engine = create_engine(DATABASE_URL)

class LogEvent(BaseModel):
    user_id: int
    report_name: str
    action: str
    duration: int

@app.get("/")
def home():
    return {"message": "Backend Running"}

@app.post("/log-event")
def log_event(event: LogEvent):

    query = text("""
        INSERT INTO user_logs
        (user_id, report_name, action, duration)
        VALUES
        (:user_id, :report_name, :action, :duration)
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "user_id": event.user_id,
            "report_name": event.report_name,
            "action": event.action,
            "duration": event.duration
        })
        conn.commit()

    return {"status": "logged"}