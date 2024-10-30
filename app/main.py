from fastapi import FastAPI, BackgroundTasks
from app.generate_data import generate_sample_data
from app.model import detect_anomalies
from kafka.kafka import process_messages
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # 서버 시작 시 백그라운드로 Kafka 메시지 처리 작업을 시작
    background_tasks = BackgroundTasks()
    background_tasks.add_task(process_messages)

@app.get("/")
async def root():
    return {"message": "Anomaly Detection API is running."}

# 샘플 데이터 테스트
@app.post("/detect-anomalies/")
def detect_anomalies_endpoint():
    df = generate_sample_data(num_samples=1)
    anomalies = detect_anomalies(df)
    return {"anomalies": anomalies}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)