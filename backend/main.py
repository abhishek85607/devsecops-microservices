import os
import redis
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="DevSecOps Core API", version="1.0.0")

# Prometheus Metrics Instrumentation
Instrumentator().instrument(app).expose(app)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Redis client
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.on_event("startup")
def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database init warning (retrying later): {e}")

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "backend"}

@app.get("/api/v1/data")
def get_data():
    cached = r.get("cached_payload")
    if cached:
        return {"source": "redis_cache", "data": cached}
    
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT message, created_at FROM audit_logs ORDER BY id DESC LIMIT 5;")
        records = cur.fetchall()
        cur.close()
        conn.close()
        payload = [{"message": r[0], "created_at": str(r[1])} for r in records]
        r.setex("cached_payload", 15, str(payload))
        return {"source": "postgresql", "data": payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class Item(BaseModel):
    message: str

@app.post("/api/v1/data")
def create_data(item: Item):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO audit_logs (message) VALUES (%s) RETURNING id;", (item.message,))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        r.delete("cached_payload")
        return {"id": new_id, "message": item.message, "status": "persisted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
