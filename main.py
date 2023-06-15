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
    truck_data = session.query(TruckRequests).filter_by(vin=req.vin).first()

    if truck_data is not None:
        return Truck(**truck_data.to_json())

    api_request = requests.get(
        f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{req.vin}?format=json"
    )

    api_res = api_request.json()["Results"][0]

    if api_res["ErrorCode"] != "0":
        detail = {"errors": api_res["ErrorText"]}
        raise HTTPException(status_code=422, detail=detail)

    truck_res = Truck(
        vin=req.vin,
        make=api_res["Make"],
        model_name=api_res["Model"],
        model_year=api_res["ModelYear"],
        body_class=api_res["BodyClass"],
    )

    truck_db_save = TruckRequests(
        vin=truck_res.vin,
        make=truck_res.make,
        model_name=truck_res.model_name,
        model_year=truck_res.model_year,
        body_class=truck_res.body_class
    )

    session.add(truck_db_save)

    return truck_res


@app.get("/remove")
def remove_vin(audio_type: str, data: str):
    sound_file = Path(f"sounds/{audio_type}/{data}.mp3").exists()
    if not sound_file:
        raise HTTPException(status_code=404, detail="file not found")
    return {"url": f"/audio/{audio_type}/{data}"}


@app.get("/export")
def export_data(audio_type: str, filename: str):
    return FileResponse(f"sounds/{audio_type}/{filename}.mp3")
