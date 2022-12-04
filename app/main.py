import io
import pathlib
import uuid

import pytesseract
import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    File,
    Header,
    HTTPException,
    Request,
    UploadFile,
    status
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from PIL import Image

from config import Settings, get_settings


BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"


app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# @app.get("/", response_class=HTMLResponse)  # this response class expects HTML string to be returned
# def home_view(request: Request, settings: Settings = Depends(get_settings)):
#     return templates.TemplateResponse("home.html", {"request": request, "abc": 123})


def verify_auth(settings: Settings, authorization=Header(None)):
    if settings.debug and settings.skip_auth:
        return

    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No authorization credentials")

    label, token = authorization.split()  # {"authorization": "Bearer <token>"}
    if token != settings.app_auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@app.post("/")
async def extract_text_from_image(file: UploadFile = File(...), authorization=Header(None), settings: Settings = Depends(get_settings)):
    verify_auth(settings, authorization)

    bytes_str = io.BytesIO(await file.read())

    try:
        image = Image.open(bytes_str)  # opencv (cv2) usage also possible
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image")

    predictions_raw = pytesseract.image_to_string(image)
    predictions_processed = [x for x in predictions_raw.split("\n")]

    return {"results": predictions_processed, "original": predictions_raw}


@app.post("/img-echo", response_class=FileResponse)
async def echo_image(file: UploadFile = File(...), settings: Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid endpoint")

    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())

    try:
        image = Image.open(bytes_str)  # opencv (cv2) usage also possible
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image")

    file_name = pathlib.Path(file.filename)
    file_extension = file_name.suffix  # .jpeg, .txt, etc.
    destination_directory = rf"{UPLOAD_DIR}\{uuid.uuid1()}{file_extension}"  # uuid1 - uuid with timestamp

    # with open(destination_directory, "wb") as file:
    #     file.write(bytes_str.read())

    image.save(destination_directory)

    return destination_directory


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
