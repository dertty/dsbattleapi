from sqlalchemy.orm import Session
from . import models, schemas

import datetime
import pytz


def create_submit(db: Session, public_score: float, private_score: float, file_location: str, hid: int, uid: int, bid: int):
    db_submit = models.Submit(
        bid=bid,
        hid=hid,
        submit_dt=datetime.datetime.now(pytz.timezone('Europe/Moscow')),
        uid=uid,
        private_score=private_score,
        public_score=public_score,
        comment=file_location
    )
    db.add(db_submit)
    db.commit()
    db.refresh(db_submit)

    return db_submit
