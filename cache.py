from datetime import datetime
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, declarative_base
from config import TruckDBConfig

Base = declarative_base()

connection = "sqlite:///{dbname}".format(dbname=TruckDBConfig.name)

engine = db.create_engine(connection, connect_args={"check_same_thread": False})

Session = sessionmaker()

Session.configure(bind=engine)

session = Session()


class TruckRequests(Base):
    __tablename__ = "truck_requests"
    id = db.Column("id", db.Integer, primary_key=True)
    vin_number = db.Column("vin_number", db.String(17))
    make = db.Column("make", db.String(255))
    model_name = db.Column("model_name", db.String(255))
    model_year = db.Column("model_year", db.String(255))
    body_class = db.Column("body_class", db.String(255))
    date = db.Column("date", db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"<Requests(user={self.id},complete={self.user_id})>"


def create_table(model, engine=engine):
    if not db.inspect(engine).has_table(model.__table__.name):
        model.__table__.create(engine)
        return "Created."
    return "Already exists."


def delete_table(model, engine=engine):
    if db.inspect(engine).has_table(model.__table__.name):
        model.__table__.drop(engine)
        return "Deleted."
    return "Does not exist."


# print(create_table(Requests))
# print(create_table(User))
# check_request = session.query(Requests).all()
# print(check_request)

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-m", "--migrate", type="choice", choices=["up", "down"],default="up")
    (options, args) = parser.parse_args()
    if options.migrate == "up":
        create_table(TruckRequests)
    if options.migrate == "down":
        delete_table(TruckRequests)
