from pydantic import BaseModel, Field
import datetime


# Submit schema

class SubmitBase(BaseModel):
    public_score: float
    bid: int
    hid: int
    uid: int


class SubmitCreate(SubmitBase):
    pass


class Submit(SubmitBase):

    class Config:
        orm_mode = True
