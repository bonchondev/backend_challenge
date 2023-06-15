from fastapi.testclient import TestClient
from dbsetup import create_table, delete_table
from main import app
from models import TruckDB


@app.on_event("startup")
async def startup_event():
    create_table(TruckDB,prefix="test")

@app.on_event("shutdown")
async def shutdown_event():
    delete_table(TruckDB, prefix="test")


def test_lookup():
    test_vin = "1XKWDB0X57J211825"
    with TestClient(app) as test_client:
        response = test_client.get(f"/lookup?vin={test_vin}")
        assert response.status_code == 200
        assert response.json() == {
            "vin": "1XKWDB0X57J211825",
            "make": "KENWORTH",
            "model_name": "W9 Series",
            "model_year": "2007",
            "body_class": "Truck-Tractor",
            "cached": False,
        }
        second_response = test_client.get(f"/lookup?vin={test_vin}")
        assert second_response.status_code == 200
        assert second_response.json() == {
            "vin": "1XKWDB0X57J211825",
            "make": "KENWORTH",
            "model_name": "W9 Series",
            "model_year": "2007",
            "body_class": "Truck-Tractor",
            "cached": True,
        }


