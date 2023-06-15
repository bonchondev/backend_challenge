from pydantic import BaseModel, Field, validator


class VinNumber(BaseModel):
    vin: str = Field(min_length=17, max_length=17)


class TruckResponse(VinNumber):
    make: str
    model_name: str
    model_year: str
    body_class: str
    cached: bool = False

    class Config:
        orm_mode = True

    @validator("vin")
    def vin_alphanumeric(cls, field):
        assert field.isalnum(), "must be alphanumeric"
        return field
