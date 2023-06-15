from pathlib import Path
from fastapi.testclient import TestClient
from dbsetup import create_table, delete_table
from main import app
from config import settings
from models import TruckDB


@app.on_event("startup")
async def startup_event():
    """
    Can add prefix when creating table and
    use that same DB and models, but different tables for
    testing.
    """
    # create_table(TruckDB,prefix="test")
    create_table(TruckDB)


@app.on_event("shutdown")
async def shutdown_event():
    # delete_table(TruckDB, prefix="test")
    delete_table(TruckDB)


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


def test_remove():
    test_vin = "1XKWDB0X57J211825"
    with TestClient(app) as test_client:
        test_client.get(f"/lookup?vin={test_vin}")
        response = test_client.post(f"/remove", json={"vin": test_vin})
        assert response.status_code == 200
        assert response.json() == {"vin": test_vin, "cache_deleted": True}


def test_export():
    test_vin = "1XKWDB0X57J211825"
    with TestClient(app) as test_client:
        test_client.get(f"/lookup?vin={test_vin}")
        response = test_client.get("/export")
        assert response.status_code == 200
        parquet_file = Path(".") / settings.export_location / settings.parquet_name
        assert parquet_file.exists()


def test_failed_remove():
    test_vin = "1XKWDB0X57J211825"
    wrong_vin = "1XKWDB0X57.211825"
    with TestClient(app) as test_client:
        test_client.get(f"/lookup?vin={test_vin}")
        response = test_client.post(f"/remove", json={"vin": wrong_vin})
        assert response.status_code == 404
        assert response.json() == {"detail": {"error": "Vin Number not found"}}


def test_failed_lookup():
    wrong_vin = "1XKWDB0X57.211825"
    with TestClient(app) as test_client:
        wrong_vin = "1XKWDB0X57.211825"
        response = test_client.get(f"/lookup?vin={wrong_vin}")
        assert response.status_code == 422
        assert response.json() == {"detail": {"errors": "VIN must be alphanumeric"}}
