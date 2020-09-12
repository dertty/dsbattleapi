from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends, HTTPException, status

from dsbattle_api_app.core.models import schemas
from dsbattle_api_app.core.database import get_db

import numpy as np
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error, roc_auc_score, f1_score

import datetime
import pytz
import secrets
from io import StringIO

from sqlalchemy.orm import Session
from dsbattle_api_app.core.models import crud
from dsbattle_api_app.core.functions.s3 import get_file_from_s3, save_file_to_s3

router = APIRouter()


@router.post("/submit/{hid}/{uid}/{bid}", response_model=schemas.Submit, summary="Сохранение результатов сабмита")
def create_submit(
        hid: int,
        uid: int,
        bid: int,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        token: str = '',
):
    correct_token = secrets.compare_digest(token, "qwerty1234567890987654321qwerty")
    if not correct_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login",
        )
    uploaded_file = np.genfromtxt(StringIO(file.file.read().decode('utf8')), delimiter=';', skip_header=True)
    new_file_name = file.filename.split(".")[0] + "__" + datetime.datetime.now(pytz.timezone('Europe/Moscow')).isoformat() + "." + file.filename.split(".")[1]
    file_location = f'hackathons_submits/hid{hid}/uid{uid}/bid{bid}/{new_file_name}'


    file_for_public_score = np.genfromtxt(
        StringIO(get_file_from_s3(f'hackathons_resources/hid{hid}/public_dataset.csv').decode('utf8')),
        delimiter=';', skip_header=True)
    public_score = float(accuracy_score(file_for_public_score[:, 1], uploaded_file[:, 1]))


    def jobs_for_background():
        save_file_to_s3(file.file, file_location)
        file_for_private_score = np.genfromtxt(
            StringIO(get_file_from_s3(f'hackathons_resources/hid{hid}/private_dataset.csv').decode('utf-8')),
            delimiter=';', skip_header=True)
        private_score = float(accuracy_score(file_for_private_score[:, 1], uploaded_file[:, 1]))

        crud.create_submit(
            db=db,
            public_score=public_score,
            private_score=private_score,
            file_location=file_location,
            hid=hid, uid=uid, bid=bid)

    background_tasks.add_task(jobs_for_background)

    return {
        'hid': hid,
        'uid': uid,
        'bid': bid,
        'public_score': public_score,
    }

