from datetime import datetime
import sqlalchemy as db
from sqlalchemy.orm import Session
from dbsetup import Base

class TruckDB(Base):
    __tablename__ = "truck_info"
    id = db.Column("id", db.Integer, primary_key=True)
    vin = db.Column("vin_number", db.String(17))
    make = db.Column("make", db.String(255))
    model_name = db.Column("model_name", db.String(255))
    model_year = db.Column("model_year", db.String(255))
    body_class = db.Column("body_class", db.String(255))
    date = db.Column("date", db.DateTime, default=datetime.now())
    cached = True

    def to_json(self):
        return {
            "vin": self.vin,
            "make": self.make,
            "model_name" : self.model_name,
            "model_year": self.model_year,
            "body_class": self.body_class,
            "cached" : self.cached
        }

    def save(self,db: Session):
        db.add(self)
        db.commit()
        db.refresh(self)

    def delete(self, db: Session):
        db.delete(self)
        db.commit()

    def __repr__(self):
        return f"<TruckRequests(vin={self.vin},make={self.make})>"


