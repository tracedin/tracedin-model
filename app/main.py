from fastapi import FastAPI, HTTPException
# from contextlib import asynccontextmanager
from app.generate_data import generate_sample_data
from app.model import detect_anomalies
# from kafka.kafka import process_messages
from pydantic import BaseModel
from typing import List
import uvicorn
import pandas as pd

app = FastAPI()

# @app.on_event("startup")
# async def startup_event():
#     # 서버 시작 시 백그라운드로 Kafka 메시지 처리 작업을 시작
#     background_tasks = BackgroundTasks()
#     background_tasks.add_task(process_messages)

# @asynccontextmanager
# async def lifespan_handler(app: FastAPI):
#     # 서버 시작 시 Kafka 메시지 처리 작업을 백그라운드로 시작
#     task = process_messages()
#
#     yield
#     # 서버 종료 시 백그라운드 작업 정리
#     task.cancel()

class Span(BaseModel):
    id: str
    traceId: str
    projectKey: str
    duration: float

@app.get("/")
async def root():
    return {"message": "Anomaly Detection API is running."}

# 샘플 데이터 테스트
@app.post("/sample-detect-anomalies/")
def sample_detect_anomalies_endpoint():
    df = generate_sample_data(num_samples=1)
    anomalies = detect_anomalies(df)
    return {"anomalies": anomalies}

@app.post("/detect_anomalies")
async def detect_anomalies_endpoint(spans: List[Span]):
    spans_df = pd.DataFrame([span.dict() for span in spans])
    anomalies = detect_anomalies(spans_df)

    if not anomalies:
        raise HTTPException(status_code=404, detail="No spans detected")

    return anomalies


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)