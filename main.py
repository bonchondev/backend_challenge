from pathlib import Path
from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models import TruckResponse, VinNumber
from cache import SessionLocal, TruckDB
from config import init_app
import requests

app = init_app()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/lookup")
async def lookup_vin(req: VinNumber, db: Session = Depends(get_db)) -> TruckResponse:
    truck_data = db.query(TruckDB).filter_by(vin=req.vin).first()

    if truck_data is not None:
        return TruckResponse(**truck_data.to_json())

    api_request = requests.get(
        f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{req.vin}?format=json"
    )

    api_res = api_request.json()["Results"][0]

    if api_res["ErrorCode"] != "0":
        detail = {"errors": api_res["ErrorText"]}
        raise HTTPException(status_code=400, detail=detail)

    truck_res = TruckResponse(
        vin=req.vin,
        make=api_res["Make"],
        model_name=api_res["Model"],
        model_year=api_res["ModelYear"],
        body_class=api_res["BodyClass"],
    )

    truck_db = TruckDB(**truck_res.dict())

    truck_db.save(db)

    return truck_res


@app.post("/remove")
def remove_vin(req: VinNumber, db: Session = Depends(get_db)):
    truck_data = db.query(TruckDB).filter_by(vin=req.vin).first()
    if truck_data is None:
        raise HTTPException(status_code=404, detail={"error" : "Vin Number not found"})
    truck_data.delete(db)
    return {"vin": req.vin, "cache_deleted" : True}


@app.get("/export")
def export_data(db: Session = Depends(get_db)):
    """
    Needs to export data as a parquet
    """
    return FileResponse(f"sounds/{audio_type}/{filename}.mp3")

