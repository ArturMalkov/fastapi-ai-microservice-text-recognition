import io
import shutil
import time

from fastapi.testclient import TestClient
from PIL import Image, ImageChops

from app.main import app, BASE_DIR, UPLOAD_DIR
from config import get_settings


client = TestClient(app)


# def test_get_home():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert "text/html" in response.headers["Content-Type"]
#     # assert response.text != "..."


def test_invalid_file_upload_error():
    response = client.post("/")
    assert response.status_code == 422
    assert "application/json" in response.headers["Content-Type"]
    # assert response.text != "..."


def test_prediction():
    settings = get_settings()
    saved_images_path = BASE_DIR / "images"
    for file_path in saved_images_path.glob("*"):  # "*" means every file that's in there - as opposed to "*.png", "*.txt", etc.
        try:
            image = Image.open(file_path)  # more reliable way than checking extensions
        except:
            image = None

        response = client.post("/",
                               files={"file": open(file_path, "rb")},
                               headers={"Authorization": f"JWT {settings.app_auth_token}"}
                               )
        # file_extension = str(image.suffix).replace(".", "")  # 'png' instead of '.png' - not a reliable way btw
        # assert file_extension in response.headers["Content-Type"]
        if image is None:
            assert response.status_code == 400
        else:
            # Returning a valid image
            assert response.status_code == 200
            data = response.json()
            assert len(data.keys()) == 2


def test_prediction_missing_headers():
    saved_images_path = BASE_DIR / "images"
    for file_path in saved_images_path.glob("*"):
        try:
            image = Image.open(file_path)
        except:
            image = None

        response = client.post("/",
                               files={"file": open(file_path, "rb")},
                               )
        assert response.status_code == 401


def test_echo_upload():
    saved_images_path = BASE_DIR / "images"
    for file_path in saved_images_path.glob("*"):  # "*" means every file that's in there - as opposed to "*.png", "*.txt", etc.
        try:
            image = Image.open(file_path)  # more reliable way than checking extensions
        except:
            image = None

        response = client.post("/img-echo", files={"file": open(file_path, "rb")})
        # file_extension = str(image.suffix).replace(".", "")  # 'png' instead of '.png' - not a reliable way btw
        # assert file_extension in response.headers["Content-Type"]
        if image is None:
            assert response.status_code == 400
        else:
            # Returning a valid image
            assert response.status_code == 200
            response_bytes_stream = io.BytesIO(response.content)
            echo_image = Image.open(response_bytes_stream)
            difference = ImageChops.difference(echo_image, image).getbbox()
            assert difference is None  # to make sure that it's literally the exact same image

    time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)  # to remove the directory after each test
