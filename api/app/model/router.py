import hashlib
import os
import tempfile

from app import settings as config
from app import utils
from app.auth.jwt import get_current_user
from app.model.schema import PredictResponse
from app.model.services import model_predict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

router = APIRouter(tags=["Model"], prefix="/model")


@router.post("/predict")
async def predict(file: UploadFile = File(None), current_user=Depends(get_current_user)):
    rpse = {"success": False, "prediction": None, "score": None, "image_file_name": None}
    # To correctly implement this endpoint you should:
    #   1. Check a file was sent and that file is an image, see `allowed_file()` from `utils.py`.
    if file is not None and utils.allowed_file(file.filename):
        #   2. Store the image to disk, calculate hash (see `get_file_hash()` from `utils.py`) before
        #      to avoid re-writing an image already uploaded.
        file_bytes = await file.read()
        extension = os.path.splitext(file.filename)[1].lower()
        file_hash = hashlib.md5(file_bytes).hexdigest() + extension
        file_path = os.path.join(config.UPLOAD_FOLDER, file_hash)
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        if not os.path.exists(file_path):
            with tempfile.NamedTemporaryFile(dir=config.UPLOAD_FOLDER, delete=False) as tmp:
                tmp.write(file_bytes)
                tmp.flush()
                os.fsync(tmp.fileno())
                temp_name = tmp.name
            try:
                os.replace(temp_name, file_path)
            except Exception:
                if os.path.exists(temp_name):
                    os.remove(temp_name)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Storage error, please try again."
                )
        #   3. Send the file to be processed by the `model` service, see `model_predict()` from `services.py`.
        prediction, score = await model_predict(file_hash)

        # 4. Update and return `rpse` dict with the corresponding values
        # If user sends an invalid request (e.g. no file provided) this endpoint
        # should return `rpse` dict with default values HTTP 400 Bad Request code
        if prediction is None or score is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model service failed to provide a prediction. Please try again."
            )

        rpse.update({
            "success": True,
            "prediction": prediction,
            "score": score,
            "image_file_name": file_hash
        })

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type is not supported."
        )

    return PredictResponse(**rpse)
