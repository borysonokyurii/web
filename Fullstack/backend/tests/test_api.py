import pytest
import pandas as pd
from fastapi.testclient import TestClient
from main import app 
from database import get_db

client = TestClient(app)

def override_get_db():
    class MockConnection:
        def close(self):
            pass
    yield MockConnection()

app.dependency_overrides[get_db] = override_get_db

def test_get_rating_success(mocker):
    mock_df = pd.DataFrame([
        {"delivery_status": "On Time", "avg_review_score": 4.8, "total_orders": 150}
    ])
    
    mocker.patch("pandas.read_sql", return_value=mock_df)

    response = client.get("/api/rating")

    assert response.status_code == 200
    assert response.json()[0]["delivery_status"] == "On Time"
    assert response.json()[0]["avg_review_score"] == 4.8

def test_get_rating_database_error(mocker):
    mocker.patch("pandas.read_sql", side_effect=Exception("Connection Lost"))

    response = client.get("/api/rating")

    assert response.status_code == 500
    assert "Помилка Connection Lost" in response.json()["detail"]

def test_get_rating_empty_data(mocker):
    mock_df = pd.DataFrame(columns=["delivery_status", "avg_review_score", "total_orders"])
    mocker.patch("pandas.read_sql", return_value=mock_df)

    response = client.get("/api/rating")

    assert response.status_code == 200
    assert response.json() == [] 