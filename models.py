from pydantic import BaseModel, Field, validator


class VinNumber(BaseModel):
    vin: str = Field(min_length=17, max_length=17)


class Truck(BaseModel):
    vin: str = Field(min_length=17, max_length=17)
    make: str
    model: str
    model_year: str
    body: str
    cached: bool = False

    @validator("vin")
    def vin_alphanumeric(cls, field):
        assert field.isalnum(), "must be alphanumeric"
        return field
