from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from config import ValidationErrorLoggingRoute
from models import Truck, VinNumber
from cache import TruckRequests, session
import requests


app = FastAPI()
app.router.route_class = ValidationErrorLoggingRoute


@app.get("/lookup")
async def lookup_vin(req: VinNumber) -> Truck:
    truck_data = session.query(TruckRequests).filter_by(vin_number=req.vin).first()
    print(truck_data)
    test_truck = Truck(
        vin=req.vin,
        make="woah",
        model="wo",
        model_year="noway",
        body="thereisn't",
        cached=True,
    )
    return test_truck


@app.get("/remove")
def remove_vin(audio_type: str, data: str):
    sound_file = Path(f"sounds/{audio_type}/{data}.mp3").exists()
    if not sound_file:
        raise HTTPException(status_code=404, detail="file not found")
    return {"url": f"/audio/{audio_type}/{data}"}


@app.get("/export")
def export_data(audio_type: str, filename: str):
    return FileResponse(f"sounds/{audio_type}/{filename}.mp3")
