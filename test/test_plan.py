from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_plan_endpoint():
    payload = {
        "traveler_name": "Alex",
        "origin_city": "Hyderabad",
        "days": 5,
        "month": "June",
        "budget_total": 900,
        "interests": ["beach", "food"],
        "visa_passport": "Indian"
    }
    response = client.post("/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "destination" in data
    assert "itinerary" in data
    assert "estimated_cost_breakdown" in data
