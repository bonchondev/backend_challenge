from contextlib import contextmanager
import sqlalchemy as db
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError
from config import settings
from logger import logger

from sqlalchemy.orm import sessionmaker, declarative_base, Session

connection = "sqlite:///{dbname}".format(dbname="truck.db")

engine = db.create_engine(connection, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)


@contextmanager
def safe_db_connect(db: Session):
    try:
        yield db
    except OperationalError as exc:
        if settings.environment == "dev":
            err_message = f"may need to run [python dbsetup.py -m up] -> {exc._message}"
        else:
            err_message = "contact admin for help"
        logger.error(err_message)
        raise HTTPException(
            status_code=424, detail={"error": f"Problem with db: {err_message}"}
        )


def create_table(model,prefix=None, engine=engine):
    if not db.inspect(engine).has_table(model.__table__.name):
        if prefix and prefix not in model.__table__.name:
            model.__table__.name = f'{prefix}_{model.__table__.name}'
        model.__table__.create(engine)
        return "Created."
    return "Already exists."


def delete_table(model, prefix=None, engine=engine):
    if prefix and prefix not in model.__table__.name:
        model.__table__.name = f'{prefix}_{model.__table__.name}'
    if db.inspect(engine).has_table(model.__table__.name):
        model.__table__.drop(engine)
        return "Deleted."
    return "Does not exist."

if __name__ == "__main__":
    from optparse import OptionParser
    from models import TruckDB
    parser = OptionParser()
    parser.add_option("-m", "--migrate", type="choice", choices=["up", "down"],default="up")
    (options, args) = parser.parse_args()
    if options.migrate == "up":
        create_status = create_table(TruckDB)
        print(create_status)
    if options.migrate == "down":
        delete_status = delete_table(TruckDB)
        print(delete_status)
