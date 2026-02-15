import uvicorn
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from backend.database import get_db, engine

load_dotenv()

# DATABASE_URL setup removed as it is handled in database.py

def get_query():
    return text("""
        SELECT 
        CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late Delivery' 
        ELSE 'On Time' 
        END AS delivery_status,
        ROUND(AVG(r.review_score)::numeric, 2)::float AS avg_review_score,
        COUNT(o.order_id ) as total_orders
        FROM orders o 
        JOIN order_reviews r ON o.order_id = r.order_id 
        WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
        GROUP BY 1
    """)

def get_second_query():
    # optimized query to reduce load
    return text("""WITH cte AS (
    SELECT 
    s.seller_city, s.seller_state,
    COUNT(o.order_id) AS "total", 
    SUM(CASE WHEN o.order_estimated_delivery_date < o.order_delivered_customer_date THEN 1 
    ELSE 0 END) AS "late_orders",
    ROUND(AVG(p.product_weight_g)::numeric, 2) AS "avg_weight_per_order"
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id 
    JOIN sellers s ON oi.seller_id = s.seller_id 
    JOIN products p ON oi.product_id = p.product_id 
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY 1,2)
    SELECT *, 
    ROUND(((late_orders::numeric / total) * 100), 2) AS "Delay_Rate"
    FROM cte
    WHERE total > 10 
    ORDER BY "avg_weight_per_order" DESC;
    """)



@asynccontextmanager
async def lifespan(app:FastAPI):
    if engine:
        try:
            with engine.connect() as con:
                con.execute(text("SELECT 1"))
            yield 
            engine.dispose() 
            print("зєднання закрито")
        except Exception as e:
            print(f"Database connection failed: {e}")
            yield
    else:
        print("Engine not initialized")
        yield

app = FastAPI(title="Olist Analytics API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/rating")
def get_summary(db: Connection = Depends(get_db)):
    try:
        df = pd.read_sql(get_query(), db)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка {str(e)}")
    
@app.get("/api/corel")
def get_corelation(db: Connection = Depends(get_db)):
    try:
        df = pd.read_sql(get_second_query(), db)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)