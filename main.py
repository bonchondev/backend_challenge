from pathlib import Path
from json.decoder import JSONDecodeError
import pyarrow as pa
import pyarrow.parquet as pq
from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from apimodels import TruckResponse, VinNumber
from dbsetup import SessionLocal, safe_db_connect
from models import TruckDB
from config import alphanumeric_query_validation, init_app, settings
from logger import logger
import requests

app = init_app()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/lookup")
async def lookup_vin(
    vin: str = Depends(alphanumeric_query_validation), sess: Session = Depends(get_db)
) -> TruckResponse:
    with safe_db_connect(sess) as db:
        truck_data = db.query(TruckDB).filter_by(vin=vin).first()

    if truck_data is not None:
        return TruckResponse(**truck_data.to_json())

    api_request = requests.get(
        f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"
    )

    try:
        api_res = api_request.json()["Results"][0]
    except JSONDecodeError:
        detail = {"errors": f"Couldn't jsonify response, problem with VIN"}
        logger.error(detail)
        raise HTTPException(status_code=400, detail=detail)

    if api_res["ErrorCode"] != "0":
        detail = {"errors": api_res["ErrorText"]}
        logger.error(detail)
        raise HTTPException(status_code=400, detail=detail)

    truck_res = TruckResponse(
        vin=vin,
        make=api_res["Make"],
        model_name=api_res["Model"],
        model_year=api_res["ModelYear"],
        body_class=api_res["BodyClass"],
    )

    truck_db = TruckDB(**truck_res.dict())

    truck_db.save(db)

    return truck_res


@app.post("/remove")
async def remove_vin(req: VinNumber, sess: Session = Depends(get_db)):
    with safe_db_connect(sess) as db:
        truck_data = db.query(TruckDB).filter_by(vin=req.vin).first()
    if truck_data is None:
        logger.debug("no vin number found")
        raise HTTPException(status_code=404, detail={"error": "Vin Number not found"})

    truck_data.delete(db)

    return {"vin": req.vin, "cache_deleted": True}


@app.get("/export")
async def export_data(sess: Session = Depends(get_db)):
    with safe_db_connect(sess) as db:
        all_truck_data = db.query(TruckDB).all()

    truck_json_list = [data.to_json() for data in all_truck_data]

    parq_table = pa.Table.from_pylist(truck_json_list)

    parq_save_location = Path(".") / settings.export_location

    if not parq_save_location.exists():
        logger.info("created export location")
        parq_save_location.mkdir()

    parq_file = parq_save_location / settings.parquet_name

    pq.write_table(parq_table, parq_file)

    return FileResponse(
        parq_file,
        media_type="application/x-parquet",
        filename=parq_file.name,
    )
